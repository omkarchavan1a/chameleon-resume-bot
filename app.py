import streamlit as st
import os
import io
import pdfplumber
from datetime import datetime
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from openai import OpenAI

# Load external configuration from backend/.env file
load_dotenv("backend/.env")

# ─── NVIDIA NIM Client ───────────────────────────────────────────────────────
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
BASE_URL       = "https://integrate.api.nvidia.com/v1"
MODEL          = "meta/llama-3.3-70b-instruct"

if not NVIDIA_API_KEY:
    st.error("NVIDIA_API_KEY environment variable is missing. Please configure backend/.env.")
    st.stop()

client = OpenAI(api_key=NVIDIA_API_KEY, base_url=BASE_URL)

# ─── Database Connection ──────────────────────────────────────────────────────
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "resume_bot"

@st.cache_resource
def get_db_collection():
    if MONGODB_URI:
        try:
            mongo_client = MongoClient(
                MONGODB_URI, 
                serverSelectionTimeoutMS=10000, 
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=True
            )
            mongo_client.admin.command('ping')
            return mongo_client[DB_NAME].resumes

        except Exception as e:
            st.warning(f"Could not connect to MongoDB: {str(e)}")
            return None
    else:
        st.warning("MONGODB_URI not found in environment. History will not be saved.")
        return None

resumes_collection = get_db_collection()

# ─── Prompts and Logic ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Expert ATS (Applicant Tracking System) Specialist and Professional Resume Writer.

Your task is to transform the user's "Master Experience" into a highly tailored, Chameleon-style resume that:

1. **Position Pivot**: Adjust the Professional Summary and Core Skills to highlight only tools/experiences relevant to the target role.
   - AI-heavy role → prioritize CrewAI, automation, ML, GenAI work
   - Web-heavy role → prioritize Next.js, React, Tailwind, frontend work
   - Full-stack → balance both

2. **City Adaptation**:
   - Update contact header to reflect the Target City
   - Tech hubs (Bangalore, Pune, Hyderabad) → use high-tech corporate language
   - Highlight local projects or regional clients when applicable
   - Remote → emphasize async communication, global collaboration, distributed team experience

3. **Keyword Optimization**: Seamlessly integrate high-ranking keywords from the Job Description to pass ATS filters. Embed naturally — not as a keyword dump.

4. **Quantifiable Impact**: Every experience bullet MUST follow:
   "Accomplished [X] as measured by [Y], by doing [Z]"
   Example: "Reduced deployment time by 60% (from 45min to 18min) by implementing automated CI/CD pipelines with GitHub Actions."

5. **Output Format** — Clean Markdown only:
   - **Header**: Name, Email, Phone, LinkedIn, GitHub, City
   - **Professional Summary**: 3-4 impactful sentences tailored to role+city
   - **Technical Stack**: Grouped by category (Languages, Frameworks, AI/ML, DevOps, etc.) — show only relevant ones first
   - **Professional Experience**: Last 3-4 roles, each with 3-4 quantified bullets
   - **Key Projects**: Best 3 projects for THIS specific role (choose wisely)
   - **Education**

Rules:
- One page structure (concise but impactful)
- No filler phrases like "hardworking team player"
- No generic objectives
- Use strong action verbs: Architected, Automated, Delivered, Slashed, Scaled, Spearheaded
- ATS-safe formatting (no tables in the main sections, clean headers)
"""

def extract_pdf_text(file_buffer):
    text = ""
    with pdfplumber.open(file_buffer) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text

def build_user_prompt(master_data, target_position, target_city, job_description):
    jd_section = f"\n\n**Job Description:**\n{job_description}" if job_description.strip() else ""
    return f"""Please create a Chameleon Resume with the following inputs:

**Target Position:** {target_position}
**Target City:** {target_city}

**Master Data (Full Work History, Skills & Projects):**
{master_data}
{jd_section}

Transform this into a perfectly tailored resume following all the rules. Output ONLY the clean Markdown resume — no preamble, no explanation."""

REFINE_SYSTEM_PROMPT = """You are an Expert Resume Editor and ATS Specialist.

You will receive an existing resume in Markdown format, along with specific editing instructions from the user.

Your job is to apply ONLY the requested changes with surgical precision:
- Do NOT rewrite sections that weren't mentioned
- Do NOT change names, contact info, or facts unless explicitly asked
- DO preserve the existing structure, formatting, and Markdown style
- DO apply the instructions intelligently — if user says "make it shorter", condense without losing keywords
- DO maintain ATS compatibility (clean headers, no tables, strong action verbs)
- DO keep all quantified impact bullets (Accomplished X by Y via Z format)

Output ONLY the complete updated resume in clean Markdown — no explanations, no commentary."""

def generate_resume(master_data, target_position, target_city, job_description):
    user_prompt = build_user_prompt(master_data, target_position, target_city, job_description)
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.6,
        top_p=0.9,
        max_tokens=2048,
        stream=False
    )
    return completion

def refine_resume_f(current_resume, instructions, target_position, target_city):
    context = ""
    if target_position: context += f"Original role target: {target_position}\n"
    if target_city: context += f"Original city target: {target_city}\n"

    user_msg = f"""{context}
--- CURRENT RESUME ---
{current_resume}
--- END RESUME ---

EDIT INSTRUCTIONS:
{instructions}

Apply the instructions above to the resume and return the complete updated resume."""

    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": REFINE_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.4,
        top_p=0.9,
        max_tokens=2048,
        stream=False
    )
    return completion

# ─── Session State ────────────────────────────────────────────────────────────
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = ""
if "master_data" not in st.session_state:
    st.session_state.master_data = ""

# ─── Streamlit UI ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chameleon Resume Bot", page_icon="🦎", layout="wide")

st.title("🦎 Chameleon Resume Bot")
st.subheader("AI-Powered ATS Resume Generator")

tab_gen, tab_hist = st.tabs(["✨ Generator", "📜 History"])

with tab_gen:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("1. Input Data")
        
        pdf_file = st.file_uploader("Upload your Master Resume (PDF)", type=["pdf"])
        if pdf_file is not None:
            if not st.session_state.master_data:
                with st.spinner("Extracting text from PDF..."):
                    text = extract_pdf_text(pdf_file)
                    st.session_state.master_data = text
                st.success("PDF Extracted successfully!")

        master_data_input = st.text_area(
            "Master Experience (Auto-filled from PDF if uploaded)",
            value=st.session_state.master_data,
            height=200
        )
        st.session_state.master_data = master_data_input

        target_position = st.text_input("Target Position", placeholder="e.g., Senior Full-Stack Developer")
        target_city = st.text_input("Target City", placeholder="e.g., Pune, Mumbai, Remote")
        job_description = st.text_area("Job Description (Optional, boosts ATS)", height=150)

        if st.button("🦎 Generate Chameleon Resume", type="primary"):
            if not target_position or not target_city or not st.session_state.master_data:
                st.error("Please fill in the Master Experience, Target Position, and Target City.")
            else:
                with st.spinner("Generating Resume using NVIDIA NIM (Llama 3.3 70B)..."):
                    try:
                        completion = generate_resume(
                            st.session_state.master_data, 
                            target_position, 
                            target_city, 
                            job_description
                        )
                        resume_md = completion.choices[0].message.content
                        tokens_used = completion.usage.total_tokens if completion.usage else 0
                        
                        st.session_state.generated_resume = resume_md

                        # Persist to Mongo
                        if resumes_collection is not None:
                            resumes_collection.insert_one({
                                "type": "generation",
                                "target_position": target_position,
                                "target_city": target_city,
                                "resume_markdown": resume_md,
                                "tokens_used": tokens_used,
                                "timestamp": datetime.utcnow()
                            })
                    except Exception as e:
                        st.error(f"Error during generation: {e}")

    with col2:
        st.header("2. Output")
        
        if st.session_state.generated_resume:
            st.markdown("### 📄 Generated Resume")
            
            # Action Tabs for Output
            out_view, out_refine = st.tabs(["Preview & Raw", "Refine & Edit"])
            
            with out_view:
                st.download_button(
                    label="⬇️ Download Markdown",
                    data=st.session_state.generated_resume,
                    file_name=f"resume_{target_position.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
                
                show_raw = st.toggle("Show Raw Markdown")
                if show_raw:
                    st.code(st.session_state.generated_resume, language="markdown")
                else:
                    st.markdown(st.session_state.generated_resume)

            with out_refine:
                st.info("Ask AI to make specific changes without losing existing format.")
                refine_instructions = st.text_area("Custom Edit Instructions", placeholder="e.g. 'Make it more concise', 'Add leadership examples'")
                if st.button("✏️ Apply Changes"):
                    if not refine_instructions:
                        st.warning("Please provide edit instructions.")
                    else:
                        with st.spinner("Refining resume..."):
                            try:
                                completion = refine_resume_f(
                                    st.session_state.generated_resume,
                                    refine_instructions,
                                    target_position,
                                    target_city
                                )
                                refined_md = completion.choices[0].message.content
                                tokens_used = completion.usage.total_tokens if completion.usage else 0
                                
                                st.session_state.generated_resume = refined_md
                                
                                if resumes_collection is not None:
                                    resumes_collection.insert_one({
                                        "type": "refinement",
                                        "instructions": refine_instructions,
                                        "target_position": target_position,
                                        "target_city": target_city,
                                        "resume_markdown": refined_md,
                                        "tokens_used": tokens_used,
                                        "timestamp": datetime.utcnow()
                                    })
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error during refinement: {e}")
        else:
            st.info("Fill out the left panel and click Generate.")

with tab_hist:
    st.header("Recent Generations")
    if resumes_collection is not None:
        try:
            history = list(resumes_collection.find().sort("timestamp", -1).limit(10))
            if history:
                for doc in history:
                    with st.expander(f"{doc.get('type', 'generation').title()} - {doc.get('target_position', 'Unknown')} ({doc.get('timestamp', '')})"):
                        if doc.get("instructions"):
                            st.write(f"**Instructions:** {doc['instructions']}")
                        st.code(doc.get("resume_markdown", ""), language="markdown")
            else:
                st.write("No history found.")
        except Exception as e:
            st.error(f"Error fetching history: {e}")
    else:
        st.warning("MongoDB not connected.")

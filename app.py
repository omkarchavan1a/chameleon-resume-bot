import streamlit as st
import os
import io
import pdfplumber
import json
from datetime import datetime
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from openai import OpenAI

# Custom Imports
from styles import inject_styles
from config import MASTER_PROFILE, JD_TEMPLATES, JD_CATEGORIES

# Load external configuration
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
    return None

resumes_collection = get_db_collection()

# ─── UI Setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chameleon Resume Bot", page_icon="🦎", layout="wide")
inject_styles()

# ─── Sidebar Settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='gecko-header'>🦎</div>", unsafe_allow_html=True)
    st.title("Settings")
    
    current_theme = st.selectbox("Resume Theme", ["Modern Dark", "Classic Blue", "Emerald", "Gold"], index=0)
    
    st.divider()
    st.markdown("### Profile Data")
    if st.button("🔄 Reset to Master Profile", help="Load pre-configured data for Omkar", type="secondary"):
        st.session_state.master_data = json.dumps(MASTER_PROFILE, indent=2)
        st.rerun()

# ─── Prompts and Logic ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Expert ATS Specialist and Professional Resume Writer.
Transform the user's "Master Experience" into a tailored, Chameleon-style resume:
1. Position Pivot: Highlight only relevant tools/experiences.
2. City Adaptation: Update contact header and language tone.
3. Keyword Optimization: Integrate JD keywords naturally.
4. Quantifiable Impact: Use 'Accomplished [X] by [Y] via [Z]' format.
5. Format: Clean Markdown only.
"""

def generate_resume(master_data, target_position, target_city, job_description):
    jd_section = f"\n\n**Job Description:**\n{job_description}" if job_description.strip() else ""
    user_prompt = f"""
Target Position: {target_position}
Target City: {target_city}
Master Data: {master_data}
{jd_section}
Output ONLY clean Markdown resume.
"""
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.6,
        max_tokens=2048
    )

# ─── Session State ────────────────────────────────────────────────────────────
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = ""
if "master_data" not in st.session_state:
    st.session_state.master_data = ""

# ─── Main UI ─────────────────────────────────────────────────────────────────
tab_gen, tab_hist = st.tabs(["✨ Generator Suite", "📜 History Archive"])

with tab_gen:
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("### 1. Intelligence Input")
        
        # Quick Select Pills (Role)
        st.markdown("**Quick Role Pick:**")
        role_cols = st.columns(len(JD_CATEGORIES))
        for i, (cat, roles) in enumerate(JD_CATEGORIES.items()):
            role_btn = role_cols[i].button(cat, key=f"role_{cat}", use_container_width=True)
            if role_btn:
                st.session_state.target_position = roles[0]
                st.session_state.job_description = JD_TEMPLATES.get(roles[0], "")

        # Target Inputs
        target_pos = st.text_input("Target Position", value=st.session_state.get('target_position', ""), placeholder="Software Engineer")
        target_city = st.text_input("Target City", placeholder="Pune, Remote, New York")
        
        # Data Input
        exp_tab1, exp_tab2 = st.tabs(["📝 Text Paste", "📂 PDF Upload"])
        with exp_tab1:
            m_data = st.text_area("Master Experience", value=st.session_state.master_data, height=300)
            st.session_state.master_data = m_data
        with exp_tab2:
            pdf_file = st.file_uploader("Upload Master Resume", type=["pdf"])
            if pdf_file:
                with st.spinner("Decoding PDF..."):
                    with pdfplumber.open(pdf_file) as pdf:
                        st.session_state.master_data = "\n".join([p.extract_text() for p in pdf.pages if p.extract_text()])
                st.success("PDF Content Analyzed!")

        job_desc = st.text_area("Job Description (Optional)", value=st.session_state.get('job_description', ""), height=150)

        if st.button("🦎 Generate Chameleon Resume", type="primary", use_container_width=True):
            if not target_pos or not target_city or not st.session_state.master_data:
                st.warning("Ensure all required fields are filled.")
            else:
                with st.status("🚀 Engineering Resume...", expanded=True) as status:
                    st.write("Analyzing master experience...")
                    st.write("Applying city-specific tailoring...")
                    st.write("Optimizing for ATS filters...")
                    try:
                        res = generate_resume(st.session_state.master_data, target_pos, target_city, job_desc)
                        st.session_state.generated_resume = res.choices[0].message.content
                        status.update(label="✅ Resume Engineered!", state="complete", expanded=False)
                        
                        # Save to Mongo
                        if resumes_collection is not None:
                            resumes_collection.insert_one({
                                "type": "generation",
                                "target_position": target_pos,
                                "target_city": target_city,
                                "resume_markdown": st.session_state.generated_resume,
                                "timestamp": datetime.utcnow()
                            })
                    except Exception as e:
                        st.error(f"Engine Failure: {e}")

    with col_out:
        st.markdown("### 2. Live Preview")
        if not st.session_state.generated_resume:
            st.markdown(
                f"<div style='border: 1px dashed rgba(255,255,255,0.2); border-radius: 12px; padding: 4rem; text-align: center; color: #64748b;'>"
                f"<span style='font-size: 3rem;'>📄</span><br>Start on the left to see the magic here.</div>", 
                unsafe_allow_html=True
            )
        else:
            with st.container(border=True):
                st.markdown(st.session_state.generated_resume)
            
            st.divider()
            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.download_button("⬇️ Download MD", st.session_state.generated_resume, file_name="chameleon_resume.md")
            with dcol2:
                if st.button("📋 Copy to Clipboard"):
                    st.toast("Copied to clipboard! (Simulated)")

with tab_hist:
    st.markdown("### 📜 Generation Archive")
    if resumes_collection is not None:
        try:
            history = list(resumes_collection.find().sort("timestamp", -1).limit(6))
            if history:
                for doc in history:
                    with st.expander(f"{doc.get('target_position', 'Unknown')} | {doc.get('timestamp').strftime('%Y-%m-%d %H:%M')}"):
                        st.markdown(doc['resume_markdown'])
            else:
                st.info("Archive is empty.")
        except:
            st.error("Database unavailable.")
    else:
        st.warning("Database connection not established.")

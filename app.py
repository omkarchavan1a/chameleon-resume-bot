import streamlit as st
import os
import io
import pdfplumber
import json
import re
from datetime import datetime
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from openai import OpenAI

# PDF Generation imports - try multiple methods
PDF_METHOD = None
try:
    import markdown as md_parser
    from playwright.sync_api import sync_playwright
    PDF_METHOD = "playwright"
except ImportError as e:
    pass

# Fallback to fpdf2 if Playwright not available
if PDF_METHOD is None:
    try:
        from fpdf import FPDF
        PDF_METHOD = "fpdf"
    except ImportError:
        pass

if PDF_METHOD is None:
    st.warning("⚠️ PDF generation not available. Install dependencies:\n\n`pip install playwright markdown`\nor\n`pip install fpdf2`")

# Custom Imports
from styles import inject_styles, get_theme_css, get_industry_badge_css
from config import MASTER_PROFILE, JD_TEMPLATES, JD_CATEGORIES, RESUME_THEMES, INDUSTRY_TEMPLATES, RESUME_STRUCTURES, INDUSTRY_SAMPLE_CONTENT, HTML_TEMPLATES
from resume_engine import ResumeEngine

# ─── PDF Generation Helper ────────────────────────────────────────────────────
PDF_CSS_STYLES = """
@page {
    size: A4;
    margin: 2cm;
}
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}
h1 {
    font-size: 24pt;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
}
h2 {
    font-size: 16pt;
    color: #34495e;
    margin-top: 25px;
    margin-bottom: 15px;
}
h3 {
    font-size: 13pt;
    color: #2c3e50;
}
strong {
    color: #2c3e50;
}
em {
    color: #7f8c8d;
    font-size: 10pt;
}
ul {
    margin: 10px 0;
    padding-left: 20px;
}
li {
    margin: 5px 0;
}
p {
    margin: 10px 0;
}
"""

@st.cache_resource(show_spinner=False)
def ensure_playwright_browsers():
    """Ensure Playwright browsers and system deps are installed (runs once per session)."""
    import subprocess
    try:
        # First try launching — if it works, nothing to do
        with sync_playwright() as p:
            browser = p.chromium.launch()
            browser.close()
        return True
    except Exception:
        pass

    # Install system-level shared libraries (needed on Streamlit Cloud / Linux)
    try:
        subprocess.run(["playwright", "install-deps", "chromium"], check=True,
                       capture_output=True)
    except Exception:
        pass  # May fail on Windows/Mac — that's fine, libs are already there

    # Install the browser binaries
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True,
                       capture_output=True)
    except Exception as e:
        return False

    return True

def generate_pdf_local(markdown_content):
    """Generate PDF using available method (WeasyPrint or markdown_pdf)."""
    if PDF_METHOD is None:
        return None
    
    try:
        if PDF_METHOD == "playwright":
            # Use Playwright for high-fidelity conversion
            html_content = md_parser.markdown(markdown_content, extensions=['extra'])
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>{PDF_CSS_STYLES}</style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(full_html)
                pdf_bytes = page.pdf(format="A4", print_background=True)
                browser.close()
                return pdf_bytes
            
        elif PDF_METHOD == "fpdf":
            # Use fpdf2 fallback - pure Python, no external dependencies
            try:
                from fpdf import FPDF
                
                # Create PDF with proper margins
                pdf = FPDF()
                pdf.set_margins(15, 15, 15)
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                
                # Track position for proper layout
                effective_width = pdf.w - pdf.l_margin - pdf.r_margin
                
                # Parse markdown and add to PDF
                lines = markdown_content.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        pdf.ln(5)
                        continue
                    
                    # Handle headers
                    if line.startswith('# '):
                        pdf.set_font('Helvetica', 'B', 16)
                        text = line[2:].encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(effective_width, 10, text, ln=True)
                        pdf.ln(5)
                    elif line.startswith('## '):
                        pdf.set_font('Helvetica', 'B', 14)
                        text = line[3:].encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(effective_width, 8, text, ln=True)
                        pdf.ln(3)
                    elif line.startswith('### '):
                        pdf.set_font('Helvetica', 'B', 12)
                        text = line[4:].encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(effective_width, 6, text, ln=True)
                    elif line.startswith('- ') or line.startswith('* '):
                        pdf.set_font('Helvetica', '', 11)
                        bullet_text = ('- ' + line[2:]).encode('latin-1', 'replace').decode('latin-1')
                        pdf.cell(effective_width, 6, bullet_text, ln=True)
                    elif '**' in line:
                        # Handle inline bold
                        pdf.set_font('Helvetica', '', 11)
                        text = line.replace('**', '').encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(effective_width, 6, text)
                    else:
                        pdf.set_font('Helvetica', '', 11)
                        # Remove other markdown formatting
                        clean_line = line.replace('*', '').replace('`', '')
                        clean_line = clean_line.encode('latin-1', 'replace').decode('latin-1')
                        pdf.multi_cell(effective_width, 6, clean_line)
                
                output = io.BytesIO()
                pdf.output(output)
                return output.getvalue()
            except Exception as e:
                st.error(f"PDF generation failed: {e}")
                return None
            
    except Exception as e:
        st.error(f"PDF generation error: {e}")
        return None


def generate_themed_pdf(markdown_content, theme_name='modern'):
    """Generate PDF with theme-specific styling."""
    if PDF_METHOD == "playwright":
        # Use Playwright with theme CSS
        try:
            html_content = md_parser.markdown(markdown_content, extensions=['extra'])
            theme_css = get_theme_css(theme_name)
            
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>{PDF_CSS_STYLES}</style>
                <style>{theme_css}</style>
            </head>
            <body>
                <div class="resume-container">
                    {html_content}
                </div>
            </body>
            </html>
            """
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(full_html)
                pdf_bytes = page.pdf(format="A4", print_background=True)
                browser.close()
                return pdf_bytes
        except Exception as e:
            st.error(f"Themed PDF generation failed: {e}")
            # Fallback to local
            return generate_pdf_local(markdown_content)
    else:
        # Use standard PDF generation
        return generate_pdf_local(markdown_content)


def generate_html_pdf(markdown_content, template_path=None, llm_data=None):
    """Generate PDF using HTML templates and ResumeEngine via Playwright.
    
    Args:
        markdown_content: The resume markdown content
        template_path: Path to HTML template
        llm_data: Optional dict with ATS analysis (ats_score, keyword_match, strengths, improvements, etc.)
    """
    if PDF_METHOD != "playwright":
        return generate_pdf_local(markdown_content)
        
    try:
        if not template_path:
            template_path = list(HTML_TEMPLATES.values())[0]
            
        engine = ResumeEngine()
        data = engine.parse_markdown(markdown_content)
        # Merge LLM data if provided
        if llm_data:
            data["llm_analysis"] = llm_data
        html_rendered = engine.render_html(template_path, data)
        
        ready = ensure_playwright_browsers()
        if not ready:
            st.warning("⚠️ Chromium could not be set up. Generating a basic PDF instead.")
            return generate_pdf_local(markdown_content)

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.set_content(html_rendered)
            page.wait_for_load_state("networkidle")
            pdf_bytes = page.pdf(
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"}
            )
            browser.close()
            return pdf_bytes
    except Exception as e:
        st.error(f"PDF generation error: {e}")
        return generate_pdf_local(markdown_content)


# Load external configuration
load_dotenv("backend/.env")

# ─── Admin Credentials ───────────────────────────────────────────────────────
ADMIN_EMAIL = "omkarchavan1500@gmail.com"
ADMIN_PASSWORD = "omkarchavan@1"

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
def get_db_collections():
    if MONGODB_URI:
        try:
            mongo_client = MongoClient(
                MONGODB_URI, 
                serverSelectionTimeoutMS=10000, 
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=True
            )
            mongo_client.admin.command('ping')
            db = mongo_client[DB_NAME]
            # Create TTL index to auto-delete resumes after 12 days (1036800 seconds)
            try:
                db.resumes.create_index(
                    [("timestamp", 1)],
                    expireAfterSeconds=1036800,  # 12 days
                    background=True
                )
            except Exception:
                pass  # Index may already exist
            return db.resumes, db.users
        except Exception as e:
            st.warning(f"Could not connect to MongoDB: {str(e)}")
            return None, None
    return None, None

resumes_collection, users_collection = get_db_collections()

# ─── Helper Functions ─────────────────────────────────────────────────────────
def validate_email(email):
    regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(regex, email) is not None

def validate_phone(phone):
    digits = re.sub(r'\D', '', phone)
    return len(digits) == 10 or (len(digits) == 12 and digits.startswith('91'))

def format_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    return phone

# ─── UI Setup ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chameleon Resume Bot", page_icon="🦎", layout="wide")
inject_styles()

# ─── Sidebar Settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='gecko-header'>🦎</div>", unsafe_allow_html=True)
    st.title("Settings")
    
    template_names = list(HTML_TEMPLATES.keys())
    # Sync selectbox with session state
    current_idx = 0
    if "selected_template" in st.session_state:
        try:
            current_idx = template_names.index(st.session_state.selected_template)
        except ValueError:
            current_idx = 0
            
    selected_t = st.selectbox("Resume Theme", template_names, index=current_idx)
    if selected_t != st.session_state.get("selected_template"):
        st.session_state.selected_template = selected_t
        st.rerun()
    
    st.divider()
    st.markdown("### Profile Data")
    if st.button("🔄 Reset to Master Profile", help="Load pre-configured data for Omkar", type="secondary"):
        st.session_state.master_data = json.dumps(MASTER_PROFILE, indent=2)
        st.rerun()

# ─── Prompts and Logic ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an Expert ATS Specialist and Professional Resume Writer.
Transform the user's "Master Experience" into a tailored, Chameleon-style resume:
1. Start with candidate name as: # [Full Name]
2. Position Pivot: Highlight only relevant tools/experiences.
3. City Adaptation: Update contact header and language tone.
4. Keyword Optimization: Integrate JD keywords naturally.
5. Quantifiable Impact: Use 'Accomplished [X] by [Y] via [Z]' format.
6. Format: Clean Markdown only.
"""

def generate_resume(master_data, target_position, target_city, job_description):
    jd_section = f"\n\n**Job Description:**\n{job_description}" if job_description.strip() else ""
    user_prompt = f"""
Target Position: {target_position}
Target City: {target_city}
Master Data: {master_data}
{jd_section}

Instructions:
- Extract the candidate's full name from the Master Data
- Start the resume with: # [Full Name]
- Include title and contact info on the next line
- Output ONLY clean Markdown resume.
"""
    return client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_prompt}],
        temperature=0.6,
        max_tokens=2048
    )


def generate_ats_analysis(resume_markdown, job_description, target_position):
    """Generate ATS analysis and AI insights for the resume."""
    analysis_prompt = f"""
You are an ATS (Applicant Tracking System) expert. Analyze this resume for the position: {target_position}

Resume:
{resume_markdown}

Job Description:
{job_description if job_description.strip() else "Not provided"}

Provide a JSON response with:
1. candidate_name (string): The candidate's full name from the resume
2. ats_score (number 0-100): Estimated ATS compatibility score
3. keyword_match (number 0-100): Keyword match percentage with job description
4. strengths (array): Top 3 strengths of this resume
5. improvements (array): Top 3 specific improvements to make
6. missing_keywords (array): Important keywords missing from the resume
7. summary (string): Brief 2-sentence analysis summary

Output ONLY valid JSON in this format:
{{"candidate_name": "John Doe", "ats_score": 85, "keyword_match": 78, "strengths": [...], "improvements": [...], "missing_keywords": [...], "summary": "..."}}
"""
    try:
        res = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are an expert ATS analyzer."}, {"role": "user", "content": analysis_prompt}],
            temperature=0.3,
            max_tokens=1024
        )
        import json as json_module
        content = res.choices[0].message.content
        if content is None:
            raise ValueError("Empty response from API")
        # Extract JSON from possible markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json_module.loads(content)
    except Exception as e:
        # Return default analysis if generation fails
        return {
            "candidate_name": "Candidate",
            "ats_score": 75,
            "keyword_match": 70,
            "strengths": ["Well-structured format", "Clear experience descriptions", "Professional presentation"],
            "improvements": ["Add more quantifiable achievements", "Include relevant certifications", "Expand skills section"],
            "missing_keywords": [],
            "summary": "Resume is well-formatted and ATS-friendly with room for keyword optimization."
        }

# ─── Session State ────────────────────────────────────────────────────────────
if "generated_resume" not in st.session_state:
    st.session_state.generated_resume = ""
if "master_data" not in st.session_state:
    st.session_state.master_data = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False
if "llm_analysis" not in st.session_state:
    st.session_state.llm_analysis = None

# ─── Main Navigation ───────────────────────────────────────────────────────────
# Check if admin mode is requested
query_params = st.query_params
if query_params.get("admin") == "true":
    st.session_state.show_admin = True
else:
    if "show_admin" not in st.session_state:
        st.session_state.show_admin = False

# ─── ADMIN PANEL ─────────────────────────────────────────────────────────────
if st.session_state.show_admin:
    st.markdown("# 🔐 Admin Dashboard")
    st.markdown("---")
    
    # Admin Login
    if not st.session_state.admin_logged_in:
        with st.form("admin_login"):
            st.markdown("### Admin Login")
            admin_email = st.text_input("Email", value="omkarchavan1500@gmail.com")
            admin_password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if admin_email == ADMIN_EMAIL and admin_password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    else:
        # Admin Dashboard Content
        col1, col2, col3 = st.columns(3)
        
        if users_collection is not None and resumes_collection is not None:
            try:
                total_users = users_collection.count_documents({})
                total_resumes = resumes_collection.count_documents({})
                
                # Today's users
                today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
                today_users = users_collection.count_documents({"registered_at": {"$gte": today_start}})
                
                with col1:
                    st.metric("Total Users", total_users)
                with col2:
                    st.metric("Total Resumes", total_resumes)
                with col3:
                    st.metric("Today's Users", today_users)
                
                st.markdown("---")
                st.markdown("### 👥 Registered Users")
                
                # Get all users with their resume counts
                users = list(users_collection.find().sort("registered_at", -1))
                
                if users:
                    for user in users:
                        email = user.get("email", "Unknown")
                        phone = format_phone(user.get("phone", ""))
                        reg_date = user.get("registered_at", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")
                        last_active = user.get("last_active", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")
                        
                        # Count resumes for this user
                        resume_count = resumes_collection.count_documents({"user_email": email})
                        
                        with st.expander(f"📧 {email} | 📱 {phone} | 📝 {resume_count} resumes"):
                            st.write(f"**Registered:** {reg_date}")
                            st.write(f"**Last Active:** {last_active}")
                            
                            if resume_count > 0:
                                st.markdown("**Recent Resumes:**")
                                user_resumes = list(resumes_collection.find(
                                    {"user_email": email}
                                ).sort("timestamp", -1).limit(3))
                                
                                for resume in user_resumes:
                                    pos = resume.get("target_position", "Unknown Position")
                                    city = resume.get("target_city", "Unknown City")
                                    date = resume.get("timestamp", datetime.utcnow()).strftime("%Y-%m-%d %H:%M")
                                    
                                    with st.container(border=True):
                                        st.markdown(f"**{pos}** — {city} ({date})")
                                        st.markdown(resume.get("resume_markdown", "")[:500] + "...")
                else:
                    st.info("No users registered yet.")
                    
            except Exception as e:
                st.error(f"Database error: {str(e)}")
        else:
            st.warning("Database connection not established.")
        
        if st.button("Logout", type="secondary"):
            st.session_state.admin_logged_in = False
            st.session_state.show_admin = False
            st.query_params.clear()
            st.rerun()
        
        if st.button("← Back to Resume Generator"):
            st.session_state.show_admin = False
            st.query_params.clear()
            st.rerun()

# ─── USER REGISTRATION FLOW ────────────────────────────────────────────────────
elif not st.session_state.user_registered:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align:center; font-size:4rem;'>🦎</div>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center; background: linear-gradient(135deg, #4f9cff 0%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Chameleon Resume Bot</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color: #94a3b8;'>AI-Powered ATS Resume Generator</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("user_registration", clear_on_submit=False):
            st.markdown("### 👤 Enter Your Details")
            st.markdown("Please provide your contact information to get started.")
            
            email = st.text_input("Email Address *", placeholder="you@example.com")
            phone = st.text_input("Phone Number *", placeholder="9876543210 or +91 9876543210")
            
            submitted = st.form_submit_button("Continue to Resume Generator →", use_container_width=True, type="primary")
            
            if submitted:
                if not email or not phone:
                    st.error("Please fill in all required fields.")
                elif not validate_email(email):
                    st.error("Please enter a valid email address.")
                elif not validate_phone(phone):
                    st.error("Please enter a valid 10-digit phone number.")
                else:
                    # Store in session
                    st.session_state.user_email = email.lower()
                    st.session_state.user_phone = phone
                    st.session_state.user_registered = True
                    
                    # Save to MongoDB
                    if users_collection is not None:
                        try:
                            existing = users_collection.find_one({"email": email.lower()})
                            if existing:
                                users_collection.update_one(
                                    {"email": email.lower()},
                                    {"$set": {"last_active": datetime.utcnow()}}
                                )
                            else:
                                users_collection.insert_one({
                                    "email": email.lower(),
                                    "phone": re.sub(r'\D', '', phone)[-10:],  # Store last 10 digits
                                    "registered_at": datetime.utcnow(),
                                    "last_active": datetime.utcnow()
                                })
                            st.success("Registration successful!")
                        except Exception as e:
                            st.warning(f"Could not save to database: {e}")
                    
                    st.rerun()
        
        st.markdown("---")
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("🎯 ATS Optimized &nbsp;•&nbsp; 🤖 AI-Powered &nbsp;•&nbsp; ⚡ Instant Results")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Admin link (subtle)
        st.markdown("<div style='text-align:center; margin-top:2rem;'>", unsafe_allow_html=True)
        if st.button("🔐 Admin Panel", type="tertiary"):
            st.session_state.show_admin = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─── MAIN RESUME GENERATOR ─────────────────────────────────────────────────────
else:
    # Show user info in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Current User")
        st.write(f"**Email:** {st.session_state.user_email}")
        st.write(f"**Phone:** {format_phone(st.session_state.user_phone)}")
        if st.button("🔄 Change User", type="secondary", use_container_width=True):
            st.session_state.user_registered = False
            st.session_state.user_email = ""
            st.session_state.user_phone = ""
            st.rerun()
        st.markdown("---")
        if st.button("🔐 Admin Panel", type="tertiary", use_container_width=True):
            st.session_state.show_admin = True
            st.rerun()
    
    # Main tabs
    tab_gen, tab_hist = st.tabs(["✨ Generator Suite", "📜 History Archive"])

    with tab_gen:

        col_in, col_out = st.columns([1, 1], gap="large")

        with col_in:
            st.markdown("### 1. Intelligence Input")
            
            # Quick Select Pills (Role)
            st.markdown("**Quick Role Pick:**")
            role_pills = list(JD_CATEGORIES.keys())
            p_cols = st.columns(len(role_pills))
            for i, cat in enumerate(role_pills):
                if p_cols[i].button(cat, key=f"p_{cat}", use_container_width=True):
                    st.session_state.target_position = JD_CATEGORIES[cat][0]
                    st.session_state.job_description = JD_TEMPLATES.get(JD_CATEGORIES[cat][0], "")

            # Target Inputs
            target_pos = st.text_input("Target Position", value=st.session_state.get('target_position', ""), placeholder="Software Engineer")
            target_city = st.text_input("Target City", placeholder="Pune, Remote, New York")
            job_desc = st.text_area("Job Description (Optional)", value=st.session_state.get('job_description', ""), height=150)
            
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

            st.markdown("---")
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
                            
                            # Generate ATS analysis
                            st.write("🔍 Generating ATS analysis...")
                            st.session_state.llm_analysis = generate_ats_analysis(
                                st.session_state.generated_resume, 
                                job_desc, 
                                target_pos
                            )
                            
                            status.update(label="✅ Resume Engineered!", state="complete", expanded=False)
                            
                            # Save to Mongo
                            if resumes_collection is not None:
                                resume_doc = {
                                    "user_email": st.session_state.user_email,
                                    "target_position": target_pos,
                                    "target_city": target_city,
                                    "resume_markdown": st.session_state.generated_resume,
                                    "llm_analysis": st.session_state.llm_analysis,
                                    "timestamp": datetime.utcnow()
                                }
                                resumes_collection.insert_one(resume_doc)
                        except Exception as e:
                            st.error(f"Engine Failure: {e}")

        with col_out:
            st.markdown("### 2. Live Preview")
            if not st.session_state.generated_resume:
                st.markdown(
                    f"<div style='border: 1px dashed rgba(255,255,255,0.2); border-radius: 20px; padding: 4rem; text-align: center; color: #64748b; background: rgba(255,255,255,0.02);'>"
                    f"<span style='font-size: 4rem; display: block; margin-bottom: 1rem;'>📄</span>Prepare your inputs to see the magic.</div>", 
                    unsafe_allow_html=True
                )
                if st.button("✨ Load Sample Data to Preview Templates"):
                    st.session_state.master_data = "# Sarah Chen\nFull-Stack Engineer | sarah@example.com\n\n## Summary\nExpert in React and Node.js with 5 years experience.\n\n## Experience\n### Senior Engineer | Tech Corp\n2020-Present\n- Led frontend team of 5."
                    st.session_state.generated_resume = st.session_state.master_data
                    st.rerun()
            else:
                # Preview mode selection
                p_tabs = st.tabs(["✨ Preview", "🎨 Design Gallery", "📝 Source", "🤖 AI Analysis"])
                
                with p_tabs[0]:
                    # Mini Gallery Selection
                    st.markdown('<p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 10px;">Quick Theme Switch:</p>', unsafe_allow_html=True)
                    mini_cols = st.columns(5)
                    # Show all available templates from config
                    template_items = list(HTML_TEMPLATES.items())
                    for i, (name, path) in enumerate(template_items):
                        with mini_cols[i % 5]:
                            # Smaller buttons as "pills"
                            is_selected = st.session_state.get('selected_template') == name
                            if st.button(name[:10] + "..", key=f"mini_{name}", help=name, type="primary" if is_selected else "secondary"):
                                st.session_state.selected_template = name
                                st.rerun()
                    
                    # Main Preview
                    with st.spinner("Rendering..."):
                        try:
                            engine = ResumeEngine()
                            data = engine.parse_markdown(st.session_state.generated_resume)
                            # Add LLM analysis to data for website preview only
                            data["llm_analysis"] = st.session_state.get('llm_analysis')
                            t_id = st.session_state.get('selected_template', 'Minimalist')
                            t_path = HTML_TEMPLATES.get(t_id)
                            html_rendered = engine.render_html(t_path, data)
                            
                            st.markdown(f"""
                                <div style="background: white; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); overflow: hidden; height: 750px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                                    <iframe srcdoc='{html_rendered.replace("'", "&apos;")}' style="width: 100%; height: 100%; border: none;"></iframe>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Actions below preview
                            st.markdown("<br>", unsafe_allow_html=True)
                            act_col1, act_col2 = st.columns(2)
                            with act_col1:
                                if PDF_METHOD:
                                    # PDF without LLM analysis (website only)
                                    pdf_bytes = generate_html_pdf(
                                        st.session_state.generated_resume, 
                                        t_path, 
                                        None  # No LLM analysis in PDF
                                    )
                                    if pdf_bytes:
                                        st.download_button("📥 Download PDF", pdf_bytes, file_name=f"resume_{t_id.lower().replace(' ', '_')}.pdf", mime="application/pdf", use_container_width=True)
                                    else:
                                        st.button("📥 Download PDF", disabled=True, use_container_width=True)
                            with act_col2:
                                st.button("📋 Copy Link", use_container_width=True)
                                
                        except Exception as e:
                            st.error(f"Render Error: {e}")

                with p_tabs[1]:
                    st.markdown("### 🎨 Theme Gallery")
                    st.markdown('<p style="color: #94a3b8; margin-bottom: 20px;">Explore all 10 professional designs tailored with your data.</p>', unsafe_allow_html=True)
                    
                    g_cols = st.columns(2)
                    template_items = list(HTML_TEMPLATES.items())
                    
                    for i, (name, path) in enumerate(template_items):
                        with g_cols[i % 2]:
                            with st.container(border=True):
                                st.markdown(f"#### {name}")
                                
                                # Mini preview (HTML only, no PDF generation here for speed)
                                try:
                                    engine = ResumeEngine()
                                    data = engine.parse_markdown(st.session_state.generated_resume)
                                    mini_html = engine.render_html(path, data)
                                    
                                    # Scale down for gallery preview
                                    styled_mini = mini_html.replace("</head>", """
                                        <style>
                                            body { 
                                                transform: scale(0.35); 
                                                transform-origin: top left; 
                                                width: 285%; 
                                                height: 285%; 
                                                overflow: hidden; 
                                                background: white; 
                                                pointer-events: none;
                                            }
                                            ::-webkit-scrollbar { display: none; }
                                        </style>
                                    </head>""")
                                    
                                    st.components.v1.html(styled_mini, height=300, scrolling=False)
                                except Exception as e:
                                    st.error(f"Preview failed: {e}")
                                
                                # Quick action buttons
                                bcol1, bcol2 = st.columns(2)
                                with bcol1:
                                    if st.button(f"✨ Select", key=f"sel_{name}", use_container_width=True):
                                        st.session_state.selected_template = name
                                        st.toast(f"Theme '{name}' applied!")
                                        st.rerun()
                                with bcol2:
                                    # Link to a dedicated download or just inform
                                    st.button("📄 Info", key=f"info_{name}", use_container_width=True, disabled=True)
                                
                                st.markdown("<br>", unsafe_allow_html=True)

                with p_tabs[2]:
                    with st.container(border=True):
                        st.markdown(st.session_state.generated_resume)
                
                st.divider()
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    st.download_button("📄 MD", st.session_state.generated_resume, file_name="chameleon_resume.md", use_container_width=True)
                with dcol2:
                    # PDF download using template generation
                    if PDF_METHOD:
                        template_path = HTML_TEMPLATES.get(st.session_state.selected_template)
                        pdf_bytes = generate_html_pdf(
                            st.session_state.generated_resume, 
                            template_path,
                            st.session_state.get('llm_analysis')
                        )
                        if pdf_bytes:
                            st.download_button("📄 PDF", pdf_bytes, file_name="chameleon_resume.pdf", mime="application/pdf", use_container_width=True)
                        else:
                            st.button("📄 PDF", disabled=True, use_container_width=True)
                    else:
                        st.button("📄 PDF", disabled=True, help="Install weasyprint", use_container_width=True)
                with dcol3:
                    if st.button("📋 Copy", use_container_width=True):
                        st.toast("Copied to clipboard! (Simulated)")

                with p_tabs[3]:
                    st.markdown("### 🤖 AI Analysis & ATS Score")
                    llm_data = st.session_state.get('llm_analysis')
                    if llm_data:
                        candidate_name = llm_data.get('candidate_name', 'Candidate')
                        st.markdown(f"## 👤 {candidate_name}")
                        col1, col2 = st.columns(2)
                        ats_score = llm_data.get('ats_score', 0)
                        keyword_match = llm_data.get('keyword_match', 0)
                        
                        with col1:
                            st.metric("ATS Score", f"{ats_score}/100", delta=None)
                        with col2:
                            st.metric("Keyword Match", f"{keyword_match}%", delta=None)
                        
                        if llm_data.get('summary'):
                            st.info(llm_data.get('summary'))
                        
                        scol1, scol2 = st.columns(2)
                        with scol1:
                            st.markdown("**✓ Strengths**")
                            for s in llm_data.get('strengths', [])[:3]:
                                st.success(s)
                        with scol2:
                            st.markdown("**⚡ Improvements**")
                            for i in llm_data.get('improvements', [])[:3]:
                                st.warning(i)
                        
                        if llm_data.get('missing_keywords'):
                            st.markdown("**📝 Missing Keywords**")
                            st.error(", ".join(llm_data.get('missing_keywords', [])[:5]))
                    else:
                        st.info("Generate a resume to see AI analysis.")

    with tab_hist:
        st.markdown("### 📜 Generation Archive")
        if resumes_collection is not None:
            try:
                # Show only current user's resumes if user is logged in
                query = {}
                if st.session_state.user_email:
                    query = {"user_email": st.session_state.user_email}
                
                history = list(resumes_collection.find(query).sort("timestamp", -1).limit(10))
                if history:
                    for doc in history:
                        user_tag = ""
                        if doc.get("user_email"):
                            user_tag = f" | 👤 {doc.get('user_email')}"
                        
                        with st.expander(f"{doc.get('target_position', 'Unknown')} | {doc.get('timestamp').strftime('%Y-%m-%d %H:%M')}{user_tag}"):
                            st.markdown(doc['resume_markdown'])
                else:
                    st.info("Archive is empty.")
            except Exception as e:
                st.error(f"Database error: {str(e)}")
        else:
            st.warning("Database connection not established.")

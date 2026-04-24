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
    from weasyprint import HTML, CSS
    PDF_METHOD = "weasyprint"
except (ImportError, OSError) as e:
    # OSError happens on Windows when GTK libraries are missing
    pass

# Fallback to fpdf2 if WeasyPrint not available or failed
if PDF_METHOD is None:
    try:
        from fpdf import FPDF
        PDF_METHOD = "fpdf"
    except ImportError:
        pass

if PDF_METHOD is None:
    st.warning("⚠️ PDF generation not available. Install dependencies:\n\n`pip install weasyprint markdown`\nor\n`pip install fpdf2`")

# Custom Imports
from styles import inject_styles, get_theme_css, get_industry_badge_css
from config import MASTER_PROFILE, JD_TEMPLATES, JD_CATEGORIES, RESUME_THEMES, INDUSTRY_TEMPLATES, RESUME_STRUCTURES, INDUSTRY_SAMPLE_CONTENT

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

def generate_pdf_local(markdown_content):
    """Generate PDF using available method (WeasyPrint or markdown_pdf)."""
    if PDF_METHOD is None:
        return None
    
    try:
        if PDF_METHOD == "weasyprint":
            # Use WeasyPrint
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
            pdf_bytes = HTML(string=full_html).write_pdf()
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
    if PDF_METHOD == "weasyprint":
        # Use WeasyPrint with theme CSS
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
            pdf_bytes = HTML(string=full_html).write_pdf()
            return pdf_bytes
        except Exception as e:
            st.error(f"Themed PDF generation failed: {e}")
            # Fallback to local
            return generate_pdf_local(markdown_content)
    else:
        # Use standard PDF generation
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
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "user_phone" not in st.session_state:
    st.session_state.user_phone = ""
if "user_registered" not in st.session_state:
    st.session_state.user_registered = False
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

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
    tab_gen, tab_templates, tab_hist = st.tabs(["✨ Generator Suite", "🎨 Templates", "📜 History Archive"])

    with tab_templates:
        # Initialize session state for template selection
        if 'selected_industry' not in st.session_state:
            st.session_state.selected_industry = 'tech'
        if 'selected_theme' not in st.session_state:
            st.session_state.selected_theme = 'modern'
        if 'selected_structure' not in st.session_state:
            st.session_state.selected_structure = 'chronological'
        if 'preview_content' not in st.session_state:
            st.session_state.preview_content = None
            
        # Inject template gallery CSS
        st.markdown(get_industry_badge_css(), unsafe_allow_html=True)
        
        st.markdown("### 🎨 Resume Template Gallery")
        st.markdown("Browse industry-specific templates with different visual themes and structures. Preview before downloading.")
        st.markdown("---")
        
        # Create filter sidebar and main content layout
        filter_col, main_col = st.columns([1, 3])
        
        with filter_col:
            st.markdown("#### 🎯 Filters")
            
            # Industry Filter
            st.markdown("**Industry**")
            industry_options = {key: f"{val['icon']} {val['name']}" for key, val in INDUSTRY_TEMPLATES.items()}
            selected_industry = st.selectbox(
                "Select Industry",
                options=list(industry_options.keys()),
                format_func=lambda x: industry_options[x],
                index=list(industry_options.keys()).index(st.session_state.selected_industry),
                label_visibility="collapsed"
            )
            
            # Theme Filter
            st.markdown("**Visual Theme**")
            theme_options = {key: f"{val['icon']} {val['name']}" for key, val in RESUME_THEMES.items()}
            selected_theme = st.selectbox(
                "Select Theme",
                options=list(theme_options.keys()),
                format_func=lambda x: theme_options[x],
                index=list(theme_options.keys()).index(st.session_state.selected_theme),
                label_visibility="collapsed"
            )
            
            # Structure Filter
            st.markdown("**Layout Structure**")
            structure_options = {key: f"{val['icon']} {val['name']}" for key, val in RESUME_STRUCTURES.items()}
            selected_structure = st.selectbox(
                "Select Structure",
                options=list(structure_options.keys()),
                format_func=lambda x: structure_options[x],
                index=list(structure_options.keys()).index(st.session_state.selected_structure),
                label_visibility="collapsed"
            )
            
            # Update session state
            st.session_state.selected_industry = selected_industry
            st.session_state.selected_theme = selected_theme
            st.session_state.selected_structure = selected_structure
            
            # Show selected filters info
            st.divider()
            st.markdown("**Selected Configuration**")
            st.caption(f"Industry: {INDUSTRY_TEMPLATES[selected_industry]['name']}")
            st.caption(f"Theme: {RESUME_THEMES[selected_theme]['name']}")
            st.caption(f"Structure: {RESUME_STRUCTURES[selected_structure]['name']}")
            
        with main_col:
            # Display all industry templates as cards
            st.markdown("#### 📋 Industry Templates")
            
            # Show templates for selected industry
            industry_data = INDUSTRY_TEMPLATES[selected_industry]
            sample_content = INDUSTRY_SAMPLE_CONTENT.get(selected_industry, INDUSTRY_SAMPLE_CONTENT['general'])
            
            # Create template card
            with st.container(border=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                            <span style="font-size: 2rem;">{industry_data['icon']}</span>
                            <div>
                                <h4 style="margin: 0; color: {industry_data['badge_color']};">{industry_data['name']} Template</h4>
                                <p style="margin: 0; font-size: 0.85rem; color: #666;">{industry_data['summary_focus']}</p>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Skills highlighted
                    skills_text = " • ".join(industry_data['skills_highlight'])
                    st.caption(f"**Key Skills:** {skills_text}")
                    
                    # Theme preview
                    theme_data = RESUME_THEMES[selected_theme]
                    st.caption(f"**Theme:** {theme_data['name']} - {theme_data['description']}")
                    
                with col2:
                    # Preview button
                    if st.button("👁️ Preview", use_container_width=True, type="primary"):
                        st.session_state.preview_content = sample_content
                        st.session_state.preview_theme = selected_theme
                    
                    # Download buttons
                    if PDF_METHOD:
                        pdf_bytes = generate_themed_pdf(sample_content, selected_theme)
                        if pdf_bytes:
                            st.download_button(
                                "📄 PDF",
                                data=pdf_bytes,
                                file_name=f"{selected_industry}-{selected_theme}-resume.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                    
                    st.download_button(
                        "📄 Markdown",
                        data=sample_content,
                        file_name=f"{selected_industry}-{selected_theme}-resume.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
            
            # Show Live Preview if selected
            if st.session_state.preview_content:
                st.divider()
                st.markdown("#### 👁️ Live Preview")
                
                preview_theme = st.session_state.get('preview_theme', 'modern')
                theme_css = get_theme_css(preview_theme)
                
                # Render styled preview
                try:
                    html_content = md_parser.markdown(st.session_state.preview_content, extensions=['extra'])
                except:
                    html_content = st.session_state.preview_content.replace('# ', '<h1>').replace('## ', '<h2>').replace('\n', '<br>')
                
                preview_html = f"""
                <style>{theme_css}</style>
                <div class="resume-container">
                    {html_content}
                </div>
                """
                st.markdown(preview_html, unsafe_allow_html=True)
            
            # Show all industries in expandable section
            with st.expander("📁 Browse All Industry Templates"):
                for ind_key, ind_data in INDUSTRY_TEMPLATES.items():
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.markdown(f"**{ind_data['icon']} {ind_data['name']}** - {ind_data['summary_focus']}")
                    with cols[1]:
                        if st.button("Select", key=f"select_{ind_key}", use_container_width=True):
                            st.session_state.selected_industry = ind_key
                            st.rerun()
    
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
                            
                            # Save to Mongo with user_email
                            if resumes_collection is not None:
                                resume_doc = {
                                    "type": "generation",
                                    "target_position": target_pos,
                                    "target_city": target_city,
                                    "resume_markdown": st.session_state.generated_resume,
                                    "timestamp": datetime.utcnow()
                                }
                                if st.session_state.user_email:
                                    resume_doc["user_email"] = st.session_state.user_email
                                    # Update user's last_active
                                    if users_collection is not None:
                                        users_collection.update_one(
                                            {"email": st.session_state.user_email},
                                            {"$set": {"last_active": datetime.utcnow()}}
                                        )
                                resumes_collection.insert_one(resume_doc)
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
                dcol1, dcol2, dcol3 = st.columns(3)
                with dcol1:
                    st.download_button("📄 MD", st.session_state.generated_resume, file_name="chameleon_resume.md", use_container_width=True)
                with dcol2:
                    # PDF download using local generation
                    if PDF_METHOD:
                        pdf_bytes = generate_pdf_local(st.session_state.generated_resume)
                        if pdf_bytes:
                            st.download_button("📄 PDF", pdf_bytes, file_name="chameleon_resume.pdf", mime="application/pdf", use_container_width=True)
                        else:
                            st.button("📄 PDF", disabled=True, use_container_width=True)
                    else:
                        st.button("📄 PDF", disabled=True, help="Install weasyprint or markdown-pdf", use_container_width=True)
                with dcol3:
                    if st.button("📋 Copy", use_container_width=True):
                        st.toast("Copied to clipboard! (Simulated)")

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

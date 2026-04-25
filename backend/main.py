"""
Chameleon Resume Bot — FastAPI Backend
Powered by NVIDIA NIM API (meta/llama-3.3-70b-instruct)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from pydantic import BaseModel, field_validator
from openai import OpenAI
import os
import pathlib
import io
import pdfplumber
import re
from dotenv import load_dotenv
from datetime import datetime
from database import Database, get_db
from typing import Optional, List
import uuid
import markdown
from weasyprint import HTML, CSS

# Load external configuration from .env file
load_dotenv()
# ─── NVIDIA NIM Client ───────────────────────────────────────────────────────
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
if not NVIDIA_API_KEY:
    raise ValueError("NVIDIA_API_KEY environment variable is missing. Please configure backend/.env.")

BASE_URL       = "https://integrate.api.nvidia.com/v1"
MODEL          = "meta/llama-3.3-70b-instruct"

client = OpenAI(api_key=NVIDIA_API_KEY, base_url=BASE_URL)

# ─── Database Lifespan ────────────────────────────────────────────────────────
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await Database.connect()
    yield
    # Shutdown: Close connection
    await Database.disconnect()

# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(title="Chameleon Resume Bot", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
FRONTEND_DIR = pathlib.Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")

@app.get("/")
async def serve_landing():
    """Serve the user registration landing page."""
    return FileResponse(str(FRONTEND_DIR / "landing.html"))

@app.get("/generator")
async def serve_generator():
    """Serve the main resume generator app."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/admin")
async def serve_admin_login():
    """Serve the admin login page."""
    return FileResponse(str(FRONTEND_DIR / "admin" / "login.html"))

@app.get("/admin/dashboard")
async def serve_admin_dashboard():
    """Serve the admin dashboard page."""
    return FileResponse(str(FRONTEND_DIR / "admin" / "dashboard.html"))

# ─── Admin Credentials ───────────────────────────────────────────────────────
ADMIN_EMAIL = "omkarchavan1500@gmail.com"
ADMIN_PASSWORD = "omkarchavan@1"

# Session storage (simple in-memory for single-admin use)
admin_sessions = set()  # Store valid session tokens

# ─── Request / Response Models ────────────────────────────────────────────────
class ResumeRequest(BaseModel):
    master_data: str          # Full work history, skills, projects
    target_position: str      # e.g., "Senior Full-Stack Developer"
    target_city: str          # e.g., "Pune", "Mumbai", "Remote"
    job_description: str = "" # Optional JD for ATS keyword matching
    theme: str = "modern"     # Visual theme selected by user
    user_email: str = ""     # Email of the registered user

class ResumeResponse(BaseModel):
    resume_markdown: str
    tokens_used: int

class UserRegistration(BaseModel):
    email: str
    phone: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', v)
        # Support 10 digits (Indian) or +91 prefix (12 digits total)
        if len(digits) == 10:
            return digits
        elif len(digits) == 12 and digits.startswith('91'):
            return digits[2:]  # Remove 91 prefix, store 10 digits
        else:
            raise ValueError('Phone must be 10 digits (or +91 prefix)')

class AdminLogin(BaseModel):
    email: str
    password: str

class UserWithResumes(BaseModel):
    email: str
    phone: str
    registered_at: datetime
    last_active: datetime
    resume_count: int
    resumes: List[dict] = []

# ─── Admin Auth Dependency ────────────────────────────────────────────────────
async def require_admin(request: Request):
    """Verify admin session from cookie."""
    session_token = request.cookies.get("admin_session")
    if not session_token or session_token not in admin_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return True

# ─── System Prompt ─────────────────────────────────────────────────────────────
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

def build_user_prompt(req: ResumeRequest) -> str:
    jd_section = f"\n\n**Job Description:**\n{req.job_description}" if req.job_description.strip() else ""
    return f"""Please create a Chameleon Resume with the following inputs:

**Target Position:** {req.target_position}
**Target City:** {req.target_city}

**Master Data (Full Work History, Skills & Projects):**
{req.master_data}
{jd_section}

Transform this into a perfectly tailored resume following all the rules. Output ONLY the clean Markdown resume — no preamble, no explanation."""



# ─── PDF Extraction Endpoint ───────────────────────────────────────────────────
@app.post("/api/extract-pdf")
async def extract_pdf(file: UploadFile = File(...)):
    """Extract text from an uploaded PDF resume."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        print(f"[INFO] Started PDF extraction for file: {file.filename}")
        content = await file.read()
        if not content:
            print("[ERROR] Received empty file content")
            raise HTTPException(status_code=400, detail="Empty file uploaded")
            
        pdf_text = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            print(f"[INFO] PDF opened successfully, pages: {len(pdf.pages)}")
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    pdf_text += text + "\n"
                print(f"[INFO] Processed page {i+1}/{len(pdf.pages)}")

        if not pdf_text.strip():
            print("[WARNING] No text extracted from PDF content")
            raise HTTPException(status_code=400, detail="Could not extract text from PDF. It might be an image-only scan or empty.")

        print(f"[OK] Successfully extracted {len(pdf_text)} characters from PDF")
        return {"text": pdf_text, "filename": file.filename}

    except Exception as e:
        print(f"[ERROR] PDF processing failed: {str(e)}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"PDF extraction error: {str(e)}")


# ─── Theme HTML Endpoint ────────────────────────────────────────────────────────
THEMES_DIR = pathlib.Path(__file__).parent.parent / "files"

THEME_FILE_MAP = {
    "minimalist":       "resume-1-minimalist.html",
    "dark-tech":        "resume-2-dark-tech.html",
    "colorful":         "resume-3-colorful-creative.html",
    "timeline":         "resume-4-timeline-narrative.html",
    "card":             "resume-5-card-based.html",
    "sidebar":          "resume-6-sidebar-layout.html",
    "masonry":          "resume-7-masonry-grid.html",
    "glassmorphism":    "resume-8-glassmorphism.html",
    "vintage":          "resume-9-vintage-retro.html",
    "data-viz":         "resume-10-data-visualization.html",
}

@app.get("/api/get-theme/{theme_id}")
async def get_theme_html(theme_id: str):
    """Return the raw HTML of a resume theme template."""
    filename = THEME_FILE_MAP.get(theme_id)
    if not filename:
        raise HTTPException(status_code=404, detail=f"Theme '{theme_id}' not found.")
    theme_path = THEMES_DIR / filename
    if not theme_path.exists():
        raise HTTPException(status_code=404, detail=f"Theme file not found on server.")
    return FileResponse(str(theme_path), media_type="text/html")


# ─── API Endpoints ─────────────────────────────────────────────────────────────
@app.post("/api/generate-resume", response_model=ResumeResponse)
async def generate_resume(req: ResumeRequest):
    """Generate a tailored Chameleon Resume using NVIDIA NIM."""
    # Validate inputs
    if not req.master_data.strip():
        raise HTTPException(status_code=400, detail="Master data cannot be empty.")
    if not req.target_position.strip():
        raise HTTPException(status_code=400, detail="Target position is required.")
    if not req.target_city.strip():
        raise HTTPException(status_code=400, detail="Target city is required.")
    
    # Check NVIDIA API key is configured
    if not NVIDIA_API_KEY or NVIDIA_API_KEY == "your-api-key-here" or len(NVIDIA_API_KEY) < 10:
        raise HTTPException(
            status_code=503, 
            detail="NVIDIA API key not configured. Please set NVIDIA_API_KEY in backend/.env file."
        )

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": build_user_prompt(req)},
            ],
            temperature=0.6,
            top_p=0.9,
            max_tokens=2048,
            stream=False
        )

        resume_md = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens if completion.usage else 0

        # Persist to MongoDB (with graceful degradation if DB is unavailable)
        try:
            db = await get_db()
            if db is not None:
                resume_doc = {
                    "type": "generation",
                    "target_position": req.target_position,
                    "target_city": req.target_city,
                    "theme": req.theme,
                    "resume_markdown": resume_md,
                    "tokens_used": tokens_used,
                    "timestamp": datetime.now()
                }
                if req.user_email:
                    resume_doc["user_email"] = req.user_email
                    # Update user's last_active
                    try:
                        await db.users.update_one(
                            {"email": req.user_email},
                            {"$set": {"last_active": datetime.now()}},
                            upsert=True
                        )
                    except Exception as db_err:
                        print(f"[WARNING] Could not update user activity: {db_err}")
                
                try:
                    await db.resumes.insert_one(resume_doc)
                except Exception as insert_err:
                    print(f"[WARNING] Could not save resume to database: {insert_err}")
            else:
                print("[WARNING] Database not available, resume generated but not saved")
        except Exception as db_err:
            print(f"[WARNING] Database error: {db_err}")

        return ResumeResponse(resume_markdown=resume_md, tokens_used=tokens_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NVIDIA NIM API error: {str(e)}")


@app.get("/api/history")
async def get_resume_history():
    """Retrieve the last 10 generated resumes."""
    try:
        db = await get_db()
        if db is None:
            # Return empty array if database is unavailable
            return []
        cursor = db.resumes.find().sort("timestamp", -1).limit(10)
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"]) # Serialize ObjectId
            history.append(doc)
        return history
    except Exception as e:
        # Log error but return empty array instead of crashing
        print(f"[WARNING] History fetch error: {e}")
        return []


@app.get("/api/health")
async def health_check():
    """Health check endpoint with database status."""
    try:
        db = await get_db()
        db_status = "connected" if db else "disconnected"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
    
    return {
        "status": "ok",
        "model": MODEL,
        "provider": "NVIDIA NIM",
        "database": db_status,
        "api_key_configured": bool(NVIDIA_API_KEY and len(NVIDIA_API_KEY) > 10)
    }


@app.get("/api/models")
async def list_models():
    """Return supported models info."""
    return {
        "active_model": MODEL,
        "provider": "NVIDIA NIM",
        "capabilities": ["resume_generation", "ats_optimization", "keyword_injection", "resume_refinement"],
    }


# ─── Refine Resume ─────────────────────────────────────────────────────────────
class RefineRequest(BaseModel):
    current_resume: str       # The already-generated resume markdown
    instructions:   str       # User's edit instructions
    target_position: str = "" # Original context
    target_city:     str = ""
    theme:           str = "modern"

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

@app.post("/api/refine-resume", response_model=ResumeResponse)
async def refine_resume(req: RefineRequest):
    """Apply targeted edits to an existing generated resume."""
    if not req.current_resume.strip():
        raise HTTPException(status_code=400, detail="Current resume cannot be empty.")
    if not req.instructions.strip():
        raise HTTPException(status_code=400, detail="Edit instructions cannot be empty.")

    context = ""
    if req.target_position:
        context += f"Original role target: {req.target_position}\n"
    if req.target_city:
        context += f"Original city target: {req.target_city}\n"

    user_msg = f"""{context}
--- CURRENT RESUME ---
{req.current_resume}
--- END RESUME ---

EDIT INSTRUCTIONS:
{req.instructions}

Apply the instructions above to the resume and return the complete updated resume."""

    try:
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": REFINE_SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg},
            ],
            temperature=0.4,
            top_p=0.9,
            max_tokens=2048,
            stream=False
        )

        refined_md  = completion.choices[0].message.content
        tokens_used = completion.usage.total_tokens if completion.usage else 0

        # Persist to MongoDB (with graceful degradation)
        try:
            db = await get_db()
            if db is not None:
                await db.resumes.insert_one({
                    "type": "refinement",
                    "instructions": req.instructions,
                    "target_position": req.target_position,
                    "target_city": req.target_city,
                    "theme": req.theme,
                    "resume_markdown": refined_md,
                    "tokens_used": tokens_used,
                    "timestamp": datetime.now()
                })
            else:
                print("[WARNING] Database not available, refinement generated but not saved")
        except Exception as db_err:
            print(f"[WARNING] Database error during refinement save: {db_err}")

        return ResumeResponse(resume_markdown=refined_md, tokens_used=tokens_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NVIDIA NIM API error: {str(e)}")


# ─── User Registration Endpoints ───────────────────────────────────────────────
@app.post("/api/register-user")
async def register_user(user: UserRegistration):
    """Register a new user with email and phone."""
    try:
        db = await get_db()
        
        # Check if email already exists
        existing = await db.users.find_one({"email": user.email})
        if existing:
            # Update last_active for existing user
            await db.users.update_one(
                {"email": user.email},
                {"$set": {"last_active": datetime.now()}}
            )
            return {"success": True, "message": "User already registered, updated activity", "email": user.email}
        
        # Create new user
        user_doc = {
            "email": user.email,
            "phone": user.phone,
            "registered_at": datetime.now(),
            "last_active": datetime.now()
        }
        await db.users.insert_one(user_doc)
        
        return {"success": True, "message": "User registered successfully", "email": user.email}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.get("/api/check-user")
async def check_user(email: str):
    """Check if a user exists."""
    try:
        db = await get_db()
        user = await db.users.find_one({"email": email.lower()})
        if user:
            return {"exists": True, "email": user["email"], "phone": user["phone"]}
        return {"exists": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check user error: {str(e)}")


# ─── Admin Endpoints ───────────────────────────────────────────────────────────
@app.post("/api/admin/login")
async def admin_login(credentials: AdminLogin, response: Response):
    """Admin login with session cookie."""
    if credentials.email != ADMIN_EMAIL or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate session token
    session_token = str(uuid.uuid4())
    admin_sessions.add(session_token)
    
    # Set cookie (HTTP-only, secure in production)
    response.set_cookie(
        key="admin_session",
        value=session_token,
        httponly=True,
        max_age=86400,  # 24 hours
        samesite="lax"
    )
    
    return {"success": True, "message": "Login successful"}


@app.post("/api/admin/logout")
async def admin_logout(request: Request, response: Response):
    """Admin logout - clear session."""
    session_token = request.cookies.get("admin_session")
    if session_token and session_token in admin_sessions:
        admin_sessions.discard(session_token)
    
    response.delete_cookie(key="admin_session")
    return {"success": True, "message": "Logout successful"}


@app.get("/api/admin/check")
async def admin_check(request: Request):
    """Check if admin is authenticated."""
    session_token = request.cookies.get("admin_session")
    if session_token and session_token in admin_sessions:
        return {"authenticated": True}
    return {"authenticated": False}


@app.get("/api/admin/stats")
async def get_admin_stats(authorized: bool = Depends(require_admin)):
    """Get dashboard statistics for admin panel."""
    try:
        db = await get_db()
        if db is None:
            return {
                "total_users": 0,
                "total_resumes": 0,
                "today_users": 0,
                "database_status": "disconnected"
            }
        
        # Get counts
        total_users = await db.users.count_documents({})
        total_resumes = await db.resumes.count_documents({})
        
        # Get today's users
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = await db.users.count_documents({"registered_at": {"$gte": today_start}})
        
        return {
            "total_users": total_users,
            "total_resumes": total_resumes,
            "today_users": today_users,
            "database_status": "connected"
        }
    except Exception as e:
        print(f"[WARNING] Admin stats error: {e}")
        return {
            "total_users": 0,
            "total_resumes": 0,
            "today_users": 0,
            "database_status": "error",
            "error": str(e)
        }


@app.get("/api/admin/users")
async def get_admin_users(authorized: bool = Depends(require_admin)):
    """Get all users with their resume counts and details."""
    try:
        db = await get_db()
        
        # Get all users
        users_cursor = db.users.find().sort("registered_at", -1)
        users = []
        
        async for user in users_cursor:
            # Count resumes for this user
            resume_count = await db.resumes.count_documents({"user_email": user["email"]})
            
            # Get recent resumes for this user
            resumes_cursor = db.resumes.find(
                {"user_email": user["email"]}
            ).sort("timestamp", -1).limit(5)
            
            resumes = []
            async for resume in resumes_cursor:
                resume["_id"] = str(resume["_id"])
                resumes.append(resume)
            
            users.append({
                "email": user["email"],
                "phone": user["phone"],
                "registered_at": user["registered_at"],
                "last_active": user["last_active"],
                "resume_count": resume_count,
                "resumes": resumes
            })
        
        return {"users": users, "total": len(users)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# ─── Resume Templates Data ───────────────────────────────────────────────────
RESUME_TEMPLATES = [
    {
        "id": "fullstack-dev",
        "title": "Full-Stack Developer",
        "description": "React, Node.js, TypeScript, MongoDB, AWS",
        "icon": "⚛️",
        "color": "#61dafb",
        "content": """# Alex Johnson
**Full-Stack Developer**
📧 alex.johnson@email.com | 📱 +91 98765 43210 | 🔗 linkedin.com/in/alexjohnson | 💻 github.com/alexjohnson
📍 Bangalore, India

## Professional Summary
Innovative Full-Stack Developer with 4+ years of experience building scalable web applications using React, Node.js, and TypeScript. Passionate about creating seamless user experiences and robust backend systems. Proven track record of delivering high-quality code and mentoring junior developers.

## Technical Skills
**Frontend:** React.js, Next.js, TypeScript, JavaScript (ES6+), HTML5, CSS3, Tailwind CSS, Redux, Webpack
**Backend:** Node.js, Express.js, FastAPI, Python, REST APIs, GraphQL, WebSocket
**Database:** MongoDB, PostgreSQL, MySQL, Redis, Firebase
**Cloud & DevOps:** AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD, GitHub Actions
**Tools:** Git, VS Code, Postman, Figma, Jira

## Professional Experience

**Senior Full-Stack Developer | TechCorp Solutions**
*Jan 2022 – Present | Bangalore, India*
- Architected and developed a real-time collaboration platform serving 50,000+ active users
- Reduced application load time by 60% through code splitting, lazy loading, and Redis caching
- Led a team of 4 developers, conducted code reviews, and established coding standards
- Implemented microservices architecture using Docker and Kubernetes

**Full-Stack Developer | StartupXYZ**
*Jun 2020 – Dec 2021 | Pune, India*
- Built MVP from scratch using React, Node.js, and MongoDB; secured $2M in seed funding
- Developed RESTful APIs handling 10,000+ requests/day with 99.9% uptime
- Integrated payment gateways (Stripe, Razorpay) and implemented real-time notifications
- Implemented automated testing with Jest and Cypress, achieving 85% code coverage

## Education
**Bachelor of Technology in Computer Science**
Pune Institute of Computer Technology | 2016 – 2020 | CGPA: 8.7/10

## Projects
**E-Commerce Platform** | React, Node.js, MongoDB, Stripe
- Built a full-featured e-commerce platform with 1,000+ products
- Implemented JWT authentication, cart management, and order tracking
- Source: github.com/alexjohnson/ecommerce-platform

**Task Management App** | Next.js, TypeScript, PostgreSQL, Prisma
- Developed a Trello-like task management application with drag-and-drop interface
- Features include real-time updates, team collaboration, and analytics dashboard

## Certifications
- AWS Certified Developer – Associate (2023)
- MongoDB Certified Developer (2022)
- Meta Frontend Developer Certificate (2021)
"""
    },
    {
        "id": "ai-ml-engineer",
        "title": "AI/ML Engineer",
        "description": "Python, TensorFlow, PyTorch, LangChain, LLMs",
        "icon": "🤖",
        "color": "#ff6b6b",
        "content": """# Priya Sharma
**AI/ML Engineer**
📧 priya.sharma@email.com | 📱 +91 98765 43211 | 🔗 linkedin.com/in/priyasharma-ai
📍 Hyderabad, India

## Professional Summary
Results-driven AI/ML Engineer with 5+ years of experience developing intelligent systems using deep learning, NLP, and large language models. Expert in building production-grade AI solutions that solve real-world business problems. Strong background in MLOps and model deployment.

## Technical Skills
**Languages:** Python, SQL, R
**ML/DL Frameworks:** TensorFlow, PyTorch, Keras, Scikit-learn, XGBoost, LightGBM
**NLP & LLMs:** LangChain, Hugging Face Transformers, OpenAI API, spaCy, NLTK, BERT, GPT
**Data Tools:** Pandas, NumPy, Matplotlib, Seaborn, Plotly, Jupyter
**MLOps:** MLflow, Kubeflow, Docker, Kubernetes, AWS SageMaker, GCP Vertex AI
**Vector DBs:** Pinecone, ChromaDB, Weaviate, FAISS

## Professional Experience

**Senior AI Engineer | DataBrains AI**
*Mar 2021 – Present | Hyderabad, India*
- Built an intelligent document processing system using LLMs achieving 95% accuracy
- Developed RAG-based chatbots for enterprise clients, reducing support tickets by 40%
- Fine-tuned BERT models for sentiment analysis, improving F1 score from 0.72 to 0.89
- Led MLOps initiatives, reducing model deployment time from 2 weeks to 2 days

**Machine Learning Engineer | Analytics Pro**
*Jul 2019 – Feb 2021 | Bangalore, India*
- Designed and implemented recommendation systems increasing user engagement by 35%
- Built computer vision models for quality inspection, reducing defect miss rate by 60%
- Created automated ML pipelines using Apache Airflow and MLflow
- Collaborated with data engineers to optimize data pipelines for 10TB+ datasets

## Education
**Master of Technology in Artificial Intelligence**
Indian Institute of Technology, Bombay | 2017 – 2019 | CGPA: 9.1/10

**Bachelor of Engineering in Computer Science**
Visvesvaraya Technological University | 2013 – 2017 | CGPA: 8.9/10

## Projects
**Intelligent Resume Parser** | Python, LangChain, OpenAI, FastAPI
- Developed an AI-powered resume parsing system processing 1000+ resumes/day
- Extracted structured data with 92% accuracy using custom NER models
- Deployed as microservice handling 500+ concurrent requests

**Predictive Maintenance System** | Python, TensorFlow, IoT, AWS
- Built predictive models for manufacturing equipment failure prediction
- Achieved 87% precision in predicting failures 48 hours in advance
- Saved client ₹50+ lakhs annually in maintenance costs

## Publications & Research
- "Efficient Fine-tuning of LLMs for Low-Resource Languages" – EMNLP 2023
- "RAG Architecture for Enterprise Knowledge Management" – arXiv 2023

## Certifications
- Deep Learning Specialization – DeepLearning.AI (2022)
- TensorFlow Developer Certificate – Google (2021)
- AWS Machine Learning Specialty (2020)
"""
    },
    {
        "id": "data-scientist",
        "title": "Data Scientist",
        "description": "Python, SQL, Machine Learning, Statistics, Tableau",
        "icon": "📊",
        "color": "#4ecdc4",
        "content": """# Rahul Verma
**Data Scientist**
📧 rahul.verma@email.com | 📱 +91 98765 43212 | 🔗 linkedin.com/in/rahulverma-ds
📍 Mumbai, India

## Professional Summary
Analytical Data Scientist with 4+ years of experience transforming complex data into actionable business insights. Expert in statistical analysis, predictive modeling, and data visualization. Proven ability to drive data-informed decision making and optimize business processes.

## Technical Skills
**Languages:** Python, R, SQL, Scala
**Analytics:** Pandas, NumPy, SciPy, Statsmodels, Scikit-learn
**Visualization:** Tableau, Power BI, Matplotlib, Seaborn, Plotly, D3.js
**Big Data:** Apache Spark, Hadoop, Hive, Presto
**Cloud:** AWS (Redshift, EMR, Athena), GCP (BigQuery), Azure
**Statistics:** A/B Testing, Hypothesis Testing, Regression Analysis, Time Series

## Professional Experience

**Senior Data Scientist | FinanceHub Analytics**
*Apr 2021 – Present | Mumbai, India*
- Developed credit risk models reducing default rates by 23% and saving ₹10+ crores annually
- Built customer segmentation models enabling targeted marketing, increasing ROI by 40%
- Created interactive Tableau dashboards used by 200+ stakeholders for decision making
- Led data quality initiatives improving data accuracy from 85% to 98%

**Data Analyst | RetailMax Solutions**
*Jun 2019 – Mar 2021 | Delhi, India*
- Analyzed sales data across 500+ stores, identifying trends that increased revenue by 15%
- Automated reporting pipelines using Python and SQL, saving 20+ hours/week
- Built predictive models for inventory optimization, reducing stockouts by 30%
- Conducted A/B tests for pricing strategies, optimizing margins by 8%

## Education
**Master of Science in Data Science**
Indian Institute of Technology, Madras | 2017 – 2019 | CGPA: 8.8/10

**Bachelor of Statistics (Honors)**
Delhi University | 2014 – 2017 | CGPA: 8.6/10

## Projects
**Customer Churn Prediction** | Python, XGBoost, SQL
- Built ensemble models achieving 89% accuracy in predicting customer churn
- Identified key churn drivers leading to retention strategy changes
- Implemented real-time scoring API processing 10,000+ predictions/day

**Supply Chain Optimization** | Python, Linear Programming, Tableau
- Developed optimization models reducing logistics costs by 18%
- Created interactive dashboards for supply chain visibility
- Integrated with ERP systems for automated decision support

## Certifications
- Google Professional Data Engineer (2022)
- Tableau Desktop Certified Professional (2021)
- Certified Analytics Professional (CAP) (2020)
"""
    },
    {
        "id": "devops-engineer",
        "title": "DevOps Engineer",
        "description": "AWS, Docker, Kubernetes, Jenkins, Terraform, Linux",
        "icon": "⚙️",
        "color": "#f7b731",
        "content": """# Karthik Rajan
**DevOps Engineer**
📧 karthik.rajan@email.com | 📱 +91 98765 43213 | 🔗 linkedin.com/in/karthikrajan-devops
📍 Chennai, India

## Professional Summary
Experienced DevOps Engineer with 5+ years of expertise in cloud infrastructure, CI/CD automation, and container orchestration. Proven track record of implementing infrastructure as code, reducing deployment times by 80%, and ensuring 99.99% system uptime. Strong advocate for DevSecOps practices.

## Technical Skills
**Cloud Platforms:** AWS (EC2, ECS, EKS, Lambda, S3, CloudFormation), Azure, GCP
**Containerization:** Docker, Kubernetes, Helm, Amazon ECR
**CI/CD:** Jenkins, GitHub Actions, GitLab CI, ArgoCD, Spinnaker
**IaC:** Terraform, Ansible, Pulumi, CloudFormation, Vagrant
**Monitoring:** Prometheus, Grafana, ELK Stack, Datadog, New Relic, PagerDuty
**Security:** HashiCorp Vault, AWS Secrets Manager, Trivy, SonarQube
**Scripting:** Python, Bash, PowerShell, Go

## Professional Experience

**Senior DevOps Engineer | CloudFirst Technologies**
*Jan 2021 – Present | Chennai, India*
- Architected Kubernetes clusters on EKS serving 50+ microservices with 99.99% uptime
- Implemented GitOps workflow using ArgoCD, reducing deployment time from 2 hours to 15 minutes
- Built automated infrastructure using Terraform, managing 200+ AWS resources
- Established DevSecOps pipeline with integrated security scanning, reducing vulnerabilities by 70%

**DevOps Engineer | ScaleUp Solutions**
*May 2019 – Dec 2020 | Bangalore, India*
- Migrated 30+ applications from on-premise to AWS, achieving 40% cost reduction
- Implemented Docker containerization across all services, improving deployment consistency
- Built Jenkins pipelines for automated testing and deployment
- Set up monitoring stack (Prometheus + Grafana), reducing MTTR by 60%

## Education
**Bachelor of Technology in Information Technology**
Anna University, Chennai | 2015 – 2019 | CGPA: 8.5/10

## Projects
**Multi-Environment Infrastructure** | Terraform, AWS, Kubernetes
- Designed reusable Terraform modules for multi-environment setup (dev, staging, prod)
- Implemented auto-scaling policies handling 10x traffic spikes
- Achieved infrastructure deployment time of under 30 minutes

**GitOps Implementation** | ArgoCD, Kubernetes, Helm
- Set up GitOps-based deployment workflow for 20+ applications
- Implemented automated rollback on failed deployments
- Reduced mean time to recovery (MTTR) from 2 hours to 10 minutes

## Certifications
- AWS Certified Solutions Architect – Professional (2023)
- Certified Kubernetes Administrator (CKA) (2022)
- HashiCorp Certified: Terraform Associate (2021)
"""
    },
    {
        "id": "product-manager",
        "title": "Product Manager",
        "description": "Agile, Strategy, Analytics, Stakeholder Management",
        "icon": "📱",
        "color": "#5f27cd",
        "content": """# Ananya Patel
**Product Manager**
📧 ananya.patel@email.com | 📱 +91 98765 43214 | 🔗 linkedin.com/in/ananyapatel-pm
📍 Bangalore, India

## Professional Summary
Strategic Product Manager with 6+ years of experience driving product vision, roadmap, and execution for B2B and B2C products. Expert in Agile methodologies, data-driven decision making, and cross-functional team leadership. Delivered products generating $10M+ in annual revenue.

## Core Competencies
**Product Strategy:** Market Research, Competitive Analysis, Go-to-Market, Product Vision
**Agile & Process:** Scrum, Kanban, JIRA, Confluence, Product Analytics, A/B Testing
**Analytics:** SQL, Mixpanel, Amplitude, Google Analytics, Tableau, Data-driven Decisions
**Tools:** Figma, Miro, Balsamiq, Postman, Swagger, GitHub
**Leadership:** Team Management, Stakeholder Communication, Prioritization, OKRs

## Professional Experience

**Senior Product Manager | Tech Innovations Pvt Ltd**
*Mar 2020 – Present | Bangalore, India*
- Led product strategy for SaaS platform serving 10,000+ enterprise customers
- Increased user activation rate from 45% to 78% through onboarding optimization
- Managed product roadmap for team of 15 engineers, designers, and analysts
- Launched 3 major features generating $3M in additional ARR

**Product Manager | GrowthStartup Inc**
*Jul 2018 – Feb 2020 | Mumbai, India*
- Owned mobile app product with 1M+ downloads and 4.6★ rating
- Implemented growth experiments increasing DAU by 150% in 6 months
- Conducted 100+ user interviews informing product decisions
- Reduced customer acquisition cost by 35% through product-led growth

**Associate Product Manager | Digital Solutions**
*Jun 2017 – Jun 2018 | Pune, India*
- Assisted in launching e-commerce platform processing ₹50+ crores annually
- Analyzed user behavior data to identify conversion optimization opportunities
- Collaborated with engineering on technical feasibility assessments

## Education
**Master of Business Administration (MBA)**
Indian Institute of Management, Ahmedabad | 2015 – 2017

**Bachelor of Engineering in Computer Science**
Birla Institute of Technology, Pilani | 2011 – 2015 | CGPA: 8.4/10

## Key Achievements
- Led product that won "Best Enterprise SaaS Product" at TechSparks 2023
- Featured speaker at ProductTank Bangalore and India Product Management Summit
- Published articles on product management in leading tech publications

## Certifications
- Certified Scrum Product Owner (CSPO) – Scrum Alliance (2022)
- Product Analytics Certification – Mixpanel (2021)
- Google Analytics Certified (2020)
"""
    },
    {
        "id": "ux-designer",
        "title": "UX Designer",
        "description": "Figma, User Research, Prototyping, Design Systems",
        "icon": "🎨",
        "color": "#e84393",
        "content": """# Sneha Reddy
**UX/UI Designer**
📧 sneha.reddy@email.com | 📱 +91 98765 43215 | 🔗 linkedin.com/in/snehareddy-ux
🎨 behance.net/snehareddy | 📍 Bangalore, India

## Professional Summary
Creative UX Designer with 4+ years of experience crafting intuitive digital experiences for web and mobile applications. Expert in user research, design systems, and prototyping. Passionate about accessibility and inclusive design. Portfolio includes products serving 5M+ users.

## Design Skills
**Design Tools:** Figma, Sketch, Adobe XD, Photoshop, Illustrator, After Effects
**Prototyping:** Figma Prototyping, Principle, Framer, Proto.io
**Research:** User Interviews, Usability Testing, A/B Testing, Heatmaps, Analytics
**Design Systems:** Component Libraries, Style Guides, Design Tokens, Storybook
**Front-end:** HTML, CSS, JavaScript basics, Responsive Design
**Methodologies:** Design Thinking, Double Diamond, Lean UX, Agile/Scrum

## Professional Experience

**Senior UX Designer | DesignCraft Studio**
*Jan 2021 – Present | Bangalore, India*
- Lead UX for fintech app with 2M+ users, improving task completion rate by 45%
- Built comprehensive design system with 200+ components, reducing design time by 30%
- Conducted 50+ usability testing sessions, identifying and fixing critical UX issues
- Mentored 3 junior designers, conducting design reviews and skill workshops

**UX Designer | ProductFirst Tech**
*Jun 2019 – Dec 2020 | Hyderabad, India*
- Redesigned e-commerce checkout flow, reducing cart abandonment by 28%
- Created wireframes, prototypes, and high-fidelity designs for 10+ features
- Collaborated with PMs and engineers to ensure design feasibility
- Implemented accessibility improvements achieving WCAG 2.1 AA compliance

**Junior UX Designer | CreativeAgency**
*Jul 2018 – May 2019 | Chennai, India*
- Designed responsive websites for 15+ clients across various industries
- Created user personas, journey maps, and information architecture
- Assisted in user research and usability testing activities

## Education
**Master of Design (M.Des) in Interaction Design**
IDC School of Design, IIT Bombay | 2016 – 2018

**Bachelor of Fine Arts in Visual Communication**
Srishti Institute of Art, Design and Technology | 2012 – 2016 | CGPA: 8.7/10

## Portfolio Highlights
**Healthcare App Redesign** | Figma, User Research, Usability Testing
- Complete redesign of patient-facing healthcare app
- Simplified appointment booking from 12 steps to 4 steps
- Increased patient satisfaction score from 3.2 to 4.6/5

**Design System Creation** | Figma, Design Tokens, Documentation
- Created comprehensive design system for enterprise SaaS platform
- 200+ components, 50+ patterns, complete documentation
- Reduced design-to-dev handoff time by 40%

## Awards & Recognition
- "Best Mobile UX Design" – India Design Awards 2023
- Featured in "Top 30 UX Designers to Watch" – Design Matters India

## Certifications
- Google UX Design Professional Certificate (2022)
- Nielsen Norman Group UX Master Certification (2021)
- Figma Advanced Certification (2020)
"""
    },
    {
        "id": "backend-developer",
        "title": "Backend Developer",
        "description": "Python, FastAPI, PostgreSQL, Redis, Microservices",
        "icon": "🐍",
        "color": "#00d2d3",
        "content": """# Vikram Singh
**Backend Developer**
📧 vikram.singh@email.com | 📱 +91 98765 43216 | 🔗 linkedin.com/in/vikramsingh-backend
💻 github.com/vikramsingh | 📍 Pune, India

## Professional Summary
Backend Developer with 5+ years of experience building high-performance, scalable APIs and microservices. Expert in Python, distributed systems, and database optimization. Passionate about clean code, system design, and solving complex technical challenges.

## Technical Skills
**Languages:** Python, Go, Java, SQL, Bash
**Frameworks:** FastAPI, Django, Flask, Gin, Spring Boot
**Databases:** PostgreSQL, MongoDB, Redis, Elasticsearch, ClickHouse
**Message Queues:** Kafka, RabbitMQ, Celery, AWS SQS
**Cloud:** AWS (Lambda, EC2, RDS), GCP, Azure
**DevOps:** Docker, Kubernetes, Terraform, GitHub Actions
**Other:** gRPC, GraphQL, REST API Design, Microservices, System Design

## Professional Experience

**Senior Backend Engineer | ScaleTech Solutions**
*Feb 2021 – Present | Pune, India*
- Architected microservices handling 1M+ requests/day with 99.95% uptime
- Optimized PostgreSQL queries reducing response time from 2s to 200ms
- Built real-time data processing pipeline using Kafka and Redis Streams
- Implemented distributed caching strategy, reducing database load by 60%

**Backend Developer | APIFirst Labs**
*Jul 2019 – Jan 2021 | Bangalore, India*
- Developed RESTful APIs using FastAPI serving 500K+ daily active users
- Designed database schemas and optimized queries for complex analytics
- Implemented OAuth2 and JWT authentication with role-based access control
- Built automated testing suite achieving 90% code coverage

**Software Engineer | StartUpHub**
*Jun 2018 – Jun 2019 | Mumbai, India*
- Created backend services for fintech application processing ₹100+ crores daily
- Integrated with 10+ third-party APIs including payment gateways
- Implemented background job processing using Celery and Redis

## Education
**Bachelor of Technology in Computer Engineering**
College of Engineering, Pune (COEP) | 2014 – 2018 | CGPA: 8.9/10

## Projects
**High-Performance API Gateway** | Python, FastAPI, Redis, PostgreSQL
- Built API gateway handling 10,000+ RPS with rate limiting and caching
- Implemented authentication, request validation, and response transformation
- Achieved p99 latency of under 50ms

**Distributed Task Queue** | Python, Celery, RabbitMQ, Docker
- Developed scalable task processing system handling 100,000+ tasks/day
- Implemented retry mechanisms, dead letter queues, and monitoring
- Reduced task processing time by 70% through optimization

**Open Source Contributions**
- FastAPI-contrib: 500+ stars, helper libraries for FastAPI
- Python-cachetools: Performance improvements merged to main repo

## Certifications
- AWS Certified Developer – Associate (2023)
- MongoDB Certified Developer (2022)
- System Design Certificate – Educative.io (2021)
"""
    },
    {
        "id": "frontend-developer",
        "title": "Frontend Developer",
        "description": "React, Next.js, TypeScript, Tailwind CSS, Performance",
        "icon": "💻",
        "color": "#ff9f43",
        "content": """# Divya Krishnan
**Frontend Developer**
📧 divya.krishnan@email.com | 📱 +91 98765 43217 | 🔗 linkedin.com/in/divyakrishnan-frontend
💻 github.com/divyakrishnan | 📍 Bangalore, India

## Professional Summary
Creative Frontend Developer with 4+ years of experience building fast, accessible, and responsive web applications. Expert in React ecosystem, modern JavaScript, and performance optimization. Passionate about creating delightful user experiences and writing clean, maintainable code.

## Technical Skills
**Core:** JavaScript (ES6+), TypeScript, HTML5, CSS3, Responsive Design
**Frameworks:** React.js, Next.js, Vue.js, Redux, Zustand, React Query
**Styling:** Tailwind CSS, Styled Components, SASS/SCSS, CSS-in-JS, Emotion
**Build Tools:** Webpack, Vite, Rollup, Babel, ESLint, Prettier
**Testing:** Jest, React Testing Library, Cypress, Playwright, Storybook
**Performance:** Core Web Vitals, Lighthouse, Code Splitting, Lazy Loading
**Tools:** Git, VS Code, Figma, Postman, npm/yarn/pnpm

## Professional Experience

**Senior Frontend Developer | WebWizards Agency**
*Jan 2021 – Present | Bangalore, India*
- Developed Next.js applications achieving 95+ Lighthouse scores
- Implemented complex animations using Framer Motion and GSAP
- Built reusable component library used across 10+ projects
- Optimized bundle size by 40% through code splitting and tree shaking

**Frontend Developer | AppInnovators**
*Jun 2019 – Dec 2020 | Chennai, India*
- Built responsive React applications serving 1M+ monthly active users
- Implemented state management using Redux and Context API
- Created automated testing suite with 85% code coverage
- Collaborated with UX team to implement pixel-perfect designs

**Junior Web Developer | DigitalCrafts**
*Jul 2018 – May 2019 | Coimbatore, India*
- Developed responsive websites for 20+ clients using HTML, CSS, JavaScript
- Implemented WordPress themes and custom plugins
- Optimized website performance achieving 90+ PageSpeed scores

## Education
**Bachelor of Technology in Information Technology**
PSG College of Technology, Coimbatore | 2014 – 2018 | CGPA: 8.6/10

## Projects
**E-Commerce Dashboard** | Next.js, TypeScript, Tailwind CSS, Recharts
- Built feature-rich admin dashboard with real-time analytics
- Implemented dark mode, data visualization, and data tables
- Optimized for performance with SSR and ISR

**Social Media Analytics Tool** | React, D3.js, Node.js
- Created interactive dashboard for social media performance tracking
- Implemented data visualizations using D3.js and Recharts
- Integrated with Facebook, Twitter, and Instagram APIs

**Performance Optimization Case Study**
- Improved LCP from 4.2s to 1.8s through image optimization and CDN
- Reduced FID from 200ms to 50ms by optimizing JavaScript execution
- Achieved perfect 100 Lighthouse score on production app

## Certifications
- Meta Frontend Developer Certificate (2023)
- JavaScript Algorithms and Data Structures – freeCodeCamp (2022)
- React Developer Nanodegree – Udacity (2021)
"""
    },
    {
        "id": "cloud-architect",
        "title": "Cloud Architect",
        "description": "AWS, Azure, Infrastructure, Security, Cost Optimization",
        "icon": "☁️",
        "color": "#54a0ff",
        "content": """# Arun Kumar
**Cloud Architect**
📧 arun.kumar@email.com | 📱 +91 98765 43218 | 🔗 linkedin.com/in/arunkumar-cloud
📍 Hyderabad, India

## Professional Summary
Experienced Cloud Architect with 7+ years of expertise designing and implementing enterprise-scale cloud solutions. Expert in AWS and Azure, infrastructure automation, and cloud security. Proven track record of migrating complex workloads to cloud, achieving 40% cost optimization while improving reliability.

## Technical Skills
**Cloud Platforms:** AWS (Expert), Azure (Expert), GCP (Proficient)
**Compute:** EC2, Lambda, ECS, EKS, Fargate, Auto Scaling, Load Balancers
**Storage:** S3, EBS, EFS, Glacier, Azure Blob, Azure Files
**Networking:** VPC, Direct Connect, Transit Gateway, VPN, Route 53, Azure VNet
**Security:** IAM, KMS, WAF, Shield, GuardDuty, Azure AD, Sentinel
**IaC:** Terraform, CloudFormation, ARM Templates, Pulumi
**Monitoring:** CloudWatch, Azure Monitor, Datadog, New Relic

## Professional Experience

**Lead Cloud Architect | CloudGenius Consulting**
*Mar 2019 – Present | Hyderabad, India*
- Designed cloud architecture for 20+ enterprise clients across fintech, healthcare, and e-commerce
- Led migration of 500+ servers to AWS, achieving 45% infrastructure cost reduction
- Implemented multi-region disaster recovery with RPO < 15 minutes and RTO < 1 hour
- Established cloud governance framework ensuring security and compliance

**Senior Cloud Engineer | TechScale Solutions**
*Jul 2017 – Feb 2019 | Bangalore, India*
- Architected serverless solutions processing 10M+ events/day using Lambda and EventBridge
- Implemented Infrastructure as Code managing 300+ resources with Terraform
- Designed hybrid cloud connectivity between on-premise and AWS using Direct Connect
- Optimized cloud costs by 35% through Reserved Instances and Savings Plans

**Systems Administrator | Enterprise Systems**
*Jun 2015 – Jun 2017 | Chennai, India*
- Managed on-premise infrastructure of 200+ servers
- Led virtualization project using VMware, reducing hardware costs by 50%
- Implemented backup and disaster recovery solutions

## Education
**Master of Technology in Cloud Computing**
Bits Pilani (WILP) | 2017 – 2019

**Bachelor of Engineering in Computer Science**
Anna University, Chennai | 2011 – 2015 | CGPA: 8.3/10

## Key Projects
**Multi-Cloud DR Solution** | AWS, Azure, Terraform
- Designed disaster recovery solution across AWS and Azure
- Achieved RPO of 5 minutes and RTO of 30 minutes
- Automated failover using Route 53 health checks and Lambda

**FinOps Implementation** | AWS, CloudHealth, Python
- Implemented cloud cost optimization program saving $500K annually
- Created automated tagging and cost allocation system
- Built dashboards for real-time cost monitoring and alerts

**Security Compliance Automation** | AWS Config, Lambda, Python
- Automated security compliance checks for 20+ AWS accounts
- Implemented automated remediation for common security issues
- Achieved 95% compliance score in security audits

## Certifications
- AWS Certified Solutions Architect – Professional (2023)
- AWS Certified Security – Specialty (2022)
- Microsoft Certified: Azure Solutions Architect Expert (2021)
- Certified Kubernetes Administrator (CKA) (2020)
"""
    },
    {
        "id": "cybersecurity-engineer",
        "title": "Cybersecurity Engineer",
        "description": "Security Tools, Penetration Testing, SIEM, Compliance",
        "icon": "🔒",
        "color": "#10ac84",
        "content": """# Neha Gupta
**Cybersecurity Engineer**
📧 neha.gupta@email.com | 📱 +91 98765 43219 | 🔗 linkedin.com/in/nehagupta-security
📍 Delhi NCR, India

## Professional Summary
Dedicated Cybersecurity Engineer with 5+ years of experience protecting enterprise infrastructure and applications from cyber threats. Expert in vulnerability assessment, penetration testing, SIEM implementation, and security automation. Proven track record of identifying critical vulnerabilities and implementing robust security controls.

## Technical Skills
**Security Tools:** Burp Suite, Metasploit, Nessus, Nmap, Wireshark, OWASP ZAP
**SIEM & Monitoring:** Splunk, QRadar, Elastic Security, Wazuh, Sentinel
**Cloud Security:** AWS Security Hub, GuardDuty, Azure Security Center, Prisma Cloud
**Network Security:** Firewalls, IDS/IPS, VPN, Zero Trust Architecture
**Compliance:** ISO 27001, SOC 2, GDPR, PCI-DSS, NIST Cybersecurity Framework
**Languages:** Python, PowerShell, Bash, SQL
**Certifications:** CISSP, CEH, OSCP, CompTIA Security+

## Professional Experience

**Senior Security Engineer | SecureNet Solutions**
*Apr 2021 – Present | Delhi NCR, India*
- Conducted 100+ penetration tests identifying 500+ vulnerabilities across web and mobile apps
- Implemented SIEM solution processing 10GB+ logs/day, reducing threat detection time by 80%
- Designed and deployed Zero Trust architecture for 1,000+ user organization
- Automated vulnerability scanning and reporting, saving 40 hours/week

**Cybersecurity Analyst | DefenseFirst Security**
*Jul 2019 – Mar 2021 | Bangalore, India*
- Monitored and responded to 1,000+ security alerts/month, reducing false positives by 60%
- Conducted security assessments of cloud infrastructure and recommended remediation
- Developed incident response playbooks reducing MTTR from 4 hours to 45 minutes
- Trained 50+ developers on secure coding practices and OWASP Top 10

**Security Operations Center (SOC) Analyst | CyberShield**
*Jun 2018 – Jun 2019 | Mumbai, India*
- Monitored security events 24/7 using Splunk and QRadar
- Investigated and escalated 200+ security incidents
- Created threat intelligence reports for management

## Education
**Master of Technology in Cybersecurity**
Indian Institute of Technology, Delhi | 2016 – 2018 | CGPA: 8.7/10

**Bachelor of Technology in Computer Science**
Netaji Subhas Institute of Technology | 2012 – 2016 | CGPA: 8.5/10

## Projects
**Automated Vulnerability Scanner** | Python, Docker, Elasticsearch
- Built automated scanner integrating multiple open-source security tools
- Generated comprehensive reports with risk ratings and remediation guidance
- Scanning 100+ applications weekly, identifying 300+ vulnerabilities monthly

**Threat Detection Platform** | Python, Machine Learning, Splunk
- Developed ML-based anomaly detection for network traffic
- Reduced false positives by 70% compared to rule-based detection
- Detected 15+ advanced persistent threats (APTs) in first year

**Security Awareness Training Program**
- Created interactive security training modules for 500+ employees
- Reduced phishing click rate from 25% to 5% within 6 months
- Implemented simulated phishing campaigns with detailed analytics

## Bug Bounty & Research
- HackerOne: Ranked in top 500, reported 50+ valid vulnerabilities
- CVEs: Discovered and responsibly disclosed 10+ CVEs
- Published research on "AI-Powered Phishing Detection" in security journals

## Certifications
- Certified Information Systems Security Professional (CISSP) – (ISC)² (2023)
- Offensive Security Certified Professional (OSCP) – Offensive Security (2022)
- Certified Ethical Hacker (CEH) – EC-Council (2021)
- CompTIA Security+ – CompTIA (2020)
"""
    }
]

# ─── PDF Generation Models ────────────────────────────────────────────────────
class PDFRequest(BaseModel):
    markdown: str
    filename: str = "resume.pdf"

class TemplateResponse(BaseModel):
    id: str
    title: str
    description: str
    icon: str
    color: str
    content: str


# ─── PDF Generation Helper ────────────────────────────────────────────────────
CSS_STYLES = """
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
hr {
    border: none;
    border-top: 1px solid #ecf0f1;
    margin: 20px 0;
}
"""

def markdown_to_pdf(markdown_content: str) -> bytes:
    """Convert markdown content to PDF bytes."""
    # Convert markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['extra'])
    
    # Wrap in full HTML document
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>{CSS_STYLES}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    pdf_bytes = HTML(string=full_html).write_pdf()
    return pdf_bytes


# ─── Templates API Endpoints ──────────────────────────────────────────────────
@app.get("/api/templates")
async def get_templates():
    """Get all available resume templates."""
    return {"templates": RESUME_TEMPLATES}


@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID."""
    for template in RESUME_TEMPLATES:
        if template["id"] == template_id:
            return template
    raise HTTPException(status_code=404, detail="Template not found")


@app.post("/api/generate-pdf")
async def generate_pdf(request: PDFRequest):
    """Generate PDF from markdown content."""
    try:
        pdf_bytes = markdown_to_pdf(request.markdown)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={request.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

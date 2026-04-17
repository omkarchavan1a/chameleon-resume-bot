"""
Chameleon Resume Bot — FastAPI Backend
Powered by NVIDIA NIM API (meta/llama-3.3-70b-instruct)
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import pathlib
import io
import pdfplumber
from dotenv import load_dotenv
from datetime import datetime
from database import Database, get_db

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
async def serve_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

# ─── Request / Response Models ────────────────────────────────────────────────
class ResumeRequest(BaseModel):
    master_data: str          # Full work history, skills, projects
    target_position: str      # e.g., "Senior Full-Stack Developer"
    target_city: str          # e.g., "Pune", "Mumbai", "Remote"
    job_description: str = "" # Optional JD for ATS keyword matching
    theme: str = "modern"     # Visual theme selected by user

class ResumeResponse(BaseModel):
    resume_markdown: str
    tokens_used: int

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


# ─── API Endpoints ─────────────────────────────────────────────────────────────
@app.post("/api/generate-resume", response_model=ResumeResponse)
async def generate_resume(req: ResumeRequest):
    """Generate a tailored Chameleon Resume using NVIDIA NIM."""
    if not req.master_data.strip():
        raise HTTPException(status_code=400, detail="Master data cannot be empty.")
    if not req.target_position.strip():
        raise HTTPException(status_code=400, detail="Target position is required.")
    if not req.target_city.strip():
        raise HTTPException(status_code=400, detail="Target city is required.")

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

        # Persist to MongoDB
        db = await get_db()
        await db.resumes.insert_one({
            "type": "generation",
            "target_position": req.target_position,
            "target_city": req.target_city,
            "theme": req.theme,
            "resume_markdown": resume_md,
            "tokens_used": tokens_used,
            "timestamp": datetime.utcnow()
        })

        return ResumeResponse(resume_markdown=resume_md, tokens_used=tokens_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NVIDIA NIM API error: {str(e)}")


@app.get("/api/history")
async def get_resume_history():
    """Retrieve the last 10 generated resumes."""
    try:
        db = await get_db()
        cursor = db.resumes.find().sort("timestamp", -1).limit(10)
        history = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"]) # Serialize ObjectId
            history.append(doc)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "model": MODEL, "provider": "NVIDIA NIM"}


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

        # Persist to MongoDB
        db = await get_db()
        await db.resumes.insert_one({
            "type": "refinement",
            "instructions": req.instructions,
            "target_position": req.target_position,
            "target_city": req.target_city,
            "theme": req.theme,
            "resume_markdown": refined_md,
            "tokens_used": tokens_used,
            "timestamp": datetime.utcnow()
        })

        return ResumeResponse(resume_markdown=refined_md, tokens_used=tokens_used)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NVIDIA NIM API error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)


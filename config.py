"""
Chameleon Resume Bot — Data Configuration
Ported from Premium Frontend (frontend/static/app.js)
"""

MASTER_PROFILE = {
    "personal": {
        "name": "Omkar Darekar",
        "email": "omkar@omkaritdetermination.com",
        "phone": "+91-XXXXXXXXXX",
        "linkedin": "linkedin.com/in/omkar-darekar",
        "github": "github.com/omkar-darekar",
        "website": "omkaritdetermination.com",
        "brand": "Omkar IT Determination"
    },
    "summary": """Full-Stack Developer & AI Automation Engineer with 3+ years of hands-on experience
building production-grade web applications and intelligent AI systems. Deep expertise in
Next.js, Python, and multi-agent AI orchestration frameworks (CrewAI, LangChain, LangGraph).
Proven track record of architecting scalable RAG systems, deploying LLM-powered automation
workflows, and shipping high-performance web products for clients across India.
Known for bridging the gap between cutting-edge AI research and practical business solutions.""",
    "skills": {
        "languages": ["Python", "JavaScript (ES2024+)", "TypeScript", "HTML5", "CSS3", "SQL"],
        "frontend": ["Next.js 14/15", "React 18", "Tailwind CSS", "Vite", "ShadCN/UI", "Framer Motion", "Three.js"],
        "backend": ["FastAPI", "Node.js", "Express.js", "REST APIs", "GraphQL", "WebSockets"],
        "ai_ml": [
            "LangChain", "LangGraph", "CrewAI", "AutoGen",
            "OpenAI API", "NVIDIA NIM", "Google Gemini API",
            "TensorFlow 2.x", "PyTorch", "Hugging Face Transformers",
            "RAG (Retrieval Augmented Generation)", "Vector Embeddings",
            "Sentence-Transformers (MiniLM-L6-v2, Gemma-300M)",
            "Multi-Agent Systems", "AI Workflow Automation",
            "Prompt Engineering", "FAISS", "ChromaDB", "Pinecone"
        ],
        "databases": ["MongoDB", "PostgreSQL", "MySQL", "Redis", "Supabase", "Firebase"],
        "devops": ["Docker", "GitHub Actions (CI/CD)", "Vercel", "Railway", "Linux", "Nginx"],
        "tools": ["Git", "VS Code", "Postman", "Figma", "n8n (workflow automation)"],
    },
    "experience": [
        {
            "company": "Omkar IT Determination (Self-Founded)",
            "role": "Founder & Full-Stack AI Engineer",
            "period": "Jan 2023 – Present",
            "location": "Pune, Maharashtra",
            "type": "Full-time / Freelance",
            "highlights": [
                "Architected and launched 6+ client web applications using Next.js + MongoDB + Tailwind CSS, reducing average client time-to-market by 40% through reusable component libraries",
                "Built an Intelligent Document Processing (IDP) system using LangGraph multi-agent pipeline, MiniLM-L6-v2 embeddings, and FAISS vector store — achieved 91% semantic retrieval accuracy on PDF contract analysis",
                "Designed a CrewAI-powered AI automation platform that replaced 15+ manual research workflows for clients, saving an average of 22 hours/week per client",
                "Developed a RAG-based knowledge assistant using LangChain + ChromaDB for a manufacturing client in Pune — reduced query resolution time by 65% (from 8 min to 2.8 min)",
                "Delivered portfolio websites for 12+ clients with dynamic admin dashboards and CMS features using Next.js + Supabase, achieving 100% on-time delivery",
                "Implemented Firebase + MongoDB dual-DB architecture for a SaaS product, handling 10K+ daily requests with 99.7% uptime",
            ]
        },
        {
            "company": "Freelance — Various Clients (India)",
            "role": "Full-Stack Developer & AI Consultant",
            "period": "Jun 2022 – Dec 2022",
            "location": "Remote / Pune",
            "type": "Freelance",
            "highlights": [
                "Delivered 4 React/Next.js web applications for clients in Mumbai and Hyderabad, generating ₹3.2L in revenue within the first 6 months",
                "Integrated OpenAI GPT-4 API into a customer support chatbot for an e-commerce client, reducing support ticket volume by 38%",
                "Built Python FastAPI backend services with JWT authentication and PostgreSQL database, achieving <80ms average API response time",
                "Designed and deployed n8n automation workflows connecting CRM, email, and Slack — eliminated 8+ hours of manual data entry per week for client teams",
            ]
        }
    ],
    "projects": [
        {
            "name": "🧠 Intelligent Document Processing (IDP) Agent",
            "stack": "Python, LangGraph, LangChain, MiniLM-L6-v2, FAISS, FastAPI, TensorFlow",
            "desc": "Flagship multi-agent AI system for semantic PDF analysis, RAG-based Q&A, and visual data extraction.",
            "impact": "65% reduction in document review time for manufacturing client"
        },
        {
            "name": "🤖 CrewAI Research Automation Platform",
            "stack": "Python, CrewAI, AutoGen, OpenAI API, FastAPI, Next.js, MongoDB",
            "desc": "Multi-agent research and content generation system with 5 specialized AI agents.",
            "impact": "Replaced 15+ manual workflows; saving 22 hrs/week per client"
        }
    ],
    "education": {
        "degree": "Bachelor of Technology — Computer Science & Engineering",
        "college": "Pune Institute of Technology",
        "year": "2022",
        "gpa": "8.4 / 10",
        "extras": ["AI/ML Specialization — Coursera (DeepLearning.AI)", "Full-Stack Web Development — Udemy", "LangChain & Vector Databases — DeepLearning.AI"]
    }
}

JD_TEMPLATES = {
    "Senior Full-Stack Developer": "Requirements: Multi-year experience with Next.js, React, Node.js/FastAPI. Expert in REST/GraphQL, SQL/NoSQL databases. Proficiency in Docker, CI/CD, and Cloud.",
    "Backend Architect": "Seeking high-level architect with deep Python/Django/FastAPI knowledge. Must handle high-concurrency systems, microservices optimization, and distributed databases.",
    "AI/ML Engineer": "Focus on GenAI. Requirements: Python, PyTorch/TensorFlow. Hands-on with LangChain, LlamaIndex, RAG pipelines, and Vector DBs.",
    "Technical Product Manager": "Requirements: Strong technical background + product strategy. Experience with Agile roadmap management and user-centric feature discovery."
}

JD_CATEGORIES = {
    "IT": ["Senior Full-Stack Developer", "Backend Architect"],
    "AI": ["AI/ML Engineer"],
    "MGMT": ["Technical Product Manager"]
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE DEFINITIONS - Visual Themes, Industries, and Layout Structures
# ═══════════════════════════════════════════════════════════════════════════════

# Visual Themes with distinct styling
RESUME_THEMES = {
    "modern": {
        "name": "Modern",
        "icon": "✨",
        "color": "#4f9cff",
        "accent": "#a855f7",
        "font": "Inter",
        "description": "Clean lines with subtle gradients",
        "header_style": "gradient_border",
        "section_style": "cards"
    },
    "classic": {
        "name": "Classic",
        "icon": "📜",
        "color": "#2c3e50",
        "accent": "#34495e",
        "font": "Georgia",
        "description": "Traditional serif elegance",
        "header_style": "underline",
        "section_style": "traditional"
    },
    "minimal": {
        "name": "Minimal",
        "icon": "⬜",
        "color": "#1a1a1a",
        "accent": "#666666",
        "font": "Helvetica",
        "description": "Pure whitespace focus",
        "header_style": "clean",
        "section_style": "minimal"
    },
    "professional": {
        "name": "Professional",
        "icon": "💼",
        "color": "#1e3a5f",
        "accent": "#2c5282",
        "font": "Segoe UI",
        "description": "Corporate navy aesthetic",
        "header_style": "boxed",
        "section_style": "corporate"
    },
    "creative": {
        "name": "Creative",
        "icon": "🎨",
        "color": "#ff6b6b",
        "accent": "#4ecdc4",
        "font": "Poppins",
        "description": "Bold colors with icons",
        "header_style": "colorful",
        "section_style": "modern_cards"
    }
}

# Mapping of Local HTML Templates in files/ directory
HTML_TEMPLATES = {
    "Minimalist": "files/resume-1-minimalist.html",
    "Dark Tech": "files/resume-2-dark-tech.html",
    "Colorful Creative": "files/resume-3-colorful-creative.html",
    "Timeline Narrative": "files/resume-4-timeline-narrative.html",
    "Card Based": "files/resume-5-card-based.html",
    "Sidebar Layout": "files/resume-6-sidebar-layout.html",
    "Masonry Grid": "files/resume-7-masonry-grid.html",
    "Glassmorphism": "files/resume-8-glassmorphism.html",
    "Vintage Retro": "files/resume-9-vintage-retro.html",
    "Data Visualization": "files/resume-10-data-visualization.html"
}

# Industry-specific templates with tailored content
INDUSTRY_TEMPLATES = {
    "tech": {
        "name": "Technology",
        "icon": "💻",
        "skills_highlight": ["Programming", "Frameworks", "AI/ML", "Cloud"],
        "sections_order": ["summary", "skills", "experience", "projects", "education"],
        "summary_focus": "Technical expertise and innovation",
        "badge_color": "#3b82f6"
    },
    "healthcare": {
        "name": "Healthcare",
        "icon": "🏥",
        "skills_highlight": ["Patient Care", "Clinical", "Certifications", "EMR/EHR"],
        "sections_order": ["summary", "certifications", "experience", "skills", "education"],
        "summary_focus": "Patient care and clinical excellence",
        "badge_color": "#10b981"
    },
    "finance": {
        "name": "Finance",
        "icon": "💰",
        "skills_highlight": ["Financial Analysis", "Risk Management", "Compliance", "Forecasting"],
        "sections_order": ["summary", "skills", "experience", "certifications", "education"],
        "summary_focus": "Financial acumen and risk management",
        "badge_color": "#f59e0b"
    },
    "marketing": {
        "name": "Marketing",
        "icon": "📢",
        "skills_highlight": ["Digital Marketing", "Analytics", "Content Strategy", "SEO/SEM"],
        "sections_order": ["summary", "skills", "projects", "experience", "education"],
        "summary_focus": "Brand growth and audience engagement",
        "badge_color": "#e11d48"
    },
    "education": {
        "name": "Education",
        "icon": "📚",
        "skills_highlight": ["Curriculum Design", "Student Engagement", "Assessment", "Technology Integration"],
        "sections_order": ["summary", "education", "experience", "skills", "certifications"],
        "summary_focus": "Student success and pedagogical excellence",
        "badge_color": "#8b5cf6"
    },
    "general": {
        "name": "General Professional",
        "icon": "🎯",
        "skills_highlight": ["Leadership", "Communication", "Problem Solving", "Project Management"],
        "sections_order": ["summary", "experience", "skills", "education"],
        "summary_focus": "Professional excellence and results",
        "badge_color": "#6366f1"
    }
}

# Resume structure/layout types
RESUME_STRUCTURES = {
    "chronological": {
        "name": "Chronological",
        "icon": "📅",
        "description": "Experience-focused timeline",
        "section_order": ["header", "summary", "experience", "skills", "education", "projects"],
        "experience_format": "timeline",
        "skills_format": "grouped",
        "emphasis": "career_progression"
    },
    "functional": {
        "name": "Functional",
        "icon": "🎯",
        "description": "Skills-focused competencies",
        "section_order": ["header", "summary", "skills", "experience", "education"],
        "experience_format": "compact",
        "skills_format": "detailed",
        "emphasis": "competencies"
    },
    "hybrid": {
        "name": "Hybrid",
        "icon": "⚖️",
        "description": "Balanced skills + experience",
        "section_order": ["header", "summary", "key_highlights", "experience", "skills", "education"],
        "experience_format": "detailed",
        "skills_format": "categorized",
        "emphasis": "balanced"
    },
    "executive": {
        "name": "Executive",
        "icon": "👔",
        "description": "Leadership-focused summary",
        "section_order": ["header", "executive_summary", "key_achievements", "experience", "board_positions", "education"],
        "experience_format": "highlights",
        "skills_format": "strategic",
        "emphasis": "leadership"
    }
}

# Sample industry content for preview
INDUSTRY_SAMPLE_CONTENT = {
    "tech": """# Software Engineer

**Full-Stack Developer** | San Francisco, CA | linkedin.com/in/johndoe

## Professional Summary
Innovative Software Engineer with 5+ years of experience building scalable web applications. Expert in React, Node.js, and cloud technologies. Passionate about clean code and user-centric design.

## Technical Skills
**Languages:** JavaScript, TypeScript, Python, Go
**Frontend:** React, Next.js, Vue.js, Tailwind CSS
**Backend:** Node.js, Express, FastAPI, GraphQL
**Cloud:** AWS, GCP, Docker, Kubernetes

## Professional Experience

### Senior Software Engineer | TechCorp Inc.
*January 2022 – Present*
- Architected microservices handling 1M+ daily requests
- Reduced API latency by 40% through GraphQL optimization
- Mentored team of 5 junior developers

### Software Engineer | StartupXYZ
*June 2019 – December 2021*
- Built full-stack SaaS platform from scratch
- Implemented CI/CD pipelines reducing deployment time by 60%

## Education
B.S. Computer Science, Stanford University (2019)""",

    "healthcare": """# Registered Nurse

**RN, BSN, CCRN** | Boston, MA | nurse.jane@email.com

## Professional Summary
Compassionate Registered Nurse with 6+ years of critical care experience. Specialized in ICU and emergency care with a focus on patient advocacy and evidence-based practice.

## Certifications & Licenses
- Registered Nurse License (RN) - MA #123456
- CCRN (Critical Care Registered Nurse)
- BLS, ACLS, PALS Certified

## Clinical Experience

### Critical Care Nurse | Massachusetts General Hospital
*March 2020 – Present*
- Provide direct care to 2-3 critically ill patients per shift in 24-bed ICU
- Collaborate with multidisciplinary team on complex cases
- Precept 3 nursing students annually

### Staff Nurse | City Medical Center
*June 2018 – February 2020*
- Managed patient care on 30-bed medical-surgical unit
- Achieved 95% patient satisfaction rating

## Education
Bachelor of Science in Nursing, Boston College (2018)""",

    "finance": """# Financial Analyst

**CFA Level II Candidate** | New York, NY | analyst@email.com

## Professional Summary
Detail-oriented Financial Analyst with expertise in financial modeling, risk assessment, and investment analysis. Track record of delivering actionable insights that drive portfolio performance.

## Core Competencies
- Financial Modeling & Valuation
- Risk Management & Compliance
- Portfolio Analysis
- Market Research
- SQL & Excel Advanced

## Professional Experience

### Senior Financial Analyst | Goldman Sachs
*March 2021 – Present*
- Manage $500M portfolio analysis and reporting
- Develop risk models reducing exposure by 15%
- Present weekly market updates to executive team

### Financial Analyst | JP Morgan
*July 2019 – February 2021*
- Conducted due diligence on 50+ investment opportunities
- Built automated reporting dashboards saving 20 hours/week

## Education
B.S. Finance, Wharton School, University of Pennsylvania (2019)""",

    "marketing": """# Marketing Manager

**Digital Marketing Specialist** | Austin, TX | marketer@email.com

## Professional Summary
Results-driven Marketing Manager with 7+ years experience driving brand growth across digital channels. Expert in content strategy, SEO/SEM, and marketing automation.

## Marketing Expertise
- SEO/SEM & Content Strategy
- Social Media Management
- Marketing Automation (HubSpot, Marketo)
- Analytics & Attribution
- Brand Development

## Campaign Highlights
- Increased organic traffic by 200% in 12 months
- Generated $2M pipeline through targeted campaigns
- Reduced CAC by 35% through optimization

## Professional Experience

### Marketing Manager | TechScale Inc.
*January 2020 – Present*
- Lead marketing team of 8 across content, paid, and product marketing
- Orchestrate $1M annual marketing budget
- Achieve 150% of pipeline targets 3 years running

### Digital Marketing Specialist | GrowthAgency
*June 2017 – December 2019*
- Managed $500K monthly ad spend across Google and Facebook

## Education
B.A. Marketing, University of Texas at Austin (2017)""",

    "education": """# High School Teacher

**Mathematics & STEM Educator** | Chicago, IL | teacher@school.edu

## Professional Summary
Dedicated educator with 8+ years teaching mathematics and leading STEM initiatives. Committed to fostering inclusive learning environments and leveraging technology to enhance student engagement.

## Teaching Credentials
- Illinois Professional Educator License (6-12 Mathematics)
- ESL Endorsement
- Google Certified Educator

## Teaching Experience

### Mathematics Teacher | Lincoln High School
*August 2018 – Present*
- Teach Algebra II, Pre-Calculus, and AP Statistics (120 students/year)
- Implemented flipped classroom model increasing pass rates by 25%
- Lead Math Department Professional Learning Community

### Middle School Teacher | Washington Academy
*August 2016 – June 2018*
- Taught 7th and 8th grade mathematics
- Coordinated school-wide science fair

## Education
M.Ed. Curriculum & Instruction, Northwestern University (2016)
B.S. Mathematics, University of Illinois (2014)""",

    "general": """# Project Manager

**PMP Certified** | Denver, CO | pm@email.com

## Professional Summary
Versatile Project Manager with 6+ years leading cross-functional teams and delivering complex projects on time and under budget. Expert in Agile and Waterfall methodologies.

## Key Skills
- Project Planning & Execution
- Stakeholder Management
- Risk Assessment
- Budget Management ($5M+ experience)
- Agile/Scrum Certified

## Professional Experience

### Senior Project Manager | Enterprise Solutions
*March 2020 – Present*
- Lead $10M portfolio of 15 concurrent projects
- Manage team of 25 across 3 departments
- Achieve 98% on-time delivery rate

### Project Manager | TechSystems Inc.
*June 2017 – February 2020*
- Delivered 12 software projects using Agile methodology
- Reduced project overruns by 40% through improved planning

## Education
B.S. Business Administration, Colorado State University (2017)"""
}

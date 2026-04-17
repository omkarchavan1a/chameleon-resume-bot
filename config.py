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

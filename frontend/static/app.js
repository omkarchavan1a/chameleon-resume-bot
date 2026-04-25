/* ═══════════════════════════════════════════════════════════════════════════
   Chameleon Resume Bot — Frontend Logic (v2 — Master Data Pre-loaded)
   ═══════════════════════════════════════════════════════════════════════════ */

const API_BASE = '';
let historyData = []; // Local cache of recent generations
let currentTheme = 'minimalist'; // Default theme
let currentMarkdown = ''; // Current rendered resume markdown

// ═══════════════════════════════════════════════════════════════════════════════
//  USER AUTH CHECK — Redirect to landing if not registered
// ═══════════════════════════════════════════════════════════════════════════════
(function checkUserAuth() {
  const userEmail = localStorage.getItem('user_email');
  if (!userEmail) {
    // Not registered, redirect to landing page
    window.location.href = '/';
    return;
  }
  // User is registered, proceed with app
})();

// ══════════════════════════════════════════════════════════════════════════════
//  MASTER EXPERIENCE DATA — Full profile for Omkar (Omkar IT Determination)
//  Edit this object to keep your profile up to date
// ══════════════════════════════════════════════════════════════════════════════
const MASTER_PROFILE = {
  personal: {
    name:     "Omkar Darekar",
    email:    "omkar@omkaritdetermination.com",
    phone:    "+91-XXXXXXXXXX",
    linkedin: "linkedin.com/in/omkar-darekar",
    github:   "github.com/omkar-darekar",
    website:  "omkaritdetermination.com",
    brand:    "Omkar IT Determination"
  },

  summary: `Full-Stack Developer & AI Automation Engineer with 3+ years of hands-on experience
building production-grade web applications and intelligent AI systems. Deep expertise in
Next.js, Python, and multi-agent AI orchestration frameworks (CrewAI, LangChain, LangGraph).
Proven track record of architecting scalable RAG systems, deploying LLM-powered automation
workflows, and shipping high-performance web products for clients across India.
Known for bridging the gap between cutting-edge AI research and practical business solutions.`,

  skills: {
    languages:   ["Python", "JavaScript (ES2024+)", "TypeScript", "HTML5", "CSS3", "SQL"],
    frontend:    ["Next.js 14/15", "React 18", "Tailwind CSS", "Vite", "ShadCN/UI", "Framer Motion", "Three.js"],
    backend:     ["FastAPI", "Node.js", "Express.js", "REST APIs", "GraphQL", "WebSockets"],
    ai_ml:       [
      "LangChain", "LangGraph", "CrewAI", "AutoGen",
      "OpenAI API", "NVIDIA NIM", "Google Gemini API",
      "TensorFlow 2.x", "PyTorch", "Hugging Face Transformers",
      "RAG (Retrieval Augmented Generation)", "Vector Embeddings",
      "Sentence-Transformers (MiniLM-L6-v2, Gemma-300M)",
      "Multi-Agent Systems", "AI Workflow Automation",
      "Prompt Engineering", "FAISS", "ChromaDB", "Pinecone"
    ],
    databases:   ["MongoDB", "PostgreSQL", "MySQL", "Redis", "Supabase", "Firebase"],
    devops:      ["Docker", "GitHub Actions (CI/CD)", "Vercel", "Railway", "Linux", "Nginx"],
    tools:       ["Git", "VS Code", "Postman", "Figma", "n8n (workflow automation)"],
  },

  experience: [
    {
      company:    "Omkar IT Determination (Self-Founded)",
      role:       "Founder & Full-Stack AI Engineer",
      period:     "Jan 2023 – Present",
      location:   "Pune, Maharashtra",
      type:       "Full-time / Freelance",
      highlights: [
        "Architected and launched 6+ client web applications using Next.js + MongoDB + Tailwind CSS, reducing average client time-to-market by 40% through reusable component libraries",
        "Built an Intelligent Document Processing (IDP) system using LangGraph multi-agent pipeline, MiniLM-L6-v2 embeddings, and FAISS vector store — achieved 91% semantic retrieval accuracy on PDF contract analysis",
        "Designed a CrewAI-powered AI automation platform that replaced 15+ manual research workflows for clients, saving an average of 22 hours/week per client",
        "Developed a RAG-based knowledge assistant using LangChain + ChromaDB for a manufacturing client in Pune — reduced query resolution time by 65% (from 8 min to 2.8 min)",
        "Delivered portfolio websites for 12+ clients with dynamic admin dashboards and CMS features using Next.js + Supabase, achieving 100% on-time delivery",
        "Implemented Firebase + MongoDB dual-DB architecture for a SaaS product, handling 10K+ daily requests with 99.7% uptime",
      ]
    },
    {
      company:    "Freelance — Various Clients (India)",
      role:       "Full-Stack Developer & AI Consultant",
      period:     "Jun 2022 – Dec 2022",
      location:   "Remote / Pune",
      type:       "Freelance",
      highlights: [
        "Delivered 4 React/Next.js web applications for clients in Mumbai and Hyderabad, generating ₹3.2L in revenue within the first 6 months",
        "Integrated OpenAI GPT-4 API into a customer support chatbot for an e-commerce client, reducing support ticket volume by 38%",
        "Built Python FastAPI backend services with JWT authentication and PostgreSQL database, achieving <80ms average API response time",
        "Designed and deployed n8n automation workflows connecting CRM, email, and Slack — eliminated 8+ hours of manual data entry per week for client teams",
      ]
    },
    {
      company:    "Self-Learning & Open Source",
      role:       "AI/ML Research & Development",
      period:     "Jan 2022 – May 2022",
      location:   "Remote",
      type:       "Personal R&D",
      highlights: [
        "Completed 3 end-to-end ML projects using TensorFlow and PyTorch covering NLP, computer vision, and time-series forecasting",
        "Contributed to open-source LangChain examples repository — 45+ GitHub stars on personal AI toolkit library",
        "Published 5 technical blog posts on RAG architecture and CrewAI agent design patterns — 2,800+ cumulative reads",
      ]
    }
  ],

  projects: [
    {
      name:    "🧠 Intelligent Document Processing (IDP) Agent",
      stack:   "Python, LangGraph, LangChain, MiniLM-L6-v2, FAISS, FastAPI, TensorFlow",
      desc:    "Flagship multi-agent AI system for semantic PDF analysis, RAG-based Q&A, and visual data extraction. Uses MiniLM for mobile context and Gemma-300M for local inference. Processes 50+ page contracts in <12 seconds with 91% retrieval accuracy.",
      impact:  "65% reduction in document review time for manufacturing client",
      github:  "github.com/omkar-darekar/idp-agent"
    },
    {
      name:    "🤖 CrewAI Research Automation Platform",
      stack:   "Python, CrewAI, AutoGen, OpenAI API, FastAPI, Next.js, MongoDB",
      desc:    "Multi-agent research and content generation system with 5 specialized AI agents (Researcher, Writer, Editor, SEO Analyst, Publisher). Supports parallel agent execution and human-in-the-loop review workflows.",
      impact:  "Replaced 15+ manual workflows; saving 22 hrs/week per client",
      github:  "github.com/omkar-darekar/crewai-research-platform"
    },
    {
      name:    "🚀 Portfolio & Admin CMS Platform",
      stack:   "Next.js 15, Tailwind CSS, MongoDB, Vercel, Firebase Auth, Framer Motion",
      desc:    "Production portfolio website with dynamic full-stack CMS admin dashboard. Features real-time content editing, project management, blog publishing, and contact form with MongoDB storage. Deployed on Vercel with 99.9% uptime.",
      impact:  "Used by 12+ clients; 100% on-time delivery, Lighthouse score 96+",
      github:  "github.com/omkar-darekar/portfolio-cms"
    },
    {
      name:    "💬 AI Customer Support Chatbot",
      stack:   "Next.js, OpenAI GPT-4 API, LangChain, Pinecone, Node.js, MongoDB",
      desc:    "RAG-powered customer support bot with product knowledge base embedding, conversation memory, and escalation routing. Deployed for e-commerce client with 10K+ monthly active users.",
      impact:  "38% reduction in support tickets; avg resolution in <90 seconds",
      github:  "github.com/omkar-darekar/ai-support-bot"
    },
    {
      name:    "🔄 n8n + AI Workflow Automation Engine",
      stack:   "n8n, Python, OpenAI API, PostgreSQL, REST APIs, Zapier",
      desc:    "No-code/low-code automation platform connecting 20+ business tools. AI-enhanced data processing nodes for intelligent routing, summarization, and classification of business workflows.",
      impact:  "Eliminated 8+ hrs/week manual work per client across 3 businesses",
      github:  "github.com/omkar-darekar/ai-workflow-engine"
    },
    {
      name:    "📊 Real-Time Analytics Dashboard",
      stack:   "Next.js, Recharts, PostgreSQL, FastAPI, Docker, Redis",
      desc:    "Real-time business intelligence dashboard with live data streaming via WebSockets, interactive drill-down charts, and PDF report export. Handles 50K+ data points per refresh.",
      impact:  "Reduced manual reporting by 100%; stakeholder review time cut by 4 hrs/week",
      github:  "github.com/omkar-darekar/realtime-analytics"
    }
  ],

  education: {
    degree:  "Bachelor of Technology — Computer Science & Engineering",
    college: "Pune Institute of Technology",
    year:    "2022",
    gpa:     "8.4 / 10",
    extras:  ["AI/ML Specialization — Coursera (DeepLearning.AI)", "Full-Stack Web Development — Udemy", "LangChain & Vector Databases — DeepLearning.AI"]
  },

  certifications: [
    "Google Associate Cloud Engineer (GCP) — 2023",
    "DeepLearning.AI LangChain for LLM Application Development",
    "AWS Certified Cloud Practitioner — 2023",
    "Meta Front-End Developer Certificate"
  ],

  softSkills: [
    "Client Communication & Requirement Gathering",
    "Agile / Scrum Project Management",
    "Technical Documentation Writing",
    "Problem-solving under tight deadlines",
    "Cross-functional team collaboration"
  ],

  languages_spoken: ["English (Professional)", "Hindi (Native)", "Marathi (Native)"],

  achievements: [
    "Built and launched 6+ production web apps serving real clients in India",
    "Bootstrapped 'Omkar IT Determination' from ₹0 to ₹5L+ revenue in first year",
    "45+ GitHub stars on personal AI toolkit library",
    "Mentored 3 junior developers in Python and React fundamentals"
  ]
};

// ══════════════════════════════════════════════════════════════════════════════
//  JOB DESCRIPTION TEMPLATES — Role-specific ATS-optimized JDs
// ══════════════════════════════════════════════════════════════════════════════
const JD_TEMPLATES = {
  // IT & Software
  "Senior Full-Stack Developer": `Requirements: Multi-year experience with Next.js, React, Node.js/FastAPI. Expert in REST/GraphQL, SQL/NoSQL databases. Proficiency in Docker, CI/CD, and Cloud. Responsibilities includes architecting scalable web products and mentoring junior devs.`,
  "Backend Architect": `Seeking high-level architect with deep Python/Django/FastAPI knowledge. Must handle high-concurrency systems, microservices optimization, and distributed databases. Deep understanding of Redis, Kafka, and Kubernetes required.`,
  "Cloud Security Engineer": `Lead security audits, implement Zero Trust architecture, and manage cloud identity. Proficiency in AWS Security Hub, Azure Sentinel, or GCP Armor. Strong focus on SOX/SOC2 compliance and automated threat detection.`,
  "Frontend Lead (UX Focused)": `Requirements: Expert Next.js dev with flair for motion (GSAP/Framer). Strong sense of design systems, typography, and accessibility (WCAG). Responsibility to lead UI team and ship elite-feeling products.`,

  // AI & Data
  "AI/ML Engineer": `Focus on GenAI. Requirements: Python, PyTorch/TensorFlow. Hands-on with LangChain, LlamaIndex, RAG pipelines, and Vector DBs. Experience with fine-tuning LLMs and MLOps deployment is essential.`,
  "NLP Specialist": `Seeking expert in text analysis, sentiment engines, and custom LLM evaluation. Must be proficient with HuggingFace, transformer architectures, and semantic search optimization.`,
  "Data Scientist (GenAI Focused)": `Bridge the gap between raw data and AI insight. Experience with data engineering and pipeline building. Must know how to evaluate LLM outputs and build synthetic datasets for training.`,
  "AI Automation Consultant": `Expert in process mapping and AI-lead ROI strategy. Proficiency with CrewAI, AutoGen, or LangGraph. Experience deploying n8n or Zapier automations for multi-step enterprise workflows.`,

  // Mobile & DevOps
  "Mobile App Lead (React Native)": `Build cross-platform high-performance apps. Requirements: React Native, Expo, App Store/Play Store deployment. Knowledge of mobile-first UX and deep-linking is required.`,
  "DevOps Strategist": `Optimization expert for build pipelines. Mastery of GitHub Actions, Terraform/Pulumi (IaC), and AWS/GCP architecture. Focus on 99.99% uptime and auto-scaling logic.`,
  "Site Reliability Engineer (SRE)": `Focus on monitoring and fault tolerance. Experience with Prometheus, Grafana, and incident response management. Mastery of Kubernetes and serverless performance.`,

  // Strategy & Management
  "Technical Product Manager": `Requirements: Strong technical background + product strategy. Experience with Agile roadmap management and user-centric feature discovery. Ability to bridge the gap between AI research and marketable features.`,
  "Solutions Architect": `Directly work with clients to design complex technical integrations. Strong communication and ability to draft comprehensive technical proposals and system diagrams.`,
  "Technical Project Manager (AI/ML)": `Manage AI-centric development cycles. Experience with sprint planning in research-intensive environments. Strong Jira & documentation skills.`,
  "CTO (Start-up / Fractional)": `Strategic leadership for seed/series-A startups. Ability to build initial tech stack (Next.js/Python), hire engineering teams, and define technical roadmap for growth.`
};

// Category mapping for dynamic pill injection
const JD_CATEGORIES = {
  "it":      ["Senior Full-Stack Developer", "Backend Architect", "Frontend Lead (UX Focused)"],
  "ai":      ["AI/ML Engineer", "NLP Specialist", "Data Scientist (GenAI Focused)", "AI Automation Consultant"],
  "backend": ["Cloud Security Engineer", "DevOps Strategist", "Site Reliability Engineer (SRE)"],
  "mgmt":    ["Technical Product Manager", "Solutions Architect", "Technical Project Manager (AI/ML)", "CTO (Start-up / Fractional)"]
};

// ══════════════════════════════════════════════════════════════════════════════
//  HELPER: serialize master profile to clean text for the API
// ══════════════════════════════════════════════════════════════════════════════
function serializeMasterProfile(profile) {
  const p = profile;
  let text = '';

  text += `=== PERSONAL INFO ===\n`;
  text += `Name: ${p.personal.name}\nBrand: ${p.personal.brand}\nEmail: ${p.personal.email}\nPhone: ${p.personal.phone}\nLinkedIn: ${p.personal.linkedin}\nGitHub: ${p.personal.github}\nWebsite: ${p.personal.website}\n\n`;

  text += `=== PROFESSIONAL SUMMARY ===\n${p.summary}\n\n`;

  text += `=== TECHNICAL SKILLS ===\n`;
  text += `Languages: ${p.skills.languages.join(', ')}\n`;
  text += `Frontend: ${p.skills.frontend.join(', ')}\n`;
  text += `Backend: ${p.skills.backend.join(', ')}\n`;
  text += `AI/ML: ${p.skills.ai_ml.join(', ')}\n`;
  text += `Databases: ${p.skills.databases.join(', ')}\n`;
  text += `DevOps & Tools: ${p.skills.devops.join(', ')}, ${p.skills.tools.join(', ')}\n\n`;

  text += `=== WORK EXPERIENCE ===\n`;
  p.experience.forEach(exp => {
    text += `\n[${exp.role}] @ ${exp.company} | ${exp.period} | ${exp.location} | ${exp.type}\n`;
    exp.highlights.forEach(h => { text += `  • ${h}\n`; });
  });

  text += `\n=== KEY PROJECTS ===\n`;
  p.projects.forEach(proj => {
    text += `\n${proj.name}\n`;
    text += `  Stack: ${proj.stack}\n`;
    text += `  Description: ${proj.desc}\n`;
    text += `  Impact: ${proj.impact}\n`;
    text += `  GitHub: ${proj.github}\n`;
  });

  text += `\n=== EDUCATION ===\n`;
  text += `${p.education.degree} — ${p.education.college} (${p.education.year}) | GPA: ${p.education.gpa}\n`;
  text += `Additional Courses: ${p.education.extras.join('; ')}\n`;

  text += `\n=== CERTIFICATIONS ===\n`;
  p.certifications.forEach(c => { text += `  • ${c}\n`; });

  text += `\n=== ACHIEVEMENTS ===\n`;
  p.achievements.forEach(a => { text += `  • ${a}\n`; });

  text += `\n=== SOFT SKILLS ===\n${p.softSkills.join(', ')}\n`;
  text += `\n=== LANGUAGES SPOKEN ===\n${p.languages_spoken.join(', ')}\n`;

  return text;
}

// ═══════════════════════════════════════════════════════════════════════════════
//  ANIMATED BACKGROUND CANVAS
// ═══════════════════════════════════════════════════════════════════════════════
(function initCanvas() {
  const canvas = document.getElementById('bg-canvas');
  const ctx    = canvas.getContext('2d');
  let W, H;
  const particles = [];

  function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
  window.addEventListener('resize', resize);
  resize();

  for (let i = 0; i < 100; i++) particles.push({
    x:  Math.random() * W, y:  Math.random() * H,
    r:  Math.random() * 1.5 + 0.5,
    dx: (Math.random() - 0.5) * 0.3, dy: (Math.random() - 0.5) * 0.3,
    a:  Math.random(),
    color: `hsl(${Math.random() > 0.5 ? 220 : 270}, 80%, 70%)`
  });

  function draw() {
    ctx.clearRect(0, 0, W, H);
    const grad = ctx.createRadialGradient(W * 0.3, H * 0.2, 0, W * 0.3, H * 0.2, W * 0.7);
    grad.addColorStop(0, 'rgba(79,156,255,0.04)');
    grad.addColorStop(1, 'transparent');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.dx; p.y += p.dy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color.replace(')', `,${p.a * 0.4})`).replace('hsl', 'hsla');
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

// ═══════════════════════════════════════════════════════════════════════════════
//  HEALTH CHECK
// ═══════════════════════════════════════════════════════════════════════════════
async function checkHealth() {
  const dot = document.getElementById('health-indicator');
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    dot.className = res.ok ? 'health-dot online' : 'health-dot offline';
    dot.title     = res.ok ? 'API Online ✓'      : 'API Error';
  } catch {
    dot.className = 'health-dot offline';
    dot.title     = 'API Offline';
  }
}
checkHealth();
setInterval(checkHealth, 30_000);

// Profile is internal — no textarea to fill

// ═══════════════════════════════════════════════════════════════════════════════
//  CITY PILLS (only city pills — role pills handled by quickRole() in HTML)
// ═══════════════════════════════════════════════════════════════════════════════
document.querySelectorAll('.city-pills:not(.role-pills) .pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.city-pills:not(.role-pills) .pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    document.getElementById('target-city').value = pill.dataset.city;
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
//  JD TEMPLATE SELECTOR
// ═══════════════════════════════════════════════════════════════════════════════
document.querySelectorAll('.jd-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.jd-pill').forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
    const role = pill.dataset.role;
    if (JD_TEMPLATES[role]) {
      document.getElementById('job-description').value = JD_TEMPLATES[role];
      // Also auto-fill position if empty
      const posField = document.getElementById('target-position');
      if (!posField.value.trim()) posField.value = role;
    }
    showToast(`📋 JD loaded: ${role}`);
  });
});

// ═══════════════════════════════════════════════════════════════════════════════
//  PDF UPLOAD & EXTRACTION LOGIC
// ═══════════════════════════════════════════════════════════════════════════════
let uploadedResumeText = null;

const pdfUploadInput = document.getElementById('pdf-upload');
const uploadLabel     = document.getElementById('upload-label');
const extractionStatus = document.getElementById('extraction-status');
const uploadSuccess    = document.getElementById('upload-success');
const fileNameDisplay  = document.getElementById('file-name-display');
const btnRemovePdf     = document.getElementById('btn-remove-pdf');

// File Selection
pdfUploadInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) handleFileUpload(file);
});

// Drag & Drop
uploadLabel.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadLabel.classList.add('dragover');
});
uploadLabel.addEventListener('dragleave', () => {
  uploadLabel.classList.remove('dragover');
});
uploadLabel.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadLabel.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') {
    handleFileUpload(file);
  } else {
    showToast('❌ Please upload a valid PDF file.');
  }
});

// Removal
btnRemovePdf.addEventListener('click', () => {
  uploadedResumeText = null;
  pdfUploadInput.value = '';
  show('upload-label');
  hide('upload-success');
  hide('extraction-status');
  showToast('🗑️ Uploaded resume removed');
});

async function handleFileUpload(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    showToast('❌ Only PDF files are supported.');
    return;
  }

  hide('upload-label');
  show('extraction-status');
  hide('upload-success');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_BASE}/api/extract-pdf`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(errorData.detail || `Server error: ${res.status}`);
    }
    const data = await res.json();

    uploadedResumeText = data.text;
    fileNameDisplay.textContent = file.name;
    
    hide('extraction-status');
    show('upload-success');
    showToast('✅ Resume details imported successfully!');
    
    // Smooth scroll to next step
    setTimeout(() => {
      document.getElementById('target-position').focus();
    }, 500);

  } catch (err) {
    uploadedResumeText = null;
    hide('extraction-status');
    show('upload-label');
    console.error('PDF Extraction Error:', err);
    showToast(`❌ Error: ${err.message}`);
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  CLEAR BUTTON
// ═══════════════════════════════════════════════════════════════════════════════
document.getElementById('clear-btn').addEventListener('click', () => {
  document.getElementById('target-position').value = '';
  document.getElementById('target-city').value     = '';
  document.getElementById('job-description').value = '';
  document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.jd-pill').forEach(p => p.classList.remove('active'));
  resetOutput();
  showToast('🗑️ Form cleared');
});

// ═══════════════════════════════════════════════════════════════════════════════
//  STATE MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════


function resetOutput() {
  show('idle-state');
  hide('loading-state');
  hide('output-content');
  document.getElementById('output-controls').style.display = 'none';
  document.getElementById('token-info').classList.add('hidden');
  currentMarkdown = '';
}
function show(id) { document.getElementById(id).classList.remove('hidden'); }
function hide(id) { document.getElementById(id).classList.add('hidden'); }

// ═══════════════════════════════════════════════════════════════════════════════
//  LOADING STEP SEQUENCER
// ═══════════════════════════════════════════════════════════════════════════════
function animateLoadingSteps(position) {
  document.getElementById('step-tailor').textContent = `✂️ Tailoring for ${position}...`;
  const steps = ['step-analyze','step-tailor','step-ats','step-format'];
  let i = 0;
  const iv = setInterval(() => {
    if (i > 0) document.getElementById(steps[i-1]).className = 'load-step done';
    if (i < steps.length) { document.getElementById(steps[i]).className = 'load-step active'; i++; }
    else clearInterval(iv);
  }, 900);
  return iv;
}
function resetLoadingSteps() {
  ['step-analyze','step-tailor','step-ats','step-format'].forEach(id => {
    document.getElementById(id).className = 'load-step';
  });
  document.getElementById('step-analyze').className = 'load-step active';
}

// ═══════════════════════════════════════════════════════════════════════════════
//  DESIGN & THEME LOGIC
// ═══════════════════════════════════════════════════════════════════════════════
function selectTheme(btn) {
  currentTheme = btn.dataset.theme;
  const themeName = btn.dataset.label || btn.querySelector('span').textContent;

  document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('active-theme-name').textContent = themeName;

  // If a resume is already rendered, re-render with new theme
  if (currentMarkdown) {
    injectIntoTheme(currentMarkdown);
  }
  showToast(`🎨 Theme: ${themeName}`);
}

// Parse markdown into structured data for HTML injection
function parseMarkdownToData(md) {
  const lines = md.split('\n');
  const data = { name:'', title:'', contact:[], summary:'', skills:[], experience:[], education:[], projects:[] };
  let section = '';
  let currentEntry = null;

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;

    // H1 = Name
    if (/^# /.test(line)) { data.name = line.replace(/^# /, '').trim(); continue; }
    // H2 = Section headers
    if (/^## /.test(line)) {
      const h = line.replace(/^## /, '').toLowerCase();
      if (h.includes('summary') || h.includes('profile'))     section = 'summary';
      else if (h.includes('experience') || h.includes('work')) section = 'experience';
      else if (h.includes('skill') || h.includes('technical')) section = 'skills';
      else if (h.includes('education'))                         section = 'education';
      else if (h.includes('project'))                           section = 'projects';
      else section = 'other';
      currentEntry = null;
      continue;
    }
    // H3 = job title / entry header
    if (/^### /.test(line)) {
      const text = line.replace(/^### /, '').trim();
      // Parse "Position @ Company | Date" or "Position — Company (Date)"
      const m = text.match(/^(.+?)\s*[@|–—]\s*(.+?)\s*[|(]?\s*(\d{4}[^)]*)?\)?$/);
      currentEntry = m ? { position:m[1].trim(), org:m[2].trim(), date:m[3]||'', bullets:[] } : { position:text, org:'', date:'', bullets:[] };
      if (section==='experience') data.experience.push(currentEntry);
      else if (section==='education') data.education.push(currentEntry);
      else if (section==='projects') data.projects.push(currentEntry);
      continue;
    }
    // Bold line (no H3) might be a sub-heading like contact info
    if (/^\*\*/.test(line) && !section) {
      // Likely title line under name
      data.title = line.replace(/\*\*/g,'').trim();
      continue;
    }
    // Bullet points
    if (/^[-*]\s/.test(line)) {
      const bullet = line.replace(/^[-*]\s/, '').trim();
      if (section === 'summary') { data.contact.push(bullet); continue; }
      if (currentEntry) { currentEntry.bullets.push(bullet); continue; }
      if (section === 'skills') { data.skills.push(bullet); continue; }
      continue;
    }
    // Plain lines
    if (section === 'summary') {
      data.summary += (data.summary ? ' ' : '') + line;
    } else if (section === 'skills') {
      // Comma-separated skills
      line.split(',').forEach(s => { const t=s.replace(/\*\*/g,'').trim(); if(t) data.skills.push(t); });
    } else if (!section && line.includes('@') || line.includes('+91') || line.includes('linkedin') || line.includes('github')) {
      data.contact.push(line.replace(/\*\*/g,'').trim());
    } else if (!section && !data.title) {
      data.title = line.replace(/\*\*/g,'').trim();
    }
  }
  return data;
}

// Inject LLM markdown into a fetched theme HTML string
function buildThemedHTML(themeHTML, md) {
  const d = parseMarkdownToData(md);
  const htmlMd = marked.parse(md); // fallback full render

  // Replace common placeholder patterns in the theme HTML
  let out = themeHTML
    // Name
    .replace(/SARAH CHEN|ALEX RODRIGUEZ|DAVID PARK|MARCUS JOHNSON|ELENA VASQUEZ|JAMES WRIGHT|PRIYA SHARMA|THOMAS CHEN|[A-Z]{2,}\s[A-Z]{2,}/g,
              d.name ? d.name.toUpperCase() : 'YOUR NAME')
    // Title/role line (italic or class-based)
    .replace(/(Product Designer &amp; Creative Technologist|Full Stack Engineer \| Cloud Architecture|Financial Analyst|[A-Za-z]+ &amp; [A-Za-z]+)/g,
              d.title || d.name)
    // Email
    .replace(/sarah@example\.com|alex@example\.com|david@example\.com/g,
              d.contact.find(c=>c.includes('@')) || 'email@example.com')
    // Phone
    .replace(/\+1 \(555\) \d{3}-\d{4}/g,
              d.contact.find(c=>c.includes('+91')||c.match(/\d{10}/)) || '+91-0000000000');

  // Inject a full markdown-rendered content block before </body> as a safe fallback
  // for themes where pattern replacement may not cover all data
  const resumeBlock = `
    <style>
      .crb-injected-resume { display:none; }
    </style>
    <div class="crb-injected-resume" data-markdown="1">${htmlMd}</div>`;

  return out.replace('</body>', resumeBlock + '\n</body>');
}

async function injectIntoTheme(markdown) {
  const iframe = document.getElementById('resume-iframe');
  if (!iframe) return;

  try {
    const res = await fetch(`${API_BASE}/api/get-theme/${currentTheme}`);
    if (!res.ok) throw new Error('Theme not found');
    const themeHTML = await res.text();
    const themedHTML = buildThemedHTML(themeHTML, markdown);

    // Write into iframe
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    doc.open();
    doc.write(themedHTML);
    doc.close();

    // Auto-resize iframe to content
    iframe.onload = () => {
      try {
        const h = iframe.contentDocument.documentElement.scrollHeight;
        iframe.style.height = Math.max(h, 800) + 'px';
      } catch(e) {}
    };
    setTimeout(() => {
      try {
        const h = iframe.contentDocument.documentElement.scrollHeight;
        iframe.style.height = Math.max(h, 800) + 'px';
      } catch(e) {}
    }, 500);

  } catch(err) {
    console.error('Theme injection error:', err);
    // Fallback: render plain markdown in the preview div
    const preview = document.getElementById('resume-preview');
    preview.innerHTML = marked.parse(markdown);
    preview.classList.remove('hidden');
    const wrapper = document.getElementById('resume-preview-wrapper');
    if (wrapper) wrapper.style.display = 'none';
  }
}

function renderResume(markdown) {
  currentMarkdown = markdown;
  document.getElementById('resume-raw-code').textContent = markdown;

  show('output-content');
  showPreview();
  document.getElementById('output-controls').style.display = 'flex';

  injectIntoTheme(markdown);

  document.getElementById('output-content').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ═══════════════════════════════════════════════════════════════════════════════
//  DYNAMIC PILL INJECTION
// ═══════════════════════════════════════════════════════════════════════════════
function injectJDPills() {
  for (const [cat, roles] of Object.entries(JD_CATEGORIES)) {
    const container = document.getElementById(`jd-pills-${cat}`);
    if (!container) continue;
    
    roles.forEach(role => {
      const pill = document.createElement('span');
      pill.className = 'jd-pill';
      pill.dataset.role = role;
      pill.textContent = getShortRoleName(role);
      
      pill.onclick = () => {
        document.querySelectorAll('.jd-pill').forEach(p => p.classList.remove('active'));
        pill.classList.add('active');
        if (JD_TEMPLATES[role]) {
          document.getElementById('job-description').value = JD_TEMPLATES[role];
          const posField = document.getElementById('target-position');
          if (!posField.value.trim()) posField.value = role;
          showToast(`📋 Loaded template for ${role}`);
        }
      };
      container.appendChild(pill);
    });
  }
}

function getShortRoleName(role) {
  // Simple abbreviations for pills
  return role.replace('Full-Stack', 'FS').replace('Developer', 'Dev').replace('Engineer', 'Eng');
}

// ═══════════════════════════════════════════════════════════════════════════════
//  HISTORY LOGIC (with theme support)
// ═══════════════════════════════════════════════════════════════════════════════
async function fetchHistory() {
  try {
    const res = await fetch(`${API_BASE}/api/history`);
    if (!res.ok) throw new Error('Failed to fetch history');
    historyData = await res.json();
    renderHistoryList(historyData);
  } catch (err) {
    console.error('History Error:', err);
  }
}

function renderHistoryList(history) {
  const list = document.getElementById('history-list');
  if (!history || history.length === 0) {
    list.innerHTML = '<div class="history-empty">No recent resumes yet.</div>';
    return;
  }

  list.innerHTML = '';
  history.forEach(item => {
    const el = document.createElement('div');
    el.className = 'history-item';
    
    const date = new Date(item.timestamp).toLocaleDateString(undefined, { 
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' 
    });

    const typeLabel = item.type === 'refinement' ? 'REFINED' : 'GENERATED';
    const themeLabel = item.theme || 'modern';

    el.innerHTML = `
      <div class="history-role">${item.target_position}</div>
      <div class="history-meta">
        <span class="history-type" style="background:var(--bg-overlay); color:var(--accent-light)">${typeLabel}</span>
        <span class="history-theme-tag">${themeLabel}</span>
        <span>${item.target_city || ''}</span>
        <span>•</span>
        <span>${date}</span>
      </div>
    `;
    el.onclick = () => loadHistoryItem(item);
    list.appendChild(el);
  });
}

function loadHistoryItem(item) {
  if (item.theme) {
    currentTheme = item.theme;
    updateThemeUI(currentTheme);
  }
  currentMarkdown = item.resume_markdown;
  renderResume(currentMarkdown);
  if (item.tokens_used) {
    document.getElementById('token-count').textContent = item.tokens_used.toLocaleString();
    document.getElementById('token-info').classList.remove('hidden');
  }
  showToast(`📜 Loaded: ${item.target_position} (${currentTheme})`);
}

function updateThemeUI(themeId) {
  const btn = document.querySelector(`.theme-btn[data-theme="${themeId}"]`);
  if (btn) {
    document.querySelectorAll('.theme-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const label = btn.dataset.label || btn.querySelector('span').textContent;
    document.getElementById('active-theme-name').textContent = label;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
//  FORM SUBMIT
// ═══════════════════════════════════════════════════════════════════════════════
document.getElementById('resume-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const position = document.getElementById('target-position').value.trim();
  const city     = document.getElementById('target-city').value.trim();
  
  // Prioritize uploaded PDF text, fall back to master profile
  const master   = uploadedResumeText || serializeMasterProfile(MASTER_PROFILE);
  const jd       = document.getElementById('job-description').value.trim();

  if (!position) { highlightError('target-position'); showToast('❌ Please enter a target position'); return; }
  if (!city)     { highlightError('target-city');     showToast('❌ Please enter a target city');     return; }

  const btn = document.getElementById('generate-btn');
  btn.disabled = true;
  btn.classList.add('loading');
  btn.querySelector('.btn-text').textContent = 'Generating...';
  btn.querySelector('.btn-arrow').textContent = '';

  hide('idle-state');
  hide('output-content');
  show('loading-state');
  resetLoadingSteps();
  const stepIv = animateLoadingSteps(position);

  try {
    const res = await fetch(`${API_BASE}/api/generate-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ master_data: master, target_position: position, target_city: city, job_description: jd, theme: currentTheme, user_email: localStorage.getItem('user_email') || '' })
    });

    const data = await res.json();
    clearInterval(stepIv);
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

    currentMarkdown = data.resume_markdown;
    renderResume(currentMarkdown);
    
    // Refresh history
    fetchHistory();

    if (data.tokens_used > 0) {
      document.getElementById('token-count').textContent = data.tokens_used.toLocaleString();
      document.getElementById('token-info').classList.remove('hidden');
    }
    showToast('✅ Resume generated successfully!');

  } catch (err) {
    clearInterval(stepIv);
    renderError(err.message);
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.querySelector('.btn-text').textContent = 'Generate Chameleon Resume';
    btn.querySelector('.btn-arrow').textContent = '→';
    hide('loading-state');
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
//  REFINE RESUME
// ═══════════════════════════════════════════════════════════════════════════════
async function refineResume() {
  const instr = document.getElementById('refine-instructions').value.trim();
  if (!instr) { showToast('❌ Please enter refinement instructions'); return; }

  const btn = document.getElementById('refine-btn');
  btn.disabled = true;
  btn.classList.add('loading');
  btn.textContent = 'Refining...';

  try {
    const res = await fetch(`${API_BASE}/api/refine-resume`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        current_resume: currentMarkdown,
        instructions: instr,
        target_position: document.getElementById('target-position').value || 'Resume Update',
        target_city: document.getElementById('target-city').value || '',
        theme: currentTheme,
        user_email: localStorage.getItem('user_email') || ''
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

    currentMarkdown = data.resume_markdown;
    renderResume(currentMarkdown);
    document.getElementById('refine-instructions').value = '';
    
    // Refresh history
    fetchHistory();

    if (data.tokens_used > 0) {
      document.getElementById('token-count').textContent = data.tokens_used.toLocaleString();
      document.getElementById('token-info').classList.remove('hidden');
    }
    showToast('✨ Resume refined successfully!');

  } catch (err) {
    showToast(`❌ Refinement failed: ${err.message}`);
  } finally {
    btn.disabled = false;
    btn.classList.remove('loading');
    btn.textContent = 'Refine with AI';
  }
}

function highlightError(fieldId) {
  const el = document.getElementById(fieldId);
  el.style.borderColor = '#ef4444';
  el.focus();
  el.addEventListener('input', () => el.style.borderColor = '', { once: true });
}

// ═══════════════════════════════════════════════════════════════════════════════
//  ERROR RENDERER
// ═══════════════════════════════════════════════════════════════════════════════

function renderError(msg) {
  document.getElementById('resume-preview').innerHTML = `
    <div style="text-align:center; padding: 3rem; color:#ef4444;">
      <div style="font-size:3rem; margin-bottom:1rem;">⚠️</div>
      <h3 style="color:#ef4444; margin-bottom:0.5rem;">Generation Failed</h3>
      <p style="color:#6b7280; font-size:0.85rem; font-family:monospace; word-break:break-all;">${escapeHtml(msg)}</p>
      <button onclick="resetOutput()" style="margin-top:1.5rem; padding:8px 20px; background:#ef4444; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:600;">Try Again</button>
    </div>`;
  show('output-content');
  document.getElementById('output-controls').style.display = 'none';
}

function escapeHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ═══════════════════════════════════════════════════════════════════════════════
//  VIEW TOGGLE
// ═══════════════════════════════════════════════════════════════════════════════
function showPreview() {
  const wrapper = document.getElementById('resume-preview-wrapper');
  if (wrapper) wrapper.style.display = 'block';
  document.getElementById('resume-raw').classList.add('hidden');
  document.getElementById('resume-preview').classList.add('hidden');
  document.getElementById('preview-btn').classList.add('active');
  document.getElementById('raw-btn').classList.remove('active');
}
function showRaw() {
  const wrapper = document.getElementById('resume-preview-wrapper');
  if (wrapper) wrapper.style.display = 'none';
  document.getElementById('resume-raw').classList.remove('hidden');
  document.getElementById('resume-preview').classList.add('hidden');
  document.getElementById('raw-btn').classList.add('active');
  document.getElementById('preview-btn').classList.remove('active');
}

// ═══════════════════════════════════════════════════════════════════════════════
//  COPY / PRINT
// ═══════════════════════════════════════════════════════════════════════════════
function copyMarkdown() {
  if (!currentMarkdown) return;
  navigator.clipboard.writeText(currentMarkdown).then(() => showToast('📋 Markdown copied!'));
}
function copyPlainText() {
  navigator.clipboard.writeText(document.getElementById('resume-preview').innerText).then(() => showToast('📝 Plain text copied!'));
}
function printResume() {
  document.getElementById('print-area').innerHTML = document.getElementById('resume-preview').innerHTML;
  window.print();
}

// ═══════════════════════════════════════════════════════════════════════════════
//  TOAST
// ═══════════════════════════════════════════════════════════════════════════════
function showToast(msg) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position:fixed; bottom:2rem; right:2rem; z-index:9999;
    background:linear-gradient(135deg,#1e293b,#2d3748);
    border:1px solid rgba(79,156,255,0.3); color:#f0f6ff;
    padding:12px 20px; border-radius:12px; font-size:0.85rem;
    font-weight:600; font-family:Inter,sans-serif;
    box-shadow:0 8px 32px rgba(0,0,0,0.5);
    transform:translateY(20px); opacity:0;
    transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    max-width:320px; word-break:break-word;
  `;
  toast.textContent = msg;
  document.body.appendChild(toast);
  requestAnimationFrame(() => { toast.style.transform='translateY(0)'; toast.style.opacity='1'; });
  setTimeout(() => {
    toast.style.transform='translateY(20px)'; toast.style.opacity='0';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

// Initial calls
fetchHistory();
injectJDPills();



// ═══════════════════════════════════════════════════════════════════════════════
//  USER MANAGEMENT
// ═══════════════════════════════════════════════════════════════════════════════
function changeUser() {
  if (confirm('Are you sure you want to switch to a different user? Your current session data will be cleared.')) {
    localStorage.removeItem('user_email');
    localStorage.removeItem('user_phone');
    window.location.href = '/';
  }
}

/**
 * Download the current resume as a PDF using html2pdf.js
 * Captures the themed iframe content for accurate PDF output.
 */
function downloadPDF() {
  if (!currentMarkdown) {
    showToast('❌ No resume to download.');
    return;
  }

  const iframe = document.getElementById('resume-iframe');
  let element;

  try {
    // Use iframe body content if available
    const iDoc = iframe && (iframe.contentDocument || iframe.contentWindow.document);
    if (iDoc && iDoc.body && iDoc.body.innerHTML.trim()) {
      element = iDoc.body.cloneNode(true);
      // Inject theme styles into the clone for pdf rendering
      const styleEl = document.createElement('style');
      Array.from(iDoc.head.querySelectorAll('style')).forEach(s => {
        styleEl.textContent += s.textContent;
      });
      const wrapper = document.createElement('div');
      wrapper.appendChild(styleEl);
      wrapper.appendChild(element);
      element = wrapper;
    } else {
      throw new Error('iframe empty');
    }
  } catch(e) {
    // Fallback: use plain markdown preview div
    element = document.getElementById('resume-preview').cloneNode(true);
  }

  element.style.boxShadow = 'none';
  element.style.margin = '0';
  element.style.width = '100%';

  const candidateName = (currentMarkdown.match(/^# (.+)$/m)||[])[1] || 'Candidate';
  const opt = {
    margin: [0.3, 0.3],
    filename: `${candidateName.replace(/\s+/g,'_')}_Resume.pdf`,
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2, useCORS: true, letterRendering: true },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  };

  showToast('⏳ Generating PDF...');
  html2pdf().set(opt).from(element).save()
    .then(() => showToast('✅ PDF downloaded!'))
    .catch(err => { console.error(err); showToast('❌ PDF generation failed.'); });
}

/**
 * Update a specific design setting using CSS variables
 */
function updateDesignSetting(prop, val) {
  const preview = document.getElementById('resume-preview');
  if (!preview) return;

  // Update Label
  const labelId = `val-${prop}`;
  const label = document.getElementById(labelId);
  if (label) label.textContent = val;

  // Apply to CSS Variable
  const variableMap = {
    'font-size': '--resume-font-size',
    'spacing': '--resume-spacing'
  };

  const variable = variableMap[prop];
  if (variable) {
    const unit = prop === 'font-size' ? 'pt' : '';
    preview.style.setProperty(variable, `${val}${unit}`);
  }
}

/**
 * Set the primary accent color for the resume
 */
function setAccent(el) {
  const color = el.dataset.color;
  const preview = document.getElementById('resume-preview');
  if (!preview) return;

  // Update UI
  document.querySelectorAll('.color-dot').forEach(d => d.classList.remove('active'));
  el.classList.add('active');

  // Apply CSS Variable
  preview.style.setProperty('--resume-primary', color);
  
  showToast(`🎨 Color updated: ${color}`);
}

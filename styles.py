
PREMIUM_CSS = """
<style>
/* ── Premium Styles ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono&display=swap');

/* Main Overrides */
.stApp {
    background: #070b14;
    color: #f0f6ff;
    font-family: 'Inter', sans-serif;
}

/* Glass Panels */
div[data-testid="stVerticalBlock"] > div:has(div.stExpander), .stMarkdown div[data-testid="stBlock"] {
    background: rgba(17, 24, 39, 0.7) !important;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(99, 173, 255, 0.2);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

/* Card Glow */
.stMarkdown div[data-testid="stBlock"]:hover {
    border-color: rgba(168, 85, 247, 0.4);
    box-shadow: 0 8px 40px rgba(168, 85, 247, 0.15);
    transition: all 0.3s ease;
}

/* Custom Buttons */
button[kind="primary"] {
    background: linear-gradient(135deg, #4f9cff 0%, #a855f7 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

/* Gecko Pulse */
@keyframes chameleon-pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 12px rgba(79,156,255,0.5)); }
    50%       { transform: scale(1.05); filter: drop-shadow(0 0 20px rgba(168,85,247,0.7)); }
}
.gecko-header {
    font-size: 3rem;
    animation: chameleon-pulse 3s ease-in-out infinite;
    text-align: center;
}

/* Hide Streamlit Header/Footer */
header {visibility: hidden;}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* Custom Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}
.stTabs [data-baseweb=\"tab\"] {
    background: rgba(255,255,255,0.05);
    border-radius: 10px 10px 0 0;
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    background: rgba(79, 156, 255, 0.15) !important;
    color: #4f9cff !important;
    border-bottom: 2px solid #4f9cff !important;
}
</style>
"""

def inject_styles():
    import streamlit as st
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# THEME-SPECIFIC CSS GENERATORS FOR RESUME TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

def get_theme_css(theme_name):
    """Generate CSS for a specific resume theme."""
    themes = {
        "modern": """
            .resume-container {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                background: #ffffff;
                color: #1a1a2e;
                line-height: 1.6;
            }
            .resume-header {
                background: linear-gradient(135deg, #4f9cff 0%, #a855f7 100%);
                color: white;
                padding: 30px;
                border-radius: 12px;
                margin-bottom: 25px;
            }
            .resume-header h1 {
                margin: 0 0 10px 0;
                font-size: 2.2em;
                font-weight: 700;
            }
            .resume-header .contact-info {
                opacity: 0.9;
                font-size: 0.95em;
            }
            .section {
                margin-bottom: 25px;
                padding: 20px;
                background: #f8fafc;
                border-radius: 8px;
                border-left: 4px solid #4f9cff;
            }
            .section h2 {
                color: #1e3a5f;
                font-size: 1.3em;
                margin: 0 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #e2e8f0;
            }
            .job-title {
                font-weight: 600;
                color: #2d3748;
                font-size: 1.1em;
            }
            .company {
                color: #4f9cff;
                font-weight: 500;
            }
            .date {
                color: #718096;
                font-size: 0.9em;
                font-style: italic;
            }
            ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 6px 0;
            }
        """,
        "classic": """
            .resume-container {
                font-family: 'Georgia', 'Times New Roman', serif;
                max-width: 800px;
                margin: 0 auto;
                background: #ffffff;
                color: #2c3e50;
                line-height: 1.7;
            }
            .resume-header {
                text-align: center;
                padding-bottom: 20px;
                margin-bottom: 30px;
                border-bottom: 3px double #2c3e50;
            }
            .resume-header h1 {
                margin: 0;
                font-size: 2.5em;
                font-weight: normal;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            .resume-header .contact-info {
                margin-top: 10px;
                font-size: 0.95em;
                color: #555;
            }
            .section {
                margin-bottom: 25px;
            }
            .section h2 {
                color: #2c3e50;
                font-size: 1.2em;
                margin: 0 0 15px 0;
                padding-bottom: 5px;
                border-bottom: 1px solid #2c3e50;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .job-title {
                font-weight: bold;
                font-size: 1.05em;
            }
            .company {
                font-style: italic;
            }
            .date {
                float: right;
                font-style: italic;
                color: #666;
            }
            ul {
                margin: 8px 0;
                padding-left: 25px;
            }
        """,
        "minimal": """
            .resume-container {
                font-family: 'Helvetica Neue', Arial, sans-serif;
                max-width: 700px;
                margin: 0 auto;
                background: #ffffff;
                color: #1a1a1a;
                line-height: 1.6;
                padding: 40px;
            }
            .resume-header {
                margin-bottom: 40px;
            }
            .resume-header h1 {
                margin: 0;
                font-size: 2em;
                font-weight: 300;
                letter-spacing: -1px;
            }
            .resume-header .contact-info {
                margin-top: 8px;
                font-size: 0.9em;
                color: #666;
            }
            .section {
                margin-bottom: 35px;
            }
            .section h2 {
                font-size: 0.75em;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #999;
                margin: 0 0 20px 0;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }
            .job-title {
                font-weight: 500;
            }
            .company {
                color: #666;
            }
            .date {
                color: #999;
                font-size: 0.85em;
            }
            ul {
                margin: 12px 0;
                padding-left: 20px;
            }
            li {
                margin: 8px 0;
            }
        """,
        "professional": """
            .resume-container {
                font-family: 'Segoe UI', Tahoma, Geneva, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                background: #ffffff;
                color: #1e3a5f;
                line-height: 1.6;
            }
            .resume-header {
                background: #1e3a5f;
                color: white;
                padding: 25px 30px;
                margin: -40px -40px 30px -40px;
            }
            .resume-header h1 {
                margin: 0 0 8px 0;
                font-size: 2em;
                font-weight: 600;
            }
            .resume-header .contact-info {
                font-size: 0.9em;
                opacity: 0.9;
            }
            .section {
                margin-bottom: 25px;
            }
            .section h2 {
                color: #1e3a5f;
                font-size: 1.1em;
                margin: 0 0 15px 0;
                padding: 8px 12px;
                background: #f0f4f8;
                border-left: 4px solid #2c5282;
                font-weight: 600;
            }
            .job-title {
                font-weight: 600;
                color: #1e3a5f;
            }
            .company {
                font-weight: 500;
                color: #2c5282;
            }
            .date {
                color: #4a5568;
                font-size: 0.9em;
            }
            ul {
                margin: 10px 0;
                padding-left: 20px;
            }
            li {
                margin: 6px 0;
            }
        """,
        "creative": """
            .resume-container {
                font-family: 'Poppins', 'Segoe UI', sans-serif;
                max-width: 800px;
                margin: 0 auto;
                background: linear-gradient(135deg, #fff5f5 0%, #f0fff4 100%);
                color: #2d3748;
                line-height: 1.6;
                padding: 30px;
            }
            .resume-header {
                text-align: center;
                padding: 30px;
                background: white;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(255, 107, 107, 0.15);
                margin-bottom: 30px;
            }
            .resume-header h1 {
                margin: 0 0 10px 0;
                font-size: 2.5em;
                background: linear-gradient(135deg, #ff6b6b 0%, #4ecdc4 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 700;
            }
            .resume-header .contact-info {
                color: #718096;
                font-size: 0.95em;
            }
            .section {
                margin-bottom: 25px;
                background: white;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            }
            .section h2 {
                color: #ff6b6b;
                font-size: 1.3em;
                margin: 0 0 15px 0;
                padding-bottom: 10px;
                border-bottom: 3px solid #4ecdc4;
                display: inline-block;
            }
            .job-title {
                font-weight: 600;
                color: #2d3748;
            }
            .company {
                color: #ff6b6b;
                font-weight: 500;
            }
            .date {
                background: #fff5f5;
                color: #ff6b6b;
                padding: 2px 10px;
                border-radius: 20px;
                font-size: 0.85em;
            }
            ul {
                margin: 12px 0;
                padding-left: 20px;
            }
            li {
                margin: 8px 0;
                position: relative;
            }
            li::marker {
                color: #4ecdc4;
            }
        """
    }
    return themes.get(theme_name, themes["modern"])


def get_industry_badge_css():
    """CSS for industry badges in template gallery."""
    return """
    <style>
    .industry-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .theme-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .theme-card:hover {
        border-color: rgba(79, 156, 255, 0.4);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    .template-preview-box {
        background: #f8fafc;
        border-radius: 8px;
        padding: 15px;
        max-height: 200px;
        overflow: hidden;
        font-size: 0.85rem;
        color: #475569;
        border: 1px solid #e2e8f0;
    }
    .template-filter-btn {
        background: rgba(79, 156, 255, 0.1);
        border: 1px solid rgba(79, 156, 255, 0.3);
        color: #4f9cff;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .template-filter-btn:hover, .template-filter-btn.active {
        background: rgba(79, 156, 255, 0.2);
        border-color: #4f9cff;
    }
    </style>
    """

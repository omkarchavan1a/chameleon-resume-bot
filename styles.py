
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

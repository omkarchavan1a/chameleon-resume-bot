import streamlit as st
import json
import os

# ─── Premium UI Design System ────────────────────────────────────────────────
# Load Premium CSS from external file to prevent IDE parse errors
try:
    with open("premium_styles.css", "r") as f:
        PREMIUM_CSS = f"<style>{f.read()}</style>"
except Exception:
    # Fallback to minimal style if file missing
    PREMIUM_CSS = "<style>.stApp { background: #070b14; color: #f0f6ff; }</style>"

def inject_styles():
    """Inject the premium design system into the Streamlit app."""
    st.markdown(PREMIUM_CSS, unsafe_allow_html=True)

# ─── Resume Theme CSS ────────────────────────────────────────────────────────
# Load Resume Themes from external JSON to stop IDE from parsing CSS as Python
try:
    with open("resume_themes.json", "r") as f:
        RESUME_THEME_CSS = json.load(f)
except Exception:
    # Minimal fallbacks if JSON is missing
    RESUME_THEME_CSS = {
        "modern": ".resume-container { font-family: 'Inter', sans-serif; padding: 40px; }",
        "minimal": ".resume-container { font-family: 'Helvetica Neue', sans-serif; padding: 30px; }"
    }

def get_theme_css(theme_name):
    """Return the CSS for a specific resume theme."""
    theme_key = str(theme_name).lower()
    return f"<style>{RESUME_THEME_CSS.get(theme_key, RESUME_THEME_CSS.get('modern', ''))}</style>"

# ─── Component Styles ────────────────────────────────────────────────────────
def get_industry_badge_css(industry_name=None):
    """Return CSS for industry-specific badges and gallery components."""
    # Move this to a file if it grows larger
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
        background: rgba(79, 156, 255, 0.1);
        border: 1px solid rgba(79, 156, 255, 0.3);
        color: #4f9cff;
    }
    .theme-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
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
    </style>
    """

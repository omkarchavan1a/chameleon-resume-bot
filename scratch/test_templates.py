import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from resume_engine import ResumeEngine
from config import HTML_TEMPLATES

def test_all_templates():
    engine = ResumeEngine()
    sample_md = """# John Doe
**Software Engineer** | New York | john@example.com

## Summary
Experienced engineer.

## Skills
Python, React, Node.js

## Experience
### Senior Engineer | TechCo
*2020 - Present*
- Built stuff.
"""
    data = engine.parse_markdown(sample_md)
    
    for name, path in HTML_TEMPLATES.items():
        print(f"Testing template: {name} ({path})")
        try:
            html = engine.render_html(path, data)
            print(f"  Success: {len(html)} bytes")
        except Exception as e:
            print(f"  FAILED: {e}")

if __name__ == "__main__":
    test_all_templates()

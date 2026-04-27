import os
import re
import io
import json
import copy
from bs4 import BeautifulSoup
import markdown

class ResumeEngine:
    def __init__(self):
        pass

    @staticmethod
    def parse_markdown(md_content):
        """Parse resume markdown into structured data."""
        data = {
            "name": "Anonymous",
            "title": "",
            "contact": {"email": "", "phone": "", "linkedin": "", "github": ""},
            "summary": "",
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "awards": []
        }
        
        lines = md_content.split('\n')
        section_aliases = {
            "summary": ["summary", "professional summary", "profile", "objective", "about"],
            "skills": ["skills", "technical skills", "technical stack", "core competencies", "competencies", "tech stack"],
            "experience": ["experience", "professional experience", "work experience", "employment", "work history"],
            "education": ["education", "academic background", "academics"],
            "projects": ["projects", "key projects", "selected projects", "project"],
            "awards": ["awards", "certifications", "licenses", "achievements", "honors", "quantifiable impact"]
        }
        
        # Extract Name (usually first # header)
        for i, line in enumerate(lines):
            if line.startswith('# '):
                data["name"] = line[2:].strip()
                # Next line often contains title/contact
                if i + 1 < len(lines):
                    info_line = lines[i+1].strip()
                    if '|' in info_line:
                        parts = [p.strip() for p in info_line.split('|')]
                        data["title"] = parts[0]
                        # Try to find email/phone in other parts
                        for p in parts[1:]:
                            if '@' in p: data["contact"]["email"] = p
                            elif re.search(r'\d{5}', p): data["contact"]["phone"] = p
                            elif 'linkedin' in p.lower(): data["contact"]["linkedin"] = p
                            elif 'github' in p.lower(): data["contact"]["github"] = p
                break
        
        # Extract title + contact from intro lines (before first ## section)
        intro_lines = []
        for line in lines[1:]:
            if line.startswith('## '):
                break
            if line.strip():
                intro_lines.append(line.strip())
        
        if intro_lines and not data["title"]:
            first_intro = intro_lines[0].strip('* ').strip()
            if '@' not in first_intro and not re.search(r'\+?\d[\d\s\-()]{7,}', first_intro):
                data["title"] = first_intro
        
        contact_blob = " | ".join(intro_lines)
        if not data["contact"]["email"]:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_blob)
            if email_match:
                data["contact"]["email"] = email_match.group(0)
        if not data["contact"]["phone"]:
            phone_match = re.search(r'(\+?\d[\d\s\-()]{7,}\d)', contact_blob)
            if phone_match:
                data["contact"]["phone"] = phone_match.group(1).strip()
        if not data["contact"]["linkedin"]:
            linkedin_match = re.search(r'(https?://[^\s|]*linkedin[^\s|]*|linkedin[^\s|]*)', contact_blob, re.IGNORECASE)
            if linkedin_match:
                data["contact"]["linkedin"] = linkedin_match.group(1).strip()
        if not data["contact"]["github"]:
            github_match = re.search(r'(https?://[^\s|]*github[^\s|]*|github[^\s|]*)', contact_blob, re.IGNORECASE)
            if github_match:
                data["contact"]["github"] = github_match.group(1).strip()

        # Split by sections
        sections = re.split(r'\n## ', md_content)
        for section in sections:
            lines = section.split('\n')
            header = lines[0].strip().lower()
            content = '\n'.join(lines[1:]).strip()
            normalized_header = re.sub(r'[^a-z\s]', '', header).strip()
            section_type = None
            for key, aliases in section_aliases.items():
                if any(alias in normalized_header for alias in aliases):
                    section_type = key
                    break
            
            if section_type == "summary":
                data["summary"] = content
            elif section_type == "skills":
                # Extract bullet points or comma separated
                if ',' in content and '\n' not in content:
                    data["skills"] = [s.strip() for s in content.split(',') if s.strip()]
                else:
                    parsed_skills = []
                    for l in content.split('\n'):
                        line = l.strip()
                        if not line:
                            continue
                        line = re.sub(r'^[-*]\s*', '', line)
                        line = re.sub(r'^\*\*[^:]+:\*\*\s*', '', line).strip()
                        parts = [p.strip() for p in line.split(',') if p.strip()]
                        if parts and len(parts) > 1:
                            parsed_skills.extend(parts)
                        elif line:
                            parsed_skills.append(line)
                    data["skills"] = parsed_skills
            elif section_type == "experience":
                exp_entries = re.split(r'\n### |\n\*\*', '\n' + content)
                for entry in exp_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    raw_header = entry_lines[0].strip('* ').strip()
                    role = raw_header
                    company = ""
                    if '|' in raw_header:
                        header_parts = [p.strip() for p in raw_header.split('|')]
                        role = header_parts[0] if header_parts else raw_header
                        company = header_parts[1] if len(header_parts) > 1 else ""
                    elif ' at ' in raw_header.lower():
                        at_split = re.split(r'\bat\b', raw_header, maxsplit=1, flags=re.IGNORECASE)
                        role = at_split[0].strip() if at_split else raw_header
                        company = at_split[1].strip() if len(at_split) > 1 else ""
                    elif ' - ' in raw_header:
                        dash_parts = [p.strip() for p in raw_header.split(' - ', 1)]
                        role = dash_parts[0]
                        company = dash_parts[1] if len(dash_parts) > 1 else ""
                    
                    date = ""
                    highlights = []
                    for l in entry_lines[1:]:
                        l = l.strip()
                        if not l: continue
                        if re.search(r'\d{4}', l) and not l.startswith('-') and not l.startswith('*'):
                            date = l
                        elif l.startswith('-') or l.startswith('*'):
                            highlights.append(re.sub(r'^[-*]\s*', '', l))
                    
                    data["experience"].append({
                        "role": role,
                        "company": company,
                        "date": date,
                        "highlights": highlights
                    })
            elif section_type == "education":
                edu_entries = re.split(r'\n### |\n\*\*', '\n' + content)
                for entry in edu_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    data["education"].append({
                        "degree": entry_lines[0].strip('* ').strip(),
                        "details": '\n'.join(entry_lines[1:]).strip()
                    })
            elif section_type == "projects":
                proj_entries = re.split(r'\n### |\n\*\*', '\n' + content)
                for entry in proj_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    title = entry_lines[0].strip('* ').strip()
                    description = ""
                    highlights = []
                    for l in entry_lines[1:]:
                        l = l.strip()
                        if not l: continue
                        if l.startswith('-') or l.startswith('*'):
                            highlights.append(re.sub(r'^[-*]\s*', '', l))
                        else:
                            description += " " + l
                    data["projects"].append({
                        "title": title,
                        "description": description.strip(),
                        "highlights": highlights
                    })
            elif section_type == "awards":
                # Parse achievements/quantifiable impact as list of strings
                for line in content.split('\n'):
                    line = line.strip()
                    if not line: continue
                    if line.startswith('-') or line.startswith('*'):
                        data["awards"].append(re.sub(r'^[-*]\s*', '', line))
                    elif line and not line.startswith('#'):
                        data["awards"].append(line)
                    
        return data

    # ─────────────────────────────────────────────────────────────────────────
    # HTML rendering helpers
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _cls_match(tag, *keywords):
        """Return True if any of the tag's exact classes match any of the keywords."""
        if not hasattr(tag, 'get'):
            return False
        classes = tag.get('class', [])
        if isinstance(classes, str):
            classes = [classes]
        classes = [c.lower() for c in classes]
        return any(kw.lower() in classes for kw in keywords)

    @staticmethod
    def _find_by_cls(soup, *keywords):
        """Find the first element whose exact class contains any keyword."""
        return soup.find(lambda t: ResumeEngine._cls_match(t, *keywords))

    @staticmethod
    def _set_text(elem, text):
        """Clear an element and set its text content."""
        if elem is not None:
            elem.clear()
            elem.string = str(text)

    @staticmethod
    def _is_header_matching(tag, *keywords):
        """Returns True if the tag is a header (or simple div) containing one of the keywords."""
        if tag.name not in ['h1', 'h2', 'h3', 'div', 'span']:
            return False
        if tag.name == 'div' and tag.find(['div', 'section', 'ul']):
            return False
        text = tag.get_text(strip=True).lower()
        return any(kw in text for kw in keywords)

    @staticmethod
    def _hide_section_if_empty(soup, section, data_list):
        """Hide or remove a section if there's no data."""
        if not data_list or len(data_list) == 0:
            if section:
                section.decompose()
            return True
        return False

    @staticmethod
    def render_html(template_path, data):
        """
        Inject structured resume data into an HTML template.
        """
        if not os.path.exists(template_path):
            return f"<p>Template not found: {template_path}</p>"

        with open(template_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        soup = BeautifulSoup(raw_html, 'html.parser')
        fe = ResumeEngine  # shorthand

        # ── 1. Name ──────────────────────────────────────────────────────────
        name_elem = fe._find_by_cls(soup, 'name', 'candidate-name', 'full-name', 'hero-name', 'author-name')
        fe._set_text(name_elem, data.get("name", ""))

        # ── 2. Title / Role ──────────────────────────────────────────────────
        title_elem = fe._find_by_cls(soup, 'title', 'role', 'subtitle', 'tagline', 'hero-title', 'job-title', 'profession')
        fe._set_text(title_elem, data.get("title", ""))

        # ── 3. Contact ───────────────────────────────────────────────────────
        contact_container = soup.find(class_='contact')
        if contact_container:
            for link in contact_container.find_all('a'):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if 'mailto' in href or '@' in text:
                    if data["contact"]["email"]:
                        link.string = data["contact"]["email"]
                        link['href'] = f"mailto:{data['contact']['email']}"
                elif 'linkedin' in href.lower() or 'linkedin' in text.lower():
                    if data["contact"]["linkedin"]:
                        link['href'] = data["contact"]["linkedin"]
                elif 'github' in href.lower() or 'github' in text.lower():
                    if data["contact"]["github"]:
                        link['href'] = data["contact"]["github"]

            for item in contact_container.find_all(['span', 'div', 'p']):
                text = item.get_text(strip=True)
                if re.search(r'\+?\d[\d\s\-()]{7,}', text) and data["contact"]["phone"]:
                    if not item.find(['span', 'div', 'a']):
                        item.clear()
                        item.string = data["contact"]["phone"]
                        break

        # ── 4. Summary ───────────────────────────────────────────────────────
        summary_text = data.get("summary", "")
        summary_elem = fe._find_by_cls(soup, 'summary', 'about-text', 'profile-text', 'bio', 'objective', 'summary-text')
        if not summary_elem:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'summary', 'about', 'profile', 'objective'))
            if hdr:
                summary_section = hdr.find_parent(['section', 'article']) or hdr.parent
                if not summary_text:
                    fe._hide_section_if_empty(soup, summary_section, [])
                else:
                    candidate = hdr.find_next(['p', 'div'])
                    if candidate and not candidate.find(['h2', 'h3']):
                        summary_elem = candidate
        if summary_text and summary_elem:
            fe._set_text(summary_elem, summary_text)

        # ── 5. Experience ─────────────────────────────────────────────────────
        exp_data = data.get("experience", [])
        exp_section = fe._find_by_cls(soup, 'experience-list', 'experience-container', 'work-experience', 'work-history', 'jobs-list')
        if not exp_section:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'experience', 'work history', 'employment', 'career'))
            if hdr:
                exp_section = hdr.find_parent(['section', 'article']) or hdr.parent
        if fe._hide_section_if_empty(soup, exp_section, exp_data):
            pass  # Section hidden
        elif exp_data and exp_section:
            entry_tmpl = exp_section.find(lambda t: fe._cls_match(t, 'entry', 'experience-item', 'job-item', 'work-item', 'position-block'))
            if entry_tmpl:
                tmpl_clone = copy.copy(entry_tmpl)
                entry_classes = entry_tmpl.get('class', [])
                for e in exp_section.find_all(class_=entry_classes):
                    e.decompose()
                for item in exp_data:
                    new_e = copy.copy(tmpl_clone)
                    if new_e is None: continue
                    role_el = new_e.find(lambda t: fe._cls_match(t, 'position', 'role', 'job-title', 'work-title'))
                    fe._set_text(role_el, item.get("role", ""))
                    co_el = new_e.find(lambda t: fe._cls_match(t, 'organization', 'company', 'employer', 'workplace'))
                    fe._set_text(co_el, item.get("company", ""))
                    date_el = new_e.find(lambda t: fe._cls_match(t, 'date', 'period', 'duration', 'tenure'))
                    fe._set_text(date_el, item.get("date", ""))
                    ul = new_e.find('ul')
                    if ul:
                        ul.clear()
                        for hl in item.get("highlights", []):
                            li = soup.new_tag('li')
                            li.string = hl
                            ul.append(li)
                    else:
                        desc_el = new_e.find(lambda t: fe._cls_match(t, 'description', 'entry-description', 'details'))
                        fe._set_text(desc_el, ' '.join(item.get("highlights", [])))
                    exp_section.append(new_e)

        # ── 5b. Projects ──────────────────────────────────────────────────────
        proj_data = data.get("projects", [])
        proj_section = fe._find_by_cls(soup, 'projects-list', 'projects-container')
        if not proj_section:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'project', 'key projects'))
            if hdr:
                proj_section = hdr.find_parent(['section', 'article']) or hdr.parent
        if fe._hide_section_if_empty(soup, proj_section, proj_data):
            pass  # Section hidden
        elif proj_data and proj_section:
            entry_tmpl = proj_section.find(lambda t: fe._cls_match(t, 'entry', 'project-item', 'project-block'))
            if entry_tmpl:
                tmpl_clone = copy.copy(entry_tmpl)
                entry_classes = entry_tmpl.get('class', [])
                for e in proj_section.find_all(class_=entry_classes):
                    e.decompose()
                for item in proj_data:
                    new_e = copy.copy(tmpl_clone)
                    if new_e is None: continue
                    title_el = new_e.find(lambda t: fe._cls_match(t, 'position', 'project-title', 'project-name'))
                    fe._set_text(title_el, item.get("title", ""))
                    desc_el = new_e.find(lambda t: fe._cls_match(t, 'organization', 'project-desc'))
                    fe._set_text(desc_el, item.get("description", ""))
                    ul = new_e.find('ul')
                    if ul:
                        ul.clear()
                        for hl in item.get("highlights", []):
                            li = soup.new_tag('li')
                            li.string = hl
                            ul.append(li)
                    proj_section.append(new_e)

        # ── 5c. Achievements ──────────────────────────────────────────────────
        awards_data = data.get("awards", [])
        awards_section = fe._find_by_cls(soup, 'achievements-list', 'awards-container')
        if not awards_section:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'achievement', 'achievements', 'awards'))
            if hdr:
                awards_section = hdr.find_parent(['section', 'article']) or hdr.parent
        if fe._hide_section_if_empty(soup, awards_section, awards_data):
            pass  # Section hidden
        elif awards_data and awards_section:
            ul = awards_section.find('ul')
            if ul:
                ul.clear()
                for award in awards_data:
                    li = soup.new_tag('li')
                    li.string = award
                    ul.append(li)
            else:
                desc_el = awards_section.find(lambda t: fe._cls_match(t, 'description', 'entry-description'))
                fe._set_text(desc_el, '\n'.join(awards_data))

        # ── 6. Education ──────────────────────────────────────────────────────
        edu_data = data.get("education", [])
        edu_section = fe._find_by_cls(soup, 'education-list', 'education-container', 'edu-list')
        if not edu_section:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'education'))
            if hdr:
                edu_section = hdr.find_parent(['section', 'article']) or hdr.parent
        if fe._hide_section_if_empty(soup, edu_section, edu_data):
            pass  # Section hidden
        elif edu_data and edu_section:
            entry_tmpl = edu_section.find(lambda t: fe._cls_match(t, 'entry', 'education-item', 'edu-item'))
            if entry_tmpl:
                tmpl_clone = copy.copy(entry_tmpl)
                for e in edu_section.find_all(class_=entry_tmpl.get('class', [])):
                    e.decompose()
                for item in edu_data:
                    new_e = copy.copy(tmpl_clone)
                    if new_e is None: continue
                    deg_el = new_e.find(lambda t: fe._cls_match(t, 'position', 'degree', 'qualification'))
                    fe._set_text(deg_el, item.get("degree", ""))
                    det_el = new_e.find(lambda t: fe._cls_match(t, 'organization', 'institution', 'school', 'details', 'edu-details'))
                    fe._set_text(det_el, item.get("details", ""))
                    edu_section.append(new_e)

        # ── 7. Skills ─────────────────────────────────────────────────────────
        skills_data = data.get("skills", [])
        skills_section = None
        skills_container = fe._find_by_cls(soup, 'skills-grid', 'skills-list', 'skills-container', 'skill-tags', 'skills-wrapper', 'tech-stack', 'pills', 'tags')
        if not skills_container:
            hdr = soup.find(lambda t: fe._is_header_matching(t, 'skill'))
            if hdr:
                skills_section = hdr.find_parent(['section', 'article']) or hdr.parent
                skills_container = hdr.find_next(['div', 'ul', 'p'])
        if fe._hide_section_if_empty(soup, skills_section or skills_container, skills_data):
            pass  # Section hidden
        elif skills_data and skills_container:
            item_tmpl = skills_container.find(lambda t: t.name in ['div', 'span', 'li'] and fe._cls_match(t, 'skill-tag', 'skill-item', 'skill-box', 'skill-badge', 'tag', 'skill-pill', 'pill', 'badge', 'skill-name'))
            if item_tmpl:
                tmpl_clone = copy.copy(item_tmpl)
                item_classes = item_tmpl.get('class', [])
                for e in skills_container.find_all(class_=item_classes):
                    e.decompose()
                for skill in skills_data:
                    new_i = copy.copy(tmpl_clone)
                    if new_i is None: continue
                    label_el = new_i.find(lambda t: fe._cls_match(t, 'skill-label', 'skill-title', 'label', 'skill-name'))
                    if label_el:
                        fe._set_text(label_el, skill)
                        for other in new_i.find_all(lambda t: fe._cls_match(t, 'skill-level', 'skill-fill', 'skill-bar', 'skill-value', 'value')):
                            other.decompose()
                    else:
                        fe._set_text(new_i, skill)
                    skills_container.append(new_i)
                    skills_container.append(soup.new_string(" "))
            else:
                skills_container.clear()
                for skill in skills_data:
                    span = soup.new_tag('span', attrs={'class': 'skill-tag'})
                    span.string = skill
                    skills_container.append(span)
                    skills_container.append(soup.new_string(" "))

        # ── 8. LLM Analysis / ATS Score ───────────────────────────────────────
        llm_data = data.get("llm_analysis")
        if llm_data:
            fe._inject_llm_analysis_section(soup, llm_data)

        # ── 9. Fallback ───────────────────────────────────────────────────────
        PLACEHOLDER_NAMES = {'sarah chen', 'john doe', 'your name', 'jane doe', 'alex johnson'}
        name_check = fe._find_by_cls(soup, 'name', 'candidate-name', 'full-name', 'hero-name')
        name_text = name_check.get_text(strip=True) if name_check else ""
        data_name = data.get("name", "")
        # Check if name was properly injected (not empty and not a placeholder)
        injected = (
            name_check is not None and
            name_text and
            name_text.lower() not in PLACEHOLDER_NAMES and
            name_text.lower() == data_name.lower()
        )
        if not injected and data_name and data_name != "Anonymous":
            md_html = markdown.markdown(ResumeEngine._data_to_markdown(data), extensions=['extra', 'nl2br'])
            main = soup.find(class_=lambda c: c and any(x in c for x in ['container', 'resume', 'page'])) or soup.body
            if main:
                main.clear()
                main.append(BeautifulSoup(md_html, 'html.parser'))

        return str(soup)

    @staticmethod
    def _data_to_markdown(data):
        lines = []
        if data.get("name"): lines.append(f"# {data['name']}")
        lines.append('')
        if data.get("summary"):
            lines.append("## Professional Summary")
            lines.append(data["summary"])
            lines.append('')
        if data.get("skills"):
            lines.append("## Skills")
            lines.append(', '.join(data["skills"]))
            lines.append('')
        return '\n'.join(lines)

    @staticmethod
    def _inject_llm_analysis_section(soup, llm_data):
        """Inject a new LLM analysis section at the end of the document."""
        candidate_name = llm_data.get("candidate_name", "Candidate") if llm_data else "Candidate"
        ats_score = llm_data.get("ats_score", 0) if llm_data else 0
        keyword_match = llm_data.get("keyword_match", 0) if llm_data else 0
        summary = llm_data.get("summary", "") if llm_data else ""
        strengths = llm_data.get("strengths", []) if llm_data else []
        improvements = llm_data.get("improvements", []) if llm_data else []
        missing_keywords = llm_data.get("missing_keywords", []) if llm_data else []

        # Create analysis section HTML
        analysis_html = f"""
        <section class="llm-analysis-section" style="margin-top: 40px; padding: 25px; background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); border-radius: 12px; border-left: 4px solid #3b82f6;">
            <h2 style="font-family: 'Space Mono', monospace; font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 5px;">
                {candidate_name}
            </h2>
            <h3 style="font-family: 'Space Mono', monospace; font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #64748b; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #cbd5e1;">
                AI Analysis & ATS Score
            </h3>

            <div style="display: flex; gap: 30px; margin-bottom: 20px; flex-wrap: wrap;">
                <div style="text-align: center; padding: 15px 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 32px; font-weight: 700; color: {'#22c55e' if ats_score >= 80 else '#eab308' if ats_score >= 60 else '#ef4444'};">{ats_score}</div>
                    <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">ATS Score</div>
                </div>
                <div style="text-align: center; padding: 15px 25px; background: white; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <div style="font-size: 32px; font-weight: 700; color: {'#22c55e' if keyword_match >= 80 else '#eab308' if keyword_match >= 60 else '#ef4444'};">{keyword_match}%</div>
                    <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">Keyword Match</div>
                </div>
            </div>

            {f'<p style="font-size: 13px; color: #475569; line-height: 1.6; margin-bottom: 20px; font-style: italic;">{summary}</p>' if summary else ''}

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                {f'''<div style="background: white; padding: 15px; border-radius: 8px;">
                    <h4 style="font-size: 12px; color: #22c55e; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">✓ Strengths</h4>
                    <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #475569; line-height: 1.8;">
                        {''.join(f'<li>{s}</li>' for s in strengths[:3])}
                    </ul>
                </div>''' if strengths else ''}

                {f'''<div style="background: white; padding: 15px; border-radius: 8px;">
                    <h4 style="font-size: 12px; color: #f59e0b; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 1px;">⚡ Improvements</h4>
                    <ul style="margin: 0; padding-left: 18px; font-size: 12px; color: #475569; line-height: 1.8;">
                        {''.join(f'<li>{i}</li>' for i in improvements[:3])}
                    </ul>
                </div>''' if improvements else ''}
            </div>

            {f'''<div style="margin-top: 15px; padding: 12px 15px; background: #fef3c7; border-radius: 8px; border: 1px solid #fcd34d;">
                <span style="font-size: 11px; color: #92400e; font-weight: 600;">Missing Keywords: </span>
                <span style="font-size: 11px; color: #b45309;">{', '.join(missing_keywords[:5])}</span>
            </div>''' if missing_keywords else ''}
        </section>
        """

        # Find container and append
        container = soup.find(class_=lambda c: c and any(x in c for x in ['container', 'resume', 'page', 'main-content']))
        if container:
            container.append(BeautifulSoup(analysis_html, 'html.parser'))
        else:
            body = soup.body
            if body:
                body.append(BeautifulSoup(analysis_html, 'html.parser'))

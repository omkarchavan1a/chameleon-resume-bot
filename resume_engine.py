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

        # Split by sections
        sections = re.split(r'\n## ', md_content)
        for section in sections:
            lines = section.split('\n')
            header = lines[0].strip().lower()
            content = '\n'.join(lines[1:]).strip()
            
            if 'summary' in header:
                data["summary"] = content
            elif 'skills' in header:
                # Extract bullet points or comma separated
                if ',' in content and '\n' not in content:
                    data["skills"] = [s.strip() for s in content.split(',') if s.strip()]
                else:
                    data["skills"] = [re.sub(r'^[-*]\s*', '', l).strip() for l in content.split('\n') if l.strip()]
            elif 'experience' in header:
                exp_entries = re.split(r'\n### ', '\n' + content)
                for entry in exp_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    header_parts = entry_lines[0].split('|')
                    role = header_parts[0].strip()
                    company = header_parts[1].strip() if len(header_parts) > 1 else ""
                    
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
            elif 'education' in header:
                edu_entries = re.split(r'\n### ', '\n' + content)
                for entry in edu_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    data["education"].append({
                        "degree": entry_lines[0].strip(),
                        "details": '\n'.join(entry_lines[1:]).strip()
                    })
            elif 'project' in header:
                proj_entries = re.split(r'\n### ', '\n' + content)
                for entry in proj_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    data["projects"].append({
                        "name": entry_lines[0].strip(),
                        "details": '\n'.join(entry_lines[1:]).strip()
                    })
            elif 'award' in header or 'certification' in header:
                award_entries = re.split(r'\n### ', '\n' + content)
                for entry in award_entries:
                    if not entry.strip(): continue
                    entry_lines = entry.strip().split('\n')
                    data["awards"].append({
                        "name": entry_lines[0].strip(),
                        "details": '\n'.join(entry_lines[1:]).strip()
                    })
                    
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
        # Do not match container divs that wrap the whole page!
        # If it has block children like 'div', 'section', 'ul', it's probably a container, not a header.
        if tag.name == 'div' and tag.find(['div', 'section', 'ul']):
            return False
        text = tag.get_text(strip=True).lower()
        return any(kw in text for kw in keywords)

    @staticmethod
    def render_html(template_path, data):
        """
        Inject structured resume data into an HTML template.

        Strategy:
        1. Try precise DOM injection using the class names present in the templates.
        2. If the injected name doesn't match (i.e. injection failed), fall back to
           embedding a fully rendered markdown block inside the template's main container.
        This guarantees the downloaded PDF always contains the user's real data.
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

            # Update phone text in leaf nodes
            for item in contact_container.find_all(['span', 'div', 'p']):
                text = item.get_text(strip=True)
                if re.search(r'\+?\d[\d\s\-()]{7,}', text) and data["contact"]["phone"]:
                    if not item.find(['span', 'div', 'a']):
                        item.clear()
                        item.string = data["contact"]["phone"]
                        break

        # ── 4. Summary ───────────────────────────────────────────────────────
        summary_text = data.get("summary", "")
        if summary_text:
            summary_elem = fe._find_by_cls(soup, 'summary', 'about-text', 'profile-text', 'bio', 'objective', 'summary-text')
            if not summary_elem:
                hdr = soup.find(lambda t: fe._is_header_matching(t, 'summary', 'about', 'profile', 'objective'))
                if hdr:
                    candidate = hdr.find_next(['p', 'div'])
                    # Don't grab another section header
                    if candidate and not candidate.find(['h2', 'h3']):
                        summary_elem = candidate
            fe._set_text(summary_elem, summary_text)

        # ── 5. Experience ─────────────────────────────────────────────────────
        exp_data = data.get("experience", [])
        if exp_data:
            exp_section = fe._find_by_cls(soup, 'experience-list', 'experience-container', 'work-experience', 'work-history', 'jobs-list')
            if not exp_section:
                hdr = soup.find(lambda t: fe._is_header_matching(t, 'experience', 'work history', 'employment', 'career'))
                if hdr:
                    exp_section = hdr.find_parent(['section', 'article']) or hdr.parent

            if exp_section:
                # Find first entry element to use as clone template
                entry_tmpl = exp_section.find(lambda t: fe._cls_match(t, 'entry', 'experience-item', 'job-item', 'work-item', 'position-block'))

                if entry_tmpl:
                    entry_classes = entry_tmpl.get('class', [])
                    for e in exp_section.find_all(class_=entry_classes):
                        e.decompose()

                    for item in exp_data:
                        new_e = copy.copy(entry_tmpl)
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
                else:
                    # No clonable entry — build raw HTML blocks
                    hdr_tag = exp_section.find(lambda t: t.name in ['h2', 'h3'] and
                                               any(x in t.get_text().lower() for x in ['experience', 'work']))
                    exp_section.clear()
                    if hdr_tag:
                        exp_section.append(hdr_tag)
                    for item in exp_data:
                        highlights_html = ''.join(f'<li>{h}</li>' for h in item.get("highlights", []))
                        block = BeautifulSoup(
                            f'<div class="entry">'
                            f'<div class="entry-header">'
                            f'<div><div class="position">{item.get("role","")}</div>'
                            f'<div class="organization">{item.get("company","")}</div></div>'
                            f'<div class="date">{item.get("date","")}</div></div>'
                            f'<div class="entry-description"><ul>{highlights_html}</ul></div></div>',
                            'html.parser'
                        )
                        exp_section.append(block)

        # ── 6. Education ──────────────────────────────────────────────────────
        edu_data = data.get("education", [])
        if edu_data:
            edu_section = fe._find_by_cls(soup, 'education-list', 'education-container', 'edu-list')
            if not edu_section:
                hdr = soup.find(lambda t: fe._is_header_matching(t, 'education'))
                if hdr:
                    edu_section = hdr.find_parent(['section', 'article']) or hdr.parent

            if edu_section:
                entry_tmpl = edu_section.find(lambda t: fe._cls_match(t, 'entry', 'education-item', 'edu-item'))
                if entry_tmpl:
                    for e in edu_section.find_all(class_=entry_tmpl.get('class', [])):
                        e.decompose()
                    for item in edu_data:
                        new_e = copy.copy(entry_tmpl)
                        if new_e is None: continue
                        deg_el = new_e.find(lambda t: fe._cls_match(t, 'position', 'degree', 'qualification'))
                        fe._set_text(deg_el, item.get("degree", ""))
                        det_el = new_e.find(lambda t: fe._cls_match(t, 'organization', 'institution', 'school', 'details', 'edu-details'))
                        fe._set_text(det_el, item.get("details", ""))
                        edu_section.append(new_e)

        # ── 7. Skills ─────────────────────────────────────────────────────────
        skills_data = data.get("skills", [])
        if skills_data:
            skills_container = fe._find_by_cls(soup, 'skills-grid', 'skills-list', 'skills-container', 'skill-tags', 'skills-wrapper', 'tech-stack')
            if not skills_container:
                hdr = soup.find(lambda t: fe._is_header_matching(t, 'skill'))
                if hdr:
                    section = hdr.find_parent(['section', 'article'])
                    if section:
                        skills_container = (
                            fe._find_by_cls(section, 'skills-grid', 'skills-list', 'skill-tags')
                            or section
                        )
                    else:
                        skills_container = hdr.find_next(['div', 'ul'])

            if skills_container:
                item_tmpl = skills_container.find(lambda t: fe._cls_match(t, 'skill-tag', 'skill-item', 'skill-box', 'skill-badge', 'tag'))
                if item_tmpl:
                    for e in skills_container.find_all(class_=item_tmpl.get('class', [])):
                        e.decompose()
                    for skill in skills_data:
                        new_i = copy.copy(item_tmpl)
                        if new_i is None: continue
                        label_el = new_i.find(lambda t: fe._cls_match(t, 'skill-label', 'skill-title', 'label'))
                        value_el = new_i.find(lambda t: fe._cls_match(t, 'skill-value', 'skill-text', 'value'))
                        if label_el:
                            label_el.clear()
                            label_el.string = skill
                            if value_el:
                                value_el.clear()
                        else:
                            new_i.clear()
                            new_i.string = skill
                        skills_container.append(new_i)
                else:
                    skills_container.clear()
                    for skill in skills_data:
                        span = soup.new_tag('span', attrs={'class': 'skill-tag'})
                        span.string = skill
                        skills_container.append(span)
                        skills_container.append(BeautifulSoup(' ', 'html.parser'))

        # ── 8. Fallback: embed rendered markdown if injection failed ──────────
        # Check if the name was actually injected (not a placeholder)
        PLACEHOLDER_NAMES = {'sarah chen', 'john doe', 'your name', 'jane doe', 'alex johnson', ''}
        name_check = fe._find_by_cls(soup, 'name', 'candidate-name', 'full-name', 'hero-name')
        injected = (
            name_check is not None and
            name_check.get_text(strip=True).lower() not in PLACEHOLDER_NAMES
        )

        if not injected and data.get("name", "Anonymous") != "Anonymous":
            md_html = markdown.markdown(
                ResumeEngine._data_to_markdown(data),
                extensions=['extra', 'nl2br']
            )
            fallback_css = """
            <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; color: #222; line-height: 1.7; padding: 40px; }
            h1 { font-size: 28px; margin-bottom: 4px; }
            h2 { font-size: 18px; border-bottom: 1px solid #ccc; padding-bottom: 4px; margin-top: 24px; }
            h3 { font-size: 14px; margin-bottom: 2px; }
            ul { margin: 8px 0 8px 20px; }
            li { margin-bottom: 4px; }
            p { margin: 6px 0; }
            </style>
            """
            # Try to embed inside the template's <style> and <body>
            style_tag = soup.find('style')
            if style_tag:
                style_tag.insert_after(BeautifulSoup(fallback_css, 'html.parser'))

            main_container = (
                soup.find(class_=lambda c: c and any(x in c for x in ['container', 'resume', 'page', 'wrapper']))
                or soup.find('main')
                or soup.body
            )
            if main_container:
                main_container.clear()
                main_container.append(BeautifulSoup(md_html, 'html.parser'))

        return str(soup)

    @staticmethod
    def _data_to_markdown(data):
        """Convert structured resume data back to clean markdown (used for fallback rendering)."""
        lines = []
        name = data.get("name", "")
        title = data.get("title", "")
        contact = data.get("contact", {})

        if name:
            lines.append(f"# {name}")
        contact_parts = [title] if title else []
        for k in ['email', 'phone', 'linkedin', 'github']:
            if contact.get(k):
                contact_parts.append(contact[k])
        if contact_parts:
            lines.append(' | '.join(contact_parts))
        lines.append('')

        if data.get("summary"):
            lines.append("## Professional Summary")
            lines.append(data["summary"])
            lines.append('')

        if data.get("experience"):
            lines.append("## Experience")
            for exp in data["experience"]:
                company = exp.get('company', '')
                role = exp.get('role', '')
                heading = f"{role} | {company}" if company else role
                lines.append(f"### {heading}")
                if exp.get('date'):
                    lines.append(f"*{exp['date']}*")
                for h in exp.get("highlights", []):
                    lines.append(f"- {h}")
                lines.append('')

        if data.get("education"):
            lines.append("## Education")
            for edu in data["education"]:
                lines.append(f"### {edu.get('degree','')}")
                if edu.get('details'):
                    lines.append(edu['details'])
                lines.append('')

        if data.get("skills"):
            lines.append("## Skills")
            lines.append(', '.join(data["skills"]))
            lines.append('')

        if data.get("projects"):
            lines.append("## Projects")
            for proj in data["projects"]:
                lines.append(f"### {proj.get('name','')}")
                if proj.get('details'):
                    lines.append(proj['details'])
                lines.append('')

        if data.get("awards"):
            lines.append("## Awards & Certifications")
            for award in data["awards"]:
                lines.append(f"### {award.get('name','')}")
                if award.get('details'):
                    lines.append(award['details'])
                lines.append('')

        return '\n'.join(lines)

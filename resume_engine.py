import os
import re
import io
import json
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

    @staticmethod
    def render_html(template_path, data):
        """Inject structured data into an HTML template."""
        if not os.path.exists(template_path):
            return f"Template not found: {template_path}"
            
        with open(template_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # 1. Update Name and Title
        name_elem = soup.find(class_='name')
        if name_elem: name_elem.string = data["name"]
        
        title_elem = soup.find(class_='title')
        if title_elem: title_elem.string = data["title"]
        
        # 2. Update Contact
        contact_container = soup.find(class_='contact')
        if contact_container:
            links = contact_container.find_all('a')
            for link in links:
                href = link.get('href', '')
                if 'mailto' in href and data["contact"]["email"]:
                    link.string = data["contact"]["email"]
                    link['href'] = f"mailto:{data['contact']['email']}"
                elif ('linkedin' in href or 'linkedin' in link.text.lower()) and data["contact"]["linkedin"]:
                    link['href'] = data["contact"]["linkedin"]
                elif ('github' in href or 'github' in link.text.lower()) and data["contact"]["github"]:
                    link['href'] = data["contact"]["github"]
            
            # Update phone if present as span or text
            spans = contact_container.find_all('span')
            for span in spans:
                if re.search(r'\d', span.text) and data["contact"]["phone"]:
                    span.string = data["contact"]["phone"]

        # 3. Update Summary
        summary_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and 'summary' in tag.text.lower())
        summary_container = soup.find(class_='summary') or soup.find(class_='summary-text')
        if not summary_container and summary_header:
            summary_container = summary_header.find_next(['div', 'p'])
        
        if summary_container:
            if data["summary"]:
                text_elem = summary_container.find(class_='summary-text') or summary_container
                if text_elem: text_elem.string = data["summary"]
            else:
                outer_summary = summary_container.find_parent(['section', 'div'], class_=['section', 'card']) or summary_container
                outer_summary.decompose()

        # 4. Update Experience
        exp_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and 'experience' in tag.text.lower())
        if exp_header:
            container = exp_header.find_parent(['section', 'div', 'main'], class_=['section', 'main', 'card', 'content-section'])
            if not container:
                container = exp_header.find_next(['div', 'section'])
                
            if data["experience"] and container:
                entry_template = container.find(class_=['entry', 'entry-item'])
                if entry_template:
                    entries = container.find_all(class_=['entry', 'entry-item'])
                    for e in entries: e.decompose()
                    
                    for item in data["experience"]:
                        new_entry = BeautifulSoup(str(entry_template), 'html.parser').find()
                        
                        pos = new_entry.find(class_=['position', 'job-title'])
                        if pos: pos.string = item["role"]
                        
                        org = new_entry.find(class_=['organization', 'company', 'employer'])
                        if org: org.string = item["company"]
                        
                        date = new_entry.find(class_=['date', 'period'])
                        if date: date.string = item["date"]
                        
                        ul = new_entry.find('ul')
                        if ul:
                            ul.clear()
                            for h in item["highlights"]:
                                li = soup.new_tag('li')
                                li.string = h
                                ul.append(li)
                        
                        container.append(new_entry)
            elif container:
                outer_exp = container.find_parent(['section', 'div'], class_=['section', 'card']) or container
                outer_exp.decompose()

        # 5. Update Education
        edu_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and 'education' in tag.text.lower())
        if edu_header:
            container = edu_header.find_parent(['section', 'div', 'main'], class_=['section', 'main', 'card', 'content-section'])
            if not container:
                container = edu_header.find_next(['div', 'section'])
                
            if data["education"] and container:
                entry_template = container.find(class_=['entry', 'entry-item'])
                if entry_template:
                    entries = container.find_all(class_=['entry', 'entry-item'])
                    for e in entries: e.decompose()
                    
                    for item in data["education"]:
                        new_entry = BeautifulSoup(str(entry_template), 'html.parser').find()
                        
                        degree = new_entry.find(class_=['position', 'degree', 'study-program'])
                        if degree: degree.string = item["degree"]
                        
                        desc = new_entry.find(class_=['entry-description', 'description', 'edu-details'])
                        if desc: desc.string = item["details"]
                        
                        container.append(new_entry)
            elif container:
                outer_edu = container.find_parent(['section', 'div'], class_=['section', 'card']) or container
                outer_edu.decompose()

        # 6. Update Skills
        skills_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and 'skills' in tag.text.lower())
        if skills_header:
            skills_container = skills_header.find_parent(['section', 'div'], class_=['section', 'card'])
            if not skills_container:
                skills_container = skills_header.find_next(['div', 'section'])
                
            if data["skills"] and skills_container:
                inner_container = skills_container.find(class_=['skills-grid', 'skills-container', 'skills-list', 'skill-tags']) or skills_container
                
                # Handle skill-tag pattern
                if inner_container.find(class_=['skill-tag', 'skill-item']):
                    tags = inner_container.find_all(class_=['skill-tag', 'skill-item'])
                    for t in tags: t.decompose()
                    for s in data["skills"]:
                        new_tag = soup.new_tag('span', attrs={'class': 'skill-tag'})
                        new_tag.string = s
                        inner_container.append(new_tag)
                else:
                    inner_container.clear()
                    for s in data["skills"]:
                        span = soup.new_tag('span', attrs={'class': 'skill-tag'})
                        span.string = s
                        inner_container.append(span)
            elif skills_container:
                skills_container.decompose()

        # 7. Update Projects
        proj_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and 'project' in tag.text.lower())
        if proj_header:
            container = proj_header.find_parent(['section', 'div', 'main'], class_=['section', 'main', 'card', 'content-section'])
            if not container:
                container = proj_header.find_next(['div', 'section'])
                
            if data["projects"] and container:
                entry_template = container.find(class_=['entry', 'entry-item'])
                if entry_template:
                    entries = container.find_all(class_=['entry', 'entry-item'])
                    for e in entries: e.decompose()
                    for item in data["projects"]:
                        new_entry = BeautifulSoup(str(entry_template), 'html.parser').find()
                        name = new_entry.find(class_=['position', 'name', 'project-title']) or new_entry.find('span')
                        if name: name.string = item["name"]
                        desc = new_entry.find(class_=['entry-description', 'description', 'project-details'])
                        if desc: desc.string = item["details"]
                        container.append(new_entry)
            elif container:
                outer_proj = container.find_parent(['section', 'div'], class_=['section', 'card']) or container
                outer_proj.decompose()

        # 8. Update Awards/Certifications
        award_header = soup.find(lambda tag: tag.name in ['div', 'span', 'h2', 'h3'] and any(x in tag.text.lower() for x in ['award', 'certif', 'honor']))
        if award_header:
            container = award_header.find_parent(['section', 'div', 'main'], class_=['section', 'main', 'card', 'content-section'])
            if not container:
                container = award_header.find_next(['div', 'section'])
                
            if data["awards"] and container:
                entry_template = container.find(class_=['entry', 'entry-item'])
                if entry_template:
                    entries = container.find_all(class_=['entry', 'entry-item'])
                    for e in entries: e.decompose()
                    for item in data["awards"]:
                        new_entry = BeautifulSoup(str(entry_template), 'html.parser').find()
                        name = new_entry.find(class_=['position', 'name', 'award-title']) or new_entry.find('span')
                        if name: name.string = item["name"]
                        desc = new_entry.find(class_=['entry-description', 'description', 'award-details'])
                        if desc: desc.string = item["details"]
                        container.append(new_entry)
            elif container:
                outer_award = container.find_parent(['section', 'div'], class_=['section', 'card']) or container
                outer_award.decompose()

        return str(soup)

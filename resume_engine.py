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
            
        # 1. Basic Info (Highest Precision)
        name_elem = soup.find(class_='name')
        if name_elem: 
            name_elem.clear()
            name_elem.string = data["name"]
        
        title_elem = soup.find(class_='title')
        if title_elem: 
            title_elem.clear()
            title_elem.string = data["title"]
        
        # 2. Contact Info
        contact_container = soup.find(class_='contact')
        if contact_container:
            # Update links
            for link in contact_container.find_all('a'):
                href = link.get('href', '')
                if 'mailto' in href or (link.string and '@' in link.string):
                    if data["contact"]["email"]:
                        link.string = data["contact"]["email"]
                        link['href'] = f"mailto:{data['contact']['email']}"
                elif 'linkedin' in href or 'linkedin' in (link.string or '').lower():
                    if data["contact"]["linkedin"]:
                        link['href'] = data["contact"]["linkedin"]
                elif 'github' in href or 'github' in (link.string or '').lower():
                    if data["contact"]["github"]:
                        link['href'] = data["contact"]["github"]
            
            # Update phone numbers in spans/divs
            for item in contact_container.find_all(['span', 'div']):
                if item.string and re.search(r'\d{5}', item.string):
                    if data["contact"]["phone"]:
                        item.string = data["contact"]["phone"]

        # 3. Summary Section
        summary_container = soup.find(class_=['summary', 'summary-text', 'about-text'])
        if not summary_container:
            # Fallback: search for header with "summary" or "about"
            header = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'div'] and 
                              any(x in tag.text.lower() for x in ['summary', 'about', 'profile']))
            if header:
                summary_container = header.find_next(['p', 'div'])
        
        if summary_container:
            summary_container.clear()
            summary_container.string = data.get("summary", "")

        # 4. Experience Section
        exp_container = soup.find(class_=['experience-list', 'experience-container', 'work-experience'])
        if not exp_container:
            header = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'div'] and 
                              any(x in tag.text.lower() for x in ['experience', 'work history']))
            if header:
                exp_container = header.find_parent(['section', 'div'], class_=['section', 'card']) or header.find_next(['div', 'section'])

        if exp_container and data.get("experience"):
            template = exp_container.find(class_=['entry', 'experience-item'])
            if template:
                # Remove existing entries
                for entry in exp_container.find_all(class_=['entry', 'experience-item']):
                    entry.decompose()
                
                for item in data["experience"]:
                    new_entry = BeautifulSoup(str(template), 'html.parser').find()
                    
                    role = new_entry.find(class_=['position', 'role', 'job-title'])
                    if role: role.string = item["role"]
                    
                    company = new_entry.find(class_=['organization', 'company', 'employer'])
                    if company: company.string = item["company"]
                    
                    date = new_entry.find(class_=['date', 'period'])
                    if date: date.string = item["date"]
                    
                    desc_list = new_entry.find('ul')
                    if desc_list:
                        desc_list.clear()
                        for highlight in item["highlights"]:
                            li = soup.new_tag('li')
                            li.string = highlight
                            desc_list.append(li)
                    
                    exp_container.append(new_entry)

        # 5. Education Section
        edu_container = soup.find(class_=['education-list', 'education-container'])
        if not edu_container:
            header = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'div'] and 'education' in tag.text.lower())
            if header:
                edu_container = header.find_parent(['section', 'div'], class_=['section', 'card']) or header.find_next(['div', 'section'])

        if edu_container and data.get("education"):
            template = edu_container.find(class_=['entry', 'education-item'])
            if template:
                for entry in edu_container.find_all(class_=['entry', 'education-item']):
                    entry.decompose()
                
                for item in data["education"]:
                    new_entry = BeautifulSoup(str(template), 'html.parser').find()
                    degree = new_entry.find(class_=['position', 'degree'])
                    if degree: degree.string = item["degree"]
                    details = new_entry.find(class_=['organization', 'details', 'edu-details'])
                    if details: details.string = item.get("details", "")
                    edu_container.append(new_entry)

        # 6. Skills Section (The tricky one)
        skills_container = soup.find(class_=['skills-grid', 'skills-list', 'skills-container', 'skill-tags'])
        if not skills_container:
            header = soup.find(lambda tag: tag.name in ['h1', 'h2', 'h3', 'div'] and 'skills' in tag.text.lower())
            if header:
                # Find the actual grid/list within the section
                section = header.find_parent(['section', 'div'], class_=['section', 'card'])
                if section:
                    skills_container = section.find(class_=['skills-grid', 'skills-list', 'skills-container', 'skill-tags']) or section
                else:
                    skills_container = header.find_next(['div', 'ul'])

        if skills_container and data.get("skills"):
            # Try to find a template for a single skill
            item_template = skills_container.find(class_=['skill-tag', 'skill-item', 'skill-box'])
            if item_template:
                # Clean up existing items
                for item in skills_container.find_all(class_=['skill-tag', 'skill-item', 'skill-box']):
                    item.decompose()
                
                for skill in data["skills"]:
                    new_item = BeautifulSoup(str(item_template), 'html.parser').find()
                    if not new_item:
                        continue
                        
                    classes = new_item.get('class', [])
                    if not isinstance(classes, list):
                        classes = [classes] if classes else []
                        
                    # If it's a simple tag, set string
                    if 'skill-tag' in classes or 'skill-item' in classes:
                        new_item.string = skill
                    else:
                        # Find title or list within box
                        title = new_item.find(class_=['skill-title', 'skill-label'])
                        if title: 
                            title.string = skill
                        else:
                            new_item.string = skill
                    skills_container.append(new_item)
            else:
                # Fallback: simple bullet list or clearing
                skills_container.clear()
                for skill in data["skills"]:
                    span = soup.new_tag('span', attrs={'class': 'skill-tag'})
                    span.string = skill
                    skills_container.append(span)

        return str(soup)

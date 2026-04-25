from bs4 import BeautifulSoup
import traceback

def _cls_match(tag, *keywords):
    if not hasattr(tag, 'get'):
        return False
    classes = tag.get('class', [])
    if isinstance(classes, str):
        classes = [classes]
    combined = ' '.join(classes).lower()
    return any(kw in combined for kw in keywords)

try:
    with open('../files/resume-1-minimalist.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    res = soup.find(lambda t: _cls_match(t, 'name'))
    print('Result:', res)
except Exception as e:
    traceback.print_exc()

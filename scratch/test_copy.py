from bs4 import BeautifulSoup
import copy

soup = BeautifulSoup('<div class="pill">System Design</div>', 'html.parser')
tmpl = soup.find('div')
new_i = copy.copy(tmpl)
new_i.clear()
new_i.string = 'Python'
print(f'Original: {tmpl}')
print(f'New: {new_i}')

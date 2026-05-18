"""Probe ACGME ADS public reports to find the program-by-institution data."""
import requests
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
})

# Inspect Report/3 content
r = session.get('https://apps.acgme.org/ads/Public/Reports/Report/3', timeout=20)
text = r.text

# Find all headings, table labels, form fields
heads = re.findall(r'<th[^>]*>(.*?)</th>', text, re.DOTALL)
labels = re.findall(r'<label[^>]*>(.*?)</label>', text, re.DOTALL)
inputs = re.findall(r'<(?:input|select)[^>]*name="([^"]+)"[^>]*>', text)

# Strip HTML
def strip_html(s):
    return re.sub(r'<[^>]*>', '', s).strip()

print('Page title (from H3):')
h3s = re.findall(r'<h3[^>]*>(.*?)</h3>', text, re.DOTALL)
for h in h3s[:5]:
    print(f'  {strip_html(h)[:120]}')

print('\nTable headers:')
for h in heads[:25]:
    print(f'  {strip_html(h)[:120]}')

print('\nForm labels:')
for l in labels[:15]:
    print(f'  {strip_html(l)[:100]}')

print('\nForm inputs:')
for i in inputs[:25]:
    print(f'  {i}')

# Look for download / report-data hints
print('\nDownload / data hints:')
for kw in ['Download', 'CSV', 'Excel', 'xlsx', 'Export']:
    if kw in text:
        idx = text.find(kw)
        print(f'  {kw}: ...{text[max(0,idx-30):idx+80]}...')

import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # Try the search URL and wait for network idle
    page.goto('https://forums.studentdoctor.net/search/?q=PSLF&t=post&o=relevance', wait_until='networkidle', timeout=30000)
    page.wait_for_timeout(3000)

    print(f'URL: {page.url}')

    # Take screenshot
    page.screenshot(path='C:/Users/zanen/PSLF_2026/sdn_debug.png')

    # Get HTML and look for thread links
    html = page.content()
    pattern = r'href="([^"]*?/threads/[^"]*?)"'
    thread_links = re.findall(pattern, html)
    print(f'Thread links in HTML: {len(thread_links)}')
    for link in thread_links[:10]:
        print(f'  {link}')

    # Check forms
    forms = page.query_selector_all('form')
    print(f'Forms: {len(forms)}')
    for form in forms[:5]:
        action = form.get_attribute('action') or ''
        method = form.get_attribute('method') or ''
        print(f'  form action={action} method={method}')

    # Check if the search form needs POST submission
    # Try submitting the search form directly
    search_form = page.query_selector('form[action*="search"]')
    if search_form:
        print(f'Found search form')
        # Try to use the visible search input
        visible_inputs = page.query_selector_all('input:visible')
        print(f'Visible inputs: {len(visible_inputs)}')
        for inp in visible_inputs:
            name = inp.get_attribute('name') or ''
            print(f'  visible input: name={name}')

    browser.close()

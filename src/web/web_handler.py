import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from termcolor import colored

def crawl(domain, payloads):
    start_time = time.time()
    vuln_count = 0
    print(colored(f"\nStarting scan on: {domain}", 'cyan', attrs=['bold']))

    # Playwright setup replaces the messy 'Options' block
    with sync_playwright() as p:
        # Launching Chromium - cleaner and lighter than standard Chrome
        browser = p.chromium.launch(headless=True)

        # 'context' handles the User-Agent and Window Size effortlessly
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        forms = []
        param_urls = []
        visited = set()
        queue = [domain]
        max_pages = 10
        pages_crawled = 0

        while queue and pages_crawled < max_pages:
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            print(colored(f"[+] Crawling: {url}", 'cyan'))
            pages_crawled += 1

            try:
                # Playwright's goto waits for the network to be idle (more stable than sleep)
                page.goto(url, wait_until="domcontentloaded", timeout=10000)

                # Replaces your manual sleep(0.2) with a more reliable check
                page.wait_for_load_state("networkidle")

                # Get the content for BeautifulSoup
                soup = BeautifulSoup(page.content(), 'html.parser')

                for form in soup.find_all('form'):
                    action = urljoin(url, form.get('action') or url)
                    method = form.get('method', 'get').lower()
                    inputs = []
                    # More specific selector for input fields
                    for inp in form.find_all(['input', 'textarea', 'select']):
                        name = inp.get('name') or inp.get('id')
                        if name:
                            inputs.append((name, inp.get('type', 'text')))
                    if inputs:
                        forms.append({'url': url, 'action': action, 'method': method, 'inputs': inputs})

                current_url = page.url
                if '?' in current_url:
                    param_urls.append(current_url)

                for a in soup.find_all('a', href=True):
                    link = urljoin(url, a['href'])
                    parsed_link = urlparse(link)
                    if parsed_link.netloc == urlparse(domain).netloc and link not in visited and '?' in link:
                        queue.append(link)

            except Exception as e:
                print(colored(f"[!] Crawl error at {url}: {str(e)[:100]}", 'red'))

        # De-duplicate forms based on URL
        forms = list({f['url']: f for f in forms}.values())
        param_urls = list(set(param_urls))

        # IMPORTANT: You will need to rewrite your tf, tu, and tl functions
        # to accept 'page' instead of 'driver'
        if forms:
            print(colored(f"[+] Found {len(forms)} forms", 'green'))
            for form in forms:
                vuln_count += tf(page, form, payloads)

        if param_urls:
            print(colored(f"[+] Found {len(param_urls)} param URLs", 'green'))
            for p_url in param_urls:
                vuln_count += tu(page, p_url, payloads)

        if not forms and not param_urls:
            print(colored("[!] No forms/params found. Testing loose inputs...", 'yellow'))
            vuln_count += tl(page, domain, payloads)

        browser.close()

    time_taken = time.time() - start_time
    print("\n" + "="*60)
    if vuln_count > 0:
        print(colored("TARGET IS VULNERABLE TO XSS! Fix it!".center(60), 'green', attrs=['bold']))
    else:
        print(colored("No XSS vulnerability found. keep trying :)".center(60), 'red', attrs=['bold']))
    print(colored(f"Scan completed in {time_taken:.2f} seconds. Issues found: {vuln_count}", 'cyan'))
    print("="*60)
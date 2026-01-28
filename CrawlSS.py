import os
import platform

from termcolor import colored
from pathlib import Path

TOOL_NAME = "dzXSS"
TOOL_VERSION = "1.0"
PAYLOADS_DIR = "payloads"

def clear_terminal():
    """Clear terminal based on operating system"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_banner():
    """Print application banner"""
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

    for idx, file in enumerate(payload_files, start=1):
        print(f"{idx}. {file.name}")

    # """Allow user to pick a payload from the payloads directory"""
    # try:
    #     payload_files = [f for f in os.listdir(PAYLOADS_DIR) if os.path.isfile(os.path.join(PAYLOADS_DIR, f))]
    #     if not payload_files:
    #         print(colored("No payload files found in the payloads directory.", 'red'))
    #         return None

    #     print(colored("Available Payloads:", 'green', attrs=['bold']))
    #     for idx, file in enumerate(payload_files, start=1):
    #         print(f"{idx}. {file}")

    #     choice = int(input(colored("Select a payload by number: ", 'yellow')))
    #     if 1 <= choice <= len(payload_files):
    #         selected_file = payload_files[choice - 1]
    #         with open(os.path.join(PAYLOADS_DIR, selected_file), 'r') as f:
    #             payloads = f.read().splitlines()
    #         return payloads
    #     else:
    #         print(colored("Invalid selection.", 'red'))
    #         return None
    # except Exception as e:
    #     print(colored(f"Error selecting payload: {e}", 'red'))
    #     return None



if __name__ == "__main__":
    clear_terminal()
    print_banner()
    pick_payload()

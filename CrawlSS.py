import os
import platform

from termcolor import colored

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

if __name__ == "__main__":
    clear_terminal()
    print_banner()
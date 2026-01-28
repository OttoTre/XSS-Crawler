#!/usr/bin/env python
import sys

from termcolor import colored

from src.crawlss import run

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print(colored("\n[!]🛑 Program interrupted by user. Exiting...", 'yellow'))
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
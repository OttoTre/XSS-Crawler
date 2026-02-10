#!/usr/bin/env python3
"""
Test Runner for crawlss Project
Run all tests and generate coverage reports
"""

import subprocess
import sys

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running crawlss Tests...")
    print("=" * 50)

    cmd = [
        "python", "-m", "pytest",
        "tests/py/test_crawlss.py",
        "tests/py/test_web_utils.py",
        "-v"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("STDERR:")
            print(result.stderr)

        print(f"\nExit code: {result.returncode}")

        if result.returncode == 0:
            print("✅ All tests passed!")
            print("💡 Tip: Install pytest-cov for coverage reports: pip install pytest-cov")
        else:
            print("❌ Some tests failed!")

        return result.returncode

    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return 1

if __name__ == "__main__":
    exit_code = run_tests()

    sys.exit(exit_code)

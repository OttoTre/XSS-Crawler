#!/usr/bin/env python3
"""
Test Runner for CrawlSS Project
Run all tests and generate coverage reports
"""

import subprocess
import sys

def run_tests():
    """Run all tests with coverage"""
    print("🧪 Running CrawlSS Tests...")
    print("=" * 50)

    # Run pytest without coverage first (since pytest-cov might not be available)
    cmd = [
        "python", "-m", "pytest",
        "tests/py/test_CrawlSS.py",  # pytest version
        "-v"                      # verbose output
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

def run_unittest():
    """Fallback to unittest if pytest fails"""
    print("📋 Running with unittest...")
    cmd = ["python", "tests/ut/test_CrawlSS.py"]

    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    # Try pytest first, fallback to unittest
    exit_code = run_tests()

    if exit_code != 0:
        print("\n🔄 Trying unittest...")
        exit_code = run_unittest()

    sys.exit(exit_code)
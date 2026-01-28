import pytest
from unittest.mock import patch
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path so we can import CrawlSS
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import your functions
from CrawlSS import clear_terminal, print_banner, pick_payload, PAYLOADS_DIR

class TestCrawlSS:
    """Modern pytest test cases for CrawlSS.py"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        test_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(test_dir)

        yield test_dir

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)

    def test_clear_terminal_windows(self, temp_dir):
        """Test clear_terminal on Windows"""
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value='Windows'):
                clear_terminal()
                mock_system.assert_called_once_with('cls')

    def test_clear_terminal_unix(self, temp_dir):
        """Test clear_terminal on Unix/Linux/Mac"""
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value='Linux'):
                clear_terminal()
                mock_system.assert_called_once_with('clear')

    def test_print_banner(self, temp_dir):
        """Test that print_banner executes without error"""
        # Just test that it doesn't crash
        print_banner()

    def test_pick_payload_creates_directory(self, temp_dir):
        """Test that pick_payload creates payloads directory if it doesn't exist"""
        payloads_path = Path(temp_dir) / PAYLOADS_DIR

        # Ensure directory doesn't exist
        if payloads_path.exists():
            shutil.rmtree(payloads_path)

        with patch('builtins.print'):
            result = pick_payload()
            assert result is None
            assert payloads_path.exists()

    def test_pick_payload_with_files(self, temp_dir):
        """Test pick_payload with actual payload files"""
        payloads_path = Path(temp_dir) / PAYLOADS_DIR
        payloads_path.mkdir(exist_ok=True)

        # Create test files
        (payloads_path / 'payload1.txt').write_text('<script>alert(1)</script>')
        (payloads_path / 'payload2.txt').write_text('<img src=x onerror=alert(2)>')
        (payloads_path / 'not_payload.py').write_text('print("not a payload")')

        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value='1'):
                result = pick_payload()
                assert result is not None
                assert isinstance(result, list)
                assert '<script>alert(1)</script>' in result

    @pytest.mark.parametrize("os_type,cmd", [
        ("Windows", "cls"),
        ("Linux", "clear"),
        ("Darwin", "clear"),  # macOS
    ])
    def test_clear_terminal_all_platforms(self, temp_dir, os_type, cmd):
        """Test clear_terminal on all platforms using parametrize"""
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value=os_type):
                clear_terminal()
                mock_system.assert_called_once_with(cmd)

# Test coverage - add this to requirements.txt
# pytest-cov

# To run with coverage:
# pytest test_CrawlSS.py --cov=CrawlSS --cov-report=html
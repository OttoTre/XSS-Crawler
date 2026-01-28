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
from CrawlSS import clear_terminal, print_banner, pick_payload, validate_url, load_domains_from_file, PAYLOADS_DIR

class TestCrawlSS:
    @pytest.fixture
    def temp_dir(self):
        test_dir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(test_dir)

        yield test_dir

        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(test_dir)

    def test_clear_terminal_windows(self):
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value='Windows'):
                clear_terminal()
                mock_system.assert_called_once_with('cls')

    def test_clear_terminal_unix(self):
        """Test clear_terminal on Unix/Linux/Mac"""
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value='Linux'):
                clear_terminal()
                mock_system.assert_called_once_with('clear')

    def test_print_banner(self):
        # Just test that it doesn't crash
        print_banner()

    def test_pick_payload_creates_directory(self, temp_dir):
        payloads_path = Path(temp_dir) / PAYLOADS_DIR

        # Ensure directory doesn't exist
        if payloads_path.exists():
            shutil.rmtree(payloads_path)

        with patch('builtins.print'):
            result = pick_payload()
            assert result is None
            assert payloads_path.exists()

    def test_pick_payload_with_files(self, temp_dir):
        payloads_path = Path(temp_dir) / PAYLOADS_DIR
        payloads_path.mkdir(exist_ok=True)

        (payloads_path / 'payload1.txt').write_text('<script>alert(1)</script>')
        (payloads_path / 'payload2.txt').write_text('<img src=x onerror=alert(2)>')
        (payloads_path / 'not_payload.py').write_text('print("not a payload")')

        with patch('builtins.print'):
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
    def test_clear_terminal_all_platforms(self, os_type, cmd):
        """Test clear_terminal on all platforms using parametrize"""
        with patch('os.system') as mock_system:
            with patch('platform.system', return_value=os_type):
                clear_terminal()
                mock_system.assert_called_once_with(cmd)

    def test_validate_url_http(self):
        result = validate_url("http://example.com")
        assert result == "http://example.com"

    def test_validate_url_https(self):
        result = validate_url("https://example.com")
        assert result == "https://example.com"

    def test_validate_url_no_protocol(self):
        result = validate_url("example.com")
        assert result == "https://example.com"

    def test_validate_url_with_whitespace(self):
        result = validate_url("  example.com  ")
        assert result == "https://example.com"

    def test_load_domains_from_file(self, temp_dir):
        domains_file = Path(temp_dir) / "domains.txt"
        domains_file.write_text("example.com\nexample.org\n# comment\n\nexample.net")

        result = load_domains_from_file(str(domains_file))
        assert result is not None
        assert len(result) == 3
        assert "example.com" in result
        assert "example.org" in result
        assert "example.net" in result
        assert "# comment" not in result

    def test_load_domains_from_file_not_found(self):
        result = load_domains_from_file("/nonexistent/file.txt")
        assert result is None

    def test_load_domains_from_file_empty(self, temp_dir):
        """Test loading domains from empty file"""
        domains_file = Path(temp_dir) / "empty.txt"
        domains_file.write_text("")

        result = load_domains_from_file(str(domains_file))
        assert result is not None
        assert len(result) == 0

import unittest
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

class TestCrawlSS(unittest.TestCase):
    """Test cases for CrawlSS.py functions"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test payloads directory
        self.payloads_dir = Path(self.test_dir) / PAYLOADS_DIR
        self.payloads_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('os.system')
    def test_clear_terminal_windows(self, mock_system):
        """Test clear_terminal on Windows"""
        with patch('platform.system', return_value='Windows'):
            clear_terminal()
            mock_system.assert_called_with('cls')

    @patch('os.system')
    def test_clear_terminal_unix(self, mock_system):
        """Test clear_terminal on Unix/Linux/Mac"""
        with patch('platform.system', return_value='Linux'):
            clear_terminal()
            mock_system.assert_called_with('clear')

    @patch('builtins.print')
    def test_print_banner(self, mock_print):
        """Test that print_banner calls print functions"""
        print_banner()
        # Should call print at least twice (banner + author line)
        self.assertGreater(mock_print.call_count, 1)

    def test_pick_payload_creates_directory(self):
        """Test that pick_payload creates payloads directory if it doesn't exist"""
        # Remove the directory first
        if self.payloads_dir.exists():
            shutil.rmtree(self.payloads_dir)

        with patch('builtins.print') as mock_print:
            result = pick_payload()
            self.assertIsNone(result)
            # Check that directory was created
            self.assertTrue(self.payloads_dir.exists())
            # Check that appropriate message was printed
            mock_print.assert_called()

    def test_pick_payload_no_files(self):
        """Test pick_payload when directory exists but no files"""
        with patch('builtins.print') as mock_print:
            result = pick_payload()
            self.assertIsNone(result)
            # Should print that no files found
            mock_print.assert_called()

    def test_pick_payload_with_files(self):
        """Test pick_payload with actual payload files"""
        # Create test files
        (self.payloads_dir / 'test1.txt').write_text('payload1')
        (self.payloads_dir / 'test2.txt').write_text('payload2')
        (self.payloads_dir / 'not_txt.py').write_text('not a payload')

        with patch('builtins.print') as mock_print:
            with patch('builtins.input', return_value='1'):
                result = pick_payload()
                # Should return list of payloads from selected file
                self.assertIsNotNone(result)
                self.assertIsInstance(result, list)
                self.assertIn('payload1', result)  # Should contain payload from file

    def test_payloads_dir_constant(self):
        """Test that PAYLOADS_DIR constant is correct"""
        self.assertEqual(PAYLOADS_DIR, "payloads")

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_pick_payload_permission_error(self, mock_exists, mock_makedirs):
        """Test pick_payload when directory creation fails"""
        mock_makedirs.side_effect = PermissionError("Permission denied")

        with patch('builtins.print') as mock_print:
            with self.assertRaises(PermissionError):
                pick_payload()

if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
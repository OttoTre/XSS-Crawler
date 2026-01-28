# Testing Guide for CrawlSS

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# Run all tests with coverage
python run_tests.py

# Or run directly with pytest (auto-discovers tests/py/)
python -m pytest -v

# Or run unittest version
python tests/ut/test_CrawlSS.py

# Or run pytest version directly
python -m pytest tests/py/test_CrawlSS.py -v
```

## Project Structure

```
XssCrawler/
├── CrawlSS.py              # Main application
├── tests/                  # Test directory
│   ├── py/                 # Pytest tests
│   │   ├── __init__.py
│   │   └── test_CrawlSS.py
│   ├── ut/                 # Unittest tests
│   │   ├── __init__.py
│   │   └── test_CrawlSS.py
│   └── __init__.py
├── run_tests.py            # Test runner script
├── pytest.ini             # pytest configuration
└── TESTING.md             # This file
```

## Test Structure

### tests/py/test_CrawlSS.py (Recommended)
- Modern pytest syntax
- Parametrized tests
- Better error messages
- Coverage reporting

### tests/ut/test_CrawlSS.py (Fallback)
- Standard unittest
- More verbose setup
- Compatible with older Python versions

## What Gets Tested

✅ **clear_terminal()**
- Windows (`cls` command)
- Unix/Linux/Mac (`clear` command)

✅ **print_banner()**
- Banner displays without errors
- Colored output works

✅ **pick_payload()**
- Creates payloads directory if missing
- Lists .txt files only
- Handles empty directories
- Error handling for permissions

## Coverage Report

After running tests, open `htmlcov/index.html` in your browser to see:
- Which lines are tested
- Which lines are missing coverage
- Branch coverage
- Function coverage

## Writing New Tests

### For pytest:
```python
def test_your_function(self, temp_dir):
    # Arrange
    setup_data()

    # Act
    result = your_function()

    # Assert
    assert result == expected
```

### For unittest:
```python
def test_your_function(self):
    # Arrange
    setup_data()

    # Act
    result = your_function()

    # Assert
    self.assertEqual(result, expected)
```

## Test Scenarios Covered

- ✅ Normal operation
- ✅ Edge cases (empty directories, no files)
- ✅ Error conditions (permission denied)
- ✅ Cross-platform compatibility
- ✅ File system operations
- ✅ User interface output

## CI/CD Integration

Add to your GitHub Actions or CI pipeline:
```yaml
- name: Run Tests
  run: python run_tests.py
```
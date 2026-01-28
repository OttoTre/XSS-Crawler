# Testing Guide for crawlss

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
# Run all tests
python -m pytest -v

# Or use the test runner
python run_tests.py
```

### Run Tests with Coverage (optional)
```bash
# Install coverage tools first
pip install pytest-cov

# Then run with coverage
python -m pytest --cov=crawlss --cov-report=html tests/py/
```

## Project Structure

```
XssCrawler/
├── basic_test_website/     # Simple website for manual testing
├── payloads/               # Payloads dir
├── targets/                # Targets dir example
├── tests/                  # Test dir
│   └── py/                 # Pytest dir
├── src/                    # Source dir
│   ├── web/                # Website handler dir
|   |   └── web_handler.py  # Website handler
|   |   └── web_utils.py    # Website utils
│   └── crawlss.py          # Main logic
├── main.py                 # Run script
├── run_tests.py            # Test runner script
├── pytest.ini              # pytest configuration
└── TESTING.md              # This file
```

## Test Structure

### tests/py/test_crawlss.py
- Modern pytest syntax
- Parametrized tests
- Better error messages
- Coverage reporting
- 15 comprehensive tests
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
def test_your_function(temp_dir):
    # Arrange
    setup_data()

    # Act
    result = your_function()

    # Assert
    assert result == expected
```

## Test Scenarios Covered

- ✅ Terminal clearing (Windows, Linux, macOS)
- ✅ Banner display with colored output
- ✅ Payload file selection and loading
- ✅ URL validation and normalization
- ✅ Domain file loading
- ✅ Edge cases (empty files, missing files, whitespace)
- ✅ Error handling and user input validation
- ✅ Cross-platform compatibility

## CI/CD Integration

Add to your GitHub Actions or CI pipeline:
```yaml
- name: Run Tests
  run: python run_tests.py
```
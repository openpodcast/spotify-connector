# Tests for SpotifyConnector

This directory contains all tests for the SpotifyConnector project.

## Structure

- `test_connection_handling.py` - Tests for network error handling and retry logic
- `__init__.py` - Makes this directory a Python package

## Running Tests

From the project root directory:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_connection_handling.py

# Run with verbose output
python -m pytest tests/ -v

# Run with coverage (if pytest-cov is installed)
python -m pytest tests/ --cov=spotifyconnector
```

## Test Categories

### Connection Handling Tests (`test_connection_handling.py`)
- Network error retry logic
- Authentication handling during network failures
- Exponential backoff behavior
- Clean exit behavior after exhausting retries

## Adding New Tests

When adding new test files:
1. Name them with the `test_` prefix (e.g., `test_authentication.py`)
2. Use descriptive class names (e.g., `TestAuthentication`)
3. Use descriptive method names (e.g., `test_bearer_token_refresh`)
4. Include docstrings explaining what each test verifies

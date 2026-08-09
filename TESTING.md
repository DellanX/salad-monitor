# Testing Guide

This document describes the testing structure and conventions for the Salad Monitor project.

For manual testing procedures (API testing, Docker testing, etc.), see [MANUAL_TESTING.md](MANUAL_TESTING.md).

---

## 📁 Test Directory Structure

**The test directory structure mirrors the source code structure.**

This convention makes it easy to find tests for any given source file:

```
src/
├── __init__.py
├── config.py           → tests/test_config.py
├── state.py            → tests/test_state.py
├── log_parser.py       → tests/test_log_parser.py
├── log_watcher.py      → tests/test_log_watcher.py
├── monitor.py          → tests/test_monitor.py
├── app.py              → tests/test_app.py
└── api/
    ├── __init__.py
    └── routes.py       → tests/api/test_routes.py
```

### Naming Convention

- Source file: `src/module_name.py`
- Test file: `tests/test_module_name.py`
- Subdirectories in `src/` are mirrored in `tests/`

## 🧪 Test Framework

We use **pytest** as our test framework with the following plugins:

- `pytest` - Core testing framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `httpx` - HTTP client for API testing (used by FastAPI TestClient)

## 🏃 Running Tests

### In DevContainer (Recommended)

Since the host system doesn't have Python installed, use the devcontainer:

1. Open the project in VS Code
2. Click "Reopen in Container" when prompted (or use Command Palette: "Remote-Containers: Reopen in Container")
3. Once inside the container, run tests:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_config.py

# Run specific test class
pytest tests/test_state.py::TestState

# Run specific test
pytest tests/test_state.py::TestState::test_reset_state

# Run tests with specific marker
pytest -m unit
```

### Test Markers

Tests are marked with the following markers (defined in `pytest.ini`):

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (may require external resources)
- `@pytest.mark.slow` - Tests that take a long time to run

## 📊 Coverage

Coverage reports are generated in two formats:

1. **Terminal output** - Shows coverage percentages and missing lines
2. **HTML report** - Detailed coverage report in `htmlcov/index.html`

To view the HTML report:
```bash
pytest --cov=src --cov-report=html
# Then open htmlcov/index.html in a browser
```

## ✍️ Writing Tests

### Test Structure

Each test file should:

1. Import necessary modules and fixtures
2. Group related tests in classes (named `TestXxx`)
3. Use descriptive test function names starting with `test_`
4. Include docstrings explaining what is being tested

Example:

```python
"""Unit tests for src/my_module.py"""

import pytest
from src import my_module


@pytest.mark.unit
class TestMyModule:
    """Test my module functionality."""

    def test_basic_function(self):
        """Test that basic_function returns expected value."""
        result = my_module.basic_function()
        assert result == expected_value
```

### Test Fixtures

Common fixtures are defined in `conftest.py` files (to be created as needed).

For API testing, we provide:
- `client` - FastAPI TestClient
- `reset_state` - Resets global state before each test

### Mocking

Use `unittest.mock` for mocking:

```python
from unittest.mock import patch, MagicMock

@patch('src.module.external_function')
def test_with_mock(mock_func):
    mock_func.return_value = "mocked value"
    # test code here
```

### State Management

Tests that use global state should reset it in `setup_method`:

```python
def setup_method(self):
    """Reset state before each test."""
    state.state["salad_pending"] = False
    state.state["salad_active"] = False
    # ... reset other state variables
```

## 🎯 Test Coverage Goals

- **Unit Tests**: All pure functions and state management
- **API Tests**: All endpoints and error cases
- **Integration Tests**: End-to-end workflows (to be added)

## 🔧 CI/CD Integration

Tests should be run in CI/CD pipelines before merging:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: pytest --cov=src --cov-report=xml
```

## 📝 Adding New Tests

When adding a new source file:

1. Create the corresponding test file in `tests/` mirroring the source structure
2. Add the `@pytest.mark.unit` marker to unit tests
3. Include tests for:
   - Normal operation
   - Edge cases
   - Error conditions
   - State changes (if applicable)
4. Run tests to ensure they pass
5. Check coverage to ensure the new code is tested

## 🐛 Debugging Tests

To debug a failing test:

```bash
# Run with verbose output
pytest -v tests/test_module.py

# Run with print statements visible
pytest -s tests/test_module.py

# Run with debugger on failure
pytest --pdb tests/test_module.py

# Show local variables on failure
pytest -l tests/test_module.py
```

## 📚 Best Practices

1. **Keep tests isolated** - Each test should be independent
2. **Test one thing** - Each test should verify one behavior
3. **Use descriptive names** - Test names should explain what is being tested
4. **Mock external dependencies** - Don't rely on files, network, or databases
5. **Reset state** - Clean up after tests to avoid side effects
6. **Fast tests** - Unit tests should run in milliseconds
7. **Readable assertions** - Use clear assertion messages when needed

## 🔍 Future Improvements

- [ ] Add integration tests for log monitoring workflow
- [ ] Add tests for `log_watcher.py`
- [ ] Add tests for `monitor.py`
- [ ] Add performance/benchmark tests
- [ ] Add E2E tests with real log files
- [ ] Set up automated coverage reporting
- [ ] Add mutation testing

---

For questions about testing, see the test files themselves for examples, or refer to:
- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing documentation](https://fastapi.tiangolo.com/tutorial/testing/)

# Test Directory

This directory contains all tests for the Salad Monitor project.

## Structure

**The test directory structure mirrors the source code structure.**

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_config.py       # Tests for src/config.py
├── test_state.py        # Tests for src/state.py
├── test_log_parser.py   # Tests for src/log_parser.py
└── api/
    ├── __init__.py
    └── test_routes.py   # Tests for src/api/routes.py
```

## Convention

For each source file `src/path/to/module.py`, the corresponding test file is `tests/path/to/test_module.py`.

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

For more details, see [TESTING.md](../TESTING.md) in the project root.

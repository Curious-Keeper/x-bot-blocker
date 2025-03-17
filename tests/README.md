# Test Directory Structure

This directory contains all the tests for the X-Bot-Blocker project. The tests are organized into different categories to maintain clarity and separation of concerns.

## Directory Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests between components
├── data/             # Test data files
├── fixtures/         # Test fixtures and mock data
├── conftest.py       # Shared pytest fixtures
└── README.md         # This file
```

## Test Categories

### Unit Tests
Located in `tests/unit/`, these tests verify the functionality of individual components in isolation. Each test file corresponds to a specific module:

- `test_reporting.py`: Tests for the reporting system
- `test_monitoring.py`: Tests for the monitoring system
- `test_progress.py`: Tests for the progress tracking system

### Integration Tests
Located in `tests/integration/`, these tests verify the interaction between different components of the system.

### Test Data
Located in `tests/data/`, this directory contains test data files used by the tests.

### Fixtures
Located in `tests/fixtures/`, this directory contains shared test fixtures and mock data.

## Running Tests

To run all tests:
```bash
pytest
```

To run tests with verbose output:
```bash
pytest -v
```

To run a specific test file:
```bash
pytest tests/unit/test_reporting.py
```

To run a specific test:
```bash
pytest tests/unit/test_reporting.py::test_weekly_report_generation
```

## Test Configuration

Test configuration is managed through `conftest.py`, which provides shared fixtures for:

- Configuration management
- Test data generation
- Directory cleanup
- Mock data and objects

## Writing Tests

When writing new tests:

1. Place unit tests in the appropriate file under `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Use the provided fixtures from `conftest.py`
4. Follow the existing test structure and naming conventions
5. Include docstrings explaining the purpose of each test
6. Clean up any test data or state after the test completes 
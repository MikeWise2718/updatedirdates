# Testing Guide for UpdateDirDates

This document describes how to run tests, check code coverage, and understand the current testing status.

## Current Test Coverage

**Current coverage: 98.19%** ✅ (Target: 80%+)

### Coverage Breakdown
- `src/updatedirdates/__init__.py`: 100%
- `src/updatedirdates/main.py`: 95%  
- `src/updatedirdates/updater.py`: 100%
- **Total**: 98.19%

## Running Tests

### Prerequisites

1. Ensure you're in the project directory and virtual environment is activated:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies (if not already done):
   ```bash
   pip install -r requirements-dev.txt
   ```

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_main.py
python -m pytest tests/test_updater.py

# Run specific test
python -m pytest tests/test_main.py::TestParser::test_create_parser_basic
```

### Coverage Testing

```bash
# Run tests with coverage report
python -m pytest --cov=src/updatedirdates --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=src/updatedirdates --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html  # On macOS
start htmlcov/index.html  # On Windows
xdg-open htmlcov/index.html  # On Linux
```

### Coverage Configuration

Coverage settings are configured in `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src/updatedirdates --cov-report=html --cov-report=term-missing --cov-fail-under=80"
```

## Test Structure

### Test Files

- `tests/test_main.py`: Tests for the main module and CLI interface
- `tests/test_updater.py`: Tests for the core DirectoryUpdater functionality

### Test Categories

#### Main Module Tests (`test_main.py`)
- **Parser Tests**: Command-line argument parsing
- **Colored Output Tests**: Terminal color output functions
- **Directory Validation Tests**: Path validation logic
- **Main Function Tests**: Integration tests for the main entry point
- **Colorama Setup Tests**: Color initialization

#### Updater Module Tests (`test_updater.py`)
- **DirectoryUpdater Tests**: Class initialization and basic functionality
- **Modification Time Tests**: File and directory timestamp logic
- **Update Logic Tests**: Directory update decision making
- **Date Update Tests**: Actual timestamp modification
- **Directory Processing Tests**: Recursive directory traversal
- **Statistics Tests**: Output formatting and reporting

## Test Coverage Goals

### Lines Not Covered
Current uncovered lines (3 total out of 166):

1. `src/updatedirdates/main.py`: Lines 100-101, 156

These are mostly edge cases or platform-specific code paths that are difficult to test reliably.

### Coverage Targets
- **Minimum required**: 80%
- **Current achievement**: 98.19%
- **Target for new code**: 95%+

## Running Quality Checks

### Code Formatting
```bash
# Check formatting
python -m black --check src/ tests/

# Auto-format code
python -m black src/ tests/
```

### Linting
```bash
# Run flake8 linter
python -m flake8 src/ tests/

# Run mypy type checker
python -m mypy src/
```

### All Quality Checks Together
```bash
# Run all quality checks
python -m black --check src/ tests/ && \
python -m flake8 src/ tests/ && \
python -m mypy src/ && \
python -m pytest --cov=src/updatedirdates --cov-fail-under=80
```

## Writing New Tests

### Test Guidelines

1. **File naming**: Test files should be named `test_*.py`
2. **Class naming**: Test classes should start with `Test`
3. **Method naming**: Test methods should start with `test_`
4. **Fixtures**: Use pytest fixtures for common setup
5. **Mocking**: Use unittest.mock for external dependencies
6. **Coverage**: Aim for 95%+ coverage on new code

### Example Test Structure
```python
import pytest
from unittest.mock import Mock, patch
from updatedirdates.main import some_function

class TestSomeFeature:
    """Test some feature functionality."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = some_function("input")
        assert result == "expected"
    
    def test_error_handling(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            some_function("invalid_input")
    
    @patch('some.external.dependency')
    def test_with_mocking(self, mock_dep):
        """Test with mocked dependencies."""
        mock_dep.return_value = "mocked_result"
        result = some_function("input")
        assert result == "expected"
        mock_dep.assert_called_once()
```

## Continuous Integration

### GitHub Actions (if applicable)
The project is set up to run tests automatically on:
- Pull requests
- Pushes to main branch
- Coverage reports uploaded to coverage services

### Pre-commit Hooks
Consider setting up pre-commit hooks to run tests and quality checks:
```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Debugging Test Failures

### Common Issues
1. **Import errors**: Ensure package is installed in development mode (`pip install -e .`)
2. **Timing issues**: Use proper sleep/wait mechanisms for file system operations
3. **Platform differences**: Use `pathlib.Path` for cross-platform compatibility
4. **Temporary files**: Use pytest's `tmp_path` fixture for test isolation

### Debugging Commands
```bash
# Run single test with verbose output
python -m pytest tests/test_main.py::TestParser::test_create_parser_basic -vv

# Run with pdb debugger on failure
python -m pytest --pdb tests/test_main.py

# Show print statements
python -m pytest -s tests/test_main.py
```

## Performance Considerations

Tests are designed to be fast and reliable:
- Use `tmp_path` fixture for isolated file operations
- Mock external dependencies where possible
- Keep test data small and focused
- Parallel execution ready (if using pytest-xdist)

## Contributing Tests

When contributing new features:

1. **Write tests first** (Test-Driven Development)
2. **Maintain coverage** above 80% (preferably 95%+)
3. **Test error conditions** and edge cases
4. **Use descriptive test names** and docstrings
5. **Keep tests independent** and isolated

## Test Maintenance

### Regular Tasks
- Review and update tests when adding features
- Check coverage reports for gaps
- Update test dependencies regularly
- Refactor tests when code structure changes

### Coverage Monitoring
- Monitor coverage trends over time
- Investigate coverage drops
- Add tests for uncovered code paths
- Remove tests for removed functionality

---

Last updated: August 2025
Current coverage: 98.19%
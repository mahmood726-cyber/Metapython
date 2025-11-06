# MetaPython Test Suite

Comprehensive test suite for the MetaPython meta-analysis library.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Shared pytest fixtures
├── test_imports.py             # Import and availability tests
├── test_basic_functionality.py # Core functionality tests
├── test_data_structures.py     # Data structure validation tests
├── test_statistical_methods.py # Statistical calculation tests
├── test_numpy_operations.py    # NumPy operation tests
└── test_pandas_operations.py   # Pandas operation tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_imports.py
```

### Run tests with coverage
```bash
pytest --cov=. --cov-report=html
```

### Run tests verbosely
```bash
pytest -v
```

### Run tests with output
```bash
pytest -s
```

### Run specific test function
```bash
pytest tests/test_imports.py::test_metapython_import
```

## Test Categories

### Import Tests (`test_imports.py`)
- Module import verification
- Dependency availability checks
- Version compatibility tests
- Optional dependency graceful degradation

### Basic Functionality Tests (`test_basic_functionality.py`)
- Data class creation and validation
- Configuration object testing
- Error class verification
- Core class existence checks

### Data Structure Tests (`test_data_structures.py`)
- Fixture validation
- Data validation rules
- DataFrame operations
- NumPy array operations

### Statistical Methods Tests (`test_statistical_methods.py`)
- Distribution calculations (normal, t, chi-square)
- Heterogeneity metrics (I², Q statistic)
- Effect size pooling
- Confidence interval calculations

### NumPy Operations Tests (`test_numpy_operations.py`)
- Array creation and manipulation
- Statistical operations
- Mathematical functions
- Matrix operations

### Pandas Operations Tests (`test_pandas_operations.py`)
- DataFrame creation and manipulation
- Filtering and grouping
- Merging and concatenation
- Statistical summaries

## Fixtures

Shared fixtures are defined in `conftest.py`:

- `sample_meta_data`: Sample meta-analysis data (effect sizes, standard errors)
- `sample_binary_data`: Sample binary outcome data (2x2 tables)
- `sample_continuous_data`: Sample continuous outcome data (means, SDs)
- `random_seed`: Fixed random seed for reproducibility

## Coverage

To generate coverage reports:

```bash
# Terminal report
pytest --cov=. --cov-report=term

# HTML report
pytest --cov=. --cov-report=html
open htmlcov/index.html

# XML report (for CI/CD)
pytest --cov=. --cov-report=xml
```

## Continuous Integration

These tests are automatically run in GitHub Actions workflows:
- Python CI/CD workflow tests across Python 3.9-3.12
- Tests run on Ubuntu, Windows, and macOS
- Coverage reports generated automatically

## Writing New Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test
```python
def test_example():
    \"\"\"Test description.\"\"\"
    # Arrange
    data = [1, 2, 3]

    # Act
    result = sum(data)

    # Assert
    assert result == 6
```

### Using Fixtures
```python
def test_with_fixture(sample_meta_data):
    \"\"\"Test using a fixture.\"\"\"
    assert len(sample_meta_data) > 0
    assert 'effect_size' in sample_meta_data.columns
```

### Testing Exceptions
```python
def test_exception():
    \"\"\"Test that exception is raised.\"\"\"
    with pytest.raises(ValueError):
        raise ValueError("Test error")
```

## Test Markers

Use markers to categorize tests:

```python
@pytest.mark.slow
def test_slow_operation():
    \"\"\"Test that takes a long time.\"\"\"
    pass

@pytest.mark.requires_r
def test_r_integration():
    \"\"\"Test that requires R.\"\"\"
    pass
```

Run tests by marker:
```bash
# Run only fast tests (exclude slow)
pytest -m "not slow"

# Run only integration tests
pytest -m integration
```

## Troubleshooting

### Import Errors
If you get import errors, ensure the parent directory is in your Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Missing Dependencies
Install test dependencies:
```bash
pip install -r requirements-test.txt
```

### Test Discovery Issues
Ensure pytest can find your tests:
```bash
pytest --collect-only
```

## Contributing

When adding new features:
1. Write tests first (TDD approach)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov=.`
4. Update this README if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

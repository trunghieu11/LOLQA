# 🧪 Testing Guide

> Complete guide for testing the LOLQA microservices application

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Test Structure](#test-structure)
3. [Running Tests](#running-tests)
4. [Writing Tests](#writing-tests)
5. [Test Coverage](#test-coverage)
6. [Test Categories](#test-categories)
7. [Mocking & Fixtures](#mocking--fixtures)
8. [Continuous Integration](#continuous-integration)
9. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Install Test Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies
pip install -r requirements-test.txt
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_utils.py

# Run specific test
pytest tests/test_utils.py::TestFormatDocuments::test_format_documents_basic
```

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures and configuration
├── import_helpers.py              # Helper for importing service modules
│
├── # Core Component Tests
├── test_utils.py                  # Unit tests for utilities
├── test_config.py                 # Unit tests for configuration
├── test_data_collectors.py        # Unit tests for data collectors
├── test_rag_system.py            # Unit tests for RAG system
├── test_workflow.py              # Unit tests for workflow
│
├── # Microservices Tests
├── test_llm_service.py           # LLM Service API tests
├── test_rag_service.py           # RAG Service API tests
├── test_data_pipeline_service.py  # Data Pipeline Service tests
├── test_auth_service.py          # Auth Service API tests
│
├── # Infrastructure Tests
├── test_redis_client.py          # Redis client tests
├── test_db_client.py             # PostgreSQL client tests
├── test_metrics.py               # Prometheus metrics tests
│
├── # Integration Tests
├── test_integration.py           # End-to-end integration tests
├── test_microservices_integration.py  # Service-to-service tests
│
└── data/                         # Test data files
    └── sample_data.json
```

## 🏷️ Test Categories

### 1. **Unit Tests**
Test individual components in isolation:
- `test_utils.py`: Helper functions
- `test_config.py`: Configuration classes
- `test_data_collectors.py`: Data collection classes
- `test_rag_system.py`: RAG system methods
- `test_workflow.py`: LangGraph workflow
- `test_redis_client.py`: Redis operations
- `test_db_client.py`: Database operations
- `test_metrics.py`: Metrics collection

### 2. **Service Tests**
Test microservice API endpoints:
- `test_llm_service.py`: LLM Service endpoints
- `test_rag_service.py`: RAG Service endpoints
- `test_data_pipeline_service.py`: Data Pipeline Service endpoints
- `test_auth_service.py`: Auth Service endpoints

### 3. **Integration Tests**
Test multiple components working together:
- `test_integration.py`: End-to-end workflows
- `test_microservices_integration.py`: Service-to-service communication

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with very verbose output (show print statements)
pytest -vv -s

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests matching pattern
pytest -k "test_format"

# Run failed tests from last run
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Running Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Slow tests only
pytest -m slow

# Tests that require API keys
pytest -m requires_api

# Tests that require database
pytest -m requires_db
```

### Coverage

```bash
# Run with coverage
pytest --cov=src

# Generate HTML coverage report
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4
```

---

## ✍️ Writing Tests

### Test Structure

```python
"""
Description of test module
"""
import pytest
from unittest.mock import Mock, patch
from src.module import ClassToTest


class TestClassName:
    """Tests for ClassName"""
    
    def test_method_name(self):
        """Test description"""
        # Arrange
        instance = ClassToTest()
        
        # Act
        result = instance.method()
        
        # Assert
        assert result == expected_value
```

### Using Fixtures

Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_fixture(sample_documents):
    """Test using fixture"""
    assert len(sample_documents) > 0
```

### Mocking

#### Mock Functions

```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependency"""
    mock_function = Mock(return_value="mocked result")
    
    result = mock_function()
    
    assert result == "mocked result"
    mock_function.assert_called_once()
```

#### Patch Dependencies

```python
@patch('src.module.dependency')
def test_with_patch(mock_dependency):
    """Test with patched dependency"""
    mock_dependency.return_value = "patched"
    
    # Your test code
```

### Test Markers

Mark tests for categorization:

```python
@pytest.mark.unit
def test_unit_test():
    """Unit test"""
    pass

@pytest.mark.integration
def test_integration_test():
    """Integration test"""
    pass

@pytest.mark.slow
def test_slow_test():
    """Slow running test"""
    pass

@pytest.mark.requires_api
def test_needs_api():
    """Test that requires API key"""
    pass
```

### Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("input,expected", [
    ("test1", "expected1"),
    ("test2", "expected2"),
    ("test3", "expected3"),
])
def test_multiple_inputs(input, expected):
    """Test with multiple inputs"""
    assert process(input) == expected
```

### Testing Exceptions

```python
def test_raises_exception():
    """Test that exception is raised"""
    with pytest.raises(ValueError, match="error message"):
        raise ValueError("error message")
```

---

## 📊 Test Coverage

### Coverage Goals

- **Overall**: 70%+ coverage
- **Core modules**: 80%+ coverage
- **Critical paths**: 90%+ coverage

### Check Coverage

```bash
# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html

# Fail if coverage below 70%
pytest --cov=src --cov-fail-under=70
```

### Coverage Reports

After running with `--cov-report=html`, open `htmlcov/index.html` to see:
- Overall coverage percentage
- Coverage by file
- Line-by-line coverage
- Uncovered lines

---

## 🔄 Continuous Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📝 Best Practices

### 1. **Test Naming**
- Use descriptive names: `test_user_login_with_valid_credentials`
- Follow pattern: `test_<what>_<condition>_<expected>`

### 2. **Test Independence**
- Tests should not depend on each other
- Use fixtures for setup
- Clean up after tests

### 3. **AAA Pattern**
```python
def test_example():
    # Arrange: Set up test data
    data = create_test_data()
    
    # Act: Execute the code being tested
    result = process(data)
    
    # Assert: Verify the result
    assert result == expected
```

### 4. **Mock External Dependencies**
- Don't make real API calls
- Don't access real databases (use test DBs)
- Mock time-dependent operations

### 5. **Test Edge Cases**
- Empty inputs
- Null values
- Maximum values
- Invalid inputs
- Error conditions

---

## 🐛 Debugging Tests

### Run Single Test with Output

```bash
pytest tests/test_utils.py::test_specific -vv -s
```

### Use Debugger

```python
def test_with_debugger():
    import pdb; pdb.set_trace()
    # Test code
```

### Print Variables

```bash
# Run with print statements visible
pytest -s
```

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

## 🧪 Testing Microservices

### Service-Specific Testing

#### Testing LLM Service

```python
from fastapi.testclient import TestClient
from services.llm_service.main import app

def test_llm_service_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

#### Testing RAG Service

```python
from fastapi.testclient import TestClient
from services.rag_service.main import app

def test_rag_query():
    client = TestClient(app)
    response = client.post("/query", json={"question": "test"})
    assert response.status_code == 200
```

#### Testing with Mocks

```python
from unittest.mock import patch, MagicMock

@patch('services.llm_service.main.llm_client')
def test_with_mocked_llm(mock_llm):
    mock_llm.chat = MagicMock(return_value="mocked response")
    # Test code
```

### Common Fixtures

Available in `conftest.py`:
- `mock_redis_client` - Mock Redis client
- `mock_db_client` - Mock PostgreSQL client
- `mock_llm_service_response` - Mock LLM responses
- `mock_rag_service_response` - Mock RAG responses
- `mock_jwt_token` - Mock JWT tokens
- `sample_documents` - Sample documents for testing

### Testing Async Services

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/endpoint")
        assert response.status_code == 200
```

### Coverage for Microservices

```bash
# Test all services
pytest --cov=src --cov=shared --cov=services --cov-report=html

# Current coverage: 43%+ (target: 40% minimum)
```

---

## 🆘 Troubleshooting

### Import Errors

```bash
# Ensure you're in the project root
cd /path/to/LOLQA

# Ensure venv is activated
source venv/bin/activate

# Install in development mode
pip install -e .
```

### Service Module Import Issues

For services with hyphenated names (e.g., `auth-service`):
```python
from tests.import_helpers import import_service_module
auth_module = import_service_module("auth-service", "main")
```

### Async Test Issues

Use `pytest-asyncio`:
```python
@pytest.mark.asyncio
async def test_async():
    result = await async_function()
    assert result is not None
```

### Database Connection Issues

Use mocks for database operations in unit tests:
```python
@patch('shared.common.db_client.get_db_client')
def test_with_mock_db(mock_get_db):
    mock_db = MagicMock()
    mock_get_db.return_value = mock_db
    # Test code
```

### Slow Tests

```bash
# Show slowest 10 tests
pytest --durations=10
```

### Test Failures

```bash
# Show full diff
pytest --tb=long

# Show only failed test output
pytest --tb=short
```

---

Made with ⚔️ for quality code!


# Testing Guide

This guide explains how to run tests for the LOLQA microservices.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_redis_client.py           # Redis client tests
├── test_db_client.py              # Database client tests
├── test_llm_service.py            # LLM Service tests
├── test_rag_service.py            # RAG Service tests
├── test_data_pipeline_service.py  # Data Pipeline Service tests
├── test_auth_service.py           # Auth Service tests
├── test_microservices_integration.py  # Integration tests
├── test_metrics.py                # Metrics tests
└── TESTING_GUIDE.md               # This file
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov=shared --cov=services --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/test_llm_service.py
```

### Run Specific Test

```bash
pytest tests/test_llm_service.py::TestLLMServiceAPI::test_health_check
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Output

```bash
pytest -s
```

## Test Categories

### Unit Tests

- **test_redis_client.py**: Tests for Redis caching and job queues
- **test_db_client.py**: Tests for PostgreSQL database operations
- **test_metrics.py**: Tests for Prometheus metrics
- **test_auth_service.py**: Tests for authentication utilities

### Service Tests

- **test_llm_service.py**: Tests for LLM Service API endpoints
- **test_rag_service.py**: Tests for RAG Service API endpoints
- **test_data_pipeline_service.py**: Tests for Data Pipeline Service
- **test_auth_service.py**: Tests for Auth Service API endpoints

### Integration Tests

- **test_microservices_integration.py**: Tests for service-to-service communication

## Test Fixtures

Common fixtures available in `conftest.py`:

- `mock_redis_client`: Mock Redis client
- `mock_db_client`: Mock database client
- `mock_llm_service_response`: Mock LLM service response
- `mock_rag_service_response`: Mock RAG service response
- `mock_jwt_token`: Mock JWT token
- `sample_documents`: Sample documents for testing
- `mock_vectorstore`: Mock ChromaDB vector store

## Writing New Tests

### Example: Testing a Service Endpoint

```python
from fastapi.testclient import TestClient
from services.llm_service.main import app

def test_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
```

### Example: Testing with Mocks

```python
from unittest.mock import patch, MagicMock

@patch('services.llm_service.main.llm_client')
def test_chat(mock_llm_client):
    mock_llm_client.chat = AsyncMock(return_value="Test response")
    # Test code here
```

### Example: Testing Async Functions

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Test Coverage Goals

- **Unit Tests**: > 80% coverage
- **Service Tests**: > 70% coverage
- **Integration Tests**: Critical paths covered

## Continuous Integration

Tests should be run:
- Before committing code
- In CI/CD pipeline
- Before deploying to production

## Mocking External Services

When testing, external services should be mocked:
- OpenAI API calls
- Redis connections
- PostgreSQL connections
- HTTP requests between services

## Running Tests in Docker

```bash
docker-compose -f docker-compose.test.yml up --build
```

## Troubleshooting

### Import Errors

Make sure paths are set correctly:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Async Test Issues

Use `pytest-asyncio`:
```python
@pytest.mark.asyncio
async def test_async():
    ...
```

### Database Connection Issues

Use mocks for database operations in unit tests.


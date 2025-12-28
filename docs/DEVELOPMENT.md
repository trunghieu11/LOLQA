# 💻 Development Guide

> Complete guide for developers working on the LOLQA project

---

## 📋 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Code Standards](#code-standards)
6. [Adding New Features](#adding-new-features)
7. [Debugging](#debugging)
8. [Contributing](#contributing)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Git
- OpenAI API key

### Initial Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd LOLQA
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Run tests**:
```bash
pytest
```

---

## 🛠️ Development Setup

### Local Development

#### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f [service-name]

# Stop services
docker-compose down
```

#### Option 2: Individual Services

Run each service separately for faster iteration:

```bash
# Terminal 1: LLM Service
cd services/llm-service
python main.py

# Terminal 2: RAG Service
cd services/rag-service
python main.py

# Terminal 3: Data Pipeline Service
cd services/data-pipeline-service
python main.py

# Terminal 4: UI Service
cd services/ui-service
streamlit run main.py
```

### Development Tools

#### Code Formatting

```bash
# Format code with black
black src tests services shared

# Check formatting
black --check src tests services shared
```

#### Import Sorting

```bash
# Sort imports with isort
isort src tests services shared

# Check import sorting
isort --check-only src tests services shared
```

#### Linting

```bash
# Lint with flake8
flake8 src tests services shared --max-line-length=120 --ignore=E203,W503
```

#### Type Checking

```bash
# Type check with mypy
mypy src services shared
```

---

## 📁 Project Structure

```
LOLQA/
├── services/              # Microservices
│   ├── llm-service/       # LLM inference service
│   ├── rag-service/       # RAG query service
│   ├── data-pipeline-service/  # Data ingestion service
│   ├── auth-service/      # Authentication service
│   └── ui-service/        # Streamlit UI
│
├── shared/                # Shared code
│   └── common/           # Common utilities
│       ├── config.py     # Configuration
│       ├── db_client.py  # PostgreSQL client
│       ├── redis_client.py # Redis client
│       ├── metrics.py    # Prometheus metrics
│       └── models.py     # Pydantic models
│
├── src/                   # Legacy monolithic code
│   ├── core/             # RAG system & workflow
│   ├── data/             # Data collection
│   ├── config/           # Configuration
│   └── utils/            # Utilities
│
├── tests/                 # Test suite
│   ├── conftest.py       # Shared fixtures
│   ├── test_*.py         # Test files
│   └── import_helpers.py  # Import helpers
│
├── docs/                  # Documentation
│   ├── ARCHITECTURE.md   # Architecture guide
│   ├── DEPLOYMENT.md     # Deployment guide
│   ├── TESTING.md        # Testing guide
│   └── ...
│
├── kubernetes/           # Kubernetes manifests
├── monitoring/           # Prometheus & Grafana configs
├── scripts/              # Utility scripts
└── docker-compose.yml    # Local development orchestration
```

---

## 🔄 Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following [Code Standards](#code-standards)
- Add tests for new features
- Update documentation

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_your_feature.py

# Run with coverage
pytest --cov=src --cov=shared --cov=services
```

### 4. Format and Lint

```bash
# Format code
black src tests services shared
isort src tests services shared

# Lint
flake8 src tests services shared
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: Add your feature description"
```

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
# Create pull request on GitHub
```

---

## 📝 Code Standards

### Python Style Guide

Follow [PEP 8](https://pep8.org/) with these modifications:
- Line length: 120 characters
- Use type hints for all functions
- Use docstrings for all classes and functions

### Type Hints

```python
from typing import Optional, List, Dict

def process_data(
    data: List[Dict[str, str]],
    limit: Optional[int] = None
) -> Dict[str, int]:
    """Process data and return statistics."""
    pass
```

### Docstrings

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input is provided
    """
    pass
```

### Naming Conventions

- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### File Organization

```python
# 1. Standard library imports
import os
from typing import List

# 2. Third-party imports
from fastapi import FastAPI
from pydantic import BaseModel

# 3. Local imports
from shared.common import config
from services.llm_service import llm_client
```

---

## ✨ Adding New Features

### Adding a New Service

1. **Create service directory**:
```bash
mkdir -p services/new-service
cd services/new-service
```

2. **Create service files**:
- `main.py` - FastAPI application
- `requirements.txt` - Dependencies
- `Dockerfile` - Container definition

3. **Add to docker-compose.yml**:
```yaml
new-service:
  build: ./services/new-service
  ports:
    - "8005:8000"
  environment:
    - ENV_VAR=value
```

4. **Add tests**:
```bash
# Create test file
touch tests/test_new_service.py
```

5. **Update documentation**:
- Add to `docs/ARCHITECTURE.md`
- Update `docs/DEPLOYMENT.md` if needed

### Adding a New Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class RequestModel(BaseModel):
    field: str

@app.post("/endpoint")
async def new_endpoint(request: RequestModel):
    """Endpoint description."""
    try:
        # Implementation
        return {"result": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Adding Tests

```python
from fastapi.testclient import TestClient
from services.new_service.main import app

def test_new_endpoint():
    client = TestClient(app)
    response = client.post("/endpoint", json={"field": "value"})
    assert response.status_code == 200
    assert response.json()["result"] == "success"
```

---

## 🐛 Debugging

### Local Debugging

#### Using Print Statements

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

#### Using Debugger

```python
import pdb

def function_to_debug():
    pdb.set_trace()  # Breakpoint
    # Your code
```

#### VS Code Debugging

Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```

### Docker Debugging

```bash
# View service logs
docker-compose logs -f [service-name]

# Execute command in container
docker-compose exec [service-name] /bin/bash

# Inspect container
docker-compose exec [service-name] python -c "import sys; print(sys.path)"
```

### Service Health Checks

```bash
# Check service health
curl http://localhost:8001/health  # LLM Service
curl http://localhost:8002/health  # RAG Service
curl http://localhost:8003/health  # Data Pipeline Service
curl http://localhost:8004/health  # Auth Service
```

---

## 🤝 Contributing

### Before Submitting PR

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Coverage maintained or improved

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Code formatting
refactor: Code refactoring
test: Add tests
chore: Maintenance tasks
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Coverage maintained

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No linting errors
```

---

## 📚 Additional Resources

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Testing Guide](TESTING.md) - Testing practices
- [Deployment Guide](DEPLOYMENT.md) - Deployment instructions
- [Project Guide](PROJECT_GUIDE.md) - Complete project overview

---

Made with ⚔️ for League of Legends fans and AI enthusiasts!


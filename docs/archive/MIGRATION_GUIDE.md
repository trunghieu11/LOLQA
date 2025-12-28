# 🔄 Migration Guide: Monolithic to Microservices

This guide explains how to migrate from the monolithic LOLQA application to the microservices architecture.

## 📋 Overview

The monolithic application has been split into 4 microservices:
- **LLM Service** - Extracted LLM and embedding logic
- **RAG Service** - Extracted RAG system and LangGraph workflow
- **Data Pipeline Service** - Extracted data collection and chunking
- **UI Service** - Refactored Streamlit app to call RAG Service

## 🔄 Migration Steps

### Step 1: Backup Current Application

```bash
# Backup your current application
cp -r . ../LOLQA-backup
```

### Step 2: Review New Structure

The new structure:
```
LOLQA/
├── services/
│   ├── llm-service/          # LLM Service
│   ├── rag-service/          # RAG Service
│   ├── data-pipeline-service/ # Data Pipeline Service
│   └── ui-service/           # UI Service
├── shared/
│   └── common/               # Shared utilities
├── src/                      # Original code (still used by services)
├── docker-compose.yml        # Full stack orchestration
└── .env                      # Environment variables
```

### Step 3: Update Environment Variables

Create/update `.env` file with service-specific variables:

```env
# OpenAI (required)
OPENAI_API_KEY=your_key_here

# LLM Service
LLM_BACKEND=openai  # or "vllm"
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# RAG Service
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_RETRIEVAL_K=3

# Data Sources
USE_DATA_DRAGON=true
USE_WEB_SCRAPER=true
USE_RIOT_API=false
```

### Step 4: Migrate Data

#### Option A: Keep Existing Vector DB

If you have an existing `chroma_db` directory:
1. The RAG Service will use it automatically
2. No migration needed

#### Option B: Rebuild Vector DB

If you want to rebuild:
```bash
# Start data pipeline service
docker-compose up data-pipeline-service

# Trigger ingestion
curl -X POST http://localhost:8003/ingest
```

### Step 5: Start Services

#### Development (Docker Compose)

```bash
# Start all services
docker-compose up --build

# Or start individually
docker-compose up llm-service
docker-compose up rag-service
docker-compose up data-pipeline-service
docker-compose up ui-service
```

#### Development (Local)

```bash
# Terminal 1: LLM Service
cd services/llm-service
pip install -r requirements.txt
python main.py

# Terminal 2: RAG Service
cd services/rag-service
pip install -r requirements.txt
python main.py

# Terminal 3: Data Pipeline Service
cd services/data-pipeline-service
pip install -r requirements.txt
python main.py

# Terminal 4: UI Service
cd services/ui-service
pip install -r requirements.txt
streamlit run main.py
```

## 🔍 Key Changes

### 1. LLM Calls

**Before (Monolithic)**:
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()
response = llm.invoke("Hello")
```

**After (Microservices)**:
```python
import httpx
response = httpx.post(
    "http://llm-service:8000/chat",
    json={"messages": [{"role": "user", "content": "Hello"}]}
)
```

### 2. RAG Queries

**Before (Monolithic)**:
```python
from src.core import LoLRAGSystem
rag = LoLRAGSystem()
rag.initialize()
answer = rag.query("What are Ahri's abilities?")
```

**After (Microservices)**:
```python
import httpx
response = httpx.post(
    "http://rag-service:8000/query",
    json={"question": "What are Ahri's abilities?"}
)
answer = response.json()["answer"]
```

### 3. Data Collection

**Before (Monolithic)**:
```python
from src.data.collector import LoLDataCollector
collector = LoLDataCollector()
docs = collector.get_documents()
```

**After (Microservices)**:
```bash
curl -X POST http://data-pipeline-service:8000/ingest
```

## 🧪 Testing

### Test Individual Services

```bash
# Test LLM Service
curl http://localhost:8001/health
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Test RAG Service
curl http://localhost:8002/health
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are Ahri'\''s abilities?"}'

# Test Data Pipeline Service
curl http://localhost:8003/health
curl -X POST http://localhost:8003/ingest
```

### Test Full Flow

1. Start all services: `docker-compose up`
2. Access UI: http://localhost:8501
3. Ask a question in the UI
4. Check logs: `docker-compose logs -f`

## ⚠️ Breaking Changes

1. **Direct imports removed**: Services must communicate via HTTP
2. **Configuration**: Now uses environment variables instead of config files
3. **Initialization**: Services initialize independently
4. **Data flow**: Data pipeline must run before RAG queries

## 🔧 Troubleshooting

### Service Communication Issues

If services can't communicate:
1. Check network: `docker network ls`
2. Verify service URLs in environment variables
3. Check service health endpoints

### Vector DB Issues

If vector DB is missing:
1. Run data pipeline: `curl -X POST http://localhost:8003/ingest`
2. Check logs: `docker-compose logs data-pipeline-service`
3. Verify volume mounts in `docker-compose.yml`

### Port Conflicts

If ports are in use:
1. Modify ports in `docker-compose.yml`
2. Update service URLs in environment variables
3. Restart services

## 📚 Next Steps

1. **Add Redis** for caching and job queues
2. **Add PostgreSQL** for metadata storage
3. **Add authentication** to API Gateway
4. **Add monitoring** (Prometheus, Grafana)
5. **Deploy to Kubernetes** for production

## 🆘 Rollback

If you need to rollback to monolithic:

```bash
# Stop microservices
docker-compose down

# Use original app.py
streamlit run app.py
```

The original monolithic code is still in `src/` and `app.py` for reference.


# 🏗️ LOLQA Microservices Architecture

This document describes the microservices architecture refactoring of the LOLQA application.

## 📋 Overview

The application has been refactored from a monolithic structure into a microservices architecture with 4 main services:

1. **LLM Service** - Handles LLM inference and embeddings
2. **RAG Service** - Handles RAG queries with LangGraph workflow
3. **Data Pipeline Service** - Handles data collection, chunking, and vector DB ingestion
4. **UI Service** - Streamlit frontend that calls RAG Service

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              API Gateway (Traefik)                      │
└─────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌──────────┐   ┌─────────┐   ┌──────────┐
    │   UI    │   │   RAG    │   │   LLM   │   │  Data    │
    │ Service │   │ Service  │   │ Service │   │ Pipeline │
    │         │   │          │   │         │   │ Service  │
    │ Streamlit│  │ LangGraph│   │ vLLM/   │   │ Crawl +  │
    │         │   │ + Vector │   │ OpenAI  │   │ Chunking │
    └─────────┘   └────┬─────┘   └─────────┘   └────┬────┘
                       │              │              │
                       │              │              │
                       └──────────────┴──────────────┘
                                      │
                  ┌──────────────┴──────────────┐
                  │                             │
             ┌─────────┐                  ┌──────────┐
             │ Vector  │                  │  Redis   │
             │   DB    │                  │ (Cache + │
             │(Chroma) │                  │  Queue)  │
             └─────────┘                  └──────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (or vLLM endpoint)

### Environment Variables

Create a `.env` file in the root directory:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_BACKEND=openai  # or "vllm" for self-hosted

# RAG Configuration
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_RETRIEVAL_K=3

# Data Sources
USE_DATA_DRAGON=true
USE_WEB_SCRAPER=true
USE_RIOT_API=false
USE_SAMPLE_DATA=true

# Logging
LOG_LEVEL=INFO
```

### Start All Services

```bash
docker-compose up --build
```

This will start:
- LLM Service on port 8001
- RAG Service on port 8002
- Data Pipeline Service on port 8003
- UI Service on port 8501
- API Gateway (Traefik) on port 80

### Access Services

- **UI Service**: http://localhost:8501
- **LLM Service**: http://localhost:8001
- **RAG Service**: http://localhost:8002
- **Data Pipeline Service**: http://localhost:8003
- **Traefik Dashboard**: http://localhost:8080

## 📦 Service Details

### LLM Service

**Port**: 8001  
**Endpoints**:
- `POST /chat` - Chat completion
- `POST /embeddings` - Generate embeddings
- `GET /models` - List available models
- `GET /health` - Health check

**Configuration**:
- Supports OpenAI (default) and vLLM backends
- Set `LLM_BACKEND=vllm` and `VLLM_ENDPOINT` for self-hosted models

### RAG Service

**Port**: 8002  
**Endpoints**:
- `POST /query` - Process RAG query
- `POST /retrieve` - Retrieve documents only
- `GET /stats` - Vector DB statistics
- `GET /health` - Health check

**Dependencies**: LLM Service, Vector DB (ChromaDB)

### Data Pipeline Service

**Port**: 8003  
**Endpoints**:
- `POST /ingest` - Trigger data ingestion
- `GET /status/{job_id}` - Get job status
- `POST /schedule` - Schedule periodic runs (TODO)
- `GET /health` - Health check

**Dependencies**: LLM Service (for embeddings)

### UI Service

**Port**: 8501  
**Technology**: Streamlit  
**Dependencies**: RAG Service

## 🔧 Development

### Running Services Individually

#### LLM Service
```bash
cd services/llm-service
pip install -r requirements.txt
python main.py
```

#### RAG Service
```bash
cd services/rag-service
pip install -r requirements.txt
python main.py
```

#### Data Pipeline Service
```bash
cd services/data-pipeline-service
pip install -r requirements.txt
python main.py
```

#### UI Service
```bash
cd services/ui-service
pip install -r requirements.txt
streamlit run main.py
```

### Building Individual Services

```bash
# Build LLM Service
docker build -f services/llm-service/Dockerfile -t llm-service .

# Build RAG Service
docker build -f services/rag-service/Dockerfile -t rag-service .

# Build Data Pipeline Service
docker build -f services/data-pipeline-service/Dockerfile -t data-pipeline-service .

# Build UI Service
docker build -f services/ui-service/Dockerfile -t ui-service .
```

## 📝 API Examples

### Chat Completion (LLM Service)

```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is League of Legends?"}
    ]
  }'
```

### RAG Query (RAG Service)

```bash
curl -X POST http://localhost:8002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are Ahri'\''s abilities?",
    "k": 3
  }'
```

### Data Ingestion (Data Pipeline Service)

```bash
curl -X POST http://localhost:8003/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "force_refresh": false
  }'
```

## 🔄 Data Flow

### Query Flow
1. User → UI Service
2. UI Service → RAG Service
3. RAG Service → Vector DB (retrieve context)
4. RAG Service → LLM Service (generate answer)
5. LLM Service → RAG Service → UI Service → User

### Data Ingestion Flow
1. Data Pipeline Service → Collect data (APIs, scraping)
2. Data Pipeline Service → Chunk documents
3. Data Pipeline Service → LLM Service (get embeddings)
4. Data Pipeline Service → Vector DB (store)

## 🐛 Troubleshooting

### Services not starting

1. Check Docker logs:
   ```bash
   docker-compose logs [service-name]
   ```

2. Verify environment variables:
   ```bash
   docker-compose config
   ```

3. Check service health:
   ```bash
   curl http://localhost:8001/health  # LLM Service
   curl http://localhost:8002/health  # RAG Service
   curl http://localhost:8003/health  # Data Pipeline Service
   ```

### Vector DB not found

The vector DB is created on first data ingestion. Run:
```bash
curl -X POST http://localhost:8003/ingest
```

### Port conflicts

Modify ports in `docker-compose.yml` if you have conflicts.

## 🚀 Production Considerations

1. **Use Redis** for caching and job queues (currently in-memory)
2. **Use PostgreSQL** for job tracking and metadata
3. **Add authentication** to API Gateway
4. **Use Kubernetes** for orchestration
5. **Add monitoring** (Prometheus, Grafana)
6. **Add logging** aggregation (ELK stack)
7. **Use managed services** for Vector DB (Pinecone, Qdrant Cloud)

## 📚 Migration from Monolithic

See `MIGRATION_GUIDE.md` for details on migrating from the monolithic structure.


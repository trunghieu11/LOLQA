# 🚀 Quick Start Guide

Get your League of Legends Q&A microservices application up and running in minutes!

## Prerequisites

- **Docker and Docker Compose** installed ([Get Docker](https://www.docker.com/get-started))
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Git** (to clone the repository)

> 📖 **Need detailed instructions?** See the [API Keys Setup Guide](API_KEYS_SETUP.md) for step-by-step help.

## Quick Start (5 Minutes)

### Step 1: Clone and Setup

```bash
git clone <repository-url>
cd LOLQA
cp .env.example .env
```

### Step 2: Configure Environment Variables

Edit `.env` file and add your API keys:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional but recommended
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=lolqa

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# Redis (defaults work for local)
REDIS_URL=redis://redis:6379/0

# PostgreSQL (defaults work for local)
POSTGRES_URL=postgresql://lolqa:lolqa_password@postgres:5432/lolqa
POSTGRES_PASSWORD=lolqa_password

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your-secret-key-here
```

### Step 3: Start All Services

```bash
docker-compose up --build
```

This will start:
- **UI Service** on http://localhost:8501
- **RAG Service** on http://localhost:8002
- **LLM Service** on http://localhost:8001
- **Data Pipeline Service** on http://localhost:8003
- **Auth Service** on http://localhost:8004
- **Redis** (caching and queues)
- **PostgreSQL** (metadata storage)
- **Prometheus** (metrics) on http://localhost:9090
- **Grafana** (monitoring) on http://localhost:3000
- **Traefik** (API Gateway) on http://localhost:80

### Step 4: Ingest Data (First Time Only)

Once all services are running, ingest the League of Legends data:

```bash
curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'
```

Or with more options:

```bash
# Force refresh (re-ingest even if data exists)
curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{"force_refresh": true}'
```

This will:
- Collect data from multiple sources (Data Dragon, Web Scraper, etc.)
- Chunk the documents
- Generate embeddings
- Store in the vector database

**Note**: This may take 2-5 minutes on first run.

### Step 5: Access the Application

Open your browser and go to:

**http://localhost:8501**

You should see the League of Legends Q&A chatbot interface!

## Testing the Chatbot

Try asking questions like:
- "What are Ahri's abilities?"
- "How should I play Yasuo?"
- "Tell me about teamfighting in League of Legends"
- "What items should I build on Jinx?"

## Service Health Checks

Verify all services are running:

```bash
# Check UI Service
curl http://localhost:8501

# Check RAG Service
curl http://localhost:8002/health

# Check LLM Service
curl http://localhost:8001/health

# Check Data Pipeline Service
curl http://localhost:8003/health

# Check Auth Service
curl http://localhost:8004/health
```

## Troubleshooting

### Services Not Starting

**Check Docker logs**:
```bash
docker-compose logs [service-name]
# Example: docker-compose logs rag-service
```

**Verify environment variables**:
```bash
docker-compose config
```

**Check service health**:
```bash
curl http://localhost:8001/health  # LLM Service
curl http://localhost:8002/health  # RAG Service
curl http://localhost:8003/health  # Data Pipeline Service
```

### Port Conflicts

If ports are already in use, modify `docker-compose.yml` to use different ports.

### Vector DB Not Found

The vector database is created automatically on first data ingestion. If you see errors:
1. Make sure Data Pipeline Service is running
2. Run: `curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'`
3. Wait for ingestion to complete (check logs)

### RAG Service Not Available

If the UI shows "RAG Service is not available":
1. Check RAG Service is running: `curl http://localhost:8002/health`
2. Check RAG Service logs: `docker-compose logs rag-service`
3. Verify LLM Service is running (RAG depends on it)

### Data Ingestion Fails

If data ingestion fails:
1. Check Data Pipeline Service logs: `docker-compose logs data-pipeline-service`
2. Verify LLM Service is running (needed for embeddings)
3. Check PostgreSQL is running: `docker-compose ps postgres`
4. Verify OpenAI API key is set correctly

### UI Service ModuleNotFoundError

If you see `ModuleNotFoundError: No module named 'redis'` (or similar) when accessing the UI:
1. Rebuild the UI service: `docker-compose up --build -d ui-service`
2. Check UI service logs: `docker-compose logs ui-service`
3. Verify all dependencies are in `services/ui-service/requirements.txt`

**Note**: The UI service requires `redis`, `prometheus-client`, and `psycopg2-binary` because it imports from `shared.common` modules.

## Stopping Services

To stop all services:

```bash
docker-compose down
```

To stop and remove volumes (clean slate):

```bash
docker-compose down -v
```

## Next Steps

- **Learn the Architecture**: See [Architecture Guide](ARCHITECTURE.md)
- **Deploy to Production**: See [Deployment Guide](DEPLOYMENT.md)
- **Develop Locally**: See [Development Guide](DEVELOPMENT.md)
- **Understand Data Collection**: See [Data Collection Guide](DATA_COLLECTION.md)

## Alternative: Run Services Individually

For development, you can run services individually:

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

**Note**: You'll also need Redis and PostgreSQL running separately.

Happy coding! ⚔️

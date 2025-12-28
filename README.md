# ⚔️ LOLQA - League of Legends Q&A Application

> **Production-Ready Microservices Architecture** with RAG, LangGraph, and comprehensive testing

A comprehensive Q&A application about League of Legends built with **LangChain**, **LangGraph**, and modern microservices architecture. This application uses Retrieval Augmented Generation (RAG) to answer questions about champions, abilities, game mechanics, and strategies.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for microservices)
- OpenAI API key

### 5-Minute Setup

1. **Clone and setup**:
```bash
git clone <repository-url>
cd LOLQA
cp .env.example .env
# Edit .env with your OPENAI_API_KEY
```

2. **Start all services**:
```bash
docker-compose up --build
```

3. **Access the application**:
- **UI**: http://localhost:8501
- **API Gateway**: http://localhost:80
- **Traefik Dashboard**: http://localhost:8080

4. **Ingest data** (first time):
```bash
curl -X POST http://localhost:8003/ingest
```

> 📖 **Need more details?** See the [Quick Start Guide](docs/QUICKSTART.md)

---

## ✨ Key Features

### 🧠 Intelligent Q&A
- Answer questions about **172 League of Legends champions**
- Provide detailed information (abilities, stats, skins, lore)
- Conversation memory for context-aware responses
- No hallucination - strictly uses knowledge base

### 🏗️ Microservices Architecture
- **5 Independent Services**: UI, RAG, LLM, Data Pipeline, Auth
- **Scalable**: Each service scales independently
- **Production-Ready**: Redis caching, PostgreSQL metadata, monitoring

### 🛠️ Modern Tech Stack
- **FastAPI** for microservices
- **LangChain & LangGraph** for RAG workflows
- **ChromaDB** for vector storage
- **Redis** for caching and queues
- **PostgreSQL** for metadata
- **Prometheus & Grafana** for monitoring

### 🧪 Quality Assurance
- **117+ Tests** with 43%+ coverage
- **CI/CD** with GitHub Actions
- **Comprehensive Documentation**

---

## 📚 Documentation

### 🎯 For New Users

1. **[Quick Start Guide](docs/QUICKSTART.md)** - Get running in 5 minutes
2. **[Project Guide](docs/PROJECT_GUIDE.md)** - Complete project overview
3. **[API Keys Setup](docs/API_KEYS_SETUP.md)** - Configure your API keys

### 🏗️ For Developers

1. **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and microservices
2. **[Development Guide](docs/DEVELOPMENT.md)** - Development setup and workflow
3. **[Testing Guide](docs/TESTING.md)** - Testing practices and examples
4. **[Deployment Guide](docs/DEPLOYMENT.md)** - Deploy to production

### 📖 Complete Documentation Index

See [docs/README.md](docs/README.md) for the complete documentation index.

---

## 🏗️ Architecture

LOLQA uses a **microservices architecture** with 5 main services:

```
┌─────────────────────────────────────────────┐
│             API Gateway (Traefik)           │
└─────────────────────────────────────────────┘
         │         │         │         │
    ┌────▼───┐ ┌──▼────┐ ┌───▼───┐ ┌───▼────┐
    │   UI   │ │ RAG   │ │ LLM   │ │ Data   │
    │Service │ │Service│ │Service│ │Pipeline│
    └────────┘ └───────┘ └───────┘ └────────┘
```

**Services**:
- **UI Service** (Port 8501) - Streamlit frontend
- **RAG Service** (Port 8002) - RAG queries with LangGraph
- **LLM Service** (Port 8001) - LLM inference and embeddings
- **Data Pipeline Service** (Port 8003) - Data collection and ingestion
- **Auth Service** (Port 8004) - User authentication

**Infrastructure**:
- **Redis** - Caching and job queues
- **PostgreSQL** - Metadata storage
- **ChromaDB** - Vector database
- **Prometheus & Grafana** - Monitoring

> 📖 **For detailed architecture**: See [Architecture Guide](docs/ARCHITECTURE.md)

---

## 🛠️ Installation & Setup

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run individual services (see Development Guide)
cd services/llm-service && python main.py
```

> 📖 **For detailed setup**: See [Development Guide](docs/DEVELOPMENT.md)

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov=shared --cov=services --cov-report=html

# Run specific test
pytest tests/test_rag_service.py -v
```

**Test Coverage**: 43%+ (117 tests, 5 skipped)

> 📖 **For testing guide**: See [Testing Guide](docs/TESTING.md)

---

## 🚀 Deployment

### Local Development
```bash
docker-compose up
```

### Kubernetes
```bash
kubectl apply -f kubernetes/
```

### Cloud Platforms
- AWS (ECS/EKS)
- Google Cloud (GKE)
- Azure (AKS)
- DigitalOcean

> 📖 **For deployment guide**: See [Deployment Guide](docs/DEPLOYMENT.md)

---

## 📁 Project Structure

```
LOLQA/
├── services/              # Microservices
│   ├── llm-service/       # LLM inference
│   ├── rag-service/       # RAG queries
│   ├── data-pipeline-service/  # Data ingestion
│   ├── auth-service/      # Authentication
│   └── ui-service/        # Streamlit UI
├── shared/                # Shared code
│   └── common/           # Common utilities
├── src/                   # Legacy monolithic code
├── tests/                 # Test suite
├── docs/                  # Documentation
├── kubernetes/           # K8s manifests
└── docker-compose.yml    # Local orchestration
```

> 📖 **For detailed structure**: See [Project Guide](docs/PROJECT_GUIDE.md)

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# OpenAI
OPENAI_API_KEY=your_key_here

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_BACKEND=openai

# Redis
REDIS_URL=redis://redis:6379/0

# PostgreSQL
POSTGRES_URL=postgresql://lolqa:password@postgres:5432/lolqa

# JWT
JWT_SECRET_KEY=your-secret-key
```

> 📖 **For configuration details**: See [API Keys Setup](docs/API_KEYS_SETUP.md)

---

## 📝 Example Questions

- "What are Ahri's abilities?"
- "How should I play Yasuo?"
- "What is the role of a support champion?"
- "Tell me about teamfighting in League of Legends"
- "What items should I build on Jinx?"

---

## 🐛 Troubleshooting

### Services Not Starting
```bash
# Check logs
docker-compose logs [service-name]

# Check health
curl http://localhost:8001/health
```

### Vector DB Issues
```bash
# Recreate vector DB
rm -rf chroma_db/
curl -X POST http://localhost:8003/ingest
```

> 📖 **For more troubleshooting**: See [Deployment Guide](docs/DEPLOYMENT.md#-troubleshooting)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

> 📖 **For contribution guidelines**: See [Development Guide](docs/DEVELOPMENT.md#-contributing)

---

## 📊 Project Statistics

- **Services**: 5 microservices
- **Tests**: 117+ tests, 43%+ coverage
- **Documentation**: Comprehensive guides
- **Technologies**: FastAPI, LangChain, LangGraph, Redis, PostgreSQL

---

## 📚 Additional Resources

### External Documentation
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API](https://platform.openai.com/docs)

### Project Documentation
- [Complete Documentation Index](docs/README.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Development Guide](docs/DEVELOPMENT.md)
- [Testing Guide](docs/TESTING.md)
- [Deployment Guide](docs/DEPLOYMENT.md)

---

## 📄 License

This project is for educational purposes.

---

## 🙏 Acknowledgments

- Built with ⚔️ for League of Legends fans and AI enthusiasts
- Powered by LangChain, LangGraph, and OpenAI
- Inspired by the League of Legends community

---

**Made with ⚔️ for League of Legends fans!**

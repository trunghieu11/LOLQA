# 🏗️ LOLQA Architecture Guide

> Complete guide to the microservices architecture, system design, and component interactions

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Services](#services)
4. [Data Flow](#data-flow)
5. [Infrastructure Components](#infrastructure-components)
6. [Technology Stack](#technology-stack)
7. [Service Communication](#service-communication)
8. [Scalability & Performance](#scalability--performance)

---

## 🎯 Overview

LOLQA is built as a **microservices architecture** with 5 main services:

1. **UI Service** - Streamlit frontend
2. **RAG Service** - RAG queries with LangGraph workflow
3. **LLM Service** - LLM inference and embeddings
4. **Data Pipeline Service** - Data collection, chunking, and ingestion
5. **Auth Service** - User authentication and JWT management

### Key Design Principles

- **Separation of Concerns**: Each service has a single responsibility
- **Scalability**: Services can scale independently
- **Technology Diversity**: Each service can use different tech stacks
- **Testability**: Services can be tested independently
- **Deployment Flexibility**: Services can be deployed separately

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Traefik)                    │
│                    Port: 80, Dashboard: 8080                │
└─────────────────────────────────────────────────────────────┘
         │         │          │          │          │
         ▼         ▼           ▼         ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │   UI   │ │  RAG   │ │  LLM   │ │  Data  │ │  Auth  │
    │Service │ │Service │ │Service │ │Pipeline│ │Service │
    │ :8501  │ │ :8002  │ │ :8001  │ │ :8003  │ │ :8004  │
    └────────┘ └────┬───┘ └────┬───┘ └────┬───┘ └────────┘
                    │          │          │
                    │          │          │
         ┌──────────┴──────────┴──────────┴─────────┐
         │                                          │
    ┌────▼────┐  ┌──────────┐  ┌──────────┐  ┌──────▼────┐
    │ Vector  │  │  Redis   │  │PostgreSQL│  │Prometheus │
    │   DB    │  │ (Cache + │  │(Metadata)│  │(Metrics)  │
    │(Chroma) │  │  Queue)  │  │          │  │           │
    └─────────┘  └──────────┘  └──────────┘  └───────────┘
                                                      │
                                               ┌──────▼────┐
                                               │  Grafana  │
                                               │  :3000    │
                                               └───────────┘
```

---

## 🔧 Services

### 1. UI Service (Streamlit)

**Port**: 8501  
**Technology**: Streamlit  
**Purpose**: User-facing web interface

**Features**:
- Interactive chat interface
- Conversation history
- Example questions
- Real-time responses

**Dependencies**: RAG Service

---

### 2. RAG Service

**Port**: 8002  
**Technology**: FastAPI, LangGraph, LangChain  
**Purpose**: RAG query processing and orchestration

**Endpoints**:
- `POST /query` - Process RAG query
- `POST /retrieve` - Retrieve documents only
- `GET /stats` - Vector DB statistics
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**Dependencies**: 
- LLM Service (for embeddings and chat)
- Vector DB (ChromaDB)
- Redis (for caching)

**Key Components**:
- `rag_system.py` - RAG system implementation
- `workflow.py` - LangGraph workflow orchestration

---

### 3. LLM Service

**Port**: 8001  
**Technology**: FastAPI, OpenAI/vLLM  
**Purpose**: LLM inference and embedding generation

**Endpoints**:
- `POST /chat` - Chat completion
- `POST /embeddings` - Generate embeddings
- `GET /models` - List available models
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**Features**:
- Supports OpenAI (default) and vLLM backends
- Embedding caching with Redis (24h TTL)
- Request metrics tracking

**Configuration**:
- `LLM_BACKEND=openai` or `vllm`
- `LLM_MODEL=gpt-4o-mini` (default)
- `VLLM_ENDPOINT` (for self-hosted models)

---

### 4. Data Pipeline Service

**Port**: 8003  
**Technology**: FastAPI  
**Purpose**: Data collection, chunking, and vector DB ingestion

**Endpoints**:
- `POST /ingest` - Trigger data ingestion
- `GET /status/{job_id}` - Get job status
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**Features**:
- Multi-source data collection (Data Dragon, Web Scraper, Riot API)
- Text chunking with configurable size/overlap
- Background job processing with Redis queue
- Job tracking with PostgreSQL
- Vector DB ingestion

**Dependencies**:
- LLM Service (for embeddings)
- Redis (for job queue)
- PostgreSQL (for job tracking)
- Vector DB (ChromaDB)

---

### 5. Auth Service

**Port**: 8004  
**Technology**: FastAPI, JWT, bcrypt  
**Purpose**: User authentication and authorization

**Endpoints**:
- `POST /register` - Register new user
- `POST /login` - Login and get JWT token
- `GET /me` - Get current user info
- `GET /verify` - Verify token validity
- `GET /health` - Health check

**Features**:
- JWT token generation and verification
- Password hashing with bcrypt
- User management
- Token expiration (30 minutes default)

**Dependencies**: PostgreSQL (for user storage)

---

## 🔄 Data Flow

### Query Flow (User Question → Answer)

```
1. User → UI Service (Streamlit)
   ↓
2. UI Service → RAG Service (/query)
   ↓
3. RAG Service → Vector DB (retrieve relevant documents)
   ↓
4. RAG Service → LLM Service (/chat)
   ↓
5. LLM Service → RAG Service (generated answer)
   ↓
6. RAG Service → UI Service → User
```

### Data Ingestion Flow

```
1. Data Pipeline Service → Collect data
   ├─ Data Dragon API
   ├─ Web Scraper
   ├─ Riot API (optional)
   └─ Sample Data (fallback)
   ↓
2. Data Pipeline Service → Chunk documents
   ↓
3. Data Pipeline Service → LLM Service (/embeddings)
   ↓
4. LLM Service → Redis (cache embeddings)
   ↓
5. Data Pipeline Service → Vector DB (store with embeddings)
   ↓
6. Data Pipeline Service → PostgreSQL (log job status)
```

### Authentication Flow

```
1. User → Auth Service (/register or /login)
   ↓
2. Auth Service → PostgreSQL (verify/create user)
   ↓
3. Auth Service → Generate JWT token
   ↓
4. User → Other Services (with JWT token in header)
   ↓
5. Services → Auth Service (/verify) → Validate token
```

---

## 🗄️ Infrastructure Components

### Vector Database (ChromaDB)

**Purpose**: Store document embeddings for semantic search

**Features**:
- Persistent storage (volume mounted)
- Automatic creation on first ingestion
- Fast similarity search

**Location**: `chroma_db/` directory (Docker volume)

---

### Redis

**Purpose**: Caching and job queues

**Features**:
- Embedding cache (24h TTL)
- Job queue for pipeline processing
- Cache hit/miss metrics

**Configuration**:
- `REDIS_URL=redis://redis:6379/0`

---

### PostgreSQL

**Purpose**: Metadata storage and job tracking

**Tables**:
- `pipeline_jobs` - Job tracking
- `query_history` - Query analytics
- `embedding_cache_metadata` - Cache metadata
- `service_metrics` - Service metrics storage
- `users` - User authentication

**Configuration**:
- `POSTGRES_URL=postgresql://lolqa:password@postgres:5432/lolqa`

---

### Prometheus

**Purpose**: Metrics collection

**Features**:
- HTTP request metrics
- Cache hit/miss metrics
- Queue length metrics
- Service health metrics

**Access**: http://localhost:9090

---

### Grafana

**Purpose**: Metrics visualization

**Features**:
- Pre-configured dashboards
- Service health monitoring
- Performance metrics

**Access**: http://localhost:3000 (admin/admin)

---

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.11+** - Programming language
- **FastAPI** - API framework for services
- **Streamlit** - UI framework
- **LangChain** - RAG framework
- **LangGraph** - Workflow orchestration
- **OpenAI** - LLM and embeddings
- **ChromaDB** - Vector database
- **Redis** - Caching and queues
- **PostgreSQL** - Relational database

### Infrastructure

- **Docker** - Containerization
- **Docker Compose** - Local orchestration
- **Traefik** - API Gateway
- **Kubernetes** - Production orchestration
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization

---

## 📡 Service Communication

### Communication Patterns

1. **Synchronous (REST)**: 
   - UI → RAG Service
   - RAG Service → LLM Service
   - Services → Auth Service

2. **Asynchronous (Message Queue)**:
   - Data Pipeline → Redis Queue → Background workers

3. **Direct Database Access**:
   - Services → PostgreSQL (metadata)
   - Services → ChromaDB (vector search)
   - Services → Redis (cache)

### API Gateway (Traefik)

**Purpose**: 
- Route requests to appropriate services
- Load balancing
- SSL termination
- Request logging

**Configuration**: Automatic service discovery via Docker labels

---

## 📈 Scalability & Performance

### Horizontal Scaling

Each service can scale independently:
- **UI Service**: Multiple instances behind load balancer
- **RAG Service**: Scale based on query load
- **LLM Service**: Scale based on inference load
- **Data Pipeline**: Scale workers based on queue length

### Caching Strategy

- **Embedding Cache**: 24h TTL in Redis
- **Query Results**: Can be cached in RAG Service
- **Vector DB**: In-memory index for fast retrieval

### Performance Optimizations

- **Connection Pooling**: PostgreSQL and Redis
- **Async Processing**: Background jobs for data ingestion
- **Batch Processing**: Embedding generation in batches
- **Indexing**: Vector DB indexes for fast similarity search

---

## 🔐 Security

### Authentication

- JWT tokens for service authentication
- Password hashing with bcrypt
- Token expiration (30 minutes)

### Network Security

- Services communicate via internal Docker network
- API Gateway handles external traffic
- Environment variables for sensitive data

---

## 📚 Related Documentation

- [Quick Start Guide](QUICKSTART.md) - Get started quickly
- [Deployment Guide](DEPLOYMENT.md) - Deploy to production
- [Development Guide](DEVELOPMENT.md) - Development setup
- [Project Guide](PROJECT_GUIDE.md) - Complete project overview

---

Made with ⚔️ for League of Legends fans and AI enthusiasts!


# 🚀 Deployment Guide

> Complete guide for deploying LOLQA to various platforms

---

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Environment Configuration](#environment-configuration)
6. [Production Checklist](#production-checklist)

---

## 💻 Local Development

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API key

### Quick Start

1. **Clone the repository**:
```bash
git clone <repository-url>
cd LOLQA
```

2. **Set up environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start all services**:
```bash
docker-compose up --build
```

4. **Access services**:
- UI: http://localhost:8501
- Traefik Dashboard: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

5. **Ingest data** (first time):
```bash
curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'
```

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

---

## 🐳 Docker Deployment

### Build Individual Services

```bash
# Build LLM Service
docker build -f services/llm-service/Dockerfile -t llm-service .

# Build RAG Service
docker build -f services/rag-service/Dockerfile -t rag-service .

# Build Data Pipeline Service
docker build -f services/data-pipeline-service/Dockerfile -t data-pipeline-service .

# Build UI Service
docker build -f services/ui-service/Dockerfile -t ui-service .

# Build Auth Service
docker build -f services/auth-service/Dockerfile -t auth-service .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build -d
```

### Docker Compose Services

- **llm-service**: Port 8001
- **rag-service**: Port 8002
- **data-pipeline-service**: Port 8003
- **auth-service**: Port 8004
- **ui-service**: Port 8501
- **traefik**: Port 80, Dashboard 8080
- **redis**: Port 6379
- **postgres**: Port 5432
- **prometheus**: Port 9090
- **grafana**: Port 3000

---

## ☸️ Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Helm 3.x (optional, for Helm charts)

### Quick Start

1. **Create namespace**:
```bash
kubectl apply -f kubernetes/namespace.yaml
```

2. **Create secrets**:
```bash
# Edit kubernetes/secret.yaml with your values
kubectl apply -f kubernetes/secret.yaml
```

3. **Create configmap**:
```bash
kubectl apply -f kubernetes/configmap.yaml
```

4. **Deploy services**:
```bash
# Deploy LLM Service (example)
kubectl apply -f kubernetes/llm-service.yaml

# Deploy other services similarly
```

### Service Configuration

Each service deployment includes:
- Deployment manifest
- Service definition
- Resource limits
- Health checks
- Scaling configuration

### Accessing Services

```bash
# Port forward to access services
kubectl port-forward service/llm-service 8001:8001
kubectl port-forward service/rag-service 8002:8002
kubectl port-forward service/ui-service 8501:8501
```

### Scaling

```bash
# Scale a service
kubectl scale deployment llm-service --replicas=3 -n lolqa

# Auto-scaling (requires metrics server)
kubectl autoscale deployment llm-service --min=2 --max=10 -n lolqa
```

### Monitoring

Prometheus and Grafana can be deployed using:
- Prometheus Operator
- Helm charts
- Custom manifests

See `kubernetes/README.md` for detailed instructions.

---

## ☁️ Cloud Platforms

### Option 1: AWS (ECS/EKS)

#### ECS Deployment

1. **Build and push images**:
```bash
aws ecr create-repository --repository-name lolqa/llm-service
docker tag llm-service:latest <account>.dkr.ecr.<region>.amazonaws.com/lolqa/llm-service:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/lolqa/llm-service:latest
```

2. **Create ECS task definitions** for each service
3. **Create ECS services** with load balancers
4. **Configure environment variables** in task definitions

#### EKS Deployment

Follow Kubernetes deployment steps above, using EKS cluster.

### Option 2: Google Cloud Platform (GKE)

1. **Create GKE cluster**:
```bash
gcloud container clusters create lolqa-cluster --num-nodes=3
```

2. **Deploy using kubectl** (follow Kubernetes steps)

3. **Set up Cloud Load Balancing** for external access

### Option 3: Azure (AKS)

1. **Create AKS cluster**:
```bash
az aks create --resource-group myResourceGroup --name lolqa-cluster --node-count 3
```

2. **Deploy using kubectl** (follow Kubernetes steps)

### Option 4: DigitalOcean

1. **Create Kubernetes cluster** via DigitalOcean dashboard
2. **Deploy using kubectl** (follow Kubernetes steps)
3. **Set up Load Balancer** for external access

---

## ⚙️ Environment Configuration

### Required Environment Variables

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_BACKEND=openai  # or "vllm"

# Redis
REDIS_URL=redis://redis:6379/0

# PostgreSQL
POSTGRES_URL=postgresql://lolqa:password@postgres:5432/lolqa
POSTGRES_PASSWORD=your_password

# JWT
JWT_SECRET_KEY=your-secret-key-here

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

### Service-Specific Variables

#### LLM Service
- `VLLM_ENDPOINT` - For self-hosted vLLM models
- `LLM_MAX_TOKENS` - Maximum tokens per request

#### RAG Service
- `RAG_SIMILARITY_THRESHOLD` - Minimum similarity score
- `RAG_MAX_DOCUMENTS` - Maximum documents to retrieve

#### Data Pipeline Service
- `PIPELINE_BATCH_SIZE` - Batch size for processing
- `PIPELINE_WORKER_COUNT` - Number of worker processes

---

## ✅ Production Checklist

### Security

- [ ] Change all default passwords
- [ ] Use strong JWT secret keys
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Set up authentication on API Gateway
- [ ] Use secrets management (AWS Secrets Manager, etc.)
- [ ] Enable rate limiting
- [ ] Configure CORS properly

### Monitoring

- [ ] Set up Prometheus scraping
- [ ] Configure Grafana dashboards
- [ ] Set up alerting rules
- [ ] Configure log aggregation
- [ ] Set up distributed tracing (optional)

### Performance

- [ ] Configure resource limits
- [ ] Set up auto-scaling
- [ ] Enable connection pooling
- [ ] Configure caching strategies
- [ ] Set up CDN for static assets (if applicable)

### Reliability

- [ ] Set up health checks
- [ ] Configure liveness/readiness probes
- [ ] Set up backup strategy for databases
- [ ] Configure retry policies
- [ ] Set up circuit breakers

### Database

- [ ] Set up PostgreSQL backups
- [ ] Configure connection pooling
- [ ] Set up read replicas (if needed)
- [ ] Monitor database performance

### Vector DB

- [ ] Configure ChromaDB persistence
- [ ] Set up backups for vector DB
- [ ] Monitor vector DB size
- [ ] Plan for scaling vector DB

---

## 🐛 Troubleshooting

### Services Not Starting

1. **Check logs**:
```bash
docker-compose logs [service-name]
kubectl logs [pod-name] -n lolqa
```

2. **Verify environment variables**:
```bash
docker-compose config
kubectl describe configmap -n lolqa
```

3. **Check service health**:
```bash
curl http://localhost:8001/health  # LLM Service
curl http://localhost:8002/health  # RAG Service
curl http://localhost:8003/health  # Data Pipeline Service
```

### Port Conflicts

Modify ports in:
- `docker-compose.yml` for Docker
- Service manifests for Kubernetes
- Environment variables for cloud platforms

### Database Connection Issues

1. Verify database is running
2. Check connection string format
3. Verify network connectivity
4. Check firewall rules

### Vector DB Issues

1. Delete `chroma_db` directory to recreate
2. Verify volume mounts in Docker/Kubernetes
3. Check disk space

---

## 📚 Related Documentation

- [Architecture Guide](ARCHITECTURE.md) - System architecture
- [Quick Start Guide](QUICKSTART.md) - Get started quickly
- [Development Guide](DEVELOPMENT.md) - Development setup
- [Kubernetes README](../kubernetes/README.md) - Kubernetes-specific guide

---

Made with ⚔️ for League of Legends fans and AI enthusiasts!


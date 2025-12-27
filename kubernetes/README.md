# Kubernetes Deployment Guide

This directory contains Kubernetes manifests for deploying the LOLQA microservices.

## Prerequisites

- Kubernetes cluster (minikube, GKE, EKS, AKS, etc.)
- kubectl configured
- Docker images built and pushed to a registry

## Deployment Steps

### 1. Build and Push Docker Images

```bash
# Build images
docker build -f services/llm-service/Dockerfile -t your-registry/llm-service:latest .
docker build -f services/rag-service/Dockerfile -t your-registry/rag-service:latest .
docker build -f services/data-pipeline-service/Dockerfile -t your-registry/data-pipeline-service:latest .
docker build -f services/ui-service/Dockerfile -t your-registry/ui-service:latest .
docker build -f services/auth-service/Dockerfile -t your-registry/auth-service:latest .

# Push to registry
docker push your-registry/llm-service:latest
docker push your-registry/rag-service:latest
docker push your-registry/data-pipeline-service:latest
docker push your-registry/ui-service:latest
docker push your-registry/auth-service:latest
```

### 2. Update Image Names

Update the image names in the deployment files to match your registry.

### 3. Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 4. Create Secrets

```bash
# Edit secret.yaml with your actual secrets
kubectl apply -f secret.yaml
```

### 5. Create ConfigMap

```bash
kubectl apply -f configmap.yaml
```

### 6. Deploy Services

Deploy in order:
1. Redis
2. PostgreSQL
3. LLM Service
4. RAG Service
5. Data Pipeline Service
6. Auth Service
7. UI Service

```bash
kubectl apply -f redis.yaml
kubectl apply -f postgres.yaml
kubectl apply -f llm-service.yaml
kubectl apply -f rag-service.yaml
kubectl apply -f data-pipeline-service.yaml
kubectl apply -f auth-service.yaml
kubectl apply -f ui-service.yaml
```

### 7. Deploy Ingress

```bash
kubectl apply -f ingress.yaml
```

## Accessing Services

After deployment, services are accessible via:
- UI Service: http://ui.lolqa.local (or your ingress domain)
- API Gateway: Configured via ingress

## Monitoring

Prometheus and Grafana can be deployed separately or using Helm charts.

## Scaling

To scale a service:

```bash
kubectl scale deployment llm-service --replicas=3 -n lolqa
```

## Troubleshooting

Check pod status:
```bash
kubectl get pods -n lolqa
```

View logs:
```bash
kubectl logs -f deployment/llm-service -n lolqa
```

Describe pod:
```bash
kubectl describe pod <pod-name> -n lolqa
```


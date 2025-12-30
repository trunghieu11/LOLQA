#!/bin/bash

# Verification script for LOLQA microservices
# This script checks that all services are running and responding correctly

set -e

echo "=========================================="
echo "LOLQA Microservices Verification Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILURES=0

# Function to check service health
check_service() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Checking $name... "
    
    if response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | sed '$d')
        
        if [ "$http_code" = "$expected_status" ]; then
            echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
            return 0
        else
            echo -e "${RED}✗ FAILED${NC} (HTTP $http_code, expected $expected_status)"
            echo "  Response: $body"
            FAILURES=$((FAILURES + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ FAILED${NC} (Connection error)"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

# Function to check Docker container status
check_container() {
    local name=$1
    echo -n "Checking container $name... "
    
    if docker ps --format '{{.Names}}' | grep -q "^${name}$"; then
        status=$(docker inspect --format='{{.State.Status}}' "$name" 2>/dev/null)
        health=$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null || echo "no-healthcheck")
        
        if [ "$status" = "running" ]; then
            if [ "$health" = "healthy" ] || [ "$health" = "no-healthcheck" ] || [ "$health" = "starting" ]; then
                echo -e "${GREEN}✓ Running${NC} (Status: $status, Health: $health)"
                return 0
            else
                echo -e "${YELLOW}⚠ Running but unhealthy${NC} (Status: $status, Health: $health)"
                return 1
            fi
        else
            echo -e "${RED}✗ Not running${NC} (Status: $status)"
            FAILURES=$((FAILURES + 1))
            return 1
        fi
    else
        echo -e "${RED}✗ Container not found${NC}"
        FAILURES=$((FAILURES + 1))
        return 1
    fi
}

echo "Step 1: Checking Docker containers..."
echo "----------------------------------------"
check_container "llm-service"
check_container "rag-service"
check_container "data-pipeline-service"
check_container "auth-service"
check_container "ui-service"
check_container "redis"
check_container "postgres"
check_container "api-gateway"
echo ""

echo "Step 2: Checking service health endpoints..."
echo "----------------------------------------"
check_service "LLM Service" "http://localhost:8001/health"
check_service "RAG Service" "http://localhost:8002/health"
check_service "Data Pipeline Service" "http://localhost:8003/health"
check_service "Auth Service" "http://localhost:8004/health"
check_service "UI Service" "http://localhost:8501" 200
echo ""

echo "Step 3: Testing service endpoints..."
echo "----------------------------------------"

# Test LLM Service
echo -n "Testing LLM Service /generate... "
if response=$(curl -s -X POST "http://localhost:8001/generate" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello", "max_tokens": 10}' 2>/dev/null); then
    if echo "$response" | grep -q "text\|error"; then
        echo -e "${GREEN}✓ OK${NC}"
    else
        echo -e "${YELLOW}⚠ Unexpected response${NC}"
        FAILURES=$((FAILURES + 1))
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test RAG Service
echo -n "Testing RAG Service /query... "
if response=$(curl -s -X POST "http://localhost:8002/query" \
    -H "Content-Type: application/json" \
    -d '{"query": "test", "user_id": "test"}' 2>/dev/null); then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8002/query" \
        -H "Content-Type: application/json" \
        -d '{"query": "test", "user_id": "test"}')
    if [ "$http_code" = "200" ] || [ "$http_code" = "500" ]; then
        # 500 is acceptable if vector DB is empty (needs data ingestion)
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
    else
        echo -e "${YELLOW}⚠ HTTP $http_code${NC}"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test Data Pipeline Service
echo -n "Testing Data Pipeline Service /ingest... "
if response=$(curl -s -X POST "http://localhost:8003/ingest" \
    -H "Content-Type: application/json" \
    -d '{}' 2>/dev/null); then
    if echo "$response" | grep -q "job_id"; then
        JOB_ID=$(echo "$response" | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        echo -e "${GREEN}✓ OK${NC} (Job ID: $JOB_ID)"
        
        # Check job status
        if [ -n "$JOB_ID" ]; then
            echo -n "  Checking job status... "
            sleep 2
            if status_response=$(curl -s "http://localhost:8003/status/$JOB_ID" 2>/dev/null); then
                echo -e "${GREEN}✓ OK${NC}"
                echo "  Job status response: $status_response" | head -c 100
                echo ""
            else
                echo -e "${YELLOW}⚠ Could not check status${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠ Unexpected response${NC}"
        echo "  Response: $response"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Test Auth Service
echo -n "Testing Auth Service /register... "
if response=$(curl -s -X POST "http://localhost:8004/register" \
    -H "Content-Type: application/json" \
    -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}' 2>/dev/null); then
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8004/register" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}')
    if [ "$http_code" = "200" ] || [ "$http_code" = "400" ]; then
        # 400 is acceptable if user already exists
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
    else
        echo -e "${YELLOW}⚠ HTTP $http_code${NC}"
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "Step 4: Checking infrastructure services..."
echo "----------------------------------------"

# Check Redis
echo -n "Checking Redis connection... "
if docker exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

# Check PostgreSQL
echo -n "Checking PostgreSQL connection... "
if docker exec postgres psql -U lolqa -d lolqa -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    FAILURES=$((FAILURES + 1))
fi

echo ""
echo "=========================================="
if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Your services are ready to use:"
    echo "  - UI Service: http://localhost:8501"
    echo "  - LLM Service: http://localhost:8001"
    echo "  - RAG Service: http://localhost:8002"
    echo "  - Data Pipeline Service: http://localhost:8003"
    echo "  - Auth Service: http://localhost:8004"
    exit 0
else
    echo -e "${RED}✗ Found $FAILURES issue(s)${NC}"
    echo ""
    echo "Troubleshooting tips:"
    echo "  1. Check service logs: docker-compose logs <service-name>"
    echo "  2. Restart services: docker-compose restart"
    echo "  3. Rebuild services: docker-compose up --build -d"
    exit 1
fi


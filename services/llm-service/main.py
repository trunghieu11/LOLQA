"""LLM Service - Handles LLM inference and embeddings"""
import sys
import os
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from shared.common import (
    setup_logger,
    get_config,
    ChatRequest,
    ChatResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    setup_cors_middleware,
    setup_metrics_middleware,
    handle_service_errors
)
from shared.common.config import LLMServiceConfig
from shared.common.redis_client import RedisClient, get_embedding_cache_key
from shared.common.metrics import get_metrics, cache_hits, cache_misses
from llm_client import LLMClient

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: LLMServiceConfig = get_config("llm")
logger.info(f"Starting LLM Service with backend: {config.backend}")

# Constants
SERVICE_NAME = "llm-service"
SERVICE_VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title="LLM Service",
    description="LLM inference and embedding service",
    version=SERVICE_VERSION
)

# Setup middleware
setup_cors_middleware(app)
setup_metrics_middleware(app)

# Initialize LLM client
llm_client = LLMClient(config)

# Initialize Redis for caching
redis_client = RedisClient(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from shared.common.models import HealthResponse
    return HealthResponse(
        status="healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION
    )


@app.post("/chat", response_model=ChatResponse)
@handle_service_errors()
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion.
    
    Args:
        request: Chat request with messages
        
    Returns:
        Chat response with generated content
    """
    logger.info(f"Processing chat request with {len(request.messages)} messages")
    
    # Convert messages to format expected by client
    messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # Generate response
    response = await llm_client.chat(
        messages=messages,
        model=request.model,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )
    
    return response


@app.post("/embeddings", response_model=EmbeddingResponse)
@handle_service_errors()
async def generate_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for texts (with caching).
    
    Args:
        request: Embedding request with texts
        
    Returns:
        Embedding response with vectors
    """
    logger.info(f"Generating embeddings for {len(request.texts)} texts")
    
    model = request.model or "text-embedding-3-small"
    embeddings = []
    texts_to_embed = []
    text_indices = []
    
    # Check cache for each text
    for i, text in enumerate(request.texts):
        cache_key = get_embedding_cache_key(text, model)
        cached = redis_client.get(cache_key)
        
        if cached:
            embeddings.append(cached)
            cache_hits.labels(cache_type="embedding").inc()
        else:
            embeddings.append(None)  # Placeholder
            texts_to_embed.append(text)
            text_indices.append(i)
            cache_misses.labels(cache_type="embedding").inc()
    
    # Generate embeddings for uncached texts
    if texts_to_embed:
        new_embeddings = await llm_client.embeddings(
            texts=texts_to_embed,
            model=model
        )
        
        # Cache new embeddings and fill in placeholders
        for i, (text, embedding) in enumerate(zip(texts_to_embed, new_embeddings.embeddings)):
            cache_key = get_embedding_cache_key(text, model)
            redis_client.set(cache_key, embedding, ttl=86400)  # 24 hours
            embeddings[text_indices[i]] = embedding
    
    return EmbeddingResponse(
        embeddings=embeddings,
        model=model
    )


@app.get("/models")
@handle_service_errors()
async def list_models():
    """List available models"""
    models = await llm_client.list_models()
    return {"models": models}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)


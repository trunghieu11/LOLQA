"""LLM Service - Handles LLM inference and embeddings"""
import sys
import os
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from shared.common import setup_logger, get_config, ChatRequest, ChatResponse, EmbeddingRequest, EmbeddingResponse, HealthResponse
from shared.common.config import LLMServiceConfig
from shared.common.redis_client import RedisClient, get_embedding_cache_key
from shared.common.metrics import get_metrics, http_requests_total, http_request_duration_seconds
from llm_service.llm_client import LLMClient
import time
import os

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: LLMServiceConfig = get_config("llm")
logger.info(f"Starting LLM Service with backend: {config.backend}")

# Initialize FastAPI app
app = FastAPI(
    title="LLM Service",
    description="LLM inference and embedding service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM client
llm_client = LLMClient(config)

# Initialize Redis for caching
redis_client = RedisClient(os.getenv("REDIS_URL", "redis://localhost:6379/0"))


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track metrics"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="llm-service",
        version="1.0.0"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Generate chat completion.
    
    Args:
        request: Chat request with messages
        
    Returns:
        Chat response with generated content
    """
    try:
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
    except Exception as e:
        logger.error(f"Error in chat completion: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/embeddings", response_model=EmbeddingResponse)
async def generate_embeddings(request: EmbeddingRequest):
    """
    Generate embeddings for texts (with caching).
    
    Args:
        request: Embedding request with texts
        
    Returns:
        Embedding response with vectors
    """
    try:
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
                from shared.common.metrics import cache_hits
                cache_hits.labels(cache_type="embedding").inc()
            else:
                embeddings.append(None)  # Placeholder
                texts_to_embed.append(text)
                text_indices.append(i)
                from shared.common.metrics import cache_misses
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
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available models"""
    try:
        models = await llm_client.list_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=get_metrics(), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)


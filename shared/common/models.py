"""Shared Pydantic models for API requests/responses"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat completion request"""
    messages: List[ChatMessage] = Field(..., description="List of chat messages")
    model: Optional[str] = Field(None, description="Model name (optional, uses default if not provided)")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")


class ChatResponse(BaseModel):
    """Chat completion response"""
    content: str = Field(..., description="Generated response content")
    model: str = Field(..., description="Model used for generation")
    usage: Optional[Dict[str, int]] = Field(None, description="Token usage information")


class EmbeddingRequest(BaseModel):
    """Embedding generation request"""
    texts: List[str] = Field(..., description="List of texts to embed")
    model: Optional[str] = Field(None, description="Embedding model name")


class EmbeddingResponse(BaseModel):
    """Embedding generation response"""
    embeddings: List[List[float]] = Field(..., description="List of embedding vectors")
    model: str = Field(..., description="Model used for embeddings")


class RAGQueryRequest(BaseModel):
    """RAG query request"""
    question: str = Field(..., description="User question")
    conversation_history: Optional[List[ChatMessage]] = Field(None, description="Previous conversation messages")
    k: Optional[int] = Field(None, description="Number of documents to retrieve")


class RAGQueryResponse(BaseModel):
    """RAG query response"""
    answer: str = Field(..., description="Generated answer")
    context: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieved context documents")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(default="1.0.0", description="Service version")


class PipelineJobRequest(BaseModel):
    """Data pipeline job request"""
    sources: Optional[List[str]] = Field(None, description="Data sources to use (default: all)")
    force_refresh: bool = Field(False, description="Force refresh even if data exists")


class PipelineJobResponse(BaseModel):
    """Data pipeline job response"""
    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")


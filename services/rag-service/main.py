"""RAG Service - Handles RAG queries with LangGraph workflow"""
import sys
import os
from pathlib import Path

# Add shared and src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.common import setup_logger, get_config, HealthResponse, RAGQueryRequest, RAGQueryResponse
from shared.common.config import RAGServiceConfig
from rag_service.rag_system import RAGServiceSystem

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: RAGServiceConfig = get_config("rag")
logger.info(f"Starting RAG Service")

# Initialize FastAPI app
app = FastAPI(
    title="RAG Service",
    description="RAG and LangGraph workflow service",
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

# Initialize RAG system
rag_system = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    try:
        logger.info("Initializing RAG system...")
        rag_system = RAGServiceSystem(config)
        await rag_system.initialize()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}", exc_info=True)
        raise


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if rag_system is None:
        return HealthResponse(
            status="initializing",
            service="rag-service",
            version="1.0.0"
        )
    return HealthResponse(
        status="healthy",
        service="rag-service",
        version="1.0.0"
    )


@app.post("/query", response_model=RAGQueryResponse)
async def query(request: RAGQueryRequest):
    """
    Process RAG query using LangGraph workflow.
    
    Args:
        request: RAG query request
        
    Returns:
        RAG query response with answer and context
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        logger.info(f"Processing RAG query: {request.question[:50]}...")
        
        # Convert conversation history if provided
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        # Process query
        answer = await rag_system.query(
            question=request.question,
            conversation_history=conversation_history,
            k=request.k
        )
        
        # Optionally get context documents
        context = None
        if request.k:
            docs = await rag_system.get_relevant_documents(request.question, k=request.k)
            context = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        
        return RAGQueryResponse(
            answer=answer,
            context=context
        )
    except Exception as e:
        logger.error(f"Error processing RAG query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve")
async def retrieve(question: str, k: int = 3):
    """
    Retrieve relevant documents only (no generation).
    
    Args:
        question: Search query
        k: Number of documents to retrieve
        
    Returns:
        List of relevant documents
    """
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        docs = await rag_system.get_relevant_documents(question, k=k)
        return {
            "documents": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        }
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get vector database statistics"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    
    try:
        stats = await rag_system.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)


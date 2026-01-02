"""RAG Service - Handles RAG queries with LangGraph workflow"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add shared and src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from shared.common import setup_logger, get_config, HealthResponse, RAGQueryRequest, RAGQueryResponse
from shared.common.config import RAGServiceConfig
from rag_system import RAGServiceSystem
from langchain_core.documents import Document

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: RAGServiceConfig = get_config("rag")
logger.info(f"Starting RAG Service")

# Constants
SERVICE_NAME = "rag-service"
SERVICE_VERSION = "1.0.0"

# Initialize RAG system
rag_system = None


def format_documents(docs: list[Document]) -> list[dict]:
    """Format documents for API response"""
    return [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in docs
    ]


async def initialize_rag_system(raise_on_error: bool = False) -> bool:
    """
    Initialize RAG system.
    
    Args:
        raise_on_error: If True, raise exception on failure. If False, log and continue.
    
    Returns:
        True if successful, False otherwise
    """
    global rag_system
    try:
        logger.info("Initializing RAG system...")
        rag_system = RAGServiceSystem(config)
        await rag_system.initialize()
        logger.info("RAG system initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}", exc_info=True)
        if raise_on_error:
            raise HTTPException(
                status_code=503,
                detail=f"RAG system initialization failed: {str(e)}"
            )
        logger.warning("Service will start but RAG initialization will be deferred")
        return False


def check_rag_system_initialized() -> None:
    """Check if RAG system is initialized, raise if not"""
    if rag_system is None:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    await initialize_rag_system(raise_on_error=False)
    
    yield
    
    # Shutdown
    if rag_system is not None:
        logger.info("Shutting down RAG system...")


# Initialize FastAPI app
app = FastAPI(
    title="RAG Service",
    description="RAG and LangGraph workflow service",
    version=SERVICE_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="initializing" if rag_system is None else "healthy",
        service=SERVICE_NAME,
        version=SERVICE_VERSION
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
    global rag_system
    
    # Lazy initialization if needed
    if rag_system is None:
        await initialize_rag_system(raise_on_error=True)
    
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
            context = format_documents(docs)
        
        return RAGQueryResponse(
            answer=answer,
            context=context
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions
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
    check_rag_system_initialized()
    
    try:
        docs = await rag_system.get_relevant_documents(question, k=k)
        return {"documents": format_documents(docs)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get vector database statistics"""
    check_rag_system_initialized()
    
    try:
        stats = await rag_system.get_stats()
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)
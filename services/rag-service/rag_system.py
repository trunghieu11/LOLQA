"""RAG Service System - Adapts existing RAG system for service use"""
import sys
import os
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import httpx
from shared.common.logging import logger
from shared.common.config import RAGServiceConfig
from shared.common.models import ChatRequest, ChatMessage
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool

# Import existing code
from src.core.workflow import LoLQAGraph
from src.config.constants import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY,
    ERROR_RAG_NOT_INITIALIZED,
    MSG_LOADING_VECTOR_STORE,
    MSG_CREATING_VECTOR_STORE,
    MSG_VECTOR_STORE_CREATED
)


class LLMServiceClient:
    """Client for calling LLM Service"""
    
    def __init__(self, llm_service_url: str):
        self.llm_service_url = llm_service_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Call LLM service for chat completion"""
        response = await self.client.post(
            f"{self.llm_service_url}/chat",
            json={
                "messages": messages,
                **kwargs
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["content"]
    
    async def embeddings(self, texts: List[str]) -> List[List[float]]:
        """Call LLM service for embeddings"""
        response = await self.client.post(
            f"{self.llm_service_url}/embeddings",
            json={"texts": texts}
        )
        response.raise_for_status()
        result = response.json()
        return result["embeddings"]
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class RAGServiceSystem:
    """RAG System adapted for microservice architecture"""
    
    def __init__(self, config: RAGServiceConfig):
        """
        Initialize RAG service system.
        
        Args:
            config: RAG service configuration
        """
        self.config = config
        self.llm_client = LLMServiceClient(config.llm_service_url)
        self.vectorstore: Optional[Chroma] = None
        self.retriever: Optional[Any] = None
        self.workflow: Optional[LoLQAGraph] = None
        self.embeddings: Optional[OpenAIEmbeddings] = None
    
    async def initialize(self):
        """Initialize the RAG system"""
        try:
            logger.info("Initializing RAG system...")
            
            # Initialize embeddings (using LLM service)
            # For now, we'll use OpenAI embeddings directly
            # In production, you might want to call LLM service for embeddings
            import os
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY is required for embeddings")
            
            self.embeddings = OpenAIEmbeddings(api_key=openai_key)
            logger.info("Embeddings initialized")
            
            # Load or create vector store
            import os as os_module
            if os_module.path.exists(self.config.vector_db_path):
                logger.info(MSG_LOADING_VECTOR_STORE)
                await self._load_vector_store()
            else:
                logger.info(MSG_CREATING_VECTOR_STORE)
                # Note: Vector store creation should be done by data pipeline service
                # For now, we'll just try to load
                await self._load_vector_store()
            
            # Create retriever
            self._create_retriever()
            
            # Create workflow (simplified - without full RAG system)
            # We'll use a simpler approach for the service
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}", exc_info=True)
            raise
    
    async def _load_vector_store(self):
        """Load existing vector store"""
        self.vectorstore = Chroma(
            persist_directory=self.config.vector_db_path,
            embedding_function=self.embeddings
        )
    
    def _create_retriever(self):
        """Create retriever from vector store"""
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.config.retrieval_k}
        )
        logger.info(f"Retriever created with k={self.config.retrieval_k}")
    
    async def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        k: Optional[int] = None
    ) -> str:
        """
        Process a query using RAG.
        
        Args:
            question: User's question
            conversation_history: Optional conversation history
            k: Number of documents to retrieve
            
        Returns:
            Generated answer
        """
        if not self.retriever:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        try:
            # Retrieve relevant documents
            k = k or self.config.retrieval_k
            docs = self.retriever.invoke(question)
            if isinstance(docs, list) and len(docs) > k:
                docs = docs[:k]
            
            # Format context
            from src.utils import format_documents
            context = format_documents(docs)
            
            # Build messages for LLM
            messages = []
            if conversation_history:
                for msg in conversation_history:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add system message with context
            system_message = f"""You are a helpful assistant specialized in League of Legends knowledge.

CRITICAL INSTRUCTIONS:
- You MUST ONLY use the information provided in the Context section below
- DO NOT use any information from your training data or general knowledge
- If the answer is not in the provided context, explicitly say "I don't have that information in my knowledge base"

Context: {context}"""
            
            messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": question})
            
            # Call LLM service
            answer = await self.llm_client.chat(messages=messages)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            raise
    
    async def get_relevant_documents(self, question: str, k: Optional[int] = None) -> List[Document]:
        """
        Get relevant documents for a question.
        
        Args:
            question: User's question
            k: Number of documents to retrieve
            
        Returns:
            List of relevant Document objects
        """
        if not self.retriever:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        k = k or self.config.retrieval_k
        logger.debug(f"Retrieving {k} documents for question: {question[:50]}...")
        
        try:
            docs = self.retriever.invoke(question)
            if isinstance(docs, list):
                return docs[:k] if len(docs) > k else docs
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}", exc_info=True)
            raise
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get vector database statistics"""
        if not self.vectorstore:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        try:
            # Get collection count
            collection = self.vectorstore._collection
            count = collection.count() if hasattr(collection, 'count') else 0
            
            return {
                "total_documents": count,
                "vector_db_path": self.config.vector_db_path,
                "retrieval_k": self.config.retrieval_k
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {"error": str(e)}


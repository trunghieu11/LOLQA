"""Data Pipeline - Handles data collection, chunking, and ingestion"""
import sys
import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import httpx
from shared.common.logging import logger
from shared.common.config import DataPipelineConfig
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import existing data collection code
from src.data.collector import LoLDataCollector


class LLMServiceClient:
    """Client for calling LLM Service for embeddings"""
    
    def __init__(self, llm_service_url: str):
        self.llm_service_url = llm_service_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=300.0)  # Longer timeout for embeddings
    
    async def embeddings(self, texts: List[str]) -> List[List[float]]:
        """Call LLM service for embeddings"""
        # Batch embeddings in chunks to avoid timeout
        batch_size = 100
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = await self.client.post(
                f"{self.llm_service_url}/embeddings",
                json={"texts": batch}
            )
            response.raise_for_status()
            result = response.json()
            all_embeddings.extend(result["embeddings"])
        
        return all_embeddings
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class DataPipeline:
    """Data pipeline for collection, chunking, and ingestion"""
    
    def __init__(self, config: DataPipelineConfig):
        """
        Initialize data pipeline.
        
        Args:
            config: Data pipeline configuration
        """
        self.config = config
        self.llm_client = LLMServiceClient(config.llm_service_url)
        self.data_collector = LoLDataCollector(data_dir=config.data_directory)
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.vectorstore: Optional[Chroma] = None
    
    async def initialize(self):
        """Initialize embeddings and vector store"""
        try:
            # Initialize embeddings
            # For now, use OpenAI directly (can be changed to use LLM service)
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_API_KEY is required for embeddings")
            
            self.embeddings = OpenAIEmbeddings(api_key=openai_key)
            logger.info("Embeddings initialized")
            
            # Initialize or load vector store
            if os.path.exists(self.config.vector_db_path):
                self.vectorstore = Chroma(
                    persist_directory=self.config.vector_db_path,
                    embedding_function=self.embeddings
                )
                logger.info("Loaded existing vector store")
            else:
                # Will be created when we add documents
                logger.info("Vector store will be created on first ingestion")
            
        except Exception as e:
            logger.error(f"Error initializing pipeline: {e}", exc_info=True)
            raise
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.llm_client.close()
    
    async def run(
        self,
        sources: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Run the full data pipeline.
        
        Args:
            sources: Optional list of source names to use
            force_refresh: Force refresh even if data exists
            
        Returns:
            Pipeline result with statistics
        """
        try:
            logger.info("Starting data pipeline...")
            
            # Step 1: Collect data
            logger.info("Step 1: Collecting data...")
            documents = self.data_collector.get_documents()
            logger.info(f"Collected {len(documents)} documents")
            
            if not documents:
                raise ValueError("No documents collected")
            
            # Step 2: Chunk documents
            logger.info("Step 2: Chunking documents...")
            chunk_size = getattr(self.config, 'chunk_size', 1000)
            chunk_overlap = getattr(self.config, 'chunk_overlap', 200)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
            )
            splits = text_splitter.split_documents(documents)
            logger.info(f"Created {len(splits)} chunks from {len(documents)} documents")
            
            # Step 3: Initialize or update vector store
            if self.vectorstore is None:
                # Create new vector store
                os.makedirs(self.config.vector_db_path, exist_ok=True)
                self.vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=self.config.vector_db_path
                )
                logger.info(f"Created new vector store with {len(splits)} chunks")
            elif force_refresh:
                # Clear and recreate existing store
                if os.path.exists(self.config.vector_db_path):
                    shutil.rmtree(self.config.vector_db_path)
                
                self.vectorstore = Chroma.from_documents(
                    documents=splits,
                    embedding=self.embeddings,
                    persist_directory=self.config.vector_db_path
                )
                logger.info(f"Refreshed vector store with {len(splits)} chunks")
            else:
                # Add to existing store
                # Note: This is a simplified approach. In production, you might want
                # to check for duplicates or update existing documents
                self.vectorstore.add_documents(splits)
                logger.info(f"Added {len(splits)} chunks to existing vector store")
            
            return {
                "documents": len(documents),
                "chunks": len(splits),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error in data pipeline: {e}", exc_info=True)
            raise


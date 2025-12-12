"""
RAG System for League of Legends Q&A
Handles vector store creation, embeddings, and retrieval
"""
import os
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from data_collector import LoLDataCollector
from config import config
from constants import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY,
    ERROR_RAG_NOT_INITIALIZED,
    MSG_LOADING_VECTOR_STORE,
    MSG_CREATING_VECTOR_STORE,
    MSG_VECTOR_STORE_CREATED
)
from utils import logger, format_documents


class LoLRAGSystem:
    """RAG system for League of Legends knowledge base"""
    
    def __init__(self, persist_directory: Optional[str] = None, data_collector: Optional[LoLDataCollector] = None):
        """
        Initialize the RAG system.
        
        Args:
            persist_directory: Directory to persist vector store (defaults to config)
            data_collector: Optional custom data collector instance
        """
        self.persist_directory = persist_directory or config.rag.persist_directory
        self.data_collector = data_collector or LoLDataCollector()
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.vectorstore: Optional[Chroma] = None
        self.llm: Optional[ChatOpenAI] = None
        self.retriever: Optional[Chroma] = None
        self.qa_chain: Optional[object] = None
        
    def initialize(self):
        """Initialize the RAG system with embeddings and vector store"""
        try:
            logger.info("Initializing RAG system...")
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings()
            logger.info("Embeddings initialized")
            
            # Initialize LLM
            llm_kwargs = {
                "model": config.llm.model,
                "temperature": config.llm.temperature,
            }
            if config.llm.max_tokens:
                llm_kwargs["max_tokens"] = config.llm.max_tokens
            
            self.llm = ChatOpenAI(**llm_kwargs)
            logger.info(f"LLM initialized: {config.llm.model}")
            
            # Load or create vector store
            if os.path.exists(self.persist_directory):
                logger.info(MSG_LOADING_VECTOR_STORE)
                self._load_vector_store()
            else:
                logger.info(MSG_CREATING_VECTOR_STORE)
                self._create_vector_store()
            
            # Create retriever
            self._create_retriever()
            
            # Create QA chain
            self._create_qa_chain()
            
            # Create QA chain with history support
            self._create_qa_chain_with_history()
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}", exc_info=True)
            raise
    
    def _load_vector_store(self):
        """Load existing vector store"""
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def _create_vector_store(self):
        """Create new vector store from documents"""
        # Collect data
        documents = self.data_collector.get_documents()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        logger.info(MSG_VECTOR_STORE_CREATED.format(count=len(splits)))
    
    def _create_retriever(self):
        """Create retriever from vector store"""
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.rag.retrieval_k}
        )
        logger.info(f"Retriever created with k={config.rag.retrieval_k}")
    
    def _create_qa_chain(self):
        """Create the QA chain"""
        prompt = ChatPromptTemplate.from_template(DEFAULT_PROMPT_TEMPLATE)
        
        # Create the chain using LCEL
        self.qa_chain = (
            {
                "context": self.retriever,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("QA chain created")
    
    def _create_qa_chain_with_history(self):
        """Create the QA chain with conversation history support"""
        prompt = ChatPromptTemplate.from_template(DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY)
        
        # Create the chain using LCEL with history
        self.qa_chain_with_history = (
            {
                "context": self.retriever,
                "chat_history": RunnablePassthrough(),
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("QA chain with history created")
        
    def query(self, question: str, chat_history: Optional[str] = None) -> str:
        """
        Query the RAG system.
        
        Args:
            question: User's question
            chat_history: Optional conversation history string
            
        Returns:
            Generated answer string
            
        Raises:
            ValueError: If RAG system not initialized
        """
        if not self.qa_chain:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        logger.info(f"Processing query: {question[:50]}...")
        try:
            # Use chain with history if history is provided
            if chat_history and hasattr(self, 'qa_chain_with_history'):
                answer = self.qa_chain_with_history.invoke({
                    "question": question,
                    "chat_history": chat_history
                })
            else:
                answer = self.qa_chain.invoke(question)
            logger.info("Query processed successfully")
            return answer
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            raise
    
    def get_relevant_documents(self, question: str, k: Optional[int] = None) -> List[Document]:
        """
        Get relevant documents for a question.
        
        Args:
            question: User's question
            k: Number of documents to retrieve (defaults to config value)
            
        Returns:
            List of relevant Document objects
            
        Raises:
            ValueError: If RAG system not initialized
        """
        if not self.retriever:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        k = k or config.rag.retrieval_k
        logger.debug(f"Retrieving {k} documents for question: {question[:50]}...")
        
        # In LangChain 1.x, retrievers are Runnables and use invoke()
        # Try invoke() first, fallback to get_relevant_documents() for compatibility
        try:
            docs = self.retriever.invoke(question)
            # If invoke returns a list, use it; otherwise try with k parameter
            if isinstance(docs, list):
                return docs[:k] if len(docs) > k else docs
            return self.retriever.get_relevant_documents(question, k=k)
        except (AttributeError, TypeError):
            # Fallback for older API
            return self.retriever.get_relevant_documents(question)


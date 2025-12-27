"""
Utility functions for the League of Legends Q&A application.
Shared helper functions used across modules.
"""
import logging
import sys
from typing import List, Optional
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)


def format_documents(documents: List[Document], include_metadata: bool = False) -> str:
    """
    Format a list of documents into a readable string.
    
    Args:
        documents: List of Document objects
        include_metadata: Whether to include metadata in the output
        
    Returns:
        Formatted string representation of documents
    """
    if not documents:
        return "No relevant documents found."
    
    formatted_parts = []
    for i, doc in enumerate(documents, 1):
        part = f"[Source {i}]\n{doc.page_content}\n"
        if include_metadata and doc.metadata:
            part += f"Metadata: {doc.metadata}\n"
        formatted_parts.append(part)
    
    return "\n".join(formatted_parts)


def validate_question(question: str, min_length: int = 3) -> tuple[bool, Optional[str]]:
    """
    Validate a user question.
    
    Args:
        question: The question to validate
        min_length: Minimum required length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not question:
        return False, "Question cannot be empty"
    
    if len(question.strip()) < min_length:
        return False, f"Question must be at least {min_length} characters long"
    
    return True, None


def safe_get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Safely get an environment variable.
    
    Args:
        key: Environment variable key
        default: Default value if not found
        
    Returns:
        Environment variable value or default
    """
    import os
    return os.getenv(key, default)


def setup_logging(level: str = "INFO"):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('app.log')
        ]
    )


def log_error(error: Exception, context: str = ""):
    """
    Log an error with context.
    
    Args:
        error: The exception that occurred
        context: Additional context about where the error occurred
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)


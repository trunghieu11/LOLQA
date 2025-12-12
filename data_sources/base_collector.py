"""
Base data collector interface.
All data collectors should inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import List
from langchain_core.documents import Document
from utils import logger


class BaseDataCollector(ABC):
    """Base class for all data collectors"""
    
    @abstractmethod
    def collect(self) -> List[Document]:
        """
        Collect data and return as Document objects.
        
        Returns:
            List of Document objects
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this data collector.
        
        Returns:
            Collector name
        """
        pass
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate if the collector can run (API keys, etc.).
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None


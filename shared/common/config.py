"""Shared configuration for microservices"""
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ServiceConfig:
    """Base service configuration"""
    service_name: str
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    log_file: Optional[str] = None


@dataclass
class LLMServiceConfig(ServiceConfig):
    """LLM Service configuration"""
    backend: str = "openai"  # openai, vllm, anthropic
    openai_api_key: Optional[str] = None
    vllm_endpoint: Optional[str] = None
    default_model: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@dataclass
class RAGServiceConfig(ServiceConfig):
    """RAG Service configuration"""
    llm_service_url: str = "http://llm-service:8000"
    vector_db_path: str = "./chroma_db"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_k: int = 3


@dataclass
class DataPipelineConfig(ServiceConfig):
    """Data Pipeline Service configuration"""
    llm_service_url: str = "http://llm-service:8000"
    vector_db_path: str = "./chroma_db"
    data_directory: str = "./data"
    use_data_dragon: bool = True
    use_web_scraper: bool = True
    use_riot_api: bool = False
    use_sample_data: bool = True


@dataclass
class UIServiceConfig(ServiceConfig):
    """UI Service configuration"""
    rag_service_url: str = "http://rag-service:8000"
    port: int = 8501  # Streamlit default


def get_config(service_name: str) -> ServiceConfig:
    """
    Get configuration for a service.
    
    Args:
        service_name: Name of the service (llm, rag, data-pipeline, ui)
        
    Returns:
        Service configuration object
    """
    if service_name == "llm":
        return LLMServiceConfig(
            service_name="llm-service",
            host=os.getenv("LLM_SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("LLM_SERVICE_PORT", "8000")),
            backend=os.getenv("LLM_BACKEND", "openai"),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            vllm_endpoint=os.getenv("VLLM_ENDPOINT", "http://vllm-service:8000/v1"),
            default_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    elif service_name == "rag":
        return RAGServiceConfig(
            service_name="rag-service",
            host=os.getenv("RAG_SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("RAG_SERVICE_PORT", "8000")),
            llm_service_url=os.getenv("LLM_SERVICE_URL", "http://llm-service:8000"),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./chroma_db"),
            chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "200")),
            retrieval_k=int(os.getenv("RAG_RETRIEVAL_K", "3")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    elif service_name == "data-pipeline":
        return DataPipelineConfig(
            service_name="data-pipeline-service",
            host=os.getenv("DATA_PIPELINE_SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("DATA_PIPELINE_SERVICE_PORT", "8000")),
            llm_service_url=os.getenv("LLM_SERVICE_URL", "http://llm-service:8000"),
            vector_db_path=os.getenv("VECTOR_DB_PATH", "./chroma_db"),
            data_directory=os.getenv("DATA_DIRECTORY", "./data"),
            use_data_dragon=os.getenv("USE_DATA_DRAGON", "true").lower() == "true",
            use_web_scraper=os.getenv("USE_WEB_SCRAPER", "true").lower() == "true",
            use_riot_api=os.getenv("USE_RIOT_API", "false").lower() == "true",
            use_sample_data=os.getenv("USE_SAMPLE_DATA", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    elif service_name == "ui":
        return UIServiceConfig(
            service_name="ui-service",
            host=os.getenv("UI_SERVICE_HOST", "0.0.0.0"),
            port=int(os.getenv("UI_SERVICE_PORT", "8501")),
            rag_service_url=os.getenv("RAG_SERVICE_URL", "http://rag-service:8000"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    else:
        return ServiceConfig(service_name=service_name)


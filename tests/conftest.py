"""
Pytest configuration and shared fixtures
"""
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from langchain_core.documents import Document

# Set test environment
os.environ["TESTING"] = "true"
os.environ["OPENAI_API_KEY"] = "test-key-for-testing"
os.environ["LANGSMITH_TRACING"] = "false"


@pytest.fixture
def project_root():
    """Get project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture
def test_data_dir(project_root):
    """Get test data directory"""
    return project_root / "tests" / "data"


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings"""
    mock = MagicMock()
    mock.embed_query.return_value = [0.1] * 1536
    mock.embed_documents.return_value = [[0.1] * 1536]
    return mock


@pytest.fixture
def mock_openai_llm():
    """Mock OpenAI LLM"""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Test response")
    return mock


@pytest.fixture
def mock_vectorstore():
    """Mock ChromaDB vector store"""
    mock = MagicMock()
    mock.add_documents.return_value = None
    mock.get.return_value = {
        'documents': ['Test document content'],
        'metadatas': [{'type': 'test', 'source': 'test'}],
        'ids': ['test-id']
    }
    mock.similarity_search.return_value = [
        Document(page_content="Test content", metadata={"type": "test"})
    ]
    return mock


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        Document(
            page_content="Yasuo is a skilled swordsman champion.",
            metadata={"champion": "Yasuo", "role": "Fighter", "type": "champion"}
        ),
        Document(
            page_content="Ahri is a nine-tailed fox mage.",
            metadata={"champion": "Ahri", "role": "Mage", "type": "champion"}
        ),
        Document(
            page_content="Jinx is a marksman champion.",
            metadata={"champion": "Jinx", "role": "Marksman", "type": "champion"}
        ),
    ]


@pytest.fixture
def sample_champion_data():
    """Sample champion data for testing"""
    return {
        "name": "Yasuo",
        "title": "The Unforgiven",
        "role": "Fighter",
        "description": "A skilled swordsman",
        "abilities": {
            "Q": "Steel Tempest",
            "W": "Wind Wall",
            "E": "Sweeping Blade",
            "R": "Last Breath"
        }
    }


@pytest.fixture
def mock_data_collector():
    """Mock data collector"""
    mock = MagicMock()
    mock.get_documents.return_value = [
        Document(
            page_content="Test champion data",
            metadata={"type": "champion", "champion": "TestChamp"}
        )
    ]
    return mock


@pytest.fixture
def mock_rag_system(mock_vectorstore, mock_openai_llm):
    """Mock RAG system"""
    mock = MagicMock()
    mock.vectorstore = mock_vectorstore
    mock.llm = mock_openai_llm
    mock.query.return_value = "Test answer"
    mock.get_relevant_documents.return_value = [
        Document(page_content="Test", metadata={"type": "test"})
    ]
    return mock


@pytest.fixture
def mock_workflow(mock_rag_system):
    """Mock LangGraph workflow"""
    mock = MagicMock()
    mock.rag_system = mock_rag_system
    mock.invoke.return_value = "Test workflow response"
    return mock


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test"""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def clean_chroma_db(tmp_path):
    """Create a temporary ChromaDB directory"""
    db_path = tmp_path / "test_chroma_db"
    db_path.mkdir()
    return str(db_path)


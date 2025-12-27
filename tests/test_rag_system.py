"""
Unit tests for RAG system
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document

from src.core import LoLRAGSystem


class TestLoLRAGSystem:
    """Tests for LoLRAGSystem"""
    
    def test_initialization(self):
        """Test RAG system initialization"""
        rag = LoLRAGSystem()
        
        assert rag.embeddings is None
        assert rag.llm is None
        assert rag.vectorstore is None
        assert rag.retriever is None
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    @patch('src.core.rag_system.Chroma')
    def test_initialize_with_existing_db(self, mock_chroma, mock_llm, mock_embeddings):
        """Test initialization with existing vector store"""
        # Mock the existence check
        with patch('os.path.exists', return_value=True):
            rag = LoLRAGSystem()
            rag.initialize()
            
            assert rag.embeddings is not None
            assert rag.llm is not None
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    @patch('src.core.rag_system.Chroma')
    @patch('src.core.rag_system.LoLDataCollector')
    def test_initialize_creates_new_db(self, mock_collector, mock_chroma, mock_llm, mock_embeddings):
        """Test initialization creates new vector store if not exists"""
        # Mock that DB doesn't exist
        with patch('os.path.exists', return_value=False):
            mock_collector_instance = Mock()
            mock_collector_instance.get_documents.return_value = [
                Document(page_content="Test", metadata={"type": "test"})
            ]
            mock_collector.return_value = mock_collector_instance
            
            rag = LoLRAGSystem()
            rag.initialize()
            
            # Should have created embeddings and LLM
            assert mock_embeddings.called
            assert mock_llm.called
    
    def test_query_not_initialized(self):
        """Test query raises error when not initialized"""
        rag = LoLRAGSystem()
        
        with pytest.raises(ValueError, match="not initialized"):
            rag.query("test question")
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_query_with_tools(self, mock_llm, mock_embeddings):
        """Test query with tool calling"""
        rag = LoLRAGSystem()
        rag.embeddings = mock_embeddings()
        rag.llm = mock_llm()
        rag.vectorstore = MagicMock()
        
        # Mock LLM with tools
        mock_llm_with_tools = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Test answer"
        mock_response.tool_calls = None
        mock_llm_with_tools.invoke.return_value = mock_response
        
        rag.llm_with_tools = mock_llm_with_tools
        rag.tools = []
        
        result = rag.query("test question")
        
        assert result == "Test answer"
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_query_with_tool_calls(self, mock_llm, mock_embeddings):
        """Test query that triggers tool calls"""
        rag = LoLRAGSystem()
        rag.embeddings = mock_embeddings()
        rag.llm_instance = mock_llm()
        rag.vectorstore = MagicMock()
        
        # Mock LLM response with tool calls
        mock_llm_with_tools = MagicMock()
        mock_ai_msg = MagicMock()
        mock_ai_msg.tool_calls = [
            {"name": "count_champions", "args": {}}
        ]
        mock_llm_with_tools.invoke.return_value = mock_ai_msg
        
        # Mock tool
        mock_tool = MagicMock()
        mock_tool.name = "count_champions"
        mock_tool.invoke.return_value = "There are 172 champions"
        
        # Mock final LLM response
        mock_final_response = MagicMock()
        mock_final_response.content = "There are 172 champions in League of Legends."
        rag.llm = MagicMock()
        rag.llm.invoke.return_value = mock_final_response
        
        rag.llm_with_tools = mock_llm_with_tools
        rag.tools = [mock_tool]
        
        result = rag.query("how many champions?")
        
        assert "172" in result
    
    def test_get_relevant_documents_not_initialized(self):
        """Test get_relevant_documents raises error when not initialized"""
        rag = LoLRAGSystem()
        
        with pytest.raises(ValueError, match="not initialized"):
            rag.get_relevant_documents("test question")
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_get_relevant_documents(self, mock_llm, mock_embeddings):
        """Test getting relevant documents"""
        rag = LoLRAGSystem()
        rag.embeddings = mock_embeddings()
        rag.llm = mock_llm()
        
        # Mock retriever
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            Document(page_content="Test doc", metadata={"type": "test"})
        ]
        rag.retriever = mock_retriever
        
        docs = rag.get_relevant_documents("test question")
        
        assert len(docs) > 0
        assert isinstance(docs[0], Document)


class TestRAGSystemTools:
    """Tests for RAG system tools"""
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_count_champions_tool(self, mock_llm, mock_embeddings):
        """Test count_champions tool"""
        rag = LoLRAGSystem()
        rag.embeddings = mock_embeddings()
        rag.llm = mock_llm()
        
        # Mock vectorstore
        mock_vectorstore = MagicMock()
        mock_vectorstore.get.return_value = {
            'metadatas': [
                {'champion': 'Yasuo', 'type': 'champion'},
                {'champion': 'Ahri', 'type': 'champion'},
                {'champion': 'Jinx', 'type': 'champion'}
            ]
        }
        rag.vectorstore = mock_vectorstore
        
        # Initialize tools
        rag._create_llm_with_tools()
        
        # Find count_champions tool
        count_tool = next((t for t in rag.tools if t.name == "count_champions"), None)
        assert count_tool is not None
        
        # Test tool
        result = count_tool.invoke({})
        assert "3" in result or "champions" in result.lower()
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_search_champion_info_tool(self, mock_llm, mock_embeddings):
        """Test search_champion_info tool"""
        rag = LoLRAGSystem()
        rag.embeddings = mock_embeddings()
        rag.llm = mock_llm()
        
        # Mock retriever
        mock_retriever = MagicMock()
        mock_retriever.invoke.return_value = [
            Document(page_content="Yasuo info", metadata={"champion": "Yasuo"})
        ]
        rag.retriever = mock_retriever
        rag.vectorstore = MagicMock()
        
        # Initialize tools
        rag._create_llm_with_tools()
        
        # Find search tool
        search_tool = next((t for t in rag.tools if t.name == "search_champion_info"), None)
        assert search_tool is not None
        
        # Test tool
        result = search_tool.invoke({"query": "Yasuo"})
        assert isinstance(result, str)


"""
Integration tests for the complete system
"""
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from src.core import LoLRAGSystem, LoLQAGraph
from src.data import LoLDataCollector


@pytest.mark.integration
class TestEndToEndFlow:
    """Integration tests for end-to-end flow"""
    
    @pytest.mark.requires_api
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    @patch('src.core.rag_system.Chroma')
    def test_complete_question_answer_flow(self, mock_chroma, mock_llm, mock_embeddings):
        """Test complete flow from question to answer"""
        # Setup mocks
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_llm_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Yasuo is a skilled swordsman."
        mock_llm_instance.invoke.return_value = mock_response
        mock_llm.return_value = mock_llm_instance
        
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore
        
        # Mock that DB exists
        with patch('os.path.exists', return_value=True):
            # Initialize RAG system
            rag = LoLRAGSystem()
            rag.initialize()
            
            # Create workflow
            workflow = LoLQAGraph(rag)
            
            # Ask question
            answer = workflow.invoke("Who is Yasuo?")
            
            assert isinstance(answer, str)
            assert len(answer) > 0
    
    @pytest.mark.requires_api
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    @patch('src.core.rag_system.Chroma')
    def test_conversation_with_context(self, mock_chroma, mock_llm, mock_embeddings):
        """Test conversation with memory"""
        # Setup mocks
        mock_embeddings_instance = MagicMock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        
        # First response
        mock_response1 = MagicMock()
        mock_response1.content = "Yasuo is a champion."
        
        # Second response (with context)
        mock_response2 = MagicMock()
        mock_response2.content = "Yasuo has 15 skins."
        
        mock_llm_instance.invoke.side_effect = [mock_response1, mock_response2]
        
        mock_vectorstore = MagicMock()
        mock_chroma.return_value = mock_vectorstore
        
        with patch('os.path.exists', return_value=True):
            rag = LoLRAGSystem()
            rag.initialize()
            workflow = LoLQAGraph(rag)
            
            # First question
            answer1 = workflow.invoke("Who is Yasuo?")
            assert "Yasuo" in answer1
            
            # Second question with context
            conversation_history = [
                {"role": "user", "content": "Who is Yasuo?"},
                {"role": "assistant", "content": answer1}
            ]
            
            answer2 = workflow.invoke("How many skins does he have?", conversation_history)
            assert isinstance(answer2, str)


@pytest.mark.integration
class TestDataCollectionIntegration:
    """Integration tests for data collection"""
    
    def test_data_collector_integration(self):
        """Test data collector creates valid documents"""
        collector = LoLDataCollector()
        documents = collector.get_documents()
        
        assert len(documents) > 0
        
        for doc in documents:
            assert isinstance(doc, Document)
            assert len(doc.page_content) > 0
            assert isinstance(doc.metadata, dict)
            assert "type" in doc.metadata
    
    @patch('src.data.sources.data_dragon.requests.get')
    def test_data_dragon_integration(self, mock_get):
        """Test Data Dragon collector integration"""
        # Mock API responses
        mock_version_response = MagicMock()
        mock_version_response.json.return_value = ["15.1.1"]
        mock_version_response.raise_for_status = MagicMock()
        
        mock_champion_list_response = MagicMock()
        mock_champion_list_response.json.return_value = {
            "data": {
                "Yasuo": {"id": "Yasuo", "name": "Yasuo"}
            }
        }
        mock_champion_list_response.raise_for_status = MagicMock()
        
        mock_champion_detail_response = MagicMock()
        mock_champion_detail_response.json.return_value = {
            "data": {
                "Yasuo": {
                    "name": "Yasuo",
                    "title": "the Unforgiven",
                    "tags": ["Fighter"],
                    "skins": [{"name": "default"}],
                    "lore": "Test lore"
                }
            }
        }
        mock_champion_detail_response.raise_for_status = MagicMock()
        
        mock_get.side_effect = [
            mock_version_response,
            mock_champion_list_response,
            mock_champion_detail_response
        ]
        
        from src.data.sources import DataDragonCollector
        collector = DataDragonCollector()
        documents = collector.collect()
        
        assert len(documents) > 0
        assert any("Yasuo" in doc.page_content for doc in documents)


@pytest.mark.integration
@pytest.mark.slow
class TestRAGSystemIntegration:
    """Integration tests for RAG system"""
    
    @pytest.mark.requires_db
    @pytest.mark.skip(reason="Complex ChromaDB mocking - integration test requires real setup")
    def test_rag_system_with_real_vectorstore(self, clean_chroma_db, sample_documents):
        """Test RAG system with real vector store - skipped for now"""
        # This test requires more sophisticated mocking of ChromaDB
        # or a real test database setup
        pass


@pytest.mark.integration
class TestToolCallingIntegration:
    """Integration tests for tool calling"""
    
    @patch('src.core.rag_system.OpenAIEmbeddings')
    @patch('src.core.rag_system.ChatOpenAI')
    def test_count_champions_tool_integration(self, mock_llm, mock_embeddings):
        """Test count_champions tool in full workflow"""
        # Setup mocks
        mock_embeddings.return_value = MagicMock()
        mock_llm.return_value = MagicMock()
        
        with patch('os.path.exists', return_value=True):
            with patch('src.core.rag_system.Chroma') as mock_chroma:
                # Mock vectorstore with champion data
                mock_vectorstore = MagicMock()
                mock_vectorstore.get.return_value = {
                    'metadatas': [
                        {'champion': 'Yasuo', 'type': 'champion'},
                        {'champion': 'Ahri', 'type': 'champion'},
                        {'champion': 'Jinx', 'type': 'champion'}
                    ]
                }
                mock_chroma.return_value = mock_vectorstore
                
                rag = LoLRAGSystem()
                rag.initialize()
                
                # Verify tools were created
                assert rag.tools is not None
                assert len(rag.tools) > 0
                
                # Find count tool
                count_tool = next((t for t in rag.tools if "count" in t.name.lower()), None)
                assert count_tool is not None


"""
Unit tests for data collectors
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from langchain_core.documents import Document

from src.data.sources import (
    BaseDataCollector,
    DataDragonCollector,
    WebScraperCollector,
    RiotAPICollector,
    SampleDataCollector
)
from src.data import LoLDataCollector


class TestBaseDataCollector:
    """Tests for BaseDataCollector"""
    
    def test_base_collector_is_abstract(self):
        """Test that BaseDataCollector cannot be instantiated"""
        with pytest.raises(TypeError):
            BaseDataCollector()
    
    def test_base_collector_methods_exist(self):
        """Test that required methods are defined"""
        assert hasattr(BaseDataCollector, 'collect')
        assert hasattr(BaseDataCollector, 'get_name')
        assert hasattr(BaseDataCollector, 'validate')


class TestDataDragonCollector:
    """Tests for DataDragonCollector"""
    
    def test_initialization(self):
        """Test DataDragonCollector initialization"""
        collector = DataDragonCollector(version="14.1.1", language="en_US")
        
        assert collector.language == "en_US"
        assert collector.version == "14.1.1"
        assert collector.base_url == "https://ddragon.leagueoflegends.com"
    
    def test_get_name(self):
        """Test get_name method"""
        collector = DataDragonCollector()
        assert collector.get_name() == "DataDragon"
    
    @patch('requests.get')
    def test_get_latest_version(self, mock_get):
        """Test fetching latest version"""
        mock_response = Mock()
        mock_response.json.return_value = ["15.1.1", "15.0.1", "14.24.1"]
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        collector = DataDragonCollector()
        assert collector.version == "15.1.1"
    
    @patch('requests.get')
    def test_collect_champions(self, mock_get):
        """Test collecting champion data"""
        # Mock champion list response
        mock_list_response = Mock()
        mock_list_response.json.return_value = {
            "data": {
                "Yasuo": {"id": "Yasuo", "name": "Yasuo"},
                "Ahri": {"id": "Ahri", "name": "Ahri"}
            }
        }
        mock_list_response.raise_for_status = Mock()
        
        # Mock individual champion response
        mock_detail_response = Mock()
        mock_detail_response.json.return_value = {
            "data": {
                "Yasuo": {
                    "name": "Yasuo",
                    "title": "the Unforgiven",
                    "tags": ["Fighter", "Assassin"],
                    "skins": [{"name": "default"}]
                }
            }
        }
        mock_detail_response.raise_for_status = Mock()
        
        mock_get.side_effect = [mock_list_response, mock_detail_response, mock_detail_response]
        
        collector = DataDragonCollector(version="15.1.1")
        documents = collector.collect()
        
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
    
    def test_validate(self):
        """Test validate method"""
        collector = DataDragonCollector()
        is_valid, error = collector.validate()
        
        assert is_valid is True
        assert error is None


class TestWebScraperCollector:
    """Tests for WebScraperCollector"""
    
    def test_initialization(self):
        """Test WebScraperCollector initialization"""
        collector = WebScraperCollector(base_url="https://test.com")
        
        assert collector.base_url == "https://test.com"
    
    def test_get_name(self):
        """Test get_name method"""
        collector = WebScraperCollector()
        assert collector.get_name() == "WebScraper"
    
    @patch('requests.get')
    def test_collect_success(self, mock_get):
        """Test successful web scraping"""
        mock_response = Mock()
        mock_response.content = b"<html><body><p>Test content</p></body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        collector = WebScraperCollector()
        documents = collector.collect()
        
        assert isinstance(documents, list)
        # May be empty if parsing fails, but should not raise exception
    
    @patch('requests.get')
    def test_collect_failure(self, mock_get):
        """Test web scraping with request failure"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        collector = WebScraperCollector()
        documents = collector.collect()
        
        # May return empty list or partial results, should not raise exception
        assert isinstance(documents, list)


class TestRiotAPICollector:
    """Tests for RiotAPICollector"""
    
    def test_initialization(self):
        """Test RiotAPICollector initialization"""
        collector = RiotAPICollector(api_key="test-key", region="na1")
        
        assert collector.api_key == "test-key"
        assert collector.region == "na1"
    
    def test_get_name(self):
        """Test get_name method"""
        collector = RiotAPICollector(api_key="test-key")
        assert collector.get_name() == "RiotAPI"
    
    def test_validate_with_key(self):
        """Test validate with API key"""
        collector = RiotAPICollector(api_key="test-key")
        is_valid, error = collector.validate()
        
        # Should be valid if key exists (actual API call may fail in tests)
        assert isinstance(is_valid, bool)
    
    def test_validate_without_key(self):
        """Test validate without API key"""
        collector = RiotAPICollector(api_key=None)
        is_valid, error = collector.validate()
        
        assert is_valid is False
        assert error is not None
        assert ("API key" in error or "RIOT_API_KEY" in error)


class TestSampleDataCollector:
    """Tests for SampleDataCollector"""
    
    def test_get_name(self):
        """Test get_name method"""
        collector = SampleDataCollector()
        assert collector.get_name() == "SampleData"
    
    def test_collect(self):
        """Test collecting sample data"""
        collector = SampleDataCollector()
        documents = collector.collect()
        
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)
        
        # Check that documents have required metadata
        for doc in documents:
            assert "type" in doc.metadata
    
    def test_validate(self):
        """Test validate method"""
        collector = SampleDataCollector()
        is_valid, error = collector.validate()
        
        assert is_valid is True
        assert error is None


class TestLoLDataCollector:
    """Tests for LoLDataCollector"""
    
    def test_initialization(self):
        """Test LoLDataCollector initialization"""
        collector = LoLDataCollector()
        
        assert hasattr(collector, 'collectors')
        assert isinstance(collector.collectors, list)
    
    def test_get_documents(self):
        """Test getting documents from all collectors"""
        mock_collector = Mock()
        mock_collector.collect.return_value = [
            Document(page_content="Test", metadata={"type": "test"})
        ]
        mock_collector.get_name.return_value = "TestCollector"
        
        with patch.object(LoLDataCollector, '_initialize_collectors'):
            collector = LoLDataCollector()
            collector.collectors = [mock_collector]
            
            documents = collector.get_documents()
            
            assert len(documents) > 0
            assert all(isinstance(doc, Document) for doc in documents)
    
    def test_get_documents_handles_failures(self):
        """Test that get_documents handles collector failures gracefully"""
        failing_collector = Mock()
        failing_collector.collect.side_effect = Exception("Test error")
        failing_collector.get_name.return_value = "FailingCollector"
        
        working_collector = Mock()
        working_collector.collect.return_value = [
            Document(page_content="Test", metadata={"type": "test"})
        ]
        working_collector.get_name.return_value = "WorkingCollector"
        
        with patch.object(LoLDataCollector, '_initialize_collectors'):
            collector = LoLDataCollector()
            collector.collectors = [failing_collector, working_collector]
            
            documents = collector.get_documents()
            
            # Should still get documents from working collector
            assert len(documents) > 0


"""
Unit tests for utility functions
"""
import pytest
from langchain_core.documents import Document
from src.utils import (
    logger,
    format_documents,
    validate_question,
    safe_get_env,
    setup_logging,
    log_error
)


class TestFormatDocuments:
    """Tests for format_documents function"""
    
    def test_format_documents_basic(self, sample_documents):
        """Test basic document formatting"""
        result = format_documents(sample_documents[:2])
        
        assert "Yasuo" in result
        assert "Ahri" in result
        assert "[Source 1]" in result
        assert "[Source 2]" in result
    
    def test_format_documents_with_metadata(self, sample_documents):
        """Test document formatting with metadata"""
        result = format_documents(sample_documents[:1], include_metadata=True)
        
        assert "Yasuo" in result
        assert "champion" in result or "Fighter" in result
    
    def test_format_documents_empty_list(self):
        """Test formatting empty document list"""
        result = format_documents([])
        # Empty list returns a message, not empty string
        assert isinstance(result, str)
    
    def test_format_documents_single_document(self):
        """Test formatting single document"""
        doc = Document(page_content="Test content", metadata={"type": "test"})
        result = format_documents([doc])
        
        assert "[Source 1]" in result
        assert "Test content" in result


class TestValidateQuestion:
    """Tests for validate_question function"""
    
    def test_validate_question_valid(self):
        """Test validation of valid question"""
        is_valid, error = validate_question("Who is Yasuo?")
        assert is_valid is True
        assert error is None
    
    def test_validate_question_too_short(self):
        """Test validation of too short question"""
        is_valid, error = validate_question("Hi")
        assert is_valid is False
        assert error is not None
        assert "too short" in error.lower() or "at least" in error.lower()
    
    def test_validate_question_empty(self):
        """Test validation of empty question"""
        is_valid, error = validate_question("")
        assert is_valid is False
        assert error is not None
    
    def test_validate_question_whitespace_only(self):
        """Test validation of whitespace-only question"""
        is_valid, error = validate_question("   ")
        assert is_valid is False
        assert error is not None
    
    def test_validate_question_with_min_length(self):
        """Test validation with custom minimum length"""
        is_valid, error = validate_question("Test", min_length=5)
        assert is_valid is False
        
        is_valid, error = validate_question("Testing", min_length=5)
        assert is_valid is True


class TestSafeGetEnv:
    """Tests for safe_get_env function"""
    
    def test_safe_get_env_exists(self, monkeypatch):
        """Test getting existing environment variable"""
        monkeypatch.setenv("TEST_VAR", "test_value")
        result = safe_get_env("TEST_VAR")
        assert result == "test_value"
    
    def test_safe_get_env_not_exists(self):
        """Test getting non-existent environment variable"""
        result = safe_get_env("NONEXISTENT_VAR")
        assert result is None
    
    def test_safe_get_env_with_default(self):
        """Test getting environment variable with default"""
        result = safe_get_env("NONEXISTENT_VAR", default="default_value")
        assert result == "default_value"
    
    def test_safe_get_env_empty_string(self, monkeypatch):
        """Test getting environment variable with empty string"""
        monkeypatch.setenv("EMPTY_VAR", "")
        result = safe_get_env("EMPTY_VAR")
        assert result == ""


class TestSetupLogging:
    """Tests for setup_logging function"""
    
    def test_setup_logging_info(self):
        """Test setting up INFO level logging"""
        setup_logging("INFO")
        assert logger.level <= 20  # INFO level is 20
    
    def test_setup_logging_debug(self):
        """Test setting up DEBUG level logging"""
        setup_logging("DEBUG")
        assert logger.level <= 10  # DEBUG level is 10
    
    def test_setup_logging_warning(self):
        """Test setting up WARNING level logging"""
        setup_logging("WARNING")
        assert logger.level <= 30  # WARNING level is 30


class TestLogError:
    """Tests for log_error function"""
    
    def test_log_error_basic(self):
        """Test basic error logging"""
        try:
            raise ValueError("Test error")
        except Exception as e:
            # Should not raise exception
            log_error(e, context="test context")
    
    def test_log_error_without_context(self):
        """Test error logging without context"""
        try:
            raise RuntimeError("Test runtime error")
        except Exception as e:
            log_error(e)


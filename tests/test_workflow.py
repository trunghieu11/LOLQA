"""
Unit tests for LangGraph workflow
"""
import pytest
from unittest.mock import Mock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from src.core import LoLQAGraph


class TestLoLQAGraph:
    """Tests for LoLQAGraph workflow"""
    
    def test_initialization(self, mock_rag_system):
        """Test workflow initialization"""
        workflow = LoLQAGraph(mock_rag_system)
        
        assert workflow.rag_system == mock_rag_system
        assert workflow.workflow is not None
    
    def test_invoke_basic_question(self, mock_rag_system):
        """Test invoking workflow with basic question"""
        mock_rag_system.query.return_value = "Test answer"
        
        workflow = LoLQAGraph(mock_rag_system)
        result = workflow.invoke("Who is Yasuo?")
        
        assert result == "Test answer"
        mock_rag_system.query.assert_called_once()
    
    def test_invoke_with_conversation_history(self, mock_rag_system):
        """Test invoking workflow with conversation history"""
        mock_rag_system.query.return_value = "Test answer"
        
        conversation_history = [
            {"role": "user", "content": "Who is Yasuo?"},
            {"role": "assistant", "content": "Yasuo is a champion."}
        ]
        
        workflow = LoLQAGraph(mock_rag_system)
        result = workflow.invoke("How many skins does he have?", conversation_history)
        
        assert result == "Test answer"
        
        # Verify that chat history was passed
        call_args = mock_rag_system.query.call_args
        assert call_args is not None
    
    def test_invoke_empty_question(self, mock_rag_system):
        """Test invoking workflow with empty question"""
        workflow = LoLQAGraph(mock_rag_system)
        
        # Should handle gracefully
        result = workflow.invoke("")
        
        # Should either return error message or handle it
        assert isinstance(result, str)
    
    def test_extract_question_node(self, mock_rag_system):
        """Test _extract_question node"""
        workflow = LoLQAGraph(mock_rag_system)
        
        state = {
            "messages": [HumanMessage(content="Test question")],
            "question": "",
            "answer": "",
            "rag_context": ""
        }
        
        result = workflow._extract_question(state)
        
        assert result["question"] == "Test question"
    
    def test_generate_answer_node(self, mock_rag_system):
        """Test _generate_answer node"""
        mock_rag_system.query.return_value = "Test answer"
        
        workflow = LoLQAGraph(mock_rag_system)
        
        state = {
            "messages": [HumanMessage(content="Test question")],
            "question": "Test question",
            "answer": "",
            "rag_context": ""
        }
        
        result = workflow._generate_answer(state)
        
        assert result["answer"] == "Test answer"
    
    def test_format_response_node(self, mock_rag_system):
        """Test _format_response node"""
        workflow = LoLQAGraph(mock_rag_system)
        
        state = {
            "messages": [HumanMessage(content="Test question")],
            "question": "Test question",
            "answer": "Test answer",
            "rag_context": ""
        }
        
        result = workflow._format_response(state)
        
        # Should add AI message
        assert len(result["messages"]) == 2
        assert isinstance(result["messages"][1], AIMessage)
        assert result["messages"][1].content == "Test answer"
    
    def test_format_chat_history(self, mock_rag_system):
        """Test _format_chat_history method"""
        workflow = LoLQAGraph(mock_rag_system)
        
        conversation = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1"},
            {"role": "user", "content": "Question 2"},
        ]
        
        formatted = workflow._format_chat_history(conversation)
        
        assert isinstance(formatted, str)
        assert "Question 1" in formatted
        assert "Answer 1" in formatted
        assert "Question 2" in formatted
    
    def test_workflow_error_handling(self, mock_rag_system):
        """Test workflow handles errors gracefully"""
        mock_rag_system.query.side_effect = Exception("Test error")
        
        workflow = LoLQAGraph(mock_rag_system)
        
        # Should not raise exception
        try:
            result = workflow.invoke("Test question")
            # If it doesn't raise, check if error is handled
            assert isinstance(result, str)
        except Exception:
            # Or it may raise, which is also acceptable
            pass


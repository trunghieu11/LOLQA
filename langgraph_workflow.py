"""
LangGraph Workflow for League of Legends Q&A
Orchestrates the Q&A process with state management
"""
from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from rag_system import LoLRAGSystem
from constants import (
    NODE_EXTRACT_QUESTION,
    NODE_RETRIEVE_CONTEXT,
    NODE_GENERATE_ANSWER,
    NODE_FORMAT_RESPONSE
)
from utils import logger, format_documents


class GraphState(TypedDict):
    """State of the LangGraph workflow"""
    messages: Annotated[list, add_messages]
    question: str
    answer: str
    rag_context: str


class LoLQAGraph:
    """LangGraph workflow for Q&A processing"""
    
    def __init__(self, rag_system: LoLRAGSystem):
        self.rag_system = rag_system
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow.
        
        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node(NODE_EXTRACT_QUESTION, self._extract_question)
        workflow.add_node(NODE_RETRIEVE_CONTEXT, self._retrieve_context)
        workflow.add_node(NODE_GENERATE_ANSWER, self._generate_answer)
        workflow.add_node(NODE_FORMAT_RESPONSE, self._format_response)
        
        # Define edges
        workflow.set_entry_point(NODE_EXTRACT_QUESTION)
        workflow.add_edge(NODE_EXTRACT_QUESTION, NODE_RETRIEVE_CONTEXT)
        workflow.add_edge(NODE_RETRIEVE_CONTEXT, NODE_GENERATE_ANSWER)
        workflow.add_edge(NODE_GENERATE_ANSWER, NODE_FORMAT_RESPONSE)
        workflow.add_edge(NODE_FORMAT_RESPONSE, END)
        
        compiled = workflow.compile()
        logger.info("LangGraph workflow built successfully")
        return compiled
    
    def _extract_question(self, state: GraphState) -> GraphState:
        """
        Extract the question from the latest message.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with extracted question
        """
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, HumanMessage):
                question = last_message.content
            else:
                question = str(last_message.content)
        else:
            question = state.get("question", "")
        
        logger.debug(f"Extracted question: {question[:50]}...")
        return {
            **state,
            "question": question
        }
    
    def _retrieve_context(self, state: GraphState) -> GraphState:
        """
        Retrieve relevant context using RAG.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with retrieved context
        """
        question = state.get("question", "")
        
        # Get relevant documents
        docs = self.rag_system.get_relevant_documents(question)
        
        # Format context using utility function
        rag_context = format_documents(docs)
        
        logger.debug(f"Retrieved {len(docs)} documents for context")
        return {
            **state,
            "rag_context": rag_context
        }
    
    def _generate_answer(self, state: GraphState) -> GraphState:
        """
        Generate answer using RAG system.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with generated answer
        """
        question = state.get("question", "")
        messages = state.get("messages", [])
        
        # Format conversation history from messages (exclude the last user message)
        chat_history = self._format_chat_history(messages[:-1] if len(messages) > 1 else [])
        
        # Use RAG system to generate answer with history
        answer = self.rag_system.query(question, chat_history=chat_history if chat_history else None)
        
        logger.debug("Answer generated successfully")
        return {
            **state,
            "answer": answer
        }
    
    def _format_chat_history(self, messages: list) -> str:
        """
        Format conversation history from messages for the prompt.
        
        Args:
            messages: List of message objects (HumanMessage, AIMessage)
            
        Returns:
            Formatted conversation history string, or empty string if no history
        """
        if not messages:
            return ""
        
        history_lines = []
        for msg in messages:
            content = ""
            if isinstance(msg, HumanMessage):
                content = msg.content
                history_lines.append(f"User: {content}")
            elif isinstance(msg, AIMessage):
                content = msg.content
                history_lines.append(f"Assistant: {content}")
            else:
                # Fallback for other message types
                content = str(getattr(msg, 'content', msg))
                history_lines.append(f"User: {content}")
        
        # Only return history if we have actual content
        formatted = "\n".join(history_lines)
        return formatted if formatted.strip() else ""
    
    def _format_response(self, state: GraphState) -> GraphState:
        """
        Format the final response.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with formatted response
        """
        answer = state.get("answer", "")
        messages = state.get("messages", [])
        
        # Add AI response to messages
        new_messages = messages + [AIMessage(content=answer)]
        
        return {
            **state,
            "messages": new_messages
        }
    
    def invoke(self, question: str, conversation_history: Optional[list] = None) -> str:
        """
        Invoke the workflow with a question and optional conversation history.
        
        Args:
            question: User's question
            conversation_history: Optional list of previous messages in format 
                                [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
            
        Returns:
            Generated answer string
        """
        logger.info(f"Invoking workflow for question: {question[:50]}...")
        
        # Convert conversation history to LangChain messages if provided
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if msg.get("role") == "user":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("role") == "assistant":
                    messages.append(AIMessage(content=msg.get("content", "")))
        
        # Add current question
        messages.append(HumanMessage(content=question))
        
        initial_state = {
            "messages": messages,
            "question": "",
            "answer": "",
            "rag_context": ""
        }
        
        try:
            result = self.workflow.invoke(initial_state)
            answer = result.get("answer", "")
            logger.info("Workflow completed successfully")
            return answer
        except Exception as e:
            logger.error(f"Error in workflow execution: {e}", exc_info=True)
            raise


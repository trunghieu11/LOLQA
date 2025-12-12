"""
Streamlit Web Application for League of Legends Q&A
Main entry point for the application
"""
import streamlit as st
import streamlit.components.v1 as components
from langsmith import traceable
from rag_system import LoLRAGSystem
from langgraph_workflow import LoLQAGraph
from config import config
from constants import (
    ERROR_MISSING_API_KEY,
    ERROR_INITIALIZATION,
    ERROR_QUERY_PROCESSING,
    APP_DESCRIPTION,
    SIDEBAR_ABOUT,
    EXAMPLE_QUESTIONS,
    SESSION_MESSAGES,
    SESSION_USER_QUESTION
)
from utils import logger, validate_question


@st.cache_resource
def initialize_systems():
    """
    Initialize RAG system and LangGraph workflow (cached).
    
    Returns:
        Tuple of (rag_system, graph)
    """
    logger.info("Initializing systems...")
    try:
        rag_system = LoLRAGSystem()
        rag_system.initialize()
        graph = LoLQAGraph(rag_system)
        logger.info("Systems initialized successfully")
        return rag_system, graph
    except Exception as e:
        logger.error(f"Error initializing systems: {e}", exc_info=True)
        raise


@traceable(name="lol_qa_query")
def process_query(question: str, graph: LoLQAGraph, conversation_history: list = None) -> str:
    """
    Process a query using LangGraph workflow (traced with LangSmith).
    
    Args:
        question: User's question
        graph: LangGraph workflow instance
        conversation_history: Optional list of previous messages
        
    Returns:
        Generated answer string
    """
    return graph.invoke(question, conversation_history=conversation_history)


def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title=config.app.page_title,
        page_icon=config.app.page_icon,
        layout=config.app.layout
    )


def format_conversation_for_copy(messages: list) -> str:
    """
    Format conversation history as a readable string.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        
    Returns:
        Formatted string in the requested format
    """
    if not messages:
        return "No conversation yet."
    
    lines = []
    for i, message in enumerate(messages, 1):
        role = message.get("role", "unknown").upper()
        content = message.get("content", "")
        
        lines.append(f"[{i}] {role}:")
        lines.append(content)
        lines.append("")  # Empty line between messages
    
    return "\n".join(lines).strip()


def render_sidebar():
    """Render the sidebar with about info and example questions"""
    with st.sidebar:
        st.header("About")
        st.markdown(SIDEBAR_ABOUT)
        
        st.header("Example Questions")
        for i, q in enumerate(EXAMPLE_QUESTIONS):
            if st.button(f"💬 {q}", key=f"example_{i}", use_container_width=True):
                st.session_state[SESSION_USER_QUESTION] = q
        
        # Copy conversation section - always visible
        st.divider()
        st.header("Copy Conversation")
        
        # Copy to clipboard button
        if st.button("📋 Show Conversation to Copy", use_container_width=True, key="copy_conversation"):
            # Get messages from session state when button is clicked
            messages = st.session_state.get(SESSION_MESSAGES, [])
            formatted_conversation = format_conversation_for_copy(messages)
            
            # Show conversation in a text area for easy copying
            st.text_area(
                "Select all (Ctrl/Cmd+A) and copy (Ctrl/Cmd+C):",
                formatted_conversation,
                height=300,
                key="conversation_display"
            )
            st.info("💡 Click in the text box above, press Ctrl+A (Cmd+A on Mac) to select all, then Ctrl+C (Cmd+C) to copy")


def render_chat_history():
    """Render the chat history"""
    if SESSION_MESSAGES not in st.session_state:
        st.session_state[SESSION_MESSAGES] = []
    
    for message in st.session_state[SESSION_MESSAGES]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(graph: LoLQAGraph):
    """Handle user input and generate responses"""
    user_question = st.chat_input("Ask a question about League of Legends...")
    
    # Handle example question clicks
    if SESSION_USER_QUESTION in st.session_state:
        user_question = st.session_state[SESSION_USER_QUESTION]
        del st.session_state[SESSION_USER_QUESTION]
    
    if user_question:
        # Validate question
        is_valid, error_msg = validate_question(user_question)
        if not is_valid:
            st.warning(error_msg)
            return
        
        # Get conversation history BEFORE adding current message (to avoid duplication)
        conversation_history = st.session_state[SESSION_MESSAGES].copy()
        
        # Add user message to chat
        st.session_state[SESSION_MESSAGES].append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Pass conversation history (doesn't include current message)
                    answer = process_query(user_question, graph, conversation_history)
                    st.markdown(answer)
                    st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": answer})
                except Exception as e:
                    error_msg = ERROR_QUERY_PROCESSING.format(error=str(e))
                    logger.error(f"Error processing query: {e}", exc_info=True)
                    st.error(error_msg)
                    st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": error_msg})


def main():
    """Main Streamlit application"""
    # Setup configuration
    config.setup_langsmith()
    
    # Setup page
    setup_page()
    
    # Validate configuration
    is_valid, error_msg = config.validate()
    if not is_valid:
        st.error(ERROR_MISSING_API_KEY)
        st.stop()
    
    # Initialize systems
    try:
        rag_system, graph = initialize_systems()
    except Exception as e:
        st.error(ERROR_INITIALIZATION.format(error=str(e)))
        logger.error(f"Initialization error: {e}", exc_info=True)
        st.stop()
    
    # Header
    st.title(f"{config.app.page_icon} {config.app.page_title}")
    st.markdown(APP_DESCRIPTION)
    
    # Sidebar
    render_sidebar()
    
    # Chat history
    render_chat_history()
    
    # User input
    handle_user_input(graph)


if __name__ == "__main__":
    main()


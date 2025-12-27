"""
Streamlit Web Application for League of Legends Q&A
Main entry point for the application
"""
import streamlit as st
import streamlit.components.v1 as components
from langsmith import traceable

# Import from new structure
from src.core import LoLRAGSystem, LoLQAGraph
from src.config import config
from src.config.constants import (
    ERROR_MISSING_API_KEY,
    ERROR_INITIALIZATION,
    ERROR_QUERY_PROCESSING,
    APP_DESCRIPTION,
    SIDEBAR_ABOUT,
    EXAMPLE_QUESTIONS,
    SESSION_MESSAGES,
    SESSION_USER_QUESTION
)
from src.utils import logger, validate_question


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
        conversation_history: Previous conversation messages
        
    Returns:
        Generated answer string
    """
    try:
        logger.info(f"Invoking workflow for question: {question}...")
        result = graph.invoke(question, conversation_history or [])
        logger.info("Workflow completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in workflow: {e}", exc_info=True)
        raise


def render_sidebar():
    """Render sidebar with information and example questions"""
    with st.sidebar:
        st.title("ℹ️ About")
        st.markdown(SIDEBAR_ABOUT)
        
        st.divider()
        
        st.title("💡 Example Questions")
        for question in EXAMPLE_QUESTIONS:
            if st.button(question, key=f"example_{question}", use_container_width=True):
                st.session_state[SESSION_USER_QUESTION] = question
        
        st.divider()
        
        # Copy conversation feature
        st.title("📋 Copy Conversation")
        if SESSION_MESSAGES in st.session_state and len(st.session_state[SESSION_MESSAGES]) > 0:
            if st.button("Show Conversation to Copy", use_container_width=True):
                messages = st.session_state[SESSION_MESSAGES]
                formatted_conversation = ""
                for i, msg in enumerate(messages, 1):
                    role = "USER" if msg["role"] == "user" else "ASSISTANT"
                    formatted_conversation += f"[{i}] {role}:\n{msg['content']}\n\n"
                
                st.text_area(
                    "Select and copy the text below:",
                    value=formatted_conversation,
                    height=300,
                    key="conversation_copy"
                )
                st.info("💡 Select all text above and press Ctrl+C (Cmd+C on Mac) to copy")
        else:
            st.info("Start a conversation to enable copy")


def handle_user_input():
    """Handle user input from chat or sidebar"""
    # Check if there's a question from sidebar button
    if SESSION_USER_QUESTION in st.session_state and st.session_state[SESSION_USER_QUESTION]:
        user_question = st.session_state[SESSION_USER_QUESTION]
        st.session_state[SESSION_USER_QUESTION] = ""  # Clear it
    elif prompt := st.chat_input("Ask me anything about League of Legends..."):
        user_question = prompt
    else:
        return
    
    # Validate question
    is_valid, error_msg = validate_question(user_question)
    if not is_valid:
        st.error(error_msg)
        return
    
    # Get conversation history BEFORE adding current message
    conversation_history = st.session_state[SESSION_MESSAGES].copy()
    
    # Add user message to chat
    st.session_state[SESSION_MESSAGES].append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                _, graph = initialize_systems()
                response = process_query(user_question, graph, conversation_history)
                st.markdown(response)
                st.session_state[SESSION_MESSAGES].append({"role": "assistant", "content": response})
            except Exception as e:
                error_message = f"{ERROR_QUERY_PROCESSING}: {str(e)}"
                st.error(error_message)
                logger.error(error_message, exc_info=True)


def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title=config.app.page_title,
        page_icon=config.app.page_icon,
        layout=config.app.layout
    )
    
    # Title and description
    st.title(f"{config.app.page_icon} {config.app.page_title}")
    st.markdown(APP_DESCRIPTION)
    
    # Initialize session state
    if SESSION_MESSAGES not in st.session_state:
        st.session_state[SESSION_MESSAGES] = []
    if SESSION_USER_QUESTION not in st.session_state:
        st.session_state[SESSION_USER_QUESTION] = ""
    
    # Check for API keys
    if not config.openai_api_key:
        st.error(ERROR_MISSING_API_KEY)
        st.stop()
    
    # Initialize systems
    try:
        initialize_systems()
    except Exception as e:
        st.error(f"{ERROR_INITIALIZATION}: {str(e)}")
        st.stop()
    
    # Render sidebar
    render_sidebar()
    
    # Display chat history
    for message in st.session_state[SESSION_MESSAGES]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    handle_user_input()


if __name__ == "__main__":
    main()


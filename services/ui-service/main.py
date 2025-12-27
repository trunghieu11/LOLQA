"""UI Service - Streamlit app that calls RAG Service"""
import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import httpx
from shared.common import setup_logger, get_config
from shared.common.config import UIServiceConfig
from shared.common.models import ChatMessage, RAGQueryRequest

# Setup logger
logger = setup_logger(__name__)

# Get configuration
config: UIServiceConfig = get_config("ui")
logger.info(f"Starting UI Service")

# RAG Service URL
RAG_SERVICE_URL = config.rag_service_url

# Page configuration
st.set_page_config(
    page_title="League of Legends Q&A Assistant",
    page_icon="⚔️",
    layout="wide"
)

# Title and description
st.title("⚔️ League of Legends Q&A Assistant")
st.markdown("Ask me anything about League of Legends champions, abilities, strategies, and more!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check for RAG service
@st.cache_resource
def check_rag_service():
    """Check if RAG service is available"""
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{RAG_SERVICE_URL}/health")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"RAG service not available: {e}")
        return False


# Sidebar
with st.sidebar:
    st.title("ℹ️ About")
    st.markdown("""
    This application uses:
    - **Microservices Architecture**
    - **LangChain** for RAG
    - **LangGraph** for workflow orchestration
    
    Ask questions about:
    - Champion abilities and playstyles
    - Game mechanics
    - Item builds
    - Ranked system
    """)
    
    st.divider()
    
    st.title("💡 Example Questions")
    example_questions = [
        "What are Ahri's abilities?",
        "How should I play Yasuo?",
        "What is the role of a support champion?",
        "Tell me about teamfighting in League of Legends",
        "What items should I build on Jinx?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{question}", use_container_width=True):
            st.session_state.user_question = question

# Check RAG service availability
if not check_rag_service():
    st.error(f"⚠️ RAG Service is not available at {RAG_SERVICE_URL}")
    st.info("Please ensure the RAG service is running.")
    st.stop()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if "user_question" in st.session_state and st.session_state.user_question:
    user_question = st.session_state.user_question
    st.session_state.user_question = ""  # Clear it
elif prompt := st.chat_input("Ask me anything about League of Legends..."):
    user_question = prompt
else:
    user_question = None

if user_question:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Prepare conversation history
                conversation_history = [
                    ChatMessage(role=msg["role"], content=msg["content"])
                    for msg in st.session_state.messages[:-1]  # Exclude current message
                ]
                
                # Call RAG service
                request = RAGQueryRequest(
                    question=user_question,
                    conversation_history=conversation_history if conversation_history else None
                )
                
                with httpx.Client(timeout=60.0) as client:
                    response = client.post(
                        f"{RAG_SERVICE_URL}/query",
                        json=request.dict()
                    )
                    response.raise_for_status()
                    result = response.json()
                
                answer = result["answer"]
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except httpx.HTTPError as e:
                error_message = f"Error connecting to RAG service: {str(e)}"
                st.error(error_message)
                logger.error(error_message, exc_info=True)
            except Exception as e:
                error_message = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_message)
                logger.error(error_message, exc_info=True)


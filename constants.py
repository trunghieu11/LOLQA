"""
Constants used throughout the application.
Centralizes magic numbers and strings for easier maintenance.
"""

# Prompt Templates
DEFAULT_PROMPT_TEMPLATE = """You are a helpful assistant specialized in League of Legends game knowledge.

CRITICAL INSTRUCTIONS:
- You MUST ONLY use the information provided in the Context section below
- DO NOT use any information from your training data or general knowledge
- If the answer is not in the provided context, explicitly say "I don't have that information in my knowledge base"
- The context provided is the most up-to-date and accurate information available

Context: {context}

Question: {question}

Provide a detailed and helpful answer about League of Legends using ONLY the context provided above:"""

# Prompt Template with Conversation History
DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY = """You are a helpful assistant specialized in League of Legends game knowledge.

CRITICAL INSTRUCTIONS:
- You MUST ONLY use the information provided in the Context section below
- DO NOT use any information from your training data or general knowledge
- If the answer is not in the provided context, explicitly say "I don't have that information in my knowledge base"
- The context provided is the most up-to-date and accurate information available
- Pay attention to the conversation history. If the user refers to something mentioned earlier (like "he", "she", "it", "this champion", etc.), use the conversation history to understand what they're referring to

Context: {context}

Conversation History:
{chat_history}

Current Question: {question}

Provide a detailed and helpful answer about League of Legends using ONLY the context provided above. If the question references something from the conversation history, make sure to use that context:"""

# Error Messages
ERROR_RAG_NOT_INITIALIZED = "RAG system not initialized. Call initialize() first."
ERROR_MISSING_API_KEY = "⚠️ Please set your OPENAI_API_KEY in the .env file"
ERROR_INITIALIZATION = "Error initializing systems: {error}"
ERROR_QUERY_PROCESSING = "Sorry, I encountered an error: {error}"

# UI Messages
APP_DESCRIPTION = "Ask me anything about League of Legends champions, abilities, strategies, and more!"
SIDEBAR_ABOUT = """
This application uses:
- **LangChain** for RAG and LLM integration
- **LangGraph** for workflow orchestration
- **LangSmith** for monitoring and tracing

Ask questions about:
- Champion abilities and playstyles
- Game mechanics
- Item builds
- Ranked system
"""

# Example Questions
EXAMPLE_QUESTIONS = [
    "What are Ahri's abilities?",
    "How should I play Yasuo?",
    "What is the role of a support champion?",
    "Tell me about teamfighting in League of Legends",
    "What items should I build on Jinx?"
]

# Vector Store Messages
MSG_LOADING_VECTOR_STORE = "Loading existing vector store..."
MSG_CREATING_VECTOR_STORE = "Creating new vector store..."
MSG_VECTOR_STORE_CREATED = "Created vector store with {count} document chunks"

# LangGraph Node Names
NODE_EXTRACT_QUESTION = "extract_question"
NODE_RETRIEVE_CONTEXT = "retrieve_context"
NODE_GENERATE_ANSWER = "generate_answer"
NODE_FORMAT_RESPONSE = "format_response"

# Streamlit Session State Keys
SESSION_MESSAGES = "messages"
SESSION_USER_QUESTION = "user_question"


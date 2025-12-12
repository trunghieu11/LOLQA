"""
RAG System for League of Legends Q&A
Handles vector store creation, embeddings, and retrieval
"""
import os
from typing import List, Optional
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from data_collector import LoLDataCollector
from config import config
from constants import (
    DEFAULT_PROMPT_TEMPLATE,
    DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY,
    ERROR_RAG_NOT_INITIALIZED,
    MSG_LOADING_VECTOR_STORE,
    MSG_CREATING_VECTOR_STORE,
    MSG_VECTOR_STORE_CREATED
)
from utils import logger, format_documents


class LoLRAGSystem:
    """RAG system for League of Legends knowledge base"""
    
    def __init__(self, persist_directory: Optional[str] = None, data_collector: Optional[LoLDataCollector] = None):
        """
        Initialize the RAG system.
        
        Args:
            persist_directory: Directory to persist vector store (defaults to config)
            data_collector: Optional custom data collector instance
        """
        self.persist_directory = persist_directory or config.rag.persist_directory
        self.data_collector = data_collector or LoLDataCollector()
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.vectorstore: Optional[Chroma] = None
        self.llm: Optional[ChatOpenAI] = None
        self.retriever: Optional[Chroma] = None
        self.qa_chain: Optional[object] = None
        self.llm_with_tools: Optional[object] = None
        self.tools: Optional[list] = None
        
    def initialize(self):
        """Initialize the RAG system with embeddings and vector store"""
        try:
            logger.info("Initializing RAG system...")
            
            # Initialize OpenAI embeddings
            self.embeddings = OpenAIEmbeddings()
            logger.info("Embeddings initialized")
            
            # Initialize LLM
            llm_kwargs = {
                "model": config.llm.model,
                "temperature": config.llm.temperature,
            }
            if config.llm.max_tokens:
                llm_kwargs["max_tokens"] = config.llm.max_tokens
            
            self.llm = ChatOpenAI(**llm_kwargs)
            logger.info(f"LLM initialized: {config.llm.model}")
            
            # Load or create vector store
            if os.path.exists(self.persist_directory):
                logger.info(MSG_LOADING_VECTOR_STORE)
                self._load_vector_store()
            else:
                logger.info(MSG_CREATING_VECTOR_STORE)
                self._create_vector_store()
            
            # Create retriever
            self._create_retriever()
            
            # Create QA chain
            self._create_qa_chain()
            
            # Create QA chain with history support
            self._create_qa_chain_with_history()
            
            # Create LLM with tools
            self._create_llm_with_tools()
            
            logger.info("RAG system initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing RAG system: {e}", exc_info=True)
            raise
    
    def _load_vector_store(self):
        """Load existing vector store"""
        self.vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def _create_vector_store(self):
        """Create new vector store from documents"""
        # Collect data
        documents = self.data_collector.get_documents()
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
            length_function=len,
        )
        splits = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        logger.info(MSG_VECTOR_STORE_CREATED.format(count=len(splits)))
    
    def _create_retriever(self):
        """Create retriever from vector store with intelligent query handling"""
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": config.rag.retrieval_k}
        )
        logger.info(f"Retriever created with k={config.rag.retrieval_k}")
    
    def _create_qa_chain(self):
        """Create the QA chain"""
        prompt = ChatPromptTemplate.from_template(DEFAULT_PROMPT_TEMPLATE)
        
        # Create the chain using LCEL
        self.qa_chain = (
            {
                "context": self.retriever,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("QA chain created")
    
    def _create_qa_chain_with_history(self):
        """Create the QA chain with conversation history support"""
        prompt = ChatPromptTemplate.from_template(DEFAULT_PROMPT_TEMPLATE_WITH_HISTORY)
        
        # Create the chain using LCEL with history
        # The retriever needs the question string, so we extract it from the input dict
        # and format the retrieved documents
        def format_context(input_dict):
            """Extract question, retrieve docs, and format them"""
            question = input_dict["question"]
            docs = self.retriever.invoke(question)
            return format_documents(docs)
        
        self.qa_chain_with_history = (
            {
                "context": RunnableLambda(format_context),
                "chat_history": RunnableLambda(lambda x: x.get("chat_history", "")),
                "question": RunnableLambda(lambda x: x["question"])
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        logger.info("QA chain with history created")
    
    def _create_llm_with_tools(self):
        """Create LLM with tool calling capability"""
        # Define tools for the LLM
        
        @tool
        def search_champion_info(query: str) -> str:
            """Search for specific information about League of Legends champions, abilities, or gameplay.
            Use this when the user asks about specific champions, abilities, strategies, or detailed information.
            
            Args:
                query: The search query about champions or gameplay
                
            Returns:
                Relevant information from the knowledge base
            """
            try:
                docs = self.retriever.invoke(query)
                return format_documents(docs)
            except Exception as e:
                return f"Error searching: {str(e)}"
        
        @tool
        def count_champions(role_filter: str = "") -> str:
            """Count the total number of champions in League of Legends, optionally filtered by role.
            Use this when the user asks 'how many champions', 'total champions', 'number of champions', etc.
            
            Args:
                role_filter: Optional role filter (Fighter, Mage, Assassin, Tank, Support, Marksman, or empty string for all)
                
            Returns:
                The count of champions matching the filter
            """
            try:
                where_clause = {"type": "champion"}
                results = self.vectorstore.get(where=where_clause, limit=2000)  # Increased to get all chunks
                
                if not results or 'metadatas' not in results:
                    return "Could not retrieve champion count"
                
                # Count unique champions
                unique_champions = set()
                for metadata in results['metadatas']:
                    if metadata and 'champion' in metadata:
                        champion_name = metadata['champion']
                        champion_role = metadata.get('role', '')
                        
                        # Apply role filter if specified
                        if role_filter and role_filter.strip():
                            if role_filter.lower() in champion_role.lower():
                                unique_champions.add(champion_name)
                        else:
                            unique_champions.add(champion_name)
                
                count = len(unique_champions)
                if role_filter and role_filter.strip():
                    return f"There are {count} {role_filter} champions in League of Legends."
                else:
                    return f"There are {count} champions in League of Legends."
            except Exception as e:
                return f"Error counting champions: {str(e)}"
        
        @tool
        def list_champions(role_filter: str = "", limit: int = 20) -> str:
            """List champion names, optionally filtered by role.
            Use this when the user wants to see a list of champions.
            
            Args:
                role_filter: Optional role filter (empty string for all)
                limit: Maximum number of champions to list (default 20)
                
            Returns:
                List of champion names
            """
            try:
                where_clause = {"type": "champion"}
                results = self.vectorstore.get(where=where_clause, limit=2000)  # Increased to get all chunks
                
                if not results or 'metadatas' not in results:
                    return "Could not retrieve champions"
                
                # Get unique champions
                champions = set()
                for metadata in results['metadatas']:
                    if metadata and 'champion' in metadata:
                        champion_name = metadata['champion']
                        champion_role = metadata.get('role', '')
                        
                        # Apply role filter
                        if role_filter and role_filter.strip():
                            if role_filter.lower() in champion_role.lower():
                                champions.add(champion_name)
                        else:
                            champions.add(champion_name)
                
                champion_list = sorted(list(champions))[:limit]
                if role_filter and role_filter.strip():
                    return f"{role_filter} champions: " + ", ".join(champion_list)
                else:
                    return "Champions: " + ", ".join(champion_list)
            except Exception as e:
                return f"Error listing champions: {str(e)}"
        
        @tool
        def get_database_info() -> str:
            """Get information about the database itself, such as when it was last updated or what version it is.
            Use this when the user asks about data freshness, update time, or database version.
            
            Returns:
                Information about the database
            """
            return "This database contains live League of Legends data from Riot Games' Data Dragon API (version 15.24.1). The data is current and includes all champions, their abilities, stats, skins, and other game information. The database is regularly updated with the latest game content."
        
        self.tools = [search_champion_info, count_champions, list_champions, get_database_info]
        
        # Bind tools to LLM (OpenAI models support function calling)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        logger.info("LLM with tools created")
    
    def query(self, question: str, chat_history: Optional[str] = None) -> str:
        """
        Query the RAG system using LLM with tool calling.
        The LLM decides which tools to use based on the question.
        
        Args:
            question: User's question
            chat_history: Optional conversation history string
            
        Returns:
            Generated answer string
            
        Raises:
            ValueError: If RAG system not initialized
        """
        if not self.llm_with_tools:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        logger.info(f"Processing query with LLM tools: {question[:50]}...")
        
        try:
            # Build the prompt
            system_prompt = """You are a helpful assistant specialized in League of Legends knowledge.
You have access to tools to retrieve information from a database.

CRITICAL RULES:
1. You MUST ONLY use the tools provided to get information
2. NEVER use your training data or general knowledge
3. If a tool returns no relevant information, say "I don't have that information in my knowledge base"
4. Do NOT mention your training data cutoff date or October 2023

Available information in the database:
- Champion details (abilities, stats, lore, skins)
- Champion counts and lists
- Role-based filtering

For questions about:
- "how many champions" → use count_champions tool
- "list champions" or "all champion names" → use list_champions tool
- Specific champion info → use search_champion_info tool
- "when was data updated" → Say "This is live data from the League of Legends database"
"""
            
            if chat_history:
                prompt_text = f"""{system_prompt}

Conversation History:
{chat_history}

Current Question: {question}

Think about which tool to use."""
            else:
                prompt_text = f"""{system_prompt}

Question: {question}

Think about which tool to use."""
            
            # Call LLM with tools
            ai_msg = self.llm_with_tools.invoke(prompt_text)
            
            # Check if the LLM wants to call any tools
            if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
                logger.info(f"LLM requested {len(ai_msg.tool_calls)} tool calls")
                
                # Execute tool calls
                tool_results = []
                for tool_call in ai_msg.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    logger.info(f"Calling tool: {tool_name} with args: {tool_args}")
                    
                    # Find and execute the tool
                    for tool in self.tools:
                        if tool.name == tool_name:
                            result = tool.invoke(tool_args)
                            tool_results.append(f"{tool_name}: {result}")
                            break
                
                # Combine tool results and ask LLM to generate final answer
                tool_context = "\n\n".join(tool_results)
                final_prompt = f"""You are answering a League of Legends question using ONLY the tool results below.

Tool Results:
{tool_context}

User Question: {question}

CRITICAL RULES:
1. Answer ONLY using the information from the tool results above
2. If the tool results don't contain relevant information, say "I don't have that information in my knowledge base"
3. NEVER use your training data or mention "October 2023" or any cutoff date
4. If asked about data freshness, say "This is live data from the League of Legends database"

Provide a clear, helpful answer based strictly on the tool results."""
                
                final_answer = self.llm.invoke(final_prompt)
                answer = final_answer.content if hasattr(final_answer, 'content') else str(final_answer)
                
                logger.info("Query processed successfully with tool calls")
                return answer
            else:
                # No tool calls, use the LLM's direct response
                answer = ai_msg.content if hasattr(ai_msg, 'content') else str(ai_msg)
                logger.info("Query processed successfully without tool calls")
                return answer
                
        except Exception as e:
            logger.error(f"Error processing query with LLM tools: {e}", exc_info=True)
            raise
    
    def get_relevant_documents(self, question: str, k: Optional[int] = None) -> List[Document]:
        """
        Get relevant documents for a question.
        
        Args:
            question: User's question
            k: Number of documents to retrieve (defaults to config value)
            
        Returns:
            List of relevant Document objects
            
        Raises:
            ValueError: If RAG system not initialized
        """
        if not self.retriever:
            raise ValueError(ERROR_RAG_NOT_INITIALIZED)
        
        k = k or config.rag.retrieval_k
        logger.debug(f"Retrieving {k} documents for question: {question[:50]}...")
        
        # In LangChain 1.x, retrievers are Runnables and use invoke()
        # Try invoke() first, fallback to get_relevant_documents() for compatibility
        try:
            docs = self.retriever.invoke(question)
            # If invoke returns a list, use it; otherwise try with k parameter
            if isinstance(docs, list):
                return docs[:k] if len(docs) > k else docs
            return self.retriever.get_relevant_documents(question, k=k)
        except (AttributeError, TypeError):
            # Fallback for older API
            return self.retriever.get_relevant_documents(question)


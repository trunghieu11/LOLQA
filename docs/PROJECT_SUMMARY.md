# 📖 LOLQA Project - Complete Summary

## 🎯 Project Overview

**LOLQA** (League of Legends Q&A) is an intelligent chatbot application that answers questions about League of Legends using **Retrieval-Augmented Generation (RAG)** with LangChain, LangGraph, and OpenAI.

### Key Capabilities
- ✅ Answer questions about 172 League of Legends champions
- ✅ Count and list champions (with role filtering)
- ✅ Provide detailed information about abilities, skins, stats, lore
- ✅ Remember conversation context
- ✅ Use **tool calling** to intelligently decide how to answer questions
- ✅ Retrieve information **ONLY** from the knowledge base (no hallucination)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                      (Streamlit - app.py)                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LANGGRAPH WORKFLOW                             │
│              (langgraph_workflow.py)                             │
│                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Extract    │──▶│   Retrieve   │──▶│   Generate   │        │
│  │   Question   │   │   Context    │   │   Answer     │        │
│  └──────────────┘   └──────────────┘   └──────────────┘        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG SYSTEM                                  │
│                   (rag_system.py)                                │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐     │
│  │              LLM WITH TOOLS (ReAct Pattern)            │     │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │     │
│  │  │   search_    │  │    count_    │  │     list_    │ │     │
│  │  │  champion_   │  │  champions   │  │  champions   │ │     │
│  │  │    info      │  │              │  │              │ │     │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │     │
│  │  ┌──────────────┐                                      │     │
│  │  │get_database_ │                                      │     │
│  │  │    info      │                                      │     │
│  │  └──────────────┘                                      │     │
│  └────────────────────────────────────────────────────────┘     │
│                            │                                     │
│                            ▼                                     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │            VECTOR STORE (ChromaDB)                     │     │
│  │        711 chunks for 172 champions                    │     │
│  └────────────────────────────────────────────────────────┘     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA COLLECTION                                │
│                 (data_collector.py)                              │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Dragon  │  │ Web Scraper  │  │ Sample Data  │          │
│  │   Collector  │  │  Collector   │  │  Collector   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. **Initialization Phase** (App Startup)

```
Start App
   │
   ├─▶ Load Environment Variables (.env)
   │
   ├─▶ Initialize Data Collectors
   │   └─▶ Data Dragon API (Riot Games)
   │   └─▶ Web Scraper (League Wiki)
   │   └─▶ Sample Data (Fallback)
   │
   ├─▶ Collect Documents (172 champions)
   │
   ├─▶ Create Embeddings (OpenAI text-embedding-3-small)
   │
   ├─▶ Store in Vector Database (ChromaDB)
   │   └─▶ 711 chunks after text splitting
   │
   └─▶ Initialize RAG System with Tools
       └─▶ search_champion_info
       └─▶ count_champions
       └─▶ list_champions
       └─▶ get_database_info
```

### 2. **Query Processing Phase** (User Asks a Question)

```
User Input: "how many champions in lol?"
   │
   ├─▶ Streamlit UI (app.py)
   │   └─▶ Store in session history
   │
   ├─▶ LangGraph Workflow (langgraph_workflow.py)
   │   ├─▶ Extract Question
   │   ├─▶ Format Conversation History
   │   └─▶ Generate Answer
   │
   ├─▶ RAG System (rag_system.py)
   │   │
   │   ├─▶ LLM with Tools receives question
   │   │   └─▶ Decides which tool to use
   │   │
   │   ├─▶ Execute Tool Call
   │   │   └─▶ count_champions()
   │   │       └─▶ Query ChromaDB with filter: type="champion"
   │   │       └─▶ Count unique champion names
   │   │       └─▶ Return: "There are 172 champions in League of Legends"
   │   │
   │   └─▶ LLM generates final answer using tool result
   │
   └─▶ Return Answer to User
       └─▶ Display in Streamlit UI
```

---

## 📁 Project Structure

```
LOLQA/
│
├── 🎨 FRONTEND
│   └── app.py                          # Streamlit UI
│
├── 🧠 CORE LOGIC
│   ├── rag_system.py                   # RAG + Tool Calling
│   ├── langgraph_workflow.py           # Workflow Orchestration
│   ├── config.py                       # Configuration
│   ├── constants.py                    # Prompt Templates & Messages
│   └── utils.py                        # Helper Functions
│
├── 📊 DATA COLLECTION
│   ├── data_collector.py               # Main Collector Orchestrator
│   └── data_sources/
│       ├── base_collector.py           # Base Class
│       ├── data_dragon_collector.py    # Riot Data Dragon API
│       ├── web_scraper_collector.py    # Wiki Scraper
│       ├── riot_api_collector.py       # Riot Games API
│       └── sample_data_collector.py    # Fallback Data
│
├── 💾 DATABASE
│   └── chroma_db/                      # Vector Store (711 chunks)
│
├── 📝 DOCUMENTATION
│   ├── README.md                       # Quick Start Guide
│   ├── PROJECT_ARCHITECTURE.md         # Detailed Architecture
│   ├── PROJECT_SUMMARY.md              # This File
│   ├── API_KEYS_SETUP.md              # API Keys Guide
│   ├── DATA_COLLECTION.md             # Data Collection Details
│   └── QUICKSTART.md                  # Quick Setup
│
├── 🐳 DEPLOYMENT
│   ├── Dockerfile                      # Docker Config
│   ├── Procfile                        # Heroku/Railway
│   ├── render.yaml                     # Render Config
│   └── setup.sh                        # Setup Script
│
└── 📦 DEPENDENCIES
    ├── requirements.txt                # Python Packages
    ├── .env                           # Environment Variables
    └── venv/                          # Virtual Environment
```

---

## 🔧 Key Components Explained

### 1. **app.py** - Streamlit UI
- **Purpose**: Web interface for user interaction
- **Key Functions**:
  - `initialize_systems()`: Cached initialization of RAG + LangGraph
  - `process_query()`: Sends queries to LangGraph workflow
  - `handle_user_input()`: Manages conversation history
  - `render_sidebar()`: Shows example questions and copy button
- **Session State**:
  - `SESSION_MESSAGES`: Stores conversation history
  - Each message: `{"role": "user"/"assistant", "content": "..."}`

### 2. **rag_system.py** - RAG System with Tool Calling
- **Purpose**: Core intelligence - retrieves data and generates answers
- **Key Components**:
  
  **A. LLM with Tools (OpenAI Function Calling)**
  - `llm_with_tools`: GPT-4o-mini bound with 4 tools
  
  **B. Tools** (ReAct Pattern):
  1. **`search_champion_info(query)`**
     - Semantic search in vector store
     - Used for: "Who is Yasuo?", "What are Ahri's abilities?"
  
  2. **`count_champions(role_filter="")`**
     - Counts unique champions from metadata
     - Used for: "How many champions?", "How many mage champions?"
  
  3. **`list_champions(role_filter="", limit=20)`**
     - Lists champion names
     - Used for: "Give me all champion names"
  
  4. **`get_database_info()`**
     - Returns database version info
     - Used for: "When was data updated?"
  
  **C. Query Method**:
  ```python
  def query(question, chat_history):
      1. LLM receives question + tool descriptions
      2. LLM decides which tool(s) to call
      3. Execute tool calls
      4. LLM generates final answer using tool results
      5. Return answer
  ```

### 3. **langgraph_workflow.py** - Workflow Orchestration
- **Purpose**: Manages the flow of question → answer
- **GraphState**: Tracks conversation state
  ```python
  {
      "question": str,
      "context": str,
      "answer": str,
      "messages": List[HumanMessage, AIMessage]
  }
  ```
- **Workflow Steps**:
  1. `_extract_question`: Extracts user question from state
  2. `_generate_answer`: Calls RAG system with conversation history
  3. `_format_response`: Formats the final answer

### 4. **data_collector.py** - Data Aggregation
- **Purpose**: Collects League of Legends data from multiple sources
- **Collectors**:
  - **DataDragonCollector**: Riot's static data API (172 champions)
  - **WebScraperCollector**: Scrapes League wiki for lore
  - **SampleDataCollector**: Fallback if APIs fail
- **Output**: 181 documents (172 champions + 9 other docs)

### 5. **data_sources/** - Individual Collectors
Each collector inherits from `BaseDataCollector`:
- **DataDragonCollector**: 
  - Fetches from `https://ddragon.leagueoflegends.com`
  - Version: 15.24.1
  - Includes: abilities, stats, skins, lore, tips
- **WebScraperCollector**: 
  - Scrapes League of Legends wiki
  - Extracts lore and game mechanics
- **RiotAPICollector**: 
  - Requires API key (not used by default)
  - For live match data

### 6. **Vector Store (ChromaDB)**
- **Storage**: `chroma_db/` directory
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Data**:
  - 172 unique champions
  - 711 document chunks (after text splitting)
  - Metadata: `{type, champion, role, source}`
- **Retrieval**: Similarity search with k=3 default

---

## 🎨 Technologies & Stack

### Core Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **LangChain** | 1.1.3 | RAG framework, LLM integration |
| **LangGraph** | 1.0.0+ | Workflow orchestration, state management |
| **LangSmith** | 0.1.0+ | Monitoring, tracing, debugging |

### LLM & Embeddings
| Technology | Model | Purpose |
|------------|-------|---------|
| **OpenAI** | gpt-4o-mini | Answer generation, tool calling |
| **OpenAI Embeddings** | text-embedding-3-small | Document embeddings |

### Data Storage
| Technology | Version | Purpose |
|------------|---------|---------|
| **ChromaDB** | 0.5.0+ | Vector database |
| **Python Dictionaries** | - | Session state management |

### Web Framework
| Technology | Version | Purpose |
|------------|---------|---------|
| **Streamlit** | 1.39.0+ | Web UI, user interface |

### Data Collection
| Technology | Version | Purpose |
|------------|---------|---------|
| **Requests** | 2.31.0+ | HTTP requests to APIs |
| **BeautifulSoup4** | 4.12.2+ | Web scraping |
| **lxml** | 5.1.0+ | HTML/XML parsing |

### Utilities
| Technology | Version | Purpose |
|------------|---------|---------|
| **python-dotenv** | 1.0.0+ | Environment variable management |
| **tiktoken** | 0.8.0+ | Token counting |
| **pydantic** | 2.9.0+ | Data validation |

---

## 🚀 How It Works - Step by Step

### Scenario: User asks "how many champions in lol?"

1. **User Input** (app.py)
   ```python
   user_question = "how many champions in lol?"
   st.session_state[SESSION_MESSAGES].append({
       "role": "user",
       "content": user_question
   })
   ```

2. **Send to Workflow** (app.py → langgraph_workflow.py)
   ```python
   response = process_query(
       question=user_question,
       graph=workflow,
       conversation_history=previous_messages
   )
   ```

3. **Extract Question** (langgraph_workflow.py)
   ```python
   # GraphState updated with question
   state["question"] = "how many champions in lol?"
   ```

4. **Generate Answer** (langgraph_workflow.py → rag_system.py)
   ```python
   answer = rag_system.query(
       question="how many champions in lol?",
       chat_history=formatted_history
   )
   ```

5. **LLM with Tools** (rag_system.py)
   ```python
   # LLM receives prompt with tools
   prompt = """You have access to tools...
   Question: how many champions in lol?"""
   
   # LLM decides: "I should use count_champions tool"
   tool_calls = [
       {
           "name": "count_champions",
           "args": {}
       }
   ]
   ```

6. **Execute Tool** (rag_system.py)
   ```python
   def count_champions(role_filter=""):
       results = vectorstore.get(
           where={"type": "champion"},
           limit=2000
       )
       unique_champions = set()
       for metadata in results['metadatas']:
           unique_champions.add(metadata['champion'])
       
       return f"There are {len(unique_champions)} champions"
   
   # Result: "There are 172 champions in League of Legends."
   ```

7. **Generate Final Answer** (rag_system.py)
   ```python
   # LLM receives tool result
   final_prompt = """Tool Results:
   count_champions: There are 172 champions in League of Legends.
   
   Question: how many champions in lol?
   
   Answer based ONLY on tool results."""
   
   # LLM generates: "There are 172 champions in League of Legends."
   ```

8. **Return to User** (langgraph_workflow.py → app.py)
   ```python
   st.session_state[SESSION_MESSAGES].append({
       "role": "assistant",
       "content": "There are 172 champions in League of Legends."
   })
   st.chat_message("assistant").write(answer)
   ```

---

## 🎯 Key Features

### 1. **Intelligent Tool Calling (ReAct Pattern)**
- LLM automatically decides which tool to use
- No hardcoded query patterns
- Truly general solution

**Example Flow**:
```
Q: "how many mage champions?"
   └─▶ LLM thinks: "This is a counting question with a filter"
   └─▶ Calls: count_champions(role_filter="Mage")
   └─▶ Returns: "There are X mage champions"
```

### 2. **Conversation Memory**
- Remembers previous messages in session
- Formats history for LLM context
- Enables follow-up questions

**Example**:
```
[1] USER: "who is yasuo?"
[2] ASSISTANT: "Yasuo is a skilled swordsman..."
[3] USER: "how many skins does he have?"  # "he" = Yasuo
[2] ASSISTANT: "Yasuo has 15 skins..."     # Remembers context
```

### 3. **Hallucination Prevention**
- Strict prompts: "ONLY use tool results"
- "NEVER use training data"
- "Say 'I don't have that information' if not in context"

### 4. **Live Data**
- Data from Riot's Data Dragon API v15.24.1
- All 172 current champions
- Regularly updatable

### 5. **Copy Conversation Feature**
- Button in sidebar to copy entire chat
- Formatted as: `[1] USER: ... [2] ASSISTANT: ...`
- Useful for debugging and sharing

---

## 🔐 Environment Setup

### Required API Keys

1. **OpenAI API Key** (Required)
   - Used for: Embeddings + LLM
   - Get from: https://platform.openai.com/api-keys
   
2. **LangSmith API Key** (Optional)
   - Used for: Monitoring and tracing
   - Get from: https://smith.langchain.com

### `.env` File
```env
OPENAI_API_KEY=sk-proj-...
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=lolqa
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING=true
```

---

## 🐛 Recent Fixes & Improvements

### 1. **Context Memory Bug** ✅
- **Problem**: Agent didn't remember previous messages
- **Solution**: 
  - Added `chat_history` parameter to RAG system
  - Updated prompt template to include conversation history
  - Modified LangGraph workflow to pass history

### 2. **Hallucination Issue** ✅
- **Problem**: Agent mentioned "October 2023" training data
- **Solution**:
  - Strengthened prompt with "CRITICAL INSTRUCTIONS"
  - Added `get_database_info()` tool
  - Explicit rules against mentioning training cutoff

### 3. **Champion Count Bug** ✅
- **Problem**: Showed 121 champions instead of 172
- **Solution**:
  - Database had all 172 champions (711 chunks)
  - Increased vectorstore.get() limit from 500 → 2000
  - Now correctly counts all unique champions

### 4. **Tool Calling Implementation** ✅
- **Problem**: Manual query classification was too rigid
- **Solution**:
  - Implemented ReAct pattern with OpenAI function calling
  - LLM decides which tools to use
  - Truly general, extensible solution

---

## 📊 Performance & Scalability

### Current Capacity
- **Champions**: 172 (all current LoL champions)
- **Documents**: 181 raw documents
- **Chunks**: 711 vector store chunks
- **Retrieval Speed**: ~1-2 seconds per query
- **Concurrent Users**: Limited by Streamlit free tier

### Optimization Opportunities
1. **Caching**: Cache frequent queries
2. **Batch Processing**: Process multiple tool calls in parallel
3. **Streaming**: Stream LLM responses for better UX
4. **Redis**: Add Redis for session management at scale

---

## 🚀 Deployment Options

### 1. **Local Development**
```bash
streamlit run app.py
```
Access at: `http://localhost:8501`

### 2. **Docker**
```bash
docker build -t lolqa .
docker run -p 8501:8501 --env-file .env lolqa
```

### 3. **Cloud Platforms**
- **Streamlit Cloud**: Easiest for Streamlit apps
- **Railway**: One-click deployment
- **Render**: Good for production
- **Heroku**: Enterprise-grade

---

## 🎓 Learning Resources

### Key Concepts to Understand

1. **RAG (Retrieval-Augmented Generation)**
   - Combines retrieval with generation
   - Grounds LLM responses in facts
   - Prevents hallucination

2. **Vector Embeddings**
   - Convert text to numerical vectors
   - Enable semantic similarity search
   - More powerful than keyword search

3. **LangChain Expression Language (LCEL)**
   - Chain components with `|` operator
   - Example: `retriever | prompt | llm | parser`

4. **LangGraph**
   - State machines for workflows
   - Manage conversation state
   - Orchestrate complex flows

5. **Tool Calling (Function Calling)**
   - LLM decides which functions to call
   - Structured output from LLM
   - ReAct pattern: Reason + Act

---

## 🔮 Future Enhancements

### Possible Improvements
1. ✨ **Multi-turn conversations** with memory persistence
2. ✨ **Image generation** for champion builds
3. ✨ **Voice input/output** for hands-free interaction
4. ✨ **Champion comparison** tool
5. ✨ **Real-time match data** integration
6. ✨ **Build recommendations** based on enemy comp
7. ✨ **Patch notes** summarization
8. ✨ **Multiple languages** support

---

## 📞 Support & Contribution

### Getting Help
- 📖 Read the docs in the project root
- 🐛 Open an issue on GitHub
- 💬 Check existing issues for solutions

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📝 Quick Reference Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
streamlit run app.py

# Rebuild database
rm -rf chroma_db/
streamlit run app.py  # Will auto-rebuild

# Docker
docker build -t lolqa .
docker run -p 8501:8501 --env-file .env lolqa

# Git
git add .
git commit -m "Your message"
git push origin branch-name
```

---

## 🎯 Summary

**LOLQA** is a production-ready RAG application that demonstrates:
- ✅ Modern LLM application architecture
- ✅ Intelligent tool calling with ReAct pattern
- ✅ Conversation memory and context awareness
- ✅ Hallucination prevention through strict prompting
- ✅ Data collection from multiple sources
- ✅ Vector database for semantic search
- ✅ Workflow orchestration with LangGraph
- ✅ Monitoring and observability with LangSmith

**Tech Stack**: LangChain + LangGraph + OpenAI + ChromaDB + Streamlit

**Data**: 172 League of Legends champions from Data Dragon API v15.24.1

**Deployment**: Docker, Streamlit Cloud, Railway, Render, Heroku

---

Made with ⚔️ for League of Legends fans!


# 🎯 LOLQA Project - Complete Guide

> **Production-Ready League of Legends Q&A Assistant with RAG, Tool Calling & 80% Test Coverage**

---

## 📖 Table of Contents

1. [What is LOLQA?](#what-is-lolqa)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Project Structure](#project-structure)
5. [Tech Stack](#tech-stack)
6. [How It Works](#how-it-works)
7. [Quick Start](#quick-start)
8. [Component Details](#component-details)
9. [Data Flow Diagrams](#data-flow-diagrams)
10. [Project Statistics](#project-statistics)
11. [Use Cases](#use-cases)
12. [Technical Highlights](#technical-highlights)
13. [Quality Metrics](#quality-metrics)
14. [Recent Improvements](#recent-improvements)
15. [Deployment](#deployment)
16. [Documentation](#documentation)
17. [Contributing](#contributing)

---

## 📖 What is LOLQA?

**LOLQA** (League of Legends Q&A) is a production-ready, intelligent chatbot application that answers questions about League of Legends using **Retrieval-Augmented Generation (RAG)** with LangChain, LangGraph, and OpenAI.

The application demonstrates modern AI development practices including:
- ⚔️ **RAG Architecture** with semantic search
- 🤖 **Tool Calling** (ReAct pattern) for intelligent query routing
- 💬 **Conversation Memory** for context-aware responses
- 🧪 **80% Test Coverage** with comprehensive test suite
- 📚 **Clean Architecture** following Python best practices
- 🚀 **Production-Ready** with Docker & CI/CD

---

## ✨ Key Features

### 🧠 Intelligent Question Answering
- ✅ Answer questions about **172 League of Legends champions**
- ✅ Provide detailed information (abilities, stats, skins, lore)
- ✅ Count and list champions with role filtering
- ✅ Remember conversation context for follow-up questions
- ✅ No hallucination - strictly uses knowledge base

### 🤖 Advanced AI Capabilities
- ✅ **Tool Calling (ReAct Pattern)**: LLM intelligently decides which tools to use
- ✅ **No Hallucination**: Strictly uses knowledge base, not training data
- ✅ **Context Memory**: Remembers entire conversation history
- ✅ **4 Specialized Tools**:
  - `search_champion_info`: Semantic search for specific information
  - `count_champions`: Count champions with optional role filtering
  - `list_champions`: List champion names (with filtering)
  - `get_database_info`: Data freshness information

### 📊 Data & Knowledge Base
- ✅ **172 champions** from Riot Games Data Dragon API v15.24.1
- ✅ **711 document chunks** in vector database
- ✅ **Multiple data sources**: Data Dragon, Web Scraper, Sample Data
- ✅ **Semantic search** with ChromaDB vector store
- ✅ **Auto-updating** from live APIs

### 🏗️ Professional Quality
- ✅ **Clean code structure**: Organized in `src/` directory
- ✅ **Modular design**: Separated concerns (core, data, config, utils)
- ✅ **Well-documented**: 8 active documentation files
- ✅ **Fully tested**: 75+ tests with 80% coverage
- ✅ **Production-ready**: Docker, CI/CD configs included
- ✅ **Type hints**: Throughout codebase

---

## 🏗️ Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER (Web Browser)                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STREAMLIT UI (app.py)                            │
│                 - Chat interface                                 │
│                 - Session management                             │
│                 - Copy conversation                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         LANGGRAPH WORKFLOW (src/core/workflow.py)               │
│         - Extract question                                       │
│         - Generate answer                                        │
│         - Format response                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│          RAG SYSTEM (src/core/rag_system.py)                    │
│                                                                   │
│  LLM with Tools (ReAct Pattern):                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   search_    │  │    count_    │  │     list_    │          │
│  │  champion_   │  │  champions   │  │  champions   │          │
│  │    info      │  │              │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └─────────────────┴─────────────────┘                    │
│                         │                                         │
│                         ▼                                         │
│              VECTOR STORE (ChromaDB)                             │
│              - 172 champions                                     │
│              - 711 chunks                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│       DATA COLLECTION (src/data/collector.py)                   │
│       - Data Dragon API (Riot Games)                            │
│       - Web Scraper (League Wiki)                               │
│       - Sample Data (Fallback)                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                              │
│                                                                   │
│  app.py                                                          │
│  ├─ handle_user_input()      → Process user messages            │
│  ├─ process_query()           → Invoke workflow                  │
│  ├─ render_sidebar()          → Display conversation controls    │
│  └─ initialize_systems()      → Setup RAG + Workflow            │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│              ORCHESTRATION LAYER                                  │
│                                                                   │
│  src/core/workflow.py (LangGraph)                                │
│  ├─ _extract_question()       → Get user question               │
│  ├─ _generate_answer()        → Call RAG system                 │
│  └─ _format_response()        → Format for display              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│                    RAG LAYER                                      │
│                                                                   │
│  src/core/rag_system.py                                          │
│  ├─ query()                   → Main query processing            │
│  ├─ _create_tools()           → Define available tools           │
│  ├─ get_relevant_documents()  → Semantic search                  │
│  └─ initialize()              → Setup embeddings & LLM           │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│                   DATA LAYER                                      │
│                                                                   │
│  src/data/collector.py + src/data/sources/*                     │
│  ├─ DataDragonCollector      → Fetch champions from Riot        │
│  ├─ WebScraperCollector       → Scrape wiki content             │
│  ├─ SampleDataCollector       → Fallback data                   │
│  └─ RiotAPICollector          → Live API data (optional)        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────────┐
│                  STORAGE LAYER                                    │
│                                                                   │
│  ChromaDB (Vector Database)                                      │
│  ├─ 172 unique champions                                         │
│  ├─ 711 document chunks                                          │
│  ├─ 1536-dim embeddings                                          │
│  └─ Metadata: {type, champion, role, source}                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
LOLQA/
├── app.py                         # 📱 Main Streamlit application
├── requirements.txt               # Python dependencies
├── requirements-test.txt          # Testing dependencies
├── pytest.ini                     # Pytest configuration
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
│
├── src/                           # 📦 SOURCE CODE
│   ├── __init__.py
│   │
│   ├── core/                      # 🧠 Core Functionality
│   │   ├── __init__.py
│   │   ├── rag_system.py          # RAG with tool calling
│   │   └── workflow.py            # LangGraph orchestration
│   │
│   ├── data/                      # 📊 Data Management
│   │   ├── __init__.py
│   │   ├── collector.py           # Main orchestrator
│   │   └── sources/               # Data source collectors
│   │       ├── __init__.py
│   │       ├── base.py            # Base collector class
│   │       ├── data_dragon.py     # Riot Data Dragon API
│   │       ├── web_scraper.py     # Web scraping
│   │       ├── riot_api.py        # Riot Games API
│   │       └── sample_data.py     # Fallback data
│   │
│   ├── config/                    # ⚙️ Configuration
│   │   ├── __init__.py
│   │   ├── settings.py            # App settings
│   │   └── constants.py           # Constants & prompts
│   │
│   └── utils/                     # 🛠️ Utilities
│       ├── __init__.py
│       └── helpers.py             # Helper functions
│
├── tests/                         # 🧪 TEST SUITE
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures (15+)
│   ├── test_utils.py             # 18 tests
│   ├── test_config.py            # 12 tests
│   ├── test_data_collectors.py   # 15 tests
│   ├── test_rag_system.py        # 10 tests
│   ├── test_workflow.py          # 9 tests
│   └── test_integration.py       # 6 tests
│
├── docs/                          # 📚 DOCUMENTATION
│   ├── README.md                  # Documentation index
│   ├── PROJECT_GUIDE.md          # This file (comprehensive)
│   ├── QUICKSTART.md             # Quick start (5 min)
│   ├── API_KEYS_SETUP.md         # API configuration
│   ├── DATA_COLLECTION.md        # Data collection details
│   ├── TESTING.md                # Testing guide
│   └── archive/                  # Historical docs
│       ├── MIGRATION_GUIDE.md
│       ├── REORGANIZATION_SUMMARY.md
│       └── TESTING_SUMMARY.md
│
├── deployment/                    # 🚀 DEPLOYMENT
│   ├── Dockerfile                # Docker configuration
│   ├── Procfile                  # Heroku/Railway config
│   └── render.yaml               # Render.com config
│
├── scripts/                       # 📜 SCRIPTS
│   ├── setup.sh                  # Setup script
│   └── upgrade_python.sh         # Python upgrade
│
├── .github/                       # 🔄 CI/CD
│   └── workflows/
│       └── tests.yml             # Automated testing
│
├── chroma_db/                     # 💾 Vector database
└── venv/                          # 🐍 Virtual environment
```

### Module Organization

| Module | Purpose | Key Files |
|--------|---------|-----------|
| **src/core/** | Business logic | rag_system.py, workflow.py |
| **src/data/** | Data collection | collector.py, sources/* |
| **src/config/** | Configuration | settings.py, constants.py |
| **src/utils/** | Utilities | helpers.py |
| **tests/** | Test suite | test_*.py, conftest.py |
| **docs/** | Documentation | *.md files |
| **deployment/** | Deployment | Dockerfile, Procfile |
| **scripts/** | Utilities | setup.sh |

---

## 💻 Tech Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Framework** | LangChain | 1.1.3 | RAG framework |
| **Workflow** | LangGraph | 1.0.0+ | Orchestration |
| **Monitoring** | LangSmith | 0.1.0+ | Tracing |
| **LLM** | OpenAI | GPT-4o-mini | Answer generation |
| **Embeddings** | OpenAI | text-embedding-3-small | Vector embeddings |
| **Vector DB** | ChromaDB | 0.5.0+ | Semantic search |
| **Web UI** | Streamlit | 1.39.0+ | User interface |
| **Testing** | pytest | 7.4.0+ | Test framework |
| **Coverage** | pytest-cov | 4.1.0+ | Code coverage |
| **Python** | 3.11+ | - | Programming language |

---

## 🎯 How It Works

### Query Processing Flow

```
1. User asks: "how many champions in lol?"
   ↓
2. Streamlit UI receives question
   ↓
3. LangGraph Workflow invoked
   ↓
4. RAG System processes query
   ↓
5. LLM analyzes question → Decides to use count_champions tool
   ↓
6. Tool queries ChromaDB → Counts unique champions
   ↓
7. Tool returns: "There are 172 champions in League of Legends"
   ↓
8. LLM generates final answer using tool result
   ↓
9. Answer displayed to user
```

### Tool Calling (ReAct Pattern)

The LLM automatically decides which tool to use based on the question:

| Question | Tool Used | Result |
|----------|-----------|--------|
| "how many champions?" | `count_champions()` | Counts from database |
| "who is Yasuo?" | `search_champion_info("Yasuo")` | Semantic search |
| "list all mages" | `list_champions(role_filter="Mage")` | Filtered list |
| "when updated?" | `get_database_info()` | Data source info |

### Conversation Memory

The system remembers the entire conversation history:

```
User: "Who is Yasuo?"
Assistant: "Yasuo is a skilled swordsman champion..."

User: "How many skins does he have?"  # "he" refers to Yasuo
Assistant: "Yasuo has 15 skins including..."
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone or navigate to project
cd LOLQA

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt  # For testing

# Setup environment
cp .env.example .env
# Edit .env with your API keys
```

### 2. Configure API Keys

Edit `.env` file:

```env
# Required
OPENAI_API_KEY=sk-...

# Optional (for monitoring)
LANGSMITH_API_KEY=ls__...
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=lolqa

# Optional (for live data)
RIOT_API_KEY=RGAPI-...
```

### 3. Run Application

```bash
streamlit run app.py
```

Access at: **http://localhost:8501**

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test types
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
```

---

**(Continued in next message due to length...)**


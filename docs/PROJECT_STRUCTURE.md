# 📁 Project Structure

This document explains the organized structure of the LOLQA project.

## 🏗️ Directory Layout

```
LOLQA/
│
├── 📱 APPLICATION
│   ├── app_new.py                    # Main Streamlit application (NEW)
│   ├── app.py                        # Old app (deprecated, will be removed)
│   └── requirements.txt              # Python dependencies
│
├── 📦 SOURCE CODE (src/)
│   ├── __init__.py
│   │
│   ├── 🧠 core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── rag_system.py             # RAG system with tool calling
│   │   └── workflow.py               # LangGraph workflow orchestration
│   │
│   ├── 📊 data/                      # Data collection
│   │   ├── __init__.py
│   │   ├── collector.py              # Main data collector orchestrator
│   │   └── sources/                  # Data source collectors
│   │       ├── __init__.py
│   │       ├── base.py               # Base collector class
│   │       ├── data_dragon.py        # Riot Data Dragon API
│   │       ├── web_scraper.py        # Web scraping
│   │       ├── riot_api.py           # Riot Games API
│   │       └── sample_data.py        # Fallback sample data
│   │
│   ├── ⚙️ config/                    # Configuration
│   │   ├── __init__.py
│   │   ├── settings.py               # Application settings
│   │   └── constants.py              # Constants and prompts
│   │
│   └── 🛠️ utils/                     # Utilities
│       ├── __init__.py
│       └── helpers.py                # Helper functions
│
├── 📚 DOCUMENTATION (docs/)
│   ├── README.md                     # Main documentation (copied to root)
│   ├── PROJECT_SUMMARY.md            # Complete project summary
│   ├── PROJECT_ARCHITECTURE.md       # Detailed architecture
│   ├── ARCHITECTURE_DIAGRAM.md       # Visual diagrams
│   ├── PROJECT_STRUCTURE.md          # This file
│   ├── QUICKSTART.md                 # Quick start guide
│   ├── API_KEYS_SETUP.md            # API keys setup guide
│   ├── DATA_COLLECTION.md           # Data collection details
│   └── DATA_COLLECTION_QUICKSTART.md # Quick data collection guide
│
├── 🚀 DEPLOYMENT (deployment/)
│   ├── Dockerfile                    # Docker configuration
│   ├── Procfile                      # Heroku/Railway config
│   └── render.yaml                   # Render.com config
│
├── 📜 SCRIPTS (scripts/)
│   ├── setup.sh                      # Setup script
│   └── upgrade_python.sh             # Python upgrade script
│
├── 🧪 TESTS (tests/)
│   ├── __init__.py
│   ├── test_rag_system.py           # (To be created)
│   ├── test_workflow.py             # (To be created)
│   └── test_data_collector.py       # (To be created)
│
├── 💾 DATABASE
│   └── chroma_db/                    # Vector database (gitignored)
│
├── 📝 CONFIGURATION FILES
│   ├── .env                          # Environment variables (gitignored)
│   ├── .env.example                  # Example environment file
│   ├── .gitignore                    # Git ignore rules
│   └── requirements.txt              # Python dependencies
│
└── 🔧 OLD FILES (To be removed)
    ├── rag_system.py                 # → src/core/rag_system.py
    ├── langgraph_workflow.py         # → src/core/workflow.py
    ├── data_collector.py             # → src/data/collector.py
    ├── config.py                     # → src/config/settings.py
    ├── constants.py                  # → src/config/constants.py
    ├── utils.py                      # → src/utils/helpers.py
    └── data_sources/                 # → src/data/sources/
```

## 📦 Module Organization

### 1. **src/core/** - Core Functionality
Contains the main business logic:
- **rag_system.py**: RAG system with OpenAI tool calling
- **workflow.py**: LangGraph workflow orchestration

### 2. **src/data/** - Data Management
Handles all data collection:
- **collector.py**: Orchestrates multiple data sources
- **sources/**: Individual data source collectors
  - **base.py**: Abstract base class
  - **data_dragon.py**: Riot's static data API
  - **web_scraper.py**: Web scraping for lore
  - **riot_api.py**: Live game data API
  - **sample_data.py**: Fallback data

### 3. **src/config/** - Configuration
Centralizes all configuration:
- **settings.py**: Application settings (models, paths, etc.)
- **constants.py**: Prompt templates, error messages, UI strings

### 4. **src/utils/** - Utilities
Helper functions:
- **helpers.py**: Logging, validation, formatting

### 5. **docs/** - Documentation
All documentation files organized in one place

### 6. **deployment/** - Deployment Configs
Docker and cloud deployment configurations

### 7. **scripts/** - Utility Scripts
Setup and maintenance scripts

### 8. **tests/** - Test Suite
Unit and integration tests (to be implemented)

## 🔄 Import Structure

### Old Way (Deprecated)
```python
from rag_system import LoLRAGSystem
from langgraph_workflow import LoLQAGraph
from data_collector import LoLDataCollector
from config import config
from constants import ERROR_MESSAGE
from utils import logger
```

### New Way (Organized)
```python
from src.core import LoLRAGSystem, LoLQAGraph
from src.data import LoLDataCollector
from src.config import config
from src.config.constants import ERROR_MESSAGE
from src.utils import logger
```

## 📝 Benefits of New Structure

### ✅ Better Organization
- Clear separation of concerns
- Easy to find files
- Logical grouping

### ✅ Easier Maintenance
- Changes isolated to specific modules
- Clear dependencies
- Better code navigation

### ✅ Scalability
- Easy to add new features
- Can add new data sources easily
- Can add new tools/utilities

### ✅ Professional Structure
- Follows Python best practices
- Similar to production projects
- Ready for team collaboration

### ✅ Testing
- Dedicated tests directory
- Easy to write unit tests
- Clear test organization

## 🚀 Running the Application

### With New Structure
```bash
# Activate virtual environment
source venv/bin/activate

# Run the new app
streamlit run app_new.py
```

### After Migration Complete
```bash
# The old app.py will be replaced with app_new.py
streamlit run app.py
```

## 📚 Next Steps

1. **Test the new structure**: Ensure app_new.py works correctly
2. **Remove old files**: Delete deprecated files after testing
3. **Add tests**: Create unit tests in tests/ directory
4. **Update CI/CD**: Update deployment scripts if any
5. **Document changes**: Update README with new structure

## 🔗 Related Documentation

- [Project Summary](PROJECT_SUMMARY.md) - Complete overview
- [Architecture](PROJECT_ARCHITECTURE.md) - Detailed architecture
- [Quick Start](QUICKSTART.md) - Getting started guide
- [API Keys Setup](API_KEYS_SETUP.md) - Setting up API keys

---

Made with ⚔️ for better code organization!


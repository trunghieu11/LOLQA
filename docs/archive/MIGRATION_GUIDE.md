# 🔄 Migration Guide - Old to New Structure

This guide explains how to migrate from the old flat structure to the new organized structure.

## 📋 What Changed

### Directory Structure

**Before (Old)**:
```
LOLQA/
├── app.py
├── rag_system.py
├── langgraph_workflow.py
├── data_collector.py
├── config.py
├── constants.py
├── utils.py
├── data_sources/
│   ├── base_collector.py
│   ├── data_dragon_collector.py
│   ├── web_scraper_collector.py
│   ├── riot_api_collector.py
│   └── sample_data_collector.py
└── *.md files everywhere
```

**After (New)**:
```
LOLQA/
├── app_new.py                    # Updated main app
├── src/
│   ├── core/                     # Core logic
│   │   ├── rag_system.py
│   │   └── workflow.py
│   ├── data/                     # Data management
│   │   ├── collector.py
│   │   └── sources/
│   │       ├── base.py
│   │       ├── data_dragon.py
│   │       ├── web_scraper.py
│   │       ├── riot_api.py
│   │       └── sample_data.py
│   ├── config/                   # Configuration
│   │   ├── settings.py
│   │   └── constants.py
│   └── utils/                    # Utilities
│       └── helpers.py
├── docs/                         # All documentation
├── deployment/                   # Deployment configs
├── scripts/                      # Utility scripts
└── tests/                        # Test suite
```

## 🔄 Import Changes

### Old Imports
```python
from rag_system import LoLRAGSystem
from langgraph_workflow import LoLQAGraph
from data_collector import LoLDataCollector
from config import config
from constants import ERROR_MESSAGE
from utils import logger
from data_sources import DataDragonCollector
```

### New Imports
```python
from src.core import LoLRAGSystem, LoLQAGraph
from src.data import LoLDataCollector
from src.config import config
from src.config.constants import ERROR_MESSAGE
from src.utils import logger
from src.data.sources import DataDragonCollector
```

## 📝 File Mapping

| Old Location | New Location | Notes |
|--------------|--------------|-------|
| `app.py` | `app_new.py` | Updated with new imports |
| `rag_system.py` | `src/core/rag_system.py` | Moved to core |
| `langgraph_workflow.py` | `src/core/workflow.py` | Renamed & moved |
| `data_collector.py` | `src/data/collector.py` | Renamed & moved |
| `config.py` | `src/config/settings.py` | Renamed & moved |
| `constants.py` | `src/config/constants.py` | Moved to config |
| `utils.py` | `src/utils/helpers.py` | Renamed & moved |
| `data_sources/base_collector.py` | `src/data/sources/base.py` | Renamed & moved |
| `data_sources/data_dragon_collector.py` | `src/data/sources/data_dragon.py` | Renamed & moved |
| `data_sources/web_scraper_collector.py` | `src/data/sources/web_scraper.py` | Renamed & moved |
| `data_sources/riot_api_collector.py` | `src/data/sources/riot_api.py` | Renamed & moved |
| `data_sources/sample_data_collector.py` | `src/data/sources/sample_data.py` | Renamed & moved |
| `*.md` (scattered) | `docs/*.md` | Organized in docs/ |
| `Dockerfile`, `Procfile`, `render.yaml` | `deployment/` | Moved to deployment/ |
| `setup.sh`, `upgrade_python.sh` | `scripts/` | Moved to scripts/ |

## 🚀 How to Use the New Structure

### 1. Running the Application

**Old way**:
```bash
streamlit run app.py
```

**New way** (during migration):
```bash
streamlit run app_new.py
```

**After migration complete**:
```bash
# app_new.py will be renamed to app.py
streamlit run app.py
```

### 2. Importing Modules

**In your own code**:
```python
# Import core functionality
from src.core import LoLRAGSystem, LoLQAGraph

# Import data collectors
from src.data import LoLDataCollector
from src.data.sources import DataDragonCollector

# Import configuration
from src.config import config
from src.config.constants import ERROR_MESSAGE

# Import utilities
from src.utils import logger, format_documents
```

### 3. Adding New Features

**Adding a new data source**:
```python
# Create: src/data/sources/my_new_source.py
from src.data.sources.base import BaseDataCollector

class MyNewCollector(BaseDataCollector):
    # Your implementation
    pass

# Register in: src/data/sources/__init__.py
from src.data.sources.my_new_source import MyNewCollector
__all__.append("MyNewCollector")
```

**Adding a new utility**:
```python
# Add to: src/utils/helpers.py
def my_new_helper():
    pass

# Export in: src/utils/__init__.py
from src.utils.helpers import my_new_helper
__all__.append("my_new_helper")
```

## ✅ Migration Checklist

- [x] Create new directory structure
- [x] Move files to new locations
- [x] Update all imports
- [x] Create __init__.py files
- [x] Create .env.example
- [x] Update .gitignore
- [x] Create app_new.py with new imports
- [x] Test imports work
- [ ] Test app_new.py runs successfully
- [ ] Update all documentation
- [ ] Remove old files
- [ ] Rename app_new.py to app.py

## 🐛 Troubleshooting

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'src'`

**Solution**: Make sure you're running from the project root and have `__init__.py` files in all directories.

### Path Issues

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: './chroma_db'`

**Solution**: The paths in `src/config/settings.py` are relative to project root. Run from project root.

### Old Imports Still Used

**Error**: `ModuleNotFoundError: No module named 'rag_system'`

**Solution**: Update your imports to use the new structure (`from src.core import LoLRAGSystem`).

## 📚 Benefits of New Structure

1. **Better Organization**: Files grouped by function
2. **Easier Navigation**: Clear where each file belongs
3. **Scalability**: Easy to add new features
4. **Professional**: Follows Python best practices
5. **Testable**: Dedicated tests directory
6. **Maintainable**: Clear dependencies

## 🔗 Related Documentation

- [Project Structure](docs/PROJECT_STRUCTURE.md) - Detailed structure explanation
- [Project Summary](docs/PROJECT_SUMMARY.md) - Complete project overview
- [README](README.md) - Updated main documentation

---

Made with ⚔️ for better code organization!


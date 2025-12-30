# 📊 Data Collection System

---

## 🚀 Quick Start

### Default Setup (No Configuration Needed)

The system works out of the box with default settings:

```bash
# Start all microservices
docker-compose up --build

# Ingest data (uses Data Dragon + Web Scraper + Sample Data)
curl -X POST http://localhost:8003/ingest -H "Content-Type: application/json" -d '{}'
```

**Default behavior:**
- ✅ **Data Dragon** enabled - Fetches all 172 champions (no API key needed)
- ✅ **Web Scraper** enabled - Fetches lore and wiki content  
- ❌ **Riot API** disabled - Requires API key
- ✅ **Sample Data** enabled - Fallback

### Optional Configuration

Add to your `.env` file:

```env
# Enable/disable data sources
USE_DATA_DRAGON=true    # Recommended
USE_WEB_SCRAPER=true    # Gets lore
USE_RIOT_API=false      # Requires API key
USE_SAMPLE_DATA=true    # Fallback

# Optional: Riot API (if enabled)
RIOT_API_KEY=your_key_here
RIOT_API_REGION=na1
```

---

## 📋 Overview

The League of Legends Q&A application uses a **modular data collection system** that can fetch data from multiple sources:

1. **Data Dragon API** (Recommended) - Riot's public static data API (no API key needed)
2. **Web Scraper** - Scrapes League of Legends wiki for lore and additional information
3. **Riot Games API** - Official API for live data (requires API key, rate-limited)
4. **Sample Data** - Fallback hardcoded data when other sources are unavailable

---

## 🎯 Features

- ✅ **Multiple Data Sources** - Collect from APIs, web scraping, or fallback data
- ✅ **Automatic Fallback** - If one source fails, others are tried
- ✅ **Configurable** - Enable/disable data sources via configuration
- ✅ **Extensible** - Easy to add new data collectors
- ✅ **Error Handling** - Graceful handling of API failures
- ✅ **Logging** - Comprehensive logging of data collection process

---

## 📁 Architecture

```
data_sources/
├── __init__.py              # Package exports
├── base_collector.py         # Base interface for all collectors
├── data_dragon_collector.py  # Riot's Data Dragon API
├── web_scraper_collector.py  # Web scraping for lore
├── riot_api_collector.py     # Riot Games API (requires key)
└── sample_data_collector.py  # Fallback sample data

data_collector.py             # Main aggregator
```

---

## 🔧 Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Data Source Configuration
USE_DATA_DRAGON=true          # Enable Data Dragon (recommended, no key needed)
USE_WEB_SCRAPER=true          # Enable web scraping
USE_RIOT_API=false            # Enable Riot API (requires API key)
USE_SAMPLE_DATA=true          # Enable fallback sample data

# Data Dragon Settings
DATA_DRAGON_VERSION=          # Leave empty for latest version
DATA_DRAGON_LANGUAGE=en_US    # Language code

# Web Scraper Settings
WEB_SCRAPER_BASE_URL=https://leagueoflegends.fandom.com

# Riot API Settings (if enabled)
RIOT_API_KEY=your_riot_api_key_here
RIOT_API_REGION=na1           # Region: na1, euw1, kr, etc.
```

### Configuration in Code

The configuration is managed in `config.py`:

```python
from config import config

# Access data source configuration
config.data_source.use_data_dragon  # True/False
config.data_source.use_web_scraper   # True/False
config.data_source.use_riot_api      # True/False
config.data_source.use_sample_data   # True/False
```

---

## 📚 Data Sources

### 1. Data Dragon Collector (Recommended)

**What it collects:**
- All champion data (abilities, stats, lore)
- Item data
- Game version information

**Advantages:**
- ✅ No API key required
- ✅ Official Riot Games data
- ✅ Always up-to-date
- ✅ Comprehensive champion information

**Usage:**
```python
from data_sources import DataDragonCollector

collector = DataDragonCollector()
documents = collector.collect()  # Returns all champions
items = collector.collect_items()  # Returns all items
```

**API Endpoints Used:**
- `https://ddragon.leagueoflegends.com/api/versions.json` - Get latest version
- `https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/champion.json` - Champion data
- `https://ddragon.leagueoflegends.com/cdn/{version}/data/{language}/item.json` - Item data

### 2. Web Scraper Collector

**What it collects:**
- Game mechanics information
- Lore and story content
- Additional wiki content

**Advantages:**
- ✅ No API key required
- ✅ Rich lore and story content
- ✅ Community-maintained information

**Usage:**
```python
from data_sources import WebScraperCollector

collector = WebScraperCollector()
documents = collector.collect()  # Returns lore and mechanics

# Scrape specific champion lore
lore_doc = collector.scrape_champion_lore("Ahri")
```

**Note:** Web scraping may be slower and depends on website availability.

### 3. Riot Games API Collector

**What it collects:**
- Live match data
- Champion rotations
- Player statistics
- Real-time game data

**Advantages:**
- ✅ Official live data
- ✅ Real-time information

**Disadvantages:**
- ❌ Requires API key
- ❌ Rate-limited
- ❌ More complex setup

**Getting an API Key:**
1. Go to https://developer.riotgames.com/
2. Sign up for a developer account
3. Create an API key
4. Add to `.env`: `RIOT_API_KEY=your_key_here`

**Usage:**
```python
from data_sources import RiotAPICollector

collector = RiotAPICollector(api_key="your_key", region="na1")
documents = collector.collect()  # Returns champion rotations, etc.

# Get specific match data
match_doc = collector.get_match_data("match_id_here")
```

**Rate Limits:**
- Personal API key: 100 requests per 2 minutes
- Production key: Higher limits (requires approval)

### 4. Sample Data Collector (Fallback)

**What it provides:**
- Hardcoded sample data for 5 champions
- Basic game mechanics
- Item information
- Ranked system info

**When it's used:**
- All other sources fail
- Testing/development
- Offline mode

**Usage:**
```python
from data_sources import SampleDataCollector

collector = SampleDataCollector()
documents = collector.collect()  # Returns sample data
```

---

## 🚀 Usage

### Basic Usage

The main `LoLDataCollector` automatically uses all enabled sources:

```python
from data_collector import LoLDataCollector

# Initialize collector (uses config settings)
collector = LoLDataCollector()

# Get all documents from all sources
documents = collector.get_documents()

# Get specific types
champions = collector.get_champion_documents()
lore = collector.get_lore_documents()
items = collector.get_item_documents()

# Force refresh
fresh_docs = collector.refresh_data()
```

### Custom Configuration

```python
from data_collector import LoLDataCollector
from config import config

# Modify configuration
config.data_source.use_data_dragon = True
config.data_source.use_web_scraper = False
config.data_source.use_riot_api = False

# Initialize with custom config
collector = LoLDataCollector()
documents = collector.get_documents()
```

### Using Individual Collectors

```python
from data_sources import DataDragonCollector, WebScraperCollector

# Use Data Dragon only
dd_collector = DataDragonCollector()
champions = dd_collector.collect()
items = dd_collector.collect_items()

# Use Web Scraper only
ws_collector = WebScraperCollector()
lore = ws_collector.collect()
```

---

## 🔌 Creating Custom Data Collectors

To add a new data source, create a class that inherits from `BaseDataCollector`:

```python
from data_sources.base_collector import BaseDataCollector
from langchain_core.documents import Document
from typing import List

class MyCustomCollector(BaseDataCollector):
    """Custom data collector"""
    
    def get_name(self) -> str:
        return "MyCustomCollector"
    
    def collect(self) -> List[Document]:
        """Collect data and return as Documents"""
        documents = []
        
        # Your data collection logic here
        # ...
        
        return documents
    
    def validate(self) -> tuple[bool, str]:
        """Validate if collector can run"""
        # Check API keys, connectivity, etc.
        return True, None
```

Then add it to `data_collector.py`:

```python
from data_sources import MyCustomCollector

# In _initialize_collectors():
if config.data_source.use_my_custom:
    collector = MyCustomCollector()
    self.collectors.append(collector)
```

---

## 📊 Data Collection Flow

```
┌─────────────────────────────────────────┐
│      LoLDataCollector.get_documents()   │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐      ┌───────────────┐
│ Data Dragon   │      │ Web Scraper   │
│ Collector    │      │ Collector     │
└───────────────┘      └───────────────┘
        │                       │
        ▼                       ▼
┌───────────────┐      ┌───────────────┐
│ Riot API      │      │ Sample Data   │
│ Collector     │      │ Collector     │
└───────────────┘      └───────────────┘
        │                       │
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Aggregate Documents │
        │   (Remove duplicates) │
        └───────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │   Return Documents   │
        └───────────────────────┘
```

---

## 🐛 Troubleshooting

### No Data Collected

**Problem:** `get_documents()` returns empty list

**Solutions:**
1. Check logs for error messages
2. Verify internet connection
3. Check if Data Dragon API is accessible
4. Enable sample data as fallback: `USE_SAMPLE_DATA=true`

### Data Dragon API Fails

**Problem:** Data Dragon collector fails

**Solutions:**
1. Check internet connection
2. Verify API endpoint is accessible: `https://ddragon.leagueoflegends.com`
3. Check if version is valid
4. Try without specifying version (auto-detect latest)

### Web Scraper Fails

**Problem:** Web scraper returns no data

**Solutions:**
1. Check if website is accessible
2. Website structure may have changed
3. Check rate limiting (may be blocked)
4. Try different base URL

### Riot API Issues

**Problem:** Riot API collector fails

**Solutions:**
1. Verify API key is valid
2. Check rate limits (may be exceeded)
3. Verify region is correct
4. Check API status: https://developer.riotgames.com/status

---

## 📈 Performance

### Data Collection Times

- **Data Dragon**: ~5-10 seconds (all champions)
- **Web Scraper**: ~10-30 seconds (depends on pages)
- **Riot API**: ~1-2 seconds (limited by rate limits)
- **Sample Data**: <1 second (instant)

### Recommendations

1. **For Production**: Use Data Dragon + Web Scraper
2. **For Development**: Use Sample Data (fastest)
3. **For Real-time Data**: Use Riot API (with rate limiting)
4. **For Maximum Coverage**: Use all sources

---

## 🔄 Updating Data

To refresh data:

```python
# Force refresh from all sources
collector = LoLDataCollector()
fresh_docs = collector.refresh_data()
```

Or delete the vector store to force re-indexing:

```bash
rm -rf chroma_db/
# Next run will collect fresh data
```

---

## 📝 Logging

The system provides detailed logging:

```
INFO - LoLDataCollector initialized with 3 data sources
INFO - Data Dragon collector enabled
INFO - Web scraper collector enabled
INFO - Sample data collector enabled (fallback)
INFO - Collecting data from 3 sources...
INFO - Collecting from DataDragon...
INFO - ✓ DataDragon: Collected 167 documents
INFO - Collecting from WebScraper...
INFO - ✓ WebScraper: Collected 2 documents
INFO - Collecting from SampleData...
INFO - ✓ SampleData: Collected 8 documents
INFO - Data collection complete:
INFO -   ✓ Successful: DataDragon, WebScraper, SampleData
INFO -   Total documents: 177
```

---

## 🎓 Best Practices

1. **Always enable sample data** as fallback
2. **Use Data Dragon** for production (most reliable)
3. **Cache data** - don't re-collect on every request
4. **Handle errors gracefully** - one source failure shouldn't break everything
5. **Monitor rate limits** - especially for Riot API
6. **Log everything** - helps with debugging

---

## 🔗 Resources

- **Data Dragon API**: https://ddragon.leagueoflegends.com/
- **Riot Games API**: https://developer.riotgames.com/
- **League Wiki**: https://leagueoflegends.fandom.com/
- **API Documentation**: https://developer.riotgames.com/apis

---

## ✅ Summary

The new data collection system provides:

- ✅ **Flexible** - Multiple data sources
- ✅ **Reliable** - Automatic fallback
- ✅ **Extensible** - Easy to add new sources
- ✅ **Configurable** - Enable/disable sources
- ✅ **Robust** - Error handling and logging

No more hardcoded data! 🎉


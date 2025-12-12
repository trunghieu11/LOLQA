# 🚀 Data Collection Quick Start

## What Changed?

The data collection system has been **completely refactored** to support multiple real data sources instead of hardcoded sample data.

### Before
- ❌ Hardcoded sample data only
- ❌ No way to fetch real League of Legends data
- ❌ Limited to 5 champions

### After
- ✅ **Data Dragon API** - Fetches all 167+ champions from Riot Games
- ✅ **Web Scraper** - Gets lore and additional information
- ✅ **Riot API** - Live match and player data (optional)
- ✅ **Sample Data** - Fallback when APIs are unavailable
- ✅ **Modular & Extensible** - Easy to add new data sources

---

## Quick Setup

### 1. No Configuration Needed (Default)

The system works out of the box with default settings:

```bash
# Just run your app - it will use Data Dragon + Web Scraper + Sample Data
streamlit run app.py
```

**Default behavior:**
- ✅ Data Dragon enabled (fetches all champions)
- ✅ Web Scraper enabled (fetches lore)
- ❌ Riot API disabled (requires API key)
- ✅ Sample Data enabled (fallback)

### 2. Optional: Configure Data Sources

Add to your `.env` file:

```env
# Enable/disable data sources
USE_DATA_DRAGON=true    # Recommended: Gets all champions (no API key needed)
USE_WEB_SCRAPER=true    # Gets lore and wiki content
USE_RIOT_API=false      # Requires API key
USE_SAMPLE_DATA=true    # Fallback

# Optional: Riot API (if enabled)
RIOT_API_KEY=your_key_here
RIOT_API_REGION=na1
```

---

## What Data is Collected?

### Data Dragon (Default - Recommended)
- ✅ **All 167+ champions** with:
  - Abilities (Q, W, E, R)
  - Passive abilities
  - Stats and roles
  - Lore
  - Titles
- ✅ **All items** with descriptions and costs

### Web Scraper (Default)
- ✅ Game mechanics
- ✅ Lore and story content
- ✅ Wiki information

### Riot API (Optional)
- ✅ Champion rotations
- ✅ Match data
- ✅ Player statistics

### Sample Data (Fallback)
- ✅ 5 sample champions
- ✅ Basic game mechanics
- ✅ Always available

---

## Usage Examples

### Basic Usage (Automatic)

```python
from data_collector import LoLDataCollector

# Automatically uses all enabled sources
collector = LoLDataCollector()
documents = collector.get_documents()  # Gets data from all sources
```

### Get Specific Data Types

```python
collector = LoLDataCollector()

# Get only champions
champions = collector.get_champion_documents()

# Get only lore
lore = collector.get_lore_documents()

# Get only items
items = collector.get_item_documents()
```

### Use Individual Collectors

```python
from data_sources import DataDragonCollector

# Use Data Dragon only
collector = DataDragonCollector()
champions = collector.collect()  # All champions
items = collector.collect_items()  # All items
```

---

## First Run

When you run the app for the first time:

1. **Data Collection** happens automatically
2. **Data Dragon** fetches all champions (~5-10 seconds)
3. **Web Scraper** gets lore (~10-30 seconds)
4. **Vector Store** is created with all data
5. **Subsequent runs** use cached data (fast!)

**Expected output:**
```
INFO - LoLDataCollector initialized with 3 data sources
INFO - Collecting data from 3 sources...
INFO - ✓ DataDragon: Collected 167 documents
INFO - ✓ WebScraper: Collected 2 documents
INFO - ✓ SampleData: Collected 8 documents
INFO - Total documents: 177
```

---

## Troubleshooting

### "No documents collected"

**Solution:** Enable sample data fallback
```env
USE_SAMPLE_DATA=true
```

### "Data Dragon API failed"

**Possible causes:**
- No internet connection
- API temporarily down
- Firewall blocking requests

**Solution:** System automatically falls back to sample data

### "Web Scraper failed"

**Possible causes:**
- Website structure changed
- Rate limiting
- Network issues

**Solution:** Disable if not needed:
```env
USE_WEB_SCRAPER=false
```

---

## Performance

### First Run
- **Data Dragon**: ~5-10 seconds (all champions)
- **Web Scraper**: ~10-30 seconds
- **Total**: ~15-40 seconds

### Subsequent Runs
- **Cached**: <1 second (uses existing vector store)

### To Force Refresh
```python
collector = LoLDataCollector()
fresh_docs = collector.refresh_data()  # Re-collects from all sources
```

Or delete the vector store:
```bash
rm -rf chroma_db/
```

---

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `USE_DATA_DRAGON` | `true` | Enable Data Dragon (recommended) |
| `USE_WEB_SCRAPER` | `true` | Enable web scraping |
| `USE_RIOT_API` | `false` | Enable Riot API (needs key) |
| `USE_SAMPLE_DATA` | `true` | Enable fallback data |
| `DATA_DRAGON_VERSION` | (auto) | Game version (empty = latest) |
| `DATA_DRAGON_LANGUAGE` | `en_US` | Language code |
| `RIOT_API_KEY` | (none) | Riot API key |
| `RIOT_API_REGION` | `na1` | API region |

---

## Benefits

✅ **Real Data** - Fetches actual League of Legends data  
✅ **Up-to-Date** - Always uses latest game version  
✅ **Comprehensive** - All 167+ champions, not just 5  
✅ **Reliable** - Automatic fallback if APIs fail  
✅ **Extensible** - Easy to add new data sources  
✅ **Configurable** - Enable/disable sources as needed  

---

## Next Steps

1. **Run the app** - It will automatically collect data
2. **Check logs** - See what data was collected
3. **Ask questions** - Try asking about any champion!
4. **Customize** - Add your own data collectors if needed

For detailed documentation, see [DATA_COLLECTION.md](DATA_COLLECTION.md)

---

## Example Questions You Can Now Ask

With real data, you can ask about **any champion**:

- "Tell me about Ahri's abilities"
- "What is Yasuo's playstyle?"
- "How does Jinx's ultimate work?"
- "What are the best items for Thresh?"
- "Explain Lee Sin's combo"

The system now has data for **all 167+ champions**! 🎉


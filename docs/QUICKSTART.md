# 🚀 Quick Start Guide

Get your League of Legends Q&A application up and running in minutes!

## Prerequisites

- Python 3.11+ installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- LangSmith API key ([Get one here](https://smith.langchain.com/)) - Optional but recommended

> 📖 **Need detailed instructions?** See the [API Keys Setup Guide](API_KEYS_SETUP.md) for step-by-step help.

## Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
./setup.sh
```

Then:
1. Edit `.env` and add your API keys
2. Activate the virtual environment: `source venv/bin/activate`
3. Run: `streamlit run app.py`

## Option 2: Manual Setup

1. **Create virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Create `.env` file**:
```env
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=lolqa
```

4. **Run the application**:
```bash
streamlit run app.py
```

5. **Open your browser** to `http://localhost:8501`

## First Run

On the first run, the application will:
- Create sample League of Legends data
- Generate embeddings
- Build the vector store
- This may take 1-2 minutes

## Testing

Try asking:
- "What are Ahri's abilities?"
- "How should I play Yasuo?"
- "Tell me about teamfighting"

## Troubleshooting

**"OPENAI_API_KEY not found"**
- Make sure your `.env` file exists and contains your API key

**Port 8501 already in use**
- Use a different port: `streamlit run app.py --server.port=8502`

**Vector store errors**
- Delete the `chroma_db` folder and restart

## Next Steps

- Add more champions to `data_collector.py`
- Customize the LLM model in `rag_system.py`
- Deploy to Streamlit Cloud, Railway, or Render (see README.md)

Happy coding! ⚔️


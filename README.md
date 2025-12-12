# ⚔️ LOLQA - League of Legends Q&A Application

A comprehensive Q&A application about League of Legends built with **LangChain**, **LangGraph**, and **LangSmith**. This application uses Retrieval Augmented Generation (RAG) to answer questions about champions, abilities, game mechanics, and strategies.

## 🚀 Features

- **RAG System**: Vector-based retrieval for accurate answers from League of Legends knowledge base
- **LangGraph Workflow**: Orchestrated Q&A process with state management
- **LangSmith Integration**: Monitoring and tracing of all LLM calls
- **Streamlit UI**: Beautiful, interactive web interface
- **Deployment Ready**: Docker and cloud deployment configurations included

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key ([How to get one →](API_KEYS_SETUP.md#-getting-your-openai-api-key))
- LangSmith API key (optional but recommended) ([How to get one →](API_KEYS_SETUP.md#-getting-your-langsmith-api-key))

> 📖 **Need help getting API keys?** See the detailed [API Keys Setup Guide](API_KEYS_SETUP.md) for step-by-step instructions.

## 🛠️ Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=lolqa
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

> 📖 **Don't have API keys yet?** Follow the [API Keys Setup Guide](API_KEYS_SETUP.md) for detailed instructions on obtaining both keys.

4. **Run the application**:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 🏗️ Project Structure

```
.
├── app.py                 # Main Streamlit application
├── rag_system.py          # RAG system with vector store and retrieval
├── langgraph_workflow.py  # LangGraph workflow orchestration
├── data_collector.py      # Data collection and preparation
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── Procfile              # For cloud deployment
└── README.md             # This file
```

## 🐳 Docker Deployment

### Build the Docker image:
```bash
docker build -t lol-qa-app .
```

### Run the container:
```bash
docker run -p 8501:8501 --env-file .env lol-qa-app
```

## ☁️ Cloud Deployment

### Option 1: Streamlit Cloud (Recommended for Streamlit apps)

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add environment variables in the settings
5. Deploy!

### Option 2: Railway

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`

### Option 3: Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
5. Add environment variables
6. Deploy!

### Option 4: Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables: `heroku config:set OPENAI_API_KEY=...`
5. Deploy: `git push heroku main`

## 🔍 How It Works

> 📖 **For a detailed explanation of the architecture and how everything works together, see [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md)**

**Quick Overview**:

1. **Data Collection**: The `data_collector.py` module creates a knowledge base of League of Legends information (champions, abilities, game mechanics)

2. **RAG System**: The `rag_system.py` module:
   - Creates embeddings using OpenAI
   - Stores documents in ChromaDB vector store
   - Retrieves relevant context for questions
   - Generates answers using GPT-4

3. **LangGraph Workflow**: The `langgraph_workflow.py` module orchestrates:
   - Question extraction
   - Context retrieval
   - Answer generation
   - Response formatting

4. **LangSmith Monitoring**: All queries are automatically traced and logged to LangSmith for monitoring and debugging

5. **Streamlit UI**: The `app.py` provides an interactive interface for users to ask questions

## 📝 Example Questions

- "What are Ahri's abilities?"
- "How should I play Yasuo?"
- "What is the role of a support champion?"
- "Tell me about teamfighting in League of Legends"
- "What items should I build on Jinx?"

## 🔧 Configuration

### Adding More Data

To add more League of Legends data, modify the `create_sample_data()` method in `data_collector.py`. You can:
- Add more champions
- Include patch notes
- Add item descriptions
- Include strategy guides

### Customizing the LLM

Edit `rag_system.py` to change the model:
```python
self.llm = ChatOpenAI(
    model_name="gpt-4",  # or "gpt-3.5-turbo"
    temperature=0.7,
)
```

### Adjusting Retrieval

Modify the retriever settings in `rag_system.py`:
```python
self.retriever = self.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Retrieve more/fewer documents
)
```

## 🐛 Troubleshooting

### Vector Store Issues
If you encounter issues with the vector store, delete the `chroma_db` directory and restart the application to recreate it.

### API Key Errors
Ensure your `.env` file is properly configured and contains valid API keys.

### Port Already in Use
If port 8501 is in use, specify a different port:
```bash
streamlit run app.py --server.port=8502
```

## 📚 Technologies Used

- **LangChain 1.1.3**: RAG framework and LLM integration
- **LangGraph 0.3.31**: Workflow orchestration
- **LangSmith 0.3.32**: Monitoring and observability
- **OpenAI**: Embeddings and LLM
- **ChromaDB**: Vector database
- **Streamlit**: Web interface
- **Docker**: Containerization

### Version Information

This project uses the latest stable versions of LangChain ecosystem:
- `langchain==1.1.3` - Core LangChain library
- `langchain-openai==0.2.9` - OpenAI integrations
- `langchain-community==0.3.7` - Community integrations
- `langgraph==0.3.31` - Graph-based workflow orchestration
- `langsmith==0.3.32` - Monitoring and observability

## 📄 License

This project is for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📧 Support

For questions or issues, please open an issue on the repository.

---

Made with ⚔️ for League of Legends fans!


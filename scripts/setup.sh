#!/bin/bash

# Setup script for League of Legends Q&A Application

echo "⚔️  Setting up League of Legends Q&A Application..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "⚠️  Warning: Python 3.11+ is recommended. Current version: $python_version"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# OpenAI API Key (required for embeddings and LLM)
OPENAI_API_KEY=your_openai_api_key_here

# LangSmith API Key (optional but recommended for monitoring)
LANGSMITH_API_KEY=your_langsmith_api_key_here

# LangSmith Project Name (optional)
LANGSMITH_PROJECT=lolqa

# LangSmith Endpoint (optional, defaults to https://api.smith.langchain.com)
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
EOF
    echo "✅ Created .env file. Please update it with your API keys."
else
    echo "✅ .env file already exists."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data chroma_db

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update the .env file with your API keys"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the application: streamlit run app.py"
echo ""


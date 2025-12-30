#!/bin/bash

# Setup script for League of Legends Q&A Application (Microservices)

echo "⚔️  Setting up League of Legends Q&A Application (Microservices)..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Get Docker: https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi

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

# LLM Configuration
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_BACKEND=openai

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# PostgreSQL Configuration
POSTGRES_URL=postgresql://lolqa:lolqa_password@postgres:5432/lolqa
POSTGRES_PASSWORD=lolqa_password

# JWT Secret Key (generate a secure random string)
JWT_SECRET_KEY=your-secret-key-here-change-this-in-production
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
echo "1. Update the .env file with your API keys (especially OPENAI_API_KEY)"
echo "2. Start all services: docker-compose up --build"
echo "3. Ingest data (first time): curl -X POST http://localhost:8003/ingest"
echo "4. Access the application: http://localhost:8501"
echo ""
echo "For more details, see: docs/QUICKSTART.md"
echo ""


#!/bin/bash

echo "🚀 Upgrading Python and Setting Up LangChain 1.1.3"
echo ""

# Step 1: Install Python 3.11
echo "📦 Step 1: Installing Python 3.11 via Homebrew..."
brew install python@3.11

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python 3.11. Please check Homebrew installation."
    exit 1
fi

echo "✅ Python 3.11 installed successfully"
echo ""

# Step 2: Remove old virtual environment
echo "🗑️  Step 2: Removing old virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✅ Old venv removed"
else
    echo "ℹ️  No existing venv found"
fi
echo ""

# Step 3: Create new virtual environment with Python 3.11
echo "🔧 Step 3: Creating new virtual environment with Python 3.11..."
python3.11 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment. Make sure Python 3.11 is installed."
    exit 1
fi

echo "✅ Virtual environment created"
echo ""

# Step 4: Activate and upgrade pip
echo "⬆️  Step 4: Activating venv and upgrading pip..."
source venv/bin/activate
pip install --upgrade pip

echo "✅ pip upgraded"
echo ""

# Step 5: Install requirements
echo "📥 Step 5: Installing LangChain 1.1.3 and dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Installation complete!"
    echo ""
    echo "🔍 Verifying installation..."
    python -c "import langchain; print('LangChain version:', langchain.__version__)"
    python -c "import langgraph; print('LangGraph version:', langgraph.__version__)"
    python -c "import langsmith; print('LangSmith version:', langsmith.__version__)"
    echo ""
    echo "🎉 Success! You can now run: streamlit run app.py"
else
    echo ""
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi


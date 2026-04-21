#!/bin/bash
# Setup script for Legal RAG System

set -e  # Exit on error

echo "=================================="
echo "Legal RAG System - Setup Script"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "legalRAG" ]; then
    echo "❌ Error: legalRAG virtual environment not found"
    echo "Please create it first with: python3 -m venv legalRAG"
    exit 1
fi

echo "✓ Found legalRAG virtual environment"
echo ""

# Activate virtual environment
echo "📦 Activating virtual environment..."
source legalRAG/bin/activate

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
echo "This may take 2-3 minutes..."
echo ""
pip install -r backend/requirements.txt

echo ""
echo "=================================="
echo "✅ Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Create .env file with your API keys:"
echo "   cd backend"
echo "   cp .env.example .env"
echo "   # Edit .env and add your OPENAI_API_KEY"
echo ""
echo "2. Test the system:"
echo "   python backend/test_graph.py"
echo ""
echo "3. Read GETTING_STARTED.md for detailed instructions"
echo ""
echo "Your virtual environment (legalRAG) is now active!"
echo "You should see (legalRAG) in your prompt."
echo ""

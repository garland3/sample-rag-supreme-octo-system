#!/bin/bash

# RAG System Startup Script
# This script sets up and runs the RAG research system

set -e  # Exit on any error

echo "🚀 Starting RAG Research System..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "📝 Please copy .env.example to .env and configure your API keys:"
    echo "   cp .env.example .env"
    echo "   # Then edit .env with your actual API keys"
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed!"
    echo "📝 Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   # or: pip install uv"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies with uv
echo "📚 Installing dependencies with uv..."
uv pip install -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Check required environment variables
echo "🔍 Checking environment configuration..."
python3 -c "
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = ['TAVILY_API_KEY', 'LLM_BASE_URL', 'LLM_API_KEY', 'LLM_MODEL']
missing_vars = []

for var in required_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f'❌ Missing required environment variables: {missing_vars}')
    print('📝 Please check your .env file and ensure all required variables are set.')
    exit(1)
else:
    print('✅ Environment configuration OK')
"

if [ $? -ne 0 ]; then
    echo "❌ Environment check failed. Please fix configuration and try again."
    exit 1
fi

# Start the application
echo "🌐 Starting FastAPI server..."
echo "📱 Access the application at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

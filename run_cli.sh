#!/bin/bash
# Simple wrapper script to run the RAG CLI with virtual environment activated

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment and run CLI
source .venv/bin/activate && python main_cli.py "$@"

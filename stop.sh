#!/bin/bash

# Stop script for RAG System
# This script kills any running Python processes for the RAG system

echo "🛑 Stopping RAG Research System..."

# Find and kill uvicorn/FastAPI processes
echo "🔍 Looking for running FastAPI processes..."

# Kill by process name
pkill -f "uvicorn main:app" 2>/dev/null && echo "✅ Stopped uvicorn server" || echo "ℹ️  No uvicorn process found"

# Kill by port (backup method)
lsof -ti:8000 2>/dev/null | xargs kill -9 2>/dev/null && echo "✅ Killed processes on port 8000" || echo "ℹ️  No processes on port 8000"

# Kill any remaining Python processes related to main.py
pkill -f "python.*main.py" 2>/dev/null && echo "✅ Stopped main.py processes" || echo "ℹ️  No main.py processes found"

echo "🏁 RAG system stopped"

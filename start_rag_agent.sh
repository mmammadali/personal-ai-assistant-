#!/bin/bash
# 🔥 RAG Agent Startup Script for Mac/Linux
# Starts the web UI for RAG Agent

echo "===================================================="
echo "   🔥 RAG AGENT - Starting Web Interface"
echo "===================================================="
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  No virtual environment found"
    echo "   Running with system Python..."
fi

echo ""
echo "✅ Starting RAG Agent Web UI..."
echo "   URL: http://127.0.0.1:5001"
echo ""
echo "📌 Press Ctrl+C to stop the server"
echo "===================================================="
echo ""

python rag_web_ui.py


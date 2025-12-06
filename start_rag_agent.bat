@echo off
REM 🔥 RAG Agent Startup Script for Windows
REM Starts the web UI for RAG Agent

echo ====================================================
echo    🔥 RAG AGENT - Starting Web Interface
echo ====================================================
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found
    echo    Running with system Python...
)

echo.
echo ✅ Starting RAG Agent Web UI...
echo    URL: http://127.0.0.1:5001
echo.
echo 📌 Press Ctrl+C to stop the server
echo ====================================================
echo.

python rag_web_ui.py

pause


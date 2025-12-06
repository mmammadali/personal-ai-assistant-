@echo off
echo ========================================
echo   Installing ChromaDB Dependencies
echo ========================================
echo.
echo This script will install ChromaDB and all its dependencies.
echo This may take 5-10 minutes...
echo.
pause

echo Installing ChromaDB dependencies...
python -m pip install --upgrade pip

echo Step 1/3: Installing core dependencies...
python -m pip install overrides fastapi uvicorn pydantic-settings

echo Step 2/3: Installing chromadb dependencies...
python -m pip install grpcio importlib-resources mmh3 posthog pypika rich tokenizers typer

echo Step 3/3: Installing OpenTelemetry packages...
python -m pip install opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk opentelemetry-instrumentation-fastapi

echo.
echo ========================================
echo   Testing ChromaDB Installation
echo ========================================
python -c "import chromadb; print('SUCCESS: ChromaDB version:', chromadb.__version__)"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   ChromaDB installed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Installation incomplete. 
    echo   Some dependencies may still be missing.
    echo ========================================
)

echo.
echo Note: onnxruntime and kubernetes are optional and may not be available for Python 3.14
echo The RAG agent should still work without them.
echo.
pause





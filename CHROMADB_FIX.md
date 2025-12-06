# ChromaDB Installation Fix for Python 3.14

## Problem

Python 3.14 is very new (released recently) and many packages don't have pre-built wheels for it yet, including:
- `onnxruntime` - not available for Python 3.14
- `chroma-hnswlib` - requires C++ compiler to build from source

## Solution

I've created a workaround installation process:

### Option 1: Automated Installation (Recommended)

Run the installation script:

```bash
install_chromadb.bat
```

This will install ChromaDB 0.6.3 (which works without onnxruntime for basic functionality) and all required dependencies.

### Option 2: Manual Installation

Install dependencies in order:

```bash
# Step 1: Core dependencies
python -m pip install overrides fastapi uvicorn pydantic-settings

# Step 2: ChromaDB dependencies  
python -m pip install grpcio importlib-resources mmh3 posthog pypika rich tokenizers typer

# Step 3: OpenTelemetry (for monitoring)
python -m pip install opentelemetry-api opentelemetry-exporter-otlp-proto-grpc opentelemetry-sdk opentelemetry-instrumentation-fastapi
```

### Option 3: Use Python 3.11 or 3.12

For full compatibility with all packages, consider using Python 3.11 or 3.12:

1. Install Python 3.11/3.12
2. Create a virtual environment
3. Install all requirements normally

```bash
# With Python 3.11/3.12
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Current Status

ChromaDB 0.6.3 is currently installed but missing some dependencies.

### What's Installed:
✅ chromadb==0.6.3
✅ overrides
✅ fastapi
✅ uvicorn
✅ pydantic-settings

### What's Missing:
❌ grpcio
❌ mmh3
❌ posthog
❌ pypika
❌ rich
❌ tokenizers
❌ typer
❌ opentelemetry packages
❌ onnxruntime (optional - not available for Python 3.14)

## Testing

After installation, test with:

```bash
python -c "import chromadb; print('ChromaDB version:', chromadb.__version__)"
```

Then start the server and test RAG agent:

```bash
python app.py
```

Open http://127.0.0.1:5000/rag and try:
1. Upload a document
2. Ask questions
3. Get summaries

## Alternative: Use Simpler Vector Store

If ChromaDB continues to have issues, you can switch to FAISS (simpler, no compilation required):

```bash
pip install faiss-cpu
```

Then update `config.py`:
```python
RAG_VECTOR_STORE_TYPE = "faiss"
```

## Next Steps

1. Run `install_chromadb.bat` to complete installation
2. Test ChromaDB import
3. Start the web server
4. Test RAG agent functionality

---

**Note:** The RAG agent is designed to work with or without ChromaDB. The web interface will show an appropriate message if the vector store is not available.





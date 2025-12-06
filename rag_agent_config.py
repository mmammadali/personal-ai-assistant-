"""
🔥 RAG Agent Configuration
Production-grade configuration for multilingual document RAG system
Supports ChromaDB (local) and Pinecone (cloud) backends
"""
import os
from pathlib import Path
from typing import Literal
from dotenv import load_dotenv

# Load environment variables
project_root = Path(__file__).parent
env_path = project_root / '.env'
if env_path.exists():
    load_dotenv(env_path)

# ==================== VECTOR DATABASE CONFIGURATION ====================

# Choose vector database backend: "chromadb" or "pinecone"
VECTOR_DB_TYPE: Literal["chromadb", "pinecone"] = os.getenv("VECTOR_DB_TYPE", "chromadb")

# ChromaDB Configuration (Local Development)
CHROMADB_PERSIST_DIR = os.getenv("CHROMADB_PERSIST_DIR", "./chroma_db")
CHROMADB_COLLECTION_NAME = os.getenv("CHROMADB_COLLECTION_NAME", "documents")

# Pinecone Configuration (Production/Cloud)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", None)
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "gcp-starter")  # or "us-east-1-aws"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-documents")

# ==================== LLM CONFIGURATION ====================

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "❌ OPENAI_API_KEY not found in environment variables!\n"
        "Please add it to your .env file: OPENAI_API_KEY=sk-..."
    )

# Model Selection
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")  # gpt-4, gpt-4-turbo, gpt-3.5-turbo
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")  # or text-embedding-3-small

# Model Parameters
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))  # Lower = more deterministic
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# ==================== DOCUMENT PROCESSING CONFIGURATION ====================

# Document Storage
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploaded_documents"))
UPLOAD_DIR.mkdir(exist_ok=True)

# Supported File Formats
SUPPORTED_FORMATS = {
    ".pdf": "PDF Document",
    ".docx": "Word Document",
    ".doc": "Word Document (Legacy)",
    ".txt": "Text File",
    ".md": "Markdown File",
    ".csv": "CSV File",
    ".xlsx": "Excel Spreadsheet",
    ".xls": "Excel Spreadsheet (Legacy)",
    ".pptx": "PowerPoint Presentation",
    ".html": "HTML Document",
    ".json": "JSON File",
}

# Text Chunking Strategy
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))  # Characters per chunk
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))  # Overlap between chunks
CHUNK_SEPARATOR = os.getenv("CHUNK_SEPARATOR", "\n\n")  # Split on paragraphs

# ==================== RAG CONFIGURATION ====================

# Retrieval Parameters
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "4"))  # Number of chunks to retrieve
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))  # Minimum similarity score

# Summary Configuration
SUMMARY_MAX_LENGTH = int(os.getenv("SUMMARY_MAX_LENGTH", "1500"))  # Max summary length in words
EXTRACT_METADATA = True  # Extract dates, financial data, etc.

# ==================== LANGUAGE CONFIGURATION ====================

# Primary language for responses
PRIMARY_LANGUAGE = "farsi"  # All responses in Farsi
DETECT_INPUT_LANGUAGE = True  # Auto-detect input language (Farsi/English)

# Farsi Language Prompts
FARSI_SYSTEM_PROMPT = """
شما یک دستیار هوشمند برای تحلیل اسناد هستید.
وظیفه شما پاسخ دادن به سؤالات کاربر درباره اسناد به زبان فارسی روان و قابل فهم است.
همیشه پاسخ‌های دقیق، مفید و با ساختار مناسب ارائه دهید.
"""

FARSI_SUMMARY_PROMPT = """
یک خلاصه جامع و حرفه‌ای از این سند به زبان فارسی ایجاد کنید.

**موارد مهم که باید استخراج شوند:**
1. 📅 تاریخ‌ها و ضرب‌الاجل‌ها
2. 💰 اطلاعات مالی (مبالغ، هزینه‌ها، درآمدها)
3. 📋 دستورالعمل‌ها و راهنماها
4. ⚠️ اطلاعات حساس و مهم
5. 👥 اسامی افراد و سازمان‌ها
6. 🎯 نکات کلیدی و اصلی

خلاصه باید:
- روان و قابل فهم باشد
- ساختار منظم داشته باشد
- حداکثر {max_length} کلمه باشد
- شامل تمام نکات مهم و کلیدی باشد
"""

# ==================== WEB UI CONFIGURATION ====================

FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5001"))  # Changed from 5000 to avoid conflict
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# ==================== VALIDATION ====================

def validate_config():
    """Validate configuration and warn about missing optional settings"""
    errors = []
    warnings = []
    
    # Check critical settings
    if not OPENAI_API_KEY:
        errors.append("❌ OPENAI_API_KEY is required")
    
    if VECTOR_DB_TYPE == "pinecone" and not PINECONE_API_KEY:
        errors.append("❌ PINECONE_API_KEY required when VECTOR_DB_TYPE='pinecone'")
    
    # Check warnings
    if VECTOR_DB_TYPE == "chromadb":
        warnings.append("ℹ️  Using ChromaDB (local) - switch to Pinecone for production")
    
    if LLM_MODEL == "gpt-3.5-turbo":
        warnings.append("⚠️  Using GPT-3.5 - GPT-4 recommended for better Farsi support")
    
    # Print results
    if errors:
        print("\n" + "="*60)
        print("❌ CONFIGURATION ERRORS:")
        for error in errors:
            print(f"  {error}")
        print("="*60 + "\n")
        raise ValueError("Configuration validation failed")
    
    if warnings:
        print("\n" + "="*60)
        print("⚠️  CONFIGURATION WARNINGS:")
        for warning in warnings:
            print(f"  {warning}")
        print("="*60 + "\n")
    
    # Success message
    print("✅ Configuration validated successfully!")
    print(f"   Vector DB: {VECTOR_DB_TYPE}")
    print(f"   LLM Model: {LLM_MODEL}")
    print(f"   Embedding Model: {EMBEDDING_MODEL}")
    print(f"   Upload Directory: {UPLOAD_DIR}")
    print(f"   Primary Language: {PRIMARY_LANGUAGE}")

# Run validation on import
if __name__ != "__main__":
    validate_config()

# ==================== HELPER FUNCTIONS ====================

def get_vector_db_config():
    """Get active vector database configuration"""
    if VECTOR_DB_TYPE == "chromadb":
        return {
            "type": "chromadb",
            "persist_dir": CHROMADB_PERSIST_DIR,
            "collection_name": CHROMADB_COLLECTION_NAME
        }
    elif VECTOR_DB_TYPE == "pinecone":
        return {
            "type": "pinecone",
            "api_key": PINECONE_API_KEY,
            "environment": PINECONE_ENVIRONMENT,
            "index_name": PINECONE_INDEX_NAME
        }
    else:
        raise ValueError(f"Unknown VECTOR_DB_TYPE: {VECTOR_DB_TYPE}")

def get_embedding_config():
    """Get embedding model configuration"""
    return {
        "model": EMBEDDING_MODEL,
        "api_key": OPENAI_API_KEY
    }

def get_llm_config():
    """Get LLM configuration"""
    return {
        "model": LLM_MODEL,
        "api_key": OPENAI_API_KEY,
        "temperature": LLM_TEMPERATURE,
        "max_tokens": LLM_MAX_TOKENS
    }


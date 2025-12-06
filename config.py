"""
Configuration file for Iranian Manager Personal Assistant
Centralized configuration management
"""
import os
import sys
from pathlib import Path

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    
    # Get the project root directory
    project_root = Path(__file__).parent
    env_path = project_root / '.env'
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded configuration from .env file")
    else:
        print(f"ℹ️  No .env file found, using default configuration")
except ImportError:
    print("ℹ️  python-dotenv not installed, using environment variables only")
except Exception as e:
    print(f"⚠️  Error loading .env: {e}")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable is not set. "
        "Please set it in your .env file or environment variables."
    )

# Model Configuration
DEFAULT_MODEL = "gpt-4"  # Using gpt-4o-mini (gpt-5-mini doesn't exist yet)
EMBEDDING_MODEL = "text-embedding-3-large"  # OpenAI embeddings for better quality

# Flask Configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database Configuration
DATABASE_PATH = "assistant.db"

# Vector Database Configuration
# Choose: "chromadb" (local, free) or "pinecone" (cloud, multi-user)
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chromadb")

# ChromaDB Configuration (Local Development)
CHROMA_PERSIST_DIR = "./chroma_db"
CHROMA_COLLECTION_NAME = "documents"

# Pinecone Configuration (Production/Cloud)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "rag-documents")

# RAG Configuration
CHUNK_SIZE = 1000  # Size of text chunks for embedding
CHUNK_OVERLAP = 200  # Overlap between chunks
RETRIEVAL_TOP_K = 4  # Number of relevant chunks to retrieve
MAX_FILE_SIZE_MB = 50  # Maximum file size for upload

# Supported Document Formats
SUPPORTED_FORMATS = [
    ".pdf", ".docx", ".doc", ".txt", ".md", 
    ".pptx", ".ppt", ".xlsx", ".xls", ".csv",
    ".html", ".xml", ".json", ".rtf"
]

# Application Settings
APP_NAME = "Iranian Manager Personal Assistant"
APP_VERSION = "1.0.0"

# RAG Agent Configuration
RAG_VECTOR_STORE_TYPE = "faiss"  # Options: "chromadb", "faiss", or "pinecone"
RAG_CHROMA_PERSIST_DIR = "./chroma_db"
RAG_FAISS_PERSIST_DIR = "./faiss_db"  # FAISS storage directory
RAG_COLLECTION_NAME = "rag_documents"
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_MODEL = "gpt-4o"  # Model for RAG agent

# Pinecone Configuration (if using Pinecone)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", None)
PINECONE_INDEX_NAME = "rag-documents"
PINECONE_NAMESPACE = "default"

# Upload Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.pptx', '.ppt', '.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE_MB = 50

# ==================== FINANCE ASSISTANT CONFIGURATION ====================

# Finance Database
FINANCE_DB_PATH = "finance.db"
FINANCE_MODEL = "gpt-4o"  # Separate model for finance operations

# Finance Upload & Storage
FINANCE_UPLOAD_FOLDER = "finance_uploads"
FINANCE_REPORTS_FOLDER = "finance_reports"
FINANCE_DOCUMENTS_FOLDER = "finance_documents"

# OCR Configuration
# Auto-detect Tesseract path if not in PATH
_tesseract_default = "tesseract"
if sys.platform == 'win32':
    _common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in _common_paths:
        if os.path.exists(path):
            _tesseract_default = path
            break

TESSERACT_PATH = os.getenv("TESSERACT_PATH", _tesseract_default)
TESSERACT_LANG = "fas+eng"  # Persian + English
PADDLEOCR_ENABLED = True
PADDLEOCR_LANG = "persian"

# Exchange Rate Configuration
EXCHANGE_RATE_SOURCES = ["bonbast", "tgju", "cbi"]
EXCHANGE_RATE_CACHE_TTL = 3600  # 1 hour in seconds
EXCHANGE_RATE_UPDATE_INTERVAL = 3600  # Update every hour

# Vector DB for Transaction Categorization Learning
FINANCE_VECTOR_COLLECTION = "finance_transaction_patterns"

# Persian Fonts for PDF Export
PERSIAN_FONT_PATH = "./fonts/Vazir.ttf"
PERSIAN_FONT_FALLBACK = "./fonts/Sahel.ttf"

# Financial Calculations
DEFAULT_CURRENCY = "IRR"
SUPPORTED_CURRENCIES = ["IRR", "USD", "EUR", "GBP", "AED"]
TAX_RATE_VAT = 0.09  # Iranian VAT rate (9%)

# Categorization
CATEGORIZATION_CONFIDENCE_THRESHOLD = 0.7
VENDOR_FUZZY_MATCH_THRESHOLD = 0.85

# Cash Flow Projections
CASH_FLOW_FORECAST_DAYS = 90  # Default forecast period
BURN_RATE_CALCULATION_DAYS = 30  # Calculate burn rate over 30 days

# Reports
REPORT_DEFAULT_FORMAT = "pdf"
REPORT_JALALI_CALENDAR = True
REPORT_INCLUDE_CHARTS = True


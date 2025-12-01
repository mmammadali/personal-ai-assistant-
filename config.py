"""
Configuration file for Iranian Manager Personal Assistant
Centralized configuration management
"""
import os
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
DEFAULT_MODEL = "gpt-5-mini"  # Using gpt-5-mini - latest and most efficient

# Flask Configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database Configuration
DATABASE_PATH = "assistant.db"

# Application Settings
APP_NAME = "Iranian Manager Personal Assistant"
APP_VERSION = "1.0.0"


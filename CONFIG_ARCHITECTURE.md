# Configuration Architecture

## 🏗️ Overview

The Iranian Manager Personal Assistant now uses a **centralized configuration system** that makes the OpenAI API key available throughout the entire project.

---

## 📊 Configuration Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Configuration Sources                     │
│                                                              │
│  1️⃣ Environment Variables (Highest Priority)                │
│     └─ $env:OPENAI_API_KEY (Windows)                        │
│     └─ export OPENAI_API_KEY=... (Linux/Mac)                │
│                                                              │
│  2️⃣ .env File (Medium Priority)                             │
│     └─ Project Root/.env                                    │
│     └─ Loaded by python-dotenv                              │
│                                                              │
│  3️⃣ config.py Default (Fallback)                            │
│     └─ Hard-coded API key                                   │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │      config.py          │
         │  Central Configuration  │
         │                         │
         │  - OPENAI_API_KEY       │
         │  - DEFAULT_MODEL        │
         │  - FLASK_HOST           │
         │  - FLASK_PORT           │
         │  - FLASK_DEBUG          │
         │  - DATABASE_PATH        │
         └────────────┬────────────┘
                      │
                      │ Imported by all modules
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌───────────────┐
│    app.py     │          │   agent.py    │
│               │          │               │
│ Imports:      │          │ Uses API key  │
│ - OPENAI_API  │          │ for OpenAI    │
│ - DEFAULT_MOD │          │ chat models   │
│ - FLASK_*     │          │               │
└───────────────┘          └───────────────┘
        │                           │
        └─────────────┬─────────────┘
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
┌───────────────┐          ┌───────────────┐
│example_usage  │          │demo_web_inter │
│               │          │               │
│ Imports config│          │ Imports config│
│ Uses same key │          │ Uses same key │
└───────────────┘          └───────────────┘
```

---

## 🔄 How It Works

### 1. Centralized Configuration (`config.py`)

```python
"""
config.py - Single source of truth for all configuration
"""
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Configuration available to ALL modules
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default-key")
DEFAULT_MODEL = "gpt-5-mini"
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
```

### 2. All Modules Import from config.py

**app.py:**
```python
from config import OPENAI_API_KEY, DEFAULT_MODEL

assistant = IranianManagerAssistant(
    openai_api_key=OPENAI_API_KEY,
    model=DEFAULT_MODEL
)
```

**example_usage.py:**
```python
from config import OPENAI_API_KEY

assistant = IranianManagerAssistant(
    openai_api_key=OPENAI_API_KEY
)
```

---

## ✅ Benefits

| Benefit | Description |
|---------|-------------|
| **🔄 Consistency** | Same API key used everywhere |
| **🔧 Easy Updates** | Change in one place (config.py) |
| **🔐 Security** | Support for .env files (gitignored) |
| **📦 Flexibility** | Multiple configuration methods |
| **🚀 Simple** | No need to set env vars manually |

---

## 📁 File Structure

```
ai agent/
├── config.py                 ← Central configuration (NEW)
├── .env                      ← Optional environment file (gitignored)
├── setup_env.py             ← Helper to create .env file (NEW)
├── ENV_SETUP.md             ← Configuration guide (NEW)
├── CONFIG_ARCHITECTURE.md   ← This file (NEW)
│
├── app.py                   ← Updated to use config
├── agent.py                 ← Uses config via app.py
├── example_usage.py         ← Can import from config
├── demo_web_interface.py    ← Can import from config
│
├── requirements.txt         ← Updated with python-dotenv
├── start_web_ui.bat        ← Works automatically
└── start_web_ui.sh         ← Works automatically
```

---

## 🎯 Current Status

### ✅ Configured Files

| File | Status | Uses config.py |
|------|--------|----------------|
| `config.py` | ✅ Created | Central source |
| `app.py` | ✅ Updated | Yes |
| `requirements.txt` | ✅ Updated | python-dotenv added |
| `setup_env.py` | ✅ Created | Helper script |
| `ENV_SETUP.md` | ✅ Created | Documentation |

### 🔑 API Key Status

- ✅ **Configured in config.py**
- ✅ **Available to all modules**
- ✅ **Can be overridden by .env**
- ✅ **Can be overridden by environment variables**

---

## 🚀 Quick Start Commands

```bash
# 1. Install dependencies (includes python-dotenv)
pip install -r requirements.txt

# 2. (Optional) Create .env file
python setup_env.py

# 3. Run the application
python app.py

# OR use startup scripts
start_web_ui.bat     # Windows
./start_web_ui.sh    # Linux/Mac
```

---

## 🔍 Verification

Check if configuration is working:

```bash
# Test 1: Check if config.py loads
python -c "import config; print(f'Model: {config.DEFAULT_MODEL}')"

# Test 2: Check if API key is set
python -c "from config import OPENAI_API_KEY; print('✅' if OPENAI_API_KEY else '❌')"

# Test 3: Run the app
python app.py
```

Expected output on startup:
```
✅ Loaded configuration from .env file
🌐 Server starting at: http://127.0.0.1:5000
🤖 AI Model: gpt-5-mini
```

---

## 📝 Summary

Your OpenAI API key is now:
- ✅ Stored in `config.py` (with default value)
- ✅ Can be customized via `.env` file
- ✅ Can be overridden by environment variables
- ✅ Automatically loaded by all Python files
- ✅ Centrally managed in one location

**No more manual environment variable setup required!** 🎉


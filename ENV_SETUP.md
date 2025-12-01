# Environment Configuration Guide

This guide explains how to configure the OpenAI API key and other environment variables for the Iranian Manager Personal Assistant.

## 🔧 Configuration Methods

The application supports multiple ways to configure the OpenAI API key:

### Method 1: Using .env File (Recommended)

1. **Run the setup script:**
   ```bash
   python setup_env.py
   ```

2. **Or manually create a `.env` file** in the project root:
   ```bash
   # .env file
   OPENAI_API_KEY=your-openai-api-key-here
   DEFAULT_MODEL=gpt-5-mini
   FLASK_HOST=127.0.0.1
   FLASK_PORT=5000
   FLASK_DEBUG=True
   ```

### Method 2: Using Environment Variables

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-openai-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your-openai-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Method 3: Using config.py (Default Fallback)

The `config.py` file has a default API key configured. This is used as a fallback if no environment variable or .env file is found.

---

## 📋 Configuration File Structure

### `config.py` - Central Configuration

All configuration is centralized in `config.py`:

```python
# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "default-key")

# Model Configuration
DEFAULT_MODEL = "gpt-5-mini"

# Flask Configuration
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Database Configuration
DATABASE_PATH = "assistant.db"
```

---

## 🔐 Your Current API Key

Your OpenAI API key should be configured in `config.py` or `.env` file:

```
OPENAI_API_KEY=your-api-key-here
```

**Important**: Replace `your-api-key-here` with your actual OpenAI API key.

This key will be used by:
- ✅ `app.py` - Web application
- ✅ `agent.py` - AI agent
- ✅ `example_usage.py` - Example scripts
- ✅ `demo_web_interface.py` - Demo interface
- ✅ All other Python files in the project

---

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **(Optional) Create .env file:**
   ```bash
   python setup_env.py
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

The application will automatically:
- ✅ Load .env file if it exists
- ✅ Use environment variables if set
- ✅ Fall back to config.py defaults

---

## ⚙️ Available Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Pre-configured |
| `DEFAULT_MODEL` | AI model to use | `gpt-5-mini` |
| `FLASK_HOST` | Server host address | `127.0.0.1` |
| `FLASK_PORT` | Server port number | `5000` |
| `FLASK_DEBUG` | Enable debug mode | `True` |
| `DATABASE_PATH` | SQLite database path | `assistant.db` |

---

## 🔍 Verifying Configuration

To check if your API key is configured correctly:

```bash
python -c "from config import OPENAI_API_KEY; print('✅ API Key configured!' if OPENAI_API_KEY else '❌ API Key missing!')"
```

---

## 📝 Priority Order

The configuration is loaded in this priority order:

1. **Environment variables** (highest priority)
2. **.env file**
3. **config.py defaults** (fallback)

---

## 🛡️ Security Best Practices

- ✅ `.env` files are automatically ignored by git
- ✅ Never commit API keys to version control
- ✅ Use environment variables in production
- ✅ Rotate API keys periodically
- ✅ Keep API keys confidential

---

## 🎯 Next Steps

Your API key is now configured and available throughout the project! You can:

1. Run `python app.py` to start the web interface
2. Test with `python example_usage.py`
3. Modify configuration in `config.py` as needed

For questions or issues, refer to the main README.md file.


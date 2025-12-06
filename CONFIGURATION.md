# Configuration Guide

## Environment Variables

The application can be configured using environment variables. You can set these in your system or create a `.env` file (requires `python-dotenv`).

### Required Configuration

#### OpenAI API Key
```bash
# Windows (Command Prompt)
set OPENAI_API_KEY=your-api-key-here

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

### Optional Configuration

#### Flask Settings
```bash
# Development mode (enables debug logging and auto-reload)
set FLASK_ENV=development
set FLASK_DEBUG=True

# Production mode
set FLASK_ENV=production
set FLASK_DEBUG=False
```

#### Custom Port
Edit `app.py` to change the port:
```python
app.run(debug=True, host='127.0.0.1', port=5001)  # Change 5000 to your desired port
```

#### Custom Database Path
Edit the database import in your files:
```python
from database import DatabaseManager

db = DatabaseManager(db_path="custom_path.db")
```

## Creating a .env File (Optional)

If you want to use a `.env` file:

1. Install python-dotenv:
```bash
pip install python-dotenv
```

2. Create a file named `.env` in the project root:
```
OPENAI_API_KEY=your-api-key-here
FLASK_ENV=development
FLASK_DEBUG=True
```

3. Load it in your Python code:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Model Selection

You can change the OpenAI model used by the agent:

### In Web Interface (app.py):
```python
assistant = IranianManagerAssistant(
    openai_api_key=api_key,
    model="gpt-4-turbo-preview"  # Options: gpt-4o-mini, gpt-4-turbo-preview, gpt-4, gpt-3.5-turbo
)
```

### Model Recommendations:
- **gpt-4o-mini**: Fast, cost-effective (default)
- **gpt-4-turbo-preview**: Better reasoning, more expensive
- **gpt-4**: Most capable, highest cost
- **gpt-3.5-turbo**: Fastest, lowest cost (may struggle with complex queries)

## Security Best Practices

### For Development:
- Use environment variables for API keys
- Keep `.env` files out of version control (add to `.gitignore`)
- Use `FLASK_DEBUG=True` for detailed error messages

### For Production:
1. **Never expose your API key in code**
2. **Use HTTPS** with a reverse proxy (nginx, Apache)
3. **Set strong Flask secret key**:
   ```python
   app.secret_key = os.urandom(32)  # Generate securely
   ```
4. **Disable Flask debug mode**:
   ```python
   app.run(debug=False)
   ```
5. **Use a production WSGI server** (Gunicorn, uWSGI):
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 app:app
   ```
6. **Implement rate limiting**:
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
   ```
7. **Add authentication** if needed (Flask-Login, JWT)

## Database Configuration

### SQLite (Default)
- File-based, lightweight
- Perfect for development and small-scale use
- Database file: `assistant.db` (created automatically)

### PostgreSQL (Production)
For high-traffic production use:

1. Install psycopg2:
```bash
pip install psycopg2-binary
```

2. Update `database.py` to use PostgreSQL:
```python
import psycopg2

class DatabaseManager:
    def __init__(self, db_url="postgresql://user:password@localhost/dbname"):
        self.conn = psycopg2.connect(db_url)
        # ... rest of implementation
```

## Customization

### UI Theme Colors
Edit `static/css/style.css`:
```css
:root {
    --accent-primary: #10a37f;  /* Change to your brand color */
    --accent-secondary: #1a7f64;
    /* ... more color variables */
}
```

### Chat Input Placeholder
Edit `templates/chat.html`:
```html
<textarea 
    id="messageInput" 
    placeholder="Your custom placeholder text..."
></textarea>
```

### Quick Action Buttons
Add/modify in `templates/chat.html`:
```html
<button class="action-card" data-prompt="Your custom prompt">
    <i class="fas fa-icon-name"></i>
    <span>Button Label</span>
</button>
```

## Troubleshooting

### API Key Issues
```bash
# Verify your key is set
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Linux/Mac
```

### Port Already in Use
```bash
# Find process using port 5000 (Windows)
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <process_id> /F

# Or use a different port in app.py
```

### Database Locked
```bash
# Close all connections and delete the database
rm assistant.db  # Linux/Mac
del assistant.db  # Windows

# Restart the application
```

### Import Errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## Monitoring and Logging

### Enable Detailed Logging
Add to `app.py`:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Use in your code
logger.info("User message received")
logger.error("Error occurred: %s", str(e))
```

### Monitor Performance
```python
import time

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        logger.info(f"Request took {elapsed:.2f}s")
    return response
```

## Backup and Recovery

### Database Backup
```bash
# Backup SQLite database
cp assistant.db assistant_backup_$(date +%Y%m%d).db

# Restore from backup
cp assistant_backup_20231215.db assistant.db
```

### Conversation Export
Add to `app.py`:
```python
@app.route('/api/export', methods=['GET'])
def export_conversations():
    # Export logic here
    pass
```

## Support

For additional configuration help:
- Check the main README.md
- Review WEB_UI_GUIDE.md
- Examine the code comments in app.py, agent.py, tools.py









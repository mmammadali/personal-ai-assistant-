# 🤖 Iranian Manager Personal Assistant

A production-grade LangGraph-powered AI agent designed specifically for Iranian managers to manage calendar events and daily tasks with **Jalali (Persian) calendar support**, **human-in-the-loop confirmation**, and **conversational memory**.

---

## 🔥 FEATURES

### ✅ Event Management
- **Create Events**: Schedule meetings and events with date, title, attendee, description, and location
- **Retrieve Events**: Query events by date, title, or attendee (supports partial matching and combined filters)

### ✅ Task Management
- **Create Tasks**: Add tasks with due date, description, project, status, and attendant
- **Retrieve Tasks**: Search tasks by due date, project, status, description, or attendant
- **Update Status**: Change task status using flexible query parameters (no task ID required!)

### ✅ Jalali Calendar Support
- Full support for Persian/Jalali calendar (شمسی)
- Automatic date validation and normalization
- Tehran timezone (Asia/Tehran)
- Date format: `YYYY-MM-DD` or `YYYY/MM/DD`

### ✅ Human-in-the-Loop
- **Confirmation Required** for all write operations (create events, create tasks, update status)
- **Read operations** execute immediately without confirmation
- Clear presentation of pending actions before execution

### ✅ Conversational Memory
- Remembers last **7 interactions** for context-aware responses
- Maintains conversation flow across sessions
- Thread-based memory management

---

## 📦 INSTALLATION

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Requirements:**
- `langchain` - LangChain framework
- `langchain-openai` - OpenAI integration
- `langgraph` - Graph-based agent workflows
- `jdatetime` - Jalali calendar support
- `pytz` - Timezone handling
- `pydantic` - Data validation
- `flask` - Web framework (for web interface)

### 2. Set Up API Key

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or set it in your Python script:
```python
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"
```

---

## 🚀 QUICK START

### 🌐 Web Interface (Recommended)

The easiest way to use the assistant is through the professional web interface:

```bash
# Windows
start_web_ui.bat

# Linux/Mac
bash start_web_ui.sh

# Or directly
python app.py
```

Then open your browser to: **http://127.0.0.1:5000**

**Features:**
- 🎨 Modern ChatGPT-style interface
- 🌙 Dark/Light mode toggle
- 📱 Mobile-responsive design
- 💬 Real-time chat with typing indicators
- 🎯 Quick action buttons
- 🔄 Persistent conversation threads

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed web interface documentation.

---

### 💻 CLI Mode (Python)

```python
from agent import IranianManagerAssistant

# Initialize the assistant
assistant = IranianManagerAssistant(
    openai_api_key="your-api-key",
    model="gpt-4o-mini"
)

# Start chatting
response = assistant.chat("Create a meeting for 1403-09-15 titled 'Budget Review'")
print(response)
```

### Run Example Script

```bash
python example_usage.py
```

This provides an interactive CLI where you can:
- Create events and tasks
- Query your calendar and task list
- Update task statuses
- Experience human-in-the-loop confirmations

---

## 🧪 TESTING

Run comprehensive tests:

```bash
python test_assistant.py
```

Tests cover:
- ✅ Database operations (CRUD)
- ✅ Jalali date validation
- ✅ All LangChain tools
- ✅ Edge cases and error handling

---

## 📚 ARCHITECTURE

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  LANGGRAPH WORKFLOW                          │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐            │
│  │  Agent   │──▶│  Tools   │──▶│  Approval    │            │
│  │  Node    │   │  Node    │   │  Check       │            │
│  └──────────┘   └──────────┘   └──────────────┘            │
│        │                               │                     │
│        │                               ▼                     │
│        │                      ┌──────────────┐              │
│        └─────────────────────▶│   Execute    │              │
│                                │   Approved   │              │
│                                └──────────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    TOOL LAYER                                │
│  • create_event_tool      • create_task_tool                │
│  • get_event_tool         • get_task_tool                   │
│  • update_task_status_tool                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                DATABASE LAYER (SQLite)                       │
│  Tables: events, tasks                                       │
│  Jalali date fields, indexed for fast queries               │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema

#### Events Table
| Column      | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| id          | INTEGER | ✓        | Primary key (auto-increment)   |
| date        | TEXT    | ✓        | Event date (Jalali format)     |
| title       | TEXT    | ✓        | Event title                    |
| attendee    | TEXT    |          | Attendee name(s)               |
| description | TEXT    |          | Event description              |
| location    | TEXT    |          | Event location                 |

#### Tasks Table
| Column      | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| id          | INTEGER | ✓        | Primary key (auto-increment)   |
| due_date    | TEXT    | ✓        | Task due date (Jalali format)  |
| description | TEXT    | ✓        | Task description               |
| project     | TEXT    |          | Project name                   |
| status      | TEXT    | ✓        | Task status (default: "undone")|
| attendant   | TEXT    |          | Attendant name                 |

### Workflow States

1. **Agent Node**: LLM decides which tool to use based on user input
2. **Conditional Routing**:
   - **Read operations** → Execute immediately
   - **Write operations** → Request approval
3. **Approval Check**: Present action details, wait for user confirmation
4. **Execute Approved**: Run the confirmed tool
5. **Update Memory**: Store interaction for context

---

## 💡 USAGE EXAMPLES

### Example 1: Create an Event

**User Input:**
```
Create a meeting for 1403-09-20 titled "Product Launch Review" with Ahmad Mohammadi at Conference Room B
```

**Agent Response:**
```
⚠️ Confirmation Required

I'm about to execute: create_event_tool

Parameters:
- date: 1403-09-20
- title: Product Launch Review
- attendee: Ahmad Mohammadi
- location: Conference Room B

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

**User Confirmation:**
```
yes
```

**Final Response:**
```
✅ Event created successfully! Event ID: 1, Date: 1403-09-20, Title: Product Launch Review
```

---

### Example 2: Query Events

**User Input:**
```
Show me all events for Ahmad Mohammadi
```

**Agent Response:**
```
📅 Found 1 event(s):

1. **Product Launch Review**
   📆 Date: 1403-09-20
   👤 Attendee: Ahmad Mohammadi
   📍 Location: Conference Room B
   🆔 ID: 1
```

---

### Example 3: Create a Task

**User Input:**
```
Add a task: Prepare presentation slides by 1403-09-18 for Marketing Campaign project
```

**Agent Response:**
```
⚠️ Confirmation Required

I'm about to execute: create_task_tool

Parameters:
- due_date: 1403-09-18
- description: Prepare presentation slides
- project: Marketing Campaign

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

---

### Example 4: Update Task Status (Without Task ID!)

**User Input:**
```
Mark the presentation task as done
```

**Agent Response:**
```
⚠️ Confirmation Required

I'm about to execute: update_task_status_tool

Parameters:
- description: presentation
- new_status: done

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

**After Confirmation:**
```
✅ Task status updated successfully!
   Task ID: 1
   Description: Prepare presentation slides
   Due Date: 1403-09-18
   Project: Marketing Campaign
   Old status: undone
   New status: done
```

---

### Example 5: Query Tasks by Project

**User Input:**
```
Show me all tasks for Marketing Campaign
```

**Agent Response:**
```
📋 Found 1 task(s):

1. ✅ **Prepare presentation slides**
   📆 Due: 1403-09-18
   🔖 Status: done
   📁 Project: Marketing Campaign
   🆔 ID: 1
```

---

## 🔧 ADVANCED CONFIGURATION

### Custom Model Selection

```python
assistant = IranianManagerAssistant(
    openai_api_key="your-api-key",
    model="gpt-4-turbo-preview"  # Use GPT-4 for better reasoning
)
```

### Thread Management

```python
# Different conversation threads
response1 = assistant.chat("Create event...", thread_id="user_123")
response2 = assistant.chat("Create task...", thread_id="user_456")

# Get conversation history
history = assistant.get_conversation_history(thread_id="user_123")
```

### Custom Database Path

```python
from database import DatabaseManager

db = DatabaseManager(db_path="custom_path.db")
```

---

## 📝 API REFERENCE

### IranianManagerAssistant

#### `__init__(openai_api_key: str, model: str = "gpt-4o-mini")`
Initialize the assistant.

**Parameters:**
- `openai_api_key`: Your OpenAI API key
- `model`: Model name (default: "gpt-4o-mini")

#### `chat(user_input: str, thread_id: str = "default") -> str`
Send a message to the assistant.

**Parameters:**
- `user_input`: User's message
- `thread_id`: Conversation thread ID

**Returns:** Assistant's response string

#### `get_conversation_history(thread_id: str = "default") -> list`
Get conversation history for a thread.

**Returns:** List of interaction dictionaries

---

## 🛡️ ERROR HANDLING

The system includes comprehensive error handling:

- **Invalid Jalali dates** → Clear validation error messages
- **Missing required fields** → Prompts for missing information
- **Database errors** → Graceful error messages
- **Multiple task matches** → Lists all matches and asks for clarification
- **No results found** → Helpful messages with filter information

---

## 🌟 BEST PRACTICES

1. **Date Format**: Always use Jalali dates in `YYYY-MM-DD` format (e.g., `1403-09-20`)
2. **Required Fields**: Ensure required fields are provided:
   - Events: date, title
   - Tasks: due_date, description
3. **Status Values**: Use consistent status values: `undone`, `in_progress`, `done`, `cancelled`
4. **Natural Language**: Feel free to use conversational Persian or English
5. **Partial Queries**: Use partial matching for flexible searches (e.g., "09" will match "1403-09-*")

---

## 🔒 PRODUCTION CONSIDERATIONS

### Security
- Store API keys in environment variables
- Use `.env` files (with `python-dotenv`)
- Never commit API keys to version control

### Performance
- Database is indexed for fast queries
- Use connection pooling for high-load scenarios
- Consider PostgreSQL for production at scale

### Monitoring
- Add logging to track agent decisions
- Monitor tool execution times
- Track approval rates and user patterns

---

## 📄 LICENSE

This project is provided as-is for educational and commercial use.

---

## 🙏 ACKNOWLEDGMENTS

Built with:
- **LangChain** & **LangGraph** - Agent orchestration framework
- **OpenAI** - Language model provider
- **jdatetime** - Jalali calendar support

Designed following best practices from the **GLOBAL AI ENGINEERING CONSORTIUM (GAEC)** guidelines.

---

## 📞 SUPPORT

For issues, questions, or contributions:
- Review the test suite: `test_assistant.py`
- Check example usage: `example_usage.py`
- Examine the architecture: `agent.py`, `tools.py`, `database.py`

---

**Built with 🔥 for Iranian Managers**


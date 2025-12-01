# ⚡ QUICK START GUIDE
## Get Your Iranian Manager Assistant Running in 5 Minutes

---

## 🎯 Prerequisites

- Python 3.9 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Terminal/Command Prompt access

---

## 📦 Step 1: Install Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- `langchain` - Agent framework
- `langchain-openai` - OpenAI integration  
- `langgraph` - Workflow orchestration
- `jdatetime` - Jalali calendar
- `pytz` - Timezone support
- `pydantic` - Data validation

---

## 🔑 Step 2: Set Your API Key

### Option A: Environment Variable (Recommended)

**Windows:**
```bash
set OPENAI_API_KEY=sk-your-api-key-here
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### Option B: In Code

Edit `example_usage.py` line 12:
```python
api_key = "sk-your-api-key-here"  # Replace with your actual key
```

---

## 🧪 Step 3: Run Tests (Optional but Recommended)

Verify everything works:

```bash
python test_assistant.py
```

You should see:
```
🧪 ========================================================================== 🧪
   IRANIAN MANAGER PERSONAL ASSISTANT - COMPREHENSIVE TEST SUITE
🧪 ========================================================================== 🧪

TEST 1: Database Operations
✓ Testing event creation...
✓ Testing event retrieval...
✓ Testing task creation...
...
🎉 ALL TESTS COMPLETED SUCCESSFULLY!
```

---

## 🚀 Step 4: Start the Interactive Assistant

```bash
python example_usage.py
```

You'll see:
```
================================================================================
🤖 IRANIAN MANAGER PERSONAL ASSISTANT
================================================================================
Features: Event Management, Task Management, Jalali Calendar Support
Type 'quit' or 'exit' to end the conversation
================================================================================

💬 Interactive Mode Started
Example commands:
  - 'Create an event for tomorrow at 10 AM titled Team Standup'
  - 'Show me all events for this week'
  - 'Add a task to finish the presentation by Friday'
  - 'Show me all undone tasks'
  - 'Mark task 1 as done'

👤 You: 
```

---

## 💡 Step 5: Try Your First Commands

### Create an Event

**You type:**
```
Create a meeting for 1403-09-20 titled "Budget Review" with Ali Mohammadi at Conference Room A
```

**Assistant responds:**
```
⚠️ Confirmation Required

I'm about to execute: create_event_tool

Parameters:
- date: 1403-09-20
- title: Budget Review
- attendee: Ali Mohammadi
- location: Conference Room A

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

**You type:**
```
yes
```

**Assistant confirms:**
```
✅ Event created successfully! Event ID: 1, Date: 1403-09-20, Title: Budget Review
```

---

### Query Events

**You type:**
```
Show me all events for Ali Mohammadi
```

**Assistant responds:**
```
📅 Found 1 event(s):

1. **Budget Review**
   📆 Date: 1403-09-20
   👤 Attendee: Ali Mohammadi
   📍 Location: Conference Room A
   🆔 ID: 1
```

---

### Create a Task

**You type:**
```
Add a task: Complete quarterly report by 1403-09-25 for Finance project
```

**Assistant responds:**
```
⚠️ Confirmation Required

I'm about to execute: create_task_tool

Parameters:
- due_date: 1403-09-25
- description: Complete quarterly report
- project: Finance

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

**You type:**
```
yes
```

**Assistant confirms:**
```
✅ Task created successfully! Task ID: 1, Due: 1403-09-25, Description: Complete quarterly report
```

---

### Update Task Status (Without Task ID!)

**You type:**
```
Mark the Finance project task as done
```

**Assistant responds:**
```
⚠️ Confirmation Required

I'm about to execute: update_task_status_tool

Parameters:
- project: Finance
- new_status: done

Do you approve this action? Please respond with 'yes' to confirm or 'no' to cancel.
```

**You type:**
```
yes
```

**Assistant confirms:**
```
✅ Task status updated successfully!
   Task ID: 1
   Description: Complete quarterly report
   Due Date: 1403-09-25
   Project: Finance
   Old status: undone
   New status: done
```

---

## 📝 Common Commands Reference

### Events

| Command Example | Description |
|----------------|-------------|
| `Create a meeting for 1403-09-15 titled "Team Sync"` | Create new event |
| `Show all events for 1403-09` | Get events for a month |
| `Find events with Ahmad` | Search by attendee |
| `Show events at Conference Room B` | Search by location |

### Tasks

| Command Example | Description |
|----------------|-------------|
| `Create task: Finish report by 1403-09-20` | Create new task |
| `Show all undone tasks` | Filter by status |
| `Get tasks for Marketing project` | Filter by project |
| `Mark the report task as in_progress` | Update status |
| `Show tasks due tomorrow` | Filter by date |

### Status Values

Use these status values for tasks:
- `undone` (default)
- `in_progress`
- `done`
- `cancelled`

---

## 🌍 Date Format Guide

### Jalali Calendar

Always use Jalali (Persian/شمسی) dates:

**Format**: `YYYY-MM-DD` or `YYYY/MM/DD`

**Examples**:
- `1403-09-20` ✅ Correct
- `1403/09/20` ✅ Correct  
- `2024-12-10` ❌ Wrong (Gregorian)

**Current Jalali Date**: Check [time.ir](https://time.ir) or the assistant will tell you!

### Month Names (Jalali)

| Number | Persian Name | Approx. Gregorian |
|--------|--------------|-------------------|
| 01 | فروردین | Mar-Apr |
| 02 | اردیبهشت | Apr-May |
| 03 | خرداد | May-Jun |
| 04 | تیر | Jun-Jul |
| 05 | مرداد | Jul-Aug |
| 06 | شهریور | Aug-Sep |
| 07 | مهر | Sep-Oct |
| 08 | آبان | Oct-Nov |
| 09 | آذر | Nov-Dec |
| 10 | دی | Dec-Jan |
| 11 | بهمن | Jan-Feb |
| 12 | اسفند | Feb-Mar |

---

## 🔧 Troubleshooting

### Issue: "No module named 'langchain'"

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

---

### Issue: "OpenAI API key not found"

**Solution:**  
Make sure your API key is set:
```bash
# Check if it's set
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Mac/Linux

# If empty, set it
set OPENAI_API_KEY=sk-your-key  # Windows
export OPENAI_API_KEY=sk-your-key  # Mac/Linux
```

---

### Issue: "Invalid Jalali date format"

**Solution:**  
Use format `YYYY-MM-DD`:
- ✅ `1403-09-20`
- ❌ `20-09-1403`
- ❌ `09/20/1403`

---

### Issue: Database locked error

**Solution:**  
Close any other programs accessing `assistant.db`, then restart:
```bash
python example_usage.py
```

---

## 🎓 Learning Path

### Beginner
1. ✅ Complete this Quick Start
2. ✅ Try all example commands above
3. ✅ Read `README.md` for more features

### Intermediate
1. Read `ARCHITECTURE.md` to understand the system
2. Run `test_assistant.py` and examine the code
3. Modify `example_usage.py` to add custom commands

### Advanced
1. Study `agent.py` to understand LangGraph workflow
2. Extend `tools.py` with new capabilities
3. Integrate with external APIs or databases

---

## 📚 Next Steps

### Customize Your Assistant

**Change the model** (in `example_usage.py`):
```python
assistant = IranianManagerAssistant(
    openai_api_key=api_key,
    model="gpt-4-turbo-preview"  # More powerful model
)
```

**Use multiple conversation threads**:
```python
# Different users or contexts
assistant.chat("Create event...", thread_id="user_1")
assistant.chat("Create task...", thread_id="user_2")
```

**Integrate with your app**:
```python
from agent import IranianManagerAssistant

assistant = IranianManagerAssistant(openai_api_key="your-key")

# In your Flask/FastAPI endpoint
@app.post("/chat")
def chat(message: str, user_id: str):
    response = assistant.chat(message, thread_id=user_id)
    return {"response": response}
```

---

## 🎯 Pro Tips

1. **Natural Language**: You can use Persian/Farsi or English naturally
   - ✅ "یک جلسه برای فردا ایجاد کن"
   - ✅ "Create a meeting for tomorrow"

2. **Partial Queries**: Use partial information
   - ✅ "Show tasks for 1403-09" (all tasks in that month)
   - ✅ "Find events with Ali" (partial name match)

3. **Context Memory**: The agent remembers your last 7 interactions
   - ✅ "What was that meeting I created earlier?"

4. **Flexible Updates**: Update tasks without knowing the ID
   - ✅ "Mark the presentation task as done"
   - ✅ "Update the Finance project task to in_progress"

5. **Cancel Anytime**: Respond "no" to cancel any write operation

---

## 🆘 Need Help?

- **Documentation**: See `README.md` and `ARCHITECTURE.md`
- **Tests**: Run `python test_assistant.py` to verify setup
- **Code Examples**: Check `example_usage.py`

---

## ✅ Checklist: You're Ready When...

- [ ] Tests pass successfully
- [ ] You can create an event and see confirmation
- [ ] You can query events and see results
- [ ] You can create a task and approve it
- [ ] You can update task status without task ID
- [ ] Agent remembers your previous questions

---

**Congratulations! 🎉 Your Iranian Manager Assistant is ready to use!**

---

*Built with LangGraph + LangChain | Powered by OpenAI GPT-4*


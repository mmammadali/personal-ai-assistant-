# 🚀 RAG Agent - Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

### Step 2: Verify API Key

Make sure your `.env` file contains:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 3: Start the Web Interface

```bash
# Windows
start_web_ui.bat

# Or directly
python app.py
```

### Step 4: Open Browser

```
http://127.0.0.1:5000
```

### Step 5: Access RAG Agent

- Click **"مدیریت اسناد (RAG)"** in the sidebar
- You'll see the document management interface

---

## 📤 First Upload

### Create a Test Document

```bash
# Windows Command Prompt
echo این یک سند تستی است. تاریخ مهلت: 1403/09/20. مبلغ پروژه: 5,000,000 تومان. دستورالعمل: پرداخت به صورت نقدی انجام شود. > test.txt

# Or create a file manually with any text editor
```

### Upload via Web UI

1. Click the **upload button** (📤) or **"بارگذاری سند"**
2. Select your `test.txt` file
3. Wait for processing (5-10 seconds)
4. You'll see a success message!

---

## 💬 Try These Questions

Copy and paste these into the chat:

```
لیست اسناد من را نشان بده
```

```
این سند درباره چیست؟
```

```
تاریخ مهلت چه زمانی است؟
```

```
مبلغ پروژه چقدر است؟
```

```
خلاصه این سند را با استخراج تمام تاریخ‌ها و مبالغ مالی بده
```

---

## 🎯 Common Tasks

### List All Documents
```
لیست اسناد
```

### Get Summary
```
خلاصه سند [نام سند] را بده
```

### Ask Specific Question
```
از سند [نام سند] بپرس: [سوال شما]
```

### Delete Document
```
سند با شناسه [DOCUMENT_ID] را حذف کن
```

---

## 🔄 Switch Between Agents

Use the **sidebar** to switch between:

- **📅 مدیریت وظایف و رویدادها** - Task/Event Management
- **📄 مدیریت اسناد (RAG)** - Document Management

Both agents work independently with their own conversations!

---

## 🐍 Python API Example

```python
from rag_agent import RAGAgent
from config import OPENAI_API_KEY

# Initialize
agent = RAGAgent(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini"
)

# Upload
response = agent.chat(
    "لطفاً این فایل را بارگذاری کن: C:\\path\\to\\document.pdf"
)
print(response)

# Ask question
response = agent.chat("این سند درباره چیست؟")
print(response)
```

---

## 📱 Supported File Formats

- ✅ PDF (`.pdf`)
- ✅ Word (`.docx`, `.doc`)
- ✅ Text (`.txt`, `.md`)
- ✅ Excel (`.xlsx`, `.xls`)
- ✅ PowerPoint (`.pptx`, `.ppt`)
- ✅ Images (`.jpg`, `.jpeg`, `.png`)

---

## 🎨 Features

### 1. Upload Documents
- Drag & drop
- Multiple formats
- Auto-processing
- Progress indicator

### 2. Ask Questions
- Natural language queries in Farsi
- Context-aware answers
- Multi-document search

### 3. Get Summaries
- Professional Farsi summaries
- Auto-extract dates, amounts, guidelines
- Identify sensitive information

### 4. Manage Documents
- List all documents
- View details
- Delete unwanted documents

---

## ⚡ Pro Tips

1. **Use descriptive filenames**: `contract_2024.pdf` instead of `doc1.pdf`
2. **Ask follow-up questions**: The agent remembers context
3. **Be specific**: "تاریخ سررسید قرارداد چیست؟" is better than "تاریخ؟"
4. **Use the sidebar**: Easily switch between Task and Document agents
5. **Check the list**: Use "لیست اسناد" to see what's uploaded

---

## 🔧 Configuration

### Change Vector Database

Open `config.py` and change:

```python
# For local development (default)
RAG_VECTOR_STORE_TYPE = "chromadb"

# For production/cloud deployment
RAG_VECTOR_STORE_TYPE = "pinecone"
PINECONE_API_KEY = "your-api-key"
```

### Adjust Upload Limits

```python
MAX_FILE_SIZE_MB = 50  # Increase if needed
```

---

## 🐛 Troubleshooting

### Upload Fails
- Check file size (< 50MB)
- Ensure format is supported
- Check disk space

### Can't Find Documents
- Make sure upload completed successfully
- Try "لیست اسناد" to verify

### Poor Answers
- Check if document uploaded correctly
- Rephrase your question
- Be more specific

---

## 📚 More Information

- **RAG_AGENT_GUIDE.md** - Complete documentation
- **example_rag_usage.py** - Python examples
- **RAG_INTEGRATION_COMPLETE.md** - Integration details

---

## ✅ You're Ready!

```bash
python app.py
# Open http://127.0.0.1:5000
# Click "مدیریت اسناد (RAG)" in sidebar
# Upload a document
# Start asking questions!
```

**Happy document management! 🎉**


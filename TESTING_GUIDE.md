# 🧪 RAG Agent Testing Guide

## ✅ What Has Been Created

All RAG agent components have been successfully created:

1. ✅ **rag_agent.py** - Main RAG agent with LangGraph
2. ✅ **rag_tools.py** - All 6 tools (upload, query, summarize, list, delete, info)
3. ✅ **rag_vector_store.py** - Vector database abstraction
4. ✅ **document_processor.py** - Multi-format document processing
5. ✅ **Web UI** - Complete interface with sidebar
6. ✅ **API Endpoints** - RESTful API for all operations
7. ✅ **Test Scripts** - Automated testing scripts

---

## 🚀 Step-by-Step Testing Instructions

### Step 1: Install Missing Dependencies

First, install the required packages:

```bash
python -m pip install langchain-community langchain-chroma langchain-pinecone unstructured pypdf python-docx openpyxl python-pptx pillow requests
```

Or install all at once:

```bash
python -m pip install -r requirements.txt
```

### Step 2: Start the Web Server

```bash
python app.py
```

You should see:
```
🚀 Iranian Manager Personal Assistant - Web Interface
🌐 Server starting at: http://127.0.0.1:5000
```

### Step 3: Open Web Interface

Open your browser and go to:
```
http://127.0.0.1:5000
```

### Step 4: Access RAG Agent

1. Click **"مدیریت اسناد (RAG)"** in the sidebar
2. You'll see the RAG document management interface

---

## 📤 Test 1: Upload Document

### Via Web UI:
1. Click the **upload button** (📤) in the header
2. Select `QUICKSTART_RAG.md` file
3. Wait for upload and processing (5-10 seconds)
4. You should see: "✅ سند با موفقیت بارگذاری شد!"

### Via API (using Python):
```python
import requests

files = {'file': open('QUICKSTART_RAG.md', 'rb')}
response = requests.post('http://127.0.0.1:5000/api/rag/upload', files=files)
print(response.json())
```

### Expected Result:
- ✅ Success message with document ID
- ✅ Document name and metadata
- ✅ Number of chunks created

---

## 📋 Test 2: List Documents

### Via Web UI:
Type in chat:
```
لیست اسناد من را نشان بده
```

### Via API:
```python
response = requests.post(
    'http://127.0.0.1:5000/api/rag/chat',
    json={'message': 'لیست اسناد من را نشان بده'}
)
print(response.json()['response'])
```

### Expected Result:
- ✅ List of all uploaded documents
- ✅ Document names, IDs, formats
- ✅ Number of pages/chunks

---

## 💬 Test 3: Query Documents

### Test Queries (Type in Web UI):

#### Query 1: General Question
```
این سند درباره چیست؟
```

**Expected:** Summary of document content in Farsi

#### Query 2: Extract Dates
```
تاریخ‌های مهم در این سند چیست؟
```

**Expected:** List of dates found in document

#### Query 3: Financial Data
```
مبالغ مالی در سند چقدر است؟
```

**Expected:** Financial amounts extracted

#### Query 4: Guidelines
```
دستورالعمل‌های این سند چیست؟
```

**Expected:** Guidelines and instructions extracted

### Via API:
```python
queries = [
    "این سند درباره چیست؟",
    "تاریخ‌های مهم در این سند چیست؟",
    "مبالغ مالی در سند چقدر است؟"
]

for query in queries:
    response = requests.post(
        'http://127.0.0.1:5000/api/rag/chat',
        json={'message': query}
    )
    print(f"Query: {query}")
    print(f"Response: {response.json()['response'][:200]}...")
    print()
```

---

## 📝 Test 4: Summarize Document

### Via Web UI:
Type:
```
خلاصه کامل این سند را با استخراج تمام تاریخ‌ها، مبالغ مالی، و دستورالعمل‌ها بده
```

### Via API:
```python
response = requests.post(
    'http://127.0.0.1:5000/api/rag/chat',
    json={'message': 'خلاصه کامل این سند را بده'}
)
print(response.json()['response'])
```

### Expected Result:
- ✅ Professional Farsi summary
- ✅ Extracted dates section
- ✅ Financial data section
- ✅ Guidelines section
- ✅ Sensitive keywords identified
- ✅ Content preview

---

## ℹ️ Test 5: Get Document Info

### Via Web UI:
```
اطلاعات سند بارگذاری شده را نشان بده
```

### Expected Result:
- ✅ Document name
- ✅ Document ID
- ✅ File format
- ✅ Number of pages
- ✅ Number of chunks

---

## 🗑️ Test 6: Delete Document (Optional)

### Via Web UI:
First, get document ID from list, then:
```
سند با شناسه [DOCUMENT_ID] را حذف کن
```

### Expected Result:
- ✅ Confirmation message
- ✅ Document removed from database

---

## 🧪 Automated Testing

### Run Simple API Test:
```bash
python test_rag_simple.py
```

This will:
1. ✅ Check server health
2. ✅ Upload a test document
3. ✅ List documents
4. ✅ Query documents
5. ✅ Get summary
6. ✅ Get document info

### Run Full Test:
```bash
python test_rag_functionality.py
```

(Requires all dependencies installed)

---

## 📊 Testing Checklist

### Core Functionality
- [ ] Server starts successfully
- [ ] Web UI loads correctly
- [ ] Sidebar navigation works
- [ ] Can switch between agents

### Document Upload
- [ ] Upload PDF file
- [ ] Upload DOCX file
- [ ] Upload TXT file
- [ ] Upload shows progress
- [ ] Upload completes successfully
- [ ] Document ID is returned

### Document Management
- [ ] List documents works
- [ ] Document info retrieved
- [ ] Delete document works
- [ ] Multiple documents handled

### Query & Search
- [ ] General questions answered
- [ ] Date extraction works
- [ ] Financial data extracted
- [ ] Guidelines extracted
- [ ] Answers in Farsi
- [ ] Context-aware responses

### Summarization
- [ ] Summary generated
- [ ] Dates extracted
- [ ] Financial data extracted
- [ ] Guidelines extracted
- [ ] Sensitive keywords identified
- [ ] Summary in fluent Farsi

### API Endpoints
- [ ] `/health` works
- [ ] `/api/rag/chat` works
- [ ] `/api/rag/upload` works
- [ ] `/api/rag/clear` works

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'langchain_community'"

**Solution:**
```bash
python -m pip install langchain-community langchain-chroma
```

### Issue: "Server not starting"

**Solution:**
1. Check if port 5000 is in use: `netstat -ano | findstr :5000`
2. Change port in `config.py`: `FLASK_PORT = 5001`
3. Check for errors in console output

### Issue: "Upload fails"

**Solution:**
1. Check file size (< 50MB)
2. Check file format (must be in ALLOWED_EXTENSIONS)
3. Check disk space
4. Check `uploads/` folder exists

### Issue: "No documents found"

**Solution:**
1. Make sure upload completed successfully
2. Check `chroma_db/` folder exists
3. Try listing documents again
4. Check console for errors

### Issue: "Poor answers"

**Solution:**
1. Ensure document uploaded correctly
2. Check document has readable text
3. Rephrase your question
4. Be more specific in queries

---

## 📈 Performance Testing

### Test Upload Speed:
- Small file (<1MB): Should complete in 2-5 seconds
- Medium file (1-10MB): Should complete in 5-15 seconds
- Large file (10-50MB): Should complete in 15-60 seconds

### Test Query Speed:
- Simple query: 2-4 seconds
- Complex query: 4-8 seconds
- Summary: 5-10 seconds

### Test Concurrent Users:
- Test with multiple browser tabs
- Test with multiple API requests
- Monitor server performance

---

## ✅ Success Criteria

The RAG agent is working correctly if:

1. ✅ Documents upload successfully
2. ✅ Documents appear in list
3. ✅ Queries return relevant answers
4. ✅ Summaries extract key information
5. ✅ All responses are in Farsi
6. ✅ Web UI is responsive
7. ✅ API endpoints work
8. ✅ No errors in console

---

## 🎯 Next Steps After Testing

1. **Upload Real Documents**
   - Upload your actual business documents
   - Test with various formats
   - Verify extraction quality

2. **Customize Configuration**
   - Adjust chunk size for your documents
   - Change embedding model if needed
   - Configure vector database

3. **Deploy to Production**
   - Switch to Pinecone for cloud
   - Add user authentication
   - Implement backups
   - Add monitoring

---

## 📞 Support

If you encounter issues:

1. Check console output for errors
2. Review `RAG_AGENT_GUIDE.md` for detailed docs
3. Check `QUICKSTART_RAG.md` for quick reference
4. Review test scripts for examples

---

**Happy Testing! 🎉**






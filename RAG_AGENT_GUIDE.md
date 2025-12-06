# 📄 RAG Document Agent - Complete Guide

## 🎯 Overview

The RAG (Retrieval-Augmented Generation) Document Agent is a powerful AI assistant that helps you manage, analyze, and interact with documents in both **Farsi** and **English**. It's seamlessly integrated into your existing Iranian Manager Personal Assistant system.

---

## ✨ Features

### 1. **📤 Document Upload & Processing**
- Supports multiple formats: **PDF, DOCX, TXT, Excel, PowerPoint, Images**
- Automatic text extraction and chunking
- Vector embeddings for intelligent search
- Metadata extraction (pages, format, size)

### 2. **📋 Document Management**
- List all uploaded documents
- View document details
- Delete documents
- Track document metadata

### 3. **💬 Intelligent Q&A**
- Ask questions about specific documents
- Search across all documents
- Context-aware answers in Farsi
- Semantic search using vector embeddings

### 4. **📝 Smart Summarization**
- Professional document summaries in Farsi
- Automatic extraction of:
  - 📅 Dates and deadlines
  - 💰 Financial data and amounts
  - 📋 Guidelines and rules
  - 🔑 Sensitive keywords
  - 📊 Key statistics

### 5. **🌐 Dual Interface**
- **Web UI**: Beautiful drag-and-drop file upload
- **CLI**: Command-line interface for automation
- **API**: RESTful endpoints for integration

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file or set environment variables:

```bash
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Run the Web Interface

```bash
# Windows
start_web_ui.bat

# Linux/Mac
bash start_web_ui.sh

# Or directly
python app.py
```

### 4. Access the RAG Agent

Open your browser and navigate to:
- **Main App**: http://127.0.0.1:5000/
- **RAG Agent**: http://127.0.0.1:5000/rag

---

## 💻 Web Interface Usage

### Accessing the RAG Agent

1. Open the web application
2. Click on **"مدیریت اسناد (RAG)"** in the sidebar
3. You'll see the document management interface

### Uploading Documents

**Method 1: Drag & Drop**
- Drag files directly into the upload area

**Method 2: Click to Upload**
- Click the **"بارگذاری سند"** button
- Select your file
- Wait for processing (you'll see a progress bar)

**Method 3: Upload Button in Header**
- Click the upload icon (📤) in the header
- Select your file

### Asking Questions

Once documents are uploaded, you can:

```
"این سند درباره چیست؟"
(What is this document about?)

"تاریخ‌های مهم در این سند چیست؟"
(What are the important dates in this document?)

"مبلغ کل چقدر است؟"
(What is the total amount?)

"خلاصه این سند را بده"
(Give me a summary of this document)
```

### Managing Documents

```
"لیست اسناد من را نشان بده"
(Show me my documents list)

"سند با شناسه [ID] را حذف کن"
(Delete document with ID [ID])

"اطلاعات سند [نام] را نشان بده"
(Show information about document [name])
```

---

## 🐍 Python API Usage

### Basic Usage

```python
from rag_agent import RAGAgent
from config import OPENAI_API_KEY

# Initialize agent
agent = RAGAgent(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini",
    vector_store_type="chromadb"
)

# Upload a document
response = agent.chat(
    "لطفاً این فایل را بارگذاری کن: /path/to/document.pdf",
    thread_id="user123"
)
print(response)

# Ask a question
response = agent.chat(
    "این سند درباره چیست؟",
    thread_id="user123"
)
print(response)

# Get summary
response = agent.chat(
    "خلاصه این سند را با استخراج تاریخ‌ها و مبالغ مالی بده",
    thread_id="user123"
)
print(response)
```

### Advanced Usage

```python
# List all documents
response = agent.chat("لیست اسناد را نشان بده")

# Query specific document
response = agent.chat(
    "از سند contract_2024 بپرس: مهلت پرداخت چه زمانی است؟"
)

# Delete a document
response = agent.chat(
    "سند با شناسه contract_2024_abc123 را حذف کن"
)

# Reset conversation
agent.reset_conversation(thread_id="user123")

# Get conversation state
state = agent.get_conversation_state(thread_id="user123")
print(state)
```

---

## 🔧 Configuration

### Vector Store Configuration

The system supports **ChromaDB** (local) and **Pinecone** (cloud):

#### ChromaDB (Default - Local & Free)

```python
# config.py
RAG_VECTOR_STORE_TYPE = "chromadb"
RAG_CHROMA_PERSIST_DIR = "./chroma_db"
RAG_COLLECTION_NAME = "rag_documents"
```

**Pros:**
- ✅ Free and open-source
- ✅ No external dependencies
- ✅ Persistent local storage
- ✅ Perfect for development

**Cons:**
- ❌ Single-user only
- ❌ Not suitable for production cloud deployment

#### Pinecone (Cloud & Multi-Tenant)

```python
# config.py
RAG_VECTOR_STORE_TYPE = "pinecone"
PINECONE_API_KEY = "your-pinecone-api-key"
PINECONE_INDEX_NAME = "rag-documents"
PINECONE_NAMESPACE = "default"
```

**Pros:**
- ✅ Cloud-native
- ✅ Multi-tenant support
- ✅ Scalable to millions of users
- ✅ Perfect for mobile apps

**Cons:**
- ❌ Requires API key
- ❌ Paid service (free tier available)

### Document Processing Configuration

```python
# config.py
RAG_CHUNK_SIZE = 1000  # Characters per chunk
RAG_CHUNK_OVERLAP = 200  # Overlap between chunks
MAX_FILE_SIZE_MB = 50  # Maximum upload size
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt', ...}
```

---

## 📁 Supported File Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| **PDF** | `.pdf` | Full text extraction, supports Farsi |
| **Word** | `.docx`, `.doc` | Microsoft Word documents |
| **Text** | `.txt`, `.md` | Plain text and Markdown |
| **Excel** | `.xlsx`, `.xls` | Spreadsheets (tables extracted) |
| **PowerPoint** | `.pptx`, `.ppt` | Presentations |
| **Images** | `.jpg`, `.jpeg`, `.png` | OCR text extraction |

---

## 🎨 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   WEB INTERFACE                          │
│          (Sidebar with Agent Selection)                  │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  RAG AGENT (LangGraph)                   │
│                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐     │
│  │  Agent   │───▶│  Tools   │───▶│  Process     │     │
│  │  Node    │    │  Node    │    │  Response    │     │
│  └──────────┘    └──────────┘    └──────────────┘     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│                   RAG TOOLS LAYER                        │
│                                                          │
│  • upload_document_tool                                 │
│  • query_document_tool                                  │
│  • summarize_document_tool                              │
│  • list_documents_tool                                  │
│  • delete_document_tool                                 │
│  • get_document_info_tool                               │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              DOCUMENT PROCESSOR                          │
│  • Multi-format loading                                 │
│  • Text chunking                                        │
│  • Metadata extraction                                  │
│  • Intelligent info extraction (dates, finance, etc.)   │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              VECTOR STORE (ChromaDB/Pinecone)            │
│  • Embeddings (OpenAI text-embedding-3-large)           │
│  • Similarity search                                    │
│  • Document management                                  │
│  • Metadata filtering                                   │
└─────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoints

### RAG Agent Endpoints

#### 1. Chat with RAG Agent

```http
POST /api/rag/chat
Content-Type: application/json

{
  "message": "لیست اسناد من را نشان بده"
}
```

**Response:**
```json
{
  "response": "📚 اسناد موجود در پایگاه داده...",
  "timestamp": "14:30"
}
```

#### 2. Upload Document

```http
POST /api/rag/upload
Content-Type: multipart/form-data

file: [binary file data]
```

**Response:**
```json
{
  "success": true,
  "response": "✅ سند با موفقیت بارگذاری شد!...",
  "filename": "document.pdf"
}
```

#### 3. Clear Conversation

```http
POST /api/rag/clear
```

**Response:**
```json
{
  "success": true,
  "message": "گفتگو پاک شد"
}
```

---

## 🧪 Testing

### Run Example Script

```bash
python example_rag_usage.py
```

This script demonstrates:
- Listing documents
- Uploading documents
- Asking questions
- Getting summaries
- Interactive mode

### Manual Testing Steps

1. **Upload a Test Document**
   ```bash
   echo "این یک سند تستی است. تاریخ: 1403/09/15. مبلغ: 1,000,000 تومان" > test.txt
   ```

2. **Open Web Interface**
   - Go to http://127.0.0.1:5000/rag
   - Upload `test.txt`

3. **Ask Questions**
   - "این سند درباره چیست؟"
   - "تاریخ چه زمانی است؟"
   - "مبلغ چقدر است؟"

4. **Get Summary**
   - "خلاصه این سند را بده"

---

## 🌟 Best Practices

### 1. Document Upload

- ✅ **Use clear filenames**: `contract_2024.pdf` instead of `doc1.pdf`
- ✅ **Organize by topic**: Upload related documents together
- ✅ **Check file size**: Keep files under 50MB for best performance
- ✅ **Use quality scans**: For images, ensure good OCR quality

### 2. Asking Questions

- ✅ **Be specific**: "تاریخ سررسید چیست؟" is better than "تاریخ؟"
- ✅ **Reference documents**: "از قرارداد 2024 بپرس: مهلت چیست؟"
- ✅ **Use natural language**: The agent understands conversational Farsi
- ✅ **Ask follow-ups**: The agent remembers context

### 3. Document Management

- ✅ **Regular cleanup**: Delete old documents you no longer need
- ✅ **Use meaningful names**: Name documents descriptively
- ✅ **List before delete**: Check document list to get correct ID
- ✅ **Backup important docs**: Keep originals of critical files

---

## 🚀 Deployment

### Local Development (ChromaDB)

```bash
# Already configured by default
python app.py
```

### Production (Pinecone)

1. **Get Pinecone API Key**
   - Sign up at https://www.pinecone.io/
   - Create an index named `rag-documents`
   - Dimension: 3072 (for text-embedding-3-large)

2. **Update Configuration**
   ```python
   # config.py
   RAG_VECTOR_STORE_TYPE = "pinecone"
   PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
   ```

3. **Deploy to Cloud**
   - Use platforms like: Heroku, Railway, Render, AWS, Azure
   - Set environment variables
   - Use gunicorn for production server

---

## 🛠️ Troubleshooting

### Issue: "Vector store not initialized"

**Solution:**
```python
from rag_tools import initialize_vector_store
initialize_vector_store(store_type="chromadb")
```

### Issue: "File format not supported"

**Solution:** Check `ALLOWED_EXTENSIONS` in `config.py` and ensure your file format is listed.

### Issue: "Upload fails for large files"

**Solution:** Increase `MAX_FILE_SIZE_MB` in `config.py`:
```python
MAX_FILE_SIZE_MB = 100  # Increase limit
```

### Issue: "Poor Farsi text extraction"

**Solution:** Ensure the document has proper Farsi encoding (UTF-8). For scanned documents, use high-quality images for better OCR.

### Issue: "ChromaDB persistence not working"

**Solution:** Check directory permissions:
```bash
chmod 755 ./chroma_db
```

---

## 📊 Performance Tips

1. **Chunk Size**: Smaller chunks (500-1000 chars) for precise Q&A, larger (1500-2000) for summaries
2. **Embedding Model**: Use `text-embedding-3-large` for best quality (more expensive) or `text-embedding-3-small` for speed
3. **Search Results**: Adjust `k` parameter in search (4-8 chunks recommended)
4. **Model Selection**: Use `gpt-4o-mini` for speed, `gpt-4` for complex documents

---

## 🔐 Security Considerations

- ✅ **API Keys**: Never commit API keys to version control
- ✅ **File Validation**: Only allow trusted file formats
- ✅ **Size Limits**: Enforce maximum file sizes
- ✅ **User Isolation**: Use namespaces in Pinecone for multi-tenancy
- ✅ **Data Privacy**: Consider local ChromaDB for sensitive documents

---

## 📝 License

This project is part of the Iranian Manager Personal Assistant system.

---

## 🙏 Support

For issues, questions, or contributions:
- Check the main README.md
- Review example_rag_usage.py
- Examine the architecture diagrams above

---

**Built with 🔥 for Document Intelligence**


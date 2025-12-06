"""
LangChain Tools for RAG Agent
Document management, retrieval, and summarization with Farsi support
"""
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
import logging
import os
from pathlib import Path

from document_processor import DocumentProcessor, IntelligentExtractor
from rag_vector_store import VectorStoreManager, VectorStoreBase

logger = logging.getLogger(__name__)

# Global vector store instance (initialized by agent)
_vector_store: Optional[VectorStoreBase] = None
_document_processor = DocumentProcessor()


def initialize_vector_store(store_type: str = "chromadb", **kwargs):
    """Initialize the global vector store"""
    global _vector_store
    _vector_store = VectorStoreManager.create(store_type=store_type, **kwargs)
    logger.info(f"Vector store initialized: {store_type}")


def get_vector_store() -> VectorStoreBase:
    """Get the global vector store instance"""
    if _vector_store is None:
        raise RuntimeError("Vector store not initialized. Call initialize_vector_store() first.")
    return _vector_store


# ===================== DOCUMENT MANAGEMENT TOOLS =====================

@tool
def upload_document_tool(
    file_path: str,
    document_name: Optional[str] = None
) -> str:
    """
    Upload and embed a document in the vector database.
    Supports multiple formats: PDF, DOCX, TXT, Excel, PowerPoint, Images.
    Documents can be in Farsi or English.
    
    Args:
        file_path: Absolute path to the document file. REQUIRED.
        document_name: Custom name for the document (defaults to filename). OPTIONAL.
        
    Returns:
        Success message with document details
        
    Note: This tool processes the document, creates embeddings, and stores them in the database.
    """
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            return f"❌ فایل پیدا نشد: {file_path}\n(File not found)"
        
        # Get document name
        if not document_name:
            document_name = Path(file_path).stem
        
        # Generate unique document ID
        import uuid
        document_id = f"{document_name}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Processing document: {file_path}")
        
        # Process document
        result = _document_processor.process_document(
            file_path=file_path,
            document_name=document_name
        )
        
        # Get vector store
        vector_store = get_vector_store()
        
        # Add to vector database
        num_chunks = vector_store.add_documents(
            documents=result['chunks'],
            document_id=document_id
        )
        
        return (
            f"✅ **سند با موفقیت بارگذاری شد!**\n\n"
            f"📄 **نام سند:** {document_name}\n"
            f"🆔 **شناسه:** {document_id}\n"
            f"📑 **تعداد صفحات:** {result['metadata']['total_pages']}\n"
            f"🧩 **تعداد بخش‌ها:** {num_chunks}\n"
            f"📊 **تعداد کاراکترها:** {result['total_characters']}\n"
            f"📝 **فرمت:** {result['metadata']['file_extension']}\n\n"
            f"✅ Document uploaded successfully!\n"
            f"You can now ask questions about this document."
        )
    
    except ValueError as e:
        return f"❌ خطای اعتبارسنجی: {str(e)}\n(Validation error)"
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        return f"❌ خطا در بارگذاری سند: {str(e)}\n(Error uploading document)"


@tool
def list_documents_tool() -> str:
    """
    List all documents stored in the vector database.
    Shows document names, IDs, formats, and other metadata.
    
    Returns:
        List of all documents with their details
    """
    try:
        vector_store = get_vector_store()
        documents = vector_store.list_documents()
        
        if not documents:
            return (
                "📚 **هیچ سندی در پایگاه داده وجود ندارد.**\n\n"
                "لطفاً ابتدا یک سند بارگذاری کنید.\n\n"
                "📚 No documents found in the database.\n"
                "Please upload a document first."
            )
        
        # Format results
        result = f"📚 **اسناد موجود در پایگاه داده ({len(documents)} سند):**\n\n"
        
        for i, doc in enumerate(documents, 1):
            result += f"{i}. 📄 **{doc['document_name']}**\n"
            result += f"   🆔 شناسه: {doc['document_id']}\n"
            result += f"   📝 فرمت: {doc['file_extension']}\n"
            result += f"   📑 صفحات: {doc.get('total_pages', 'N/A')}\n\n"
        
        result += "\n💡 **برای پرسش درباره یک سند، می‌توانید سوال خود را بپرسید.**\n"
        result += "You can ask questions about any of these documents."
        
        return result.strip()
    
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        return f"❌ خطا در نمایش اسناد: {str(e)}\n(Error listing documents)"


@tool
def delete_document_tool(document_id: str) -> str:
    """
    Delete a document from the vector database.
    Removes all embeddings and metadata associated with the document.
    
    Args:
        document_id: The unique identifier of the document to delete. REQUIRED.
        
    Returns:
        Success or error message
        
    Note: This operation is irreversible. Make sure you have the correct document ID.
    """
    try:
        vector_store = get_vector_store()
        
        # Check if document exists
        doc_info = vector_store.get_document_info(document_id)
        if not doc_info:
            return (
                f"❌ **سند با شناسه '{document_id}' پیدا نشد.**\n\n"
                f"لطفاً لیست اسناد را بررسی کنید.\n\n"
                f"Document not found: {document_id}"
            )
        
        # Delete document
        success = vector_store.delete_document(document_id)
        
        if success:
            return (
                f"✅ **سند با موفقیت حذف شد!**\n\n"
                f"📄 نام: {doc_info['document_name']}\n"
                f"🆔 شناسه: {document_id}\n\n"
                f"✅ Document deleted successfully!"
            )
        else:
            return (
                f"❌ **خطا در حذف سند.**\n\n"
                f"Error deleting document: {document_id}"
            )
    
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        return f"❌ خطا در حذف سند: {str(e)}\n(Error deleting document)"


@tool
def get_document_info_tool(document_id: str) -> str:
    """
    Get detailed information about a specific document.
    
    Args:
        document_id: The unique identifier of the document. REQUIRED.
        
    Returns:
        Detailed document information
    """
    try:
        vector_store = get_vector_store()
        doc_info = vector_store.get_document_info(document_id)
        
        if not doc_info:
            return (
                f"❌ **سند با شناسه '{document_id}' پیدا نشد.**\n\n"
                f"Document not found: {document_id}"
            )
        
        result = "📄 **اطلاعات سند:**\n\n"
        result += f"📄 **نام:** {doc_info['document_name']}\n"
        result += f"🆔 **شناسه:** {doc_info['document_id']}\n"
        result += f"📝 **فرمت:** {doc_info['file_extension']}\n"
        result += f"📑 **صفحات:** {doc_info.get('total_pages', 'N/A')}\n"
        result += f"🧩 **تعداد بخش‌ها:** {doc_info.get('chunk_count', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting document info: {str(e)}")
        return f"❌ خطا: {str(e)}"


# ===================== QUERY TOOLS =====================

@tool
def query_document_tool(
    question: str,
    document_id: Optional[str] = None
) -> str:
    """
    Ask a question about one or all documents in the database.
    The agent will retrieve relevant information and provide an answer in Farsi.
    
    Args:
        question: The question to ask about the document(s). REQUIRED.
        document_id: Specific document to search (optional, searches all if not provided). OPTIONAL.
        
    Returns:
        Answer based on document content in fluent Farsi
        
    Note: The answer will be generated based on the most relevant sections of the document(s).
    """
    try:
        vector_store = get_vector_store()
        
        # Search for relevant chunks
        results = vector_store.search(
            query=question,
            document_id=document_id,
            k=4
        )
        
        if not results:
            if document_id:
                return (
                    f"❌ **اطلاعاتی برای این سوال در سند مشخص شده یافت نشد.**\n\n"
                    f"No relevant information found in document: {document_id}"
                )
            else:
                return (
                    "❌ **اطلاعاتی برای این سوال یافت نشد.**\n\n"
                    "هیچ سندی در پایگاه داده وجود ندارد یا سوال شما مرتبط نیست.\n\n"
                    "No relevant information found."
                )
        
        # Combine context from results
        context = "\n\n---\n\n".join([doc.page_content for doc in results])
        
        # Get source documents
        sources = list(set([doc.metadata.get('document_name', 'Unknown') for doc in results]))
        
        return (
            f"🔍 **اطلاعات یافت شده:**\n\n"
            f"{context}\n\n"
            f"📚 **منابع:** {', '.join(sources)}\n\n"
            f"💡 Based on the above information from the document(s)."
        )
    
    except Exception as e:
        logger.error(f"Error querying document: {str(e)}")
        return f"❌ خطا در جستجو: {str(e)}\n(Error querying document)"


@tool
def summarize_document_tool(document_id: str) -> str:
    """
    Generate an intelligent summary of a document in Farsi.
    Extracts important information including:
    - Dates and deadlines
    - Financial data and amounts
    - Guidelines and rules
    - Sensitive or important keywords
    
    Args:
        document_id: The unique identifier of the document to summarize. REQUIRED.
        
    Returns:
        Comprehensive summary in fluent Farsi with extracted important data
        
    Note: The summary will be professional and focus on key information.
    """
    try:
        vector_store = get_vector_store()
        
        # Check if document exists
        doc_info = vector_store.get_document_info(document_id)
        if not doc_info:
            return (
                f"❌ **سند با شناسه '{document_id}' پیدا نشد.**\n\n"
                f"Document not found: {document_id}"
            )
        
        # Get all chunks for this document
        all_chunks = vector_store.search(
            query="خلاصه کل محتوا summary entire content",  # Broad query to get all chunks
            document_id=document_id,
            k=20  # Get more chunks for complete summary
        )
        
        if not all_chunks:
            return (
                f"❌ **محتوای سند یافت نشد.**\n\n"
                f"No content found for document: {document_id}"
            )
        
        # Combine all text
        full_text = "\n\n".join([chunk.page_content for chunk in all_chunks])
        
        # Extract important information
        important_info = IntelligentExtractor.extract_important_info(full_text)
        
        # Build summary
        summary = f"📄 **خلاصه سند: {doc_info['document_name']}**\n\n"
        summary += f"🆔 **شناسه:** {document_id}\n"
        summary += f"📝 **فرمت:** {doc_info['file_extension']}\n"
        summary += f"📑 **صفحات:** {doc_info.get('total_pages', 'N/A')}\n\n"
        
        summary += "=" * 50 + "\n\n"
        
        # Dates
        if important_info['dates']:
            summary += "📅 **تاریخ‌ها و مهلت‌ها:**\n"
            for date in important_info['dates'][:10]:  # Limit to 10
                summary += f"   • {date}\n"
            summary += "\n"
        
        # Financial data
        if important_info['financial_data']:
            summary += "💰 **اطلاعات مالی:**\n"
            for item in important_info['financial_data'][:10]:
                summary += f"   • {item}\n"
            summary += "\n"
        
        # Guidelines
        if important_info['guidelines']:
            summary += "📋 **دستورالعمل‌ها و قوانین:**\n"
            for guideline in important_info['guidelines'][:10]:
                summary += f"   • {guideline}\n"
            summary += "\n"
        
        # Sensitive keywords
        if important_info['sensitive_keywords']:
            summary += "🔑 **کلمات کلیدی مهم:**\n"
            summary += f"   {', '.join(important_info['sensitive_keywords'])}\n\n"
        
        summary += "=" * 50 + "\n\n"
        
        # Content preview
        summary += "📝 **پیش‌نمایش محتوا:**\n\n"
        preview = full_text[:1000]  # First 1000 chars
        summary += f"{preview}...\n\n"
        
        summary += f"💡 **توجه:** این خلاصه به صورت هوشمند از سند استخراج شده است.\n"
        summary += "برای اطلاعات بیشتر، می‌توانید سوالات خود را بپرسید.\n\n"
        summary += "✅ **Summary generated successfully!**"
        
        return summary
    
    except Exception as e:
        logger.error(f"Error summarizing document: {str(e)}")
        return f"❌ خطا در ایجاد خلاصه: {str(e)}\n(Error generating summary)"


# Export all tools
ALL_RAG_TOOLS = [
    upload_document_tool,
    list_documents_tool,
    delete_document_tool,
    get_document_info_tool,
    query_document_tool,
    summarize_document_tool
]

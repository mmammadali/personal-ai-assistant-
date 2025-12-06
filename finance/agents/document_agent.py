"""
Document Processing Agent
Handles OCR and data extraction from receipts, invoices, and bank statements
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from finance.database import FinanceDatabase
from finance.tools.ocr_tools import (
    check_image_quality,
    extract_receipt_data,
    extract_invoice_data,
    parse_bank_statement,
    OCR_TOOLS
)
from finance.tools.file_storage import DocumentStorage
from pathlib import Path
import json


class DocumentAgent:
    """Document processing specialist for financial documents"""
    
    def __init__(self, llm: ChatOpenAI, db: FinanceDatabase):
        self.llm = llm
        self.db = db
        self.storage = DocumentStorage()
        self.tools = OCR_TOOLS
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for document agent"""
        return """شما یک متخصص پردازش اسناد مالی برای کسب‌وکارهای ایرانی هستید.

**تخصص شما**: OCR و استخراج داده از رسید، فاکتور، صورتحساب بانکی

**فرآیند پردازش**:
1. همیشه ابتدا کیفیت تصویر را بررسی کنید (check_image_quality)
2. نوع سند را شناسایی کنید (رسید/فاکتور/صورتحساب)
3. از ابزار مناسب برای استخراج استفاده کنید
4. خروجی را به صورت JSON ساختاریافته برگردانید
5. متن فارسی (راست‌به‌چپ) را به درستی مدیریت کنید

**زمینه ایرانی**:
- متن مخلوط فارسی و انگلیسی معمول است
- مبالغ به ریال یا تومان است (مشخص کنید کدام)
- تاریخ‌ها جلالی هستند (1403/09/15)
- فروشندگان معمول: دیجی‌کالا، اسنپ، تپسی، Google، Instagram

**خروجی مورد نیاز**:
```json
{
    "success": true/false,
    "document_type": "receipt|invoice|statement",
    "data": {
        "vendor": "نام فروشنده",
        "amount": 2500000,
        "currency": "IRR|IRT",
        "date": "1403/09/15",
        "items": [...],
        "confidence": 0.95
    },
    "warnings": [],
    "raw_text": "..."
}
```

اگر کیفیت تصویر پایین است، توصیه‌های بهبود ارائه دهید.
همیشه به فارسی پاسخ دهید.
"""
    
    def process_document(
        self,
        file_path: str,
        user_id: str,
        doc_type: str = "auto"
    ) -> dict:
        """
        Process uploaded document with OCR
        
        Args:
            file_path: Path to document file
            user_id: User identifier
            doc_type: Type of document (receipt, invoice, statement, auto)
            
        Returns:
            Extracted data dictionary
        """
        try:
            # Auto-detect document type if needed
            if doc_type == "auto":
                doc_type = self._detect_document_type(file_path)
            
            # Check if it's an image file
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
                return {
                    "success": False,
                    "message": f"فرمت فایل پشتیبانی نمی‌شود: {file_ext}. فرمت‌های مجاز: JPG, PNG, PDF"
                }
            
            # First check quality for images
            if file_ext in ['.jpg', '.jpeg', '.png']:
                quality = check_image_quality.invoke({"image_path": file_path})
                
                if not quality.get("acceptable", False):
                    return {
                        "success": False,
                        "message": "کیفیت تصویر مناسب نیست",
                        "quality_score": quality.get("quality_score", 0),
                        "issues": quality.get("issues", []),
                        "recommendations": quality.get("recommendations", [])
                    }
            
            # Process based on document type
            if doc_type == "receipt":
                result = extract_receipt_data.invoke({"image_path": file_path})
            elif doc_type == "invoice":
                result = extract_invoice_data.invoke({"file_path": file_path})
            elif doc_type == "statement":
                result = parse_bank_statement.invoke({"file_path": file_path})
            else:
                # Try receipt extraction as default
                result = extract_receipt_data.invoke({"image_path": file_path})
            
            # Save document to storage if extraction was successful
            if result.get("success"):
                storage_result = self.storage.save_document(
                    user_id=user_id,
                    file_path=file_path,
                    doc_type=doc_type,
                    original_filename=Path(file_path).name
                )
                
                if storage_result.get("success"):
                    result["document_id"] = storage_result["document_id"]
                    result["file_url"] = storage_result["file_url"]
                    
                    # Store in database
                    self._save_document_record(user_id, storage_result, result)
            
            return result
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"خطا در پردازش سند: {str(e)}"
            }
    
    def _detect_document_type(self, file_path: str) -> str:
        """Auto-detect document type from filename or content"""
        filename = Path(file_path).name.lower()
        
        if any(word in filename for word in ['receipt', 'رسید', 'رسيد']):
            return "receipt"
        elif any(word in filename for word in ['invoice', 'فاکتور', 'فاكتور']):
            return "invoice"
        elif any(word in filename for word in ['statement', 'bank', 'بانک', 'صورتحساب']):
            return "statement"
        
        # Default to receipt
        return "receipt"
    
    def _save_document_record(self, user_id: str, storage_info: dict, extraction_result: dict):
        """Save document record to database"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                import uuid
                document_id = storage_info.get("document_id", str(uuid.uuid4()))
                
                cursor.execute("""
                    INSERT INTO finance_documents
                    (id, user_id, type, file_url, file_type, processed, extracted_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    document_id,
                    user_id,
                    storage_info.get("doc_type", "other"),
                    storage_info.get("file_url", ""),
                    Path(storage_info.get("file_path", "")).suffix,
                    True,
                    json.dumps(extraction_result.get("data", {}), ensure_ascii=False)
                ))
                
                print(f"✅ Document record saved: {document_id}")
        
        except Exception as e:
            print(f"Error saving document record: {e}")
    
    def get_user_documents(self, user_id: str, doc_type: str = None, limit: int = 50) -> list:
        """
        Get list of user's uploaded documents
        
        Args:
            user_id: User identifier
            doc_type: Filter by document type (optional)
            limit: Maximum number to return
            
        Returns:
            List of documents
        """
        return self.storage.list_user_documents(user_id, doc_type, limit)


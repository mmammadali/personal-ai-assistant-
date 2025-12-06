"""
File Storage Management
Handles document uploads and retrieval for finance documents
"""
from pathlib import Path
from datetime import datetime
import uuid
import shutil
from typing import Optional, Dict, Any


class DocumentStorage:
    """Manages finance document uploads and storage"""
    
    def __init__(self, base_path: str = "finance_uploads"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def save_document(
        self,
        user_id: str,
        file_path: str,
        doc_type: str = "other",
        original_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save uploaded document
        
        Args:
            user_id: User identifier
            file_path: Path to uploaded file
            doc_type: Type of document (receipt, invoice, statement, other)
            original_filename: Original filename
            
        Returns:
            Document information with saved path and document_id
        """
        try:
            # Create user directory structure
            today = datetime.now()
            user_dir = self.base_path / user_id / doc_type / f"{today.year}" / f"{today.month:02d}"
            user_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            document_id = str(uuid.uuid4())
            file_extension = Path(file_path).suffix
            if not original_filename:
                original_filename = Path(file_path).name
            
            safe_filename = f"{document_id}{file_extension}"
            destination = user_dir / safe_filename
            
            # Copy file to destination
            shutil.copy2(file_path, destination)
            
            return {
                "success": True,
                "document_id": document_id,
                "file_path": str(destination),
                "file_url": f"/finance_uploads/{user_id}/{doc_type}/{today.year}/{today.month:02d}/{safe_filename}",
                "original_filename": original_filename,
                "doc_type": doc_type,
                "upload_date": today.isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"خطا در ذخیره سند: {str(e)}"
            }
    
    def get_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve document information
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            
        Returns:
            Document information or None if not found
        """
        # Search for document in user's directory
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return None
        
        # Search recursively for document
        for file_path in user_dir.rglob(f"{document_id}.*"):
            return {
                "document_id": document_id,
                "file_path": str(file_path),
                "exists": True
            }
        
        return None
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete document file
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        doc_info = self.get_document(document_id, user_id)
        if doc_info and doc_info.get("exists"):
            try:
                Path(doc_info["file_path"]).unlink()
                return True
            except Exception as e:
                print(f"Error deleting document: {e}")
                return False
        return False
    
    def list_user_documents(
        self,
        user_id: str,
        doc_type: Optional[str] = None,
        limit: int = 50
    ) -> list:
        """
        List user's uploaded documents
        
        Args:
            user_id: User identifier
            doc_type: Filter by document type (optional)
            limit: Maximum number of documents to return
            
        Returns:
            List of document information
        """
        user_dir = self.base_path / user_id
        if not user_dir.exists():
            return []
        
        documents = []
        search_dir = user_dir / doc_type if doc_type else user_dir
        
        if search_dir.exists():
            for file_path in search_dir.rglob("*.*"):
                if file_path.is_file():
                    documents.append({
                        "file_path": str(file_path),
                        "filename": file_path.name,
                        "doc_type": file_path.parent.parent.parent.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                    
                    if len(documents) >= limit:
                        break
        
        return sorted(documents, key=lambda x: x["modified"], reverse=True)


"""
🔥 Vector Database Abstraction Layer
Unified interface for ChromaDB (local) and Pinecone (cloud)
Supports easy migration between backends
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pathlib import Path
import uuid
from datetime import datetime

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

import rag_agent_config as config


class VectorStoreBase(ABC):
    """Abstract base class for vector store operations"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document], document_id: str, metadata: Dict[str, Any]) -> None:
        """Add documents to vector store with metadata"""
        pass
    
    @abstractmethod
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document"""
        pass
    
    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the vector store"""
        pass
    
    @abstractmethod
    def get_document_count(self) -> int:
        """Get total number of documents"""
        pass


class ChromaDBVectorStore(VectorStoreBase):
    """ChromaDB implementation - Local/Development"""
    
    def __init__(self):
        """Initialize ChromaDB vector store"""
        self.persist_dir = Path(config.CHROMADB_PERSIST_DIR)
        self.persist_dir.mkdir(exist_ok=True, parents=True)
        
        self.collection_name = config.CHROMADB_COLLECTION_NAME
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Initialize ChromaDB
        self.vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.persist_dir)
        )
        
        print(f"✅ ChromaDB initialized at: {self.persist_dir}")
    
    def add_documents(self, documents: List[Document], document_id: str, metadata: Dict[str, Any]) -> None:
        """Add documents to ChromaDB with metadata"""
        try:
            # Add document_id and metadata to all chunks
            for doc in documents:
                doc.metadata.update({
                    "document_id": document_id,
                    "filename": metadata.get("filename", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "upload_date": metadata.get("upload_date", datetime.now().isoformat()),
                    "file_size": metadata.get("file_size", 0),
                    "total_chunks": len(documents)
                })
            
            # Add to vector store
            self.vectorstore.add_documents(documents)
            
            print(f"✅ Added {len(documents)} chunks for document: {metadata.get('filename')}")
        
        except Exception as e:
            print(f"❌ Error adding documents to ChromaDB: {e}")
            raise
    
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search ChromaDB for similar documents"""
        try:
            if filter_dict:
                # ChromaDB filtering
                results = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = self.vectorstore.similarity_search(query, k=k)
            
            return results
        
        except Exception as e:
            print(f"❌ Error searching ChromaDB: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document from ChromaDB"""
        try:
            # Get the collection
            collection = self.vectorstore._collection
            
            # Delete all documents with this document_id
            collection.delete(
                where={"document_id": document_id}
            )
            
            print(f"✅ Deleted document: {document_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting document from ChromaDB: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents in ChromaDB"""
        try:
            # Get all documents
            collection = self.vectorstore._collection
            results = collection.get()
            
            if not results or not results['metadatas']:
                return []
            
            # Extract unique documents by document_id
            documents_dict = {}
            for metadata in results['metadatas']:
                doc_id = metadata.get('document_id')
                if doc_id and doc_id not in documents_dict:
                    documents_dict[doc_id] = {
                        'document_id': doc_id,
                        'filename': metadata.get('filename', 'Unknown'),
                        'file_type': metadata.get('file_type', 'Unknown'),
                        'upload_date': metadata.get('upload_date', 'Unknown'),
                        'file_size': metadata.get('file_size', 0),
                        'total_chunks': metadata.get('total_chunks', 0)
                    }
            
            # Sort by upload date (newest first)
            documents_list = sorted(
                documents_dict.values(),
                key=lambda x: x['upload_date'],
                reverse=True
            )
            
            return documents_list
        
        except Exception as e:
            print(f"❌ Error listing documents from ChromaDB: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get number of unique documents"""
        return len(self.list_documents())


class PineconeVectorStore(VectorStoreBase):
    """Pinecone implementation - Cloud/Production"""
    
    def __init__(self):
        """Initialize Pinecone vector store"""
        try:
            from langchain_pinecone import PineconeVectorStore as PineconeVS
            import pinecone
            
            # Initialize Pinecone
            pinecone.init(
                api_key=config.PINECONE_API_KEY,
                environment=config.PINECONE_ENVIRONMENT
            )
            
            self.index_name = config.PINECONE_INDEX_NAME
            self.embeddings = OpenAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                openai_api_key=config.OPENAI_API_KEY
            )
            
            # Check if index exists, create if not
            if self.index_name not in pinecone.list_indexes():
                print(f"Creating Pinecone index: {self.index_name}")
                pinecone.create_index(
                    name=self.index_name,
                    dimension=1536 if "small" in config.EMBEDDING_MODEL else 3072,
                    metric="cosine"
                )
            
            # Initialize vector store
            self.vectorstore = PineconeVS(
                index_name=self.index_name,
                embedding=self.embeddings
            )
            
            print(f"✅ Pinecone initialized: {self.index_name}")
        
        except ImportError:
            raise ImportError(
                "Pinecone dependencies not installed. Run: pip install pinecone-client langchain-pinecone"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone: {e}")
    
    def add_documents(self, documents: List[Document], document_id: str, metadata: Dict[str, Any]) -> None:
        """Add documents to Pinecone with metadata"""
        try:
            # Add document_id and metadata to all chunks
            for doc in documents:
                doc.metadata.update({
                    "document_id": document_id,
                    "filename": metadata.get("filename", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "upload_date": metadata.get("upload_date", datetime.now().isoformat()),
                    "file_size": metadata.get("file_size", 0),
                    "total_chunks": len(documents)
                })
            
            # Add to Pinecone with namespace as user_id (for multi-tenancy)
            namespace = metadata.get("user_id", "default")
            self.vectorstore.add_documents(documents, namespace=namespace)
            
            print(f"✅ Added {len(documents)} chunks to Pinecone: {metadata.get('filename')}")
        
        except Exception as e:
            print(f"❌ Error adding documents to Pinecone: {e}")
            raise
    
    def search(self, query: str, k: int = 4, filter_dict: Optional[Dict] = None) -> List[Document]:
        """Search Pinecone for similar documents"""
        try:
            namespace = filter_dict.get("user_id", "default") if filter_dict else "default"
            
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                namespace=namespace,
                filter=filter_dict
            )
            
            return results
        
        except Exception as e:
            print(f"❌ Error searching Pinecone: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document from Pinecone"""
        try:
            # Pinecone delete by metadata filter
            self.vectorstore.delete(filter={"document_id": document_id})
            
            print(f"✅ Deleted document from Pinecone: {document_id}")
            return True
        
        except Exception as e:
            print(f"❌ Error deleting document from Pinecone: {e}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all unique documents in Pinecone"""
        try:
            # Note: Pinecone doesn't have a direct "list all" API
            # You would need to maintain a separate metadata store (e.g., PostgreSQL)
            # For now, return empty list with a note
            print("⚠️  Pinecone list_documents requires separate metadata store")
            return []
        
        except Exception as e:
            print(f"❌ Error listing documents from Pinecone: {e}")
            return []
    
    def get_document_count(self) -> int:
        """Get number of unique documents"""
        return len(self.list_documents())


# ==================== FACTORY FUNCTION ====================

def get_vector_store() -> VectorStoreBase:
    """
    Factory function to get the appropriate vector store based on config
    Returns ChromaDB or Pinecone instance
    """
    if config.VECTOR_DB_TYPE == "chromadb":
        return ChromaDBVectorStore()
    elif config.VECTOR_DB_TYPE == "pinecone":
        return PineconeVectorStore()
    else:
        raise ValueError(f"Unknown vector database type: {config.VECTOR_DB_TYPE}")


# ==================== SINGLETON INSTANCE ====================

# Global vector store instance (lazy initialization)
_vector_store_instance: Optional[VectorStoreBase] = None

def get_vector_store_instance() -> VectorStoreBase:
    """Get or create singleton vector store instance"""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = get_vector_store()
    return _vector_store_instance


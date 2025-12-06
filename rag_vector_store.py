"""
Vector Database Manager for RAG Agent
Supports both ChromaDB (local) and Pinecone (cloud) with easy switching
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
from pathlib import Path

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try to import ChromaDB (optional)
try:
    from langchain_chroma import Chroma
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    logger.warning("ChromaDB not available, using in-memory vector store")

# Try to import Pinecone (optional)
try:
    from langchain_pinecone import PineconeVectorStore
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

# Try to import FAISS (optional)
try:
    from langchain_community.vectorstores import FAISS
    import faiss as faiss_lib
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


class VectorStoreBase(ABC):
    """Abstract base class for vector stores"""
    
    @abstractmethod
    def add_documents(self, documents: List[Document], document_id: str) -> int:
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    def search(self, query: str, document_id: Optional[str] = None, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        pass
    
    @abstractmethod
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents"""
        pass
    
    @abstractmethod
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a document"""
        pass


class ChromaDBStore(VectorStoreBase):
    """ChromaDB implementation - local, persistent, free"""
    
    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: str = "./chroma_db",
        embeddings: Optional[Any] = None
    ):
        """
        Initialize ChromaDB vector store
        
        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist data
            embeddings: Embeddings model (defaults to OpenAI)
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize vector store
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
        
        logger.info(f"ChromaDB initialized at {self.persist_directory}")
    
    def add_documents(self, documents: List[Document], document_id: str) -> int:
        """
        Add documents to ChromaDB
        
        Args:
            documents: List of Document objects
            document_id: Unique document identifier
            
        Returns:
            Number of documents added
        """
        # Add document_id to all chunks
        for doc in documents:
            doc.metadata["document_id"] = document_id
        
        # Add to vector store
        self.vectorstore.add_documents(documents)
        
        logger.info(f"Added {len(documents)} chunks for document '{document_id}'")
        return len(documents)
    
    def search(
        self,
        query: str,
        document_id: Optional[str] = None,
        k: int = 4
    ) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            document_id: Filter by document ID (optional)
            k: Number of results to return
            
        Returns:
            List of similar Document objects
        """
        if document_id:
            # Search with filter
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter={"document_id": document_id}
            )
        else:
            # Search across all documents
            results = self.vectorstore.similarity_search(query, k=k)
        
        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if successful
        """
        try:
            # Get the collection
            collection = self.client.get_collection(self.collection_name)
            
            # Get all IDs for this document
            results = collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # Delete by IDs
                collection.delete(ids=results['ids'])
                logger.info(f"Deleted {len(results['ids'])} chunks for document '{document_id}'")
                return True
            else:
                logger.warning(f"No chunks found for document '{document_id}'")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the collection
        
        Returns:
            List of document information dictionaries
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            
            # Get all metadata
            results = collection.get(include=["metadatas"])
            
            # Extract unique documents
            documents_map = {}
            for metadata in results.get('metadatas', []):
                doc_id = metadata.get('document_id')
                if doc_id and doc_id not in documents_map:
                    documents_map[doc_id] = {
                        'document_id': doc_id,
                        'document_name': metadata.get('document_name', doc_id),
                        'file_extension': metadata.get('file_extension', 'unknown'),
                        'total_pages': metadata.get('total_pages', 0),
                    }
            
            return list(documents_map.values())
        
        except Exception as e:
            logger.error(f"Error listing documents: {str(e)}")
            return []
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document information or None
        """
        try:
            collection = self.client.get_collection(self.collection_name)
            
            results = collection.get(
                where={"document_id": document_id},
                include=["metadatas"]
            )
            
            if results['metadatas']:
                metadata = results['metadatas'][0]
                return {
                    'document_id': document_id,
                    'document_name': metadata.get('document_name', document_id),
                    'file_extension': metadata.get('file_extension', 'unknown'),
                    'total_pages': metadata.get('total_pages', 0),
                    'chunk_count': len(results['metadatas'])
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return None


class PineconeStore(VectorStoreBase):
    """Pinecone implementation - cloud, scalable, multi-tenant ready"""
    
    def __init__(
        self,
        index_name: str = "rag-documents",
        namespace: str = "default",
        api_key: Optional[str] = None,
        embeddings: Optional[Any] = None
    ):
        """
        Initialize Pinecone vector store
        
        Args:
            index_name: Pinecone index name
            namespace: Namespace for multi-tenancy
            api_key: Pinecone API key
            embeddings: Embeddings model
        """
        try:
            from pinecone import Pinecone
        except ImportError:
            raise ImportError("Please install pinecone-client: pip install pinecone-client")
        
        self.index_name = index_name
        self.namespace = namespace
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=api_key)
        self.index = pc.Index(index_name)
        
        # Initialize vector store
        self.vectorstore = PineconeVectorStore(
            index=self.index,
            embedding=self.embeddings,
            namespace=namespace
        )
        
        logger.info(f"Pinecone initialized: {index_name}/{namespace}")
    
    def add_documents(self, documents: List[Document], document_id: str) -> int:
        """Add documents to Pinecone"""
        for doc in documents:
            doc.metadata["document_id"] = document_id
        
        self.vectorstore.add_documents(documents)
        logger.info(f"Added {len(documents)} chunks to Pinecone for '{document_id}'")
        return len(documents)
    
    def search(
        self,
        query: str,
        document_id: Optional[str] = None,
        k: int = 4
    ) -> List[Document]:
        """Search Pinecone"""
        if document_id:
            results = self.vectorstore.similarity_search(
                query,
                k=k,
                filter={"document_id": document_id}
            )
        else:
            results = self.vectorstore.similarity_search(query, k=k)
        
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """Delete document from Pinecone"""
        try:
            self.index.delete(
                filter={"document_id": document_id},
                namespace=self.namespace
            )
            logger.info(f"Deleted document '{document_id}' from Pinecone")
            return True
        except Exception as e:
            logger.error(f"Error deleting from Pinecone: {str(e)}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List documents in Pinecone"""
        # Note: Pinecone doesn't have native list capability
        # Would need to maintain separate metadata store
        logger.warning("list_documents not fully implemented for Pinecone")
        return []
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document info from Pinecone"""
        logger.warning("get_document_info not fully implemented for Pinecone")
        return None


class FAISSStore(VectorStoreBase):
    """FAISS implementation - local, fast, Python 3.14 compatible"""
    
    def __init__(
        self,
        collection_name: str = "rag_documents",
        persist_directory: str = "./faiss_db",
        embeddings: Optional[Any] = None
    ):
        """
        Initialize FAISS vector store
        
        Args:
            collection_name: Name of the collection (used for file naming)
            persist_directory: Directory to persist data
            embeddings: Embeddings model (defaults to OpenAI)
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = embeddings or OpenAIEmbeddings(model="text-embedding-3-large")
        
        # FAISS index path
        self.index_path = self.persist_directory / f"{collection_name}.faiss"
        self.metadata_path = self.persist_directory / f"{collection_name}_metadata.pkl"
        
        # Load or create FAISS index
        if self.index_path.exists():
            try:
                self.vectorstore = FAISS.load_local(
                    str(self.persist_directory),
                    self.embeddings,
                    collection_name,
                    allow_dangerous_deserialization=True
                )
                logger.info(f"Loaded existing FAISS index from {self.index_path}")
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}. Creating new index.")
                self.vectorstore = None
        else:
            self.vectorstore = None
        
        # Track documents metadata separately
        self.documents_metadata = self._load_metadata()
        
        logger.info(f"FAISS initialized at {self.persist_directory}")
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata from disk"""
        if self.metadata_path.exists():
            try:
                import pickle
                with open(self.metadata_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Could not load metadata: {e}")
        return {}
    
    def _save_metadata(self):
        """Save metadata to disk"""
        try:
            import pickle
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.documents_metadata, f)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def add_documents(self, documents: List[Document], document_id: str) -> int:
        """
        Add documents to FAISS
        
        Args:
            documents: List of Document objects
            document_id: Unique document identifier
            
        Returns:
            Number of documents added
        """
        # Add document_id to all chunks
        for doc in documents:
            doc.metadata["document_id"] = document_id
        
        # Create or update vector store
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vectorstore.add_documents(documents)
        
        # Save to disk
        self.vectorstore.save_local(str(self.persist_directory), self.collection_name)
        
        # Update metadata
        if documents:
            first_doc = documents[0].metadata
            self.documents_metadata[document_id] = {
                'document_id': document_id,
                'document_name': first_doc.get('document_name', document_id),
                'file_extension': first_doc.get('file_extension', 'unknown'),
                'total_pages': first_doc.get('total_pages', 0),
                'chunk_count': len(documents)
            }
            self._save_metadata()
        
        logger.info(f"Added {len(documents)} chunks for document '{document_id}'")
        return len(documents)
    
    def search(
        self,
        query: str,
        document_id: Optional[str] = None,
        k: int = 4
    ) -> List[Document]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            document_id: Filter by document ID (optional)
            k: Number of results to return
            
        Returns:
            List of similar Document objects
        """
        if self.vectorstore is None:
            logger.warning("No documents in vector store yet")
            return []
        
        # Search
        results = self.vectorstore.similarity_search(query, k=k*2 if document_id else k)
        
        # Filter by document_id if specified
        if document_id:
            results = [doc for doc in results if doc.metadata.get('document_id') == document_id][:k]
        
        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete all chunks of a document
        
        Note: FAISS doesn't support deletion, so we rebuild the index without the document
        
        Args:
            document_id: Document identifier
            
        Returns:
            True if successful
        """
        if self.vectorstore is None:
            return False
        
        try:
            # Get all documents from the index
            all_docs = []
            docstore = self.vectorstore.docstore
            
            for doc_id in docstore._dict.keys():
                doc = docstore._dict[doc_id]
                if doc.metadata.get('document_id') != document_id:
                    all_docs.append(doc)
            
            if all_docs:
                # Rebuild index without the deleted document
                self.vectorstore = FAISS.from_documents(all_docs, self.embeddings)
                self.vectorstore.save_local(str(self.persist_directory), self.collection_name)
            else:
                # No documents left
                self.vectorstore = None
                if self.index_path.exists():
                    import shutil
                    shutil.rmtree(self.persist_directory, ignore_errors=True)
                    self.persist_directory.mkdir(parents=True, exist_ok=True)
            
            # Remove from metadata
            if document_id in self.documents_metadata:
                del self.documents_metadata[document_id]
                self._save_metadata()
            
            logger.info(f"Deleted document '{document_id}'")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the collection
        
        Returns:
            List of document information dictionaries
        """
        return list(self.documents_metadata.values())
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific document
        
        Args:
            document_id: Document identifier
            
        Returns:
            Document information or None
        """
        return self.documents_metadata.get(document_id)


class VectorStoreManager:
    """
    Factory class for vector store creation
    Easily switch between ChromaDB and Pinecone via config
    """
    
    @staticmethod
    def create(
        store_type: str = "chromadb",
        **kwargs
    ) -> VectorStoreBase:
        """
        Create a vector store instance
        
        Args:
            store_type: "chromadb", "faiss", or "pinecone"
            **kwargs: Store-specific arguments
            
        Returns:
            Vector store instance
        """
        store_type_lower = store_type.lower()
        
        if store_type_lower == "chromadb":
            if not CHROMADB_AVAILABLE:
                raise ImportError("ChromaDB not available. Install with: pip install chromadb langchain-chroma")
            return ChromaDBStore(**kwargs)
        
        elif store_type_lower == "faiss":
            if not FAISS_AVAILABLE:
                raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
            return FAISSStore(**kwargs)
        
        elif store_type_lower == "pinecone":
            if not PINECONE_AVAILABLE:
                raise ImportError("Pinecone not available. Install with: pip install pinecone-client langchain-pinecone")
            return PineconeStore(**kwargs)
        
        else:
            raise ValueError(f"Unknown vector store type: {store_type}. Supported: chromadb, faiss, pinecone")


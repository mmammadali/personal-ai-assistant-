"""
Vector Store Manager - Abstraction Layer for ChromaDB and Pinecone
Allows seamless switching between local (ChromaDB) and cloud (Pinecone) vector databases
"""
import os
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import config


class VectorStoreManager:
    """
    Unified interface for vector database operations.
    Supports both ChromaDB (local) and Pinecone (cloud).
    """
    
    def __init__(self, user_id: Optional[str] = None):
        """
        Initialize vector store manager.
        
        Args:
            user_id: User identifier for multi-tenancy (required for Pinecone)
        """
        self.user_id = user_id or "default_user"
        self.db_type = config.VECTOR_DB_TYPE.lower()
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            openai_api_key=config.OPENAI_API_KEY
        )
        
        # Initialize appropriate vector store
        if self.db_type == "chromadb":
            self._init_chromadb()
        elif self.db_type == "pinecone":
            self._init_pinecone()
        else:
            raise ValueError(f"Unsupported vector database type: {self.db_type}")
    
    def _init_chromadb(self):
        """Initialize ChromaDB (local storage)."""
        print(f"🔵 Initializing ChromaDB (Local Storage)")
        print(f"   Persist Directory: {config.CHROMA_PERSIST_DIR}")
        
        # Create persist directory if it doesn't exist
        os.makedirs(config.CHROMA_PERSIST_DIR, exist_ok=True)
        
        # Initialize ChromaDB with persistence
        self.vectorstore = Chroma(
            collection_name=config.CHROMA_COLLECTION_NAME,
            embedding_function=self.embeddings,
            persist_directory=config.CHROMA_PERSIST_DIR,
        )
        print(f"✅ ChromaDB initialized successfully")
    
    def _init_pinecone(self):
        """Initialize Pinecone (cloud storage)."""
        print(f"🟣 Initializing Pinecone (Cloud Storage)")
        
        # Check if Pinecone API key is configured
        if not config.PINECONE_API_KEY:
            raise ValueError(
                "Pinecone API key not configured. "
                "Set PINECONE_API_KEY in your .env file."
            )
        
        try:
            from langchain_pinecone import PineconeVectorStore
            from pinecone import Pinecone, ServerlessSpec
            
            # Initialize Pinecone client
            pc = Pinecone(api_key=config.PINECONE_API_KEY)
            
            # Create index if it doesn't exist
            index_name = config.PINECONE_INDEX_NAME
            existing_indexes = [index.name for index in pc.list_indexes()]
            
            if index_name not in existing_indexes:
                print(f"   Creating new Pinecone index: {index_name}")
                pc.create_index(
                    name=index_name,
                    dimension=3072,  # text-embedding-3-large dimension
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            # Initialize vector store with namespace for user isolation
            self.vectorstore = PineconeVectorStore(
                index_name=index_name,
                embedding=self.embeddings,
                namespace=self.user_id,  # User isolation
                pinecone_api_key=config.PINECONE_API_KEY
            )
            print(f"✅ Pinecone initialized successfully (namespace: {self.user_id})")
            
        except ImportError:
            raise ImportError(
                "Pinecone dependencies not installed. "
                "Run: pip install pinecone-client langchain-pinecone"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Pinecone: {str(e)}")
    
    def add_documents(
        self, 
        documents: List[Document], 
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Add documents to vector store.
        
        Args:
            documents: List of Document objects to add
            doc_id: Unique document identifier
            metadata: Additional metadata to attach
            
        Returns:
            List of IDs of added vectors
        """
        try:
            # Add doc_id and user_id to all document metadata
            for doc in documents:
                doc.metadata["doc_id"] = doc_id
                doc.metadata["user_id"] = self.user_id
                if metadata:
                    doc.metadata.update(metadata)
            
            # Add to vector store
            ids = self.vectorstore.add_documents(documents)
            
            print(f"✅ Added {len(documents)} chunks from document '{doc_id}'")
            return ids
            
        except Exception as e:
            print(f"❌ Error adding documents: {str(e)}")
            raise
    
    def similarity_search(
        self, 
        query: str, 
        k: int = None,
        doc_id: Optional[str] = None
    ) -> List[Document]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return (default from config)
            doc_id: Optional document ID to filter results
            
        Returns:
            List of relevant documents
        """
        try:
            k = k or config.RETRIEVAL_TOP_K
            
            # Build filter for user isolation and optional doc_id
            filter_dict = {"user_id": self.user_id}
            if doc_id:
                filter_dict["doc_id"] = doc_id
            
            # Perform search
            if self.db_type == "chromadb":
                results = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:  # Pinecone - namespace already isolates users
                if doc_id:
                    results = self.vectorstore.similarity_search(
                        query,
                        k=k,
                        filter={"doc_id": doc_id}
                    )
                else:
                    results = self.vectorstore.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            print(f"❌ Error during similarity search: {str(e)}")
            raise
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all vectors associated with a document.
        
        Args:
            doc_id: Document identifier to delete
            
        Returns:
            True if successful
        """
        try:
            if self.db_type == "chromadb":
                # ChromaDB: Delete by metadata filter
                self.vectorstore.delete(
                    filter={"doc_id": doc_id, "user_id": self.user_id}
                )
            else:
                # Pinecone: Delete by metadata filter (within namespace)
                self.vectorstore.delete(
                    filter={"doc_id": doc_id}
                )
            
            print(f"✅ Deleted document '{doc_id}'")
            return True
            
        except Exception as e:
            print(f"❌ Error deleting document: {str(e)}")
            return False
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all documents in the vector store for current user.
        
        Returns:
            List of document metadata dictionaries
        """
        try:
            if self.db_type == "chromadb":
                # ChromaDB: Get all documents for this user
                collection = self.vectorstore._collection
                results = collection.get(
                    where={"user_id": self.user_id},
                    include=["metadatas"]
                )
                
                # Extract unique documents
                doc_dict = {}
                for metadata in results.get("metadatas", []):
                    doc_id = metadata.get("doc_id")
                    if doc_id and doc_id not in doc_dict:
                        doc_dict[doc_id] = metadata
                
                return list(doc_dict.values())
            
            else:
                # Pinecone: Query with empty vector to get all (limited approach)
                # Note: Pinecone doesn't have a native "list all" operation
                # This is a workaround - in production, maintain a separate metadata DB
                print("⚠️  Pinecone listing is limited. Consider using separate metadata store.")
                return []
            
        except Exception as e:
            print(f"❌ Error listing documents: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """
        Get total number of unique documents for current user.
        
        Returns:
            Number of documents
        """
        try:
            documents = self.list_documents()
            return len(documents)
        except:
            return 0
    
    def clear_all_documents(self) -> bool:
        """
        Delete all documents for current user (use with caution!).
        
        Returns:
            True if successful
        """
        try:
            if self.db_type == "chromadb":
                self.vectorstore.delete(
                    filter={"user_id": self.user_id}
                )
            else:
                # Pinecone: Delete all in namespace
                from pinecone import Pinecone
                pc = Pinecone(api_key=config.PINECONE_API_KEY)
                index = pc.Index(config.PINECONE_INDEX_NAME)
                index.delete(delete_all=True, namespace=self.user_id)
            
            print(f"✅ Cleared all documents for user '{self.user_id}'")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing documents: {str(e)}")
            return False


# Factory function for easy instantiation
def get_vector_store(user_id: Optional[str] = None) -> VectorStoreManager:
    """
    Factory function to get vector store manager.
    
    Args:
        user_id: User identifier (important for multi-tenancy)
        
    Returns:
        VectorStoreManager instance
    """
    return VectorStoreManager(user_id=user_id)


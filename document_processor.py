"""
Document Processor for RAG Agent
Handles multiple document formats: PDF, DOCX, TXT, Excel, PowerPoint, Images
Supports Farsi and English text extraction
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import os
import logging

# LangChain document loaders
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredExcelLoader,
    UnstructuredPowerPointLoader,
    UnstructuredImageLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Universal document processor supporting multiple formats
    with intelligent text chunking and metadata extraction
    """
    
    SUPPORTED_FORMATS = {
        '.pdf': PyPDFLoader,
        '.docx': Docx2txtLoader,
        '.doc': Docx2txtLoader,
        '.txt': TextLoader,
        '.md': TextLoader,
        '.xlsx': UnstructuredExcelLoader,
        '.xls': UnstructuredExcelLoader,
        '.pptx': UnstructuredPowerPointLoader,
        '.ppt': UnstructuredPowerPointLoader,
        '.jpg': UnstructuredImageLoader,
        '.jpeg': UnstructuredImageLoader,
        '.png': UnstructuredImageLoader,
    }
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        encoding: str = 'utf-8'
    ):
        """
        Initialize document processor
        
        Args:
            chunk_size: Size of text chunks for embedding
            chunk_overlap: Overlap between chunks for context preservation
            encoding: Text encoding (utf-8 supports Farsi)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = encoding
        
        # Text splitter optimized for multilingual content
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", "،", "؛", " ", ""]
        )
    
    def detect_format(self, file_path: str) -> str:
        """
        Detect document format from file extension
        
        Args:
            file_path: Path to document
            
        Returns:
            File extension
            
        Raises:
            ValueError: If format is not supported
        """
        ext = Path(file_path).suffix.lower()
        
        if ext not in self.SUPPORTED_FORMATS:
            supported = ", ".join(self.SUPPORTED_FORMATS.keys())
            raise ValueError(
                f"Unsupported file format: {ext}\n"
                f"Supported formats: {supported}"
            )
        
        return ext
    
    def load_document(self, file_path: str) -> List[Document]:
        """
        Load document using appropriate loader based on format
        
        Args:
            file_path: Path to document
            
        Returns:
            List of Document objects
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format is unsupported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Detect format
        ext = self.detect_format(file_path)
        loader_class = self.SUPPORTED_FORMATS[ext]
        
        logger.info(f"Loading document: {file_path} (format: {ext})")
        
        try:
            # Special handling for text files with encoding
            if ext in ['.txt', '.md']:
                loader = loader_class(file_path, encoding=self.encoding)
            else:
                loader = loader_class(file_path)
            
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} document(s)")
            
            return documents
        
        except Exception as e:
            logger.error(f"Error loading document: {str(e)}")
            raise
    
    def chunk_documents(
        self,
        documents: List[Document],
        add_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Split documents into chunks and add metadata
        
        Args:
            documents: List of Document objects
            add_metadata: Additional metadata to add to each chunk
            
        Returns:
            List of chunked Document objects with metadata
        """
        logger.info(f"Chunking {len(documents)} document(s)")
        
        # Split documents
        chunks = self.text_splitter.split_documents(documents)
        
        # Add custom metadata
        if add_metadata:
            for chunk in chunks:
                chunk.metadata.update(add_metadata)
        
        logger.info(f"Created {len(chunks)} chunks")
        
        return chunks
    
    def process_document(
        self,
        file_path: str,
        document_name: Optional[str] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete document processing pipeline:
        1. Load document
        2. Extract text
        3. Chunk text
        4. Add metadata
        
        Args:
            file_path: Path to document
            document_name: Custom document name (defaults to filename)
            additional_metadata: Additional metadata to attach
            
        Returns:
            Dictionary with chunks and document info
        """
        # Get document name
        if not document_name:
            document_name = Path(file_path).stem
        
        # Load document
        documents = self.load_document(file_path)
        
        # Prepare metadata
        metadata = {
            "document_name": document_name,
            "file_path": file_path,
            "file_extension": Path(file_path).suffix.lower(),
            "total_pages": len(documents),
        }
        
        if additional_metadata:
            metadata.update(additional_metadata)
        
        # Chunk documents
        chunks = self.chunk_documents(documents, add_metadata=metadata)
        
        # Calculate statistics
        total_chars = sum(len(chunk.page_content) for chunk in chunks)
        
        return {
            "document_name": document_name,
            "file_path": file_path,
            "chunks": chunks,
            "num_chunks": len(chunks),
            "total_characters": total_chars,
            "metadata": metadata
        }
    
    def extract_text(self, file_path: str) -> str:
        """
        Extract raw text from document without chunking
        
        Args:
            file_path: Path to document
            
        Returns:
            Complete document text
        """
        documents = self.load_document(file_path)
        return "\n\n".join([doc.page_content for doc in documents])
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """
        Get list of supported file formats
        
        Returns:
            List of supported extensions
        """
        return list(DocumentProcessor.SUPPORTED_FORMATS.keys())


# ===================== INTELLIGENT CONTENT EXTRACTION =====================

class IntelligentExtractor:
    """
    Extracts important information from documents using pattern matching
    Supports Farsi and English content
    """
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """Extract dates in various formats (Jalali, Gregorian)"""
        import re
        
        dates = []
        
        # Jalali dates (YYYY/MM/DD or YYYY-MM-DD)
        jalali_pattern = r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
        dates.extend(re.findall(jalali_pattern, text))
        
        # Gregorian dates
        gregorian_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{4}\b'
        dates.extend(re.findall(gregorian_pattern, text))
        
        # Persian date words
        persian_months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                         'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']
        for month in persian_months:
            if month in text:
                dates.append(f"Contains {month}")
        
        return list(set(dates))
    
    @staticmethod
    def extract_financial_data(text: str) -> List[str]:
        """Extract financial numbers, amounts, currencies"""
        import re
        
        financial = []
        
        # Money patterns (Persian and English)
        money_patterns = [
            r'\d+[\s,]*(?:تومان|ریال|دلار|یورو)',  # Persian currency
            r'[$€£]\s*\d+[\s,]*\d*',  # Western currency symbols
            r'\d+[\s,]*\d+\s*(?:USD|EUR|IRR|GBP)',  # Currency codes
        ]
        
        for pattern in money_patterns:
            financial.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return list(set(financial))
    
    @staticmethod
    def extract_guidelines(text: str) -> List[str]:
        """Extract guidelines, rules, instructions"""
        import re
        
        guidelines = []
        
        # Look for numbered lists, bullets, imperatives
        patterns = [
            r'^\d+[.)]\s*.+$',  # Numbered lists
            r'^[•\-*]\s*.+$',  # Bullet points
            r'(?:باید|بایستی|لازم است|الزامی است)\s+.+?[.،]',  # Persian imperatives
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            guidelines.extend(matches[:10])  # Limit to 10 items
        
        return guidelines
    
    @staticmethod
    def detect_sensitive_keywords(text: str) -> List[str]:
        """Detect sensitive keywords (confidential, private, etc.)"""
        sensitive_keywords_fa = [
            'محرمانه', 'خصوصی', 'سری', 'حساس', 'مخفی',
            'قرارداد', 'توافقنامه', 'پروژه', 'بودجه', 'هزینه'
        ]
        
        sensitive_keywords_en = [
            'confidential', 'private', 'secret', 'sensitive',
            'contract', 'agreement', 'budget', 'financial'
        ]
        
        found = []
        text_lower = text.lower()
        
        for keyword in sensitive_keywords_fa + sensitive_keywords_en:
            if keyword.lower() in text_lower:
                found.append(keyword)
        
        return list(set(found))
    
    @staticmethod
    def extract_important_info(text: str) -> Dict[str, List[str]]:
        """
        Extract all important information from document
        
        Args:
            text: Document text
            
        Returns:
            Dictionary with extracted information categories
        """
        return {
            "dates": IntelligentExtractor.extract_dates(text),
            "financial_data": IntelligentExtractor.extract_financial_data(text),
            "guidelines": IntelligentExtractor.extract_guidelines(text),
            "sensitive_keywords": IntelligentExtractor.detect_sensitive_keywords(text)
        }

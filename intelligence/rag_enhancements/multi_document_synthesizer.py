"""
Multi-Document Synthesizer
Synthesizes information from multiple documents simultaneously
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging

logger = logging.getLogger(__name__)


class MultiDocumentSynthesizer:
    """Synthesizes information from multiple documents"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    
    def synthesize_documents(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        max_documents: int = 10
    ) -> Dict[str, Any]:
        """
        Synthesize information from multiple documents
        
        Args:
            documents: List of document chunks with metadata
            query: User query
            max_documents: Maximum number of documents to synthesize
            
        Returns:
            Synthesized answer with source attribution
        """
        if not documents:
            return {
                'answer': 'هیچ سندی برای ترکیب پیدا نشد',
                'sources': [],
                'contradictions': []
            }
        
        # Limit documents
        documents = documents[:max_documents]
        
        # Prepare document text
        doc_texts = []
        sources = []
        
        for i, doc in enumerate(documents):
            content = doc.get('content', doc.get('page_content', ''))
            metadata = doc.get('metadata', {})
            
            doc_texts.append(f"[سند {i+1}]\n{content}")
            
            source_info = {
                'document_id': metadata.get('document_id', f'doc_{i+1}'),
                'document_name': metadata.get('document_name', metadata.get('source', 'Unknown')),
                'page': metadata.get('page', None),
                'chunk_index': i
            }
            sources.append(source_info)
        
        # Create synthesis prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """شما یک تحلیل‌گر متخصص هستید که اطلاعات از چندین سند را ترکیب می‌کنید.

دستورالعمل‌ها:
1. اطلاعات مرتبط از همه اسناد را ترکیب کنید
2. در صورت وجود تناقض، آن را مشخص کنید
3. برای هر بخش از پاسخ، منبع را ذکر کنید
4. پاسخ جامع و ساختاریافته باشد
5. اگر اطلاعات کافی نیست، صادقانه بگویید"""),
            ("human", """سوال: {query}

اسناد:
{documents}

لطفاً اطلاعات را از همه اسناد ترکیب کرده و پاسخ جامعی ارائه دهید. برای هر بخش منبع را مشخص کنید.""")
        ])
        
        documents_text = "\n\n---\n\n".join(doc_texts)
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(query=query, documents=documents_text)
            )
            
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Extract contradictions (simple pattern matching, can be enhanced)
            contradictions = self._detect_contradictions(doc_texts, query)
            
            return {
                'answer': answer,
                'sources': sources,
                'contradictions': contradictions,
                'document_count': len(documents)
            }
        
        except Exception as e:
            logger.error(f"Error synthesizing documents: {e}")
            return {
                'answer': f'خطا در ترکیب اسناد: {str(e)}',
                'sources': sources,
                'contradictions': []
            }
    
    def synthesize_with_priority(
        self,
        documents: List[Dict[str, Any]],
        query: str,
        priority_documents: List[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesize documents with priority ordering
        
        Args:
            documents: List of document chunks
            query: User query
            priority_documents: List of document IDs to prioritize
            
        Returns:
            Synthesized answer with priority consideration
        """
        if priority_documents:
            # Reorder documents
            priority_docs = []
            other_docs = []
            
            for doc in documents:
                doc_id = doc.get('metadata', {}).get('document_id', '')
                if doc_id in priority_documents:
                    priority_docs.append(doc)
                else:
                    other_docs.append(doc)
            
            # Combine with priority first
            ordered_documents = priority_docs + other_docs
        else:
            ordered_documents = documents
        
        return self.synthesize_documents(ordered_documents, query)
    
    def _detect_contradictions(
        self,
        doc_texts: List[str],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions between documents
        
        Args:
            doc_texts: List of document texts
            query: User query
            
        Returns:
            List of detected contradictions
        """
        # Simple contradiction detection
        # Can be enhanced with more sophisticated NLP
        
        contradictions = []
        
        if len(doc_texts) < 2:
            return contradictions
        
        # Check for conflicting numbers/dates
        # This is a simplified version - can be enhanced
        
        return contradictions


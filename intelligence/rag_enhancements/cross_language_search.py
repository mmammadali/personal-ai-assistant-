"""
Cross-Language Document Search
Search in one language, find documents in another language
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL, EMBEDDING_MODEL
import logging

logger = logging.getLogger(__name__)


class CrossLanguageSearch:
    """Enables cross-language document search"""
    
    def __init__(self, model_name: str = None, embedding_model: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model or EMBEDDING_MODEL,
            api_key=OPENAI_API_KEY
        )
    
    def search_across_languages(
        self,
        query: str,
        query_language: str = "auto",
        target_languages: Optional[List[str]] = None,
        vector_store: Any = None,
        k: int = 4
    ) -> Dict[str, Any]:
        """
        Search across languages
        
        Args:
            query: Search query
            query_language: Language of query ('auto', 'persian', 'english')
            target_languages: Target languages to search (None for all)
            vector_store: Vector store instance
            k: Number of results to return
            
        Returns:
            Search results with translations
        """
        if not vector_store:
            return {
                'results': [],
                'error': 'Vector store not provided'
            }
        
        # Detect query language if auto
        if query_language == "auto":
            query_language = self._detect_language(query)
        
        # Search in vector store (embeddings are language-agnostic)
        try:
            results = vector_store.search(query, k=k)
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return {
                'results': [],
                'error': str(e)
            }
        
        # Translate query if needed for context
        translated_query = self._translate_query(query, query_language)
        
        # Process results
        processed_results = []
        for result in results:
            content = result.get('content', result.get('page_content', ''))
            metadata = result.get('metadata', {})
            
            # Detect document language
            doc_language = self._detect_language(content)
            
            # Translate if different from query language
            translated_content = None
            if doc_language != query_language:
                translated_content = self._translate_excerpt(content, doc_language, query_language)
            
            processed_results.append({
                'content': content,
                'translated_content': translated_content,
                'document_language': doc_language,
                'query_language': query_language,
                'metadata': metadata,
                'relevance_score': result.get('score', 0.0)
            })
        
        return {
            'query': query,
            'translated_query': translated_query,
            'query_language': query_language,
            'results': processed_results,
            'total_results': len(processed_results)
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        if not text:
            return "unknown"
        
        # Simple detection based on character sets
        persian_chars = set('ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی')
        text_chars = set(text)
        
        persian_count = len(text_chars.intersection(persian_chars))
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "unknown"
        
        persian_ratio = persian_count / total_chars if total_chars > 0 else 0
        
        if persian_ratio > 0.3:
            return "persian"
        else:
            return "english"
    
    def _translate_query(
        self,
        query: str,
        source_language: str
    ) -> str:
        """Translate query for better context"""
        if source_language == "english":
            target = "persian"
        elif source_language == "persian":
            target = "english"
        else:
            return query
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a professional translator. Translate the query accurately while preserving its meaning and search intent."),
                ("human", "Translate this {source_language} query to {target_language}:\n{query}")
            ])
            
            response = self.llm.invoke(
                prompt.format_messages(
                    source_language=source_language,
                    target_language=target,
                    query=query
                )
            )
            
            return response.content if hasattr(response, 'content') else query
        
        except Exception as e:
            logger.error(f"Error translating query: {e}")
            return query
    
    def _translate_excerpt(
        self,
        text: str,
        source_language: str,
        target_language: str,
        max_length: int = 500
    ) -> str:
        """Translate document excerpt"""
        if not text:
            return ""
        
        # Limit text length
        text = text[:max_length]
        
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a professional translator. Translate the text accurately while preserving technical terms and context."),
                ("human", "Translate this {source_language} text to {target_language}:\n{text}")
            ])
            
            response = self.llm.invoke(
                prompt.format_messages(
                    source_language=source_language,
                    target_language=target_language,
                    text=text
                )
            )
            
            return response.content if hasattr(response, 'content') else text
        
        except Exception as e:
            logger.error(f"Error translating excerpt: {e}")
            return text


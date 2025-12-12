"""
Document Comparator
Compares document versions and highlights changes
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class DocumentComparator:
    """Compares document versions and highlights changes"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.2
        )
    
    def compare_documents(
        self,
        document1: Dict[str, Any],
        document2: Dict[str, Any],
        highlight_changes: bool = True
    ) -> Dict[str, Any]:
        """
        Compare two document versions
        
        Args:
            document1: First document (older version)
            document2: Second document (newer version)
            highlight_changes: Whether to highlight changes
            
        Returns:
            Comparison result with changes
        """
        content1 = document1.get('content', document1.get('page_content', ''))
        content2 = document2.get('content', document2.get('page_content', ''))
        
        metadata1 = document1.get('metadata', {})
        metadata2 = document2.get('metadata', {})
        
        # Calculate similarity
        similarity = SequenceMatcher(None, content1, content2).ratio()
        
        # Detect changes
        changes = self._detect_changes(content1, content2)
        
        # Categorize changes
        categorized_changes = self._categorize_changes(changes)
        
        return {
            'similarity': similarity,
            'changes': changes,
            'categorized_changes': categorized_changes,
            'document1_info': {
                'name': metadata1.get('document_name', 'Document 1'),
                'version': metadata1.get('version', 'unknown'),
                'date': metadata1.get('date', 'unknown')
            },
            'document2_info': {
                'name': metadata2.get('document_name', 'Document 2'),
                'version': metadata2.get('version', 'unknown'),
                'date': metadata2.get('date', 'unknown')
            },
            'summary': self._generate_summary(changes, categorized_changes)
        }
    
    def _detect_changes(
        self,
        content1: str,
        content2: str
    ) -> List[Dict[str, Any]]:
        """Detect changes between two documents"""
        changes = []
        
        # Use difflib for basic change detection
        matcher = SequenceMatcher(None, content1, content2)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    'type': 'modified',
                    'old_text': content1[i1:i2],
                    'new_text': content2[j1:j2],
                    'position': i1
                })
            elif tag == 'delete':
                changes.append({
                    'type': 'deleted',
                    'old_text': content1[i1:i2],
                    'position': i1
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'added',
                    'new_text': content2[j1:j2],
                    'position': i1
                })
        
        return changes
    
    def _categorize_changes(
        self,
        changes: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize changes by severity"""
        categorized = {
            'critical': [],
            'notable': [],
            'minor': []
        }
        
        for change in changes:
            # Simple categorization based on length and keywords
            text = change.get('old_text', '') + change.get('new_text', '')
            text_lower = text.lower()
            
            # Critical keywords
            critical_keywords = ['قیمت', 'مبلغ', 'تاریخ', 'مهلت', 'deadline', 'price', 'amount', 'date']
            notable_keywords = ['شرایط', 'قوانین', 'terms', 'conditions', 'policy']
            
            if any(keyword in text_lower for keyword in critical_keywords):
                severity = 'critical'
            elif any(keyword in text_lower for keyword in notable_keywords) or len(text) > 100:
                severity = 'notable'
            else:
                severity = 'minor'
            
            categorized[severity].append(change)
        
        return categorized
    
    def _generate_summary(
        self,
        changes: List[Dict[str, Any]],
        categorized: Dict[str, List[Dict[str, Any]]]
    ) -> str:
        """Generate summary of changes"""
        total = len(changes)
        critical = len(categorized['critical'])
        notable = len(categorized['notable'])
        minor = len(categorized['minor'])
        
        summary = f"تغییرات شناسایی شده: {total} مورد\n"
        summary += f"  - بحرانی: {critical}\n"
        summary += f"  - قابل توجه: {notable}\n"
        summary += f"  - جزئی: {minor}"
        
        return summary


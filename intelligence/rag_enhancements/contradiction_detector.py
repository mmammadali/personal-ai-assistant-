"""
Contradiction Detector
Detects conflicting information between documents and determines which version takes precedence
"""
from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ContradictionDetector:
    """Detects contradictions and determines precedence"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.2
        )
    
    def detect_contradictions(
        self,
        documents: List[Dict[str, Any]],
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect contradictions between documents
        
        Args:
            documents: List of document chunks with metadata
            query: Optional query to focus contradiction detection
            
        Returns:
            List of detected contradictions
        """
        if len(documents) < 2:
            return []
        
        contradictions = []
        
        # Extract document information
        doc_info = []
        for i, doc in enumerate(documents):
            content = doc.get('content', doc.get('page_content', ''))
            metadata = doc.get('metadata', {})
            
            doc_info.append({
                'index': i,
                'content': content,
                'document_id': metadata.get('document_id', f'doc_{i+1}'),
                'document_name': metadata.get('document_name', metadata.get('source', 'Unknown')),
                'date': metadata.get('date', metadata.get('uploaded_at')),
                'version': metadata.get('version', None)
            })
        
        # Compare documents pairwise
        for i in range(len(doc_info)):
            for j in range(i + 1, len(doc_info)):
                doc1 = doc_info[i]
                doc2 = doc_info[j]
                
                # Detect contradictions
                contradictions_found = self._compare_documents(doc1, doc2, query)
                contradictions.extend(contradictions_found)
        
        return contradictions
    
    def determine_superseding_document(
        self,
        documents: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Determine which document supersedes others based on version, date, and authority
        
        Args:
            documents: List of documents
            contradictions: List of detected contradictions
            
        Returns:
            Superseding logic and recommendations
        """
        if not contradictions:
            return {
                'superseding_logic': 'no_contradictions',
                'recommendations': []
            }
        
        # Analyze document metadata
        doc_metadata = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            doc_metadata.append({
                'document_id': metadata.get('document_id', ''),
                'document_name': metadata.get('document_name', ''),
                'date': metadata.get('date', metadata.get('uploaded_at')),
                'version': metadata.get('version', None),
                'authority': metadata.get('authority', 'standard')
            })
        
        # Determine precedence rules
        precedence_rules = []
        
        # Rule 1: Latest version wins
        versions = [d.get('version') for d in doc_metadata if d.get('version')]
        if versions:
            latest_version = max(v for v in versions if v is not None)
            precedence_rules.append({
                'rule': 'latest_version',
                'description': f'نسخه {latest_version} جدیدترین است',
                'priority': 'high'
            })
        
        # Rule 2: Latest date wins
        dates = [d.get('date') for d in doc_metadata if d.get('date')]
        if dates:
            # Parse dates and find latest
            parsed_dates = []
            for date_str in dates:
                try:
                    # Try various date formats
                    parsed_dates.append(self._parse_date(date_str))
                except:
                    pass
            
            if parsed_dates:
                latest_date = max(parsed_dates)
                precedence_rules.append({
                    'rule': 'latest_date',
                    'description': f'تاریخ {latest_date} جدیدترین است',
                    'priority': 'high'
                })
        
        # Rule 3: Authority level
        authorities = [d.get('authority') for d in doc_metadata]
        if 'official' in authorities or 'policy' in authorities:
            precedence_rules.append({
                'rule': 'authority',
                'description': 'اسناد رسمی/سیاستی اولویت دارند',
                'priority': 'critical'
            })
        
        # Generate recommendations
        recommendations = []
        for contradiction in contradictions:
            doc1_name = contradiction.get('document1', {}).get('name', 'Unknown')
            doc2_name = contradiction.get('document2', {}).get('name', 'Unknown')
            
            recommendations.append({
                'contradiction': contradiction.get('description', ''),
                'recommendation': f'برای "{contradiction.get("topic", "")}"، {doc1_name} را بررسی کنید',
                'priority': contradiction.get('severity', 'medium')
            })
        
        return {
            'superseding_logic': precedence_rules,
            'recommendations': recommendations,
            'contradiction_count': len(contradictions)
        }
    
    def analyze_policy_versions(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze policy document versions and determine which takes precedence
        
        Args:
            documents: List of policy documents
            
        Returns:
            Policy version analysis
        """
        # Extract version information
        versions = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            versions.append({
                'document_id': metadata.get('document_id', ''),
                'document_name': metadata.get('document_name', ''),
                'version': metadata.get('version', 'unknown'),
                'date': metadata.get('date', metadata.get('uploaded_at')),
                'content': doc.get('content', doc.get('page_content', ''))[:500]  # First 500 chars
            })
        
        # Sort by version/date
        sorted_versions = sorted(
            versions,
            key=lambda x: (
                self._parse_version(x.get('version', '0')),
                self._parse_date(x.get('date', '')) if x.get('date') else datetime.min
            ),
            reverse=True
        )
        
        latest = sorted_versions[0] if sorted_versions else None
        
        return {
            'total_versions': len(versions),
            'latest_version': latest,
            'version_history': sorted_versions,
            'superseding_policy': latest.get('document_name') if latest else None
        }
    
    def _compare_documents(
        self,
        doc1: Dict[str, Any],
        doc2: Dict[str, Any],
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Compare two documents for contradictions"""
        contradictions = []
        
        # Use LLM to detect contradictions
        prompt = ChatPromptTemplate.from_messages([
            ("system", """شما یک تحلیل‌گر متخصص هستید که تناقضات بین اسناد را شناسایی می‌کنید.

دستورالعمل‌ها:
1. تناقضات واقعی را شناسایی کنید (نه فقط تفاوت‌های جزئی)
2. شدت تناقض را مشخص کنید (critical, notable, minor)
3. موضوع تناقض را مشخص کنید"""),
            ("human", """مقایسه دو سند برای تناقض:

سند 1 ({doc1_name}):
{doc1_content}

سند 2 ({doc2_name}):
{doc2_content}

{query_context}

آیا تناقضی وجود دارد؟ اگر بله، جزئیات را مشخص کنید.""")
        ])
        
        query_context = f"سوال کاربر: {query}" if query else "تحلیل کلی"
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    doc1_name=doc1.get('document_name', 'سند 1'),
                    doc1_content=doc1.get('content', '')[:2000],  # Limit length
                    doc2_name=doc2.get('document_name', 'سند 2'),
                    doc2_content=doc2.get('content', '')[:2000],
                    query_context=query_context
                )
            )
            
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response for contradictions
            if 'تناقض' in answer.lower() or 'contradiction' in answer.lower():
                contradictions.append({
                    'document1': {
                        'name': doc1.get('document_name'),
                        'id': doc1.get('document_id')
                    },
                    'document2': {
                        'name': doc2.get('document_name'),
                        'id': doc2.get('document_id')
                    },
                    'description': answer,
                    'severity': self._extract_severity(answer),
                    'topic': self._extract_topic(answer, query)
                })
        
        except Exception as e:
            logger.error(f"Error comparing documents: {e}")
        
        return contradictions
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string to datetime"""
        if not date_str:
            return datetime.min
        
        # Try various formats
        formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str[:19], fmt)
            except:
                continue
        
        return datetime.min
    
    def _parse_version(self, version_str: str) -> float:
        """Parse version string to comparable number"""
        if not version_str or version_str == 'unknown':
            return 0.0
        
        # Extract numbers
        numbers = re.findall(r'\d+\.?\d*', version_str)
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass
        
        return 0.0
    
    def _extract_severity(self, text: str) -> str:
        """Extract severity from text"""
        text_lower = text.lower()
        
        if 'critical' in text_lower or 'بحرانی' in text_lower or 'مهم' in text_lower:
            return 'critical'
        elif 'notable' in text_lower or 'قابل توجه' in text_lower:
            return 'notable'
        else:
            return 'minor'
    
    def _extract_topic(self, text: str, query: Optional[str] = None) -> str:
        """Extract topic from text or use query"""
        if query:
            return query[:50]
        
        # Extract first sentence or key phrase
        sentences = text.split('.')
        if sentences:
            return sentences[0][:50]
        
        return 'موضوع نامشخص'


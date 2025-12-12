"""
Action Extractor
Extracts actionable items, deadlines, and responsibilities from documents
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ActionExtractor:
    """Extracts actionable items from documents"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.2
        )
    
    def extract_actions(
        self,
        document_content: str,
        include_deadlines: bool = True,
        include_responsibilities: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract actionable items from document
        
        Args:
            document_content: Document content
            include_deadlines: Whether to extract deadlines
            include_responsibilities: Whether to extract responsible parties
            
        Returns:
            List of action items
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting actionable items from documents.

Extract:
1. Specific actions/tasks
2. Deadlines (if mentioned)
3. Responsible parties (if mentioned)
4. Priority levels
5. Dependencies

Format as structured JSON-like list."""),
            ("human", """Extract all actionable items from this document:

{document}

Include deadlines: {include_deadlines}
Include responsibilities: {include_responsibilities}""")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    document=document_content[:6000],
                    include_deadlines=include_deadlines,
                    include_responsibilities=include_responsibilities
                )
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            actions = self._parse_actions(text, document_content)
            
            return actions
        
        except Exception as e:
            logger.error(f"Error extracting actions: {e}")
            return []
    
    def extract_deadlines(
        self,
        document_content: str
    ) -> List[Dict[str, Any]]:
        """Extract all deadlines from document"""
        # Pattern matching for dates
        date_patterns = [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY
            r'(deadline|مهلت|تاریخ|date).*?(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'by\s+(\w+\s+\d{1,2},?\s+\d{4})',  # "by January 15, 2024"
        ]
        
        deadlines = []
        for pattern in date_patterns:
            matches = re.finditer(pattern, document_content, re.IGNORECASE)
            for match in matches:
                deadlines.append({
                    'text': match.group(0),
                    'date': match.group(1) if len(match.groups()) > 0 else match.group(0),
                    'position': match.start()
                })
        
        # Use LLM to extract deadline context
        if deadlines:
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Extract deadline information with context and associated tasks."),
                ("human", "Document excerpt around deadlines:\n{document}")
            ])
            
            try:
                # Get context around each deadline
                deadline_contexts = []
                for deadline in deadlines[:10]:  # Limit to 10
                    start = max(0, deadline['position'] - 200)
                    end = min(len(document_content), deadline['position'] + 200)
                    context = document_content[start:end]
                    deadline_contexts.append(context)
                
                context_text = '\n\n---\n\n'.join(deadline_contexts)
                
                response = self.llm.invoke(
                    prompt.format_messages(document=context_text)
                )
                
                # Parse response for deadline details
                deadline_details = self._parse_deadline_details(
                    response.content if hasattr(response, 'content') else str(response)
                )
                
                # Merge with found deadlines
                for i, deadline in enumerate(deadlines[:len(deadline_details)]):
                    if i < len(deadline_details):
                        deadline.update(deadline_details[i])
            
            except Exception as e:
                logger.error(f"Error processing deadline context: {e}")
        
        return deadlines
    
    def extract_responsibilities(
        self,
        document_content: str
    ) -> List[Dict[str, Any]]:
        """Extract responsible parties and their tasks"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract responsible parties and their assigned tasks/actions from the document.
Format as: Person/Team -> Task/Action"""),
            ("human", "Extract responsibilities:\n{document}")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(document=document_content[:6000])
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            responsibilities = self._parse_responsibilities(text)
            
            return responsibilities
        
        except Exception as e:
            logger.error(f"Error extracting responsibilities: {e}")
            return []
    
    def _parse_actions(
        self,
        text: str,
        original_document: str
    ) -> List[Dict[str, Any]]:
        """Parse action items from extracted text"""
        actions = []
        
        # Split by common delimiters
        items = re.split(r'\n\s*[-•*]\s*|\d+\.\s*', text)
        
        for item in items:
            item = item.strip()
            if not item or len(item) < 10:
                continue
            
            # Extract action
            action = {
                'description': item,
                'deadline': None,
                'responsible': None,
                'priority': 'medium',
                'dependencies': []
            }
            
            # Try to extract deadline
            deadline_match = re.search(
                r'(deadline|مهلت|by|تا|تاریch).*?(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\w+\s+\d{1,2})',
                item,
                re.IGNORECASE
            )
            if deadline_match:
                action['deadline'] = deadline_match.group(0)
            
            # Try to extract responsible party
            responsible_match = re.search(
                r'(responsible|مسئول|assigned to|توسط).*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
                item,
                re.IGNORECASE
            )
            if responsible_match:
                action['responsible'] = responsible_match.group(2)
            
            # Determine priority
            if any(word in item.lower() for word in ['urgent', 'فوری', 'critical', 'بحرانی']):
                action['priority'] = 'high'
            elif any(word in item.lower() for word in ['low', 'پایین', 'optional']):
                action['priority'] = 'low'
            
            actions.append(action)
        
        return actions
    
    def _parse_deadline_details(self, text: str) -> List[Dict[str, Any]]:
        """Parse deadline details from LLM response"""
        details = []
        
        # Simple parsing - can be enhanced
        lines = text.split('\n')
        for line in lines:
            if 'deadline' in line.lower() or 'مهلت' in line:
                details.append({
                    'context': line,
                    'task': None
                })
        
        return details
    
    def _parse_responsibilities(self, text: str) -> List[Dict[str, Any]]:
        """Parse responsibilities from text"""
        responsibilities = []
        
        # Look for patterns like "Person -> Task" or "Person: Task"
        patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[-:>]\s*(.+)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(is responsible|مسئول)\s+(.+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                responsibilities.append({
                    'person': match.group(1),
                    'task': match.group(2) if len(match.groups()) > 1 else match.group(0)
                })
        
        return responsibilities


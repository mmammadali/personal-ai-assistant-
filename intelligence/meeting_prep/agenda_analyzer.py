"""
Agenda Analyzer
Analyzes meeting agendas and extracts key topics, participants, and structure
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
import re

logger = logging.getLogger(__name__)


class AgendaAnalyzer:
    """Analyzes meeting agendas"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.2
        )
    
    def analyze_agenda(
        self,
        agenda_text: str,
        meeting_date: Optional[str] = None,
        meeting_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze meeting agenda
        
        Args:
            agenda_text: Agenda text
            meeting_date: Meeting date
            meeting_title: Meeting title
            
        Returns:
            Structured agenda analysis
        """
        # Extract agenda items
        agenda_items = self._extract_agenda_items(agenda_text)
        
        # Extract participants
        participants = self._extract_participants(agenda_text)
        
        # Extract time allocations
        time_allocations = self._extract_time_allocations(agenda_text)
        
        # Categorize topics
        topic_categories = self._categorize_topics(agenda_items)
        
        # Identify key decisions needed
        decisions_needed = self._identify_decisions(agenda_text)
        
        return {
            'meeting_title': meeting_title,
            'meeting_date': meeting_date,
            'agenda_items': agenda_items,
            'participants': participants,
            'time_allocations': time_allocations,
            'topic_categories': topic_categories,
            'decisions_needed': decisions_needed,
            'estimated_duration': self._estimate_duration(time_allocations),
            'priority_topics': self._identify_priority_topics(agenda_items)
        }
    
    def _extract_agenda_items(self, agenda_text: str) -> List[Dict[str, Any]]:
        """Extract agenda items from text"""
        items = []
        
        # Pattern matching for numbered/bulleted items
        patterns = [
            r'\d+\.\s*(.+?)(?=\d+\.|$)',
            r'[-•*]\s*(.+?)(?=[-•*]|$)',
            r'Topic\s+\d+:\s*(.+?)(?=Topic|$)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, agenda_text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                item_text = match.group(1).strip()
                if len(item_text) > 10:  # Filter out very short items
                    items.append({
                        'text': item_text,
                        'position': match.start()
                    })
        
        # Use LLM for better extraction if needed
        if not items or len(items) < 2:
            items = self._llm_extract_items(agenda_text)
        
        return items
    
    def _llm_extract_items(self, agenda_text: str) -> List[Dict[str, Any]]:
        """Use LLM to extract agenda items"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Extract all agenda items from the meeting agenda. List them in order."),
            ("human", "Agenda:\n{agenda}")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(agenda=agenda_text[:3000])
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse response
            items = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up
                    line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                    if len(line) > 10:
                        items.append({'text': line, 'position': 0})
            
            return items
        
        except Exception as e:
            logger.error(f"Error extracting agenda items: {e}")
            return []
    
    def _extract_participants(self, agenda_text: str) -> List[str]:
        """Extract participant names"""
        participants = []
        
        # Common patterns
        patterns = [
            r'Participants?:\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            r'Attendees?:\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            r'شرکت‌کنندگان?:\s*(.+?)(?=\n\n|\n[ا-ی]|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, agenda_text, re.IGNORECASE | re.MULTILINE)
            if match:
                participant_text = match.group(1)
                # Split by common delimiters
                names = re.split(r'[,،;؛\n]', participant_text)
                for name in names:
                    name = name.strip()
                    if name and len(name) > 2:
                        participants.append(name)
        
        return list(set(participants))  # Remove duplicates
    
    def _extract_time_allocations(self, agenda_text: str) -> List[Dict[str, Any]]:
        """Extract time allocations for agenda items"""
        allocations = []
        
        # Pattern for time (e.g., "10:00-10:15", "15 minutes", "30 min")
        time_patterns = [
            r'(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})',
            r'(\d+)\s*(?:minutes?|mins?|دقیقه)',
            r'(\d+)\s*(?:hours?|hrs?|ساعت)',
        ]
        
        for pattern in time_patterns:
            matches = re.finditer(pattern, agenda_text, re.IGNORECASE)
            for match in matches:
                allocations.append({
                    'text': match.group(0),
                    'position': match.start()
                })
        
        return allocations
    
    def _categorize_topics(self, agenda_items: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Categorize agenda topics"""
        categories = {
            'strategic': [],
            'operational': [],
            'financial': [],
            'technical': [],
            'administrative': []
        }
        
        keywords = {
            'strategic': ['strategy', 'vision', 'goals', 'planning', 'استراتژی', 'چشم‌انداز'],
            'operational': ['operations', 'process', 'workflow', 'عملیات', 'فرآیند'],
            'financial': ['budget', 'cost', 'revenue', 'financial', 'بودجه', 'مالی'],
            'technical': ['technical', 'implementation', 'system', 'فنی', 'پیاده‌سازی'],
            'administrative': ['admin', 'hr', 'policy', 'administrative', 'اداری']
        }
        
        for item in agenda_items:
            text_lower = item['text'].lower()
            categorized = False
            
            for category, category_keywords in keywords.items():
                if any(keyword in text_lower for keyword in category_keywords):
                    categories[category].append(item['text'])
                    categorized = True
                    break
            
            if not categorized:
                categories['operational'].append(item['text'])
        
        return categories
    
    def _identify_decisions(self, agenda_text: str) -> List[str]:
        """Identify decisions that need to be made"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Identify key decisions that need to be made in this meeting."),
            ("human", "Agenda:\n{agenda}")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(agenda=agenda_text[:3000])
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse decisions
            decisions = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                    if len(line) > 10:
                        decisions.append(line)
            
            return decisions
        
        except Exception as e:
            logger.error(f"Error identifying decisions: {e}")
            return []
    
    def _estimate_duration(self, time_allocations: List[Dict[str, Any]]) -> Optional[str]:
        """Estimate total meeting duration"""
        if not time_allocations:
            return None
        
        # Simple estimation based on number of items
        # Can be enhanced with actual time parsing
        return "60 minutes"  # Default
    
    def _identify_priority_topics(self, agenda_items: List[Dict[str, Any]]) -> List[str]:
        """Identify high-priority topics"""
        priority_keywords = ['urgent', 'critical', 'important', 'فوری', 'مهم', 'بحرانی']
        
        priority_topics = []
        for item in agenda_items:
            if any(keyword in item['text'].lower() for keyword in priority_keywords):
                priority_topics.append(item['text'])
        
        return priority_topics


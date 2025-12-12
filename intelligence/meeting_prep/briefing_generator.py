"""
Briefing Packet Generator
Generates comprehensive briefing packets for meetings
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
from intelligence.meeting_prep.agenda_analyzer import AgendaAnalyzer
from database import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class BriefingGenerator:
    """Generates meeting briefing packets"""
    
    def __init__(self, model_name: str = None, db_path: str = "assistant.db"):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
        self.agenda_analyzer = AgendaAnalyzer(model_name)
        self.db = DatabaseManager(db_path)
    
    def generate_briefing_packet(
        self,
        meeting_id: Optional[int] = None,
        agenda_text: Optional[str] = None,
        meeting_date: Optional[str] = None,
        meeting_title: Optional[str] = None,
        include_context: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive briefing packet
        
        Args:
            meeting_id: Database event ID
            agenda_text: Agenda text
            meeting_date: Meeting date
            meeting_title: Meeting title
            include_context: Whether to include related context
            
        Returns:
            Complete briefing packet
        """
        # Get meeting info from database if ID provided
        if meeting_id:
            events = self.db.get_events()
            event = next((e for e in events if e.get('id') == meeting_id), None)
            if event:
                meeting_title = meeting_title or event.get('title')
                meeting_date = meeting_date or event.get('date')
                agenda_text = agenda_text or event.get('description')
        
        # Analyze agenda
        agenda_analysis = self.agenda_analyzer.analyze_agenda(
            agenda_text or "",
            meeting_date,
            meeting_title
        )
        
        # Generate sections
        executive_summary = self._generate_executive_summary(agenda_analysis)
        key_topics = self._generate_key_topics(agenda_analysis)
        background_context = self._generate_background_context(agenda_analysis) if include_context else None
        preparation_checklist = self._generate_preparation_checklist(agenda_analysis)
        
        return {
            'meeting_info': {
                'title': meeting_title,
                'date': meeting_date,
                'participants': agenda_analysis.get('participants', [])
            },
            'executive_summary': executive_summary,
            'agenda_analysis': agenda_analysis,
            'key_topics': key_topics,
            'background_context': background_context,
            'preparation_checklist': preparation_checklist,
            'estimated_duration': agenda_analysis.get('estimated_duration')
        }
    
    def _generate_executive_summary(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> str:
        """Generate executive summary"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise executive summary of the meeting agenda."),
            ("human", """Meeting Title: {title}
Date: {date}
Agenda Items: {items}

Generate a 2-3 sentence executive summary.""")
        ])
        
        try:
            items_text = '\n'.join([item['text'] for item in agenda_analysis.get('agenda_items', [])[:5]])
            
            response = self.llm.invoke(
                prompt.format_messages(
                    title=agenda_analysis.get('meeting_title', 'Meeting'),
                    date=agenda_analysis.get('meeting_date', 'TBD'),
                    items=items_text
                )
            )
            
            return response.content if hasattr(response, 'content') else str(response)
        
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return "Executive summary generation failed."
    
    def _generate_key_topics(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate key topics with context"""
        topics = []
        
        priority_topics = agenda_analysis.get('priority_topics', [])
        topic_categories = agenda_analysis.get('topic_categories', {})
        
        # Combine priority and categorized topics
        for category, items in topic_categories.items():
            for item in items[:3]:  # Top 3 per category
                topics.append({
                    'topic': item,
                    'category': category,
                    'priority': 'high' if item in priority_topics else 'medium'
                })
        
        return topics
    
    def _generate_background_context(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate background context from related documents/events"""
        # Get related events/tasks from database
        related_events = []
        related_tasks = []
        
        # Search for related items based on keywords
        agenda_items = agenda_analysis.get('agenda_items', [])
        if agenda_items:
            # Extract keywords
            keywords = []
            for item in agenda_items[:3]:
                keywords.extend(item['text'].split()[:3])
            
            # Search database (simplified)
            # In real implementation, would search more intelligently
        
        return {
            'related_events': related_events,
            'related_tasks': related_tasks,
            'context_notes': 'Related context will be populated from database search'
        }
    
    def _generate_preparation_checklist(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate preparation checklist"""
        checklist = []
        
        # Standard items
        checklist.append("Review agenda items")
        checklist.append("Prepare talking points")
        checklist.append("Review relevant documents")
        
        # Topic-specific items
        topic_categories = agenda_analysis.get('topic_categories', {})
        
        if topic_categories.get('financial'):
            checklist.append("Review financial data and budgets")
        
        if topic_categories.get('strategic'):
            checklist.append("Review strategic documents and goals")
        
        if topic_categories.get('technical'):
            checklist.append("Review technical specifications")
        
        # Decisions needed
        decisions = agenda_analysis.get('decisions_needed', [])
        if decisions:
            checklist.append(f"Prepare input for {len(decisions)} decision(s)")
        
        return checklist


"""
Talking Point Suggester
Suggests talking points based on agenda and context
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
from intelligence.meeting_prep.agenda_analyzer import AgendaAnalyzer
import logging

logger = logging.getLogger(__name__)


class TalkingPointSuggester:
    """Suggests talking points for meetings"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.7
        )
        self.agenda_analyzer = AgendaAnalyzer(model_name)
    
    def suggest_talking_points(
        self,
        agenda_text: str,
        user_role: str = "participant",
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Suggest talking points for meeting
        
        Args:
            agenda_text: Meeting agenda
            user_role: User's role in meeting
            meeting_context: Optional meeting context
            
        Returns:
            Suggested talking points organized by agenda item
        """
        # Analyze agenda
        agenda_analysis = self.agenda_analyzer.analyze_agenda(agenda_text)
        
        # Generate talking points for each agenda item
        talking_points_by_topic = {}
        
        for item in agenda_analysis.get('agenda_items', []):
            topic = item['text']
            points = self._generate_talking_points_for_topic(
                topic,
                user_role,
                meeting_context
            )
            talking_points_by_topic[topic] = points
        
        # Generate opening/closing remarks
        opening_remarks = self._generate_opening_remarks(agenda_analysis, user_role)
        closing_remarks = self._generate_closing_remarks(agenda_analysis, user_role)
        
        return {
            'talking_points_by_topic': talking_points_by_topic,
            'opening_remarks': opening_remarks,
            'closing_remarks': closing_remarks,
            'key_points_to_emphasize': self._identify_key_points(agenda_analysis),
            'questions_to_ask': self._generate_questions(agenda_analysis)
        }
    
    def _generate_talking_points_for_topic(
        self,
        topic: str,
        user_role: str,
        meeting_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate talking points for a specific topic"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a meeting preparation assistant. Generate 3-5 concise talking points for the user's role.

Talking points should be:
- Relevant to the topic
- Appropriate for the user's role
- Actionable and specific
- Professional"""),
            ("human", """Topic: {topic}
User Role: {role}
Context: {context}

Generate 3-5 talking points.""")
        ])
        
        context_text = str(meeting_context) if meeting_context else "General meeting"
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    topic=topic,
                    role=user_role,
                    context=context_text
                )
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse talking points
            points = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Clean up
                    import re
                    line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                    if len(line) > 10:
                        points.append(line)
            
            return points[:5]  # Limit to 5
        
        except Exception as e:
            logger.error(f"Error generating talking points: {e}")
            return []
    
    def _generate_opening_remarks(
        self,
        agenda_analysis: Dict[str, Any],
        user_role: str
    ) -> str:
        """Generate opening remarks"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate professional opening remarks for a meeting."),
            ("human", """Meeting: {title}
Role: {role}
Agenda Items: {items}

Generate 2-3 sentence opening remarks.""")
        ])
        
        try:
            items_text = '\n'.join([item['text'] for item in agenda_analysis.get('agenda_items', [])[:3]])
            
            response = self.llm.invoke(
                prompt.format_messages(
                    title=agenda_analysis.get('meeting_title', 'Meeting'),
                    role=user_role,
                    items=items_text
                )
            )
            
            return response.content if hasattr(response, 'content') else ""
        
        except Exception as e:
            logger.error(f"Error generating opening remarks: {e}")
            return ""
    
    def _generate_closing_remarks(
        self,
        agenda_analysis: Dict[str, Any],
        user_role: str
    ) -> str:
        """Generate closing remarks"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate professional closing remarks summarizing key decisions and next steps."),
            ("human", """Meeting: {title}
Role: {role}
Decisions: {decisions}

Generate 2-3 sentence closing remarks.""")
        ])
        
        try:
            decisions_text = '\n'.join(agenda_analysis.get('decisions_needed', [])[:3])
            
            response = self.llm.invoke(
                prompt.format_messages(
                    title=agenda_analysis.get('meeting_title', 'Meeting'),
                    role=user_role,
                    decisions=decisions_text or "Various agenda items"
                )
            )
            
            return response.content if hasattr(response, 'content') else ""
        
        except Exception as e:
            logger.error(f"Error generating closing remarks: {e}")
            return ""
    
    def _identify_key_points(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify key points to emphasize"""
        key_points = []
        
        # Priority topics
        priority_topics = agenda_analysis.get('priority_topics', [])
        key_points.extend(priority_topics[:3])
        
        # Decisions needed
        decisions = agenda_analysis.get('decisions_needed', [])
        key_points.extend([f"Decision needed: {d}" for d in decisions[:2]])
        
        return key_points
    
    def _generate_questions(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate questions to ask during meeting"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate insightful questions to ask during the meeting based on the agenda."),
            ("human", """Agenda Items:
{items}

Generate 3-5 relevant questions.""")
        ])
        
        try:
            items_text = '\n'.join([item['text'] for item in agenda_analysis.get('agenda_items', [])])
            
            response = self.llm.invoke(
                prompt.format_messages(items=items_text)
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse questions
            questions = []
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if line and ('?' in line or line[0].isdigit() or line.startswith('-')):
                    import re
                    line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                    if len(line) > 10:
                        questions.append(line)
            
            return questions[:5]
        
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            return []


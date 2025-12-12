"""
Question Predictor
Predicts likely questions from meeting participants
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
from intelligence.meeting_prep.agenda_analyzer import AgendaAnalyzer
import logging

logger = logging.getLogger(__name__)


class QuestionPredictor:
    """Predicts questions from meeting participants"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.6
        )
        self.agenda_analyzer = AgendaAnalyzer(model_name)
    
    def predict_questions(
        self,
        agenda_text: str,
        participant_roles: Optional[List[str]] = None,
        meeting_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Predict likely questions from participants
        
        Args:
            agenda_text: Meeting agenda
            participant_roles: List of participant roles
            meeting_context: Optional meeting context
            
        Returns:
            Predicted questions organized by participant/role
        """
        # Analyze agenda
        agenda_analysis = self.agenda_analyzer.analyze_agenda(agenda_text)
        
        # Get participants
        participants = agenda_analysis.get('participants', [])
        
        # Predict questions by role
        questions_by_role = {}
        
        if participant_roles:
            for role in participant_roles:
                questions = self._predict_questions_for_role(
                    role,
                    agenda_analysis,
                    meeting_context
                )
                questions_by_role[role] = questions
        else:
            # Predict general questions
            general_questions = self._predict_general_questions(agenda_analysis)
            questions_by_role['general'] = general_questions
        
        # Predict questions by topic
        questions_by_topic = {}
        for item in agenda_analysis.get('agenda_items', []):
            topic = item['text']
            questions = self._predict_questions_for_topic(topic, meeting_context)
            questions_by_topic[topic] = questions
        
        return {
            'questions_by_role': questions_by_role,
            'questions_by_topic': questions_by_topic,
            'most_likely_questions': self._rank_questions(questions_by_role, questions_by_topic),
            'preparation_answers': self._suggest_answers(agenda_analysis)
        }
    
    def _predict_questions_for_role(
        self,
        role: str,
        agenda_analysis: Dict[str, Any],
        meeting_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Predict questions for a specific role"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Predict likely questions that a {role} would ask in this meeting.

Consider:
- Role-specific concerns
- Agenda topics
- Typical questions for this role"""),
            ("human", """Agenda Items:
{items}

Role: {role}
Context: {context}

Predict 3-5 likely questions.""")
        ])
        
        try:
            items_text = '\n'.join([item['text'] for item in agenda_analysis.get('agenda_items', [])])
            context_text = str(meeting_context) if meeting_context else "General meeting"
            
            response = self.llm.invoke(
                prompt.format_messages(
                    role=role,
                    items=items_text,
                    context=context_text
                )
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse questions
            questions = self._parse_questions(text)
            return questions[:5]
        
        except Exception as e:
            logger.error(f"Error predicting questions for role: {e}")
            return []
    
    def _predict_general_questions(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> List[str]:
        """Predict general questions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Predict common questions that might be asked in this meeting."),
            ("human", """Agenda:
{items}

Predict 5-7 likely general questions.""")
        ])
        
        try:
            items_text = '\n'.join([item['text'] for item in agenda_analysis.get('agenda_items', [])])
            
            response = self.llm.invoke(
                prompt.format_messages(items=items_text)
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            return self._parse_questions(text)[:7]
        
        except Exception as e:
            logger.error(f"Error predicting general questions: {e}")
            return []
    
    def _predict_questions_for_topic(
        self,
        topic: str,
        meeting_context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Predict questions for a specific topic"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Predict questions that might be asked about this specific topic."),
            ("human", """Topic: {topic}

Predict 3-5 likely questions.""")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(topic=topic)
            )
            
            text = response.content if hasattr(response, 'content') else str(response)
            return self._parse_questions(text)[:5]
        
        except Exception as e:
            logger.error(f"Error predicting questions for topic: {e}")
            return []
    
    def _parse_questions(self, text: str) -> List[str]:
        """Parse questions from text"""
        questions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a question
            if '?' in line:
                # Clean up
                import re
                line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                if len(line) > 10:
                    questions.append(line)
            elif line[0].isdigit() or line.startswith('-') or line.startswith('•'):
                # Might be a question without ?
                line = re.sub(r'^\d+\.\s*|^[-•*]\s*', '', line)
                if any(word in line.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who', 'چرا', 'چگونه', 'چه', 'کی']):
                    questions.append(line)
        
        return questions
    
    def _rank_questions(
        self,
        questions_by_role: Dict[str, List[str]],
        questions_by_topic: Dict[str, List[str]]
    ) -> List[str]:
        """Rank questions by likelihood"""
        all_questions = []
        
        # Collect all questions
        for role_questions in questions_by_role.values():
            all_questions.extend(role_questions)
        
        for topic_questions in questions_by_topic.values():
            all_questions.extend(topic_questions)
        
        # Remove duplicates
        unique_questions = list(dict.fromkeys(all_questions))
        
        # Return top 10
        return unique_questions[:10]
    
    def _suggest_answers(
        self,
        agenda_analysis: Dict[str, Any]
    ) -> Dict[str, str]:
        """Suggest answers to predicted questions"""
        # This would generate suggested answers
        # For now, return placeholder
        return {
            'note': 'Answer suggestions will be generated based on agenda content and context'
        }


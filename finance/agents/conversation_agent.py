"""
Conversational Agent
Handles dialogue, clarifications, and general assistance
"""
from langchain_openai import ChatOpenAI


class ConversationAgent:
    """Conversational interface specialist"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def handle_clarification(self, user_input: str, context: dict) -> str:
        """
        Handle clarification requests
        
        Args:
            user_input: User's message
            context: Conversation context
            
        Returns:
            Clarifying question or response
        """
        # TODO: Implement conversational handling
        return "من یک دستیار مالی هوشمند هستم. چگونه می‌توانم کمکتان کنم؟"


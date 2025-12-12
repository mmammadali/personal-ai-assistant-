"""
Role-Based Document Summarizer
Generates summaries tailored to specific roles (CEO, CFO, Legal, etc.)
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging

logger = logging.getLogger(__name__)


class RoleBasedSummarizer:
    """Generates role-adaptive document summaries"""
    
    # Role-specific focus areas
    ROLE_FOCUS = {
        'ceo': {
            'focus': ['executive_summary', 'strategic_decisions', 'key_metrics', 'risks', 'opportunities'],
            'language': 'high-level strategic',
            'detail_level': 'summary'
        },
        'cfo': {
            'focus': ['financial_data', 'budget', 'costs', 'revenue', 'financial_risks', 'roi'],
            'language': 'financial and quantitative',
            'detail_level': 'detailed'
        },
        'legal': {
            'focus': ['liabilities', 'compliance', 'contract_terms', 'legal_risks', 'obligations'],
            'language': 'legal and compliance',
            'detail_level': 'detailed'
        },
        'manager': {
            'focus': ['action_items', 'deadlines', 'resources', 'team_implications', 'next_steps'],
            'language': 'actionable and operational',
            'detail_level': 'moderate'
        },
        'technical': {
            'focus': ['technical_specifications', 'implementation_details', 'requirements', 'constraints'],
            'language': 'technical and precise',
            'detail_level': 'detailed'
        },
        'general': {
            'focus': ['overview', 'key_points', 'summary'],
            'language': 'general',
            'detail_level': 'summary'
        }
    }
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    
    def summarize_for_role(
        self,
        document_content: str,
        role: str = 'general',
        summary_length: str = 'moderate',
        include_action_items: bool = True
    ) -> Dict[str, Any]:
        """
        Generate role-adaptive summary
        
        Args:
            document_content: Document content to summarize
            role: Target role ('ceo', 'cfo', 'legal', 'manager', 'technical', 'general')
            summary_length: 'brief', 'moderate', or 'detailed'
            include_action_items: Whether to extract action items
            
        Returns:
            Role-adaptive summary with action items
        """
        role_config = self.ROLE_FOCUS.get(role.lower(), self.ROLE_FOCUS['general'])
        
        # Create role-specific prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional document summarizer specializing in {role} perspectives.

Focus on:
{focus_areas}

Language style: {language_style}
Detail level: {detail_level}

Generate a summary that is:
- Relevant to {role} role
- Highlights {focus_areas}
- Uses {language_style} language
- Appropriate {detail_level} level of detail"""),
            ("human", """Document content:
{document}

Generate a {summary_length} summary for a {role} role.

{action_items_instruction}""")
        ])
        
        focus_areas = ', '.join(role_config['focus'])
        action_items_instruction = ""
        if include_action_items:
            action_items_instruction = "Also extract specific action items, deadlines, and responsibilities."
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    role=role.upper(),
                    focus_areas=focus_areas,
                    language_style=role_config['language'],
                    detail_level=role_config['detail_level'],
                    document=document_content[:8000],  # Limit length
                    summary_length=summary_length,
                    action_items_instruction=action_items_instruction
                )
            )
            
            summary = response.content if hasattr(response, 'content') else str(response)
            
            # Extract action items if requested
            action_items = []
            if include_action_items:
                action_items = self._extract_action_items(document_content, role)
            
            return {
                'summary': summary,
                'role': role,
                'summary_length': summary_length,
                'action_items': action_items,
                'focus_areas': role_config['focus']
            }
        
        except Exception as e:
            logger.error(f"Error generating role-based summary: {e}")
            return {
                'summary': f'خطا در تولید خلاصه: {str(e)}',
                'role': role,
                'error': str(e)
            }
    
    def generate_multi_role_summary(
        self,
        document_content: str,
        roles: List[str] = None,
        summary_length: str = 'moderate'
    ) -> Dict[str, Any]:
        """
        Generate summaries for multiple roles
        
        Args:
            document_content: Document content
            roles: List of roles to summarize for
            summary_length: Summary length
            
        Returns:
            Dictionary with summaries for each role
        """
        if not roles:
            roles = ['ceo', 'cfo', 'manager']
        
        summaries = {}
        for role in roles:
            summaries[role] = self.summarize_for_role(
                document_content,
                role=role,
                summary_length=summary_length,
                include_action_items=True
            )
        
        return {
            'document_length': len(document_content),
            'roles': roles,
            'summaries': summaries
        }
    
    def _extract_action_items(
        self,
        document_content: str,
        role: str
    ) -> List[Dict[str, Any]]:
        """Extract action items from document"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract specific action items, deadlines, and responsibilities from the document.
Format as a structured list with:
- Action description
- Responsible party (if mentioned)
- Deadline (if mentioned)
- Priority level"""),
            ("human", """Document:
{document}

Extract action items relevant to {role} role.""")
        ])
        
        try:
            response = self.llm.invoke(
                prompt.format_messages(
                    document=document_content[:4000],
                    role=role
                )
            )
            
            # Parse action items (simple parsing, can be enhanced)
            action_text = response.content if hasattr(response, 'content') else str(response)
            action_items = self._parse_action_items(action_text)
            
            return action_items
        
        except Exception as e:
            logger.error(f"Error extracting action items: {e}")
            return []
    
    def _parse_action_items(self, text: str) -> List[Dict[str, Any]]:
        """Parse action items from text"""
        items = []
        
        # Simple parsing - split by lines and look for action patterns
        lines = text.split('\n')
        current_item = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for action indicators
            if any(indicator in line.lower() for indicator in ['action', 'task', 'deadline', 'responsible', 'action item']):
                if current_item:
                    items.append(current_item)
                
                current_item = {
                    'description': line,
                    'responsible': None,
                    'deadline': None,
                    'priority': 'medium'
                }
            elif current_item:
                # Add to current item
                if 'responsible' in line.lower() or 'مسئول' in line:
                    current_item['responsible'] = line
                elif 'deadline' in line.lower() or 'مهلت' in line or 'date' in line.lower():
                    current_item['deadline'] = line
                else:
                    current_item['description'] += ' ' + line
        
        if current_item:
            items.append(current_item)
        
        return items


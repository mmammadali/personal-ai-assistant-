"""
Search Tools
LangChain tools for cross-agent search and context management
"""
from langchain_core.tools import tool
from typing import Optional, List
from intelligence.context_manager import ContextManager


# Initialize context manager
context_manager = ContextManager()


@tool
def search_across_agents_tool(
    query: str,
    entity_types: Optional[str] = None
) -> str:
    """
    Search across all agents (events, tasks, documents) with a single query.
    
    Args:
        query: Search query string. REQUIRED.
        entity_types: Comma-separated entity types to search (e.g., "event,task"). If not provided, searches all types. OPTIONAL.
        
    Returns:
        Formatted search results from all agents
    """
    try:
        entity_types_list = None
        if entity_types:
            entity_types_list = [t.strip() for t in entity_types.split(',')]
        
        results = context_manager.search_across_agents(query, entity_types_list)
        
        if not results:
            return f"🔍 No results found for: {query}"
        
        result_text = f"🔍 Search Results for: {query}\n"
        result_text += "=" * 50 + "\n\n"
        
        # Events
        if 'events' in results:
            result_text += f"📅 Events ({len(results['events'])}):\n"
            for event in results['events'][:5]:  # Top 5
                result_text += f"   • {event.get('title', 'Untitled')}\n"
                result_text += f"     Date: {event.get('date', 'N/A')}\n"
                if event.get('attendee'):
                    result_text += f"     Attendee: {event['attendee']}\n"
            result_text += "\n"
        
        # Tasks
        if 'tasks' in results:
            result_text += f"📋 Tasks ({len(results['tasks'])}):\n"
            for task in results['tasks'][:5]:  # Top 5
                result_text += f"   • {task.get('description', 'Untitled')}\n"
                result_text += f"     Due: {task.get('due_date', 'N/A')}\n"
                result_text += f"     Status: {task.get('status', 'unknown')}\n"
            result_text += "\n"
        
        return result_text.strip()
    
    except Exception as e:
        return f"❌ Error searching: {str(e)}"


@tool
def get_related_context_tool(
    entity_type: str,
    entity_id: int,
    relationship_type: Optional[str] = None
) -> str:
    """
    Get all entities related to a specific event, task, or document.
    
    Args:
        entity_type: Type of entity - "event", "task", or "document". REQUIRED.
        entity_id: ID of the entity. REQUIRED.
        relationship_type: Filter by relationship type (optional). OPTIONAL.
        
    Returns:
        List of related entities
    """
    try:
        related = context_manager.get_related_entities(
            entity_type=entity_type,
            entity_id=entity_id,
            relationship_type=relationship_type
        )
        
        if not related:
            return f"ℹ️ No related entities found for {entity_type} {entity_id}."
        
        result = f"🔗 Related Entities for {entity_type} {entity_id}:\n\n"
        
        # Group by type
        by_type = {}
        for rel in related:
            rel_type = rel['type']
            if rel_type not in by_type:
                by_type[rel_type] = []
            by_type[rel_type].append(rel)
        
        for rel_type, entities in by_type.items():
            result += f"{rel_type.capitalize()}s ({len(entities)}):\n"
            for entity in entities:
                result += f"   • ID: {entity['id']}"
                if entity.get('relationship'):
                    result += f" ({entity['relationship']})"
                result += "\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error getting related context: {str(e)}"


@tool
def create_context_link_tool(
    source_type: str,
    source_id: int,
    target_type: str,
    target_id: int,
    relationship_type: Optional[str] = None
) -> str:
    """
    Create a link between two entities (e.g., link a task to an event).
    
    Args:
        source_type: Type of source entity - "event", "task", or "document". REQUIRED.
        source_id: ID of source entity. REQUIRED.
        target_type: Type of target entity. REQUIRED.
        target_id: ID of target entity. REQUIRED.
        relationship_type: Type of relationship - "related_to", "depends_on", "references". OPTIONAL.
        
    Returns:
        Success message with link ID
    """
    try:
        link_id = context_manager.create_context_link(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
            relationship_type=relationship_type
        )
        
        return f"✅ Context link created!\n   Link ID: {link_id}\n   {source_type} {source_id} → {target_type} {target_id}\n   Relationship: {relationship_type or 'related_to'}"
    
    except Exception as e:
        return f"❌ Error creating context link: {str(e)}"


@tool
def get_context_summary_tool(
    entity_type: str,
    entity_id: int
) -> str:
    """
    Get comprehensive context summary for an entity including related entities.
    
    Args:
        entity_type: Type of entity - "event", "task", or "document". REQUIRED.
        entity_id: ID of the entity. REQUIRED.
        
    Returns:
        Comprehensive context summary
    """
    try:
        summary = context_manager.get_context_summary(entity_type, entity_id)
        
        result = f"📊 Context Summary for {entity_type} {entity_id}\n"
        result += "=" * 50 + "\n\n"
        
        # Entity details
        entity_details = summary.get('entity_details')
        if entity_details:
            if entity_type == 'event':
                result += f"📅 {entity_details.get('title', 'Untitled')}\n"
                result += f"   Date: {entity_details.get('date', 'N/A')}\n"
                if entity_details.get('attendee'):
                    result += f"   Attendee: {entity_details['attendee']}\n"
            elif entity_type == 'task':
                result += f"📋 {entity_details.get('description', 'Untitled')}\n"
                result += f"   Due: {entity_details.get('due_date', 'N/A')}\n"
                result += f"   Status: {entity_details.get('status', 'unknown')}\n"
        
        # Related entities
        related = summary.get('related_entities', [])
        if related:
            result += f"\n🔗 Related Entities ({len(related)}):\n"
            for rel in related[:5]:
                result += f"   • {rel['type']} {rel['id']}"
                if rel.get('relationship'):
                    result += f" ({rel['relationship']})"
                result += "\n"
        else:
            result += "\nℹ️ No related entities found.\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error getting context summary: {str(e)}"


# Export all search tools
SEARCH_TOOLS = [
    search_across_agents_tool,
    get_related_context_tool,
    create_context_link_tool,
    get_context_summary_tool
]


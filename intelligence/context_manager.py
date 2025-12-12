"""
Context Manager
Manages cross-agent context and relationships
"""
import sqlite3
from typing import List, Dict, Optional, Any
from contextlib import contextmanager
from database import DatabaseManager


class ContextManager:
    """Manages cross-agent context and relationships"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db_path = db_path
        self.db = DatabaseManager(db_path)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_context_link(
        self,
        source_type: str,
        source_id: int,
        target_type: str,
        target_id: int,
        relationship_type: Optional[str] = None
    ) -> int:
        """
        Create a context link between two entities
        
        Args:
            source_type: Type of source entity ('event', 'task', 'document', etc.)
            source_id: ID of source entity
            target_type: Type of target entity
            target_id: ID of target entity
            relationship_type: Type of relationship (e.g., 'related_to', 'depends_on', 'references')
            
        Returns:
            Link ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO context_links (
                    source_type, source_id, target_type, target_id, relationship_type
                )
                VALUES (?, ?, ?, ?, ?)
            """, (source_type, source_id, target_type, target_id, relationship_type))
            return cursor.lastrowid
    
    def get_related_entities(
        self,
        entity_type: str,
        entity_id: int,
        relationship_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Get all entities related to a given entity
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            relationship_type: Filter by relationship type (optional)
            
        Returns:
            List of related entity dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM context_links 
                WHERE (source_type = ? AND source_id = ?)
                   OR (target_type = ? AND target_id = ?)
            """
            params = [entity_type, entity_id, entity_type, entity_id]
            
            if relationship_type:
                query += " AND relationship_type = ?"
                params.append(relationship_type)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Format results
            related = []
            for row in rows:
                link = dict(row)
                if link['source_type'] == entity_type and link['source_id'] == entity_id:
                    related.append({
                        'type': link['target_type'],
                        'id': link['target_id'],
                        'relationship': link.get('relationship_type')
                    })
                else:
                    related.append({
                        'type': link['source_type'],
                        'id': link['source_id'],
                        'relationship': link.get('relationship_type')
                    })
            
            return related
    
    def search_across_agents(
        self,
        query: str,
        entity_types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict]]:
        """
        Search across all agent contexts
        
        Args:
            query: Search query string
            entity_types: List of entity types to search (optional)
            
        Returns:
            Dictionary mapping entity types to search results
        """
        results = {}
        query_lower = query.lower()
        
        # Search events
        if not entity_types or 'event' in entity_types:
            events = self.db.get_events()
            matching_events = [
                e for e in events
                if query_lower in e.get('title', '').lower()
                or query_lower in e.get('description', '').lower()
                or query_lower in e.get('attendee', '').lower()
            ]
            if matching_events:
                results['events'] = matching_events
        
        # Search tasks
        if not entity_types or 'task' in entity_types:
            tasks = self.db.get_tasks()
            matching_tasks = [
                t for t in tasks
                if query_lower in (t.get('description') or '').lower()
                or query_lower in (t.get('project') or '').lower()
            ]
            if matching_tasks:
                results['tasks'] = matching_tasks
        
        return results
    
    def get_context_summary(
        self,
        entity_type: str,
        entity_id: int
    ) -> Dict[str, Any]:
        """
        Get comprehensive context summary for an entity
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            Dictionary with context summary
        """
        # Get related entities
        related = self.get_related_entities(entity_type, entity_id)
        
        # Get entity details
        entity_details = None
        if entity_type == 'event':
            events = self.db.get_events()
            entity_details = next((e for e in events if e.get('id') == entity_id), None)
        elif entity_type == 'task':
            entity_details = self.db.get_task_by_id(entity_id)
        
        return {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'entity_details': entity_details,
            'related_entities': related,
            'related_count': len(related)
        }


"""
Dependency Analyzer
Analyzes and manages task dependencies
"""
import sqlite3
from typing import List, Dict, Optional, Set
from contextlib import contextmanager
from database import DatabaseManager


class DependencyAnalyzer:
    """Analyzes task dependencies and creates dependency graphs"""
    
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
    
    def create_dependency(
        self,
        task_id: int,
        depends_on_task_id: int,
        dependency_type: Optional[str] = None
    ) -> int:
        """
        Create a task dependency relationship
        
        Args:
            task_id: Task that depends on another
            depends_on_task_id: Task that must be completed first
            dependency_type: Type of dependency (e.g., 'blocks', 'requires')
            
        Returns:
            Dependency ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_dependencies (task_id, depends_on_task_id, dependency_type)
                VALUES (?, ?, ?)
            """, (task_id, depends_on_task_id, dependency_type))
            return cursor.lastrowid
    
    def get_task_dependencies(self, task_id: int) -> List[Dict]:
        """
        Get all tasks that a task depends on
        
        Args:
            task_id: Task ID
            
        Returns:
            List of dependency dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT td.*, t.description as depends_on_description, t.status as depends_on_status
                FROM task_dependencies td
                JOIN tasks t ON td.depends_on_task_id = t.id
                WHERE td.task_id = ?
            """, (task_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_blocking_tasks(self, task_id: int) -> List[Dict]:
        """
        Get all tasks that depend on this task (tasks this task blocks)
        
        Args:
            task_id: Task ID
            
        Returns:
            List of tasks that depend on this task
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT td.*, t.description as blocking_task_description, t.status as blocking_task_status
                FROM task_dependencies td
                JOIN tasks t ON td.task_id = t.id
                WHERE td.depends_on_task_id = ?
            """, (task_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def analyze_dependency_chain(self, task_id: int) -> Dict:
        """
        Analyze the full dependency chain for a task
        
        Args:
            task_id: Task ID
            
        Returns:
            Dictionary with dependency chain information
        """
        dependencies = self.get_task_dependencies(task_id)
        blocking = self.get_blocking_tasks(task_id)
        
        # Check if any dependencies are incomplete
        incomplete_dependencies = [
            dep for dep in dependencies
            if dep.get('depends_on_status') != 'done'
        ]
        
        # Check if this task blocks others
        blocked_tasks = [
            block for block in blocking
            if block.get('blocking_task_status') != 'done'
        ]
        
        return {
            'task_id': task_id,
            'dependencies': dependencies,
            'blocking_tasks': blocking,
            'has_incomplete_dependencies': len(incomplete_dependencies) > 0,
            'incomplete_dependencies': incomplete_dependencies,
            'blocks_other_tasks': len(blocked_tasks) > 0,
            'blocked_tasks': blocked_tasks,
            'can_start': len(incomplete_dependencies) == 0
        }
    
    def detect_implicit_dependencies(
        self,
        task_description: str,
        all_tasks: List[Dict]
    ) -> List[int]:
        """
        Detect implicit dependencies from task descriptions
        
        Args:
            task_description: Description of the task
            all_tasks: List of all tasks to check against
            
        Returns:
            List of task IDs that might be dependencies
        """
        desc_lower = task_description.lower()
        potential_deps = []
        
        # Keywords that suggest dependencies
        dependency_keywords = [
            'after', 'بعد از', 'following', 'پس از',
            'once', 'when', 'وقتی که',
            'complete', 'finish', 'تمام شدن'
        ]
        
        # Check if description mentions other tasks
        for task in all_tasks:
            task_desc = task.get('description', '').lower()
            task_id = task.get('id')
            
            # Simple keyword matching (could be enhanced with NLP)
            for keyword in dependency_keywords:
                if keyword in desc_lower:
                    # Check if task description is mentioned
                    if task_desc and any(word in desc_lower for word in task_desc.split()[:3]):
                        potential_deps.append(task_id)
                        break
        
        return potential_deps
    
    def get_execution_order(self, task_ids: List[int]) -> List[int]:
        """
        Get optimal execution order based on dependencies
        
        Args:
            task_ids: List of task IDs to order
            
        Returns:
            Ordered list of task IDs (dependencies first)
        """
        # Build dependency graph
        graph = {task_id: set() for task_id in task_ids}
        
        for task_id in task_ids:
            deps = self.get_task_dependencies(task_id)
            for dep in deps:
                dep_id = dep['depends_on_task_id']
                if dep_id in graph:
                    graph[task_id].add(dep_id)
        
        # Topological sort
        ordered = []
        visited = set()
        temp_visited = set()
        
        def visit(task_id: int):
            if task_id in temp_visited:
                # Circular dependency detected
                return
            if task_id in visited:
                return
            
            temp_visited.add(task_id)
            
            # Visit dependencies first
            for dep_id in graph[task_id]:
                if dep_id in graph:
                    visit(dep_id)
            
            temp_visited.remove(task_id)
            visited.add(task_id)
            ordered.append(task_id)
        
        for task_id in task_ids:
            if task_id not in visited:
                visit(task_id)
        
        return ordered


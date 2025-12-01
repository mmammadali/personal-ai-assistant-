"""
Database management for Iranian Manager Personal Assistant
Handles events and tasks with Jalali date support
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path


class DatabaseManager:
    """Manages SQLite database for events and tasks"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db_path = db_path
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    attendee TEXT,
                    description TEXT,
                    location TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tasks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    due_date TEXT NOT NULL,
                    description TEXT NOT NULL,
                    project TEXT,
                    status TEXT DEFAULT 'undone',
                    attendant TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_title ON events(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
    
    # ============= EVENT OPERATIONS =============
    
    def create_event(
        self,
        date: str,
        title: str,
        attendee: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> int:
        """
        Create a new event
        
        Args:
            date: Event date in Jalali format (YYYY-MM-DD or YYYY/MM/DD)
            title: Event title (required)
            attendee: Attendee name (optional)
            description: Event description (optional)
            location: Event location (optional)
            
        Returns:
            Event ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (date, title, attendee, description, location)
                VALUES (?, ?, ?, ?, ?)
            """, (date, title, attendee, description, location))
            return cursor.lastrowid
    
    def get_events(
        self,
        date: Optional[str] = None,
        title: Optional[str] = None,
        attendee: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events based on filters
        
        Args:
            date: Filter by date (exact match or partial)
            title: Filter by title (case-insensitive partial match)
            attendee: Filter by attendee (case-insensitive partial match)
            
        Returns:
            List of event dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if date:
                query += " AND date LIKE ?"
                params.append(f"%{date}%")
            
            if title:
                query += " AND title LIKE ?"
                params.append(f"%{title}%")
            
            if attendee:
                query += " AND attendee LIKE ?"
                params.append(f"%{attendee}%")
            
            query += " ORDER BY date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    # ============= TASK OPERATIONS =============
    
    def create_task(
        self,
        due_date: str,
        description: str,
        project: Optional[str] = None,
        status: str = "undone",
        attendant: Optional[str] = None
    ) -> int:
        """
        Create a new task
        
        Args:
            due_date: Task due date in Jalali format
            description: Task description (required)
            project: Project name (optional)
            status: Task status (default: "undone")
            attendant: Attendant name (optional)
            
        Returns:
            Task ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (due_date, description, project, status, attendant)
                VALUES (?, ?, ?, ?, ?)
            """, (due_date, description, project, status, attendant))
            return cursor.lastrowid
    
    def get_tasks(
        self,
        due_date: Optional[str] = None,
        project: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
        attendant: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tasks based on filters
        
        Args:
            due_date: Filter by due date (exact or partial)
            project: Filter by project (case-insensitive partial)
            status: Filter by status (exact match)
            description: Filter by description (case-insensitive partial)
            attendant: Filter by attendant (case-insensitive partial)
            
        Returns:
            List of task dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if due_date:
                query += " AND due_date LIKE ?"
                params.append(f"%{due_date}%")
            
            if project:
                query += " AND project LIKE ?"
                params.append(f"%{project}%")
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if description:
                query += " AND description LIKE ?"
                params.append(f"%{description}%")
            
            if attendant:
                query += " AND attendant LIKE ?"
                params.append(f"%{attendant}%")
            
            query += " ORDER BY due_date ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def update_task_status(self, task_id: int, new_status: str) -> bool:
        """
        Update task status
        
        Args:
            task_id: Task ID
            new_status: New status value
            
        Returns:
            True if successful, False if task not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET status = ? WHERE id = ?
            """, (new_status, task_id))
            return cursor.rowcount > 0
    
    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            return dict(row) if row else None


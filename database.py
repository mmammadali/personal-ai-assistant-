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
            
            # Event attendees table for multiple attendees support
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_attendees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    attendee_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE,
                    UNIQUE(event_id, attendee_name)
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
            
            # Energy levels table for productivity tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    hour INTEGER NOT NULL,
                    energy_score REAL,
                    activity_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, hour)
                )
            """)
            
            # Productivity metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS productivity_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    task_completed_count INTEGER DEFAULT 0,
                    meeting_count INTEGER DEFAULT 0,
                    focus_hours REAL DEFAULT 0,
                    peak_hour INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_type TEXT NOT NULL,
                    preference_key TEXT NOT NULL,
                    preference_value TEXT,
                    confidence REAL DEFAULT 1.0,
                    usage_count INTEGER DEFAULT 1,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(preference_type, preference_key)
                )
            """)
            
            # User patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT,
                    frequency INTEGER DEFAULT 1,
                    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Suggestions log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suggestions_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion_type TEXT NOT NULL,
                    suggestion_content TEXT,
                    accepted BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Context links table for cross-agent relationships
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_type TEXT NOT NULL,
                    source_id INTEGER NOT NULL,
                    target_type TEXT NOT NULL,
                    target_id INTEGER NOT NULL,
                    relationship_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Reminders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    reminder_type TEXT NOT NULL,
                    trigger_time TEXT,
                    trigger_location TEXT,
                    trigger_activity TEXT,
                    reminder_text TEXT NOT NULL,
                    related_event_id INTEGER,
                    related_task_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Notifications queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_type TEXT NOT NULL,
                    notification_content TEXT NOT NULL,
                    importance_score REAL DEFAULT 0.5,
                    status TEXT DEFAULT 'pending',
                    delivered_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Task dependencies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_dependencies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    depends_on_task_id INTEGER,
                    dependency_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id),
                    FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id)
                )
            """)
            
            # Document versions table (for RAG enhancements)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_name TEXT NOT NULL,
                    version_number INTEGER NOT NULL,
                    file_path TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(document_name, version_number)
                )
            """)
            
            # Create indexes for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_title ON events(title)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_attendees_event_id ON event_attendees(event_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_attendees_name ON event_attendees(attendee_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_energy_levels_date_hour ON energy_levels(date, hour)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_productivity_metrics_date ON productivity_metrics(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications_queue(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_dependencies_task_id ON task_dependencies(task_id)")
    
    # ============= EVENT OPERATIONS =============
    
    def create_event(
        self,
        date: str,
        title: str,
        attendee: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> int:
        """
        Create a new event
        
        Args:
            date: Event date in Jalali format (YYYY-MM-DD or YYYY/MM/DD)
            title: Event title (required)
            attendee: Single attendee name (optional, for backward compatibility)
            description: Event description (optional)
            location: Event location (optional)
            attendees: List of attendee names (optional, takes precedence over attendee)
            
        Returns:
            Event ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Use attendees list if provided, otherwise use single attendee for backward compatibility
            if attendees is None and attendee:
                attendees = [attendee]
            elif attendees is None:
                attendees = []
            
            # Store first attendee in legacy field for backward compatibility
            legacy_attendee = attendees[0] if attendees else attendee
            
            cursor.execute("""
                INSERT INTO events (date, title, attendee, description, location)
                VALUES (?, ?, ?, ?, ?)
            """, (date, title, legacy_attendee, description, location))
            event_id = cursor.lastrowid
            
            # Store all attendees in the event_attendees table
            for attendee_name in attendees:
                if attendee_name and attendee_name.strip():
                    cursor.execute("""
                        INSERT INTO event_attendees (event_id, attendee_name)
                        VALUES (?, ?)
                    """, (event_id, attendee_name.strip()))
            
            return event_id
    
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
            attendee: Filter by attendee (case-insensitive partial match, searches all attendees)
            
        Returns:
            List of event dictionaries with attendees list
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build base query
            if attendee:
                # Use subquery to find event IDs that match attendee criteria
                # This handles both legacy attendee field and new event_attendees table
                attendee_pattern = f"%{attendee}%"
                
                # First, get event IDs that match attendee in either location
                cursor.execute("""
                    SELECT DISTINCT e.id FROM events e
                    LEFT JOIN event_attendees ea ON e.id = ea.event_id
                    WHERE (e.attendee LIKE ? OR ea.attendee_name LIKE ?)
                """, (attendee_pattern, attendee_pattern))
                matching_event_ids = [row[0] for row in cursor.fetchall()]
                
                if not matching_event_ids:
                    return []
                
                # Now build the main query with the matching event IDs
                placeholders = ','.join(['?'] * len(matching_event_ids))
                query = f"SELECT * FROM events WHERE id IN ({placeholders})"
                params = list(matching_event_ids)
            else:
                query = "SELECT * FROM events WHERE 1=1"
                params = []
            
            # Add date filter
            if date:
                query += " AND date LIKE ?"
                params.append(f"%{date}%")
            
            # Add title filter
            if title:
                query += " AND title LIKE ?"
                params.append(f"%{title}%")
            
            query += " ORDER BY date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts and add attendees list
            events = []
            for row in rows:
                event_dict = dict(row)
                event_id = event_dict['id']
                
                # Get all attendees for this event
                cursor.execute("""
                    SELECT attendee_name FROM event_attendees
                    WHERE event_id = ?
                    ORDER BY attendee_name
                """, (event_id,))
                attendee_rows = cursor.fetchall()
                event_dict['attendees'] = [row['attendee_name'] for row in attendee_rows]
                
                # If no attendees in new table but legacy attendee exists, use it
                if not event_dict['attendees'] and event_dict.get('attendee'):
                    event_dict['attendees'] = [event_dict['attendee']]
                
                events.append(event_dict)
            
            return events
    
    def get_event_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific event by ID
        
        Args:
            event_id: Event ID
            
        Returns:
            Event dictionary with attendees list, or None if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            event_dict = dict(row)
            
            # Get all attendees for this event
            cursor.execute("""
                SELECT attendee_name FROM event_attendees
                WHERE event_id = ?
                ORDER BY attendee_name
            """, (event_id,))
            attendee_rows = cursor.fetchall()
            event_dict['attendees'] = [row['attendee_name'] for row in attendee_rows]
            
            # If no attendees in new table but legacy attendee exists, use it
            if not event_dict['attendees'] and event_dict.get('attendee'):
                event_dict['attendees'] = [event_dict['attendee']]
            
            return event_dict
    
    def update_event(
        self,
        event_id: int,
        date: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> bool:
        """
        Update an existing event
        
        Args:
            event_id: Event ID
            date: New date (optional)
            title: New title (optional)
            description: New description (optional)
            location: New location (optional)
            attendees: New list of attendees (optional, replaces all existing attendees)
            
        Returns:
            True if successful, False if event not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if event exists
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            if not cursor.fetchone():
                return False
            
            # Build update query dynamically
            updates = []
            params = []
            
            if date is not None:
                updates.append("date = ?")
                params.append(date)
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            
            if location is not None:
                updates.append("location = ?")
                params.append(location)
            
            # Update attendees if provided
            if attendees is not None:
                # Delete existing attendees
                cursor.execute("DELETE FROM event_attendees WHERE event_id = ?", (event_id,))
                
                # Insert new attendees
                for attendee_name in attendees:
                    if attendee_name and attendee_name.strip():
                        cursor.execute("""
                            INSERT INTO event_attendees (event_id, attendee_name)
                            VALUES (?, ?)
                        """, (event_id, attendee_name.strip()))
                
                # Update legacy attendee field with first attendee for backward compatibility
                if attendees:
                    updates.append("attendee = ?")
                    params.append(attendees[0])
                else:
                    updates.append("attendee = ?")
                    params.append(None)
            
            # Execute update if there are changes
            if updates:
                params.append(event_id)
                query = f"UPDATE events SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
            
            return True
    
    def delete_event(self, event_id: int) -> bool:
        """
        Delete an event and all its attendees
        
        Args:
            event_id: Event ID
            
        Returns:
            True if successful, False if event not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if event exists
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            if not cursor.fetchone():
                return False
            
            # Delete event (CASCADE will automatically delete attendees)
            cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
            
            return cursor.rowcount > 0
    
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
    
    # ============= ENERGY LEVELS OPERATIONS =============
    
    def get_energy_levels(self, date: Optional[str] = None, hour: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get energy level records"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM energy_levels WHERE 1=1"
            params = []
            
            if date:
                query += " AND date = ?"
                params.append(date)
            
            if hour is not None:
                query += " AND hour = ?"
                params.append(hour)
            
            query += " ORDER BY date DESC, hour ASC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    # ============= PRODUCTIVITY METRICS OPERATIONS =============
    
    def get_productivity_metrics(self, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get productivity metrics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM productivity_metrics WHERE 1=1"
            params = []
            
            if date:
                query += " AND date = ?"
                params.append(date)
            
            query += " ORDER BY date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def update_productivity_metrics(
        self,
        date: str,
        task_completed_count: Optional[int] = None,
        meeting_count: Optional[int] = None,
        focus_hours: Optional[float] = None,
        peak_hour: Optional[int] = None
    ) -> None:
        """Update or create productivity metrics for a date"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if record exists
            cursor.execute("SELECT * FROM productivity_metrics WHERE date = ?", (date,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                updates = []
                params = []
                
                if task_completed_count is not None:
                    updates.append("task_completed_count = task_completed_count + ?")
                    params.append(task_completed_count)
                
                if meeting_count is not None:
                    updates.append("meeting_count = meeting_count + ?")
                    params.append(meeting_count)
                
                if focus_hours is not None:
                    updates.append("focus_hours = focus_hours + ?")
                    params.append(focus_hours)
                
                if peak_hour is not None:
                    updates.append("peak_hour = ?")
                    params.append(peak_hour)
                
                if updates:
                    params.append(date)
                    query = f"UPDATE productivity_metrics SET {', '.join(updates)} WHERE date = ?"
                    cursor.execute(query, params)
            else:
                # Create new
                cursor.execute("""
                    INSERT INTO productivity_metrics 
                    (date, task_completed_count, meeting_count, focus_hours, peak_hour)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    date,
                    task_completed_count or 0,
                    meeting_count or 0,
                    focus_hours or 0.0,
                    peak_hour
                ))


"""
Meeting Database Management
Handles all meeting data storage with SQLite
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import uuid


class MeetingDatabase:
    """Manages SQLite database for meeting operations"""
    
    def __init__(self, db_path: str = "meeting.db"):
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
        """Create all meeting tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Meetings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    date TEXT NOT NULL,
                    duration INTEGER,
                    recording_path TEXT,
                    transcript_path TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transcripts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transcripts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL,
                    speaker_id TEXT,
                    speaker_name TEXT,
                    text TEXT NOT NULL,
                    start_time REAL,
                    end_time REAL,
                    confidence REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)
            
            # Action items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    assignee TEXT,
                    due_date TEXT,
                    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)
            
            # Meeting analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL,
                    speaker_name TEXT,
                    talk_time INTEGER,
                    word_count INTEGER,
                    participation_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)
            
            # Meeting participants table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meeting_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT,
                    role TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_user_id ON meetings(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transcripts_meeting_id ON transcripts(meeting_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_items_meeting_id ON action_items(meeting_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_items_status ON action_items(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_meeting_id ON meeting_analytics(meeting_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_participants_meeting_id ON meeting_participants(meeting_id)")
    
    def create_meeting(
        self,
        user_id: str,
        title: str,
        date: str,
        duration: Optional[int] = None,
        recording_path: Optional[str] = None,
        transcript_path: Optional[str] = None,
        summary: Optional[str] = None
    ) -> int:
        """Create a new meeting record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meetings (user_id, title, date, duration, recording_path, transcript_path, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, title, date, duration, recording_path, transcript_path, summary))
            return cursor.lastrowid
    
    def get_meeting(self, meeting_id: int) -> Optional[Dict[str, Any]]:
        """Get meeting by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_meetings(
        self,
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get meetings with optional date filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM meetings WHERE user_id = ?"
            params = [user_id]
            
            if date_from:
                query += " AND date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND date <= ?"
                params.append(date_to)
            
            query += " ORDER BY date DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_meeting(
        self,
        meeting_id: int,
        title: Optional[str] = None,
        duration: Optional[int] = None,
        recording_path: Optional[str] = None,
        transcript_path: Optional[str] = None,
        summary: Optional[str] = None
    ) -> bool:
        """Update meeting record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if duration is not None:
                updates.append("duration = ?")
                params.append(duration)
            if recording_path is not None:
                updates.append("recording_path = ?")
                params.append(recording_path)
            if transcript_path is not None:
                updates.append("transcript_path = ?")
                params.append(transcript_path)
            if summary is not None:
                updates.append("summary = ?")
                params.append(summary)
            
            if not updates:
                return False
            
            params.append(meeting_id)
            query = f"UPDATE meetings SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            return cursor.rowcount > 0
    
    def add_transcript_segment(
        self,
        meeting_id: int,
        text: str,
        speaker_id: Optional[str] = None,
        speaker_name: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        confidence: Optional[float] = None
    ) -> int:
        """Add a transcript segment"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transcripts (meeting_id, speaker_id, speaker_name, text, start_time, end_time, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (meeting_id, speaker_id, speaker_name, text, start_time, end_time, confidence))
            return cursor.lastrowid
    
    def get_transcript(self, meeting_id: int) -> List[Dict[str, Any]]:
        """Get all transcript segments for a meeting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transcripts 
                WHERE meeting_id = ? 
                ORDER BY start_time ASC, id ASC
            """, (meeting_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_action_item(
        self,
        meeting_id: int,
        description: str,
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
        status: str = "pending"
    ) -> int:
        """Add an action item"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO action_items (meeting_id, description, assignee, due_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (meeting_id, description, assignee, due_date, status))
            return cursor.lastrowid
    
    def get_action_items(
        self,
        meeting_id: Optional[int] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get action items with optional filters"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ai.*, m.user_id, m.title as meeting_title, m.date as meeting_date
                FROM action_items ai
                JOIN meetings m ON ai.meeting_id = m.id
                WHERE 1=1
            """
            params = []
            
            if meeting_id:
                query += " AND ai.meeting_id = ?"
                params.append(meeting_id)
            if user_id:
                query += " AND m.user_id = ?"
                params.append(user_id)
            if status:
                query += " AND ai.status = ?"
                params.append(status)
            
            query += " ORDER BY ai.created_at DESC"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_action_item_status(self, item_id: int, status: str) -> bool:
        """Update action item status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE action_items 
                SET status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (status, item_id))
            return cursor.rowcount > 0
    
    def add_analytics(
        self,
        meeting_id: int,
        speaker_name: str,
        talk_time: int,
        word_count: int,
        participation_score: Optional[float] = None
    ) -> int:
        """Add meeting analytics for a speaker"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meeting_analytics (meeting_id, speaker_name, talk_time, word_count, participation_score)
                VALUES (?, ?, ?, ?, ?)
            """, (meeting_id, speaker_name, talk_time, word_count, participation_score))
            return cursor.lastrowid
    
    def get_analytics(self, meeting_id: int) -> List[Dict[str, Any]]:
        """Get analytics for a meeting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM meeting_analytics 
                WHERE meeting_id = ? 
                ORDER BY talk_time DESC
            """, (meeting_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def add_participant(
        self,
        meeting_id: int,
        name: str,
        email: Optional[str] = None,
        role: Optional[str] = None
    ) -> int:
        """Add a meeting participant"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meeting_participants (meeting_id, name, email, role)
                VALUES (?, ?, ?, ?)
            """, (meeting_id, name, email, role))
            return cursor.lastrowid
    
    def get_participants(self, meeting_id: int) -> List[Dict[str, Any]]:
        """Get participants for a meeting"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM meeting_participants 
                WHERE meeting_id = ?
            """, (meeting_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def search_meetings(
        self,
        user_id: str,
        query: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search meetings by title or summary"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            search_query = """
                SELECT * FROM meetings 
                WHERE user_id = ? 
                AND (title LIKE ? OR summary LIKE ?)
            """
            params = [user_id, f"%{query}%", f"%{query}%"]
            
            if date_from:
                search_query += " AND date >= ?"
                params.append(date_from)
            if date_to:
                search_query += " AND date <= ?"
                params.append(date_to)
            
            search_query += " ORDER BY date DESC LIMIT 50"
            cursor.execute(search_query, params)
            return [dict(row) for row in cursor.fetchall()]


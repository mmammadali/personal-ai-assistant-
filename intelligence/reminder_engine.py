"""
Reminder Engine
Intelligent context-based reminder system
"""
import jdatetime
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import sqlite3
from contextlib import contextmanager
from database import DatabaseManager


class ReminderEngine:
    """Manages intelligent context-based reminders"""
    
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
    
    def create_reminder(
        self,
        reminder_text: str,
        reminder_type: str = "time",
        trigger_time: Optional[str] = None,
        trigger_location: Optional[str] = None,
        trigger_activity: Optional[str] = None,
        related_event_id: Optional[int] = None,
        related_task_id: Optional[int] = None
    ) -> int:
        """
        Create a new reminder
        
        Args:
            reminder_text: Text of the reminder
            reminder_type: Type - "time", "location", "activity", "context"
            trigger_time: Time trigger (Jalali date/time format)
            trigger_location: Location trigger
            trigger_activity: Activity trigger
            related_event_id: Related event ID
            related_task_id: Related task ID
            
        Returns:
            Reminder ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reminders (
                    reminder_type, trigger_time, trigger_location, trigger_activity,
                    reminder_text, related_event_id, related_task_id, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """, (
                reminder_type, trigger_time, trigger_location, trigger_activity,
                reminder_text, related_event_id, related_task_id
            ))
            return cursor.lastrowid
    
    def get_active_reminders(
        self,
        current_time: Optional[str] = None,
        current_location: Optional[str] = None,
        current_activity: Optional[str] = None
    ) -> List[Dict]:
        """
        Get active reminders based on current context
        
        Args:
            current_time: Current time (Jalali format)
            current_location: Current location
            current_activity: Current activity
            
        Returns:
            List of active reminders
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM reminders 
                WHERE status = 'pending'
            """
            params = []
            
            # Time-based reminders
            if current_time:
                query += " AND (trigger_time IS NULL OR trigger_time <= ?)"
                params.append(current_time)
            
            # Location-based reminders
            if current_location:
                query += " AND (trigger_location IS NULL OR trigger_location = ?)"
                params.append(current_location)
            
            # Activity-based reminders
            if current_activity:
                query += " AND (trigger_activity IS NULL OR trigger_activity = ?)"
                params.append(current_activity)
            
            query += " ORDER BY created_at ASC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def mark_reminder_delivered(self, reminder_id: int) -> bool:
        """Mark a reminder as delivered"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE reminders SET status = 'delivered' WHERE id = ?
            """, (reminder_id,))
            return cursor.rowcount > 0
    
    def create_context_reminder(
        self,
        reminder_text: str,
        context_keywords: List[str],
        related_event_id: Optional[int] = None,
        related_task_id: Optional[int] = None
    ) -> int:
        """
        Create a context-based reminder that triggers when keywords appear
        
        Args:
            reminder_text: Text of the reminder
            context_keywords: Keywords that trigger the reminder
            related_event_id: Related event ID
            related_task_id: Related task ID
            
        Returns:
            Reminder ID
        """
        # Store keywords in trigger_activity field (comma-separated)
        trigger_activity = ",".join(context_keywords)
        
        return self.create_reminder(
            reminder_text=reminder_text,
            reminder_type="context",
            trigger_activity=trigger_activity,
            related_event_id=related_event_id,
            related_task_id=related_task_id
        )
    
    def check_context_triggers(
        self,
        current_text: str,
        current_activity: Optional[str] = None
    ) -> List[Dict]:
        """
        Check if current context triggers any reminders
        
        Args:
            current_text: Current conversation/text context
            current_activity: Current activity description
            
        Returns:
            List of triggered reminders
        """
        text_lower = current_text.lower()
        activity_lower = (current_activity or "").lower()
        
        # Get context-based reminders
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM reminders 
                WHERE status = 'pending' 
                AND reminder_type = 'context'
                AND trigger_activity IS NOT NULL
            """)
            rows = cursor.fetchall()
        
        triggered = []
        for row in rows:
            reminder = dict(row)
            keywords = reminder.get('trigger_activity', '').split(',')
            
            # Check if any keyword matches
            for keyword in keywords:
                keyword = keyword.strip().lower()
                if keyword and (keyword in text_lower or keyword in activity_lower):
                    triggered.append(reminder)
                    break
        
        return triggered
    
    def create_smart_reminder_for_event(
        self,
        event_id: int,
        reminder_minutes_before: int = 15
    ) -> Optional[int]:
        """
        Automatically create a reminder for an event
        
        Args:
            event_id: Event ID
            reminder_minutes_before: Minutes before event to remind
            
        Returns:
            Reminder ID or None
        """
        # Find event by ID
        events = self.db.get_events()
        event = next((e for e in events if e.get('id') == event_id), None)
        
        if not event:
            return None
        
        # Calculate reminder time
        try:
            event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d')
            # Extract time from title/description if available
            # For now, default to 9 AM
            reminder_time = event_date.replace(hour=9, minute=0) - jdatetime.timedelta(minutes=reminder_minutes_before)
            
            reminder_text = f"یادآوری: {event.get('title', 'رویداد')} در {event.get('date', '')}"
            
            return self.create_reminder(
                reminder_text=reminder_text,
                reminder_type="time",
                trigger_time=reminder_time.strftime('%Y-%m-%d %H:%M'),
                related_event_id=event_id
            )
        except:
            return None
    
    def create_smart_reminder_for_task(
        self,
        task_id: int,
        days_before_due: int = 1
    ) -> Optional[int]:
        """
        Automatically create a reminder for a task
        
        Args:
            task_id: Task ID
            days_before_due: Days before due date to remind
            
        Returns:
            Reminder ID or None
        """
        task = self.db.get_task_by_id(task_id)
        if not task:
            return None
        
        try:
            due_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d')
            reminder_date = due_date - jdatetime.timedelta(days=days_before_due)
            
            reminder_text = f"یادآوری: {task.get('description', 'وظیفه')} تا {task.get('due_date', '')}"
            
            return self.create_reminder(
                reminder_text=reminder_text,
                reminder_type="time",
                trigger_time=reminder_date.strftime('%Y-%m-%d'),
                related_task_id=task_id
            )
        except:
            return None


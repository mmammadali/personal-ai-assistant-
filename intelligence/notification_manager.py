"""
Notification Manager
Smart notification management with importance scoring and activity detection
"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager
from database import DatabaseManager


class NotificationManager:
    """Manages smart notifications with importance scoring"""
    
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
    
    def create_notification(
        self,
        notification_type: str,
        notification_content: str,
        importance_score: float = 0.5
    ) -> int:
        """
        Create a new notification
        
        Args:
            notification_type: Type of notification (e.g., 'task_due', 'event_soon', 'reminder')
            notification_content: Content of the notification
            importance_score: Importance score (0.0-1.0). Default: 0.5
            
        Returns:
            Notification ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO notifications_queue (
                    notification_type, notification_content, importance_score, status
                )
                VALUES (?, ?, ?, 'pending')
            """, (notification_type, notification_content, importance_score))
            return cursor.lastrowid
    
    def calculate_importance_score(
        self,
        notification_type: str,
        urgency_factor: float = 0.5,
        user_relevance: float = 0.5
    ) -> float:
        """
        Calculate importance score for a notification
        
        Args:
            notification_type: Type of notification
            urgency_factor: Urgency factor (0.0-1.0)
            user_relevance: User relevance factor (0.0-1.0)
            
        Returns:
            Importance score (0.0-1.0)
        """
        # Base importance by type
        type_scores = {
            'task_overdue': 0.9,
            'task_due_today': 0.8,
            'event_starting_soon': 0.7,
            'reminder': 0.6,
            'suggestion': 0.4,
            'update': 0.3
        }
        
        base_score = type_scores.get(notification_type, 0.5)
        
        # Combine with urgency and relevance
        final_score = (base_score * 0.5) + (urgency_factor * 0.3) + (user_relevance * 0.2)
        
        return min(1.0, max(0.0, final_score))
    
    def get_pending_notifications(
        self,
        limit: Optional[int] = None,
        min_importance: float = 0.0
    ) -> List[Dict]:
        """
        Get pending notifications sorted by importance
        
        Args:
            limit: Maximum number of notifications to return
            min_importance: Minimum importance score
            
        Returns:
            List of notification dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT * FROM notifications_queue 
                WHERE status = 'pending' 
                AND importance_score >= ?
                ORDER BY importance_score DESC, created_at ASC
            """
            params = [min_importance]
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def mark_notification_delivered(self, notification_id: int) -> bool:
        """Mark a notification as delivered"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notifications_queue 
                SET status = 'delivered', delivered_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (notification_id,))
            return cursor.rowcount > 0
    
    def batch_create_notifications(
        self,
        notifications: List[Dict]
    ) -> List[int]:
        """
        Create multiple notifications at once
        
        Args:
            notifications: List of notification dictionaries
            
        Returns:
            List of notification IDs
        """
        notification_ids = []
        for notif in notifications:
            notif_id = self.create_notification(
                notification_type=notif.get('type', 'update'),
                notification_content=notif.get('content', ''),
                importance_score=notif.get('importance', 0.5)
            )
            notification_ids.append(notif_id)
        
        return notification_ids
    
    def get_notification_summary(self) -> Dict:
        """
        Get summary of notifications
        
        Returns:
            Dictionary with notification statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM notifications_queue 
                GROUP BY status
            """)
            status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Count by type
            cursor.execute("""
                SELECT notification_type, COUNT(*) as count 
                FROM notifications_queue 
                WHERE status = 'pending'
                GROUP BY notification_type
            """)
            type_counts = {row['notification_type']: row['count'] for row in cursor.fetchall()}
            
            # Average importance
            cursor.execute("""
                SELECT AVG(importance_score) as avg_importance 
                FROM notifications_queue 
                WHERE status = 'pending'
            """)
            avg_importance = cursor.fetchone()['avg_importance'] or 0.0
            
            return {
                'status_counts': status_counts,
                'type_counts': type_counts,
                'avg_importance': avg_importance,
                'pending_count': status_counts.get('pending', 0)
            }


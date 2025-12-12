"""
Follow-up Agent
Tracks and manages action items and meeting follow-ups
"""
from typing import Dict, Any, List, Optional
import logging
import jdatetime

from meeting.database import MeetingDatabase

logger = logging.getLogger(__name__)


class FollowUpAgent:
    """Agent for tracking action items and follow-ups"""
    
    def __init__(self, db: MeetingDatabase):
        """
        Initialize follow-up agent
        
        Args:
            db: MeetingDatabase instance
        """
        self.db = db
    
    def track_action_items(self, meeting_id: int) -> List[Dict[str, Any]]:
        """
        Get all action items for a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            List of action items
        """
        try:
            action_items = self.db.get_action_items(meeting_id=meeting_id)
            return action_items
            
        except Exception as e:
            logger.error(f"Error tracking action items: {e}")
            return []
    
    def get_pending_action_items(
        self,
        user_id: str,
        include_overdue: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get pending action items for a user
        
        Args:
            user_id: User identifier
            include_overdue: Include overdue items
            
        Returns:
            List of pending action items
        """
        try:
            action_items = self.db.get_action_items(
                user_id=user_id,
                status="pending"
            )
            
            # Also get in_progress items
            in_progress = self.db.get_action_items(
                user_id=user_id,
                status="in_progress"
            )
            action_items.extend(in_progress)
            
            # Filter overdue items if requested
            if include_overdue:
                today = jdatetime.date.today()
                for item in action_items:
                    due_date_str = item.get("due_date")
                    if due_date_str:
                        try:
                            # Parse Jalali date
                            parts = due_date_str.split("-")
                            if len(parts) == 3:
                                due_date = jdatetime.date(
                                    int(parts[0]),
                                    int(parts[1]),
                                    int(parts[2])
                                )
                                item["is_overdue"] = due_date < today
                            else:
                                item["is_overdue"] = False
                        except Exception:
                            item["is_overdue"] = False
                    else:
                        item["is_overdue"] = False
            else:
                # Filter out overdue items
                today = jdatetime.date.today()
                filtered_items = []
                for item in action_items:
                    due_date_str = item.get("due_date")
                    if due_date_str:
                        try:
                            parts = due_date_str.split("-")
                            if len(parts) == 3:
                                due_date = jdatetime.date(
                                    int(parts[0]),
                                    int(parts[1]),
                                    int(parts[2])
                                )
                                if due_date >= today:
                                    filtered_items.append(item)
                            else:
                                filtered_items.append(item)
                        except Exception:
                            filtered_items.append(item)
                    else:
                        filtered_items.append(item)
                action_items = filtered_items
            
            # Sort by due date (overdue first, then by date)
            action_items.sort(key=lambda x: (
                not x.get("is_overdue", False),
                x.get("due_date") or "9999-99-99"
            ))
            
            return action_items
            
        except Exception as e:
            logger.error(f"Error getting pending action items: {e}")
            return []
    
    def update_action_item_status(
        self,
        item_id: int,
        status: str
    ) -> bool:
        """
        Update action item status
        
        Args:
            item_id: Action item ID
            status: New status (pending, in_progress, completed, cancelled)
            
        Returns:
            True if successful
        """
        try:
            valid_statuses = ["pending", "in_progress", "completed", "cancelled"]
            if status not in valid_statuses:
                logger.error(f"Invalid status: {status}")
                return False
            
            return self.db.update_action_item_status(item_id, status)
            
        except Exception as e:
            logger.error(f"Error updating action item status: {e}")
            return False
    
    def get_action_item_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of action items for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Action items summary
        """
        try:
            all_items = self.db.get_action_items(user_id=user_id)
            
            summary = {
                "total": len(all_items),
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0,
                "overdue": 0
            }
            
            today = jdatetime.date.today()
            
            for item in all_items:
                status = item.get("status", "pending")
                if status in summary:
                    summary[status] += 1
                
                # Check if overdue
                due_date_str = item.get("due_date")
                if due_date_str and status in ["pending", "in_progress"]:
                    try:
                        parts = due_date_str.split("-")
                        if len(parts) == 3:
                            due_date = jdatetime.date(
                                int(parts[0]),
                                int(parts[1]),
                                int(parts[2])
                            )
                            if due_date < today:
                                summary["overdue"] += 1
                    except Exception:
                        pass
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting action item summary: {e}")
            return {
                "total": 0,
                "pending": 0,
                "in_progress": 0,
                "completed": 0,
                "cancelled": 0,
                "overdue": 0
            }
    
    def get_upcoming_deadlines(
        self,
        user_id: str,
        days_ahead: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get action items with upcoming deadlines
        
        Args:
            user_id: User identifier
            days_ahead: Number of days to look ahead
            
        Returns:
            List of action items with upcoming deadlines
        """
        try:
            pending_items = self.get_pending_action_items(user_id, include_overdue=True)
            
            today = jdatetime.date.today()
            target_date = today + jdatetime.timedelta(days=days_ahead)
            
            upcoming = []
            for item in pending_items:
                due_date_str = item.get("due_date")
                if due_date_str:
                    try:
                        parts = due_date_str.split("-")
                        if len(parts) == 3:
                            due_date = jdatetime.date(
                                int(parts[0]),
                                int(parts[1]),
                                int(parts[2])
                            )
                            if today <= due_date <= target_date:
                                item["days_until_due"] = (due_date - today).days
                                upcoming.append(item)
                    except Exception:
                        pass
            
            # Sort by due date
            upcoming.sort(key=lambda x: x.get("due_date") or "9999-99-99")
            
            return upcoming
            
        except Exception as e:
            logger.error(f"Error getting upcoming deadlines: {e}")
            return []


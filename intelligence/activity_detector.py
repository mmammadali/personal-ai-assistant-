"""
Activity Detector
Detects user activity patterns to optimize notification timing
"""
import jdatetime
from typing import List, Dict, Optional, Any
from database import DatabaseManager


class ActivityDetector:
    """Detects user activity patterns"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
    
    def detect_current_activity(
        self,
        recent_messages: List[str],
        recent_actions: List[str]
    ) -> Dict[str, Any]:
        """
        Detect current user activity from context
        
        Args:
            recent_messages: Recent conversation messages
            recent_actions: Recent actions taken
            
        Returns:
            Dictionary with activity information
        """
        # Analyze messages for activity keywords
        all_text = " ".join(recent_messages + recent_actions).lower()
        
        activity_keywords = {
            'meeting': ['meeting', 'جلسه', 'میتینگ', 'appointment', 'ملاقات'],
            'focus_work': ['task', 'وظیفه', 'work', 'project', 'پروژه', 'code', 'develop'],
            'communication': ['email', 'ایمیل', 'call', 'تماس', 'message', 'پیام'],
            'planning': ['plan', 'برنامه', 'schedule', 'زمانبندی', 'organize'],
            'review': ['review', 'بررسی', 'check', 'چک', 'audit']
        }
        
        detected_activities = []
        for activity, keywords in activity_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                detected_activities.append(activity)
        
        # Determine primary activity
        primary_activity = detected_activities[0] if detected_activities else 'idle'
        
        # Estimate activity intensity
        intensity = 'high' if len(detected_activities) > 2 else 'medium' if detected_activities else 'low'
        
        return {
            'primary_activity': primary_activity,
            'detected_activities': detected_activities,
            'intensity': intensity,
            'is_busy': intensity in ['high', 'medium'] and primary_activity != 'idle'
        }
    
    def should_send_notification(
        self,
        notification_importance: float,
        current_activity: Dict
    ) -> bool:
        """
        Determine if notification should be sent based on current activity
        
        Args:
            notification_importance: Importance score (0.0-1.0)
            current_activity: Current activity information
            
        Returns:
            True if notification should be sent
        """
        # High importance notifications always sent
        if notification_importance >= 0.8:
            return True
        
        # If user is in focus work, only send high importance
        if current_activity.get('primary_activity') == 'focus_work':
            return notification_importance >= 0.7
        
        # If user is in meeting, only send urgent
        if current_activity.get('primary_activity') == 'meeting':
            return notification_importance >= 0.9
        
        # Otherwise, send based on importance threshold
        return notification_importance >= 0.5
    
    def get_optimal_notification_times(
        self,
        date: str
    ) -> List[Dict]:
        """
        Get optimal times to send notifications based on activity patterns
        
        Args:
            date: Target date in Jalali format
            
        Returns:
            List of optimal time windows
        """
        # Get events for the date
        events = self.db.get_events(date=date)
        
        # Identify busy periods (when events are scheduled)
        busy_periods = []
        for event in events:
            # Extract time if available
            title = event.get('title', '').lower()
            # Simple time extraction (could be enhanced)
            busy_periods.append({
                'start': 9,  # Default
                'end': 10,
                'type': 'event'
            })
        
        # Suggest notification windows (gaps between events)
        optimal_windows = [
            {'start': 8, 'end': 9, 'reason': 'Morning check-in'},
            {'start': 12, 'end': 13, 'reason': 'Lunch break'},
            {'start': 17, 'end': 18, 'reason': 'End of day'}
        ]
        
        return optimal_windows
    
    def get_user_availability_status(
        self,
        current_time: Optional[str] = None
    ) -> str:
        """
        Get current user availability status
        
        Args:
            current_time: Current time (default: now)
            
        Returns:
            Availability status ('available', 'busy', 'in_meeting', 'focus_time')
        """
        if not current_time:
            current_time = jdatetime.datetime.now()
        else:
            current_time = jdatetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M')
        
        hour = current_time.hour
        
        # Get events for today
        today = current_time.date().strftime('%Y-%m-%d')
        events = self.db.get_events(date=today)
        
        # Check if in meeting time
        if events:
            # Simplified check - would need time extraction
            return 'in_meeting' if 9 <= hour <= 17 else 'available'
        
        # Check focus time (high energy hours)
        if 9 <= hour <= 11 or 14 <= hour <= 16:
            return 'focus_time'
        
        if 13 <= hour <= 14:
            return 'lunch_break'
        
        return 'available'


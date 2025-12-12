"""
Notification Tools
LangChain tools for smart notification management
"""
from langchain_core.tools import tool
from typing import Optional
import jdatetime
from intelligence.notification_manager import NotificationManager
from intelligence.activity_detector import ActivityDetector


# Initialize managers
notification_manager = NotificationManager()
activity_detector = ActivityDetector()


@tool
def create_notification_tool(
    notification_type: str,
    notification_content: str,
    importance_score: Optional[float] = None
) -> str:
    """
    Create a new notification with smart importance scoring.
    
    Args:
        notification_type: Type of notification - "task_due", "event_soon", "reminder", "suggestion", "update". REQUIRED.
        notification_content: Content of the notification. REQUIRED.
        importance_score: Manual importance score (0.0-1.0). If not provided, will be calculated automatically. OPTIONAL.
        
    Returns:
        Success message with notification ID
    """
    try:
        # Calculate importance if not provided
        if importance_score is None:
            urgency = 0.7 if 'urgent' in notification_content.lower() or 'important' in notification_content.lower() else 0.5
            relevance = 0.8 if notification_type in ['task_due', 'event_soon'] else 0.5
            importance_score = notification_manager.calculate_importance_score(
                notification_type=notification_type,
                urgency_factor=urgency,
                user_relevance=relevance
            )
        
        notification_id = notification_manager.create_notification(
            notification_type=notification_type,
            notification_content=notification_content,
            importance_score=importance_score
        )
        
        return f"✅ Notification created!\n   ID: {notification_id}\n   Type: {notification_type}\n   Importance: {importance_score:.2f}\n   Content: {notification_content}"
    
    except Exception as e:
        return f"❌ Error creating notification: {str(e)}"


@tool
def get_pending_notifications_tool(
    limit: int = 10,
    min_importance: float = 0.0
) -> str:
    """
    Get pending notifications sorted by importance.
    
    Args:
        limit: Maximum number of notifications to return. Default: 10.
        min_importance: Minimum importance score (0.0-1.0). Default: 0.0 (all notifications).
        
    Returns:
        Formatted list of pending notifications
    """
    try:
        notifications = notification_manager.get_pending_notifications(
            limit=limit,
            min_importance=min_importance
        )
        
        if not notifications:
            return "✅ No pending notifications."
        
        result = f"🔔 Pending Notifications ({len(notifications)}):\n\n"
        
        for i, notif in enumerate(notifications, 1):
            importance = notif.get('importance_score', 0.0)
            
            # Importance indicator
            if importance >= 0.8:
                importance_emoji = "🔴"
            elif importance >= 0.6:
                importance_emoji = "🟡"
            else:
                importance_emoji = "🟢"
            
            result += f"{i}. {importance_emoji} [{notif.get('notification_type', 'unknown')}]\n"
            result += f"   {notif.get('notification_content', 'No content')}\n"
            result += f"   Importance: {importance:.2f}\n"
            result += f"   ID: {notif.get('id')}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error getting notifications: {str(e)}"


@tool
def check_notification_timing_tool(
    notification_importance: float,
    current_activity: Optional[str] = None
) -> str:
    """
    Check if it's a good time to send a notification based on current activity.
    
    Args:
        notification_importance: Importance score of the notification (0.0-1.0). REQUIRED.
        current_activity: Current activity description (optional, for better detection). OPTIONAL.
        
    Returns:
        Recommendation on whether to send notification now
    """
    try:
        # Detect current activity
        activity_info = activity_detector.detect_current_activity(
            recent_messages=[current_activity] if current_activity else [],
            recent_actions=[]
        )
        
        should_send = activity_detector.should_send_notification(
            notification_importance=notification_importance,
            current_activity=activity_info
        )
        
        result = f"⏰ Notification Timing Check\n"
        result += f"   Importance: {notification_importance:.2f}\n"
        result += f"   Current Activity: {activity_info.get('primary_activity', 'unknown')}\n"
        result += f"   Activity Intensity: {activity_info.get('intensity', 'unknown')}\n\n"
        
        if should_send:
            result += "✅ Recommendation: Send notification now\n"
            result += "   (High importance or user is available)"
        else:
            result += "⏸️ Recommendation: Delay notification\n"
            result += f"   (User is {activity_info.get('primary_activity', 'busy')}, wait for better time)"
        
        return result
    
    except Exception as e:
        return f"❌ Error checking notification timing: {str(e)}"


@tool
def get_notification_summary_tool() -> str:
    """
    Get summary statistics of notifications.
    
    Returns:
        Notification summary with counts and statistics
    """
    try:
        summary = notification_manager.get_notification_summary()
        
        result = "📊 Notification Summary\n"
        result += "=" * 30 + "\n\n"
        
        result += f"📬 Pending: {summary.get('pending_count', 0)}\n"
        
        status_counts = summary.get('status_counts', {})
        for status, count in status_counts.items():
            if status != 'pending':
                result += f"   {status.capitalize()}: {count}\n"
        
        result += f"\n📈 Average Importance: {summary.get('avg_importance', 0.0):.2f}\n\n"
        
        type_counts = summary.get('type_counts', {})
        if type_counts:
            result += "By Type:\n"
            for notif_type, count in type_counts.items():
                result += f"   {notif_type}: {count}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error getting notification summary: {str(e)}"


@tool
def get_optimal_notification_times_tool(
    date: Optional[str] = None
) -> str:
    """
    Get optimal time windows for sending notifications based on schedule.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). Default: today.
        
    Returns:
        List of optimal notification time windows
    """
    try:
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        optimal_windows = activity_detector.get_optimal_notification_times(date)
        
        result = f"⏰ Optimal Notification Times for {date}\n\n"
        
        for i, window in enumerate(optimal_windows, 1):
            start = window.get('start', 0)
            end = window.get('end', 0)
            reason = window.get('reason', 'Good time window')
            
            result += f"{i}. {start}:00 - {end}:00\n"
            result += f"   💡 {reason}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error getting optimal notification times: {str(e)}"


# Export all notification tools
NOTIFICATION_TOOLS = [
    create_notification_tool,
    get_pending_notifications_tool,
    check_notification_timing_tool,
    get_notification_summary_tool,
    get_optimal_notification_times_tool
]


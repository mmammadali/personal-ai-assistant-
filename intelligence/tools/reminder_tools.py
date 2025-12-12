"""
Reminder Tools
LangChain tools for intelligent context-based reminders
"""
from langchain_core.tools import tool
from typing import Optional, List
import jdatetime
from intelligence.reminder_engine import ReminderEngine


# Initialize reminder engine
reminder_engine = ReminderEngine()


@tool
def create_reminder_tool(
    reminder_text: str,
    reminder_type: str = "time",
    trigger_time: Optional[str] = None,
    trigger_location: Optional[str] = None,
    trigger_activity: Optional[str] = None
) -> str:
    """
    Create a new reminder with context awareness.
    
    Args:
        reminder_text: Text of the reminder. REQUIRED.
        reminder_type: Type of reminder - "time", "location", "activity", or "context". Default: "time".
        trigger_time: Time trigger in Jalali format (YYYY-MM-DD or YYYY-MM-DD HH:MM). OPTIONAL.
        trigger_location: Location trigger (e.g., "office", "home"). OPTIONAL.
        trigger_activity: Activity trigger (e.g., "meeting", "call"). OPTIONAL.
        
    Returns:
        Success message with reminder ID
    """
    try:
        reminder_id = reminder_engine.create_reminder(
            reminder_text=reminder_text,
            reminder_type=reminder_type,
            trigger_time=trigger_time,
            trigger_location=trigger_location,
            trigger_activity=trigger_activity
        )
        
        result = f"✅ Reminder created successfully!\n"
        result += f"   Reminder ID: {reminder_id}\n"
        result += f"   Text: {reminder_text}\n"
        result += f"   Type: {reminder_type}\n"
        
        if trigger_time:
            result += f"   Trigger Time: {trigger_time}\n"
        if trigger_location:
            result += f"   Trigger Location: {trigger_location}\n"
        if trigger_activity:
            result += f"   Trigger Activity: {trigger_activity}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error creating reminder: {str(e)}"


@tool
def create_context_reminder_tool(
    reminder_text: str,
    context_keywords: str,
    related_event_id: Optional[int] = None,
    related_task_id: Optional[int] = None
) -> str:
    """
    Create a context-based reminder that triggers when specific keywords appear in conversation.
    
    Args:
        reminder_text: Text of the reminder. REQUIRED.
        context_keywords: Comma-separated keywords that trigger the reminder (e.g., "meeting,client,call"). REQUIRED.
        related_event_id: Related event ID. OPTIONAL.
        related_task_id: Related task ID. OPTIONAL.
        
    Returns:
        Success message with reminder ID
    """
    try:
        keywords_list = [k.strip() for k in context_keywords.split(',')]
        
        reminder_id = reminder_engine.create_context_reminder(
            reminder_text=reminder_text,
            context_keywords=keywords_list,
            related_event_id=related_event_id,
            related_task_id=related_task_id
        )
        
        result = f"✅ Context reminder created!\n"
        result += f"   Reminder ID: {reminder_id}\n"
        result += f"   Text: {reminder_text}\n"
        result += f"   Triggers on: {', '.join(keywords_list)}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error creating context reminder: {str(e)}"


@tool
def create_smart_event_reminder_tool(
    event_id: int,
    minutes_before: int = 15
) -> str:
    """
    Automatically create a smart reminder for an event (e.g., 15 minutes before).
    
    Args:
        event_id: Event ID to create reminder for. REQUIRED.
        minutes_before: Minutes before event to remind. Default: 15.
        
    Returns:
        Success message with reminder details
    """
    try:
        reminder_id = reminder_engine.create_smart_reminder_for_event(
            event_id=event_id,
            reminder_minutes_before=minutes_before
        )
        
        if reminder_id:
            return f"✅ Smart reminder created for event {event_id}!\n   Reminder ID: {reminder_id}\n   Will remind {minutes_before} minutes before the event."
        else:
            return f"❌ Could not create reminder. Event {event_id} not found."
    
    except Exception as e:
        return f"❌ Error creating smart event reminder: {str(e)}"


@tool
def create_smart_task_reminder_tool(
    task_id: int,
    days_before_due: int = 1
) -> str:
    """
    Automatically create a smart reminder for a task (e.g., 1 day before due date).
    
    Args:
        task_id: Task ID to create reminder for. REQUIRED.
        days_before_due: Days before due date to remind. Default: 1.
        
    Returns:
        Success message with reminder details
    """
    try:
        reminder_id = reminder_engine.create_smart_reminder_for_task(
            task_id=task_id,
            days_before_due=days_before_due
        )
        
        if reminder_id:
            return f"✅ Smart reminder created for task {task_id}!\n   Reminder ID: {reminder_id}\n   Will remind {days_before_due} day(s) before due date."
        else:
            return f"❌ Could not create reminder. Task {task_id} not found."
    
    except Exception as e:
        return f"❌ Error creating smart task reminder: {str(e)}"


@tool
def get_active_reminders_tool(
    current_time: Optional[str] = None,
    current_location: Optional[str] = None
) -> str:
    """
    Get all active reminders based on current context (time, location).
    
    Args:
        current_time: Current time in Jalali format (YYYY-MM-DD or YYYY-MM-DD HH:MM). Default: now.
        current_location: Current location. OPTIONAL.
        
    Returns:
        List of active reminders
    """
    try:
        if not current_time:
            current_time = jdatetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        reminders = reminder_engine.get_active_reminders(
            current_time=current_time,
            current_location=current_location
        )
        
        if not reminders:
            return "✅ No active reminders at this time."
        
        result = f"🔔 Active Reminders ({len(reminders)}):\n\n"
        
        for i, reminder in enumerate(reminders, 1):
            result += f"{i}. {reminder.get('reminder_text', 'Untitled')}\n"
            result += f"   Type: {reminder.get('reminder_type', 'unknown')}\n"
            
            if reminder.get('trigger_time'):
                result += f"   Time: {reminder['trigger_time']}\n"
            if reminder.get('trigger_location'):
                result += f"   Location: {reminder['trigger_location']}\n"
            if reminder.get('trigger_activity'):
                result += f"   Activity: {reminder['trigger_activity']}\n"
            
            result += f"   ID: {reminder.get('id')}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error getting active reminders: {str(e)}"


# Export all reminder tools
REMINDER_TOOLS = [
    create_reminder_tool,
    create_context_reminder_tool,
    create_smart_event_reminder_tool,
    create_smart_task_reminder_tool,
    get_active_reminders_tool
]


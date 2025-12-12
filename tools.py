"""
LangChain tools for Iranian Manager Personal Assistant
All tools with proper schemas, validation, and Jalali date support
"""
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
import jdatetime
import re
from database import DatabaseManager
from intelligence.date_parser import NaturalDateParser


# Initialize database manager
db = DatabaseManager()


def validate_jalali_date(date_str: str) -> str:
    """
    Validate and normalize Jalali date format
    
    Args:
        date_str: Date string in various formats (YYYY-MM-DD, YYYY/MM/DD, etc.)
        
    Returns:
        Normalized date string (YYYY-MM-DD)
        
    Raises:
        ValueError: If date format is invalid
    """
    # Remove extra spaces
    date_str = date_str.strip()
    
    # Try natural language parsing first (Persian/English, relative, weekdays)
    parser = NaturalDateParser()
    parsed_natural = parser.parse(date_str)
    if parsed_natural:
        date_str = parsed_natural
    
    # Replace forward slashes with hyphens
    date_str = date_str.replace("/", "-")
    
    # Try to parse the date
    try:
        parts = date_str.split("-")
        if len(parts) == 3:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            # Validate using jdatetime
            jdate = jdatetime.date(year, month, day)
            return jdate.strftime("%Y-%m-%d")
        else:
            raise ValueError("Date must have year, month, and day")
    except Exception as e:
        raise ValueError(f"Invalid Jalali date format: {date_str}. Expected format: YYYY-MM-DD or YYYY/MM/DD. Error: {str(e)}")


# ===================== EVENT TOOLS =====================

@tool
def create_event_tool(
    date: str,
    title: str,
    attendee: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None
) -> str:
    """
    Create a new calendar event.
    
    Args:
        date: Event date in Jalali format (YYYY-MM-DD or YYYY/MM/DD). REQUIRED.
        title: Event title. REQUIRED.
        attendee: Name of single attendee (for backward compatibility). OPTIONAL.
        description: Event description. OPTIONAL.
        location: Event location. OPTIONAL.
        attendees: List of attendee names (takes precedence over attendee). OPTIONAL.
        
    Returns:
        Success message with event ID
        
    Note: This tool should only be called after user confirmation.
    """
    try:
        # Validate date
        normalized_date = validate_jalali_date(date)
        
        # Create event
        event_id = db.create_event(
            date=normalized_date,
            title=title,
            attendee=attendee,
            description=description,
            location=location,
            attendees=attendees
        )
        
        # Get created event to show attendees
        event = db.get_event_by_id(event_id)
        attendees_str = ", ".join(event.get('attendees', [])) if event and event.get('attendees') else (attendee or "None")
        
        return f"✅ Event created successfully! Event ID: {event_id}, Date: {normalized_date}, Title: {title}, Attendees: {attendees_str}"
    
    except ValueError as e:
        return f"❌ Date validation error: {str(e)}"
    except Exception as e:
        return f"❌ Error creating event: {str(e)}"


@tool
def get_event_tool(
    date: Optional[str] = None,
    title: Optional[str] = None,
    attendee: Optional[str] = None
) -> str:
    """
    Get calendar events based on search criteria.
    
    Args:
        date: Filter by date (Jalali format, can be partial like "1403-05"). OPTIONAL.
        title: Filter by title (partial match, case-insensitive). OPTIONAL.
        attendee: Filter by attendee name (partial match, case-insensitive). OPTIONAL.
        
    Returns:
        List of matching events or message if none found
        
    Note: At least one filter parameter should be provided. Can combine multiple filters.
    """
    try:
        # Normalize date if provided
        if date:
            parsed = NaturalDateParser().parse(date)
            if parsed:
                date = parsed
            elif date:
                date = date.replace("/", "-")
        
        # Query database
        events = db.get_events(date=date, title=title, attendee=attendee)
        
        if not events:
            filters = []
            if date:
                filters.append(f"date={date}")
            if title:
                filters.append(f"title={title}")
            if attendee:
                filters.append(f"attendee={attendee}")
            filter_str = ", ".join(filters) if filters else "no filters"
            return f"📅 No events found matching: {filter_str}"
        
        # Format results
        result = f"📅 Found {len(events)} event(s):\n\n"
        for i, event in enumerate(events, 1):
            result += f"{i}. **{event['title']}**\n"
            result += f"   📆 Date: {event['date']}\n"
            # Show attendees from new table or legacy field
            attendees = event.get('attendees', [])
            if not attendees and event.get('attendee'):
                attendees = [event['attendee']]
            if attendees:
                if len(attendees) == 1:
                    result += f"   👤 Attendee: {attendees[0]}\n"
                else:
                    result += f"   👥 Attendees: {', '.join(attendees)}\n"
            if event['description']:
                result += f"   📝 Description: {event['description']}\n"
            if event['location']:
                result += f"   📍 Location: {event['location']}\n"
            result += f"   🆔 ID: {event['id']}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error retrieving events: {str(e)}"


@tool
def update_event_tool(
    event_id: int,
    date: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None
) -> str:
    """
    Update an existing calendar event. You can update any field(s) of the event.
    
    Args:
        event_id: Event ID to update. REQUIRED.
        date: New event date in Jalali format (YYYY-MM-DD or YYYY/MM/DD). OPTIONAL.
        title: New event title. OPTIONAL.
        description: New event description. OPTIONAL.
        location: New event location. OPTIONAL.
        attendees: New list of attendee names (replaces all existing attendees). OPTIONAL.
        
    Returns:
        Success message with updated event details
        
    Note: This tool should only be called after user confirmation.
          Provide at least one field to update (besides event_id).
    """
    try:
        # Check if event exists
        event = db.get_event_by_id(event_id)
        if not event:
            return f"❌ Event with ID {event_id} not found."
        
        # Normalize date if provided
        normalized_date = None
        if date:
            normalized_date = validate_jalali_date(date)
        
        # Update event
        success = db.update_event(
            event_id=event_id,
            date=normalized_date,
            title=title,
            description=description,
            location=location,
            attendees=attendees
        )
        
        if not success:
            return f"❌ Failed to update event with ID {event_id}"
        
        # Get updated event to show changes
        updated_event = db.get_event_by_id(event_id)
        attendees_list = updated_event.get('attendees', [])
        attendees_str = ", ".join(attendees_list) if attendees_list else "None"
        
        result = f"✅ Event updated successfully!\n"
        result += f"   🆔 Event ID: {event_id}\n"
        result += f"   📆 Date: {updated_event['date']}\n"
        result += f"   📝 Title: {updated_event['title']}\n"
        if updated_event.get('description'):
            result += f"   📄 Description: {updated_event['description']}\n"
        if updated_event.get('location'):
            result += f"   📍 Location: {updated_event['location']}\n"
        result += f"   👥 Attendees: {attendees_str}\n"
        
        return result
    
    except ValueError as e:
        return f"❌ Date validation error: {str(e)}"
    except Exception as e:
        return f"❌ Error updating event: {str(e)}"


@tool
def delete_event_tool(event_id: int) -> str:
    """
    Delete a calendar event permanently.
    
    Args:
        event_id: Event ID to delete. REQUIRED.
        
    Returns:
        Success message or error
        
    Note: This tool should only be called after user confirmation.
          This action cannot be undone.
    """
    try:
        # Check if event exists and get details for confirmation message
        event = db.get_event_by_id(event_id)
        if not event:
            return f"❌ Event with ID {event_id} not found."
        
        # Delete event
        success = db.delete_event(event_id)
        
        if success:
            return f"✅ Event deleted successfully!\n   🆔 Event ID: {event_id}\n   📝 Title: {event['title']}\n   📆 Date: {event['date']}"
        else:
            return f"❌ Failed to delete event with ID {event_id}"
    
    except Exception as e:
        return f"❌ Error deleting event: {str(e)}"


# ===================== TASK TOOLS =====================

@tool
def create_task_tool(
    due_date: str,
    description: str,
    project: Optional[str] = None,
    status: str = "undone",
    attendant: Optional[str] = None
) -> str:
    """
    Create a new task.
    
    Args:
        due_date: Task due date in Jalali format (YYYY-MM-DD or YYYY/MM/DD). REQUIRED.
        description: Task description. REQUIRED.
        project: Project name. OPTIONAL.
        status: Task status (default: "undone"). OPTIONAL.
        attendant: Attendant name. OPTIONAL.
        
    Returns:
        Success message with task ID
        
    Note: This tool should only be called after user confirmation.
    """
    try:
        # Validate date
        normalized_date = validate_jalali_date(due_date)
        
        # Create task
        task_id = db.create_task(
            due_date=normalized_date,
            description=description,
            project=project,
            status=status,
            attendant=attendant
        )
        
        return f"✅ Task created successfully! Task ID: {task_id}, Due: {normalized_date}, Description: {description}"
    
    except ValueError as e:
        return f"❌ Date validation error: {str(e)}"
    except Exception as e:
        return f"❌ Error creating task: {str(e)}"


@tool
def get_task_tool(
    due_date: Optional[str] = None,
    project: Optional[str] = None,
    status: Optional[str] = None,
    description: Optional[str] = None,
    attendant: Optional[str] = None
) -> str:
    """
    Get tasks based on search criteria.
    
    Args:
        due_date: Filter by due date (Jalali format, can be partial). OPTIONAL.
        project: Filter by project name (partial match, case-insensitive). OPTIONAL.
        status: Filter by status (exact match, e.g., "undone", "done", "in_progress"). OPTIONAL.
        description: Filter by description (partial match, case-insensitive). OPTIONAL.
        attendant: Filter by attendant name (partial match, case-insensitive). OPTIONAL.
        
    Returns:
        List of matching tasks or message if none found
        
    Note: At least one filter parameter should be provided. Can combine multiple filters.
    """
    try:
        # Normalize date if provided
        if due_date:
            parsed = NaturalDateParser().parse(due_date)
            if parsed:
                due_date = parsed
            else:
                due_date = validate_jalali_date(due_date)
        
        # Query database
        tasks = db.get_tasks(due_date=due_date, project=project, status=status, description=description, attendant=attendant)
        
        if not tasks:
            filters = []
            if due_date:
                filters.append(f"due_date={due_date}")
            if project:
                filters.append(f"project={project}")
            if status:
                filters.append(f"status={status}")
            if description:
                filters.append(f"description={description}")
            if attendant:
                filters.append(f"attendant={attendant}")
            filter_str = ", ".join(filters) if filters else "no filters"
            return f"📋 No tasks found matching: {filter_str}"
        
        # Format results
        result = f"📋 Found {len(tasks)} task(s):\n\n"
        for i, task in enumerate(tasks, 1):
            status_emoji = "✅" if task['status'] == "done" else "⏳" if task['status'] == "in_progress" else "⭕"
            result += f"{i}. {status_emoji} **{task['description']}**\n"
            result += f"   📆 Due: {task['due_date']}\n"
            result += f"   🔖 Status: {task['status']}\n"
            if task['project']:
                result += f"   📁 Project: {task['project']}\n"
            if task['attendant']:
                result += f"   👤 Attendant: {task['attendant']}\n"
            result += f"   🆔 ID: {task['id']}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error retrieving tasks: {str(e)}"


@tool
def update_task_status_tool(
    new_status: str,
    due_date: Optional[str] = None,
    description: Optional[str] = None,
    project: Optional[str] = None,
    attendant: Optional[str] = None,
    task_id: Optional[int] = None
) -> str:
    """
    Update the status of an existing task by finding it using various query parameters.
    
    Args:
        new_status: New status value (e.g., "done", "in_progress", "undone", "cancelled"). REQUIRED.
        due_date: Filter by due date (Jalali format, can be partial). OPTIONAL.
        description: Filter by description (partial match, case-insensitive). OPTIONAL.
        project: Filter by project name (partial match, case-insensitive). OPTIONAL.
        attendant: Filter by attendant name (partial match, case-insensitive). OPTIONAL.
        task_id: Direct task ID if known. OPTIONAL.
        
    Returns:
        Success message or error
        
    Note: This tool should only be called after user confirmation.
          Provide at least one query parameter to identify the task.
          If multiple tasks match, user will need to provide more specific criteria.
    """
    try:
        # If task_id is provided directly, use it
        if task_id:
            task = db.get_task_by_id(task_id)
            if not task:
                return f"❌ Task with ID {task_id} not found."
            
            # Update status
            success = db.update_task_status(task_id, new_status)
            
            if success:
                return f"✅ Task status updated successfully!\n   Task ID: {task_id}\n   Description: {task['description']}\n   Old status: {task['status']}\n   New status: {new_status}"
            else:
                return f"❌ Failed to update task status for ID {task_id}"
        
        # Otherwise, search for the task using provided criteria
        # Normalize date if provided
        if due_date:
            parsed = NaturalDateParser().parse(due_date)
            if parsed:
                due_date = parsed
            else:
                due_date = validate_jalali_date(due_date)
        
        # Search for matching tasks using all provided criteria
        tasks = db.get_tasks(due_date=due_date, project=project, description=description, attendant=attendant)
        
        if not tasks:
            criteria = []
            if due_date:
                criteria.append(f"due_date={due_date}")
            if description:
                criteria.append(f"description={description}")
            if project:
                criteria.append(f"project={project}")
            if attendant:
                criteria.append(f"attendant={attendant}")
            criteria_str = ", ".join(criteria) if criteria else "no criteria"
            return f"❌ No tasks found matching: {criteria_str}"
        
        if len(tasks) > 1:
            # Multiple tasks found, list them
            result = f"⚠️ Found {len(tasks)} matching tasks. Please be more specific or provide the task ID:\n\n"
            for i, task in enumerate(tasks, 1):
                status_emoji = "✅" if task['status'] == "done" else "⏳" if task['status'] == "in_progress" else "⭕"
                result += f"{i}. {status_emoji} **{task['description']}**\n"
                result += f"   📆 Due: {task['due_date']}\n"
                result += f"   🔖 Status: {task['status']}\n"
                if task['project']:
                    result += f"   📁 Project: {task['project']}\n"
                if task['attendant']:
                    result += f"   👤 Attendant: {task['attendant']}\n"
                result += f"   🆔 ID: {task['id']}\n\n"
            return result.strip()
        
        # Exactly one task found, update it
        task = tasks[0]
        success = db.update_task_status(task['id'], new_status)
        
        if success:
            return f"✅ Task status updated successfully!\n   Task ID: {task['id']}\n   Description: {task['description']}\n   Due Date: {task['due_date']}\n   Project: {task.get('project', 'N/A')}\n   Old status: {task['status']}\n   New status: {new_status}"
        else:
            return f"❌ Failed to update task status for task ID {task['id']}"
    
    except Exception as e:
        return f"❌ Error updating task status: {str(e)}"


# Import calendar optimization tools
try:
    from intelligence.tools.calendar_tools import CALENDAR_TOOLS
    CALENDAR_TOOLS_AVAILABLE = True
except ImportError:
    CALENDAR_TOOLS_AVAILABLE = False
    CALENDAR_TOOLS = []

# Import task prediction tools
try:
    from intelligence.tools.task_prediction_tools import TASK_PREDICTION_TOOLS
    TASK_PREDICTION_TOOLS_AVAILABLE = True
except ImportError:
    TASK_PREDICTION_TOOLS_AVAILABLE = False
    TASK_PREDICTION_TOOLS = []

# Import reminder tools
try:
    from intelligence.tools.reminder_tools import REMINDER_TOOLS
    REMINDER_TOOLS_AVAILABLE = True
except ImportError:
    REMINDER_TOOLS_AVAILABLE = False
    REMINDER_TOOLS = []

# Import notification tools
try:
    from intelligence.tools.notification_tools import NOTIFICATION_TOOLS
    NOTIFICATION_TOOLS_AVAILABLE = True
except ImportError:
    NOTIFICATION_TOOLS_AVAILABLE = False
    NOTIFICATION_TOOLS = []

# Import summary tools
try:
    from intelligence.tools.summary_tools import SUMMARY_TOOLS
    SUMMARY_TOOLS_AVAILABLE = True
except ImportError:
    SUMMARY_TOOLS_AVAILABLE = False
    SUMMARY_TOOLS = []

# Import search tools
try:
    from intelligence.tools.search_tools import SEARCH_TOOLS
    SEARCH_TOOLS_AVAILABLE = True
except ImportError:
    SEARCH_TOOLS_AVAILABLE = False
    SEARCH_TOOLS = []

# Export all tools
ALL_TOOLS = [
    create_event_tool,
    get_event_tool,
    update_event_tool,
    delete_event_tool,
    create_task_tool,
    get_task_tool,
    update_task_status_tool
]

# Add calendar tools if available
if CALENDAR_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(CALENDAR_TOOLS)

# Add task prediction tools if available
if TASK_PREDICTION_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(TASK_PREDICTION_TOOLS)

# Add reminder tools if available
if REMINDER_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(REMINDER_TOOLS)

# Add notification tools if available
if NOTIFICATION_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(NOTIFICATION_TOOLS)

# Add summary tools if available
if SUMMARY_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(SUMMARY_TOOLS)

# Add search tools if available
if SEARCH_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(SEARCH_TOOLS)

# ===================== PHASE 2 TOOLS =====================

# Import insight tools (Phase 2.1)
try:
    from intelligence.tools.insight_tools import ALL_INSIGHT_TOOLS
    INSIGHT_TOOLS_AVAILABLE = True
except ImportError:
    INSIGHT_TOOLS_AVAILABLE = False
    ALL_INSIGHT_TOOLS = []

# Import learning tools (Phase 2.2)
try:
    from intelligence.tools.learning_tools import ALL_LEARNING_TOOLS
    LEARNING_TOOLS_AVAILABLE = True
except ImportError:
    LEARNING_TOOLS_AVAILABLE = False
    ALL_LEARNING_TOOLS = []

# Import automation tools (Phase 2.3)
try:
    from intelligence.tools.automation_tools import ALL_AUTOMATION_TOOLS
    AUTOMATION_TOOLS_AVAILABLE = True
except ImportError:
    AUTOMATION_TOOLS_AVAILABLE = False
    ALL_AUTOMATION_TOOLS = []

# Import document tools (Phase 2.10)
try:
    from intelligence.tools.document_tools import ALL_DOCUMENT_TOOLS
    DOCUMENT_TOOLS_AVAILABLE = True
except ImportError:
    DOCUMENT_TOOLS_AVAILABLE = False
    ALL_DOCUMENT_TOOLS = []

# Add Phase 2 tools if available
if INSIGHT_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(ALL_INSIGHT_TOOLS)

if LEARNING_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(ALL_LEARNING_TOOLS)

if AUTOMATION_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(ALL_AUTOMATION_TOOLS)

if DOCUMENT_TOOLS_AVAILABLE:
    ALL_TOOLS.extend(ALL_DOCUMENT_TOOLS)


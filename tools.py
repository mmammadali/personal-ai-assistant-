"""
LangChain tools for Iranian Manager Personal Assistant
All tools with proper schemas, validation, and Jalali date support
"""
from langchain_core.tools import tool
from typing import Optional, List, Dict, Any
import jdatetime
import re
from database import DatabaseManager


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
    location: Optional[str] = None
) -> str:
    """
    Create a new calendar event.
    
    Args:
        date: Event date in Jalali format (YYYY-MM-DD or YYYY/MM/DD). REQUIRED.
        title: Event title. REQUIRED.
        attendee: Name of attendee(s). OPTIONAL.
        description: Event description. OPTIONAL.
        location: Event location. OPTIONAL.
        
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
            location=location
        )
        
        return f"✅ Event created successfully! Event ID: {event_id}, Date: {normalized_date}, Title: {title}"
    
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
            # Allow partial dates for queries
            if date.count("-") == 2 or date.count("/") == 2:
                date = validate_jalali_date(date)
            else:
                # Partial date, just normalize separators
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
            if event['attendee']:
                result += f"   👤 Attendee: {event['attendee']}\n"
            if event['description']:
                result += f"   📝 Description: {event['description']}\n"
            if event['location']:
                result += f"   📍 Location: {event['location']}\n"
            result += f"   🆔 ID: {event['id']}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error retrieving events: {str(e)}"


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
            if due_date.count("-") == 2 or due_date.count("/") == 2:
                due_date = validate_jalali_date(due_date)
            else:
                due_date = due_date.replace("/", "-")
        
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
            if due_date.count("-") == 2 or due_date.count("/") == 2:
                due_date = validate_jalali_date(due_date)
            else:
                due_date = due_date.replace("/", "-")
        
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


# Export all tools
ALL_TOOLS = [
    create_event_tool,
    get_event_tool,
    create_task_tool,
    get_task_tool,
    update_task_status_tool
]


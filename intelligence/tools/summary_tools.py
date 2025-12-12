"""
Summary Tools
LangChain tools for generating smart summaries
"""
from langchain_core.tools import tool
from typing import Optional
import jdatetime
from intelligence.summarizers.daily_summarizer import DailySummarizer
from intelligence.summarizers.weekly_summarizer import WeeklySummarizer


# Initialize summarizers
daily_summarizer = DailySummarizer()
weekly_summarizer = WeeklySummarizer()


@tool
def generate_daily_summary_tool(
    date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive daily summary of events, tasks, and productivity.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). Default: today.
        
    Returns:
        Formatted daily summary
    """
    try:
        summary = daily_summarizer.generate_daily_summary(date)
        
        result = f"📅 خلاصه روزانه - {summary['date']}\n"
        result += "=" * 50 + "\n\n"
        result += summary['summary_text']
        
        return result
    
    except Exception as e:
        return f"❌ Error generating daily summary: {str(e)}"


@tool
def generate_weekly_summary_tool(
    week_start_date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive weekly summary of activities and productivity.
    
    Args:
        week_start_date: Start date of week in Jalali format (YYYY-MM-DD). Default: start of current week.
        
    Returns:
        Formatted weekly summary
    """
    try:
        summary = weekly_summarizer.generate_weekly_summary(week_start_date)
        
        result = f"📊 خلاصه هفتگی\n"
        result += f"از {summary['week_start']} تا {summary['week_end']}\n"
        result += "=" * 50 + "\n\n"
        result += summary['summary_text']
        
        return result
    
    except Exception as e:
        return f"❌ Error generating weekly summary: {str(e)}"


@tool
def generate_task_summary_tool(
    date: Optional[str] = None,
    project: Optional[str] = None
) -> str:
    """
    Generate a summary of tasks for a specific date or project.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). OPTIONAL.
        project: Project name to filter by. OPTIONAL.
        
    Returns:
        Formatted task summary
    """
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        if date:
            tasks = db.get_tasks(due_date=date)
        elif project:
            tasks = db.get_tasks(project=project)
        else:
            # Get all undone tasks
            tasks = db.get_tasks(status='undone')
            tasks.extend(db.get_tasks(status='in_progress'))
        
        if not tasks:
            return "✅ No tasks found."
        
        completed = [t for t in tasks if t.get('status') == 'done']
        pending = [t for t in tasks if t.get('status') != 'done']
        
        result = f"📋 Task Summary\n"
        if date:
            result += f"Date: {date}\n"
        if project:
            result += f"Project: {project}\n"
        result += "=" * 30 + "\n\n"
        
        result += f"Total: {len(tasks)}\n"
        result += f"✅ Completed: {len(completed)}\n"
        result += f"⏳ Pending: {len(pending)}\n\n"
        
        if pending:
            result += "Pending Tasks:\n"
            for task in pending[:10]:
                result += f"   • {task.get('description', 'Untitled')}\n"
                result += f"     Due: {task.get('due_date', 'N/A')}\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error generating task summary: {str(e)}"


@tool
def generate_event_summary_tool(
    date: Optional[str] = None,
    days_ahead: int = 7
) -> str:
    """
    Generate a summary of upcoming events.
    
    Args:
        date: Start date in Jalali format (YYYY-MM-DD). Default: today.
        days_ahead: Number of days ahead to include. Default: 7.
        
    Returns:
        Formatted event summary
    """
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        start_date = jdatetime.datetime.strptime(date, '%Y-%m-%d').date()
        end_date = start_date + jdatetime.timedelta(days=days_ahead)
        
        all_events = db.get_events()
        upcoming_events = []
        
        for event in all_events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if start_date <= event_date <= end_date:
                    upcoming_events.append(event)
            except:
                continue
        
        if not upcoming_events:
            return f"✅ No events in the next {days_ahead} days."
        
        # Sort by date
        upcoming_events.sort(key=lambda x: x.get('date', ''))
        
        result = f"📅 Upcoming Events (Next {days_ahead} days)\n"
        result += "=" * 40 + "\n\n"
        
        for event in upcoming_events:
            result += f"📆 {event.get('date', 'N/A')}\n"
            result += f"   {event.get('title', 'Untitled')}\n"
            if event.get('attendee'):
                result += f"   👤 {event['attendee']}\n"
            if event.get('location'):
                result += f"   📍 {event['location']}\n"
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error generating event summary: {str(e)}"


# Export all summary tools
SUMMARY_TOOLS = [
    generate_daily_summary_tool,
    generate_weekly_summary_tool,
    generate_task_summary_tool,
    generate_event_summary_tool
]


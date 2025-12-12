"""
Task Prediction Tools
LangChain tools for predictive task management and morning briefing
"""
from langchain_core.tools import tool
from typing import Optional
import jdatetime
from intelligence.task_predictor import TaskPredictor
from intelligence.dependency_analyzer import DependencyAnalyzer
from intelligence.calendar_optimizer import CalendarOptimizer
from intelligence.energy_analyzer import EnergyAnalyzer


# Initialize predictors
task_predictor = TaskPredictor()
dependency_analyzer = DependencyAnalyzer()
calendar_optimizer = CalendarOptimizer()
energy_analyzer = EnergyAnalyzer()


@tool
def generate_morning_briefing_tool(
    date: Optional[str] = None
) -> str:
    """
    Generate a comprehensive morning briefing with prioritized tasks, schedule suggestions, and calendar overview.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). If not provided, uses today.
        
    Returns:
        Formatted morning briefing with tasks, events, and schedule suggestions
    """
    try:
        briefing = task_predictor.generate_morning_briefing(date)
        
        result = f"🌅 Morning Briefing - {briefing['date']}\n"
        result += "=" * 50 + "\n\n"
        
        # Events today
        if briefing['events']:
            result += f"📅 Events Today ({len(briefing['events'])}):\n"
            for event in briefing['events'][:5]:  # Top 5 events
                result += f"   • {event.get('title', 'Untitled')}\n"
                if event.get('attendee'):
                    result += f"     👤 {event['attendee']}\n"
                if event.get('location'):
                    result += f"     📍 {event['location']}\n"
            result += "\n"
        
        # Prioritized tasks
        if briefing['prioritized_tasks']:
            result += f"📋 Priority Tasks ({briefing['tasks_count']} total):\n\n"
            
            for i, item in enumerate(briefing['prioritized_tasks'], 1):
                task = item['task']
                priority = item['priority']
                est_hours = item['estimated_hours']
                
                # Priority indicator
                if priority >= 50:
                    priority_emoji = "🔴"
                elif priority >= 20:
                    priority_emoji = "🟡"
                else:
                    priority_emoji = "🟢"
                
                result += f"{i}. {priority_emoji} {task.get('description', 'Untitled')}\n"
                result += f"   📆 Due: {task.get('due_date', 'N/A')}\n"
                result += f"   ⏱️ Estimated: {est_hours:.1f}h\n"
                result += f"   📊 Priority: {priority:.1f}\n"
                
                if task.get('project'):
                    result += f"   📁 Project: {task['project']}\n"
                
                # Check dependencies
                deps = dependency_analyzer.get_task_dependencies(task.get('id', 0))
                if deps:
                    incomplete = [d for d in deps if d.get('depends_on_status') != 'done']
                    if incomplete:
                        result += f"   ⚠️ Depends on {len(incomplete)} incomplete task(s)\n"
                
                result += "\n"
        
        # Schedule suggestion
        total_hours = briefing['total_estimated_hours']
        result += f"⏰ Total Estimated Time: {total_hours:.1f} hours\n\n"
        
        # Get optimal deep work hours
        optimal_hours = energy_analyzer.get_optimal_deep_work_hours()
        if optimal_hours:
            result += "💡 Suggested Focus Times:\n"
            for hour, score in optimal_hours[:3]:
                hour_str = f"{hour}:00"
                result += f"   • {hour_str} (Energy: {score:.2f})\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error generating morning briefing: {str(e)}"


@tool
def predict_task_priorities_tool(
    date: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Predict and rank task priorities based on due dates, dependencies, and patterns.
    
    Args:
        date: Reference date in Jalali format (YYYY-MM-DD). Default: today.
        limit: Maximum number of tasks to return. Default: 10.
        
    Returns:
        Formatted list of prioritized tasks
    """
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Get all undone tasks
        all_tasks = db.get_tasks(status='undone')
        all_tasks.extend(db.get_tasks(status='in_progress'))
        
        # Predict priorities
        prioritized = task_predictor.predict_task_priorities(all_tasks, date)
        
        if not prioritized:
            return "✅ No tasks to prioritize. All tasks are complete!"
        
        result = f"📊 Task Priority Prediction (Top {limit}):\n\n"
        
        for i, (task, priority) in enumerate(prioritized[:limit], 1):
            # Priority indicator
            if priority >= 50:
                priority_emoji = "🔴 URGENT"
            elif priority >= 20:
                priority_emoji = "🟡 HIGH"
            else:
                priority_emoji = "🟢 NORMAL"
            
            result += f"{i}. {priority_emoji} - Priority: {priority:.1f}\n"
            result += f"   📝 {task.get('description', 'Untitled')}\n"
            result += f"   📆 Due: {task.get('due_date', 'N/A')}\n"
            result += f"   🔖 Status: {task.get('status', 'undone')}\n"
            
            if task.get('project'):
                result += f"   📁 Project: {task['project']}\n"
            
            # Check dependencies
            task_id = task.get('id')
            if task_id:
                deps = dependency_analyzer.get_task_dependencies(task_id)
                incomplete = [d for d in deps if d.get('depends_on_status') != 'done']
                if incomplete:
                    result += f"   ⚠️ Blocked by {len(incomplete)} incomplete dependency(ies)\n"
            
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error predicting priorities: {str(e)}"


@tool
def estimate_completion_time_tool(
    description: str,
    project: Optional[str] = None
) -> str:
    """
    Estimate task completion time based on historical data and task characteristics.
    
    Args:
        description: Task description. REQUIRED.
        project: Project name (optional, for project-specific estimates).
        
    Returns:
        Estimated completion time with explanation
    """
    try:
        estimated_hours = task_predictor.estimate_completion_time(description, project)
        
        # Format time estimate
        if estimated_hours < 1.0:
            time_str = f"{int(estimated_hours * 60)} minutes"
        elif estimated_hours == 1.0:
            time_str = "1 hour"
        else:
            time_str = f"{estimated_hours:.1f} hours"
        
        result = f"⏱️ Time Estimate for: {description}\n\n"
        result += f"Estimated Duration: {time_str}\n"
        
        # Add context
        if estimated_hours <= 0.5:
            result += "💡 This is a quick task - good for filling gaps in your schedule."
        elif estimated_hours <= 2.0:
            result += "💡 This is a moderate task - plan a focused time block."
        else:
            result += "💡 This is a longer task - consider breaking it into smaller chunks."
        
        if project:
            result += f"\n📁 Project: {project}"
        
        return result
    
    except Exception as e:
        return f"❌ Error estimating completion time: {str(e)}"


@tool
def analyze_task_dependencies_tool(
    task_id: Optional[int] = None,
    description: Optional[str] = None
) -> str:
    """
    Analyze task dependencies - what tasks must be completed first, and what tasks are blocked.
    
    Args:
        task_id: Task ID to analyze. OPTIONAL.
        description: Task description to search for. OPTIONAL.
        
    Returns:
        Dependency analysis report
    """
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        # Find task if description provided
        if description and not task_id:
            tasks = db.get_tasks(description=description)
            if tasks:
                task_id = tasks[0].get('id')
        
        if not task_id:
            return "❌ Please provide either task_id or description to analyze dependencies."
        
        # Get dependency analysis
        analysis = dependency_analyzer.analyze_dependency_chain(task_id)
        
        result = f"🔗 Dependency Analysis for Task ID {task_id}\n"
        result += "=" * 50 + "\n\n"
        
        # Dependencies (what this task depends on)
        if analysis['dependencies']:
            result += f"📥 This task depends on {len(analysis['dependencies'])} task(s):\n\n"
            for dep in analysis['dependencies']:
                status_emoji = "✅" if dep.get('depends_on_status') == 'done' else "⏳"
                result += f"   {status_emoji} Task {dep['depends_on_task_id']}: {dep.get('depends_on_description', 'N/A')}\n"
                result += f"      Status: {dep.get('depends_on_status', 'unknown')}\n"
                if dep.get('dependency_type'):
                    result += f"      Type: {dep['dependency_type']}\n"
                result += "\n"
        else:
            result += "✅ No dependencies - this task can be started immediately.\n\n"
        
        # Blocking tasks (what depends on this task)
        if analysis['blocking_tasks']:
            result += f"📤 This task blocks {len(analysis['blocking_tasks'])} task(s):\n\n"
            for block in analysis['blocking_tasks']:
                result += f"   ⏳ Task {block['task_id']}: {block.get('blocking_task_description', 'N/A')}\n"
                result += f"      Status: {block.get('blocking_task_status', 'unknown')}\n\n"
        else:
            result += "ℹ️ No tasks depend on this task.\n\n"
        
        # Summary
        if analysis['can_start']:
            result += "✅ Status: Ready to start\n"
        else:
            result += "⚠️ Status: Blocked - complete dependencies first\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error analyzing dependencies: {str(e)}"


@tool
def suggest_task_schedule_tool(
    date: Optional[str] = None
) -> str:
    """
    Suggest optimal task schedule based on productivity patterns, energy levels, and task priorities.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). Default: today.
        
    Returns:
        Suggested task schedule with time blocks
    """
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        # Get tasks for the date
        tasks = db.get_tasks()
        today = jdatetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        # Filter relevant tasks
        relevant_tasks = []
        for task in tasks:
            try:
                due_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date <= today + jdatetime.timedelta(days=7) and task['status'] != 'done':
                    relevant_tasks.append(task)
            except:
                continue
        
        # Predict priorities
        prioritized = task_predictor.predict_task_priorities(relevant_tasks, date)
        
        # Get optimal hours
        optimal_deep_work = energy_analyzer.get_optimal_deep_work_hours()
        optimal_meetings = energy_analyzer.get_optimal_meeting_hours()
        
        result = f"📅 Suggested Task Schedule for {date}\n"
        result += "=" * 50 + "\n\n"
        
        # Morning block (9-12)
        result += "🌅 Morning Block (9:00 - 12:00) - High Energy\n"
        morning_tasks = [t for t, p in prioritized if p >= 30][:2]
        for task in morning_tasks:
            est_time = task_predictor.estimate_completion_time(task.get('description', ''))
            result += f"   • {task.get('description', 'Untitled')} ({est_time:.1f}h)\n"
        result += "\n"
        
        # Afternoon block (14-17)
        result += "☀️ Afternoon Block (14:00 - 17:00) - Moderate Energy\n"
        afternoon_tasks = [t for t, p in prioritized if 10 <= p < 30][:2]
        for task in afternoon_tasks:
            est_time = task_predictor.estimate_completion_time(task.get('description', ''))
            result += f"   • {task.get('description', 'Untitled')} ({est_time:.1f}h)\n"
        result += "\n"
        
        # Quick tasks (anytime)
        result += "⚡ Quick Tasks (Fill gaps)\n"
        quick_tasks = [t for t, p in prioritized if p < 10][:3]
        for task in quick_tasks:
            est_time = task_predictor.estimate_completion_time(task.get('description', ''))
            if est_time <= 0.5:
                result += f"   • {task.get('description', 'Untitled')} ({est_time:.1f}h)\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error suggesting schedule: {str(e)}"


# Export all task prediction tools
TASK_PREDICTION_TOOLS = [
    generate_morning_briefing_tool,
    predict_task_priorities_tool,
    estimate_completion_time_tool,
    analyze_task_dependencies_tool,
    suggest_task_schedule_tool
]


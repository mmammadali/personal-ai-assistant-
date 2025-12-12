"""
Weekly Summarizer
Generates weekly summaries of activities and productivity
"""
import jdatetime
from typing import Dict, List, Any, Optional
from database import DatabaseManager


class WeeklySummarizer:
    """Generates weekly activity summaries"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
    
    def generate_weekly_summary(
        self,
        week_start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly summary
        
        Args:
            week_start_date: Start date of week in Jalali format. Default: start of current week.
            
        Returns:
            Dictionary with weekly summary
        """
        if not week_start_date:
            today = jdatetime.date.today()
            # Get start of week (Saturday in Jalali calendar)
            days_since_saturday = (today.weekday() + 2) % 7
            week_start = today - jdatetime.timedelta(days=days_since_saturday)
            week_start_date = week_start.strftime('%Y-%m-%d')
        
        week_start = jdatetime.datetime.strptime(week_start_date, '%Y-%m-%d').date()
        week_end = week_start + jdatetime.timedelta(days=6)
        
        # Get all events in the week
        all_events = self.db.get_events()
        week_events = []
        for event in all_events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if week_start <= event_date <= week_end:
                    week_events.append(event)
            except:
                continue
        
        # Get all tasks in the week
        all_tasks = self.db.get_tasks()
        week_tasks = []
        completed_tasks = []
        for task in all_tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if week_start <= task_date <= week_end:
                    week_tasks.append(task)
                    if task.get('status') == 'done':
                        completed_tasks.append(task)
            except:
                continue
        
        # Get productivity metrics for the week
        all_metrics = self.db.get_productivity_metrics()
        week_metrics = []
        for metric in all_metrics:
            try:
                metric_date = jdatetime.datetime.strptime(metric['date'], '%Y-%m-%d').date()
                if week_start <= metric_date <= week_end:
                    week_metrics.append(metric)
            except:
                continue
        
        # Calculate totals
        total_tasks_completed = sum(m.get('task_completed_count', 0) for m in week_metrics)
        total_meetings = sum(m.get('meeting_count', 0) for m in week_metrics)
        total_focus_hours = sum(m.get('focus_hours', 0) for m in week_metrics)
        
        summary = {
            'week_start': week_start_date,
            'week_end': week_end.strftime('%Y-%m-%d'),
            'events_count': len(week_events),
            'tasks_total': len(week_tasks),
            'tasks_completed': len(completed_tasks),
            'total_tasks_completed': total_tasks_completed,
            'total_meetings': total_meetings,
            'total_focus_hours': total_focus_hours,
            'completion_rate': len(completed_tasks) / max(len(week_tasks), 1),
            'summary_text': self._generate_summary_text(
                week_events, week_tasks, completed_tasks,
                total_tasks_completed, total_meetings, total_focus_hours
            )
        }
        
        return summary
    
    def _generate_summary_text(
        self,
        events: List[Dict],
        tasks: List[Dict],
        completed_tasks: List[Dict],
        total_completed: int,
        total_meetings: int,
        total_focus_hours: float
    ) -> str:
        """Generate human-readable weekly summary text"""
        lines = []
        
        lines.append("📊 خلاصه هفتگی:")
        lines.append("=" * 30)
        
        # Events
        lines.append(f"\n📅 رویدادها: {len(events)}")
        
        # Tasks
        completion_rate = len(completed_tasks) / max(len(tasks), 1) * 100
        lines.append(f"\n📋 وظایف:")
        lines.append(f"   کل: {len(tasks)}")
        lines.append(f"   تکمیل شده: {len(completed_tasks)} ({completion_rate:.1f}%)")
        
        # Productivity
        lines.append(f"\n📊 بهره‌وری:")
        lines.append(f"   ✅ وظایف تکمیل شده: {total_completed}")
        lines.append(f"   📅 جلسات: {total_meetings}")
        lines.append(f"   ⏰ ساعات تمرکز: {total_focus_hours:.1f}")
        
        return "\n".join(lines)


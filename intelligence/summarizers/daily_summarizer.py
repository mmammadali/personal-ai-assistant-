"""
Daily Summarizer
Generates daily summaries of activities, tasks, and events
"""
import jdatetime
from typing import Dict, List, Any
from database import DatabaseManager


class DailySummarizer:
    """Generates daily activity summaries"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
    
    def generate_daily_summary(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate comprehensive daily summary
        
        Args:
            date: Target date in Jalali format (YYYY-MM-DD). Default: today.
            
        Returns:
            Dictionary with daily summary
        """
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        # Get events for the day
        events = self.db.get_events(date=date)
        
        # Get tasks due or completed on this day
        tasks = self.db.get_tasks(due_date=date)
        completed_tasks = [t for t in tasks if t.get('status') == 'done']
        
        # Get productivity metrics
        metrics = self.db.get_productivity_metrics(date=date)
        daily_metrics = metrics[0] if metrics else None
        
        summary = {
            'date': date,
            'events_count': len(events),
            'events': events,
            'tasks_total': len(tasks),
            'tasks_completed': len(completed_tasks),
            'tasks_pending': len([t for t in tasks if t.get('status') != 'done']),
            'productivity_metrics': daily_metrics,
            'summary_text': self._generate_summary_text(events, tasks, completed_tasks, daily_metrics)
        }
        
        return summary
    
    def _generate_summary_text(
        self,
        events: List[Dict],
        tasks: List[Dict],
        completed_tasks: List[Dict],
        metrics: Optional[Dict]
    ) -> str:
        """Generate human-readable summary text"""
        lines = []
        
        # Events summary
        if events:
            lines.append(f"📅 {len(events)} رویداد:")
            for event in events[:5]:  # Top 5
                lines.append(f"   • {event.get('title', 'Untitled')}")
        else:
            lines.append("📅 هیچ رویدادی ثبت نشده")
        
        # Tasks summary
        if tasks:
            lines.append(f"\n📋 {len(tasks)} وظیفه:")
            lines.append(f"   ✅ تکمیل شده: {len(completed_tasks)}")
            lines.append(f"   ⏳ در انتظار: {len(tasks) - len(completed_tasks)}")
            
            if completed_tasks:
                lines.append("\n   تکمیل شده‌ها:")
                for task in completed_tasks[:3]:
                    lines.append(f"      • {task.get('description', 'Untitled')}")
        else:
            lines.append("\n📋 هیچ وظیفه‌ای ثبت نشده")
        
        # Productivity summary
        if metrics:
            lines.append(f"\n📊 آمار بهره‌وری:")
            if metrics.get('task_completed_count'):
                lines.append(f"   ✅ وظایف تکمیل شده: {metrics['task_completed_count']}")
            if metrics.get('meeting_count'):
                lines.append(f"   📅 جلسات: {metrics['meeting_count']}")
            if metrics.get('focus_hours'):
                lines.append(f"   ⏰ ساعات تمرکز: {metrics['focus_hours']:.1f}")
        
        return "\n".join(lines)


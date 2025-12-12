"""
Task Predictor
Predicts task priorities and completion times based on historical data
"""
import jdatetime
from typing import List, Dict, Optional, Tuple, Any
from datetime import timedelta
from database import DatabaseManager
from collections import defaultdict


class TaskPredictor:
    """Predicts task priorities and completion times"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
    
    def analyze_task_completion_patterns(
        self,
        days_back: int = 60
    ) -> Dict[str, Any]:
        """
        Analyze patterns in task completion
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with completion pattern statistics
        """
        tasks = self.db.get_tasks()
        
        # Filter recent tasks
        today = jdatetime.date.today()
        cutoff_date = today - jdatetime.timedelta(days=days_back)
        
        recent_tasks = []
        for task in tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if task_date >= cutoff_date:
                    recent_tasks.append(task)
            except:
                continue
        
        # Analyze completion patterns
        completed_tasks = [t for t in recent_tasks if t['status'] == 'done']
        overdue_tasks = []
        on_time_tasks = []
        
        for task in completed_tasks:
            try:
                due_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                # Estimate completion date (simplified - would need created_at tracking)
                if task.get('created_at'):
                    # Would need to parse created_at to calculate actual completion time
                    on_time_tasks.append(task)
                else:
                    on_time_tasks.append(task)  # Assume on-time for now
            except:
                pass
        
        # Calculate average completion time by project
        project_stats = defaultdict(lambda: {'count': 0, 'avg_days': 0})
        
        # Analyze by description keywords
        keyword_stats = defaultdict(int)
        for task in completed_tasks:
            desc = task.get('description', '').lower()
            # Common keywords
            keywords = ['email', 'call', 'meeting', 'report', 'review', 'update']
            for keyword in keywords:
                if keyword in desc:
                    keyword_stats[keyword] += 1
        
        return {
            'total_tasks': len(recent_tasks),
            'completed_count': len(completed_tasks),
            'completion_rate': len(completed_tasks) / max(len(recent_tasks), 1),
            'project_stats': dict(project_stats),
            'keyword_frequency': dict(keyword_stats)
        }
    
    def estimate_completion_time(
        self,
        description: str,
        project: Optional[str] = None
    ) -> float:
        """
        Estimate task completion time based on historical data
        
        Args:
            description: Task description
            project: Project name (optional)
            
        Returns:
            Estimated completion time in hours
        """
        desc_lower = description.lower()
        
        # Base time estimates by keyword
        keyword_times = {
            'email': 0.25,  # 15 minutes
            'call': 0.5,    # 30 minutes
            'meeting': 1.0,  # 1 hour
            'report': 2.0,   # 2 hours
            'review': 1.5,   # 1.5 hours
            'update': 0.5,   # 30 minutes
            'prepare': 1.0,  # 1 hour
            'analyze': 2.0,  # 2 hours
            'write': 1.5,    # 1.5 hours
            'design': 3.0,   # 3 hours
            'develop': 4.0,  # 4 hours
            'test': 1.0,     # 1 hour
        }
        
        # Find matching keywords
        estimated_time = 1.0  # Default 1 hour
        for keyword, time in keyword_times.items():
            if keyword in desc_lower:
                estimated_time = max(estimated_time, time)
        
        # Adjust based on description length (longer descriptions = more complex)
        word_count = len(description.split())
        if word_count > 20:
            estimated_time *= 1.5
        elif word_count > 10:
            estimated_time *= 1.2
        
        return min(estimated_time, 8.0)  # Cap at 8 hours
    
    def predict_task_priorities(
        self,
        tasks: List[Dict],
        date: Optional[str] = None
    ) -> List[Tuple[Dict, float]]:
        """
        Predict task priorities based on due date, dependencies, and patterns
        
        Args:
            tasks: List of task dictionaries
            date: Reference date (default: today)
            
        Returns:
            List of (task, priority_score) tuples, sorted by priority
        """
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        today = jdatetime.datetime.strptime(date, '%Y-%m-%d').date()
        
        prioritized = []
        
        for task in tasks:
            try:
                due_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                days_until_due = (due_date - today).days
                
                # Calculate priority score
                priority = 0.0
                
                # Urgency factor (closer due date = higher priority)
                if days_until_due < 0:
                    priority += 100  # Overdue tasks get highest priority
                elif days_until_due == 0:
                    priority += 50   # Due today
                elif days_until_due <= 1:
                    priority += 30  # Due tomorrow
                elif days_until_due <= 3:
                    priority += 20  # Due this week
                elif days_until_due <= 7:
                    priority += 10  # Due next week
                
                # Status factor
                if task['status'] == 'undone':
                    priority += 10
                elif task['status'] == 'in_progress':
                    priority += 5
                
                # Project factor (tasks with projects might be more important)
                if task.get('project'):
                    priority += 5
                
                prioritized.append((task, priority))
            
            except:
                # If date parsing fails, give default priority
                prioritized.append((task, 5.0))
        
        # Sort by priority (highest first)
        prioritized.sort(key=lambda x: x[1], reverse=True)
        
        return prioritized
    
    def generate_morning_briefing(
        self,
        date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate morning briefing with prioritized tasks and schedule suggestions
        
        Args:
            date: Target date (default: today)
            
        Returns:
            Dictionary with briefing content
        """
        if not date:
            date = jdatetime.date.today().strftime('%Y-%m-%d')
        
        # Get tasks due today or upcoming
        today = jdatetime.datetime.strptime(date, '%Y-%m-%d').date()
        week_end = today + jdatetime.timedelta(days=7)
        
        all_tasks = self.db.get_tasks()
        
        # Filter relevant tasks
        relevant_tasks = []
        for task in all_tasks:
            try:
                due_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date <= week_end and task['status'] != 'done':
                    relevant_tasks.append(task)
            except:
                continue
        
        # Get events for today
        events_today = self.db.get_events(date=date)
        
        # Predict priorities
        prioritized_tasks = self.predict_task_priorities(relevant_tasks, date)
        
        # Estimate completion times
        task_schedule = []
        total_estimated_hours = 0.0
        
        for task, priority in prioritized_tasks[:10]:  # Top 10 tasks
            estimated_time = self.estimate_completion_time(
                task.get('description', ''),
                task.get('project')
            )
            total_estimated_hours += estimated_time
            
            task_schedule.append({
                'task': task,
                'priority': priority,
                'estimated_hours': estimated_time
            })
        
        return {
            'date': date,
            'tasks_count': len(relevant_tasks),
            'events_today': len(events_today),
            'prioritized_tasks': task_schedule[:5],  # Top 5 for briefing
            'total_estimated_hours': total_estimated_hours,
            'events': events_today
        }


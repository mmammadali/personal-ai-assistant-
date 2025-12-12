"""
Productivity Analyzer
Analyzes productivity patterns, energy dips, stress signals, and generates insights
"""
import jdatetime
from typing import List, Dict, Optional, Tuple, Any
from datetime import timedelta
from collections import defaultdict
from database import DatabaseManager
from intelligence.energy_analyzer import EnergyAnalyzer


class ProductivityAnalyzer:
    """Analyzes productivity patterns and generates insights"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
        self.energy_analyzer = EnergyAnalyzer(db_path)
    
    def analyze_productivity_patterns(
        self,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze productivity patterns over time
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with productivity pattern analysis
        """
        today = jdatetime.date.today()
        cutoff_date = today - jdatetime.timedelta(days=days_back)
        
        # Get tasks
        tasks = self.db.get_tasks()
        recent_tasks = []
        for task in tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if task_date >= cutoff_date:
                    recent_tasks.append(task)
            except:
                continue
        
        # Get events
        events = self.db.get_events()
        recent_events = []
        for event in events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except:
                continue
        
        # Get productivity metrics
        metrics = self.db.get_productivity_metrics()
        recent_metrics = []
        for metric in metrics:
            try:
                metric_date = jdatetime.datetime.strptime(metric['date'], '%Y-%m-%d').date()
                if metric_date >= cutoff_date:
                    recent_metrics.append(metric)
            except:
                continue
        
        # Analyze patterns
        task_completion_by_day = defaultdict(int)
        meeting_count_by_day = defaultdict(int)
        completed_tasks = [t for t in recent_tasks if t['status'] == 'done']
        
        for task in completed_tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                day_name = self._get_day_name_persian(task_date)
                task_completion_by_day[day_name] += 1
            except:
                continue
        
        for event in recent_events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                day_name = self._get_day_name_persian(event_date)
                meeting_count_by_day[day_name] += 1
            except:
                continue
        
        # Calculate productivity scores
        total_days = len(set(
            [jdatetime.datetime.strptime(m['date'], '%Y-%m-%d').date() 
             for m in recent_metrics if m.get('date')]
        )) or 1
        
        avg_tasks_per_day = len(completed_tasks) / total_days if total_days > 0 else 0
        avg_meetings_per_day = len(recent_events) / total_days if total_days > 0 else 0
        
        # Find peak productivity day
        peak_day = max(task_completion_by_day.items(), key=lambda x: x[1])[0] if task_completion_by_day else None
        
        # Analyze energy patterns
        energy_patterns = self.energy_analyzer.get_energy_patterns(days_back=days_back)
        peak_hours = self._identify_peak_hours_from_patterns(energy_patterns)
        low_energy_hours = self._identify_low_energy_hours_from_patterns(energy_patterns)
        
        return {
            'analysis_period_days': days_back,
            'total_tasks_completed': len(completed_tasks),
            'total_meetings': len(recent_events),
            'avg_tasks_per_day': round(avg_tasks_per_day, 2),
            'avg_meetings_per_day': round(avg_meetings_per_day, 2),
            'task_completion_by_day': dict(task_completion_by_day),
            'meeting_count_by_day': dict(meeting_count_by_day),
            'peak_productivity_day': peak_day,
            'peak_hours': peak_hours,
            'low_energy_hours': low_energy_hours,
            'productivity_trend': self._calculate_trend(recent_metrics)
        }
    
    def detect_stress_signals(
        self,
        days_back: int = 14
    ) -> Dict[str, Any]:
        """
        Detect potential stress signals from patterns
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with stress signal analysis
        """
        today = jdatetime.date.today()
        cutoff_date = today - jdatetime.timedelta(days=days_back)
        
        # Get recent tasks and events
        tasks = self.db.get_tasks()
        events = self.db.get_events()
        
        recent_tasks = []
        for task in tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if task_date >= cutoff_date:
                    recent_tasks.append(task)
            except:
                continue
        
        recent_events = []
        for event in events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except:
                continue
        
        # Stress indicators
        overdue_tasks = [t for t in recent_tasks 
                         if t['status'] == 'undone' and 
                         jdatetime.datetime.strptime(t['due_date'], '%Y-%m-%d').date() < today]
        
        # High meeting density
        meetings_by_day = defaultdict(int)
        for event in recent_events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                meetings_by_day[event_date] += 1
            except:
                continue
        
        high_meeting_days = [date for date, count in meetings_by_day.items() if count >= 5]
        
        # Low completion rate
        completed_tasks = [t for t in recent_tasks if t['status'] == 'done']
        completion_rate = len(completed_tasks) / len(recent_tasks) if recent_tasks else 0
        
        # Energy dips
        energy_patterns = self.energy_analyzer.get_energy_patterns(days_back=days_back)
        if energy_patterns:
            avg_energy = sum(p.get('avg_energy', 0) for p in energy_patterns.values()) / len(energy_patterns)
        else:
            avg_energy = 0.5
        
        stress_signals = []
        stress_level = "low"
        
        if len(overdue_tasks) > 5:
            stress_signals.append({
                'type': 'overdue_tasks',
                'severity': 'high',
                'message': f'{len(overdue_tasks)} وظیفه معوق دارید',
                'count': len(overdue_tasks)
            })
            stress_level = "high"
        
        if len(high_meeting_days) > 3:
            stress_signals.append({
                'type': 'high_meeting_density',
                'severity': 'medium',
                'message': f'{len(high_meeting_days)} روز با ۵+ جلسه',
                'count': len(high_meeting_days)
            })
            if stress_level == "low":
                stress_level = "medium"
        
        if completion_rate < 0.5 and len(recent_tasks) > 10:
            stress_signals.append({
                'type': 'low_completion_rate',
                'severity': 'medium',
                'message': f'نرخ تکمیل: {completion_rate:.0%}',
                'rate': completion_rate
            })
            if stress_level == "low":
                stress_level = "medium"
        
        if avg_energy < 0.4:
            stress_signals.append({
                'type': 'low_energy',
                'severity': 'medium',
                'message': f'سطح انرژی پایین: {avg_energy:.0%}',
                'avg_energy': avg_energy
            })
            if stress_level == "low":
                stress_level = "medium"
        
        return {
            'stress_level': stress_level,
            'signals': stress_signals,
            'overdue_tasks_count': len(overdue_tasks),
            'high_meeting_days_count': len(high_meeting_days),
            'completion_rate': completion_rate,
            'avg_energy': avg_energy
        }
    
    def generate_weekly_insights(
        self,
        week_start_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive weekly productivity insights
        
        Args:
            week_start_date: Start date of week in Jalali format (YYYY-MM-DD)
                           If None, uses current week
                           
        Returns:
            Dictionary with weekly insights
        """
        if week_start_date:
            week_start = jdatetime.datetime.strptime(week_start_date, '%Y-%m-%d').date()
        else:
            today = jdatetime.date.today()
            # Get start of week (Saturday in Jalali calendar)
            days_since_saturday = (today.weekday() + 2) % 7
            week_start = today - jdatetime.timedelta(days=days_since_saturday)
        
        week_end = week_start + jdatetime.timedelta(days=6)
        
        # Get tasks and events for the week
        tasks = self.db.get_tasks()
        events = self.db.get_events()
        
        week_tasks = []
        for task in tasks:
            try:
                task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if week_start <= task_date <= week_end:
                    week_tasks.append(task)
            except:
                continue
        
        week_events = []
        for event in events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if week_start <= event_date <= week_end:
                    week_events.append(event)
            except:
                continue
        
        # Analyze week
        completed_tasks = [t for t in week_tasks if t['status'] == 'done']
        pending_tasks = [t for t in week_tasks if t['status'] == 'undone']
        
        # Productivity patterns
        patterns = self.analyze_productivity_patterns(days_back=7)
        
        # Stress signals
        stress = self.detect_stress_signals(days_back=7)
        
        # Recommendations
        recommendations = self._generate_recommendations(patterns, stress, week_tasks, week_events)
        
        return {
            'week_start': week_start.strftime('%Y-%m-%d'),
            'week_end': week_end.strftime('%Y-%m-%d'),
            'tasks_completed': len(completed_tasks),
            'tasks_pending': len(pending_tasks),
            'meetings_count': len(week_events),
            'completion_rate': len(completed_tasks) / len(week_tasks) if week_tasks else 0,
            'productivity_patterns': patterns,
            'stress_signals': stress,
            'recommendations': recommendations,
            'peak_hours': patterns.get('peak_hours', []),
            'optimal_schedule_suggestions': self._suggest_optimal_schedule(patterns)
        }
    
    def suggest_schedule_optimization(
        self,
        target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest calendar optimization based on productivity patterns
        
        Args:
            target_date: Target date for optimization (YYYY-MM-DD)
                        If None, uses tomorrow
                        
        Returns:
            Dictionary with optimization suggestions
        """
        if target_date:
            target = jdatetime.datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target = jdatetime.date.today() + jdatetime.timedelta(days=1)
        
        # Get existing events for target date
        events = self.db.get_events(date=target.strftime('%Y-%m-%d'))
        
        # Get productivity patterns
        patterns = self.analyze_productivity_patterns(days_back=30)
        peak_hours = patterns.get('peak_hours', [])
        low_energy_hours = patterns.get('low_energy_hours', [])
        
        suggestions = []
        
        # Suggest blocking peak hours for deep work
        if peak_hours:
            peak_start = min(peak_hours)
            peak_end = max(peak_hours)
            suggestions.append({
                'type': 'block_peak_hours',
                'priority': 'high',
                'message': f'ساعات اوج ({peak_start}:00-{peak_end}:00) را برای کارهای عمیق خالی نگه دارید',
                'hours': list(range(peak_start, peak_end + 1))
            })
        
        # Suggest avoiding meetings during peak hours
        if peak_hours and events:
            meeting_times = self._extract_meeting_times(events)
            conflicting_meetings = [m for m in meeting_times if m in peak_hours]
            if conflicting_meetings:
                suggestions.append({
                    'type': 'reschedule_meetings',
                    'priority': 'medium',
                    'message': f'جلسات در ساعات اوج ({conflicting_meetings}) را به ساعات کم‌انرژی منتقل کنید',
                    'conflicting_hours': conflicting_meetings
                })
        
        # Suggest breaks
        if low_energy_hours:
            suggestions.append({
                'type': 'schedule_breaks',
                'priority': 'low',
                'message': f'در ساعات کم‌انرژی ({low_energy_hours}) استراحت کنید',
                'break_hours': low_energy_hours
            })
        
        return {
            'target_date': target.strftime('%Y-%m-%d'),
            'suggestions': suggestions,
            'peak_hours': peak_hours,
            'low_energy_hours': low_energy_hours
        }
    
    def recommend_breaks(
        self,
        target_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend break times based on patterns
        
        Args:
            target_date: Target date (YYYY-MM-DD)
            
        Returns:
            List of break recommendations
        """
        if target_date:
            target = jdatetime.datetime.strptime(target_date, '%Y-%m-%d').date()
        else:
            target = jdatetime.date.today()
        
        # Get events for target date
        events = self.db.get_events(date=target.strftime('%Y-%m-%d'))
        
        # Get productivity patterns
        patterns = self.analyze_productivity_patterns(days_back=30)
        low_energy_hours = patterns.get('low_energy_hours', [])
        
        # Default break times if no data
        if not low_energy_hours:
            low_energy_hours = [14, 15, 16]  # Afternoon dip
        
        # Find gaps between meetings
        meeting_times = self._extract_meeting_times(events)
        busy_hours = set(meeting_times)
        
        recommendations = []
        
        # Recommend breaks during low energy hours if not busy
        for hour in low_energy_hours:
            if hour not in busy_hours:
                recommendations.append({
                    'time': f'{hour}:00',
                    'duration_minutes': 15,
                    'type': 'short_break',
                    'reason': 'ساعت کم‌انرژی'
                })
        
        # Recommend lunch break
        if 12 not in busy_hours and 13 not in busy_hours:
            recommendations.append({
                'time': '12:30',
                'duration_minutes': 30,
                'type': 'lunch_break',
                'reason': 'ناهار'
            })
        
        return recommendations
    
    # ============= HELPER METHODS =============
    
    def _get_day_name_persian(self, date: jdatetime.date) -> str:
        """Get Persian day name"""
        days = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه']
        return days[date.weekday()]
    
    def _identify_peak_hours_from_patterns(self, energy_patterns: Dict[int, Dict[str, float]]) -> List[int]:
        """Identify peak productivity hours from energy patterns"""
        if not energy_patterns:
            return [9, 10, 11]  # Default morning hours
        
        # Get hours with energy > 0.7
        threshold = 0.7
        peak_hours = [
            hour for hour, stats in energy_patterns.items()
            if stats.get('avg_energy', 0) >= threshold
        ]
        
        return sorted(peak_hours) if peak_hours else [9, 10, 11]
    
    def _identify_low_energy_hours_from_patterns(self, energy_patterns: Dict[int, Dict[str, float]]) -> List[int]:
        """Identify low energy hours from energy patterns"""
        if not energy_patterns:
            return [14, 15, 16]  # Default afternoon dip
        
        # Get hours with energy < 0.4
        threshold = 0.4
        low_hours = [
            hour for hour, stats in energy_patterns.items()
            if stats.get('avg_energy', 0) <= threshold
        ]
        
        return sorted(low_hours) if low_hours else [14, 15, 16]
    
    def _calculate_trend(self, metrics: List[Dict]) -> str:
        """Calculate productivity trend"""
        if len(metrics) < 2:
            return "insufficient_data"
        
        # Sort by date
        sorted_metrics = sorted(metrics, key=lambda m: m.get('date', ''))
        
        # Compare first half vs second half
        mid = len(sorted_metrics) // 2
        first_half = sorted_metrics[:mid]
        second_half = sorted_metrics[mid:]
        
        first_avg = sum(m.get('task_completed_count', 0) for m in first_half) / len(first_half) if first_half else 0
        second_avg = sum(m.get('task_completed_count', 0) for m in second_half) / len(second_half) if second_half else 0
        
        if second_avg > first_avg * 1.1:
            return "improving"
        elif second_avg < first_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _extract_meeting_times(self, events: List[Dict]) -> List[int]:
        """Extract meeting times from events"""
        times = []
        for event in events:
            title = event.get('title', '')
            description = event.get('description', '')
            text = f"{title} {description}".lower()
            
            # Try to extract time
            import re
            time_patterns = [
                r'(\d{1,2}):(\d{2})',
                r'ساعت\s+(\d{1,2})',
                r'(\d{1,2})\s+بعدازظهر',
                r'(\d{1,2})\s+صبح'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, text)
                for match in matches:
                    if isinstance(match, tuple):
                        hour = int(match[0])
                    else:
                        hour = int(match)
                    times.append(hour)
        
        return times
    
    def _generate_recommendations(
        self,
        patterns: Dict,
        stress: Dict,
        tasks: List[Dict],
        events: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Based on stress signals
        if stress.get('stress_level') == 'high':
            recommendations.append('⚠️ سطح استرس بالا است. اولویت‌بندی وظایف را بررسی کنید.')
        
        if stress.get('overdue_tasks_count', 0) > 5:
            recommendations.append(f'📋 {stress["overdue_tasks_count"]} وظیفه معوق دارید. آنها را بررسی کنید.')
        
        # Based on patterns
        peak_hours = patterns.get('peak_hours', [])
        if peak_hours:
            recommendations.append(f'⏰ ساعات اوج شما: {", ".join(map(str, peak_hours))}:00. کارهای مهم را در این ساعات انجام دهید.')
        
        # Based on meeting density
        if len(events) > 10:
            recommendations.append('📅 تعداد جلسات زیاد است. برخی را حذف یا ترکیب کنید.')
        
        # Based on completion rate
        completion_rate = len([t for t in tasks if t['status'] == 'done']) / len(tasks) if tasks else 0
        if completion_rate < 0.5:
            recommendations.append('✅ نرخ تکمیل پایین است. وظایف را به بخش‌های کوچکتر تقسیم کنید.')
        
        return recommendations
    
    def _suggest_optimal_schedule(self, patterns: Dict) -> Dict[str, Any]:
        """Suggest optimal daily schedule"""
        peak_hours = patterns.get('peak_hours', [9, 10, 11])
        low_energy_hours = patterns.get('low_energy_hours', [14, 15, 16])
        
        return {
            'deep_work_hours': peak_hours,
            'meeting_hours': [h for h in range(9, 17) if h not in peak_hours and h not in low_energy_hours],
            'break_hours': low_energy_hours,
            'recommended_start': min(peak_hours) if peak_hours else 9,
            'recommended_end': max(peak_hours) if peak_hours else 17
        }


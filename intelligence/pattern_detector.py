"""
Pattern Detector
Detects recurring patterns in user behavior for automation
"""
import jdatetime
from typing import List, Dict, Optional, Tuple, Any
from collections import defaultdict, Counter
from database import DatabaseManager
import re


class PatternDetector:
    """Detects recurring patterns in user behavior"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
    
    def detect_recurring_events(
        self,
        days_back: int = 60,
        min_frequency: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Detect recurring event patterns
        
        Args:
            days_back: Number of days to analyze
            min_frequency: Minimum occurrences to consider a pattern
            
        Returns:
            List of detected recurring event patterns
        """
        events = self.db.get_events()
        
        today = jdatetime.date.today()
        cutoff_date = today - jdatetime.timedelta(days=days_back)
        
        recent_events = []
        for event in events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if event_date >= cutoff_date:
                    recent_events.append(event)
            except:
                continue
        
        # Group events by title similarity
        title_groups = defaultdict(list)
        for event in recent_events:
            normalized_title = self._normalize_title(event.get('title', ''))
            title_groups[normalized_title].append(event)
        
        patterns = []
        for title, event_list in title_groups.items():
            if len(event_list) >= min_frequency:
                # Analyze pattern
                dates = []
                for event in event_list:
                    try:
                        event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                        dates.append(event_date)
                    except:
                        continue
                
                if len(dates) >= min_frequency:
                    pattern = self._analyze_date_pattern(dates, title, event_list[0])
                    if pattern:
                        patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x.get('frequency', 0), reverse=True)
    
    def detect_recurring_tasks(
        self,
        days_back: int = 60,
        min_frequency: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Detect recurring task patterns
        
        Args:
            days_back: Number of days to analyze
            min_frequency: Minimum occurrences to consider a pattern
            
        Returns:
            List of detected recurring task patterns
        """
        tasks = self.db.get_tasks()
        
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
        
        # Group tasks by description similarity
        desc_groups = defaultdict(list)
        for task in recent_tasks:
            normalized_desc = self._normalize_description(task.get('description', ''))
            desc_groups[normalized_desc].append(task)
        
        patterns = []
        for desc, task_list in desc_groups.items():
            if len(task_list) >= min_frequency:
                # Analyze pattern
                dates = []
                for task in task_list:
                    try:
                        task_date = jdatetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                        dates.append(task_date)
                    except:
                        continue
                
                if len(dates) >= min_frequency:
                    pattern = self._analyze_date_pattern(dates, desc, task_list[0], is_task=True)
                    if pattern:
                        patterns.append(pattern)
        
        return sorted(patterns, key=lambda x: x.get('frequency', 0), reverse=True)
    
    def detect_automation_opportunities(
        self,
        days_back: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Detect opportunities for automation
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of automation opportunities
        """
        opportunities = []
        
        # Detect recurring events
        recurring_events = self.detect_recurring_events(days_back, min_frequency=3)
        for pattern in recurring_events:
            opportunities.append({
                'type': 'recurring_event',
                'pattern': pattern,
                'suggestion': f"ایجاد خودکار رویداد '{pattern['title']}' {pattern.get('pattern_description', '')}",
                'confidence': min(1.0, pattern.get('frequency', 0) / 10.0)
            })
        
        # Detect recurring tasks
        recurring_tasks = self.detect_recurring_tasks(days_back, min_frequency=3)
        for pattern in recurring_tasks:
            opportunities.append({
                'type': 'recurring_task',
                'pattern': pattern,
                'suggestion': f"ایجاد خودکار وظیفه '{pattern['title']}' {pattern.get('pattern_description', '')}",
                'confidence': min(1.0, pattern.get('frequency', 0) / 10.0)
            })
        
        # Detect common templates
        templates = self._detect_templates(days_back)
        for template in templates:
            opportunities.append({
                'type': 'template',
                'pattern': template,
                'suggestion': f"استفاده از قالب '{template['name']}' برای ایجاد سریع",
                'confidence': template.get('usage_count', 0) / 5.0
            })
        
        return sorted(opportunities, key=lambda x: x.get('confidence', 0), reverse=True)
    
    def _analyze_date_pattern(
        self,
        dates: List[jdatetime.date],
        title: str,
        sample_item: Dict,
        is_task: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Analyze date pattern to determine recurrence"""
        if len(dates) < 3:
            return None
        
        sorted_dates = sorted(dates)
        
        # Calculate intervals
        intervals = []
        for i in range(1, len(sorted_dates)):
            delta = (sorted_dates[i] - sorted_dates[i-1]).days
            intervals.append(delta)
        
        if not intervals:
            return None
        
        # Find most common interval
        interval_counter = Counter(intervals)
        most_common_interval = interval_counter.most_common(1)[0][0]
        interval_frequency = interval_counter[most_common_interval] / len(intervals)
        
        # Determine pattern type
        pattern_type = None
        pattern_description = None
        
        if most_common_interval == 1 and interval_frequency > 0.7:
            pattern_type = 'daily'
            pattern_description = 'روزانه'
        elif most_common_interval == 7 and interval_frequency > 0.7:
            pattern_type = 'weekly'
            pattern_description = 'هفتگی'
        elif most_common_interval in [14, 15] and interval_frequency > 0.6:
            pattern_type = 'biweekly'
            pattern_description = 'دوهفته‌ای'
        elif most_common_interval in [28, 29, 30, 31] and interval_frequency > 0.6:
            pattern_type = 'monthly'
            pattern_description = 'ماهانه'
        elif interval_frequency > 0.5:
            pattern_type = 'custom'
            pattern_description = f'هر {most_common_interval} روز'
        else:
            return None  # No clear pattern
        
        # Get next occurrence
        last_date = max(sorted_dates)
        next_date = last_date + jdatetime.timedelta(days=most_common_interval)
        
        return {
            'title': title,
            'pattern_type': pattern_type,
            'pattern_description': pattern_description,
            'interval_days': most_common_interval,
            'frequency': len(dates),
            'last_occurrence': last_date.strftime('%Y-%m-%d'),
            'next_occurrence': next_date.strftime('%Y-%m-%d'),
            'confidence': interval_frequency,
            'sample_item': sample_item,
            'is_task': is_task
        }
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for pattern matching"""
        if not title:
            return ""
        
        # Remove time references
        title = re.sub(r'\d{1,2}:\d{2}', '', title)
        title = re.sub(r'ساعت\s+\d+', '', title)
        
        # Remove common variations
        title = title.replace('جلسه', 'meeting')
        title = title.replace('میتینگ', 'meeting')
        
        # Normalize whitespace
        title = ' '.join(title.split())
        
        return title.lower().strip()
    
    def _normalize_description(self, description: str) -> str:
        """Normalize description for pattern matching"""
        if not description:
            return ""
        
        # Remove date references
        description = re.sub(r'\d{4}-\d{2}-\d{2}', '', description)
        
        # Normalize whitespace
        description = ' '.join(description.split())
        
        return description.lower().strip()
    
    def _detect_templates(
        self,
        days_back: int = 60
    ) -> List[Dict[str, Any]]:
        """Detect common templates from events and tasks"""
        events = self.db.get_events()
        tasks = self.db.get_tasks()
        
        today = jdatetime.date.today()
        cutoff_date = today - jdatetime.timedelta(days=days_back)
        
        # Analyze event patterns
        event_templates = defaultdict(int)
        for event in events:
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                if event_date >= cutoff_date:
                    # Create template signature
                    template = {
                        'title': event.get('title', ''),
                        'location': event.get('location', ''),
                        'attendee': event.get('attendee', '')
                    }
                    template_key = f"{template['title']}|{template['location']}|{template['attendee']}"
                    event_templates[template_key] += 1
            except:
                continue
        
        templates = []
        for template_key, count in event_templates.items():
            if count >= 3:
                parts = template_key.split('|')
                templates.append({
                    'name': parts[0] or 'رویداد بدون عنوان',
                    'type': 'event',
                    'usage_count': count,
                    'fields': {
                        'title': parts[0],
                        'location': parts[1] if len(parts) > 1 else None,
                        'attendee': parts[2] if len(parts) > 2 else None
                    }
                })
        
        return templates


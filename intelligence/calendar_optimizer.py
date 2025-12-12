"""
Calendar Optimizer
Intelligently optimizes calendar scheduling based on energy levels, patterns, and context
"""
import jdatetime
from typing import List, Dict, Optional, Tuple, Any
from datetime import timedelta
from database import DatabaseManager
from intelligence.energy_analyzer import EnergyAnalyzer


class CalendarOptimizer:
    """Optimizes calendar scheduling with energy awareness"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db = DatabaseManager(db_path)
        self.energy_analyzer = EnergyAnalyzer(db_path)
    
    def analyze_meeting_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Analyze patterns in existing meetings
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary with meeting pattern statistics
        """
        events = self.db.get_events()
        
        # Filter recent events
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
        
        # Analyze patterns
        meeting_times = []
        meeting_days = {}
        
        for event in recent_events:
            # Extract time if available in title/description
            title_lower = (event.get('title') or '').lower()
            desc_lower = (event.get('description') or '').lower()
            
            # Try to extract hour from text
            hour = self._extract_hour_from_text(title_lower + ' ' + desc_lower)
            if hour is not None:
                meeting_times.append(hour)
            
            # Track by day of week
            try:
                event_date = jdatetime.datetime.strptime(event['date'], '%Y-%m-%d').date()
                day_name = event_date.strftime('%A')
                meeting_days[day_name] = meeting_days.get(day_name, 0) + 1
            except:
                pass
        
        return {
            'total_meetings': len(recent_events),
            'avg_meetings_per_day': len(recent_events) / max(days_back, 1),
            'common_hours': self._get_common_hours(meeting_times),
            'meeting_days': meeting_days
        }
    
    def _extract_hour_from_text(self, text: str) -> Optional[int]:
        """Extract hour from text (e.g., 'ساعت 10', '10 AM', '14:30')"""
        import re
        
        # Persian hour patterns
        persian_patterns = [
            r'ساعت\s*(\d{1,2})',
            r'(\d{1,2})\s*بعدازظهر',
            r'(\d{1,2})\s*قبلازظهر',
        ]
        
        for pattern in persian_patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                if 'بعدازظهر' in text or 'pm' in text.lower():
                    if hour < 12:
                        hour += 12
                return hour
        
        # English patterns
        english_patterns = [
            r'(\d{1,2})\s*(?:am|pm)',
            r'(\d{1,2}):\d{2}',
        ]
        
        for pattern in english_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                hour = int(match.group(1))
                if 'pm' in text.lower() and hour < 12:
                    hour += 12
                return hour
        
        return None
    
    def _get_common_hours(self, hours: List[int]) -> List[Tuple[int, int]]:
        """Get most common hours with frequency"""
        from collections import Counter
        hour_counts = Counter(hours)
        return sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    def find_optimal_time_slot(
        self,
        date: str,
        duration_hours: float = 1.0,
        preferred_hours: Optional[List[int]] = None,
        avoid_low_energy: bool = True,
        meeting_type: str = "meeting"
    ) -> List[Dict[str, Any]]:
        """
        Find optimal time slots for scheduling
        
        Args:
            date: Target date in Jalali format (YYYY-MM-DD)
            duration_hours: Duration of the meeting/task
            preferred_hours: List of preferred hours (0-23)
            avoid_low_energy: Whether to avoid low-energy hours
            meeting_type: Type of meeting ('meeting', 'deep_work', 'task')
            
        Returns:
            List of suggested time slots with scores
        """
        suggestions = []
        
        # Get existing events for the date
        existing_events = self.db.get_events(date=date)
        busy_hours = set()
        
        for event in existing_events:
            title = event.get('title') or ''
            description = event.get('description') or ''
            hour = self._extract_hour_from_text(title + ' ' + description)
            if hour is not None:
                for h in range(hour, hour + int(duration_hours) + 1):
                    busy_hours.add(h % 24)
        
        # Get energy patterns
        if avoid_low_energy:
            if meeting_type == "deep_work":
                optimal_hours = self.energy_analyzer.get_optimal_deep_work_hours()
            else:
                optimal_hours = self.energy_analyzer.get_optimal_meeting_hours(duration_hours)
        else:
            optimal_hours = [(h, 0.5) for h in range(9, 18)]  # Default business hours
        
        # Score each available hour
        for hour, energy_score in optimal_hours:
            if hour in busy_hours:
                continue
            
            # Check if preferred hours match
            preference_boost = 1.2 if preferred_hours and hour in preferred_hours else 1.0
            
            # Calculate final score
            final_score = energy_score * preference_boost
            
            suggestions.append({
                'hour': hour,
                'score': final_score,
                'energy_level': energy_score,
                'available': True
            })
        
        # Sort by score
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def calculate_preparation_time(
        self,
        meeting_title: str,
        meeting_description: Optional[str] = None
    ) -> float:
        """
        Calculate preparation time needed for a meeting
        
        Args:
            meeting_title: Title of the meeting
            meeting_description: Description of the meeting
            
        Returns:
            Preparation time in hours
        """
        text = (meeting_title + ' ' + (meeting_description or '')).lower()
        
        # Keywords that suggest more preparation needed
        high_prep_keywords = [
            'presentation', 'پرزنتیشن', 'present', 'ارائه',
            'review', 'بررسی', 'audit', 'بازرسی',
            'negotiation', 'مذاکره', 'contract', 'قرارداد',
            'strategy', 'استراتژی', 'planning', 'برنامه\u200cریزی'
        ]
        
        medium_prep_keywords = [
            'meeting', 'جلسه', 'discussion', 'بحث',
            'update', 'به\u200cروزرسانی', 'status', 'وضعیت'
        ]
        
        prep_time = 0.5  # Base preparation time (30 minutes)
        
        for keyword in high_prep_keywords:
            if keyword in text:
                prep_time += 1.0
                break
        
        for keyword in medium_prep_keywords:
            if keyword in text:
                prep_time += 0.5
                break
        
        return min(prep_time, 4.0)  # Cap at 4 hours
    
    def suggest_calendar_blocking(
        self,
        date: str,
        block_type: str = "deep_work"
    ) -> List[Dict[str, Any]]:
        """
        Suggest calendar blocks for focus time
        
        Args:
            date: Target date in Jalali format
            block_type: Type of block ('deep_work', 'break', 'preparation')
            
        Returns:
            List of suggested time blocks
        """
        if block_type == "deep_work":
            optimal_hours = self.energy_analyzer.get_optimal_deep_work_hours()
        else:
            optimal_hours = [(h, 0.6) for h in range(9, 17)]
        
        # Get existing events
        existing_events = self.db.get_events(date=date)
        busy_hours = set()
        
        for event in existing_events:
            title = event.get('title') or ''
            description = event.get('description') or ''
            hour = self._extract_hour_from_text(title + ' ' + description)
            if hour is not None:
                busy_hours.add(hour)
        
        suggestions = []
        for hour, score in optimal_hours[:3]:  # Top 3 hours
            if hour not in busy_hours:
                suggestions.append({
                    'start_hour': hour,
                    'duration_hours': 2.0,  # Default 2-hour blocks
                    'type': block_type,
                    'score': score
                })
        
        return suggestions


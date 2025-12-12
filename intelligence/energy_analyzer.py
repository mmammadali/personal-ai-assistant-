"""
Energy Level Analyzer
Tracks and analyzes user productivity patterns by time of day
"""
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import jdatetime
from contextlib import contextmanager
from database import DatabaseManager


class EnergyAnalyzer:
    """Analyzes user energy levels and productivity patterns"""
    
    def __init__(self, db_path: str = "assistant.db"):
        self.db_path = db_path
        self.db = DatabaseManager(db_path)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def record_energy_level(
        self,
        date: str,
        hour: int,
        energy_score: float,
        activity_type: Optional[str] = None
    ) -> None:
        """
        Record energy level for a specific hour
        
        Args:
            date: Date in Jalali format (YYYY-MM-DD)
            hour: Hour of day (0-23)
            energy_score: Energy level (0.0-1.0, where 1.0 is peak energy)
            activity_type: Type of activity (e.g., 'meeting', 'task', 'break')
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO energy_levels (date, hour, energy_score, activity_type)
                VALUES (?, ?, ?, ?)
            """, (date, hour, energy_score, activity_type))
    
    def get_energy_patterns(
        self,
        days_back: int = 30
    ) -> Dict[int, Dict[str, float]]:
        """
        Analyze energy patterns by hour of day
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            Dictionary mapping hour (0-23) to statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get recent energy data
            cursor.execute("""
                SELECT hour, AVG(energy_score) as avg_energy, 
                       COUNT(*) as count,
                       MIN(energy_score) as min_energy,
                       MAX(energy_score) as max_energy
                FROM energy_levels
                WHERE date >= date('now', '-' || ? || ' days')
                GROUP BY hour
                ORDER BY hour
            """, (days_back,))
            
            patterns = {}
            for row in cursor.fetchall():
                patterns[row['hour']] = {
                    'avg_energy': row['avg_energy'],
                    'count': row['count'],
                    'min_energy': row['min_energy'],
                    'max_energy': row['max_energy']
                }
            
            return patterns
    
    def identify_peak_hours(self, days_back: int = 30) -> List[Tuple[int, float]]:
        """
        Identify peak productivity hours
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of (hour, avg_energy_score) tuples, sorted by energy (highest first)
        """
        patterns = self.get_energy_patterns(days_back)
        
        # Sort by average energy score
        peak_hours = [
            (hour, stats['avg_energy'])
            for hour, stats in patterns.items()
            if stats['count'] >= 3  # Require at least 3 data points
        ]
        
        peak_hours.sort(key=lambda x: x[1], reverse=True)
        return peak_hours
    
    def identify_low_energy_hours(self, days_back: int = 30) -> List[Tuple[int, float]]:
        """
        Identify low productivity hours (energy dips)
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of (hour, avg_energy_score) tuples, sorted by energy (lowest first)
        """
        patterns = self.get_energy_patterns(days_back)
        
        low_hours = [
            (hour, stats['avg_energy'])
            for hour, stats in patterns.items()
            if stats['count'] >= 3
        ]
        
        low_hours.sort(key=lambda x: x[1])  # Sort ascending
        return low_hours
    
    def get_optimal_meeting_hours(
        self,
        duration_hours: float = 1.0,
        days_back: int = 30
    ) -> List[Tuple[int, float]]:
        """
        Suggest optimal hours for meetings based on energy patterns
        
        Args:
            duration_hours: Expected meeting duration
            days_back: Number of days to analyze
            
        Returns:
            List of (start_hour, score) tuples for optimal meeting times
        """
        patterns = self.get_energy_patterns(days_back)
        optimal_times = []
        
        for hour in range(24):
            # Calculate average energy for the meeting window
            window_hours = [h % 24 for h in range(hour, hour + int(duration_hours) + 1)]
            window_energies = [
                patterns.get(h, {}).get('avg_energy', 0.5)
                for h in window_hours
            ]
            
            if window_energies:
                avg_energy = sum(window_energies) / len(window_energies)
                # Prefer moderate energy (not too high, not too low) for meetings
                # Too high = better for deep work, too low = unproductive
                score = avg_energy if 0.4 <= avg_energy <= 0.7 else avg_energy * 0.5
                optimal_times.append((hour, score))
        
        optimal_times.sort(key=lambda x: x[1], reverse=True)
        return optimal_times[:5]  # Return top 5
    
    def get_optimal_deep_work_hours(
        self,
        days_back: int = 30
    ) -> List[Tuple[int, float]]:
        """
        Suggest optimal hours for deep work (high focus tasks)
        
        Args:
            days_back: Number of days to analyze
            
        Returns:
            List of (hour, score) tuples for optimal deep work times
        """
        patterns = self.get_energy_patterns(days_back)
        deep_work_times = []
        
        for hour in range(24):
            avg_energy = patterns.get(hour, {}).get('avg_energy', 0.5)
            # For deep work, prefer highest energy hours
            deep_work_times.append((hour, avg_energy))
        
        deep_work_times.sort(key=lambda x: x[1], reverse=True)
        return deep_work_times[:5]  # Return top 5
    
    def infer_energy_from_activity(
        self,
        activity_type: str,
        hour: int
    ) -> float:
        """
        Infer energy level from activity type and time
        
        Args:
            activity_type: Type of activity ('meeting', 'task', 'break', etc.)
            hour: Hour of day (0-23)
            
        Returns:
            Estimated energy score (0.0-1.0)
        """
        # Base energy by time of day (circadian rhythm approximation)
        # Peak hours typically: 9-11 AM, 2-4 PM
        # Low hours typically: 1-3 PM (post-lunch), late evening
        
        if 9 <= hour <= 11:
            base_energy = 0.8
        elif 14 <= hour <= 16:
            base_energy = 0.75
        elif 13 <= hour <= 14:  # Post-lunch dip
            base_energy = 0.4
        elif hour >= 20:
            base_energy = 0.3
        else:
            base_energy = 0.6
        
        # Adjust based on activity type
        activity_multipliers = {
            'meeting': 0.9,  # Meetings can be draining
            'task': 1.0,
            'deep_work': 1.1,  # High energy needed
            'break': 0.5,
            'email': 0.7
        }
        
        multiplier = activity_multipliers.get(activity_type, 1.0)
        return min(1.0, base_energy * multiplier)


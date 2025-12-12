"""
Learning Engine
Tracks user preferences, learns from corrections, and adapts to user style
"""
import sqlite3
from typing import Dict, Optional, List, Any
from contextlib import contextmanager
from database import DatabaseManager
from collections import defaultdict
import json


class LearningEngine:
    """Learns user preferences and adapts behavior"""
    
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
    
    def learn_preference(
        self,
        preference_type: str,
        preference_key: str,
        preference_value: str,
        confidence: float = 1.0
    ) -> None:
        """
        Learn a user preference
        
        Args:
            preference_type: Type of preference (e.g., 'category', 'default_time', 'format')
            preference_key: Key for the preference (e.g., 'meeting_category', 'task_time')
            preference_value: Value of the preference
            confidence: Confidence level (0.0-1.0)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if preference exists
            cursor.execute("""
                SELECT * FROM user_preferences 
                WHERE preference_type = ? AND preference_key = ?
            """, (preference_type, preference_key))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing preference
                current_confidence = existing['confidence']
                current_usage = existing['usage_count']
                
                # Increase confidence and usage
                new_confidence = min(1.0, current_confidence + (confidence * 0.1))
                new_usage = current_usage + 1
                
                cursor.execute("""
                    UPDATE user_preferences 
                    SET preference_value = ?,
                        confidence = ?,
                        usage_count = ?,
                        last_used = CURRENT_TIMESTAMP
                    WHERE preference_type = ? AND preference_key = ?
                """, (preference_value, new_confidence, new_usage, preference_type, preference_key))
            else:
                # Create new preference
                cursor.execute("""
                    INSERT INTO user_preferences 
                    (preference_type, preference_key, preference_value, confidence, usage_count)
                    VALUES (?, ?, ?, ?, 1)
                """, (preference_type, preference_key, preference_value, confidence))
    
    def get_preference(
        self,
        preference_type: str,
        preference_key: str,
        min_confidence: float = 0.5
    ) -> Optional[str]:
        """
        Get a learned preference
        
        Args:
            preference_type: Type of preference
            preference_key: Key for the preference
            min_confidence: Minimum confidence threshold
            
        Returns:
            Preference value if found and confidence is high enough, None otherwise
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preference_value, confidence 
                FROM user_preferences 
                WHERE preference_type = ? AND preference_key = ? AND confidence >= ?
                ORDER BY usage_count DESC, last_used DESC
                LIMIT 1
            """, (preference_type, preference_key, min_confidence))
            
            result = cursor.fetchone()
            return result['preference_value'] if result else None
    
    def get_all_preferences(
        self,
        preference_type: Optional[str] = None,
        min_confidence: float = 0.5
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all preferences, optionally filtered by type
        
        Args:
            preference_type: Filter by type (None for all)
            min_confidence: Minimum confidence threshold
            
        Returns:
            Dictionary of preferences organized by type and key
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if preference_type:
                cursor.execute("""
                    SELECT preference_type, preference_key, preference_value, confidence, usage_count
                    FROM user_preferences 
                    WHERE preference_type = ? AND confidence >= ?
                    ORDER BY usage_count DESC
                """, (preference_type, min_confidence))
            else:
                cursor.execute("""
                    SELECT preference_type, preference_key, preference_value, confidence, usage_count
                    FROM user_preferences 
                    WHERE confidence >= ?
                    ORDER BY preference_type, usage_count DESC
                """, (min_confidence,))
            
            results = cursor.fetchall()
            
            preferences = {}
            for row in results:
                pref_type = row['preference_type']
                pref_key = row['preference_key']
                
                if pref_type not in preferences:
                    preferences[pref_type] = {}
                
                preferences[pref_type][pref_key] = {
                    'value': row['preference_value'],
                    'confidence': row['confidence'],
                    'usage_count': row['usage_count']
                }
            
            return preferences
    
    def learn_categorization(
        self,
        item_text: str,
        category: str,
        subcategory: Optional[str] = None
    ) -> None:
        """
        Learn categorization patterns
        
        Args:
            item_text: Text of the item (e.g., task description, event title)
            category: Assigned category
            subcategory: Optional subcategory
        """
        # Extract keywords from item text
        keywords = self._extract_keywords(item_text)
        
        for keyword in keywords:
            key = f"keyword_{keyword.lower()}"
            value = category
            if subcategory:
                value = f"{category}:{subcategory}"
            
            self.learn_preference('categorization', key, value, confidence=0.8)
    
    def suggest_category(
        self,
        item_text: str
    ) -> Optional[str]:
        """
        Suggest category based on learned patterns
        
        Args:
            item_text: Text to categorize
            
        Returns:
            Suggested category or None
        """
        keywords = self._extract_keywords(item_text)
        
        category_scores = defaultdict(float)
        
        for keyword in keywords:
            key = f"keyword_{keyword.lower()}"
            category = self.get_preference('categorization', key, min_confidence=0.6)
            
            if category:
                # Extract base category (before :)
                base_category = category.split(':')[0]
                category_scores[base_category] += 1.0
        
        if category_scores:
            # Return category with highest score
            return max(category_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def learn_frequently_used_value(
        self,
        field_type: str,
        field_name: str,
        value: str
    ) -> None:
        """
        Learn frequently used values for fields
        
        Args:
            field_type: Type of field (e.g., 'event', 'task')
            field_name: Name of field (e.g., 'location', 'project')
            value: Value used
        """
        key = f"{field_type}_{field_name}"
        self.learn_preference('frequent_values', key, value, confidence=0.7)
    
    def get_frequent_values(
        self,
        field_type: str,
        field_name: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get frequently used values for a field
        
        Args:
            field_type: Type of field
            field_name: Name of field
            limit: Maximum number of values to return
            
        Returns:
            List of frequent values
        """
        key = f"{field_type}_{field_name}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT preference_value, usage_count
                FROM user_preferences 
                WHERE preference_type = 'frequent_values' 
                AND preference_key LIKE ?
                AND confidence >= 0.5
                ORDER BY usage_count DESC, last_used DESC
                LIMIT ?
            """, (f"{key}%", limit))
            
            results = cursor.fetchall()
            return [row['preference_value'] for row in results]
    
    def learn_correction(
        self,
        original_value: str,
        corrected_value: str,
        context: Optional[str] = None
    ) -> None:
        """
        Learn from user corrections
        
        Args:
            original_value: Original (incorrect) value
            corrected_value: Corrected value
            context: Optional context (e.g., 'event_title', 'task_description')
        """
        # Store correction pattern
        if context:
            key = f"correction_{context}"
        else:
            key = "correction_general"
        
        # Learn that original_value should be corrected_value
        self.learn_preference('corrections', f"{key}_{original_value}", corrected_value, confidence=0.9)
    
    def apply_correction(
        self,
        value: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Apply learned corrections
        
        Args:
            value: Value to check
            context: Optional context
            
        Returns:
            Corrected value if correction exists, None otherwise
        """
        if context:
            key = f"correction_{context}"
        else:
            key = "correction_general"
        
        correction_key = f"{key}_{value}"
        return self.get_preference('corrections', correction_key, min_confidence=0.7)
    
    def learn_user_style(
        self,
        style_type: str,
        style_value: str
    ) -> None:
        """
        Learn user communication/style preferences
        
        Args:
            style_type: Type of style (e.g., 'date_format', 'time_format', 'language_preference')
            style_value: Style value
        """
        self.learn_preference('user_style', style_type, style_value, confidence=0.8)
    
    def get_user_style(
        self,
        style_type: str
    ) -> Optional[str]:
        """
        Get user style preference
        
        Args:
            style_type: Type of style
            
        Returns:
            Style value or None
        """
        return self.get_preference('user_style', style_type, min_confidence=0.6)
    
    def track_suggestion_acceptance(
        self,
        suggestion_type: str,
        suggestion_content: str,
        accepted: bool
    ) -> None:
        """
        Track whether user accepts suggestions
        
        Args:
            suggestion_type: Type of suggestion
            suggestion_content: Content of suggestion
            accepted: Whether suggestion was accepted
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suggestions_log 
                (suggestion_type, suggestion_content, accepted)
                VALUES (?, ?, ?)
            """, (suggestion_type, suggestion_content, 1 if accepted else 0))
    
    def get_suggestion_acceptance_rate(
        self,
        suggestion_type: Optional[str] = None,
        days_back: int = 30
    ) -> float:
        """
        Get acceptance rate for suggestions
        
        Args:
            suggestion_type: Filter by type (None for all)
            days_back: Number of days to analyze
            
        Returns:
            Acceptance rate (0.0-1.0)
        """
        import jdatetime
        from datetime import datetime, timedelta
        
        cutoff_date = (jdatetime.date.today() - jdatetime.timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if suggestion_type:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END) as accepted
                    FROM suggestions_log
                    WHERE suggestion_type = ? AND date(created_at) >= ?
                """, (suggestion_type, cutoff_date))
            else:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN accepted = 1 THEN 1 ELSE 0 END) as accepted
                    FROM suggestions_log
                    WHERE date(created_at) >= ?
                """, (cutoff_date,))
            
            result = cursor.fetchone()
            
            if result and result['total'] > 0:
                return result['accepted'] / result['total']
            
            return 0.5  # Default neutral rate
    
    # ============= HELPER METHODS =============
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        
        # Filter out common stop words (Persian and English)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'از', 'به', 'در', 'با', 'که', 'این', 'آن', 'را', 'برای', 'یا'
        }
        
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Return top keywords (limit to 5)
        return keywords[:5]


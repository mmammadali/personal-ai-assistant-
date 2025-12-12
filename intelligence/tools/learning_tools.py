"""
Learning Tools for LangChain
User preference learning and adaptation tools
"""
from langchain_core.tools import tool
from typing import Optional, Dict, Any, List
from intelligence.learning_engine import LearningEngine


# Initialize learning engine
_learning_engine = None


def get_learning_engine() -> LearningEngine:
    """Get or create learning engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine


@tool
def learn_user_preference_tool(
    preference_type: str,
    preference_key: str,
    preference_value: str
) -> str:
    """
    Learn a user preference for future use.
    
    Examples:
    - Category preferences: learn_user_preference("category", "meeting_type", "team_meeting")
    - Default values: learn_user_preference("default", "meeting_location", "office")
    - Format preferences: learn_user_preference("format", "date_format", "YYYY-MM-DD")
    
    Args:
        preference_type: Type of preference (e.g., 'category', 'default', 'format')
        preference_key: Key for the preference (e.g., 'meeting_category', 'task_time')
        preference_value: Value of the preference
        
    Returns:
        Confirmation message
    """
    try:
        engine = get_learning_engine()
        engine.learn_preference(preference_type, preference_key, preference_value)
        return f"✅ ترجیح کاربر یاد گرفته شد: {preference_type}/{preference_key} = {preference_value}"
    except Exception as e:
        return f"❌ خطا در یادگیری ترجیح: {str(e)}"


@tool
def get_user_preference_tool(
    preference_type: str,
    preference_key: str
) -> str:
    """
    Get a learned user preference.
    
    Args:
        preference_type: Type of preference
        preference_key: Key for the preference
        
    Returns:
        Preference value or message if not found
    """
    try:
        engine = get_learning_engine()
        value = engine.get_preference(preference_type, preference_key)
        
        if value:
            return f"✅ ترجیح کاربر: {preference_type}/{preference_key} = {value}"
        else:
            return f"ℹ️ ترجیحی برای {preference_type}/{preference_key} پیدا نشد"
    except Exception as e:
        return f"❌ خطا در دریافت ترجیح: {str(e)}"


@tool
def suggest_category_tool(
    item_text: str
) -> str:
    """
    Suggest category for an item based on learned patterns.
    
    Args:
        item_text: Text to categorize (e.g., task description, event title)
        
    Returns:
        Suggested category or message if no suggestion available
    """
    try:
        engine = get_learning_engine()
        category = engine.suggest_category(item_text)
        
        if category:
            return f"💡 پیشنهاد دسته‌بندی: {category}"
        else:
            return "ℹ️ پیشنهاد دسته‌بندی در دسترس نیست"
    except Exception as e:
        return f"❌ خطا در پیشنهاد دسته‌بندی: {str(e)}"


@tool
def get_frequent_values_tool(
    field_type: str,
    field_name: str,
    limit: int = 5
) -> str:
    """
    Get frequently used values for a field.
    
    Useful for autocomplete and suggestions.
    
    Args:
        field_type: Type of field (e.g., 'event', 'task')
        field_name: Name of field (e.g., 'location', 'project', 'attendee')
        limit: Maximum number of values to return (default: 5)
        
    Returns:
        List of frequent values
    """
    try:
        engine = get_learning_engine()
        values = engine.get_frequent_values(field_type, field_name, limit)
        
        if values:
            return f"📋 مقادیر پراستفاده برای {field_type}.{field_name}:\n" + "\n".join(f"   - {v}" for v in values)
        else:
            return f"ℹ️ مقادیر پراستفاده برای {field_type}.{field_name} پیدا نشد"
    except Exception as e:
        return f"❌ خطا در دریافت مقادیر پراستفاده: {str(e)}"


@tool
def learn_correction_tool(
    original_value: str,
    corrected_value: str,
    context: Optional[str] = None
) -> str:
    """
    Learn from a user correction.
    
    This helps the system avoid making the same mistake again.
    
    Args:
        original_value: Original (incorrect) value
        corrected_value: Corrected value
        context: Optional context (e.g., 'event_title', 'task_description')
        
    Returns:
        Confirmation message
    """
    try:
        engine = get_learning_engine()
        engine.learn_correction(original_value, corrected_value, context)
        return f"✅ تصحیح یاد گرفته شد: '{original_value}' → '{corrected_value}'"
    except Exception as e:
        return f"❌ خطا در یادگیری تصحیح: {str(e)}"


@tool
def get_suggestion_acceptance_rate_tool(
    suggestion_type: Optional[str] = None,
    days_back: int = 30
) -> str:
    """
    Get acceptance rate for suggestions to understand user preferences.
    
    Args:
        suggestion_type: Filter by type (None for all types)
        days_back: Number of days to analyze (default: 30)
        
    Returns:
        Acceptance rate report
    """
    try:
        engine = get_learning_engine()
        rate = engine.get_suggestion_acceptance_rate(suggestion_type, days_back)
        
        type_text = suggestion_type or "همه انواع"
        return f"📊 نرخ پذیرش پیشنهادها ({type_text}): {rate:.0%}"
    except Exception as e:
        return f"❌ خطا در محاسبه نرخ پذیرش: {str(e)}"


# Export all tools
ALL_LEARNING_TOOLS = [
    learn_user_preference_tool,
    get_user_preference_tool,
    suggest_category_tool,
    get_frequent_values_tool,
    learn_correction_tool,
    get_suggestion_acceptance_rate_tool
]


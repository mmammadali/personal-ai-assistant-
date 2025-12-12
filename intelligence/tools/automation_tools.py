"""
Automation Tools for LangChain
Pattern detection and automation tools
"""
from langchain_core.tools import tool
from typing import Optional, Dict, Any, List
from intelligence.automation_engine import AutomationEngine
from intelligence.pattern_detector import PatternDetector


# Initialize engines
_automation_engine = None
_pattern_detector = None


def get_automation_engine() -> AutomationEngine:
    """Get or create automation engine instance"""
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = AutomationEngine()
    return _automation_engine


def get_pattern_detector() -> PatternDetector:
    """Get or create pattern detector instance"""
    global _pattern_detector
    if _pattern_detector is None:
        _pattern_detector = PatternDetector()
    return _pattern_detector


@tool
def detect_automation_opportunities_tool(
    days_back: int = 60
) -> str:
    """
    Detect opportunities for automation based on recurring patterns.
    
    Analyzes:
    - Recurring events
    - Recurring tasks
    - Common templates
    
    Args:
        days_back: Number of days to analyze (default: 60)
        
    Returns:
        List of automation opportunities
    """
    try:
        detector = get_pattern_detector()
        opportunities = detector.detect_automation_opportunities(days_back)
        
        if not opportunities:
            return "ℹ️ فرصت خودکارسازی شناسایی نشد"
        
        report = f"🤖 **فرصت‌های خودکارسازی**\n\n"
        
        for i, opp in enumerate(opportunities[:10], 1):  # Top 10
            confidence_emoji = "🟢" if opp.get('confidence', 0) > 0.7 else "🟡" if opp.get('confidence', 0) > 0.4 else "⚪"
            
            report += f"{i}. {confidence_emoji} **{opp.get('type', 'unknown')}**\n"
            report += f"   {opp.get('suggestion', '')}\n"
            report += f"   اطمینان: {opp.get('confidence', 0):.0%}\n\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در تشخیص فرصت‌های خودکارسازی: {str(e)}"


@tool
def create_automation_rule_tool(
    rule_name: str,
    rule_type: str,
    pattern_description: str,
    action_description: str
) -> str:
    """
    Create an automation rule.
    
    Args:
        rule_name: Name of the rule
        rule_type: Type of rule ('recurring_event', 'recurring_task', 'template')
        pattern_description: Description of the pattern to match
        action_description: Description of action to take
        
    Returns:
        Confirmation message
    """
    try:
        engine = get_automation_engine()
        
        # Simple rule creation (can be enhanced)
        rule_id = engine.create_automation_rule(
            rule_name=rule_name,
            rule_type=rule_type,
            pattern={'description': pattern_description},
            action={'description': action_description},
            enabled=True
        )
        
        return f"✅ قانون خودکارسازی ایجاد شد: {rule_name} (ID: {rule_id})"
    
    except Exception as e:
        return f"❌ خطا در ایجاد قانون خودکارسازی: {str(e)}"


@tool
def execute_automation_tool(
    rule_name: Optional[str] = None
) -> str:
    """
    Execute automation rules.
    
    Args:
        rule_name: Specific rule to execute (None for all enabled rules)
        
    Returns:
        Execution results
    """
    try:
        engine = get_automation_engine()
        results = engine.execute_automation(rule_name)
        
        if not results:
            return "ℹ️ قانونی برای اجرا پیدا نشد"
        
        report = f"🤖 **نتایج اجرای خودکارسازی**\n\n"
        
        for result in results:
            status = "✅" if result.get('success') else "❌"
            report += f"{status} **{result.get('rule', 'Unknown')}**\n"
            report += f"   {result.get('result', '')}\n\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در اجرای خودکارسازی: {str(e)}"


@tool
def auto_create_recurring_items_tool(
    days_ahead: int = 7
) -> str:
    """
    Automatically create recurring events and tasks based on detected patterns.
    
    Args:
        days_ahead: Number of days ahead to create items (default: 7)
        
    Returns:
        Report of created items
    """
    try:
        engine = get_automation_engine()
        created = engine.auto_create_recurring_items(days_ahead)
        
        if not created:
            return "ℹ️ مورد تکراری برای ایجاد پیدا نشد"
        
        report = f"✅ **ایجاد خودکار موارد تکراری**\n\n"
        report += f"📅 **دوره:** {days_ahead} روز آینده\n\n"
        
        events = [c for c in created if c.get('type') == 'event']
        tasks = [c for c in created if c.get('type') == 'task']
        
        if events:
            report += f"📅 **رویدادها ({len(events)}):**\n"
            for event in events:
                report += f"   - {event.get('date')}: {event.get('title')} ({event.get('pattern')})\n"
            report += "\n"
        
        if tasks:
            report += f"📋 **وظایف ({len(tasks)}):**\n"
            for task in tasks:
                report += f"   - {task.get('due_date')}: {task.get('description')} ({task.get('pattern')})\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در ایجاد خودکار موارد تکراری: {str(e)}"


@tool
def detect_recurring_patterns_tool(
    pattern_type: str = "all",
    days_back: int = 60
) -> str:
    """
    Detect recurring patterns in events or tasks.
    
    Args:
        pattern_type: Type to detect ('events', 'tasks', 'all')
        days_back: Number of days to analyze (default: 60)
        
    Returns:
        Detected patterns report
    """
    try:
        detector = get_pattern_detector()
        
        report = "🔍 **الگوهای تکراری شناسایی شده**\n\n"
        
        if pattern_type in ['events', 'all']:
            recurring_events = detector.detect_recurring_events(days_back, min_frequency=3)
            
            if recurring_events:
                report += f"📅 **رویدادهای تکراری ({len(recurring_events)}):**\n"
                for pattern in recurring_events[:5]:  # Top 5
                    report += f"   - {pattern.get('title')}: {pattern.get('pattern_description')}\n"
                    report += f"     تکرار: {pattern.get('frequency')} بار | بعدی: {pattern.get('next_occurrence')}\n"
                report += "\n"
            else:
                report += "📅 رویداد تکراری پیدا نشد\n\n"
        
        if pattern_type in ['tasks', 'all']:
            recurring_tasks = detector.detect_recurring_tasks(days_back, min_frequency=3)
            
            if recurring_tasks:
                report += f"📋 **وظایف تکراری ({len(recurring_tasks)}):**\n"
                for pattern in recurring_tasks[:5]:  # Top 5
                    report += f"   - {pattern.get('title')}: {pattern.get('pattern_description')}\n"
                    report += f"     تکرار: {pattern.get('frequency')} بار | بعدی: {pattern.get('next_occurrence')}\n"
            else:
                report += "📋 وظیفه تکراری پیدا نشد\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در تشخیص الگوهای تکراری: {str(e)}"


# Export all tools
ALL_AUTOMATION_TOOLS = [
    detect_automation_opportunities_tool,
    create_automation_rule_tool,
    execute_automation_tool,
    auto_create_recurring_items_tool,
    detect_recurring_patterns_tool
]


"""
Insight Tools for LangChain
Weekly insights, productivity analysis, and pattern recognition tools
"""
from langchain_core.tools import tool
from typing import Optional, Dict, Any, List
from intelligence.productivity_analyzer import ProductivityAnalyzer


# Initialize productivity analyzer
_productivity_analyzer = None


def get_productivity_analyzer() -> ProductivityAnalyzer:
    """Get or create productivity analyzer instance"""
    global _productivity_analyzer
    if _productivity_analyzer is None:
        _productivity_analyzer = ProductivityAnalyzer()
    return _productivity_analyzer


@tool
def generate_weekly_insights_tool(
    week_start_date: Optional[str] = None
) -> str:
    """
    Generate comprehensive weekly productivity insights and analysis.
    
    Provides:
    - Task completion statistics
    - Meeting patterns
    - Productivity trends
    - Stress signals
    - Personalized recommendations
    - Optimal schedule suggestions
    
    Args:
        week_start_date: Start date of week in Jalali format (YYYY-MM-DD).
                        If not provided, uses current week.
                        
    Returns:
        Formatted weekly insights report in Persian
    """
    try:
        analyzer = get_productivity_analyzer()
        insights = analyzer.generate_weekly_insights(week_start_date)
        
        # Format output
        report = f"""📊 **گزارش هفتگی بهره‌وری**

📅 **هفته:** {insights['week_start']} تا {insights['week_end']}

✅ **وظایف:**
   - تکمیل شده: {insights['tasks_completed']}
   - در انتظار: {insights['tasks_pending']}
   - نرخ تکمیل: {insights['completion_rate']:.0%}

📅 **جلسات:** {insights['meetings_count']} جلسه

⏰ **ساعات اوج بهره‌وری:**
"""
        
        peak_hours = insights.get('peak_hours', [])
        if peak_hours:
            report += f"   - {', '.join(map(str, peak_hours))}:00\n"
        else:
            report += "   - داده کافی نیست\n"
        
        # Stress signals
        stress = insights.get('stress_signals', {})
        if stress.get('stress_level') != 'low':
            report += f"\n⚠️ **سیگنال‌های استرس:**\n"
            report += f"   - سطح: {stress.get('stress_level', 'نامشخص')}\n"
            if stress.get('signals'):
                for signal in stress['signals']:
                    report += f"   - {signal.get('message', '')}\n"
        
        # Recommendations
        recommendations = insights.get('recommendations', [])
        if recommendations:
            report += f"\n💡 **توصیه‌ها:**\n"
            for rec in recommendations:
                report += f"   - {rec}\n"
        
        # Schedule suggestions
        schedule = insights.get('optimal_schedule_suggestions', {})
        if schedule:
            report += f"\n📋 **پیشنهاد برنامه روزانه:**\n"
            report += f"   - کار عمیق: {', '.join(map(str, schedule.get('deep_work_hours', [])))}:00\n"
            report += f"   - جلسات: {', '.join(map(str, schedule.get('meeting_hours', [])))}:00\n"
            report += f"   - استراحت: {', '.join(map(str, schedule.get('break_hours', [])))}:00\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در تولید گزارش هفتگی: {str(e)}"


@tool
def detect_stress_signals_tool(
    days_back: int = 14
) -> str:
    """
    Detect stress signals and potential burnout indicators from user patterns.
    
    Analyzes:
    - Overdue tasks
    - Meeting density
    - Task completion rates
    - Energy levels
    
    Args:
        days_back: Number of days to analyze (default: 14)
        
    Returns:
        Stress signal analysis report
    """
    try:
        analyzer = get_productivity_analyzer()
        stress = analyzer.detect_stress_signals(days_back)
        
        report = f"""🔍 **تحلیل سیگنال‌های استرس**

📊 **سطح استرس:** {stress.get('stress_level', 'نامشخص').upper()}

📈 **آمار:**
   - وظایف معوق: {stress.get('overdue_tasks_count', 0)}
   - روزهای پرجلسه: {stress.get('high_meeting_days_count', 0)}
   - نرخ تکمیل: {stress.get('completion_rate', 0):.0%}
   - میانگین انرژی: {stress.get('avg_energy', 0):.0%}

"""
        
        signals = stress.get('signals', [])
        if signals:
            report += "⚠️ **سیگنال‌های شناسایی شده:**\n"
            for signal in signals:
                severity_emoji = {
                    'high': '🔴',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(signal.get('severity', 'low'), '⚪')
                
                report += f"   {severity_emoji} {signal.get('message', '')}\n"
        else:
            report += "✅ هیچ سیگنال استرس شناسایی نشد.\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در تشخیص سیگنال‌های استرس: {str(e)}"


@tool
def suggest_schedule_optimization_tool(
    target_date: Optional[str] = None
) -> str:
    """
    Suggest calendar optimization based on productivity patterns.
    
    Provides:
    - Optimal time slots for deep work
    - Meeting scheduling recommendations
    - Break time suggestions
    
    Args:
        target_date: Target date for optimization in Jalali format (YYYY-MM-DD).
                    If not provided, uses tomorrow.
                    
    Returns:
        Schedule optimization suggestions
    """
    try:
        analyzer = get_productivity_analyzer()
        suggestions = analyzer.suggest_schedule_optimization(target_date)
        
        report = f"""📅 **پیشنهاد بهینه‌سازی برنامه**

📆 **تاریخ هدف:** {suggestions['target_date']}

⏰ **ساعات اوج:** {', '.join(map(str, suggestions.get('peak_hours', [])))}:00
🔋 **ساعات کم‌انرژی:** {', '.join(map(str, suggestions.get('low_energy_hours', [])))}:00

💡 **پیشنهادها:**
"""
        
        for suggestion in suggestions.get('suggestions', []):
            priority_emoji = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(suggestion.get('priority', 'low'), '⚪')
            
            report += f"   {priority_emoji} {suggestion.get('message', '')}\n"
        
        if not suggestions.get('suggestions'):
            report += "   ✅ برنامه شما بهینه است!\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در پیشنهاد بهینه‌سازی: {str(e)}"


@tool
def recommend_breaks_tool(
    target_date: Optional[str] = None
) -> str:
    """
    Recommend optimal break times based on productivity patterns.
    
    Considers:
    - Energy levels by time of day
    - Existing meeting schedule
    - Optimal break timing
    
    Args:
        target_date: Target date in Jalali format (YYYY-MM-DD).
                    If not provided, uses today.
                    
    Returns:
        Break time recommendations
    """
    try:
        analyzer = get_productivity_analyzer()
        recommendations = analyzer.recommend_breaks(target_date)
        
        if not recommendations:
            return "✅ برای این تاریخ پیشنهاد استراحتی نداریم."
        
        report = f"""☕ **پیشنهاد زمان‌های استراحت**

📆 **تاریخ:** {target_date or 'امروز'}

"""
        
        for rec in recommendations:
            rec_type_emoji = {
                'short_break': '☕',
                'lunch_break': '🍽️',
                'long_break': '🧘'
            }.get(rec.get('type', 'short_break'), '⏸️')
            
            report += f"   {rec_type_emoji} **{rec.get('time')}** ({rec.get('duration_minutes')} دقیقه)\n"
            report += f"      دلیل: {rec.get('reason', '')}\n\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در پیشنهاد استراحت: {str(e)}"


@tool
def analyze_productivity_patterns_tool(
    days_back: int = 30
) -> str:
    """
    Analyze productivity patterns over time.
    
    Provides:
    - Peak productivity hours
    - Most productive days
    - Task completion patterns
    - Meeting patterns
    - Productivity trends
    
    Args:
        days_back: Number of days to analyze (default: 30)
        
    Returns:
        Productivity pattern analysis report
    """
    try:
        analyzer = get_productivity_analyzer()
        patterns = analyzer.analyze_productivity_patterns(days_back)
        
        report = f"""📊 **تحلیل الگوهای بهره‌وری**

📅 **دوره تحلیل:** {patterns['analysis_period_days']} روز گذشته

📈 **آمار کلی:**
   - وظایف تکمیل شده: {patterns['total_tasks_completed']}
   - جلسات: {patterns['total_meetings']}
   - میانگین وظایف/روز: {patterns['avg_tasks_per_day']}
   - میانگین جلسات/روز: {patterns['avg_meetings_per_day']}

⏰ **ساعات اوج:** {', '.join(map(str, patterns.get('peak_hours', [])))}:00
🔋 **ساعات کم‌انرژی:** {', '.join(map(str, patterns.get('low_energy_hours', [])))}:00

"""
        
        peak_day = patterns.get('peak_productivity_day')
        if peak_day:
            report += f"📆 **روز پرتکمیل:** {peak_day}\n\n"
        
        # Task completion by day
        task_by_day = patterns.get('task_completion_by_day', {})
        if task_by_day:
            report += "📋 **تکمیل وظایف بر اساس روز هفته:**\n"
            for day, count in sorted(task_by_day.items(), key=lambda x: x[1], reverse=True):
                report += f"   - {day}: {count} وظیفه\n"
            report += "\n"
        
        # Trend
        trend = patterns.get('productivity_trend', 'stable')
        trend_emoji = {
            'improving': '📈',
            'declining': '📉',
            'stable': '➡️',
            'insufficient_data': '❓'
        }.get(trend, '➡️')
        
        report += f"📊 **روند:** {trend_emoji} {trend}\n"
        
        return report
    
    except Exception as e:
        return f"❌ خطا در تحلیل الگوها: {str(e)}"


# Export all tools
ALL_INSIGHT_TOOLS = [
    generate_weekly_insights_tool,
    detect_stress_signals_tool,
    suggest_schedule_optimization_tool,
    recommend_breaks_tool,
    analyze_productivity_patterns_tool
]


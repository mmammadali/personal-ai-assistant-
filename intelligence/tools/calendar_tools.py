"""
Calendar Optimization Tools
LangChain tools for intelligent calendar management
"""
from langchain_core.tools import tool
from typing import Optional, List
from intelligence.calendar_optimizer import CalendarOptimizer
from intelligence.energy_analyzer import EnergyAnalyzer


# Initialize optimizers
calendar_optimizer = CalendarOptimizer()
energy_analyzer = EnergyAnalyzer()


@tool
def optimize_calendar_tool(
    date: str,
    duration_hours: float = 1.0,
    meeting_type: str = "meeting"
) -> str:
    """
    Suggest optimal meeting times based on energy levels and existing schedule.
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). REQUIRED.
        duration_hours: Duration of the meeting in hours. Default: 1.0.
        meeting_type: Type of meeting - "meeting", "deep_work", or "task". Default: "meeting".
        
    Returns:
        Formatted string with top 5 optimal time suggestions
    """
    try:
        suggestions = calendar_optimizer.find_optimal_time_slot(
            date=date,
            duration_hours=duration_hours,
            avoid_low_energy=True,
            meeting_type=meeting_type
        )
        
        if not suggestions:
            return f"⚠️ No optimal time slots found for {date}. All hours may be busy or low energy."
        
        result = f"📅 Optimal time suggestions for {date} ({duration_hours}h {meeting_type}):\n\n"
        
        for i, slot in enumerate(suggestions, 1):
            hour = slot['hour']
            score = slot['score']
            energy = slot['energy_level']
            
            # Format hour
            hour_str = f"{hour}:00"
            if hour < 12:
                hour_str += " صبح"
            else:
                hour_str += " بعدازظهر"
            
            # Energy level emoji
            if energy >= 0.7:
                energy_emoji = "🔥"
            elif energy >= 0.5:
                energy_emoji = "⚡"
            else:
                energy_emoji = "💤"
            
            result += f"{i}. {hour_str} {energy_emoji}\n"
            result += f"   Energy Score: {energy:.2f} | Overall Score: {score:.2f}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error optimizing calendar: {str(e)}"


@tool
def block_optimal_slots_tool(
    date: str,
    block_type: str = "deep_work"
) -> str:
    """
    Suggest optimal time slots to block for focus work (deep work, breaks, preparation).
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). REQUIRED.
        block_type: Type of block - "deep_work", "break", or "preparation". Default: "deep_work".
        
    Returns:
        Formatted string with suggested time blocks
    """
    try:
        suggestions = calendar_optimizer.suggest_calendar_blocking(
            date=date,
            block_type=block_type
        )
        
        if not suggestions:
            return f"⚠️ No optimal blocks found for {date}. Calendar may be full."
        
        result = f"🛡️ Suggested {block_type} blocks for {date}:\n\n"
        
        for i, block in enumerate(suggestions, 1):
            start_hour = block['start_hour']
            duration = block['duration_hours']
            end_hour = (start_hour + int(duration)) % 24
            
            start_str = f"{start_hour}:00"
            end_str = f"{end_hour}:00"
            
            result += f"{i}. {start_str} - {end_str} ({duration}h)\n"
            result += f"   Score: {block['score']:.2f}\n\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error suggesting blocks: {str(e)}"


@tool
def analyze_energy_patterns_tool(
    days_back: int = 30
) -> str:
    """
    Analyze and identify your peak productivity hours based on historical data.
    
    Args:
        days_back: Number of days to analyze. Default: 30.
        
    Returns:
        Formatted analysis of energy patterns
    """
    try:
        peak_hours = energy_analyzer.identify_peak_hours(days_back)
        low_hours = energy_analyzer.identify_low_energy_hours(days_back)
        
        if not peak_hours:
            return "⚠️ Not enough data to analyze energy patterns. Start using the system to build patterns."
        
        result = f"📊 Energy Pattern Analysis (Last {days_back} days):\n\n"
        
        result += "🔥 Peak Productivity Hours:\n"
        for hour, energy in peak_hours[:5]:
            hour_str = f"{hour}:00"
            result += f"   {hour_str}: {energy:.2f} energy score\n"
        
        result += "\n💤 Low Energy Hours (avoid important tasks):\n"
        for hour, energy in low_hours[:5]:
            hour_str = f"{hour}:00"
            result += f"   {hour_str}: {energy:.2f} energy score\n"
        
        # Get optimal meeting and deep work hours
        optimal_meetings = energy_analyzer.get_optimal_meeting_hours(days_back=days_back)
        optimal_deep_work = energy_analyzer.get_optimal_deep_work_hours(days_back=days_back)
        
        result += "\n📅 Best Hours for Meetings:\n"
        for hour, score in optimal_meetings[:3]:
            hour_str = f"{hour}:00"
            result += f"   {hour_str}: {score:.2f} score\n"
        
        result += "\n💻 Best Hours for Deep Work:\n"
        for hour, score in optimal_deep_work[:3]:
            hour_str = f"{hour}:00"
            result += f"   {hour_str}: {score:.2f} score\n"
        
        return result
    
    except Exception as e:
        return f"❌ Error analyzing energy patterns: {str(e)}"


@tool
def suggest_meeting_time_tool(
    date: str,
    meeting_title: str,
    duration_hours: float = 1.0,
    meeting_description: Optional[str] = None
) -> str:
    """
    Suggest optimal meeting time with context awareness (preparation time, energy levels).
    
    Args:
        date: Target date in Jalali format (YYYY-MM-DD). REQUIRED.
        meeting_title: Title of the meeting. REQUIRED.
        duration_hours: Duration of the meeting. Default: 1.0.
        meeting_description: Optional description for better context.
        
    Returns:
        Comprehensive suggestion with optimal time and preparation recommendations
    """
    try:
        # Calculate preparation time needed
        prep_time = calendar_optimizer.calculate_preparation_time(
            meeting_title,
            meeting_description
        )
        
        # Find optimal time slots
        suggestions = calendar_optimizer.find_optimal_time_slot(
            date=date,
            duration_hours=duration_hours,
            avoid_low_energy=True,
            meeting_type="meeting"
        )
        
        if not suggestions:
            return f"⚠️ No optimal time slots found for {date}."
        
        result = f"📅 Meeting Time Suggestion: {meeting_title}\n"
        result += f"📆 Date: {date}\n"
        result += f"⏱️ Duration: {duration_hours} hours\n\n"
        
        if prep_time > 0.5:
            result += f"⏰ Recommended Preparation Time: {prep_time:.1f} hours\n"
            result += f"   (Block {prep_time:.1f}h before the meeting for preparation)\n\n"
        
        result += "🎯 Top 3 Optimal Time Slots:\n\n"
        
        for i, slot in enumerate(suggestions[:3], 1):
            hour = slot['hour']
            score = slot['score']
            energy = slot['energy_level']
            
            hour_str = f"{hour}:00"
            if hour < 12:
                hour_str += " صبح"
            else:
                hour_str += " بعدازظهر"
            
            energy_emoji = "🔥" if energy >= 0.7 else "⚡" if energy >= 0.5 else "💤"
            
            result += f"{i}. {hour_str} {energy_emoji}\n"
            result += f"   Energy: {energy:.2f} | Score: {score:.2f}\n"
            
            if prep_time > 0:
                prep_hour = (hour - int(prep_time)) % 24
                prep_str = f"{prep_hour}:00"
                result += f"   📚 Prep time: {prep_str} - {hour_str}\n"
            
            result += "\n"
        
        return result.strip()
    
    except Exception as e:
        return f"❌ Error suggesting meeting time: {str(e)}"


# Export all calendar tools
CALENDAR_TOOLS = [
    optimize_calendar_tool,
    block_optimal_slots_tool,
    analyze_energy_patterns_tool,
    suggest_meeting_time_tool
]


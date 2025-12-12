"""
LangChain tools for Meeting Management & Transcription Agent
All tools with proper schemas, validation, and Jalali date support
"""
from langchain_core.tools import tool
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# These will be initialized by the meeting agent
_transcription_agent = None
_analysis_agent = None
_analytics_agent = None
_followup_agent = None
_export_service = None
_db = None


def initialize_tools(
    transcription_agent,
    analysis_agent,
    analytics_agent,
    followup_agent,
    export_service,
    db
):
    """Initialize tool dependencies"""
    global _transcription_agent, _analysis_agent, _analytics_agent
    global _followup_agent, _export_service, _db
    
    _transcription_agent = transcription_agent
    _analysis_agent = analysis_agent
    _analytics_agent = analytics_agent
    _followup_agent = followup_agent
    _export_service = export_service
    _db = db


@tool
def transcribe_meeting_tool(
    audio_path: str,
    meeting_title: str,
    date: str,
    user_id: str = "default"
) -> str:
    """
    Transcribe a meeting audio file and create a meeting record.
    
    Args:
        audio_path: Path to audio file. REQUIRED.
        meeting_title: Title of the meeting. REQUIRED.
        date: Meeting date in Jalali format (YYYY-MM-DD). REQUIRED.
        user_id: User identifier. OPTIONAL (default: "default").
        
    Returns:
        Success message with meeting ID and transcription status
    """
    try:
        if not _db:
            return "❌ Meeting tools not initialized"
        
        # Create meeting record
        meeting_id = _db.create_meeting(
            user_id=user_id,
            title=meeting_title,
            date=date,
            recording_path=audio_path
        )
        
        # Transcribe
        result = _transcription_agent.transcribe_meeting(
            audio_path=audio_path,
            meeting_id=meeting_id,
            user_id=user_id
        )
        
        if result.get("success"):
            return f"✅ جلسه با موفقیت رونویسی شد!\n\n" \
                   f"شناسه جلسه: {meeting_id}\n" \
                   f"عنوان: {meeting_title}\n" \
                   f"تعداد بخش‌ها: {result.get('segments_count', 0)}\n" \
                   f"تعداد گویندگان: {result.get('speakers_count', 0)}"
        else:
            return f"❌ خطا در رونویسی: {result.get('error', 'خطای نامشخص')}"
            
    except Exception as e:
        logger.error(f"Error in transcribe_meeting_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def get_meeting_transcript_tool(meeting_id: int) -> str:
    """
    Get transcript for a meeting.
    
    Args:
        meeting_id: Meeting ID. REQUIRED.
        
    Returns:
        Meeting transcript text
    """
    try:
        if not _transcription_agent:
            return "❌ Meeting tools not initialized"
        
        result = _transcription_agent.get_transcript(meeting_id)
        
        if result.get("success"):
            transcript = result.get("transcript", "")
            segments_count = result.get("segments_count", 0)
            return f"📝 **رونویسی جلسه {meeting_id}:**\n\n{transcript}\n\n" \
                   f"تعداد بخش‌ها: {segments_count}"
        else:
            return f"❌ {result.get('error', 'خطای نامشخص')}"
            
    except Exception as e:
        logger.error(f"Error in get_meeting_transcript_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def get_meeting_summary_tool(meeting_id: int) -> str:
    """
    Get summary for a meeting.
    
    Args:
        meeting_id: Meeting ID. REQUIRED.
        
    Returns:
        Meeting summary text
    """
    try:
        if not _analysis_agent or not _db:
            return "❌ Meeting tools not initialized"
        
        meeting = _db.get_meeting(meeting_id)
        if not meeting:
            return f"❌ جلسه با شناسه {meeting_id} یافت نشد"
        
        summary = meeting.get("summary")
        if summary:
            return f"📋 **خلاصه جلسه {meeting_id}:**\n\n{summary}"
        else:
            # Generate summary if not exists
            segments = _db.get_transcript(meeting_id)
            if not segments:
                return "❌ رونویسی برای این جلسه موجود نیست"
            
            transcript = " ".join([seg.get("text", "") for seg in segments])
            summary = _analysis_agent.generate_summary(transcript, meeting_id)
            return f"📋 **خلاصه جلسه {meeting_id}:**\n\n{summary}"
            
    except Exception as e:
        logger.error(f"Error in get_meeting_summary_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def get_action_items_tool(meeting_id: Optional[int] = None, user_id: str = "default") -> str:
    """
    Get action items for a meeting or user.
    
    Args:
        meeting_id: Meeting ID. OPTIONAL (if not provided, returns all user's action items).
        user_id: User identifier. OPTIONAL (default: "default").
        
    Returns:
        List of action items
    """
    try:
        if not _followup_agent or not _db:
            return "❌ Meeting tools not initialized"
        
        if meeting_id:
            action_items = _followup_agent.track_action_items(meeting_id)
            if not action_items:
                return f"📋 هیچ اقداماتی برای جلسه {meeting_id} یافت نشد"
            
            result = f"📋 **اقدامات جلسه {meeting_id}:**\n\n"
            for idx, item in enumerate(action_items, 1):
                result += f"{idx}. {item.get('description', '')}\n"
                if item.get('assignee'):
                    result += f"   مسئول: {item.get('assignee')}\n"
                if item.get('due_date'):
                    result += f"   مهلت: {item.get('due_date')}\n"
                result += f"   وضعیت: {item.get('status', 'pending')}\n\n"
            
            return result
        else:
            action_items = _followup_agent.get_pending_action_items(user_id)
            if not action_items:
                return "📋 هیچ اقدام در حال انتظاری یافت نشد"
            
            result = f"📋 **اقدامات در حال انتظار:**\n\n"
            for idx, item in enumerate(action_items, 1):
                result += f"{idx}. {item.get('description', '')}\n"
                if item.get('assignee'):
                    result += f"   مسئول: {item.get('assignee')}\n"
                if item.get('due_date'):
                    result += f"   مهلت: {item.get('due_date')}\n"
                if item.get('is_overdue'):
                    result += f"   ⚠️ گذشته از مهلت\n"
                result += f"   وضعیت: {item.get('status', 'pending')}\n\n"
            
            return result
            
    except Exception as e:
        logger.error(f"Error in get_action_items_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def get_meeting_analytics_tool(meeting_id: int) -> str:
    """
    Get analytics for a meeting (talk time, participation, etc.).
    
    Args:
        meeting_id: Meeting ID. REQUIRED.
        
    Returns:
        Meeting analytics
    """
    try:
        if not _analytics_agent:
            return "❌ Meeting tools not initialized"
        
        analytics = _analytics_agent.get_comprehensive_analytics(meeting_id)
        
        if not analytics.get("success"):
            return f"❌ {analytics.get('error', 'خطای نامشخص')}"
        
        result = f"📊 **تحلیل جلسه {meeting_id}:**\n\n"
        
        # Talk time
        talk_time = analytics.get("talk_time", {})
        if talk_time.get("success"):
            result += f"**زمان صحبت:**\n"
            result += f"کل زمان: {talk_time.get('total_time_minutes', 0):.2f} دقیقه\n\n"
            for speaker in talk_time.get("speakers", []):
                result += f"- {speaker['speaker_name']}: {speaker['talk_time_minutes']:.2f} دقیقه ({speaker['percentage']:.1f}%)\n"
            result += "\n"
        
        # Word count
        word_count = analytics.get("word_count", {})
        if word_count.get("success"):
            result += f"**تعداد کلمات:**\n"
            result += f"کل: {word_count.get('total_words', 0)} کلمه\n\n"
            for speaker in word_count.get("speakers", []):
                result += f"- {speaker['speaker_name']}: {speaker['word_count']} کلمه ({speaker['percentage']:.1f}%)\n"
            result += "\n"
        
        return result
            
    except Exception as e:
        logger.error(f"Error in get_meeting_analytics_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def search_meetings_tool(
    query: str,
    user_id: str = "default",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> str:
    """
    Search meetings by title or summary.
    
    Args:
        query: Search query. REQUIRED.
        user_id: User identifier. OPTIONAL (default: "default").
        date_from: Start date in Jalali format (YYYY-MM-DD). OPTIONAL.
        date_to: End date in Jalali format (YYYY-MM-DD). OPTIONAL.
        
    Returns:
        List of matching meetings
    """
    try:
        if not _db:
            return "❌ Meeting tools not initialized"
        
        meetings = _db.search_meetings(
            user_id=user_id,
            query=query,
            date_from=date_from,
            date_to=date_to
        )
        
        if not meetings:
            return f"📋 هیچ جلسه‌ای با جستجوی '{query}' یافت نشد"
        
        result = f"📋 **نتایج جستجو برای '{query}':**\n\n"
        for idx, meeting in enumerate(meetings, 1):
            result += f"{idx}. {meeting.get('title', 'N/A')}\n"
            result += f"   تاریخ: {meeting.get('date', 'N/A')}\n"
            result += f"   شناسه: {meeting.get('id')}\n\n"
        
        return result
            
    except Exception as e:
        logger.error(f"Error in search_meetings_tool: {e}")
        return f"❌ خطا: {str(e)}"


@tool
def export_meeting_tool(
    meeting_id: int,
    format: str = "pdf",
    export_type: str = "transcript"
) -> str:
    """
    Export meeting data to file (transcript, summary, or action items).
    
    Args:
        meeting_id: Meeting ID. REQUIRED.
        format: Export format (pdf, docx, txt). OPTIONAL (default: "pdf").
        export_type: Type of export (transcript, summary, action_items). OPTIONAL (default: "transcript").
        
    Returns:
        Path to exported file
    """
    try:
        if not _export_service:
            return "❌ Meeting tools not initialized"
        
        if export_type == "transcript":
            file_path = _export_service.export_transcript(meeting_id, format)
        elif export_type == "summary":
            file_path = _export_service.export_summary(meeting_id, format)
        elif export_type == "action_items":
            file_path = _export_service.export_action_items(meeting_id, format)
        else:
            return f"❌ نوع خروجی نامعتبر: {export_type}. گزینه‌ها: transcript, summary, action_items"
        
        return f"✅ فایل با موفقیت ایجاد شد:\n{file_path}"
            
    except Exception as e:
        logger.error(f"Error in export_meeting_tool: {e}")
        return f"❌ خطا: {str(e)}"


# List of all meeting tools
MEETING_TOOLS = [
    transcribe_meeting_tool,
    get_meeting_transcript_tool,
    get_meeting_summary_tool,
    get_action_items_tool,
    get_meeting_analytics_tool,
    search_meetings_tool,
    export_meeting_tool
]


"""
Meeting Agent - Main Entry Point
Multi-agent system for meeting management and transcription
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import operator
import jdatetime
import pytz
from pathlib import Path

from meeting.database import MeetingDatabase
from meeting.agents.transcription_agent import TranscriptionAgent
from meeting.agents.analysis_agent import AnalysisAgent
from meeting.agents.analytics_agent import AnalyticsAgent
from meeting.agents.followup_agent import FollowUpAgent
from meeting.services.export_service import ExportService
from meeting.tools import initialize_tools, MEETING_TOOLS


# ===================== STATE DEFINITION =====================

class MeetingState(TypedDict):
    """State for the meeting assistant agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    pending_action: dict | None  # Stores action awaiting approval
    memory: list[dict]  # Conversation history
    current_agent: str | None  # Track which sub-agent is active
    user_id: str  # User identifier


# ===================== MEETING AGENT CLASS =====================

class MeetingAgent:
    """
    Main Meeting Assistant with internal multi-agent orchestration
    
    Features:
    - Audio Transcription (via Soniox for Farsi)
    - Action Item Extraction
    - Meeting Summaries
    - Analytics (talk time, participation)
    - Follow-up Tracking
    - Export (PDF, DOCX, TXT)
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o", db_path: str = "meeting.db"):
        """
        Initialize the Meeting Agent
        
        Args:
            openai_api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            db_path: Path to meeting database
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=openai_api_key
        )
        
        # Initialize database
        self.db = MeetingDatabase(db_path)
        
        # Initialize sub-agents
        self.transcription_agent = TranscriptionAgent(self.db)
        self.analysis_agent = AnalysisAgent(self.llm, self.db)
        self.analytics_agent = AnalyticsAgent(self.db)
        self.followup_agent = FollowUpAgent(self.db)
        self.export_service = ExportService(self.db)
        
        # Initialize tools
        initialize_tools(
            self.transcription_agent,
            self.analysis_agent,
            self.analytics_agent,
            self.followup_agent,
            self.export_service,
            self.db
        )
        
        # Create orchestrator graph
        self.memory = MemorySaver()
        self.app = self._build_graph()
        
        print("✅ Meeting Agent initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for meeting orchestration"""
        workflow = StateGraph(MeetingState)
        
        # Add nodes
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("response", self._response_node)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Add edges
        workflow.add_edge("orchestrator", "response")
        workflow.add_edge("response", END)
        
        # Compile with checkpointer
        return workflow.compile(checkpointer=self.memory)
    
    def _get_system_prompt(self) -> str:
        """Generate system prompt for meeting orchestrator"""
        tehran_tz = pytz.timezone('Asia/Tehran')
        current_time = jdatetime.datetime.now(tz=tehran_tz)
        today = current_time.date()
        
        return f"""شما دستیار هوشمند مدیریت جلسات برای مدیران ایرانی هستید.
        
**زمان فعلی**: {current_time.strftime('%Y-%m-%d %H:%M:%S')} تهران (امروز: {today.strftime('%Y-%m-%d')})

**قابلیت‌های شما**:

1. **رونویسی جلسات**: رونویسی فایل‌های صوتی جلسات به زبان فارسی (با استفاده از Soniox)
2. **استخراج اقدامات**: شناسایی و استخراج خودکار اقدامات و وظایف از رونویسی
3. **خلاصه‌سازی**: تولید خلاصه‌های جامع از جلسات
4. **تحلیل جلسات**: محاسبه زمان صحبت، مشارکت، و آمارهای دیگر
5. **پیگیری اقدامات**: ردیابی وضعیت اقدامات و وظایف
6. **خروجی**: صادرات رونویسی، خلاصه و اقدامات به PDF/DOCX/TXT

**زمینه ایرانی**:
- تقویم: جلالی (شمسی)
- زبان: فارسی
- تاریخ‌ها به فرمت YYYY-MM-DD جلالی

**رفتار شما**:
- همیشه به فارسی پاسخ دهید
- واضح و مفید باشید
- برای رونویسی، نیاز به مسیر فایل صوتی دارید
- برای تحلیل، نیاز به شناسه جلسه دارید
- پیشنهادات فعالانه ارائه دهید

**ابزارهای موجود**:
- transcribe_meeting_tool: رونویسی فایل صوتی
- get_meeting_transcript_tool: دریافت رونویسی
- get_meeting_summary_tool: دریافت خلاصه
- get_action_items_tool: دریافت اقدامات
- get_meeting_analytics_tool: دریافت تحلیل
- search_meetings_tool: جستجوی جلسات
- export_meeting_tool: صادرات به فایل
"""
    
    def _orchestrator_node(self, state: MeetingState) -> MeetingState:
        """Main orchestrator node - routes to appropriate sub-agent"""
        messages = state["messages"]
        user_id = state.get("user_id", "default")
        
        # Get last user message
        last_message = messages[-1].content if messages else ""
        last_message_lower = last_message.lower()
        
        # Route to appropriate agent based on keywords
        response_content = None
        
        # Transcription queries
        transcription_keywords = ["رونویسی", "transcribe", "transcription", "فایل صوتی", "audio"]
        if any(keyword in last_message_lower for keyword in transcription_keywords):
            # Check if audio path is mentioned
            import re
            # Look for file paths
            path_patterns = [
                r'[A-Za-z]:[\\/][^\s]+',
                r'[\\/][^\s]+',
                r'\.(mp3|wav|m4a|aac|ogg|flac)'
            ]
            audio_path = None
            for pattern in path_patterns:
                matches = re.findall(pattern, last_message)
                if matches:
                    audio_path = matches[0]
                    break
            
            if audio_path:
                # Extract meeting title and date
                # Use LLM to extract structured info
                try:
                    extract_prompt = f"""از پیام کاربر زیر، اطلاعات جلسه را استخراج کن:
{last_message}

استخراج کن:
- عنوان جلسه (meeting_title)
- تاریخ جلسه (date) - به فرمت جلالی YYYY-MM-DD

JSON برگردان:
{{
    "meeting_title": "...",
    "date": "1403-09-15"
}}"""

                    system_prompt = """شما باید اطلاعات جلسه را از پیام کاربر استخراج کنید.
- اگر تاریخ ذکر نشده، از امروز استفاده کن
- فقط JSON برگردان"""

                    llm_response = self.llm.invoke([
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=extract_prompt)
                    ])
                    
                    import json
                    response_text = llm_response.content.strip()
                    json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                    if json_match:
                        meeting_data = json.loads(json_match.group())
                        meeting_title = meeting_data.get("meeting_title", "جلسه")
                        date = meeting_data.get("date", jdatetime.date.today().strftime("%Y-%m-%d"))
                        
                        # Create meeting record first
                        meeting_id = self.db.create_meeting(
                            user_id=user_id,
                            title=meeting_title,
                            date=date,
                            recording_path=audio_path
                        )
                        
                        # Transcribe
                        result = self.transcription_agent.transcribe_meeting(
                            audio_path=audio_path,
                            meeting_id=meeting_id,
                            user_id=user_id
                        )
                        
                        if result.get("success"):
                            response_content = f"✅ جلسه با موفقیت رونویسی شد!\n\n" \
                                             f"شناسه جلسه: {meeting_id}\n" \
                                             f"عنوان: {meeting_title}\n" \
                                             f"تعداد بخش‌ها: {result.get('segments_count', 0)}\n" \
                                             f"تعداد گویندگان: {result.get('speakers_count', 0)}"
                        else:
                            response_content = f"❌ خطا در رونویسی: {result.get('error', 'خطای نامشخص')}"
                    else:
                        response_content = "لطفاً مسیر فایل صوتی و اطلاعات جلسه را مشخص کنید"
                except Exception as e:
                    response_content = f"❌ خطا در پردازش: {str(e)}"
            else:
                response_content = "برای رونویسی، لطفاً مسیر فایل صوتی را مشخص کنید.\n" \
                                 "مثال: \"فایل صوتی /path/to/audio.mp3 را رونویسی کن\""
        
        # Summary queries
        summary_keywords = ["خلاصه", "summary", "خلاصه جلسه"]
        if not response_content and any(keyword in last_message_lower for keyword in summary_keywords):
            # Extract meeting ID
            import re
            meeting_id_match = re.search(r'\d+', last_message)
            if meeting_id_match:
                meeting_id = int(meeting_id_match.group())
                meeting = self.db.get_meeting(meeting_id)
                if meeting:
                    summary = meeting.get("summary")
                    if summary:
                        response_content = f"📋 **خلاصه جلسه {meeting_id}:**\n\n{summary}"
                    else:
                        # Generate summary
                        segments = self.db.get_transcript(meeting_id)
                        if segments:
                            transcript = " ".join([seg.get("text", "") for seg in segments])
                            summary = self.analysis_agent.generate_summary(transcript, meeting_id)
                            response_content = f"📋 **خلاصه جلسه {meeting_id}:**\n\n{summary}"
                        else:
                            response_content = "❌ رونویسی برای این جلسه موجود نیست"
                else:
                    response_content = f"❌ جلسه با شناسه {meeting_id} یافت نشد"
            else:
                response_content = "لطفاً شناسه جلسه را مشخص کنید.\n" \
                                 "مثال: \"خلاصه جلسه 1 را نشان بده\""
        
        # Action items queries
        action_keywords = ["اقدامات", "action items", "وظایف", "tasks", "todo"]
        if not response_content and any(keyword in last_message_lower for keyword in action_keywords):
            import re
            meeting_id_match = re.search(r'\d+', last_message)
            if meeting_id_match:
                meeting_id = int(meeting_id_match.group())
                action_items = self.followup_agent.track_action_items(meeting_id)
                if action_items:
                    response_content = f"📋 **اقدامات جلسه {meeting_id}:**\n\n"
                    for idx, item in enumerate(action_items, 1):
                        response_content += f"{idx}. {item.get('description', '')}\n"
                        if item.get('assignee'):
                            response_content += f"   مسئول: {item.get('assignee')}\n"
                        if item.get('due_date'):
                            response_content += f"   مهلت: {item.get('due_date')}\n"
                        response_content += f"   وضعیت: {item.get('status', 'pending')}\n\n"
                else:
                    response_content = f"📋 هیچ اقداماتی برای جلسه {meeting_id} یافت نشد"
            else:
                # Get all pending items for user
                action_items = self.followup_agent.get_pending_action_items(user_id)
                if action_items:
                    response_content = f"📋 **اقدامات در حال انتظار:**\n\n"
                    for idx, item in enumerate(action_items, 1):
                        response_content += f"{idx}. {item.get('description', '')}\n"
                        if item.get('assignee'):
                            response_content += f"   مسئول: {item.get('assignee')}\n"
                        if item.get('due_date'):
                            response_content += f"   مهلت: {item.get('due_date')}\n"
                        if item.get('is_overdue'):
                            response_content += f"   ⚠️ گذشته از مهلت\n"
                        response_content += f"   وضعیت: {item.get('status', 'pending')}\n\n"
                else:
                    response_content = "📋 هیچ اقدام در حال انتظاری یافت نشد"
        
        # Analytics queries
        analytics_keywords = ["تحلیل", "analytics", "آمار", "زمان صحبت", "talk time", "participation"]
        if not response_content and any(keyword in last_message_lower for keyword in analytics_keywords):
            import re
            meeting_id_match = re.search(r'\d+', last_message)
            if meeting_id_match:
                meeting_id = int(meeting_id_match.group())
                analytics = self.analytics_agent.get_comprehensive_analytics(meeting_id)
                if analytics.get("success"):
                    talk_time = analytics.get("talk_time", {})
                    result_text = f"📊 **تحلیل جلسه {meeting_id}:**\n\n"
                    if talk_time.get("success"):
                        result_text += f"**زمان صحبت:**\n"
                        result_text += f"کل زمان: {talk_time.get('total_time_minutes', 0):.2f} دقیقه\n\n"
                        for speaker in talk_time.get("speakers", []):
                            result_text += f"- {speaker['speaker_name']}: {speaker['talk_time_minutes']:.2f} دقیقه ({speaker['percentage']:.1f}%)\n"
                    response_content = result_text
                else:
                    response_content = f"❌ {analytics.get('error', 'خطای نامشخص')}"
            else:
                response_content = "لطفاً شناسه جلسه را مشخص کنید.\n" \
                                 "مثال: \"تحلیل جلسه 1 را نشان بده\""
        
        # If no specific routing, use LLM with tools
        if not response_content:
            # Get system prompt
            system_message = SystemMessage(content=self._get_system_prompt())
            
            # Add memory context if available
            if state.get("memory"):
                memory_context = "\n\n**گفتگوهای اخیر**:\n"
                for i, interaction in enumerate(state["memory"][-5:], 1):
                    memory_context += f"{i}. کاربر: {interaction.get('user', 'N/A')}\n   دستیار: {interaction.get('assistant', 'N/A')}\n"
                system_message.content += memory_context
            
            # Bind tools to LLM
            llm_with_tools = self.llm.bind_tools(MEETING_TOOLS)
            
            # Invoke LLM
            response = llm_with_tools.invoke([system_message] + list(messages))
            
            # Check if LLM wants to use tools
            if hasattr(response, "tool_calls") and response.tool_calls:
                # Execute tool
                from langgraph.prebuilt import ToolNode
                tool_node = ToolNode(MEETING_TOOLS)
                tool_result = tool_node({"messages": [response]})
                response_content = tool_result["messages"][-1].content
            else:
                response_content = response.content
        else:
            # Create AI message with the routed response
            response = AIMessage(content=response_content)
        
        return {"messages": [response]}
    
    def _response_node(self, state: MeetingState) -> MeetingState:
        """Final response node"""
        return state
    
    def chat(
        self,
        user_input: str,
        thread_id: str = "default",
        user_id: str = "default"
    ) -> str:
        """
        Main chat interface
        
        Args:
            user_input: User's message
            thread_id: Conversation thread ID
            user_id: User identifier
            
        Returns:
            Assistant's response
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        current_state = self.app.get_state(config)
        
        try:
            result = self.app.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "memory": current_state.values.get("memory", []) if current_state.values else [],
                    "user_id": user_id,
                    "current_agent": None,
                    "pending_action": None
                },
                config
            )
            
            # Return last message
            return result["messages"][-1].content
        except Exception as e:
            error_msg = f"❌ خطایی رخ داد: {str(e)}\nلطفاً دوباره تلاش کنید."
            return error_msg
    
    def transcribe_meeting(
        self,
        audio_path: str,
        meeting_title: str,
        date: str,
        user_id: str = "default"
    ) -> dict:
        """
        Transcribe a meeting audio file
        
        Args:
            audio_path: Path to audio file
            meeting_title: Meeting title
            date: Meeting date (Jalali format)
            user_id: User identifier
            
        Returns:
            Transcription result
        """
        # Create meeting record
        meeting_id = self.db.create_meeting(
            user_id=user_id,
            title=meeting_title,
            date=date,
            recording_path=audio_path
        )
        
        # Transcribe
        result = self.transcription_agent.transcribe_meeting(
            audio_path=audio_path,
            meeting_id=meeting_id,
            user_id=user_id
        )
        
        return result
    
    def get_meeting_summary(self, meeting_id: int) -> str:
        """Get meeting summary"""
        meeting = self.db.get_meeting(meeting_id)
        if not meeting:
            return f"❌ جلسه با شناسه {meeting_id} یافت نشد"
        
        summary = meeting.get("summary")
        if summary:
            return summary
        
        # Generate if not exists
        segments = self.db.get_transcript(meeting_id)
        if segments:
            transcript = " ".join([seg.get("text", "") for seg in segments])
            return self.analysis_agent.generate_summary(transcript, meeting_id)
        
        return "❌ رونویسی برای این جلسه موجود نیست"
    
    def reset_conversation(self, thread_id: str = "default"):
        """
        Clear conversation history
        
        Args:
            thread_id: Conversation thread ID
        """
        config = {"configurable": {"thread_id": thread_id}}
        # Reset by updating state
        self.app.update_state(config, {
            "messages": [],
            "memory": [],
            "pending_action": None,
            "current_agent": None
        }, as_node="__start__")


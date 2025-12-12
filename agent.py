"""
LangGraph Agent for Iranian Manager Personal Assistant
Includes human-in-the-loop, memory, and Jalali date support
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import operator
import jdatetime
import pytz
from tools import ALL_TOOLS
from config import get_model_for_query, DEFAULT_MODEL, COMPLEX_MODEL


# ===================== STATE DEFINITION =====================

class AgentState(TypedDict):
    """State for the personal assistant agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    pending_action: list[dict] | dict | None  # Stores actions awaiting approval (supports batches)
    memory: list[dict]  # Last 7 interactions


# ===================== SYSTEM PROMPT =====================

def get_system_prompt() -> str:
    """Generate system prompt with current Tehran time"""
    tehran_tz = pytz.timezone('Asia/Tehran')
    current_time = jdatetime.datetime.now(tz=tehran_tz)
    
    # Calculate relative dates for examples
    today = current_time.date()
    tomorrow = today + jdatetime.timedelta(days=1)
    day_after_tomorrow = today + jdatetime.timedelta(days=2)
    yesterday = today + jdatetime.timedelta(days=-1)
    # Next Saturday (future-oriented, Jalali weeks start on Saturday)
    greg_weekday = today.togregorian().weekday()  # Monday=0 ... Sunday=6
    days_to_next_saturday = (5 - greg_weekday + 7) % 7
    if days_to_next_saturday == 0:
        days_to_next_saturday = 7
    next_saturday = today + jdatetime.timedelta(days=days_to_next_saturday)
    
    return f"""شما دستیار هوشمند مدیران ایرانی هستید. زمان: {current_time.strftime('%Y-%m-%d %H:%M:%S')} تهران (امروز: {today.strftime('%Y-%m-%d')})

**رفتار**: سریع و مستقیم. فقط فیلدهای **الزامی** را چک کنید. اگر الزامی‌ها موجود است، فوراً tool بزنید - هیچ سوال اضافی نپرسید!

**قابلیت‌ها**: 
- مدیریت رویدادها و وظایف (ایجاد/جستجو/به‌روزرسانی)
- تحلیل الگوهای بهره‌وری و گزارش‌های هفتگی
- یادگیری ترجیحات کاربر و شخصی‌سازی
- خودکارسازی الگوهای تکراری
- آماده‌سازی جلسات (خلاصه، نکات گفتگو، پیش‌بینی سوالات)
- تولید گزارش‌ها و اسناد
- تحلیل اسناد و مقایسه نسخه‌ها

**🔥 رویداد یا وظیفه؟**

**رویداد**: جلسه، meeting، ملاقات، دیدار، قرار، میتینگ، پرزنتیشن → با کسی ("با آقای احمدی") یا در مکانی ("در دفتر")
مثال: "فردا ساعت 10 جلسه با آقای احمدی"

**وظیفه**: کار فردی با فعل عملی (تماس، ایمیل، گزارش، بررسی) یا "باید"/"یادم باشد"
مثال: "فردا باید به آقای احمدی زنگ بزنم"

**کلمات کلیدی**:
- رویداد: جلسه، meeting، ملاقات، قرار، "با" (کسی), "در" (جایی)
- وظیفه: باید، یادآوری، تماس، ایمیل، آماده کردن، بررسی، پرداخت

**قوانین**:

1. **فیلدهای الزامی** (فقط اینها):
   - رویداد: تاریخ + عنوان (بقیه اختیاری)
   - وظیفه: مهلت + توضیحات (بقیه اختیاری)
   - هرگز برای فیلدهای اختیاری سوال نکنید!

2. **جریان**: 
   - جستجو → فوراً اجرا
   - ایجاد/به‌روزرسانی → الزامی‌ها موجود؟ فوراً tool بزنید | ناقص؟ فقط الزامی‌ها را بپرسید
   - هرگز خودتان تأیید نخواهید - سیستم خودش می‌گیرد

3. **استخراج تاریخ** (جلالی YYYY-MM-DD):
   - امروز → {today.strftime('%Y-%m-%d')} | فردا → {tomorrow.strftime('%Y-%m-%d')} | پس‌فردا → {day_after_tomorrow.strftime('%Y-%m-%d')}
   - دیروز → {yesterday.strftime('%Y-%m-%d')} | هفته آینده → +7 روز | ماه آینده → +30 روز
   - شنبه‌ی پیش‌رو (next Saturday) → {next_saturday.strftime('%Y-%m-%d')}
   - مثال حیاتی: اگر امروز {today.strftime('%Y-%m-%d')} (پنجشنبه) باشد، «هفته آینده شنبه» یا «next week Saturday» = {next_saturday.strftime('%Y-%m-%d')} (همین شنبه‌ی پیش‌رو، نه یک هفته دیرتر)

4. **استخراج عنوان**: از کل متن بگیرید
   - ✅ "جلسه با آقای احمدی ساعت 10" | "پرزنتیشن محصول" | "میتینگ تیم"
   - ❌ فقط "جلسه" بدون جزئیات → ناقص

5. **استخراج مکان/افراد**: 
   - مکان: "در دفتر"، "کافه"، "زوم" → اختیاری
   - افراد: "با آقای احمدی"، "همراه تیم" → اختیاری

**مثال‌های کامل**:

✅ درست:
کاربر: "فردا ساعت 14 جلسه با آقای کریمی در دفتر"
→ فوراً create_event_tool(date={tomorrow.strftime('%Y-%m-%d')}, title="جلسه با آقای کریمی ساعت 14", location="دفتر")

❌ غلط:
کاربر: "فردا جلسه"
→ "لطفاً عنوان جلسه را بگویید" (عنوان الزامی ناقص است)

✅ وظیفه:
کاربر: "فردا باید به احمدی زنگ بزنم"
→ create_task_tool(due_date={tomorrow.strftime('%Y-%m-%d')}, description="تماس با احمدی")

❌ اشتباه رایج:
کاربر: "فردا باید زنگ بزنم" با create_event_tool ← غلط! این وظیفه است

**قانون طلایی**: تاریخ+عنوان یا مهلت+توضیحات موجود؟ → فوراً tool بزنید، هیچ سوال نکنید!
"""


# ===================== GRAPH NODES =====================

def create_agent_node(base_llm: ChatOpenAI):
    """Create the main agent reasoning node with dynamic model selection"""
    
    def agent_node(state: AgentState) -> AgentState:
        """Agent decides what to do based on user input"""
        messages = state["messages"]
        
        # Extract user query from messages to determine model
        user_query = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content') and isinstance(msg, HumanMessage):
                user_query = str(msg.content)
                break
        
        # Select appropriate model based on query complexity
        selected_model = get_model_for_query(user_query)
        
        # Get base model name for comparison
        base_model = getattr(base_llm, 'model_name', None) or getattr(base_llm, '_default_params', {}).get('model', DEFAULT_MODEL)
        
        # Create LLM with selected model if different from base
        if selected_model != base_model:
            from langchain_openai import ChatOpenAI
            from config import OPENAI_API_KEY
            llm = ChatOpenAI(
                api_key=OPENAI_API_KEY,
                model=selected_model,
                temperature=0
            )
        else:
            llm = base_llm
        
        # Add system prompt
        system_message = SystemMessage(content=get_system_prompt())
        
        # Add memory context if available
        if state.get("memory"):
            memory_context = "\n\n**RECENT INTERACTIONS**:\n"
            for i, interaction in enumerate(state["memory"][-7:], 1):
                memory_context += f"{i}. User: {interaction.get('user', 'N/A')}\n   Assistant: {interaction.get('assistant', 'N/A')}\n"
            system_message.content += memory_context
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(ALL_TOOLS)
        
        # Invoke LLM
        response = llm_with_tools.invoke([system_message] + list(messages))
        
        return {"messages": [response]}
    
    return agent_node


def should_continue(state: AgentState) -> Literal["tools", "check_approval", "end"]:
    """Determine next step based on agent's response"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the agent used tools
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # Tools requiring approval
        approval_tools = {"create_event_tool", "update_event_tool", "delete_event_tool", "create_task_tool", "update_task_status_tool"}
        # If any of the proposed tool calls needs approval, route to approval flow
        if any(tc.get("name") in approval_tools for tc in last_message.tool_calls):
            return "check_approval"
        # Otherwise execute tools directly
        return "tools"
    
    # No tools, end conversation
    return "end"


def check_approval_node(state: AgentState) -> AgentState:
    """Store pending action and request user approval"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Store the pending tool call
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        # Collect only the tool calls that require approval
        approval_tools = {"create_event_tool", "update_event_tool", "delete_event_tool", "create_task_tool", "update_task_status_tool"}
        tool_calls = [tc for tc in last_message.tool_calls if tc.get("name") in approval_tools]
        if not tool_calls:
            return state
        
        # Translate tool names to Persian
        tool_names_fa = {
            "create_event_tool": "ایجاد رویداد",
            "update_event_tool": "به‌روزرسانی رویداد",
            "delete_event_tool": "حذف رویداد",
            "create_task_tool": "ایجاد وظیفه",
            "update_task_status_tool": "به‌روزرسانی وضعیت وظیفه"
        }
        
        # Create approval message in Persian
        approval_message = AIMessage(
            content="⚠️ **نیاز به تأیید**\n\n"
        )
        
        # Translate parameter names to Persian
        param_names_fa = {
            "date": "تاریخ",
            "title": "عنوان",
            "attendee": "شرکت‌کننده",
            "attendees": "شرکت‌کنندگان",
            "description": "توضیحات",
            "location": "مکان",
            "due_date": "مهلت",
            "project": "پروژه",
            "status": "وضعیت",
            "attendant": "مسئول",
            "new_status": "وضعیت جدید",
            "event_id": "شناسه رویداد"
        }
        
        # List each pending action for user visibility
        for idx, tool_call in enumerate(tool_calls, 1):
            tool_name_display = tool_names_fa.get(tool_call['name'], tool_call['name'])
            approval_message.content += f"عملیات {idx}: **{tool_name_display}**\n"
            for key, value in tool_call["args"].items():
                param_display = param_names_fa.get(key, key)
                approval_message.content += f"- {param_display}: {value}\n"
            approval_message.content += "\n"
        
        approval_message.content += "**آیا این عملیات‌ها را تأیید می‌کنید؟**\n"
        approval_message.content += "لطفاً با 'بله' تأیید کنید یا با 'نه' لغو کنید.\n"
        approval_message.content += "(Please respond with 'بله' to confirm or 'نه' to cancel)"
        
        return {
            "messages": [approval_message],
            "pending_action": tool_calls
        }
    
    return state


def execute_approved_node(state: AgentState) -> AgentState:
    """Execute the approved action"""
    messages = state["messages"]
    pending_action = state.get("pending_action")
    
    if not pending_action:
        return {"messages": [AIMessage(content="No pending action to execute.")]}
    
    # Normalize to list for batch handling
    pending_actions = pending_action if isinstance(pending_action, list) else [pending_action]
    
    # Check user's response (last message should be user's approval)
    last_user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_message = msg.content.lower().strip()
            break
    
    # Persian and English approval keywords
    approval_keywords = ["yes", "y", "ok", "بله", "آره", "اره", "بلی", "باشه", "باشد", "تایید"]
    rejection_keywords = ["no", "n", "cancel", "نه", "نخیر", "خیر", "لغو", "انصراف"]
    
    # Check if user approved
    is_approved = any(keyword in last_user_message for keyword in approval_keywords) if last_user_message else False
    is_rejected = any(keyword in last_user_message for keyword in rejection_keywords) if last_user_message else False
    
    # If user approved
    if is_approved and not is_rejected:
        # Execute each tool call sequentially
        tool_node = ToolNode(ALL_TOOLS)
        execution_messages = []
        
        for action in pending_actions:
            # Create a mock AI message with the tool call
            mock_message = AIMessage(content="", tool_calls=[action])
            temp_state = {"messages": [mock_message]}
            result = tool_node(temp_state)
            execution_messages.extend(result.get("messages", []))
        
        return {
            "messages": execution_messages,
            "pending_action": None
        }
    else:
        return {
            "messages": [AIMessage(content="❌ عملیات توسط کاربر لغو شد. (Action cancelled by user)")],
            "pending_action": None
        }


def update_memory_node(state: AgentState) -> AgentState:
    """Update conversation memory (keep last 7 interactions)"""
    messages = state["messages"]
    memory = state.get("memory", [])
    
    # Extract last user-assistant pair
    user_msg = None
    assistant_msg = None
    
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and not assistant_msg:
            assistant_msg = msg.content
        elif isinstance(msg, HumanMessage) and not user_msg:
            user_msg = msg.content
        
        if user_msg and assistant_msg:
            break
    
    if user_msg and assistant_msg:
        memory.append({
            "user": user_msg,
            "assistant": assistant_msg
        })
        
        # Keep only last 7
        memory = memory[-7:]
    
    return {"memory": memory}


# ===================== GRAPH CONSTRUCTION =====================

def create_assistant_graph(llm: ChatOpenAI) -> StateGraph:
    """Construct the complete LangGraph workflow"""
    
    # Initialize graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("agent", create_agent_node(llm))
    workflow.add_node("tools", ToolNode(ALL_TOOLS))
    workflow.add_node("check_approval", check_approval_node)
    workflow.add_node("execute_approved", execute_approved_node)
    workflow.add_node("update_memory", update_memory_node)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "check_approval": "check_approval",
            "end": "update_memory"
        }
    )
    
    # Tools always go back to agent
    workflow.add_edge("tools", "agent")
    
    # After approval check, go to execute
    workflow.add_edge("check_approval", END)  # Interrupt here for user input
    
    # After execution, update memory
    workflow.add_edge("execute_approved", "update_memory")
    
    # Memory update ends the flow
    workflow.add_edge("update_memory", END)
    
    return workflow


# ===================== MAIN AGENT CLASS =====================

class IranianManagerAssistant:
    """Main assistant class with memory and checkpointing"""
    
    def __init__(self, openai_api_key: str, model: str = None):
        """
        Initialize the assistant
        
        Args:
            openai_api_key: OpenAI API key
            model: Model name (default: uses DEFAULT_MODEL from config, with dynamic selection)
        """
        from config import DEFAULT_MODEL
        self.llm = ChatOpenAI(
            model=model or DEFAULT_MODEL,
            temperature=0,
            api_key=openai_api_key
        )
        
        # Create graph
        workflow = create_assistant_graph(self.llm)
        
        # Compile with memory saver for checkpointing
        self.memory = MemorySaver()
        self.app = workflow.compile(checkpointer=self.memory)
    
    def chat(self, user_input: str, thread_id: str = "default") -> str:
        """
        Send a message to the assistant
        
        Args:
            user_input: User's message
            thread_id: Conversation thread ID
            
        Returns:
            Assistant's response
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get current state
        current_state = self.app.get_state(config)
        
        # Check if we're in approval mode
        if current_state.values.get("pending_action"):
            # User is responding to approval request - execute the action(s)
            pending_action = current_state.values.get("pending_action")
            
            # Check user's response
            user_response = user_input.lower().strip()
            approval_keywords = ["yes", "y", "ok", "بله", "آره", "اره", "بلی", "باشه", "باشد", "تایید"]
            rejection_keywords = ["no", "n", "cancel", "نه", "نخیر", "خیر", "لغو", "انصراف"]
            
            is_approved = any(keyword in user_response for keyword in approval_keywords)
            is_rejected = any(keyword in user_response for keyword in rejection_keywords)
            
            if is_approved and not is_rejected:
                # Execute the tool(s) directly by calling the tool function(s)
                from langchain_core.messages import AIMessage, ToolMessage
                
                pending_actions = pending_action if isinstance(pending_action, list) else [pending_action]
                execution_results = []
                
                for idx, action in enumerate(pending_actions, 1):
                    tool_name = action.get("name")
                    tool_args = action.get("args", {})
                    tool_call_id = action.get("id")
                    
                    # Get the tool
                    tool_func = None
                    for tool in ALL_TOOLS:
                        if tool.name == tool_name:
                            tool_func = tool
                            break
                    
                    if not tool_func:
                        execution_results.append(f"❌ ابزار {tool_name} یافت نشد.")
                        continue
                    
                    try:
                        # Invoke the tool
                        result = tool_func.invoke(tool_args)
                        execution_results.append(f"نتیجه عملیات {idx}:\n{result}")
                    except Exception as e:
                        execution_results.append(f"❌ خطا در عملیات {idx} ({tool_name}): {str(e)}")
                
                # Combine results and clear thread
                result_content = "✅ عملیات با موفقیت انجام شد!\n\n" + "\n\n".join(execution_results) + "\n\n🔄 (گفتگو پاکسازی شد - آماده دستور بعدی)"
                return f"__CLEAR_THREAD__|{result_content}"
            else:
                # User rejected - clear thread
                cancel_msg = "❌ عملیات توسط کاربر لغو شد. (Action cancelled by user)\n\n🔄 (گفتگو پاکسازی شد)"
                return f"__CLEAR_THREAD__|{cancel_msg}"
        
        # Normal conversation flow
        try:
            result = self.app.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "memory": current_state.values.get("memory", [])
                },
                config
            )
            
            # Return last message
            return result["messages"][-1].content
        except Exception as e:
            # If there's an error, reset the conversation state and return error
            from langchain_core.messages import AIMessage as AI_Msg
            error_msg = f"❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.\nError: {str(e)}"
            self.app.update_state(config, {
                "messages": [AI_Msg(content=error_msg)],
                "pending_action": None,
                "memory": current_state.values.get("memory", [])
            }, as_node="__start__")
            return error_msg
    
    def get_conversation_history(self, thread_id: str = "default") -> list:
        """Get conversation history for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.app.get_state(config)
        return state.values.get("memory", [])


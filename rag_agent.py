"""
RAG Agent for Document Q&A and Summarization
LangGraph workflow with Farsi language support
"""
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
import operator
import logging

from rag_tools import ALL_RAG_TOOLS, initialize_vector_store

logger = logging.getLogger(__name__)


# ===================== STATE DEFINITION =====================

class RAGAgentState(TypedDict):
    """State for the RAG agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_document: str | None  # Currently selected document
    conversation_context: str | None  # Context from previous interactions


# ===================== SYSTEM PROMPT =====================

def get_rag_system_prompt() -> str:
    """Generate system prompt for RAG agent in Farsi"""
    return """شما یک دستیار هوشمند مدیریت اسناد هستید که به فارسی پاسخ می‌دهید.

**قابلیت‌های شما:**

1. **📤 بارگذاری سند (Upload Document)**:
   - پشتیبانی از فرمت‌های: PDF, DOCX, TXT, Excel, PowerPoint, تصاویر
   - اسناد فارسی و انگلیسی
   - ذخیره در پایگاه داده برداری

2. **📋 مدیریت اسناد (Document Management)**:
   - نمایش لیست تمام اسناد (list_documents_tool)
   - حذف سند (delete_document_tool)
   - مشاهده اطلاعات سند (get_document_info_tool)

3. **💬 پرسش و پاسخ (Q&A)**:
   - پرسش درباره محتوای اسناد (query_document_tool)
   - جستجو در یک سند خاص یا همه اسناد
   - پاسخ‌های دقیق بر اساس محتوای سند

4. **📝 خلاصه‌سازی هوشمند (Intelligent Summarization)**:
   - خلاصه حرفه‌ای از اسناد (summarize_document_tool)
   - استخراج تاریخ‌ها و مهلت‌ها
   - استخراج اطلاعات مالی
   - استخراج دستورالعمل‌ها و قوانین
   - شناسایی اطلاعات حساس

**رفتار شما:**

✅ **همیشه به فارسی پاسخ دهید** - زبان اصلی کاربر فارسی است
✅ **واضح و مستقیم باشید** - توضیحات ساده و قابل فهم
✅ **حرفه‌ای و رسمی** - مناسب برای مدیران و کسب‌وکارها
✅ **دقیق و کامل** - اطلاعات جامع ارائه دهید
✅ **راهنمایی کنید** - اگر کاربر نمی‌داند چه کند، راهنمایی کنید

**جریان کار:**

1. اگر کاربر می‌خواهد سند بارگذاری کند:
   - از مسیر فایل بپرسید
   - از upload_document_tool استفاده کنید

2. اگر کاربر می‌خواهد اسناد را ببیند:
   - از list_documents_tool استفاده کنید

3. اگر کاربر سوالی درباره سند دارد:
   - از query_document_tool استفاده کنید
   - پاسخ را به فارسی روان و قابل فهم بازنویسی کنید

4. اگر کاربر می‌خواهد خلاصه سند را ببیند:
   - از document_id بپرسید (یا از list فهرست دریافت کنید)
   - از summarize_document_tool استفاده کنید

5. اگر کاربر می‌خواهد سندی را حذف کند:
   - از document_id بپرسید
   - از delete_document_tool استفاده کنید

**مثال‌های تعامل:**

❓ کاربر: "چه اسنادی دارم؟"
→ از list_documents_tool استفاده کن

❓ کاربر: "این سند درباره چیست؟"
→ از query_document_tool یا summarize_document_tool استفاده کن

❓ کاربر: "تاریخ‌های مهم در سند چیست؟"
→ از summarize_document_tool استفاده کن که تاریخ‌ها را استخراج می‌کند

**یادآوری مهم:**
- همیشه پاسخ‌های ابزارها را به فارسی روان و حرفه‌ای بازنویسی کنید
- اگر اطلاعاتی در سند نیست، صادقانه بگویید
- اگر نیاز به اطلاعات بیشتر دارید، بپرسید

شما دستیار تخصصی مدیریت اسناد هستید. کاربران از شما انتظار دارند که به آن‌ها در درک و استفاده از اسنادشان کمک کنید.
"""


# ===================== GRAPH NODES =====================

def create_rag_agent_node(llm: ChatOpenAI):
    """Create the main RAG agent reasoning node"""
    
    def agent_node(state: RAGAgentState) -> RAGAgentState:
        """Agent decides what to do based on user input"""
        messages = state["messages"]
        
        # Add system prompt
        system_message = SystemMessage(content=get_rag_system_prompt())
        
        # Add context if available
        if state.get("conversation_context"):
            system_message.content += f"\n\n**سیاق گفتگو قبلی:**\n{state['conversation_context']}"
        
        if state.get("current_document"):
            system_message.content += f"\n\n**سند فعلی:** {state['current_document']}"
        
        # Bind tools to LLM
        llm_with_tools = llm.bind_tools(ALL_RAG_TOOLS)
        
        # Invoke LLM
        response = llm_with_tools.invoke([system_message] + list(messages))
        
        return {"messages": [response]}
    
    return agent_node


def should_continue(state: RAGAgentState) -> Literal["tools", "end"]:
    """Determine next step based on agent's response"""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If the agent used tools, execute them
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    
    # Otherwise, end conversation
    return "end"


def process_tool_response(state: RAGAgentState) -> RAGAgentState:
    """
    Process tool responses and format them for better readability
    This node runs after tools to enhance the response quality
    """
    messages = state["messages"]
    
    # Check if last message is a tool response
    if messages and hasattr(messages[-1], "content"):
        last_content = messages[-1].content
        
        # Update conversation context with key information
        context = state.get("conversation_context", "")
        
        # Extract document references from responses
        if "شناسه:" in last_content or "document_id" in last_content:
            context += f"\n{last_content[:200]}"  # Keep first 200 chars as context
        
        return {
            "conversation_context": context[-1000:]  # Keep last 1000 chars
        }
    
    return {}


# ===================== GRAPH CONSTRUCTION =====================

def create_rag_graph(llm: ChatOpenAI) -> StateGraph:
    """Construct the complete RAG agent LangGraph workflow"""
    
    # Initialize graph
    workflow = StateGraph(RAGAgentState)
    
    # Add nodes
    workflow.add_node("agent", create_rag_agent_node(llm))
    workflow.add_node("tools", ToolNode(ALL_RAG_TOOLS))
    workflow.add_node("process_response", process_tool_response)
    
    # Set entry point
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    
    # After tools, process response then go back to agent
    workflow.add_edge("tools", "process_response")
    workflow.add_edge("process_response", "agent")
    
    return workflow


# ===================== MAIN RAG AGENT CLASS =====================

class RAGAgent:
    """
    Main RAG Agent class with document management capabilities
    Supports Farsi and English documents with intelligent Q&A and summarization
    """
    
    def __init__(
        self,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        vector_store_type: str = "chromadb",
        **vector_store_kwargs
    ):
        """
        Initialize the RAG agent
        
        Args:
            openai_api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
            vector_store_type: "chromadb" or "pinecone"
            **vector_store_kwargs: Additional arguments for vector store
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.3,  # Slightly higher for more natural responses
            api_key=openai_api_key
        )
        
        # Initialize vector store
        initialize_vector_store(
            store_type=vector_store_type,
            **vector_store_kwargs
        )
        
        logger.info(f"RAG Agent initialized with {vector_store_type}")
        
        # Create graph
        workflow = create_rag_graph(self.llm)
        
        # Compile with memory saver for checkpointing
        self.memory = MemorySaver()
        self.app = workflow.compile(checkpointer=self.memory)
    
    def chat(self, user_input: str, thread_id: str = "default") -> str:
        """
        Send a message to the RAG agent
        
        Args:
            user_input: User's message
            thread_id: Conversation thread ID
            
        Returns:
            Agent's response
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            # Get current state
            current_state = self.app.get_state(config)
            
            # Invoke agent
            result = self.app.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "current_document": current_state.values.get("current_document"),
                    "conversation_context": current_state.values.get("conversation_context", "")
                },
                config
            )
            
            # Return last message
            last_message = result["messages"][-1]
            
            # If it's an AI message, return content
            if isinstance(last_message, AIMessage):
                return last_message.content
            
            # If it's a tool message, return content with formatting
            return last_message.content
        
        except Exception as e:
            logger.error(f"Error in RAG agent chat: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"❌ خطایی رخ داد: {str(e)}\n\n(An error occurred. Please try again.)"
    
    def reset_conversation(self, thread_id: str = "default"):
        """Reset conversation for a thread"""
        config = {"configurable": {"thread_id": thread_id}}
        try:
            # Update state to clear everything
            self.app.update_state(
                config,
                {
                    "messages": [],
                    "current_document": None,
                    "conversation_context": ""
                },
                as_node="__start__"
            )
            logger.info(f"Conversation reset for thread: {thread_id}")
        except Exception as e:
            logger.error(f"Error resetting conversation: {str(e)}")
    
    def get_conversation_state(self, thread_id: str = "default") -> dict:
        """Get current conversation state"""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.app.get_state(config)
        return {
            "current_document": state.values.get("current_document"),
            "message_count": len(state.values.get("messages", [])),
            "has_context": bool(state.values.get("conversation_context"))
        }

"""
Finance Agent - Main Entry Point
Multi-agent system for Iranian business financial management
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

from finance.database import FinanceDatabase


# ===================== STATE DEFINITION =====================

class FinanceState(TypedDict):
    """State for the finance assistant agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    pending_action: dict | None  # Stores action awaiting approval
    memory: list[dict]  # Conversation history
    current_agent: str | None  # Track which sub-agent is active
    user_id: str  # User identifier


# ===================== FINANCE AGENT CLASS =====================

class FinanceAgent:
    """
    Main Finance Assistant with internal multi-agent orchestration
    
    Features:
    - Document Processing (OCR, receipts, invoices)
    - Transaction Management (CRUD, categorization)
    - Cash Management (balance, currency, projections)
    - Reporting (P&L, exports, analysis)
    - Conversational Interface (dialogue, clarifications)
    """
    
    def __init__(self, openai_api_key: str, model: str = "gpt-4o", db_path: str = "finance.db"):
        """
        Initialize the Finance Agent
        
        Args:
            openai_api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            db_path: Path to finance database
        """
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=openai_api_key
        )
        
        # Initialize database
        self.db = FinanceDatabase(db_path)
        
        # Initialize sub-agents
        from finance.agents.document_agent import DocumentAgent
        from finance.agents.transaction_agent import TransactionAgent
        from finance.agents.cash_agent import CashAgent
        from finance.agents.reporting_agent import ReportingAgent
        from finance.agents.conversation_agent import ConversationAgent
        
        self.document_agent = DocumentAgent(self.llm, self.db)
        self.transaction_agent = TransactionAgent(self.llm, self.db)
        self.cash_agent = CashAgent(self.llm, self.db)
        self.reporting_agent = ReportingAgent(self.llm, self.db)
        self.conversation_agent = ConversationAgent(self.llm)
        
        # Create orchestrator graph
        self.memory = MemorySaver()
        self.app = self._build_graph()
        
        print("✅ Finance Agent initialized successfully")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for finance orchestration"""
        workflow = StateGraph(FinanceState)
        
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
        """Generate system prompt for finance orchestrator"""
        tehran_tz = pytz.timezone('Asia/Tehran')
        current_time = jdatetime.datetime.now(tz=tehran_tz)
        today = current_time.date()
        
        return f"""شما مدیر مالی هوشمند برای کسب‌وکارهای ایرانی هستید.
        
**زمان فعلی**: {current_time.strftime('%Y-%m-%d %H:%M:%S')} تهران (امروز: {today.strftime('%Y-%m-%d')})

**قابلیت‌های شما**:

1. **پردازش اسناد**: استخراج داده از رسید، فاکتور، صورتحساب بانکی (OCR)
2. **مدیریت تراکنش‌ها**: ثبت، جستجو، ویرایش، دسته‌بندی خودکار درآمد و هزینه
3. **مدیریت نقدینگی**: پیگیری موجودی، تبدیل ارز، پیش‌بینی جریان نقدی
4. **گزارش‌گیری**: صورت سود و زیان، گزارش هزینه‌ها، گزارش مالیاتی، خروجی PDF/Excel
5. **گفتگو و راهنمایی**: پاسخ به سوالات، توضیح مفاهیم مالی

**دسته‌بندی‌های مالی**:
- درآمد: فروش محصولات، ارائه خدمات، سایر درآمدها
- هزینه: حقوق، بازاریابی، اجاره، لجستیک، خدمات حرفه‌ای

**زمینه ایرانی**:
- واحد پول: ریال و تومان (1 تومان = 10 ریال)
- تقویم: جلالی (شمسی)
- مالیات بر ارزش افزوده: 9%
- نرخ ارز: رسمی، نیما، بازار آزاد

**رفتار شما**:
- همیشه به فارسی پاسخ دهید
- واضح و مفید باشید
- پیشنهادات فعالانه ارائه دهید
- امنیت و دقت داده‌ها را رعایت کنید
- **مهم**: هرگز داده‌های مالی جعلی یا نمونه تولید نکنید
- برای سوالات مربوط به موجودی، نرخ ارز، و گزارش‌های مالی، همیشه از توابع و ابزارهای موجود استفاده کنید
- اگر داده‌ای در پایگاه داده وجود ندارد، صادقانه به کاربر بگویید که داده‌ای ثبت نشده است
"""
    
    def _orchestrator_node(self, state: FinanceState) -> FinanceState:
        """Main orchestrator node - routes to appropriate sub-agent"""
        messages = state["messages"]
        user_id = state.get("user_id", "default")
        
        # Get last user message
        last_message = messages[-1].content if messages else ""
        last_message_lower = last_message.lower()
        
        # Route to appropriate agent based on keywords
        response_content = None
        
        # Balance queries
        balance_keywords = ["موجودی", "balance", "موجود", "چقدر پول", "چقدر موجودی"]
        if any(keyword in last_message_lower for keyword in balance_keywords):
            balance_result = self.cash_agent.get_balance(user_id)
            if balance_result.get("success"):
                if balance_result.get("accounts"):
                    response_content = balance_result.get("message", "💰 موجودی شما: 0 ریال")
                    response_content += "\n\n📊 **حساب‌ها:**\n"
                    for account in balance_result["accounts"]:
                        response_content += f"- {account['name']}: {account['current_balance']:,} {account['currency']}\n"
                else:
                    response_content = "💰 **موجودی شما:**\n\n"
                    response_content += "هنوز حسابی ثبت نشده است. برای شروع، می‌توانید:\n"
                    response_content += "1. یک حساب جدید ایجاد کنید\n"
                    response_content += "2. یک تراکنش ثبت کنید (که به صورت خودکار حساب ایجاد می‌کند)\n"
                    response_content += "3. یک رسید یا فاکتور بارگذاری کنید"
            else:
                response_content = f"❌ خطا در دریافت موجودی: {balance_result.get('error', 'خطای نامشخص')}"
        
        # Account creation queries - check for account creation intent
        account_creation_indicators = [
            ("حساب", "ایجاد"), ("حساب", "بساز"), ("حساب", "اضافه"), 
            ("حساب", "جدید"), ("create", "account"), ("add", "account"),
            "ایجاد حساب", "حساب بساز", "حساب اضافه", "حساب جدید"
        ]
        is_account_creation = False
        if not response_content:
            # Check for exact phrases
            for phrase in ["ایجاد حساب", "حساب بساز", "حساب اضافه", "حساب جدید", "create account", "add account"]:
                if phrase in last_message_lower:
                    is_account_creation = True
                    break
            # Check for word pairs (more flexible)
            if not is_account_creation:
                for word1, word2 in [("حساب", "ایجاد"), ("حساب", "بساز"), ("حساب", "اضافه"), ("create", "account"), ("add", "account")]:
                    if word1 in last_message_lower and word2 in last_message_lower:
                        is_account_creation = True
                        break
        
        if is_account_creation:
            # Use LLM to extract account information in structured format
            try:
                extract_prompt = f"""از پیام کاربر زیر، اطلاعات حساب را استخراج کن و به صورت JSON برگردان:
{last_message}

فقط JSON برگردان با این فرمت:
{{
  "name": "نام حساب",
  "type": "bank یا cash یا credit_card",
  "initial_balance": عدد,
  "currency": "IRR",
  "is_toman": true/false
}}

اگر اطلاعات کامل نیست، null برگردان."""

                system_prompt = """شما باید اطلاعات حساب را از پیام کاربر استخراج کنید.
- نوع حساب: bank (بانکی)، cash (نقدی)، credit_card (کارت اعتباری)
- اگر "تومان" یا "toman" ذکر شده، is_toman را true کن
- فقط JSON برگردان، هیچ متن اضافی نه"""

                llm_response = self.llm.invoke([
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=extract_prompt)
                ])
                
                # Try to parse JSON from response
                import json
                import re
                response_text = llm_response.content.strip()
                
                # Extract JSON from response
                json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        account_data = json.loads(json_match.group())
                        
                        if account_data.get("name") and account_data.get("type"):
                            # Determine account type
                            account_type = account_data["type"].lower()
                            if "بانک" in account_type or account_type == "bank":
                                account_type = "bank"
                            elif "نقد" in account_type or account_type == "cash":
                                account_type = "cash"
                            elif "کارت" in account_type or "credit" in account_type:
                                account_type = "credit_card"
                            else:
                                account_type = "bank"  # default
                            
                            # Get balance
                            balance = float(account_data.get("initial_balance", 0))
                            if account_data.get("is_toman") or "تومان" in last_message_lower:
                                balance = balance * 10  # Convert toman to rial
                            
                            # Create account
                            result = self.cash_agent.create_account_interactive(
                                user_id=user_id,
                                name=account_data["name"],
                                account_type=account_type,
                                currency=account_data.get("currency", "IRR"),
                                initial_balance=balance
                            )
                            
                            if result.get("success"):
                                response_content = result.get("message", "✅ حساب با موفقیت ایجاد شد")
                            else:
                                response_content = f"❌ خطا: {result.get('error', 'خطای نامشخص')}"
                        else:
                            # Missing information, ask user
                            response_content = "لطفاً اطلاعات کامل حساب را مشخص کنید:\n"
                            response_content += "- نام حساب\n"
                            response_content += "- نوع حساب (بانکی، نقدی، یا کارت اعتباری)\n"
                            response_content += "- موجودی اولیه\n\n"
                            response_content += "مثال: \"حساب بانکی با نام حساب ملی و موجودی ۱۰ میلیون تومان ایجاد کن\""
                    except json.JSONDecodeError:
                        # Couldn't parse JSON, use LLM response as fallback
                        response_content = llm_response.content
                else:
                    # No JSON found, ask for clarification
                    response_content = "لطفاً اطلاعات حساب را به صورت کامل ارائه دهید:\n"
                    response_content += "مثال: \"حساب بانکی با نام حساب ملی و موجودی ۱۰ میلیون تومان ایجاد کن\""
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                response_content = f"❌ خطا در پردازش درخواست: {str(e)}\n\n"
                response_content += "لطفاً اطلاعات را به این صورت ارائه دهید:\n"
                response_content += "\"حساب [نوع] با نام [نام] و موجودی [مبلغ] [واحد] ایجاد کن\""
        
        # Financial report queries
        report_keywords = ["گزارش", "report", "سود و زیان", "profit", "loss", "expense report", "گزارش هزینه", "گزارش مالی", "گزارش درآمد", "گزارش نقدینگی", "گزارش فروشنده", "گزارش ماهانه", "گزارش مالیاتی"]
        if not response_content and any(keyword in last_message_lower for keyword in report_keywords):
            try:
                # Try to detect report type from user message
                detected_type = self.reporting_agent.detect_report_type(last_message)
                
                if detected_type:
                    # User specified a report type, generate it
                    import jdatetime
                    from datetime import datetime as dt
                    today = jdatetime.date.today()
                    
                    # Check if dates were provided in state (from frontend)
                    provided_date_from = state.get("report_date_from")
                    provided_date_to = state.get("report_date_to")
                    
                    # Prepare parameters based on report type
                    params = {}
                    
                    if detected_type == "monthly":
                        # Monthly report uses year/month instead of date range
                        # Try to extract year/month from message, or use current
                        import re
                        year_match = re.search(r'(\d{4})', last_message)
                        month_match = re.search(r'\b(فروردین|اردیبهشت|خرداد|تیر|مرداد|شهریور|مهر|آبان|آذر|دی|بهمن|اسفند)\b', last_message_lower)
                        month_num_match = re.search(r'\b(1[0-2]|[1-9])\b', last_message)
                        
                        year = int(year_match.group(1)) if year_match else today.year
                        
                        if month_match:
                            month_names = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                                          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
                            month = month_names.index(month_match.group(1)) + 1
                        elif month_num_match:
                            month = int(month_num_match.group(1))
                        else:
                            month = today.month
                        
                        params = {"year": year, "month": month}
                    else:
                        # Other reports use date range
                        if provided_date_from and provided_date_to:
                            # Dates are already in Jalali format (YYYY-MM-DD)
                            # Validate and use directly
                            try:
                                # Validate Jalali date format
                                from_parts = provided_date_from.split('-')
                                to_parts = provided_date_to.split('-')
                                
                                if len(from_parts) == 3 and len(to_parts) == 3:
                                    # Validate using jdatetime
                                    jalali_from = jdatetime.date(int(from_parts[0]), int(from_parts[1]), int(from_parts[2]))
                                    jalali_to = jdatetime.date(int(to_parts[0]), int(to_parts[1]), int(to_parts[2]))
                                    
                                    date_from = provided_date_from
                                    date_to = provided_date_to
                                else:
                                    raise ValueError("Invalid date format")
                            except Exception as e:
                                print(f"[WARNING] Jalali date validation error: {e}, using default dates")
                                # Fallback to current month
                                date_from = f"{today.year}-{today.month:02d}-01"
                                date_to = f"{today.year}-{today.month:02d}-{today.day:02d}"
                        else:
                            # Default to current month
                            date_from = f"{today.year}-{today.month:02d}-01"
                            date_to = f"{today.year}-{today.month:02d}-{today.day:02d}"
                        
                        params = {
                            "date_from": date_from,
                            "date_to": date_to
                        }
                    
                    # Generate report using reporting agent
                    result = self.reporting_agent.generate_report(
                        user_id=user_id,
                        report_type=detected_type,
                        params=params
                    )
                    
                    if result.get("success"):
                        response_content = result.get("message", "✅ گزارش با موفقیت تولید شد")
                    else:
                        response_content = result.get("message", f"❌ خطا در تولید گزارش: {result.get('error', 'خطای نامشخص')}")
                else:
                    # User asked for a report but didn't specify type - show available options
                    report_list = self.reporting_agent.list_available_reports()
                    # Return structured data for frontend to render as buttons
                    response_content = "📊 **گزارش‌های مالی موجود:**\n\nلطفاً نوع گزارش مورد نظر خود را انتخاب کنید:"
                    # Store report data in state for frontend access
                    state["pending_action"] = {
                        "type": "report_selection",
                        "reports": report_list.get("reports", {})
                    }
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                response_content = f"❌ خطا در تولید گزارش: {str(e)}"
        
        # Exchange rate queries
        exchange_keywords = ["نرخ ارز", "exchange", "دلار", "یورو", "نرخ"]
        if not response_content and any(keyword in last_message_lower for keyword in exchange_keywords):
            rate_result = self.cash_agent.fetch_exchange_rates_interactive("USD/IRR")
            if rate_result.get("success"):
                rates = rate_result.get("rates", {})
                response_content = "💱 **نرخ ارز فعلی:**\n\n"
                for currency, rate_info in rates.items():
                    if isinstance(rate_info, dict):
                        response_content += f"**{currency}**:\n"
                        if "official" in rate_info:
                            response_content += f"  - رسمی: {rate_info['official']:,} ریال\n"
                        if "nima" in rate_info:
                            response_content += f"  - نیما: {rate_info['nima']:,} ریال\n"
                        if "parallel" in rate_info:
                            response_content += f"  - بازار آزاد: {rate_info['parallel']:,} ریال\n"
            else:
                response_content = f"❌ خطا در دریافت نرخ ارز: {rate_result.get('error', 'خطای نامشخص')}"
        
        # If no specific routing, use LLM
        if not response_content:
            # Get system prompt
            system_message = SystemMessage(content=self._get_system_prompt())
            
            # Add memory context if available
            if state.get("memory"):
                memory_context = "\n\n**گفتگوهای اخیر**:\n"
                for i, interaction in enumerate(state["memory"][-5:], 1):
                    memory_context += f"{i}. کاربر: {interaction.get('user', 'N/A')}\n   دستیار: {interaction.get('assistant', 'N/A')}\n"
                system_message.content += memory_context
            
            # Invoke LLM
            response = self.llm.invoke([system_message] + list(messages))
            response_content = response.content
        else:
            # Create AI message with the routed response
            response = AIMessage(content=response_content)
        
        return {"messages": [response]}
    
    def _response_node(self, state: FinanceState) -> FinanceState:
        """Final response node"""
        return state
    
    def chat(self, user_input: str, thread_id: str = "default", user_id: str = "default", date_from: str = None, date_to: str = None) -> str:
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
            # Store date parameters in state for report generation
            invoke_state = {
                "messages": [HumanMessage(content=user_input)],
                "memory": current_state.values.get("memory", []) if current_state.values else [],
                "user_id": user_id,
                "current_agent": None,
                "pending_action": None
            }
            
            # Add date parameters if provided
            if date_from and date_to:
                invoke_state["report_date_from"] = date_from
                invoke_state["report_date_to"] = date_to
            
            result = self.app.invoke(invoke_state, config)
            
            # Return last message
            return result["messages"][-1].content
        except Exception as e:
            error_msg = f"❌ خطایی رخ داد: {str(e)}\nلطفاً دوباره تلاش کنید."
            return error_msg
    
    def upload_document(self, file_path: str, user_id: str = "default", doc_type: str = "auto") -> dict:
        """
        Process uploaded receipt/invoice
        
        Args:
            file_path: Path to uploaded file
            user_id: User identifier
            doc_type: Type of document (receipt, invoice, statement, auto)
            
        Returns:
            Extracted data dictionary
        """
        return self.document_agent.process_document(file_path, user_id, doc_type)
    
    def get_transactions(self, filters: dict, user_id: str = "default") -> list:
        """
        Get transaction list with filters
        
        Args:
            filters: Filter criteria (date_from, date_to, category, etc.)
            user_id: User identifier
            
        Returns:
            List of transactions
        """
        result = self.transaction_agent.search_transactions_interactive(user_id, filters)
        return result.get("transactions", [])
    
    def create_transaction(self, user_id: str = "default", **kwargs) -> dict:
        """Create a new transaction"""
        return self.transaction_agent.create_transaction_interactive(user_id, **kwargs)
    
    def get_categories(self, user_id: str = "default") -> list:
        """Get available categories"""
        return self.transaction_agent.get_categories(user_id)
    
    def get_balance(self, user_id: str = "default") -> dict:
        """
        Get current balance summary
        
        Args:
            user_id: User identifier
            
        Returns:
            Balance information
        """
        return self.cash_agent.get_balance(user_id)
    
    def create_account(
        self,
        user_id: str,
        name: str,
        account_type: str,
        currency: str = "IRR",
        initial_balance: float = 0.0
    ) -> dict:
        """
        Create a new account
        
        Args:
            user_id: User identifier
            name: Account name
            account_type: Type (bank, cash, credit_card)
            currency: Currency code
            initial_balance: Initial balance
            
        Returns:
            Creation result
        """
        return self.cash_agent.create_account_interactive(
            user_id=user_id,
            name=name,
            account_type=account_type,
            currency=currency,
            initial_balance=initial_balance
        )
    
    def list_accounts(self, user_id: str = "default") -> dict:
        """
        List all accounts for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of accounts
        """
        return self.cash_agent.list_accounts_interactive(user_id)
    
    def generate_report(self, report_type: str, params: dict, user_id: str = "default") -> dict:
        """
        Generate financial report
        
        Args:
            report_type: Type of report (pl, cash_flow, expense, tax)
            params: Report parameters
            user_id: User identifier
            
        Returns:
            Report data and export URL
        """
        # TODO: Implement in Phase 5
        return {
            "success": False,
            "message": "قابلیت گزارش‌گیری در حال توسعه است"
        }
    
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
    
    def init_user(self, user_id: str, name: str = "کاربر", email: str = None):
        """
        Initialize a new user with default categories
        
        Args:
            user_id: User identifier
            name: User name
            email: User email (optional)
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO finance_users (id, name, email)
                VALUES (?, ?, ?)
            """, (user_id, name, email))
        
        # Initialize default categories
        self.db.init_default_categories(user_id)
        print(f"✅ User {user_id} initialized")


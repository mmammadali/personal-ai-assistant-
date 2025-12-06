"""
Reporting Agent
Generates financial reports and handles exports
Uses hybrid approach: data-driven accuracy + AI-powered insights
"""
from langchain_openai import ChatOpenAI
from finance.database import FinanceDatabase
from finance.tools.report_generators import (
    generate_pl_statement,
    generate_expense_report,
    generate_income_report,
    generate_cash_flow_report,
    generate_vendor_analysis_report,
    generate_monthly_summary_report,
    generate_tax_report,
    REPORT_TOOLS
)
from finance.tools.ai_report_analyzer import analyze_report_with_ai


class ReportingAgent:
    """Reporting and analysis specialist"""
    
    # Available report types
    AVAILABLE_REPORTS = {
        "pl": {
            "name": "صورت سود و زیان",
            "name_en": "Profit & Loss Statement",
            "description": "گزارش کامل درآمدها، هزینه‌ها و سود خالص",
            "keywords": ["سود و زیان", "profit", "loss", "p&l", "pl"]
        },
        "expense": {
            "name": "گزارش هزینه‌ها",
            "name_en": "Expense Report",
            "description": "تحلیل هزینه‌ها بر اساس دسته‌بندی و فروشندگان",
            "keywords": ["هزینه", "expense", "cost"]
        },
        "income": {
            "name": "گزارش درآمد",
            "name_en": "Income Report",
            "description": "تحلیل درآمدها بر اساس دسته‌بندی و منابع درآمد",
            "keywords": ["درآمد", "income", "revenue", "فروش"]
        },
        "cash_flow": {
            "name": "گزارش جریان نقدی",
            "name_en": "Cash Flow Report",
            "description": "تحلیل ورودی و خروجی نقدی و موجودی حساب‌ها",
            "keywords": ["جریان نقد", "cash flow", "نقدینگی", "cashflow"]
        },
        "vendor": {
            "name": "گزارش تحلیل فروشندگان",
            "name_en": "Vendor Analysis Report",
            "description": "تحلیل هزینه‌ها و درآمدها بر اساس فروشندگان و مشتریان",
            "keywords": ["فروشنده", "vendor", "تامین کننده", "مشتری", "customer"]
        },
        "monthly": {
            "name": "گزارش خلاصه ماهانه",
            "name_en": "Monthly Summary Report",
            "description": "خلاصه کامل فعالیت‌های مالی ماهانه",
            "keywords": ["خلاصه ماهانه", "monthly summary", "گزارش ماه", "monthly"]
        },
        "tax": {
            "name": "گزارش مالیاتی",
            "name_en": "Tax Report",
            "description": "محاسبات مالیات بر ارزش افزوده و سود مشمول مالیات",
            "keywords": ["مالیات", "tax", "ارزش افزوده", "vat", "مالیاتی"]
        }
    }
    
    def __init__(self, llm: ChatOpenAI, db: FinanceDatabase):
        self.llm = llm
        self.db = db
        self.tools = REPORT_TOOLS
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    def list_available_reports(self) -> dict:
        """
        Get list of available report types
        
        Returns:
            Dictionary with available reports and their descriptions
        """
        return {
            "success": True,
            "reports": self.AVAILABLE_REPORTS,
            "message": self._format_report_list()
        }
    
    def _format_report_list(self) -> str:
        """Format available reports as a user-friendly message"""
        message = "📊 **گزارش‌های مالی موجود:**\n\n"
        
        report_num = 1
        for report_id, report_info in self.AVAILABLE_REPORTS.items():
            message += f"**{report_num}. {report_info['name']}** ({report_info['name_en']}) - {report_info['description']}\n"
            report_num += 1
        
        message += "\nلطفاً نوع گزارش مورد نظر خود را با نام یا شماره آن انتخاب کنید."
        
        return message
    
    def detect_report_type(self, user_message: str) -> str | None:
        """
        Detect report type from user message
        
        Args:
            user_message: User's message
            
        Returns:
            Report type ID or None if not detected
        """
        message_lower = user_message.lower()
        
        # Check for numeric selection (1-7, etc.)
        import re
        number_match = re.search(r'\b([1-7])\b', message_lower)
        if number_match:
            report_num = int(number_match.group(1))
            report_ids = list(self.AVAILABLE_REPORTS.keys())
            if 1 <= report_num <= len(report_ids):
                return report_ids[report_num - 1]
        
        # Check for report names FIRST (more specific than keywords)
        # This prevents false matches (e.g., "فروش" in "گزارش تحلیل فروشندگان" matching income report)
        for report_id, report_info in self.AVAILABLE_REPORTS.items():
            if report_info['name'] in user_message or report_info['name_en'].lower() in message_lower:
                return report_id
        
        # Check for report ID directly (e.g., "vendor", "income", etc.)
        for report_id in self.AVAILABLE_REPORTS.keys():
            if report_id in message_lower:
                return report_id
        
        # Check for keywords (less specific, so check last)
        for report_id, report_info in self.AVAILABLE_REPORTS.items():
            for keyword in report_info['keywords']:
                if keyword in message_lower:
                    return report_id
        
        return None
    
    def generate_report(self, user_id: str, report_type: str, params: dict, use_ai_analysis: bool = True) -> dict:
        """
        Generate financial report using hybrid approach:
        1. Query database for accurate data
        2. Use AI to generate natural language insights
        
        Args:
            user_id: User identifier
            report_type: Type of report (pl, expense, income, cash_flow, vendor, monthly, tax)
            params: Report parameters (date_from, date_to, year, month, etc.)
            use_ai_analysis: Whether to use AI for natural language insights (default: True)
            
        Returns:
            Report data with AI-generated insights
        """
        try:
            # Step 1: Get structured data from database (data-driven, accurate)
            raw_data = None
            period = {}
            
            if report_type == "pl" or report_type == "profit_loss":
                raw_data = generate_pl_statement.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to")
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            elif report_type == "expense":
                raw_data = generate_expense_report.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to"),
                    "top_n": params.get("top_n", 10)
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            elif report_type == "income":
                raw_data = generate_income_report.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to"),
                    "top_n": params.get("top_n", 10)
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            elif report_type == "cash_flow":
                raw_data = generate_cash_flow_report.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to")
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            elif report_type == "vendor":
                raw_data = generate_vendor_analysis_report.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to"),
                    "top_n": params.get("top_n", 15)
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            elif report_type == "monthly":
                raw_data = generate_monthly_summary_report.invoke({
                    "user_id": user_id,
                    "year": params.get("year"),
                    "month": params.get("month")
                })
                # Monthly report already includes period in its response
                period = raw_data.get("period", {
                    "from": f"{params.get('year')}-{params.get('month'):02d}-01", 
                    "to": f"{params.get('year')}-{params.get('month'):02d}-31"
                })
            
            elif report_type == "tax":
                raw_data = generate_tax_report.invoke({
                    "user_id": user_id,
                    "date_from": params.get("date_from"),
                    "date_to": params.get("date_to")
                })
                period = {"from": params.get("date_from"), "to": params.get("date_to")}
            
            else:
                return {
                    "success": False,
                    "message": f"نوع گزارش '{report_type}' پشتیبانی نمی‌شود"
                }
            
            # Check if data retrieval was successful
            if not raw_data.get("success"):
                return raw_data
            
            # Step 2: Use AI to generate natural language insights (if enabled)
            if use_ai_analysis:
                try:
                    ai_enhanced_message = analyze_report_with_ai(
                        llm=self.llm,
                        report_type=report_type,
                        report_data=raw_data,
                        period=period
                    )
                    
                    # Return enhanced report with AI insights
                    return {
                        "success": True,
                        "report_type": raw_data.get("report_type"),
                        "period": raw_data.get("period", period),
                        "data": raw_data,  # Keep original structured data
                        "message": ai_enhanced_message,  # AI-generated natural language report
                        "ai_enhanced": True
                    }
                except Exception as ai_error:
                    # If AI analysis fails, fall back to data-only report
                    print(f"[WARNING] AI analysis failed: {ai_error}. Using data-only report.")
                    return {
                        "success": True,
                        "report_type": raw_data.get("report_type"),
                        "period": raw_data.get("period", period),
                        "data": raw_data,
                        "message": raw_data.get("message", "گزارش تولید شد"),
                        "ai_enhanced": False,
                        "ai_error": str(ai_error)
                    }
            else:
                # Return data-only report (original behavior)
                return raw_data
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": f"خطا در تولید گزارش: {str(e)}"
            }


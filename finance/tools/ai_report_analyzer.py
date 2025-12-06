"""
AI-Powered Report Analysis
Takes structured financial data and generates natural language insights
"""
from typing import Dict, Any
from langchain_openai import ChatOpenAI
import json


def analyze_report_with_ai(
    llm: ChatOpenAI,
    report_type: str,
    report_data: Dict[str, Any],
    period: Dict[str, str]
) -> str:
    """
    Use AI to generate natural language insights from structured report data
    
    Args:
        llm: Language model instance
        report_type: Type of report (pl, expense, income, vendor, etc.)
        report_data: Structured data from database queries
        period: Period information (from, to)
        
    Returns:
        Natural language report with insights
    """
    
    # Format data for AI analysis
    data_summary = _format_data_for_ai(report_type, report_data, period)
    
    # Create prompt based on report type
    if report_type == "pl":
        prompt = _create_pl_analysis_prompt(data_summary, period)
    elif report_type == "expense":
        prompt = _create_expense_analysis_prompt(data_summary, period)
    elif report_type == "income":
        prompt = _create_income_analysis_prompt(data_summary, period)
    elif report_type == "vendor":
        prompt = _create_vendor_analysis_prompt(data_summary, period)
    elif report_type == "cash_flow":
        prompt = _create_cashflow_analysis_prompt(data_summary, period)
    elif report_type == "monthly":
        prompt = _create_monthly_analysis_prompt(data_summary, period)
    elif report_type == "tax":
        prompt = _create_tax_analysis_prompt(data_summary, period)
    else:
        prompt = _create_generic_analysis_prompt(data_summary, period)
    
    # Get AI analysis
    try:
        response = llm.invoke(prompt)
        ai_analysis = response.content if hasattr(response, 'content') else str(response)
        
        # Combine data summary with AI insights
        final_report = _combine_data_and_ai_insights(data_summary, ai_analysis, report_type)
        return final_report
    except Exception as e:
        # Fallback to data-only report if AI fails
        return _create_fallback_report(data_summary, report_type, period)


def _format_data_for_ai(report_type: str, report_data: Dict[str, Any], period: Dict[str, str]) -> str:
    """Format structured data into readable text for AI"""
    
    if report_type == "pl":
        summary = report_data.get("summary", {})
        revenue = report_data.get("revenue_breakdown", [])
        expenses = report_data.get("expense_breakdown", [])
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Total Revenue**: {summary.get('total_revenue', 0):,} ریال ({summary.get('total_revenue', 0)/10:,} تومان)
**Total Expenses**: {summary.get('total_expense', 0):,} ریال ({summary.get('total_expense', 0)/10:,} تومان)
**Net Profit**: {summary.get('net_profit', 0):,} ریال ({summary.get('net_profit', 0)/10:,} تومان)
**Profit Margin**: {summary.get('profit_margin_pct', 0):.1f}%

**Revenue by Category**:
"""
        for item in revenue[:10]:
            data_text += f"- {item['category']}: {item['amount']:,} ریال\n"
        
        data_text += "\n**Expenses by Category**:\n"
        for item in expenses[:10]:
            data_text += f"- {item['category']}: {item['amount']:,} ریال\n"
    
    elif report_type == "expense":
        summary = report_data.get("summary", {})
        categories = report_data.get("top_categories", [])
        vendors = report_data.get("top_vendors", [])
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Total Expenses**: {summary.get('total_expense', 0):,} ریال ({summary.get('total_expense', 0)/10:,} تومان)
**Transaction Count**: {summary.get('transaction_count', 0)}
**Average Transaction**: {summary.get('avg_transaction', 0):,} ریال

**Top Expense Categories**:
"""
        for item in categories[:10]:
            pct = (item['total'] / summary.get('total_expense', 1) * 100) if summary.get('total_expense', 0) > 0 else 0
            data_text += f"- {item['category']}: {item['total']:,} ریال ({pct:.1f}%) - {item['count']} transactions\n"
        
        if vendors:
            data_text += "\n**Top Vendors by Expense**:\n"
            for item in vendors[:10]:
                data_text += f"- {item['vendor']}: {item['total']:,} ریال - {item['count']} transactions\n"
    
    elif report_type == "income":
        summary = report_data.get("summary", {})
        categories = report_data.get("top_categories", [])
        sources = report_data.get("top_sources", [])
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Total Income**: {summary.get('total_income', 0):,} ریال ({summary.get('total_income', 0)/10:,} تومان)
**Transaction Count**: {summary.get('transaction_count', 0)}
**Average Transaction**: {summary.get('avg_transaction', 0):,} ریال

**Top Income Categories**:
"""
        for item in categories[:10]:
            pct = (item['total'] / summary.get('total_income', 1) * 100) if summary.get('total_income', 0) > 0 else 0
            data_text += f"- {item['category']}: {item['total']:,} ریال ({pct:.1f}%) - {item['count']} transactions\n"
        
        if sources:
            data_text += "\n**Top Income Sources**:\n"
            for item in sources[:10]:
                data_text += f"- {item['vendor']}: {item['total']:,} ریال - {item['count']} transactions\n"
    
    elif report_type == "vendor":
        expense_vendors = report_data.get("expense_vendors", [])
        income_vendors = report_data.get("income_vendors", [])
        total_expense = report_data.get("total_expense", 0)
        total_income = report_data.get("total_income", 0)
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Total Expenses from Vendors**: {total_expense:,} ریال ({total_expense/10:,} تومان)
**Total Income from Customers**: {total_income:,} ریال ({total_income/10:,} تومان)

**Top Vendors (Expenses)**:
"""
        for item in expense_vendors[:10]:
            pct = (item['total_expense'] / total_expense * 100) if total_expense > 0 else 0
            data_text += f"- {item['vendor']}: {item['total_expense']:,} ریال ({pct:.1f}%) - {item['expense_count']} transactions\n"
        
        data_text += "\n**Top Customers/Income Sources**:\n"
        for item in income_vendors[:10]:
            pct = (item['total_income'] / total_income * 100) if total_income > 0 else 0
            data_text += f"- {item['vendor']}: {item['total_income']:,} ریال ({pct:.1f}%) - {item['income_count']} transactions\n"
    
    elif report_type == "cash_flow":
        summary = report_data.get("summary", {})
        accounts = report_data.get("accounts", [])
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Cash Inflow**: {summary.get('total_inflow', 0):,} ریال ({summary.get('total_inflow', 0)/10:,} تومان)
**Cash Outflow**: {summary.get('total_outflow', 0):,} ریال ({summary.get('total_outflow', 0)/10:,} تومان)
**Net Cash Flow**: {summary.get('net_cash_flow', 0):,} ریال ({summary.get('net_cash_flow', 0)/10:,} تومان)

**Account Balances**:
"""
        for account in accounts:
            data_text += f"- {account['name']}: {account['current_balance']:,} {account['currency']}\n"
    
    elif report_type == "monthly":
        period_info = report_data.get("period", {})
        summary = report_data.get("summary", {})
        categories = report_data.get("top_expense_categories", [])
        accounts = report_data.get("accounts", [])
        
        month_name = period_info.get("month_name", f"ماه {period_info.get('month', '')}")
        year = period_info.get("year", "")
        
        data_text = f"""
**Month**: {month_name} {year}

**Total Income**: {summary.get('total_income', 0):,} ریال ({summary.get('total_income', 0)/10:,} تومان)
**Total Expenses**: {summary.get('total_expense', 0):,} ریال ({summary.get('total_expense', 0)/10:,} تومان)
**Net Profit**: {summary.get('net_profit', 0):,} ریال ({summary.get('net_profit', 0)/10:,} تومان)
**Profit Margin**: {summary.get('profit_margin_pct', 0):.1f}%

**Top Expense Categories**:
"""
        for item in categories[:10]:
            data_text += f"- {item.get('category', 'سایر')}: {item.get('total', 0):,} ریال\n"
        
        if accounts:
            data_text += "\n**Account Balances**:\n"
            for account in accounts:
                data_text += f"- {account['name']}: {account['current_balance']:,} {account['currency']}\n"
    
    elif report_type == "tax":
        summary = report_data.get("summary", {})
        
        data_text = f"""
**Period**: {period.get('from')} to {period.get('to')}

**Total Revenue**: {summary.get('total_revenue', 0):,} ریال ({summary.get('total_revenue', 0)/10:,} تومان)
**Total Expenses**: {summary.get('total_expenses', 0):,} ریال ({summary.get('total_expenses', 0)/10:,} تومان)
**Taxable Profit**: {summary.get('taxable_profit', 0):,} ریال ({summary.get('taxable_profit', 0)/10:,} تومان)
**VAT Collected**: {summary.get('vat_collected', 0):,} ریال ({summary.get('vat_collected', 0)/10:,} تومان)
**VAT Paid**: {summary.get('vat_paid', 0):,} ریال ({summary.get('vat_paid', 0)/10:,} تومان)
**Net VAT**: {summary.get('net_vat', 0):,} ریال ({summary.get('net_vat', 0)/10:,} تومان)
"""
    
    else:
        # Generic format
        data_text = json.dumps(report_data, indent=2, ensure_ascii=False)
    
    return data_text


def _create_pl_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following Profit & Loss statement data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Provide insights about profitability, trends, and recommendations
4. Highlight key findings and what they mean for the business
5. Be specific about percentages and amounts
6. Format with clear sections and emojis for readability

**Financial Data**:
{data_summary}

**Your Task**:
Generate a comprehensive financial report that includes:
1. Executive summary of financial performance
2. Analysis of revenue sources and their contribution
3. Analysis of expense categories and cost structure
4. Profitability assessment with specific insights
5. Key recommendations for improvement

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_expense_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following expense report data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Identify spending patterns and areas for cost optimization
4. Highlight top expense categories and vendors
5. Provide actionable recommendations

**Expense Data**:
{data_summary}

**Your Task**:
Generate a comprehensive expense analysis that includes:
1. Overview of total spending and patterns
2. Analysis of top expense categories
3. Vendor spending analysis
4. Cost optimization opportunities
5. Recommendations for expense management

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_income_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following income report data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Identify revenue patterns and growth opportunities
4. Highlight top income sources and categories
5. Provide actionable recommendations

**Income Data**:
{data_summary}

**Your Task**:
Generate a comprehensive income analysis that includes:
1. Overview of total revenue and patterns
2. Analysis of top income categories
3. Customer/source revenue analysis
4. Growth opportunities
5. Recommendations for revenue optimization

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_vendor_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following vendor analysis data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Analyze vendor relationships and spending patterns
4. Identify key customers and revenue sources
5. Provide actionable recommendations

**Vendor Data**:
{data_summary}

**Your Task**:
Generate a comprehensive vendor analysis that includes:
1. Overview of vendor spending and customer revenue
2. Analysis of top vendors and their impact
3. Customer revenue analysis
4. Relationship insights
5. Recommendations for vendor and customer management

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_cashflow_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following cash flow data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Analyze cash flow patterns and liquidity
4. Assess account balances and cash position
5. Provide actionable recommendations

**Cash Flow Data**:
{data_summary}

**Your Task**:
Generate a comprehensive cash flow analysis that includes:
1. Overview of cash inflows and outflows
2. Net cash flow assessment
3. Account balance analysis
4. Liquidity assessment
5. Recommendations for cash management

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_monthly_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following monthly summary data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Provide a comprehensive monthly overview
4. Highlight key achievements and concerns
5. Provide actionable recommendations

**Monthly Data**:
{data_summary}

**Your Task**:
Generate a comprehensive monthly summary that includes:
1. Executive summary of the month
2. Financial performance overview
3. Key highlights and achievements
4. Areas of concern
5. Recommendations for next month

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_tax_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following tax report data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Explain tax calculations and obligations
4. Highlight VAT and tax implications
5. Provide actionable recommendations

**Tax Data**:
{data_summary}

**Your Task**:
Generate a comprehensive tax analysis that includes:
1. Overview of tax obligations
2. VAT calculations and breakdown
3. Taxable profit analysis
4. Compliance insights
5. Recommendations for tax planning

Write the report in Persian, using natural language while maintaining accuracy with the provided numbers."""


def _create_generic_analysis_prompt(data_summary: str, period: Dict[str, str]) -> str:
    return f"""You are a financial analyst for an Iranian business. Analyze the following financial data and provide insights in Persian.

**CRITICAL RULES**:
1. Use ONLY the exact numbers provided - do NOT make up or estimate any numbers
2. Write in natural, conversational Persian
3. Provide comprehensive analysis
4. Highlight key findings
5. Provide actionable recommendations

**Financial Data**:
{data_summary}

**Your Task**:
Generate a comprehensive financial report with insights, analysis, and recommendations in Persian."""


def _combine_data_and_ai_insights(data_summary: str, ai_analysis: str, report_type: str) -> str:
    """Combine structured data with AI-generated insights"""
    
    # Start with AI analysis (which should include the data context)
    report = ai_analysis
    
    # Ensure the report has proper formatting
    if not report.startswith("📊"):
        report = f"📊 {report}"
    
    return report


def _create_fallback_report(data_summary: str, report_type: str, period: Dict[str, str]) -> str:
    """Create a basic report if AI analysis fails"""
    report_type_names = {
        "pl": "صورت سود و زیان",
        "expense": "گزارش هزینه‌ها",
        "income": "گزارش درآمد",
        "vendor": "گزارش تحلیل فروشندگان",
        "cash_flow": "گزارش جریان نقدی",
        "monthly": "گزارش خلاصه ماهانه",
        "tax": "گزارش مالیاتی"
    }
    
    report_name = report_type_names.get(report_type, "گزارش مالی")
    
    return f"""📊 **{report_name}**

**دوره**: {period.get('from')} تا {period.get('to')}

{data_summary}

*توجه: تحلیل هوشمند در دسترس نیست. داده‌های خام نمایش داده شده‌اند.*"""


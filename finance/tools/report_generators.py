"""
Report Generation Tools
Creates financial reports for Iranian businesses
"""
from typing import Dict, Any, Optional
from langchain.tools import tool
from datetime import datetime
import json


@tool
def generate_pl_statement(
    user_id: str,
    date_from: str,
    date_to: str
) -> dict:
    """
    Generate Profit & Loss (P&L) Statement
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        
    Returns:
        P&L statement with revenue, expenses, and profit
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get revenue by category
            cursor.execute("""
                SELECT c.name as category, SUM(t.amount) as total
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'income'
                AND t.date BETWEEN ? AND ?
                AND t.deleted_at IS NULL
                GROUP BY c.name
                ORDER BY total DESC
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            revenue_breakdown = [{"category": row['category'] or "سایر", "amount": row['total']} 
                               for row in cursor.fetchall()]
            total_revenue = sum(item['amount'] for item in revenue_breakdown)
            
            # Get expenses by category
            cursor.execute("""
                SELECT c.name as category, SUM(t.amount) as total
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                AND t.date BETWEEN ? AND ?
                AND t.deleted_at IS NULL
                GROUP BY c.name
                ORDER BY total DESC
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            expense_breakdown = [{"category": row['category'] or "سایر", "amount": row['total']} 
                               for row in cursor.fetchall()]
            total_expense = sum(item['amount'] for item in expense_breakdown)
            
            # Calculate profit
            net_profit = total_revenue - total_expense
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # Format report message
            message = f"""📊 **صورت سود و زیان**
            
**دوره**: {date_from} تا {date_to}

**درآمد**:
"""
            for item in revenue_breakdown[:5]:
                message += f"  • {item['category']}: {item['amount']:,} ریال\n"
            message += f"\n**جمع درآمد**: {total_revenue:,} ریال ({total_revenue/10:,} تومان)\n\n"
            
            message += "**هزینه‌ها**:\n"
            for item in expense_breakdown[:5]:
                message += f"  • {item['category']}: {item['amount']:,} ریال\n"
            message += f"\n**جمع هزینه**: {total_expense:,} ریال ({total_expense/10:,} تومان)\n\n"
            
            message += f"**سود خالص**: {net_profit:,} ریال ({net_profit/10:,} تومان)\n"
            message += f"**حاشیه سود**: {profit_margin:.1f}%"
            
            return {
                "success": True,
                "report_type": "pl_statement",
                "period": {"from": date_from, "to": date_to},
                "summary": {
                    "total_revenue": total_revenue,
                    "total_expense": total_expense,
                    "net_profit": net_profit,
                    "profit_margin_pct": profit_margin
                },
                "revenue_breakdown": revenue_breakdown,
                "expense_breakdown": expense_breakdown,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_expense_report(
    user_id: str,
    date_from: str,
    date_to: str,
    top_n: int = 10
) -> dict:
    """
    Generate Expense Report with top spending categories and vendors
    
    Args:
        user_id: User identifier
        date_from: Start date
        date_to: End date
        top_n: Number of top items to show
        
    Returns:
        Detailed expense report
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get top categories by expense
            cursor.execute("""
                SELECT c.name as category, SUM(t.amount) as total, COUNT(*) as count
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                AND t.date BETWEEN ? AND ?
                AND t.deleted_at IS NULL
                GROUP BY c.name
                ORDER BY total DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            top_categories = [dict(row) for row in cursor.fetchall()]
            
            # Get top vendors by expense
            cursor.execute("""
                SELECT vendor, SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND vendor IS NOT NULL
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
                GROUP BY vendor
                ORDER BY total DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            top_vendors = [dict(row) for row in cursor.fetchall()]
            
            total_expense = sum(cat['total'] for cat in top_categories)
            
            # Format message
            message = f"""💸 **گزارش هزینه‌ها**

**دوره**: {date_from} تا {date_to}

**بالاترین دسته‌های هزینه**:
"""
            for cat in top_categories:
                pct = (cat['total'] / total_expense * 100) if total_expense > 0 else 0
                message += f"  • {cat['category'] or 'سایر'}: {cat['total']:,} ریال ({pct:.1f}%) - {cat['count']} تراکنش\n"
            
            message += f"\n**بالاترین فروشندگان**:\n"
            for vendor in top_vendors:
                message += f"  • {vendor['vendor']}: {vendor['total']:,} ریال - {vendor['count']} تراکنش\n"
            
            message += f"\n**جمع کل هزینه**: {total_expense:,} ریال ({total_expense/10:,} تومان)"
            
            return {
                "success": True,
                "report_type": "expense_report",
                "period": {"from": date_from, "to": date_to},
                "total_expense": total_expense,
                "top_categories": top_categories,
                "top_vendors": top_vendors,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_income_report(
    user_id: str,
    date_from: str,
    date_to: str,
    top_n: int = 10
) -> dict:
    """
    Generate Income Report with revenue breakdown by category and source
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        top_n: Number of top items to show
        
    Returns:
        Detailed income report
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get income by category
            cursor.execute("""
                SELECT c.name as category, SUM(t.amount) as total, COUNT(*) as count
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'income'
                AND t.date BETWEEN ? AND ?
                AND t.deleted_at IS NULL
                GROUP BY c.name
                ORDER BY total DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            top_categories = [dict(row) for row in cursor.fetchall()]
            
            # Get top income sources (vendors/customers)
            cursor.execute("""
                SELECT vendor, SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND vendor IS NOT NULL
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
                GROUP BY vendor
                ORDER BY total DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            top_sources = [dict(row) for row in cursor.fetchall()]
            
            total_income = sum(cat['total'] for cat in top_categories)
            
            # Format message
            message = f"""💰 **گزارش درآمد**
            
**دوره**: {date_from} تا {date_to}

**بالاترین دسته‌های درآمد**:
"""
            for cat in top_categories:
                pct = (cat['total'] / total_income * 100) if total_income > 0 else 0
                message += f"  • {cat['category'] or 'سایر'}: {cat['total']:,} ریال ({pct:.1f}%) - {cat['count']} تراکنش\n"
            
            message += f"\n**بالاترین منابع درآمد**:\n"
            for source in top_sources:
                message += f"  • {source['vendor']}: {source['total']:,} ریال - {source['count']} تراکنش\n"
            
            message += f"\n**جمع کل درآمد**: {total_income:,} ریال ({total_income/10:,} تومان)"
            
            return {
                "success": True,
                "report_type": "income_report",
                "period": {"from": date_from, "to": date_to},
                "total_income": total_income,
                "top_categories": top_categories,
                "top_sources": top_sources,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_cash_flow_report(
    user_id: str,
    date_from: str,
    date_to: str
) -> dict:
    """
    Generate Cash Flow Report showing inflows and outflows
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        
    Returns:
        Cash flow report
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get cash inflows (income)
            cursor.execute("""
                SELECT SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            inflow_row = cursor.fetchone()
            total_inflow = inflow_row['total'] or 0
            inflow_count = inflow_row['count'] or 0
            
            # Get cash outflows (expenses)
            cursor.execute("""
                SELECT SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            outflow_row = cursor.fetchone()
            total_outflow = outflow_row['total'] or 0
            outflow_count = outflow_row['count'] or 0
            
            # Get account balances
            cursor.execute("""
                SELECT SUM(current_balance) as total_balance, COUNT(*) as account_count
                FROM finance_accounts
                WHERE user_id = ? AND is_active = TRUE
            """, (user_id,))
            
            balance_row = cursor.fetchone()
            total_balance = balance_row['total_balance'] or 0
            account_count = balance_row['account_count'] or 0
            
            # Calculate net cash flow
            net_cash_flow = total_inflow - total_outflow
            
            # Format message
            message = f"""💵 **گزارش جریان نقدی**
            
**دوره**: {date_from} تا {date_to}

**ورودی‌های نقدی (درآمد)**:
  • مجموع: {total_inflow:,} ریال ({total_inflow/10:,} تومان)
  • تعداد تراکنش: {inflow_count}

**خروجی‌های نقدی (هزینه)**:
  • مجموع: {total_outflow:,} ریال ({total_outflow/10:,} تومان)
  • تعداد تراکنش: {outflow_count}

**جریان نقدی خالص**: {net_cash_flow:,} ریال ({net_cash_flow/10:,} تومان)

**موجودی کل حساب‌ها**: {total_balance:,} ریال ({total_balance/10:,} تومان)
**تعداد حساب‌ها**: {account_count}
"""
            
            return {
                "success": True,
                "report_type": "cash_flow_report",
                "period": {"from": date_from, "to": date_to},
                "total_inflow": total_inflow,
                "total_outflow": total_outflow,
                "net_cash_flow": net_cash_flow,
                "total_balance": total_balance,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_vendor_analysis_report(
    user_id: str,
    date_from: str,
    date_to: str,
    top_n: int = 15
) -> dict:
    """
    Generate Vendor Analysis Report showing spending and income by vendor
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        top_n: Number of top vendors to show
        
    Returns:
        Vendor analysis report
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get top vendors by expense
            cursor.execute("""
                SELECT vendor, SUM(amount) as total_expense, COUNT(*) as expense_count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND vendor IS NOT NULL
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
                GROUP BY vendor
                ORDER BY total_expense DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            expense_vendors = [dict(row) for row in cursor.fetchall()]
            
            # Get top vendors by income
            cursor.execute("""
                SELECT vendor, SUM(amount) as total_income, COUNT(*) as income_count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND vendor IS NOT NULL
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
                GROUP BY vendor
                ORDER BY total_income DESC
                LIMIT ?
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-'), top_n))
            
            income_vendors = [dict(row) for row in cursor.fetchall()]
            
            total_expense = sum(v['total_expense'] for v in expense_vendors)
            total_income = sum(v['total_income'] for v in income_vendors)
            
            # Format message
            message = f"""🏢 **گزارش تحلیل فروشندگان**
            
**دوره**: {date_from} تا {date_to}

**بالاترین فروشندگان (هزینه)**:
"""
            for vendor in expense_vendors[:10]:
                pct = (vendor['total_expense'] / total_expense * 100) if total_expense > 0 else 0
                message += f"  • {vendor['vendor']}: {vendor['total_expense']:,} ریال ({pct:.1f}%) - {vendor['expense_count']} تراکنش\n"
            
            message += f"\n**بالاترین مشتریان/منابع (درآمد)**:\n"
            for vendor in income_vendors[:10]:
                pct = (vendor['total_income'] / total_income * 100) if total_income > 0 else 0
                message += f"  • {vendor['vendor']}: {vendor['total_income']:,} ریال ({pct:.1f}%) - {vendor['income_count']} تراکنش\n"
            
            message += f"\n**جمع کل هزینه از فروشندگان**: {total_expense:,} ریال\n"
            message += f"**جمع کل درآمد از مشتریان**: {total_income:,} ریال"
            
            return {
                "success": True,
                "report_type": "vendor_analysis_report",
                "period": {"from": date_from, "to": date_to},
                "expense_vendors": expense_vendors,
                "income_vendors": income_vendors,
                "total_expense": total_expense,
                "total_income": total_income,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_monthly_summary_report(
    user_id: str,
    year: Optional[int] = None,
    month: Optional[int] = None
) -> dict:
    """
    Generate Monthly Summary Report with overview of financial activity
    
    Args:
        user_id: User identifier
        year: Year (Jalali) - if None, uses current year
        month: Month (1-12) - if None, uses current month
        
    Returns:
        Monthly summary report
    """
    from finance.database import FinanceDatabase
    import jdatetime
    
    try:
        db = FinanceDatabase()
        
        # Use current month if not specified
        if year is None or month is None:
            today = jdatetime.date.today()
            year = year or today.year
            month = month or today.month
        
        date_from = f"{year}-{month:02d}-01"
        # Get last day of month
        if month == 12:
            date_to = f"{year}-{month:02d}-29"  # Jalali year end
        else:
            date_to = f"{year}-{month+1:02d}-01"
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total income
            cursor.execute("""
                SELECT SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND date >= ? AND date < ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            income_row = cursor.fetchone()
            total_income = income_row['total'] or 0
            income_count = income_row['count'] or 0
            
            # Get total expenses
            cursor.execute("""
                SELECT SUM(amount) as total, COUNT(*) as count
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND date >= ? AND date < ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            expense_row = cursor.fetchone()
            total_expense = expense_row['total'] or 0
            expense_count = expense_row['count'] or 0
            
            # Get top expense categories
            cursor.execute("""
                SELECT c.name as category, SUM(t.amount) as total
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                AND t.date >= ? AND t.date < ?
                AND t.deleted_at IS NULL
                GROUP BY c.name
                ORDER BY total DESC
                LIMIT 5
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            top_expense_categories = [dict(row) for row in cursor.fetchall()]
            
            # Get account balances
            cursor.execute("""
                SELECT name, current_balance, currency
                FROM finance_accounts
                WHERE user_id = ? AND is_active = TRUE
            """, (user_id,))
            
            accounts = [dict(row) for row in cursor.fetchall()]
            total_balance = sum(acc['current_balance'] for acc in accounts)
            
            # Calculate profit
            net_profit = total_income - total_expense
            profit_margin = (net_profit / total_income * 100) if total_income > 0 else 0
            
            # Format message
            month_names = ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
            month_name = month_names[month] if 1 <= month <= 12 else f"ماه {month}"
            
            message = f"""📅 **گزارش خلاصه ماهانه**
            
**ماه**: {month_name} {year}

**خلاصه مالی**:
  • درآمد کل: {total_income:,} ریال ({total_income/10:,} تومان) - {income_count} تراکنش
  • هزینه کل: {total_expense:,} ریال ({total_expense/10:,} تومان) - {expense_count} تراکنش
  • سود خالص: {net_profit:,} ریال ({net_profit/10:,} تومان)
  • حاشیه سود: {profit_margin:.1f}%

**بالاترین دسته‌های هزینه**:
"""
            for cat in top_expense_categories:
                message += f"  • {cat['category'] or 'سایر'}: {cat['total']:,} ریال\n"
            
            message += f"\n**موجودی حساب‌ها**:\n"
            for acc in accounts:
                message += f"  • {acc['name']}: {acc['current_balance']:,} {acc['currency']}\n"
            message += f"  • **جمع کل**: {total_balance:,} ریال"
            
            return {
                "success": True,
                "report_type": "monthly_summary",
                "period": {"year": year, "month": month, "month_name": month_name},
                "summary": {
                    "total_income": total_income,
                    "total_expense": total_expense,
                    "net_profit": net_profit,
                    "profit_margin_pct": profit_margin
                },
                "top_expense_categories": top_expense_categories,
                "accounts": accounts,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


@tool
def generate_tax_report(
    user_id: str,
    date_from: str,
    date_to: str
) -> dict:
    """
    Generate Tax Report for Iranian businesses (VAT calculations)
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        
    Returns:
        Tax report with VAT calculations
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        # VAT rate in Iran is 9%
        VAT_RATE = 0.09
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get taxable income (all income)
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            income_row = cursor.fetchone()
            taxable_income = income_row['total'] or 0
            
            # Get deductible expenses
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            expense_row = cursor.fetchone()
            deductible_expenses = expense_row['total'] or 0
            
            # Calculate VAT on income (output VAT)
            vat_on_income = taxable_income * VAT_RATE
            
            # Calculate VAT on expenses (input VAT - deductible)
            vat_on_expenses = deductible_expenses * VAT_RATE
            
            # Net VAT payable
            net_vat_payable = vat_on_income - vat_on_expenses
            
            # Taxable profit (for income tax calculation)
            taxable_profit = taxable_income - deductible_expenses
            
            # Format message
            message = f"""📋 **گزارش مالیاتی**
            
**دوره**: {date_from} تا {date_to}

**محاسبات مالیات بر ارزش افزوده (VAT)**:
  • درآمد مشمول مالیات: {taxable_income:,} ریال ({taxable_income/10:,} تومان)
  • مالیات بر درآمد (خروجی): {vat_on_income:,} ریال ({vat_on_income/10:,} تومان) - 9%
  
  • هزینه‌های قابل کسر: {deductible_expenses:,} ریال ({deductible_expenses/10:,} تومان)
  • مالیات بر هزینه‌ها (ورودی): {vat_on_expenses:,} ریال ({vat_on_expenses/10:,} تومان) - 9%
  
  • **مالیات قابل پرداخت**: {net_vat_payable:,} ریال ({net_vat_payable/10:,} تومان)

**سود مشمول مالیات**: {taxable_profit:,} ریال ({taxable_profit/10:,} تومان)

**نکات مهم**:
  • این گزارش بر اساس داده‌های ثبت شده محاسبه شده است
  • برای اظهارنامه مالیاتی، لطفاً با حسابدار خود مشورت کنید
  • نرخ مالیات بر ارزش افزوده: 9%
"""
            
            return {
                "success": True,
                "report_type": "tax_report",
                "period": {"from": date_from, "to": date_to},
                "taxable_income": taxable_income,
                "deductible_expenses": deductible_expenses,
                "vat_on_income": vat_on_income,
                "vat_on_expenses": vat_on_expenses,
                "net_vat_payable": net_vat_payable,
                "taxable_profit": taxable_profit,
                "message": message
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تولید گزارش: {str(e)}"
        }


# Export tools
REPORT_TOOLS = [
    generate_pl_statement,
    generate_expense_report,
    generate_income_report,
    generate_cash_flow_report,
    generate_vendor_analysis_report,
    generate_monthly_summary_report,
    generate_tax_report
]


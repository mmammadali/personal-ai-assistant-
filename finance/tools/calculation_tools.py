"""
Financial Calculation Tools
Handles financial metrics, cash flow projections, and analysis
"""
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from datetime import datetime, timedelta
import json


@tool
def calculate_financial_metrics(
    user_id: str,
    date_from: str,
    date_to: str
) -> dict:
    """
    Calculate key financial metrics for a period
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        
    Returns:
        Financial metrics including profit margins, growth rates
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total revenue
            cursor.execute("""
                SELECT SUM(amount) as total_revenue
                FROM finance_transactions
                WHERE user_id = ? AND type = 'income'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            revenue_row = cursor.fetchone()
            total_revenue = revenue_row['total_revenue'] or 0
            
            # Get total expenses
            cursor.execute("""
                SELECT SUM(amount) as total_expense
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, date_from.replace('/', '-'), date_to.replace('/', '-')))
            
            expense_row = cursor.fetchone()
            total_expense = expense_row['total_expense'] or 0
            
            # Calculate metrics
            net_profit = total_revenue - total_expense
            profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                "success": True,
                "period": f"{date_from} to {date_to}",
                "metrics": {
                    "total_revenue": total_revenue,
                    "total_expense": total_expense,
                    "net_profit": net_profit,
                    "profit_margin_pct": profit_margin
                },
                "message": f"✅ مجموع درآمد: {total_revenue:,} | هزینه: {total_expense:,} | سود خالص: {net_profit:,}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در محاسبه معیارها: {str(e)}"
        }


@tool
def calculate_burn_rate(user_id: str, days: int = 30) -> dict:
    """
    Calculate burn rate (average daily/monthly spending)
    
    Args:
        user_id: User identifier
        days: Number of days to calculate over (default: 30)
        
    Returns:
        Burn rate information
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total expenses for last N days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            cursor.execute("""
                SELECT SUM(amount) as total_expense
                FROM finance_transactions
                WHERE user_id = ? AND type = 'expense'
                AND date BETWEEN ? AND ?
                AND deleted_at IS NULL
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            
            row = cursor.fetchone()
            total_expense = row['total_expense'] or 0
            
            daily_burn = total_expense / days if days > 0 else 0
            monthly_burn = daily_burn * 30
            
            return {
                "success": True,
                "period_days": days,
                "total_expense": total_expense,
                "daily_burn_rate": daily_burn,
                "monthly_burn_rate": monthly_burn,
                "message": f"✅ نرخ سوخت: {daily_burn:,} ریال/روز | {monthly_burn:,} ریال/ماه"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@tool
def project_cash_flow(user_id: str, days: int = 90) -> dict:
    """
    Project future cash flow based on patterns
    
    Args:
        user_id: User identifier
        days: Number of days to project
        
    Returns:
        Cash flow projection
    """
    # Simplified implementation - can be enhanced with ML models
    try:
        # Get burn rate
        burn_result = calculate_burn_rate.invoke({"user_id": user_id, "days": 30})
        
        if not burn_result.get("success"):
            return {
                "success": False,
                "message": "نمی‌توان جریان نقدی را پیش‌بینی کرد"
            }
        
        daily_burn = burn_result.get("daily_burn_rate", 0)
        
        # Simple projection (can be enhanced)
        projected_expense = daily_burn * days
        
        return {
            "success": True,
            "forecast_days": days,
            "projected_total_expense": projected_expense,
            "daily_average": daily_burn,
            "message": f"✅ پیش‌بینی {days} روز آینده: {projected_expense:,} ریال هزینه",
            "note": "این یک پیش‌بینی ساده است. برای دقت بیشتر، داده‌های تاریخی بیشتری نیاز است."
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Export tools
CALCULATION_TOOLS = [
    calculate_financial_metrics,
    calculate_burn_rate,
    project_cash_flow
]


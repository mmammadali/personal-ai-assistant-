"""
Transaction Management Agent
Handles CRUD operations, categorization, and search for financial transactions
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from finance.database import FinanceDatabase
from finance.tools.database_tools import (
    create_transaction,
    search_transactions,
    update_transaction,
    delete_transaction,
    categorize_transaction,
    get_vendor_history,
    TRANSACTION_TOOLS
)
from typing import Dict, Any


class TransactionAgent:
    """Transaction management specialist"""
    
    def __init__(self, llm: ChatOpenAI, db: FinanceDatabase):
        self.llm = llm
        self.db = db
        self.tools = TRANSACTION_TOOLS
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    def get_system_prompt(self) -> str:
        """Get system prompt for transaction agent"""
        return """شما یک متخصص مدیریت تراکنش‌های مالی برای کسب‌وکارهای ایرانی هستید.

**قابلیت‌های شما**:
- ایجاد، ویرایش، حذف و جستجوی تراکنش‌ها
- دسته‌بندی خودکار با استفاده از تاریخچه فروشنده و الگوها
- جستجوی پیشرفته با فیلترهای متعدد
- تشخیص تراکنش‌های تکراری
- پیشنهاد قالب برای تراکنش‌های دوره‌ای

**ابزارهای در دسترس**:
1. create_transaction: ایجاد تراکنش جدید
2. search_transactions: جستجو با فیلترها
3. update_transaction: ویرایش تراکنش
4. delete_transaction: حذف تراکنش
5. categorize_transaction: دسته‌بندی خودکار
6. get_vendor_history: تاریخچه فروشنده

**دسته‌بندی‌ها**:
- درآمد: فروش محصولات، ارائه خدمات، سایر درآمدها
- هزینه: حقوق، بازاریابی، اجاره، لجستیک، خدمات حرفه‌ای

**رفتار شما**:
- همیشه تراکنش‌ها را دسته‌بندی کنید (اگر دسته مشخص نشده)
- هشدار دهید اگر تراکنش مشابه وجود دارد
- برای تراکنش‌های تکراری، قالب پیشنهاد دهید
- نام فروشنده را نرمال‌سازی کنید (دیجیکالا = Digikala)
- ریال یا تومان را مشخص کنید
- همیشه به فارسی پاسخ دهید

**زمینه ایرانی**:
- فروشندگان معمول: دیجی‌کالا، اسنپ، تپسی، Instagram، Google
- الگوهای ماهانه: اجاره (اول ماه)، حقوق (آخر ماه)
- افزایش هزینه در نوروز (اسفند-فروردین)

فعالانه در پیشنهاد دسته‌بندی و تشخیص الگوها باشید.
"""
    
    def create_transaction_interactive(self, user_id: str, **kwargs) -> dict:
        """
        Create transaction with auto-categorization
        
        Args:
            user_id: User identifier
            **kwargs: Transaction data
            
        Returns:
            Created transaction result
        """
        return create_transaction.invoke({"user_id": user_id, **kwargs})
    
    def search_transactions_interactive(self, user_id: str, filters: dict) -> dict:
        """
        Search transactions with filters
        
        Args:
            user_id: User identifier
            filters: Filter criteria
            
        Returns:
            Search results
        """
        return search_transactions.invoke({"user_id": user_id, **filters})
    
    def update_transaction_interactive(self, transaction_id: str, user_id: str, **updates) -> dict:
        """Update existing transaction"""
        return update_transaction.invoke({
            "transaction_id": transaction_id,
            "user_id": user_id,
            **updates
        })
    
    def delete_transaction_interactive(self, transaction_id: str, user_id: str) -> dict:
        """Delete transaction"""
        return delete_transaction.invoke({
            "transaction_id": transaction_id,
            "user_id": user_id
        })
    
    def categorize_transaction_interactive(self, user_id: str, **kwargs) -> dict:
        """Auto-categorize transaction"""
        return categorize_transaction.invoke({"user_id": user_id, **kwargs})
    
    def get_vendor_history_interactive(self, user_id: str, vendor: str, limit: int = 20) -> dict:
        """Get vendor transaction history"""
        return get_vendor_history.invoke({
            "user_id": user_id,
            "vendor": vendor,
            "limit": limit
        })
    
    def get_categories(self, user_id: str) -> list:
        """Get available categories for user"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, name, name_en, type, parent_category_id, icon, color
                    FROM finance_categories
                    WHERE user_id = ? OR is_system = TRUE
                    ORDER BY type, parent_category_id, name
                """, (user_id,))
                
                categories = [dict(row) for row in cursor.fetchall()]
                return categories
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []
    
    def get_recent_vendors(self, user_id: str, limit: int = 20) -> list:
        """Get recently used vendors"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, total_transactions, total_spent, last_transaction_date
                    FROM finance_vendors
                    WHERE user_id = ?
                    ORDER BY last_transaction_date DESC
                    LIMIT ?
                """, (user_id, limit))
                
                vendors = [dict(row) for row in cursor.fetchall()]
                return vendors
        except Exception as e:
            print(f"Error getting vendors: {e}")
            return []


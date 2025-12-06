"""
Database Tools for Finance Operations
Handles transactions, vendors, categories, and related CRUD operations
"""
from typing import Dict, Any, Optional, List
from langchain.tools import tool
from datetime import datetime, date
import uuid
import json

# Optional import for fuzzy matching
try:
    from fuzzywuzzy import fuzz
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    fuzz = None


# ===================== TRANSACTION TOOLS =====================

@tool
def create_transaction(
    user_id: str,
    amount: float,
    transaction_type: str,
    date: str,
    description: str,
    vendor: Optional[str] = None,
    category: Optional[str] = None,
    payment_method: Optional[str] = None,
    currency: str = "IRR"
) -> dict:
    """
    Create a new financial transaction
    
    Args:
        user_id: User identifier
        amount: Transaction amount (must be positive)
        transaction_type: Type of transaction (expense, income, transfer)
        date: Transaction date (Jalali format YYYY/MM/DD)
        description: Transaction description
        vendor: Vendor/merchant name (optional)
        category: Category ID or name (optional, will auto-categorize if not provided)
        payment_method: Payment method (cash, card, transfer, check)
        currency: Currency code (default: IRR)
        
    Returns:
        Created transaction information
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        # Validate inputs
        if amount <= 0:
            return {"success": False, "error": "مبلغ باید بزرگتر از صفر باشد"}
        
        if transaction_type not in ['expense', 'income', 'transfer']:
            return {"success": False, "error": "نوع تراکنش نامعتبر است"}
        
        # Normalize date format
        normalized_date = date.replace('/', '-')
        
        # Auto-categorize if category not provided
        if not category and vendor:
            category_result = categorize_transaction.invoke({
                "user_id": user_id,
                "vendor": vendor,
                "description": description,
                "amount": amount,
                "transaction_type": transaction_type
            })
            category = category_result.get("category_id")
        
        # Normalize vendor name
        normalized_vendor = _normalize_vendor_name(vendor) if vendor else None
        
        # Create transaction
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            transaction_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO finance_transactions
                (id, user_id, type, amount, currency, category_id, vendor, 
                 description, date, payment_method, amount_in_base_currency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                user_id,
                transaction_type,
                amount,
                currency,
                category,
                normalized_vendor,
                description,
                normalized_date,
                payment_method,
                amount  # TODO: Convert to base currency if needed
            ))
            
            # Update vendor statistics if vendor exists
            if normalized_vendor:
                _update_vendor_stats(db, user_id, normalized_vendor, amount, normalized_date, category)
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "message": f"✅ تراکنش با موفقیت ثبت شد (شناسه: {transaction_id[:8]})",
                "amount": amount,
                "type": transaction_type,
                "vendor": normalized_vendor,
                "category": category
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در ثبت تراکنش: {str(e)}"
        }


@tool
def search_transactions(
    user_id: str,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    transaction_type: Optional[str] = None,
    search_text: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    Search transactions with various filters
    
    Args:
        user_id: User identifier
        date_from: Start date (Jalali format)
        date_to: End date (Jalali format)
        category: Category ID or name
        vendor: Vendor name (partial match)
        min_amount: Minimum amount
        max_amount: Maximum amount
        transaction_type: Transaction type filter
        search_text: Free text search in description
        limit: Maximum results to return
        
    Returns:
        List of matching transactions
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT t.*, c.name as category_name
                FROM finance_transactions t
                LEFT JOIN finance_categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.deleted_at IS NULL
            """
            params = [user_id]
            
            # Apply filters
            if date_from:
                query += " AND t.date >= ?"
                params.append(date_from.replace('/', '-'))
            
            if date_to:
                query += " AND t.date <= ?"
                params.append(date_to.replace('/', '-'))
            
            if category:
                query += " AND (t.category_id = ? OR c.name LIKE ?)"
                params.extend([category, f"%{category}%"])
            
            if vendor:
                query += " AND t.vendor LIKE ?"
                params.append(f"%{vendor}%")
            
            if min_amount:
                query += " AND t.amount >= ?"
                params.append(min_amount)
            
            if max_amount:
                query += " AND t.amount <= ?"
                params.append(max_amount)
            
            if transaction_type:
                query += " AND t.type = ?"
                params.append(transaction_type)
            
            if search_text:
                query += " AND t.description LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY t.date DESC, t.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            transactions = [dict(row) for row in rows]
            
            return {
                "success": True,
                "count": len(transactions),
                "transactions": transactions,
                "message": f"✅ {len(transactions)} تراکنش یافت شد"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "transactions": []
        }


@tool
def update_transaction(
    transaction_id: str,
    user_id: str,
    **updates
) -> dict:
    """
    Update an existing transaction
    
    Args:
        transaction_id: Transaction identifier
        user_id: User identifier
        **updates: Fields to update (amount, category_id, vendor, description, etc.)
        
    Returns:
        Update result
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        # Build update query
        allowed_fields = ['amount', 'category_id', 'vendor', 'description', 'date', 'payment_method', 'currency']
        update_fields = []
        params = []
        
        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return {"success": False, "error": "هیچ فیلدی برای به‌روزرسانی مشخص نشده است"}
        
        params.extend([datetime.now().isoformat(), transaction_id, user_id])
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = f"""
                UPDATE finance_transactions
                SET {', '.join(update_fields)}, updated_at = ?
                WHERE id = ? AND user_id = ? AND deleted_at IS NULL
            """
            
            cursor.execute(query, params)
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": "✅ تراکنش با موفقیت به‌روزرسانی شد",
                    "updated_fields": list(updates.keys())
                }
            else:
                return {
                    "success": False,
                    "error": "تراکنش یافت نشد یا به‌روزرسانی نشد"
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در به‌روزرسانی: {str(e)}"
        }


@tool
def delete_transaction(transaction_id: str, user_id: str) -> dict:
    """
    Delete a transaction (soft delete)
    
    Args:
        transaction_id: Transaction identifier
        user_id: User identifier
        
    Returns:
        Delete result
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Soft delete
            cursor.execute("""
                UPDATE finance_transactions
                SET deleted_at = ?
                WHERE id = ? AND user_id = ? AND deleted_at IS NULL
            """, (datetime.now().isoformat(), transaction_id, user_id))
            
            if cursor.rowcount > 0:
                return {
                    "success": True,
                    "message": "✅ تراکنش حذف شد"
                }
            else:
                return {
                    "success": False,
                    "error": "تراکنش یافت نشد"
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===================== CATEGORIZATION TOOLS =====================

@tool
def categorize_transaction(
    user_id: str,
    vendor: str,
    description: str,
    amount: float,
    transaction_type: str
) -> dict:
    """
    Auto-categorize a transaction based on vendor history and patterns
    
    Args:
        user_id: User identifier
        vendor: Vendor name
        description: Transaction description
        amount: Transaction amount
        transaction_type: Type (expense or income)
        
    Returns:
        Suggested category with confidence score
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        # Strategy 1: Check vendor history
        vendor_category = _get_vendor_default_category(db, user_id, vendor)
        if vendor_category:
            return {
                "success": True,
                "category_id": vendor_category["id"],
                "category_name": vendor_category["name"],
                "confidence": 0.9,
                "method": "vendor_history",
                "message": f"✅ دسته‌بندی بر اساس تاریخچه فروشنده: {vendor_category['name']}"
            }
        
        # Strategy 2: Pattern matching based on description keywords
        pattern_category = _match_category_by_pattern(db, user_id, description, transaction_type)
        if pattern_category:
            return {
                "success": True,
                "category_id": pattern_category["id"],
                "category_name": pattern_category["name"],
                "confidence": 0.75,
                "method": "pattern_matching",
                "message": f"✅ دسته‌بندی بر اساس الگو: {pattern_category['name']}"
            }
        
        # Strategy 3: Default category for type
        default_category = _get_default_category(db, user_id, transaction_type)
        if default_category:
            return {
                "success": True,
                "category_id": default_category["id"],
                "category_name": default_category["name"],
                "confidence": 0.5,
                "method": "default",
                "message": f"دسته‌بندی پیش‌فرض: {default_category['name']}"
            }
        
        return {
            "success": False,
            "message": "دسته‌بندی خودکار امکان‌پذیر نیست"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===================== VENDOR TOOLS =====================

@tool
def get_vendor_history(user_id: str, vendor: str, limit: int = 20) -> dict:
    """
    Get transaction history for a specific vendor
    
    Args:
        user_id: User identifier
        vendor: Vendor name
        limit: Maximum transactions to return
        
    Returns:
        Vendor transaction history and statistics
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        normalized_vendor = _normalize_vendor_name(vendor)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get vendor info
            cursor.execute("""
                SELECT * FROM finance_vendors
                WHERE user_id = ? AND normalized_name = ?
            """, (user_id, normalized_vendor))
            
            vendor_row = cursor.fetchone()
            vendor_info = dict(vendor_row) if vendor_row else None
            
            # Get recent transactions
            cursor.execute("""
                SELECT * FROM finance_transactions
                WHERE user_id = ? AND vendor LIKE ? AND deleted_at IS NULL
                ORDER BY date DESC
                LIMIT ?
            """, (user_id, f"%{vendor}%", limit))
            
            transactions = [dict(row) for row in cursor.fetchall()]
            
            # Calculate statistics
            if transactions:
                total_spent = sum(t['amount'] for t in transactions if t['type'] == 'expense')
                avg_amount = total_spent / len(transactions) if transactions else 0
                
                return {
                    "success": True,
                    "vendor": vendor,
                    "vendor_info": vendor_info,
                    "transaction_count": len(transactions),
                    "total_spent": total_spent,
                    "average_amount": avg_amount,
                    "transactions": transactions,
                    "message": f"✅ {len(transactions)} تراکنش برای {vendor}"
                }
            else:
                return {
                    "success": True,
                    "vendor": vendor,
                    "transaction_count": 0,
                    "message": "تراکنشی برای این فروشنده یافت نشد"
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ===================== HELPER FUNCTIONS =====================

def _normalize_vendor_name(vendor: str) -> str:
    """Normalize vendor name for consistency"""
    if not vendor:
        return ""
    
    # Common normalizations
    replacements = {
        'digikala': 'دیجی‌کالا',
        'digi kala': 'دیجی‌کالا',
        'snapp': 'اسنپ',
        'tapsi': 'تپسی',
        'google': 'Google',
        'instagram': 'Instagram',
    }
    
    vendor_lower = vendor.lower().strip()
    for key, value in replacements.items():
        if key in vendor_lower:
            return value
    
    return vendor.strip()


def _update_vendor_stats(db, user_id: str, vendor: str, amount: float, date: str, category: str):
    """Update vendor statistics"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if vendor exists
            cursor.execute("""
                SELECT id FROM finance_vendors
                WHERE user_id = ? AND normalized_name = ?
            """, (user_id, vendor))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing vendor
                cursor.execute("""
                    UPDATE finance_vendors
                    SET total_transactions = total_transactions + 1,
                        total_spent = total_spent + ?,
                        last_transaction_date = ?,
                        default_category_id = ?
                    WHERE id = ?
                """, (amount, date, category, existing['id']))
            else:
                # Create new vendor
                vendor_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO finance_vendors
                    (id, user_id, name, normalized_name, total_transactions, total_spent, 
                     last_transaction_date, default_category_id)
                    VALUES (?, ?, ?, ?, 1, ?, ?, ?)
                """, (vendor_id, user_id, vendor, vendor, amount, date, category))
    
    except Exception as e:
        print(f"Error updating vendor stats: {e}")


def _get_vendor_default_category(db, user_id: str, vendor: str) -> Optional[dict]:
    """Get vendor's most common category"""
    try:
        normalized_vendor = _normalize_vendor_name(vendor)
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT v.default_category_id, c.name
                FROM finance_vendors v
                LEFT JOIN finance_categories c ON v.default_category_id = c.id
                WHERE v.user_id = ? AND v.normalized_name = ?
            """, (user_id, normalized_vendor))
            
            row = cursor.fetchone()
            if row and row['default_category_id']:
                return {"id": row['default_category_id'], "name": row['name']}
    
    except Exception as e:
        print(f"Error getting vendor category: {e}")
    
    return None


def _match_category_by_pattern(db, user_id: str, description: str, transaction_type: str) -> Optional[dict]:
    """Match category based on description keywords"""
    keywords = {
        'بازاریابی': ['تبلیغ', 'مارکتینگ', 'اینستاگرام', 'instagram', 'google ads'],
        'اجاره': ['rent', 'اجاره', 'رهن'],
        'حقوق': ['salary', 'حقوق', 'دستمزد', 'payroll'],
        'لجستیک': ['حمل', 'ارسال', 'shipping', 'delivery', 'پست'],
    }
    
    description_lower = description.lower()
    
    for category_name, keywords_list in keywords.items():
        if any(keyword in description_lower for keyword in keywords_list):
            try:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, name FROM finance_categories
                        WHERE (user_id = ? OR is_system = TRUE)
                        AND name LIKE ?
                        AND type = ?
                        LIMIT 1
                    """, (user_id, f"%{category_name}%", transaction_type))
                    
                    row = cursor.fetchone()
                    if row:
                        return {"id": row['id'], "name": row['name']}
            except Exception as e:
                print(f"Error matching pattern: {e}")
    
    return None


def _get_default_category(db, user_id: str, transaction_type: str) -> Optional[dict]:
    """Get default category for transaction type"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name FROM finance_categories
                WHERE (user_id = ? OR is_system = TRUE)
                AND type = ?
                AND parent_category_id IS NULL
                LIMIT 1
            """, (user_id, transaction_type))
            
            row = cursor.fetchone()
            if row:
                return {"id": row['id'], "name": row['name']}
    except Exception as e:
        print(f"Error getting default category: {e}")
    
    return None


# ===================== ACCOUNT TOOLS =====================

@tool
def create_account(
    user_id: str,
    name: str,
    account_type: str,
    currency: str = "IRR",
    initial_balance: float = 0.0
) -> dict:
    """
    Create a new financial account (bank, cash, or credit card)
    
    Args:
        user_id: User identifier
        name: Account name (e.g., "حساب بانکی ملی", "نقدی", "کارت اعتباری")
        account_type: Type of account (bank, cash, credit_card)
        currency: Currency code (default: IRR)
        initial_balance: Initial balance (default: 0.0)
        
    Returns:
        Created account information
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        # Validate inputs
        if account_type not in ['bank', 'cash', 'credit_card']:
            return {"success": False, "error": "نوع حساب نامعتبر است. باید bank، cash یا credit_card باشد"}
        
        if not name or not name.strip():
            return {"success": False, "error": "نام حساب نمی‌تواند خالی باشد"}
        
        # Create account
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            account_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO finance_accounts
                (id, user_id, name, type, currency, current_balance)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                account_id,
                user_id,
                name.strip(),
                account_type,
                currency,
                initial_balance
            ))
            
            # Get account type name in Persian
            type_names = {
                'bank': 'بانکی',
                'cash': 'نقدی',
                'credit_card': 'کارت اعتباری'
            }
            
            return {
                "success": True,
                "account_id": account_id,
                "message": f"✅ حساب {type_names.get(account_type, account_type)} با نام '{name}' با موفقیت ایجاد شد",
                "account": {
                    "id": account_id,
                    "name": name.strip(),
                    "type": account_type,
                    "currency": currency,
                    "balance": initial_balance
                }
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در ایجاد حساب: {str(e)}"
        }


@tool
def list_accounts(user_id: str) -> dict:
    """
    List all active accounts for a user
    
    Args:
        user_id: User identifier
        
    Returns:
        List of accounts
    """
    from finance.database import FinanceDatabase
    
    try:
        db = FinanceDatabase()
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, type, currency, current_balance, last_updated
                FROM finance_accounts
                WHERE user_id = ? AND is_active = TRUE
                ORDER BY created_at DESC
            """, (user_id,))
            
            accounts = [dict(row) for row in cursor.fetchall()]
            
            return {
                "success": True,
                "accounts": accounts,
                "count": len(accounts),
                "message": f"✅ {len(accounts)} حساب فعال یافت شد"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "accounts": []
        }


# Export tools
TRANSACTION_TOOLS = [
    create_transaction,
    search_transactions,
    update_transaction,
    delete_transaction,
    categorize_transaction,
    get_vendor_history
]

ACCOUNT_TOOLS = [
    create_account,
    list_accounts
]


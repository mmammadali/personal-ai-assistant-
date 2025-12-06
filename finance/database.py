"""
Finance Database Management
Handles all financial data storage with SQLite
"""
import sqlite3
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime


class FinanceDatabase:
    """Manages SQLite database for finance operations"""
    
    def __init__(self, db_path: str = "finance.db"):
        self.db_path = db_path
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create all finance tables if they don't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    preferences TEXT DEFAULT '{}'
                )
            """)
            
            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_accounts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('bank', 'cash', 'credit_card')),
                    currency TEXT DEFAULT 'IRR',
                    current_balance REAL DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE
                )
            """)
            
            # Categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_categories (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    parent_category_id TEXT,
                    type TEXT NOT NULL CHECK (type IN ('expense', 'income')),
                    icon TEXT,
                    color TEXT,
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (parent_category_id) REFERENCES finance_categories(id) ON DELETE CASCADE
                )
            """)
            
            # Vendors table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_vendors (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    normalized_name TEXT,
                    contact_info TEXT,
                    default_category_id TEXT,
                    payment_terms INTEGER,
                    notes TEXT,
                    total_transactions INTEGER DEFAULT 0,
                    total_spent REAL DEFAULT 0,
                    last_transaction_date DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (default_category_id) REFERENCES finance_categories(id) ON DELETE SET NULL
                )
            """)
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_transactions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    account_id TEXT,
                    type TEXT NOT NULL CHECK (type IN ('expense', 'income', 'transfer')),
                    amount REAL NOT NULL CHECK (amount > 0),
                    currency TEXT DEFAULT 'IRR',
                    amount_in_base_currency REAL,
                    category_id TEXT,
                    vendor TEXT,
                    description TEXT,
                    date DATE NOT NULL,
                    payment_method TEXT CHECK (payment_method IN ('cash', 'card', 'transfer', 'check')),
                    tags TEXT,
                    is_recurring BOOLEAN DEFAULT FALSE,
                    recurrence_pattern TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (account_id) REFERENCES finance_accounts(id) ON DELETE SET NULL,
                    FOREIGN KEY (category_id) REFERENCES finance_categories(id) ON DELETE SET NULL
                )
            """)
            
            # Invoices table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_invoices (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    invoice_number TEXT,
                    type TEXT NOT NULL CHECK (type IN ('customer_invoice', 'vendor_invoice')),
                    customer_vendor_id TEXT,
                    issue_date DATE NOT NULL,
                    due_date DATE,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'IRR',
                    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled')),
                    payment_date DATE,
                    related_transaction_id TEXT,
                    items TEXT,
                    notes TEXT,
                    document_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (customer_vendor_id) REFERENCES finance_vendors(id) ON DELETE SET NULL,
                    FOREIGN KEY (related_transaction_id) REFERENCES finance_transactions(id) ON DELETE SET NULL
                )
            """)
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_documents (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('receipt', 'invoice', 'statement', 'other')),
                    file_url TEXT NOT NULL,
                    file_type TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE,
                    extracted_data TEXT,
                    related_transaction_id TEXT,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (related_transaction_id) REFERENCES finance_transactions(id) ON DELETE SET NULL
                )
            """)
            
            # Budgets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_budgets (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    category_id TEXT,
                    period_type TEXT NOT NULL CHECK (period_type IN ('monthly', 'quarterly', 'annual')),
                    period_start DATE NOT NULL,
                    period_end DATE NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'IRR',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES finance_categories(id) ON DELETE CASCADE
                )
            """)
            
            # Exchange rates table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_exchange_rates (
                    id TEXT PRIMARY KEY,
                    from_currency TEXT NOT NULL,
                    to_currency TEXT NOT NULL,
                    rate REAL NOT NULL,
                    rate_type TEXT NOT NULL CHECK (rate_type IN ('official', 'parallel', 'nima')),
                    date DATE NOT NULL,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(from_currency, to_currency, rate_type, date)
                )
            """)
            
            # Conversation memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS finance_memory (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    agent_name TEXT,
                    message_type TEXT NOT NULL CHECK (message_type IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES finance_users(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_accounts_user ON finance_accounts(user_id, is_active)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_transactions_user_date ON finance_transactions(user_id, date DESC) WHERE deleted_at IS NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_transactions_category ON finance_transactions(user_id, category_id) WHERE deleted_at IS NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_transactions_vendor ON finance_transactions(vendor) WHERE deleted_at IS NULL")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_vendors_user ON finance_vendors(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_vendors_normalized ON finance_vendors(normalized_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_invoices_user_status ON finance_invoices(user_id, status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_documents_user_type ON finance_documents(user_id, type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_memory_session ON finance_memory(session_id, created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_finance_exchange_rates ON finance_exchange_rates(from_currency, to_currency, date DESC)")
            
            print("✅ Finance database initialized successfully")
    
    def init_default_categories(self, user_id: str):
        """Initialize default Iranian business categories"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            categories = [
                # Revenue categories
                ('income-1', None, 'درآمد', 'Revenue', 'income', True),
                ('income-product', 'income-1', 'فروش محصولات', 'Product Sales', 'income', True),
                ('income-service', 'income-1', 'ارائه خدمات', 'Service Revenue', 'income', True),
                ('income-other', 'income-1', 'سایر درآمدها', 'Other Income', 'income', True),
                
                # Expense categories
                ('expense-1', None, 'هزینه‌ها', 'Expenses', 'expense', True),
                ('expense-payroll', 'expense-1', 'حقوق و دستمزد', 'Payroll', 'expense', True),
                ('expense-marketing', 'expense-1', 'بازاریابی', 'Marketing', 'expense', True),
                ('expense-marketing-digital', 'expense-marketing', 'تبلیغات دیجیتال', 'Digital Ads', 'expense', True),
                ('expense-marketing-events', 'expense-marketing', 'رویدادها', 'Events', 'expense', True),
                ('expense-operations', 'expense-1', 'عملیات', 'Operations', 'expense', True),
                ('expense-rent', 'expense-operations', 'اجاره', 'Rent', 'expense', True),
                ('expense-utilities', 'expense-operations', 'آب و برق', 'Utilities', 'expense', True),
                ('expense-supplies', 'expense-operations', 'لوازم اداری', 'Office Supplies', 'expense', True),
                ('expense-logistics', 'expense-1', 'لجستیک', 'Logistics', 'expense', True),
                ('expense-professional', 'expense-1', 'خدمات حرفه‌ای', 'Professional Services', 'expense', True),
            ]
            
            import uuid
            for cat_id, parent_id, name, name_en, cat_type, is_system in categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO finance_categories 
                    (id, user_id, name, name_en, parent_category_id, type, is_system)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (cat_id, user_id, name, name_en, parent_id, cat_type, is_system))
            
            print(f"✅ Default categories initialized for user {user_id}")


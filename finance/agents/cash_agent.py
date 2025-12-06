"""
Cash Management Agent
Handles balance tracking, currency management, and cash flow projections
"""
from langchain_openai import ChatOpenAI
from finance.database import FinanceDatabase
from finance.tools.exchange_rate_tools import (
    fetch_exchange_rates,
    convert_currency,
    EXCHANGE_RATE_TOOLS
)
from finance.tools.calculation_tools import (
    calculate_financial_metrics,
    calculate_burn_rate,
    project_cash_flow,
    CALCULATION_TOOLS
)
from finance.tools.database_tools import (
    create_account,
    list_accounts,
    ACCOUNT_TOOLS
)


class CashAgent:
    """Cash management specialist"""
    
    def __init__(self, llm: ChatOpenAI, db: FinanceDatabase):
        self.llm = llm
        self.db = db
        self.tools = EXCHANGE_RATE_TOOLS + CALCULATION_TOOLS + ACCOUNT_TOOLS
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(self.tools)
    
    def get_balance(self, user_id: str) -> dict:
        """
        Get current balance summary across all accounts
        
        Args:
            user_id: User identifier
            
        Returns:
            Balance information
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get all active accounts
                cursor.execute("""
                    SELECT id, name, type, currency, current_balance, last_updated
                    FROM finance_accounts
                    WHERE user_id = ? AND is_active = TRUE
                """, (user_id,))
                
                accounts = [dict(row) for row in cursor.fetchall()]
                
                # Calculate total balance (convert all to IRR)
                total_balance_irr = 0
                for account in accounts:
                    if account['currency'] == 'IRR':
                        total_balance_irr += account['current_balance']
                    else:
                        # Convert to IRR
                        conversion = convert_currency.invoke({
                            "amount": account['current_balance'],
                            "from_currency": account['currency'],
                            "to_currency": "IRR",
                            "rate_type": "parallel"
                        })
                        if conversion.get("success"):
                            total_balance_irr += conversion.get("amount", 0)
                
                return {
                    "success": True,
                    "total_balance": total_balance_irr,
                    "currency": "IRR",
                    "accounts": accounts,
                    "account_count": len(accounts),
                    "message": f"💰 موجودی کل: {total_balance_irr:,} ریال ({total_balance_irr/10:,} تومان)"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_balance": 0,
                "accounts": []
            }
    
    def fetch_exchange_rates_interactive(self, currency_pair: str = "USD/IRR") -> dict:
        """Fetch current exchange rates"""
        return fetch_exchange_rates.invoke({"currency_pair": currency_pair})
    
    def convert_currency_interactive(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        rate_type: str = "parallel"
    ) -> dict:
        """Convert between currencies"""
        return convert_currency.invoke({
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate_type": rate_type
        })
    
    def calculate_metrics_interactive(self, user_id: str, date_from: str, date_to: str) -> dict:
        """Calculate financial metrics"""
        return calculate_financial_metrics.invoke({
            "user_id": user_id,
            "date_from": date_from,
            "date_to": date_to
        })
    
    def calculate_burn_rate_interactive(self, user_id: str, days: int = 30) -> dict:
        """Calculate burn rate"""
        return calculate_burn_rate.invoke({"user_id": user_id, "days": days})
    
    def project_cash_flow_interactive(self, user_id: str, days: int = 90) -> dict:
        """Project cash flow"""
        return project_cash_flow.invoke({"user_id": user_id, "days": days})
    
    def create_account_interactive(
        self,
        user_id: str,
        name: str,
        account_type: str,
        currency: str = "IRR",
        initial_balance: float = 0.0
    ) -> dict:
        """Create a new account"""
        return create_account.invoke({
            "user_id": user_id,
            "name": name,
            "account_type": account_type,
            "currency": currency,
            "initial_balance": initial_balance
        })
    
    def list_accounts_interactive(self, user_id: str) -> dict:
        """List all accounts"""
        return list_accounts.invoke({"user_id": user_id})


"""
Exchange Rate Tools
Fetches and manages currency exchange rates for Iranian businesses
"""
from typing import Dict, Any, Optional
from langchain.tools import tool
from datetime import datetime, timedelta
import requests

# Optional import for web scraping
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None

import json


# In-memory cache for exchange rates
_rate_cache = {}
_cache_ttl = 3600  # 1 hour


@tool
def fetch_exchange_rates(currency_pair: str = "USD/IRR") -> dict:
    """
    Fetch current exchange rates from multiple Iranian sources
    
    Args:
        currency_pair: Currency pair (e.g., USD/IRR, EUR/IRR)
        
    Returns:
        Exchange rates (official, parallel, nima) with timestamp
    """
    try:
        # Check cache first
        cache_key = f"{currency_pair}_{datetime.now().date()}"
        if cache_key in _rate_cache:
            cached_data = _rate_cache[cache_key]
            cache_time = cached_data.get('timestamp', '')
            if cache_time:
                cache_dt = datetime.fromisoformat(cache_time)
                if (datetime.now() - cache_dt).seconds < _cache_ttl:
                    return {
                        **cached_data,
                        "cached": True,
                        "message": "نرخ‌ها از حافظه موقت بازیابی شد"
                    }
        
        # Parse currency pair
        from_currency, to_currency = currency_pair.split('/')
        
        # Fetch rates from sources
        rates = {
            "success": True,
            "currency_pair": currency_pair,
            "from": from_currency,
            "to": to_currency,
            "timestamp": datetime.now().isoformat(),
            "rates": {}
        }
        
        # Try fetching from Bonbast (parallel market)
        try:
            bonbast_rate = _fetch_from_bonbast(from_currency)
            if bonbast_rate:
                rates["rates"]["parallel"] = bonbast_rate
        except Exception as e:
            print(f"Bonbast fetch error: {e}")
        
        # Use mock rates if fetching fails (for development)
        if not rates["rates"]:
            rates["rates"] = _get_mock_rates(from_currency)
            rates["message"] = "⚠️ استفاده از نرخ‌های نمونه (برای توسعه)"
        else:
            rates["message"] = "✅ نرخ‌ها با موفقیت دریافت شد"
        
        # Cache the result
        _rate_cache[cache_key] = rates
        
        return rates
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در دریافت نرخ ارز: {str(e)}",
            "rates": _get_mock_rates(from_currency)  # Fallback to mock
        }


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
    rate_type: str = "parallel"
) -> dict:
    """
    Convert amount from one currency to another
    
    Args:
        amount: Amount to convert
        from_currency: Source currency (e.g., USD)
        to_currency: Target currency (e.g., IRR)
        rate_type: Type of rate to use (official, parallel, nima)
        
    Returns:
        Converted amount with exchange rate used
    """
    try:
        if from_currency == to_currency:
            return {
                "success": True,
                "amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": 1.0,
                "message": "ارزهای مبدأ و مقصد یکسان هستند"
            }
        
        # Special handling for IRR/IRT (Rial/Toman)
        if from_currency == "IRR" and to_currency == "IRT":
            return {
                "success": True,
                "amount": amount / 10,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": 0.1,
                "message": f"✅ {amount:,} ریال = {amount/10:,} تومان"
            }
        elif from_currency == "IRT" and to_currency == "IRR":
            return {
                "success": True,
                "amount": amount * 10,
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": 10.0,
                "message": f"✅ {amount:,} تومان = {amount*10:,} ریال"
            }
        
        # Fetch exchange rate
        currency_pair = f"{from_currency}/{to_currency}"
        rates_result = fetch_exchange_rates.invoke({"currency_pair": currency_pair})
        
        if not rates_result.get("success"):
            return {
                "success": False,
                "error": "نرخ ارز در دسترس نیست"
            }
        
        rate = rates_result["rates"].get(rate_type)
        if not rate:
            # Try other rate types
            rate = (rates_result["rates"].get("parallel") or 
                   rates_result["rates"].get("official") or
                   rates_result["rates"].get("nima"))
        
        if not rate:
            return {
                "success": False,
                "error": "نرخ ارز یافت نشد"
            }
        
        converted_amount = amount * rate
        
        return {
            "success": True,
            "amount": converted_amount,
            "original_amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "rate_type": rate_type,
            "message": f"✅ {amount:,} {from_currency} = {converted_amount:,} {to_currency}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در تبدیل ارز: {str(e)}"
        }


def _fetch_from_bonbast(currency: str) -> Optional[float]:
    """
    Fetch rate from Bonbast.com (parallel market)
    Note: This is a simplified version. In production, use their API or scraping with proper error handling
    """
    # Simplified - return None to fallback to mock
    # In production, implement proper web scraping or API calls
    return None


def _get_mock_rates(currency: str) -> dict:
    """Get mock rates for development/fallback"""
    mock_rates = {
        "USD": {
            "official": 42000,
            "parallel": 55000,
            "nima": 45000
        },
        "EUR": {
            "official": 45000,
            "parallel": 60000,
            "nima": 48000
        },
        "GBP": {
            "official": 50000,
            "parallel": 68000,
            "nima": 53000
        },
        "AED": {
            "official": 11500,
            "parallel": 15000,
            "nima": 12500
        }
    }
    
    return mock_rates.get(currency, {"parallel": 50000})


# Export tools
EXCHANGE_RATE_TOOLS = [
    fetch_exchange_rates,
    convert_currency
]


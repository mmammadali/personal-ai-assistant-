"""
Comprehensive Finance Agent Testing Script
Tests all major functionality of the Finance Assistant
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"
SESSION = requests.Session()

# Test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

def test(name, func):
    """Run a test and record results"""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print('='*60)
    try:
        result = func()
        if result.get("success", False):
            results["passed"].append(name)
            print(f"✅ PASSED: {name}")
            return result
        else:
            results["failed"].append(name)
            print(f"❌ FAILED: {name}")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return result
    except Exception as e:
        results["failed"].append(name)
        print(f"❌ FAILED: {name}")
        print(f"   Exception: {str(e)}")
        return {"success": False, "error": str(e)}

def test_1_health_check():
    """Test 1: Server Health Check"""
    response = SESSION.get(f"{BASE_URL}/health")
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "data": response.json()
    }

def test_2_finance_page_load():
    """Test 2: Finance Page Loads"""
    response = SESSION.get(f"{BASE_URL}/finance")
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "has_finance_content": "مدیر مالی" in response.text or "Finance" in response.text
    }

def test_3_finance_chat_basic():
    """Test 3: Basic Finance Chat"""
    response = SESSION.post(
        f"{BASE_URL}/api/finance/chat",
        json={"message": "سلام"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    return {
        "success": response.status_code == 200 and "response" in data,
        "status": response.status_code,
        "response": data.get("response", "")[:100] if "response" in data else None
    }

def test_4_finance_chat_balance_query():
    """Test 4: Balance Query"""
    response = SESSION.post(
        f"{BASE_URL}/api/finance/chat",
        json={"message": "موجودی من چقدر است؟"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "response": data.get("response", "")[:200] if "response" in data else None
    }

def test_5_finance_chat_transaction():
    """Test 5: Transaction Creation Query"""
    response = SESSION.post(
        f"{BASE_URL}/api/finance/chat",
        json={"message": "می‌خواهم یک هزینه ثبت کنم"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "response": data.get("response", "")[:200] if "response" in data else None
    }

def test_6_finance_chat_exchange_rate():
    """Test 6: Exchange Rate Query"""
    response = SESSION.post(
        f"{BASE_URL}/api/finance/chat",
        json={"message": "نرخ دلار چقدر است؟"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "response": data.get("response", "")[:200] if "response" in data else None
    }

def test_7_finance_chat_report():
    """Test 7: Report Generation Query"""
    response = SESSION.post(
        f"{BASE_URL}/api/finance/chat",
        json={"message": "یک گزارش سود و زیان بده"},
        headers={"Content-Type": "application/json"}
    )
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "response": data.get("response", "")[:200] if "response" in data else None
    }

def test_8_get_balance_api():
    """Test 8: Balance API Endpoint"""
    response = SESSION.get(f"{BASE_URL}/api/finance/balance")
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "data": data
    }

def test_9_get_transactions_api():
    """Test 9: Transactions API Endpoint"""
    response = SESSION.get(f"{BASE_URL}/api/finance/transactions")
    data = response.json()
    return {
        "success": response.status_code == 200,
        "status": response.status_code,
        "data": data
    }

def test_10_clear_session():
    """Test 10: Clear Session"""
    response = SESSION.post(f"{BASE_URL}/api/finance/clear")
    data = response.json()
    return {
        "success": response.status_code == 200 and data.get("success", False),
        "status": response.status_code,
        "data": data
    }

def test_11_direct_agent_test():
    """Test 11: Direct Finance Agent Test (Python)"""
    try:
        from finance_agent import FinanceAgent
        from config import OPENAI_API_KEY
        
        if not OPENAI_API_KEY:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not configured"
            }
        
        agent = FinanceAgent(
            openai_api_key=OPENAI_API_KEY,
            model="gpt-4o"
        )
        
        # Test initialization
        agent.init_user("test_user_123", name="کاربر تست")
        
        # Test chat
        response = agent.chat("سلام", thread_id="test_thread", user_id="test_user_123")
        
        return {
            "success": True,
            "agent_initialized": True,
            "chat_response": response[:100] if response else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_12_database_test():
    """Test 12: Database Functionality"""
    try:
        from finance.database import FinanceDatabase
        
        db = FinanceDatabase("test_finance.db")
        
        # Test connection
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM finance_categories")
            count = cursor.fetchone()[0]
        
        return {
            "success": True,
            "database_accessible": True,
            "categories_count": count
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_13_transaction_tools():
    """Test 13: Transaction Tools Import"""
    try:
        from finance.tools.database_tools import (
            create_transaction,
            search_transactions,
            TRANSACTION_TOOLS
        )
        return {
            "success": True,
            "tools_imported": True,
            "tool_count": len(TRANSACTION_TOOLS)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_14_ocr_tools():
    """Test 14: OCR Tools Import"""
    try:
        from finance.tools.ocr_tools import (
            check_image_quality,
            extract_receipt_data,
            OCR_TOOLS
        )
        return {
            "success": True,
            "ocr_tools_imported": True,
            "tool_count": len(OCR_TOOLS)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def test_15_exchange_rate_tools():
    """Test 15: Exchange Rate Tools"""
    try:
        from finance.tools.exchange_rate_tools import (
            fetch_exchange_rates,
            convert_currency
        )
        
        # Test with mock data
        result = fetch_exchange_rates.invoke({"currency_pair": "USD/IRR"})
        
        return {
            "success": result.get("success", False),
            "tools_working": True,
            "has_rates": "rates" in result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def generate_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
    print("="*60)
    print(f"\nTotal Tests: {len(results['passed']) + len(results['failed'])}")
    print(f"✅ Passed: {len(results['passed'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⚠️  Warnings: {len(results['warnings'])}")
    
    print("\n" + "-"*60)
    print("PASSED TESTS:")
    print("-"*60)
    for test_name in results['passed']:
        print(f"  ✅ {test_name}")
    
    if results['failed']:
        print("\n" + "-"*60)
        print("FAILED TESTS:")
        print("-"*60)
        for test_name in results['failed']:
            print(f"  ❌ {test_name}")
    
    if results['warnings']:
        print("\n" + "-"*60)
        print("WARNINGS:")
        print("-"*60)
        for warning in results['warnings']:
            print(f"  ⚠️  {warning}")
    
    success_rate = (len(results['passed']) / (len(results['passed']) + len(results['failed']))) * 100 if (len(results['passed']) + len(results['failed'])) > 0 else 0
    print(f"\n{'='*60}")
    print(f"SUCCESS RATE: {success_rate:.1f}%")
    print("="*60)
    
    return {
        "total": len(results['passed']) + len(results['failed']),
        "passed": len(results['passed']),
        "failed": len(results['failed']),
        "warnings": len(results['warnings']),
        "success_rate": success_rate
    }

if __name__ == "__main__":
    print("="*60)
    print("FINANCE AGENT COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Testing at: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test("1. Server Health Check", test_1_health_check)
    test("2. Finance Page Loads", test_2_finance_page_load)
    test("3. Basic Finance Chat", test_3_finance_chat_basic)
    test("4. Balance Query", test_4_finance_chat_balance_query)
    test("5. Transaction Query", test_5_finance_chat_transaction)
    test("6. Exchange Rate Query", test_6_finance_chat_exchange_rate)
    test("7. Report Query", test_7_finance_chat_report)
    test("8. Balance API", test_8_get_balance_api)
    test("9. Transactions API", test_9_get_transactions_api)
    test("10. Clear Session", test_10_clear_session)
    test("11. Direct Agent Test", test_11_direct_agent_test)
    test("12. Database Test", test_12_database_test)
    test("13. Transaction Tools", test_13_transaction_tools)
    test("14. OCR Tools", test_14_ocr_tools)
    test("15. Exchange Rate Tools", test_15_exchange_rate_tools)
    
    # Generate report
    report = generate_report()
    
    # Save report to file
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": report
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Detailed report saved to: test_report.json")











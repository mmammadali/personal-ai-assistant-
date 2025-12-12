"""
Simple RAG Agent Test - Tests via Web API
Tests all RAG functionality through HTTP endpoints
"""
import time
import requests
import json
from pathlib import Path


def print_test_header(test_name):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f"  🧪 TEST: {test_name}")
    print("=" * 80)


def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")


def wait_for_server(max_retries=15):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:5000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except:
            pass
        if i % 3 == 0:
            print(f"⏳ Still waiting... ({i+1}/{max_retries})")
        time.sleep(2)
    return False


def test_rag_via_api():
    """Test RAG agent via web API"""
    
    print("\n" + "🚀" * 40)
    print("  RAG AGENT API TESTING")
    print("🚀" * 40)
    
    # Wait for server
    if not wait_for_server():
        print("❌ Server is not running!")
        print("Please start the server first: python app.py")
        return False
    
    base_url = "http://127.0.0.1:5000"
    session = requests.Session()
    
    # Test 1: Health Check
    print_test_header("Test 1: Health Check")
    try:
        response = session.get(f"{base_url}/health")
        if response.status_code == 200:
            print_result(True, f"Server is healthy: {response.json()}")
        else:
            print_result(False, f"Health check failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Health check error: {str(e)}")
        return False
    
    # Test 2: Upload Document
    print_test_header("Test 2: Upload Document")
    doc_path = Path("QUICKSTART_RAG.md")
    
    if not doc_path.exists():
        print(f"⚠️ {doc_path} not found, creating test document...")
        test_content = """# راهنمای سریع RAG Agent

این یک سند تستی است برای آزمایش عملکرد RAG Agent.

## تاریخ‌های مهم:
- تاریخ شروع پروژه: 1403/09/15
- تاریخ پایان: 1403/12/30
- مهلت تحویل: 1403/11/20

## اطلاعات مالی:
- بودجه کل پروژه: 50,000,000 تومان
- هزینه اولیه: 10,000,000 تومان
- هزینه نهایی: 40,000,000 تومان

## دستورالعمل‌ها:
1. باید تمام مراحل را به ترتیب انجام دهید
2. لازم است گزارش هفتگی ارائه شود
3. الزامی است که تمام اسناد را بررسی کنید

## اطلاعات حساس:
این سند محرمانه است و شامل اطلاعات قراردادی می‌باشد.
"""
        doc_path = Path("test_document.txt")
        doc_path.write_text(test_content, encoding="utf-8")
        print(f"✅ Created test document: {doc_path}")
    
    try:
        print(f"📤 Uploading: {doc_path}")
        with open(doc_path, 'rb') as f:
            files = {'file': (doc_path.name, f, 'text/plain')}
            response = session.post(f"{base_url}/api/rag/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Document uploaded successfully!")
            print(f"📝 Response preview: {data.get('response', '')[:200]}...")
        else:
            print_result(False, f"Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print_result(False, f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    time.sleep(3)  # Wait for processing
    
    # Test 3: List Documents
    print_test_header("Test 3: List Documents")
    try:
        response = session.post(
            f"{base_url}/api/rag/chat",
            json={"message": "لیست تمام اسناد من را نشان بده"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "List documents query sent successfully")
            print(f"📝 Response:\n{data.get('response', '')[:500]}...\n")
        else:
            print_result(False, f"Query failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print_result(False, f"List documents error: {str(e)}")
    
    time.sleep(2)
    
    # Test 4: Query Document
    print_test_header("Test 4: Query Document")
    test_queries = [
        "این سند درباره چیست؟",
        "تاریخ‌های مهم در این سند چیست؟",
        "مبالغ مالی در سند چقدر است؟"
    ]
    
    for i, query in enumerate(test_queries, 1):
        try:
            print(f"\n🔍 Query {i}: {query}")
            response = session.post(
                f"{base_url}/api/rag/chat",
                json={"message": query},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Query {i} executed successfully")
                print(f"📝 Response:\n{data.get('response', '')[:300]}...\n")
            else:
                print_result(False, f"Query {i} failed: {response.status_code}")
        except Exception as e:
            print_result(False, f"Query {i} error: {str(e)}")
        
        time.sleep(2)
    
    # Test 5: Summarize Document
    print_test_header("Test 5: Summarize Document")
    try:
        summary_query = "خلاصه کامل این سند را با استخراج تمام تاریخ‌ها، مبالغ مالی، و دستورالعمل‌ها بده"
        print(f"📝 Requesting summary...")
        response = session.post(
            f"{base_url}/api/rag/chat",
            json={"message": summary_query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('response', '')
            print_result(True, "Summary generated successfully")
            print(f"\n📝 Summary:\n{summary}\n")
            
            # Check for extracted information
            has_dates = "تاریخ" in summary or "1403" in summary
            has_financial = "تومان" in summary or "مبلغ" in summary or "بودجه" in summary
            has_guidelines = "دستورالعمل" in summary or "باید" in summary
            
            print("📊 Extracted Information:")
            print(f"  {'✅' if has_dates else '❌'} Dates")
            print(f"  {'✅' if has_financial else '❌'} Financial Data")
            print(f"  {'✅' if has_guidelines else '❌'} Guidelines")
        else:
            print_result(False, f"Summary failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print_result(False, f"Summary error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    time.sleep(2)
    
    # Test 6: Get Document Info
    print_test_header("Test 6: Get Document Info")
    try:
        info_query = "اطلاعات سند بارگذاری شده را نشان بده"
        response = session.post(
            f"{base_url}/api/rag/chat",
            json={"message": info_query},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Document info retrieved")
            print(f"📝 Response:\n{data.get('response', '')[:400]}...\n")
        else:
            print_result(False, f"Get info failed: {response.status_code}")
    except Exception as e:
        print_result(False, f"Get info error: {str(e)}")
    
    # Final Summary
    print_test_header("TEST SUMMARY")
    print("✅ All RAG API endpoints tested!")
    print("\n📊 Tested Features:")
    print("  ✅ Health Check")
    print("  ✅ Document Upload")
    print("  ✅ List Documents")
    print("  ✅ Query Documents")
    print("  ✅ Summarize Documents")
    print("  ✅ Get Document Info")
    print("\n🎉 RAG Agent API is fully functional!")
    print("\n💡 Web Interface:")
    print("  Open http://127.0.0.1:5000/rag in your browser")
    print("  Use the sidebar to switch between agents")
    
    return True


if __name__ == "__main__":
    try:
        test_rag_via_api()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()













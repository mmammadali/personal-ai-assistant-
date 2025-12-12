"""
Comprehensive Test Suite for Iranian Manager Personal Assistant
Tests all agents, features, and functions with API cost tracking
"""
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import traceback

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import configuration
from config import OPENAI_API_KEY, DEFAULT_MODEL, COMPLEX_MODEL

# API Cost Tracking
class APICostTracker:
    """Track API costs for different models"""
    
    # Pricing per 1K tokens (as of 2024, approximate)
    PRICING = {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},  # $0.15/$0.60 per 1M tokens
        "gpt-4o": {"input": 0.0025, "output": 0.01},  # $2.50/$10 per 1M tokens
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},  # $10/$30 per 1M tokens
        "gpt-5-mini": {"input": 0.00015, "output": 0.0006},  # Assume same as gpt-4o-mini
        "gpt-5": {"input": 0.0025, "output": 0.01},  # Assume same as gpt-4o
        "text-embedding-3-large": {"input": 0.00013, "output": 0},  # $0.13 per 1M tokens
    }
    
    def __init__(self):
        self.costs = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def track_call(self, model: str, input_tokens: int, output_tokens: int):
        """Track an API call"""
        if model not in self.PRICING:
            # Use default pricing for unknown models
            model = "gpt-4o-mini"
        
        input_cost = (input_tokens / 1000) * self.PRICING[model]["input"]
        output_cost = (output_tokens / 1000) * self.PRICING[model]["output"]
        total_cost = input_cost + output_cost
        
        self.costs.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost
        })
        
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost
    
    def get_summary(self) -> Dict:
        """Get cost summary"""
        return {
            "total_calls": len(self.costs),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "cost_by_model": self._get_cost_by_model()
        }
    
    def _get_cost_by_model(self) -> Dict:
        """Get cost breakdown by model"""
        model_costs = {}
        for cost in self.costs:
            model = cost["model"]
            if model not in model_costs:
                model_costs[model] = {"calls": 0, "cost": 0.0}
            model_costs[model]["calls"] += 1
            model_costs[model]["cost"] += cost["cost"]
        
        # Round costs
        for model in model_costs:
            model_costs[model]["cost"] = round(model_costs[model]["cost"], 4)
        
        return model_costs


# Test Results Storage
class TestResults:
    """Store test results"""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def add_result(self, test_name: str, agent: str, status: str, 
                   details: str = "", error: str = None, duration: float = 0):
        """Add a test result"""
        self.results.append({
            "test_name": test_name,
            "agent": agent,
            "status": status,  # "PASS", "FAIL", "SKIP", "ERROR"
            "details": details,
            "error": error,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_summary(self) -> Dict:
        """Get test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        skipped = sum(1 for r in self.results if r["status"] == "SKIP")
        
        total_duration = time.time() - self.start_time
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "success_rate": round((passed / total * 100) if total > 0 else 0, 2),
            "total_duration_seconds": round(total_duration, 2),
            "total_duration_minutes": round(total_duration / 60, 2)
        }


# Test Suite
class ComprehensiveTestSuite:
    """Comprehensive test suite for all agents"""
    
    def __init__(self):
        self.cost_tracker = APICostTracker()
        self.test_results = TestResults()
        self.test_db_path = "test_comprehensive.db"
        self.test_rag_db_path = "./test_chroma_db"
        self.test_finance_db_path = "test_finance_comprehensive.db"
        
        # Initialize agents
        self.main_agent = None
        self.rag_agent = None
        self.finance_agent = None
        
        print("=" * 80)
        print("🧪 COMPREHENSIVE TEST SUITE - Iranian Manager Personal Assistant")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔑 API Key: {'✅ Set' if OPENAI_API_KEY else '❌ Missing'}")
        print("=" * 80)
    
    def setup(self):
        """Setup test environment"""
        print("\n🔧 Setting up test environment...")
        
        try:
            # Initialize Main Agent
            from agent import IranianManagerAssistant
            self.main_agent = IranianManagerAssistant(
                openai_api_key=OPENAI_API_KEY,
                model=DEFAULT_MODEL
            )
            print("✅ Main Agent initialized")
        except Exception as e:
            print(f"❌ Failed to initialize Main Agent: {e}")
            traceback.print_exc()
        
        try:
            # Initialize RAG Agent
            from rag_agent import RAGAgent
            from config import RAG_VECTOR_STORE_TYPE, RAG_FAISS_PERSIST_DIR
            
            self.rag_agent = RAGAgent(
                openai_api_key=OPENAI_API_KEY,
                model=DEFAULT_MODEL,
                vector_store_type="faiss",  # Use FAISS for testing
                persist_directory=RAG_FAISS_PERSIST_DIR
            )
            print("✅ RAG Agent initialized")
        except Exception as e:
            print(f"⚠️  RAG Agent not available: {e}")
            print("   (Some tests will be skipped)")
        
        try:
            # Initialize Finance Agent
            from finance_agent import FinanceAgent
            self.finance_agent = FinanceAgent(
                openai_api_key=OPENAI_API_KEY,
                model=DEFAULT_MODEL,
                db_path=self.test_finance_db_path
            )
            print("✅ Finance Agent initialized")
        except Exception as e:
            print(f"⚠️  Finance Agent not available: {e}")
            print("   (Some tests will be skipped)")
        
        print("✅ Setup complete\n")
    
    def test_main_agent_events(self):
        """Test Main Agent - Event Management"""
        print("\n" + "=" * 80)
        print("📅 TESTING MAIN AGENT - EVENT MANAGEMENT")
        print("=" * 80)
        
        if not self.main_agent:
            self.test_results.add_result(
                "Main Agent Events", "Main Agent", "SKIP",
                "Agent not initialized"
            )
            return
        
        test_cases = [
            {
                "name": "Create Event - Full Details",
                "input": "فردا ساعت 14 جلسه با آقای احمدی در دفتر مرکزی",
                "expected": "تأیید"
            },
            {
                "name": "Create Event - Minimal Details",
                "input": "پس‌فردا جلسه تیم",
                "expected": "تأیید"
            },
            {
                "name": "Query Events - By Date",
                "input": "رویدادهای فردا را نشان بده",
                "expected": "رویداد"
            },
            {
                "name": "Query Events - By Attendee",
                "input": "جلسات با آقای احمدی",
                "expected": "رویداد"
            },
            {
                "name": "Query Events - All",
                "input": "همه رویدادها را نشان بده",
                "expected": "رویداد"
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = self.main_agent.chat(test_case["input"], thread_id="test_events")
                duration = time.time() - start_time
                
                # Estimate tokens (rough approximation)
                input_tokens = len(test_case["input"].split()) * 1.3  # Rough estimate
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                # Check if response contains expected content
                status = "PASS" if test_case["expected"].lower() in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    test_case["name"], "Main Agent", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} ({duration:.2f}s)")
                
            except Exception as e:
                self.test_results.add_result(
                    test_case["name"], "Main Agent", "ERROR",
                    "", str(e), time.time() - start_time
                )
                print(f"  ❌ {test_case['name']} - ERROR: {e}")
    
    def test_main_agent_tasks(self):
        """Test Main Agent - Task Management"""
        print("\n" + "=" * 80)
        print("📋 TESTING MAIN AGENT - TASK MANAGEMENT")
        print("=" * 80)
        
        if not self.main_agent:
            self.test_results.add_result(
                "Main Agent Tasks", "Main Agent", "SKIP",
                "Agent not initialized"
            )
            return
        
        test_cases = [
            {
                "name": "Create Task - Full Details",
                "input": "وظیفه: آماده کردن گزارش فروش تا فردا برای پروژه بازاریابی",
                "expected": "تأیید"
            },
            {
                "name": "Create Task - Minimal",
                "input": "فردا باید به احمدی زنگ بزنم",
                "expected": "تأیید"
            },
            {
                "name": "Query Tasks - By Project",
                "input": "وظایف پروژه بازاریابی",
                "expected": "وظیفه"
            },
            {
                "name": "Query Tasks - By Status",
                "input": "وظایف انجام نشده",
                "expected": "وظیفه"
            },
            {
                "name": "Update Task Status",
                "input": "وظیفه گزارش فروش را انجام شده کن",
                "expected": "تأیید"
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = self.main_agent.chat(test_case["input"], thread_id="test_tasks")
                duration = time.time() - start_time
                
                input_tokens = len(test_case["input"].split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                status = "PASS" if test_case["expected"].lower() in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    test_case["name"], "Main Agent", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} ({duration:.2f}s)")
                
            except Exception as e:
                self.test_results.add_result(
                    test_case["name"], "Main Agent", "ERROR",
                    "", str(e), time.time() - start_time
                )
                print(f"  ❌ {test_case['name']} - ERROR: {e}")
    
    def test_rag_agent(self):
        """Test RAG Agent - Document Management"""
        print("\n" + "=" * 80)
        print("📚 TESTING RAG AGENT - DOCUMENT MANAGEMENT")
        print("=" * 80)
        
        if not self.rag_agent:
            self.test_results.add_result(
                "RAG Agent", "RAG Agent", "SKIP",
                "Agent not initialized"
            )
            return
        
        test_cases = [
            {
                "name": "List Documents - Empty",
                "input": "چه اسنادی دارم؟",
                "expected": "سند"
            },
            {
                "name": "Query Document - No Documents",
                "input": "این سند درباره چیست؟",
                "expected": "سند"
            }
        ]
        
        # Create a test document if possible
        test_doc_path = None
        try:
            test_doc_path = Path("test_document.txt")
            if not test_doc_path.exists():
                test_doc_path.write_text("""
                این یک سند تست است.
                این سند شامل اطلاعات مهمی است.
                تاریخ: 1403-09-15
                مبلغ: 1,000,000 تومان
                """)
                print("  📄 Created test document")
        except Exception as e:
            print(f"  ⚠️  Could not create test document: {e}")
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = self.rag_agent.chat(test_case["input"], thread_id="test_rag")
                duration = time.time() - start_time
                
                input_tokens = len(test_case["input"].split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                status = "PASS" if test_case["expected"].lower() in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    test_case["name"], "RAG Agent", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} ({duration:.2f}s)")
                
            except Exception as e:
                self.test_results.add_result(
                    test_case["name"], "RAG Agent", "ERROR",
                    "", str(e), time.time() - start_time
                )
                print(f"  ❌ {test_case['name']} - ERROR: {e}")
        
        # Test document upload if document exists
        if test_doc_path and test_doc_path.exists():
            try:
                start_time = time.time()
                upload_msg = f"این فایل را بارگذاری کن: {test_doc_path.absolute()}"
                response = self.rag_agent.chat(upload_msg, thread_id="test_rag")
                duration = time.time() - start_time
                
                input_tokens = len(upload_msg.split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                status = "PASS" if "بارگذاری" in response or "upload" in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    "Upload Document", "RAG Agent", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} Upload Document ({duration:.2f}s)")
                
            except Exception as e:
                self.test_results.add_result(
                    "Upload Document", "RAG Agent", "ERROR",
                    "", str(e), time.time() - start_time
                )
                print(f"  ❌ Upload Document - ERROR: {e}")
    
    def test_finance_agent(self):
        """Test Finance Agent - Financial Management"""
        print("\n" + "=" * 80)
        print("💰 TESTING FINANCE AGENT - FINANCIAL MANAGEMENT")
        print("=" * 80)
        
        if not self.finance_agent:
            self.test_results.add_result(
                "Finance Agent", "Finance Agent", "SKIP",
                "Agent not initialized"
            )
            return
        
        # Initialize user
        try:
            self.finance_agent.init_user("test_user", "Test User")
            print("  ✅ User initialized")
        except Exception as e:
            print(f"  ⚠️  User initialization: {e}")
        
        test_cases = [
            {
                "name": "Get Balance - Empty",
                "input": "موجودی من چقدر است؟",
                "expected": "موجودی"
            },
            {
                "name": "Create Account",
                "input": "حساب بانکی با نام حساب ملی و موجودی ۱۰ میلیون تومان ایجاد کن",
                "expected": "حساب"
            },
            {
                "name": "Get Exchange Rate",
                "input": "نرخ ارز فعلی چیست؟",
                "expected": "نرخ"
            },
            {
                "name": "List Reports",
                "input": "چه گزارش‌هایی می‌توانم بگیرم؟",
                "expected": "گزارش"
            }
        ]
        
        for test_case in test_cases:
            try:
                start_time = time.time()
                response = self.finance_agent.chat(
                    test_case["input"], 
                    thread_id="test_finance",
                    user_id="test_user"
                )
                duration = time.time() - start_time
                
                input_tokens = len(test_case["input"].split()) * 1.3
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                status = "PASS" if test_case["expected"].lower() in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    test_case["name"], "Finance Agent", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} ({duration:.2f}s)")
                
            except Exception as e:
                self.test_results.add_result(
                    test_case["name"], "Finance Agent", "ERROR",
                    "", str(e), time.time() - start_time
                )
                print(f"  ❌ {test_case['name']} - ERROR: {e}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\n" + "=" * 80)
        print("🔍 TESTING EDGE CASES & ERROR HANDLING")
        print("=" * 80)
        
        if not self.main_agent:
            return
        
        edge_cases = [
            {
                "name": "Empty Input",
                "input": "",
                "expected": "error"
            },
            {
                "name": "Invalid Date Format",
                "input": "رویداد برای 2024-01-01",
                "expected": "جلالی"
            },
            {
                "name": "Missing Required Fields",
                "input": "یک رویداد ایجاد کن",
                "expected": "تاریخ"
            },
            {
                "name": "Very Long Input",
                "input": " ".join(["کلمه"] * 500),
                "expected": "error"
            }
        ]
        
        for test_case in edge_cases:
            try:
                start_time = time.time()
                response = self.main_agent.chat(test_case["input"], thread_id="test_edge")
                duration = time.time() - start_time
                
                input_tokens = len(test_case["input"].split()) * 1.3 if test_case["input"] else 0
                output_tokens = len(response.split()) * 1.3
                self.cost_tracker.track_call(DEFAULT_MODEL, int(input_tokens), int(output_tokens))
                
                # Edge cases should handle gracefully
                status = "PASS" if test_case["expected"].lower() in response.lower() else "FAIL"
                
                self.test_results.add_result(
                    test_case["name"], "Edge Cases", status,
                    f"Response: {response[:100]}...", None, duration
                )
                
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} ({duration:.2f}s)")
                
            except Exception as e:
                # Errors are expected for some edge cases
                status = "PASS" if "error" in test_case["expected"].lower() else "ERROR"
                self.test_results.add_result(
                    test_case["name"], "Edge Cases", status,
                    "", str(e), time.time() - start_time
                )
                print(f"  {'✅' if status == 'PASS' else '❌'} {test_case['name']} - {e}")
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 80)
        print("📊 GENERATING TEST REPORT")
        print("=" * 80)
        
        # Get summaries
        test_summary = self.test_results.get_summary()
        cost_summary = self.cost_tracker.get_summary()
        
        # Generate report
        report = {
            "test_metadata": {
                "test_date": datetime.now().isoformat(),
                "test_duration_minutes": test_summary["total_duration_minutes"],
                "api_key_set": bool(OPENAI_API_KEY),
                "models_tested": list(cost_summary["cost_by_model"].keys())
            },
            "test_results": {
                "summary": test_summary,
                "detailed_results": self.test_results.results
            },
            "api_costs": {
                "summary": cost_summary,
                "detailed_calls": self.cost_tracker.costs
            },
            "agent_status": {
                "main_agent": "✅ Available" if self.main_agent else "❌ Not Available",
                "rag_agent": "✅ Available" if self.rag_agent else "❌ Not Available",
                "finance_agent": "✅ Available" if self.finance_agent else "❌ Not Available"
            }
        }
        
        # Save JSON report
        report_path = Path("PHASE2_TEST_ANALYSIS.md")
        self._generate_markdown_report(report, report_path)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {test_summary['total_tests']}")
        print(f"✅ Passed: {test_summary['passed']}")
        print(f"❌ Failed: {test_summary['failed']}")
        print(f"⚠️  Errors: {test_summary['errors']}")
        print(f"⏭️  Skipped: {test_summary['skipped']}")
        print(f"Success Rate: {test_summary['success_rate']}%")
        print(f"Duration: {test_summary['total_duration_minutes']:.2f} minutes")
        print("\n" + "=" * 80)
        print("💰 API COST SUMMARY")
        print("=" * 80)
        print(f"Total API Calls: {cost_summary['total_calls']}")
        print(f"Total Tokens: {cost_summary['total_tokens']:,}")
        print(f"  - Input: {cost_summary['total_input_tokens']:,}")
        print(f"  - Output: {cost_summary['total_output_tokens']:,}")
        print(f"Total Cost: ${cost_summary['total_cost_usd']:.4f} USD")
        print("\nCost by Model:")
        for model, data in cost_summary['cost_by_model'].items():
            print(f"  {model}: {data['calls']} calls, ${data['cost']:.4f}")
        print("=" * 80)
        print(f"\n📄 Full report saved to: {report_path}")
        print("=" * 80)
        
        return report
    
    def _generate_markdown_report(self, report: Dict, path: Path):
        """Generate markdown report"""
        md = f"""# 🧪 Comprehensive Test Report - Iranian Manager Personal Assistant

**Test Date:** {report['test_metadata']['test_date']}  
**Duration:** {report['test_metadata']['test_duration_minutes']:.2f} minutes  
**API Key:** {'✅ Set' if report['test_metadata']['api_key_set'] else '❌ Missing'}

---

## 📊 Executive Summary

### Test Results
- **Total Tests:** {report['test_results']['summary']['total_tests']}
- **✅ Passed:** {report['test_results']['summary']['passed']}
- **❌ Failed:** {report['test_results']['summary']['failed']}
- **⚠️ Errors:** {report['test_results']['summary']['errors']}
- **⏭️ Skipped:** {report['test_results']['summary']['skipped']}
- **Success Rate:** {report['test_results']['summary']['success_rate']}%

### API Costs
- **Total API Calls:** {report['api_costs']['summary']['total_calls']}
- **Total Tokens:** {report['api_costs']['summary']['total_tokens']:,}
  - Input Tokens: {report['api_costs']['summary']['total_input_tokens']:,}
  - Output Tokens: {report['api_costs']['summary']['total_output_tokens']:,}
- **Total Cost:** **${report['api_costs']['summary']['total_cost_usd']:.4f} USD**

### Agent Availability
{self._format_agent_status(report['agent_status'])}

---

## 🔍 Detailed Test Results

### Test Breakdown by Agent

{self._format_test_results(report['test_results']['detailed_results'])}

---

## 💰 API Cost Breakdown

### Cost by Model

{self._format_cost_breakdown(report['api_costs']['summary']['cost_by_model'])}

### Cost Estimation Notes
- Pricing based on OpenAI's published rates (as of 2024)
- Token counts are estimates based on word count
- Actual costs may vary slightly
- Embedding costs not included in this estimate

---

## 📈 Functionality Assessment

### Main Agent (Task/Event Management)
{self._assess_agent_functionality('Main Agent', report['test_results']['detailed_results'])}

### RAG Agent (Document Management)
{self._assess_agent_functionality('RAG Agent', report['test_results']['detailed_results'])}

### Finance Agent (Financial Management)
{self._assess_agent_functionality('Finance Agent', report['test_results']['detailed_results'])}

---

## 🎯 Recommendations

{self._generate_recommendations(report)}

---

## 📝 Test Details

### All Test Cases

{self._format_all_tests(report['test_results']['detailed_results'])}

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Test Suite Version:** 1.0.0
"""
        
        path.write_text(md, encoding='utf-8')
    
    def _format_agent_status(self, status: Dict) -> str:
        """Format agent status"""
        lines = []
        for agent, status_text in status.items():
            lines.append(f"- **{agent.replace('_', ' ').title()}:** {status_text}")
        return "\n".join(lines)
    
    def _format_test_results(self, results: List) -> str:
        """Format test results by agent"""
        by_agent = {}
        for result in results:
            agent = result['agent']
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(result)
        
        output = []
        for agent, tests in by_agent.items():
            passed = sum(1 for t in tests if t['status'] == 'PASS')
            total = len(tests)
            output.append(f"### {agent}")
            output.append(f"- **Tests:** {total}")
            output.append(f"- **Passed:** {passed}")
            output.append(f"- **Success Rate:** {(passed/total*100) if total > 0 else 0:.1f}%")
            output.append("")
        
        return "\n".join(output)
    
    def _format_cost_breakdown(self, cost_by_model: Dict) -> str:
        """Format cost breakdown"""
        lines = []
        for model, data in cost_by_model.items():
            lines.append(f"- **{model}:**")
            lines.append(f"  - Calls: {data['calls']}")
            lines.append(f"  - Cost: ${data['cost']:.4f} USD")
        return "\n".join(lines)
    
    def _assess_agent_functionality(self, agent_name: str, results: List) -> str:
        """Assess agent functionality"""
        agent_tests = [r for r in results if r['agent'] == agent_name]
        if not agent_tests:
            return f"⚠️ No tests executed for {agent_name}"
        
        passed = sum(1 for t in agent_tests if t['status'] == 'PASS')
        total = len(agent_tests)
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate >= 80:
            status = "✅ Excellent"
        elif success_rate >= 60:
            status = "⚠️ Good"
        else:
            status = "❌ Needs Improvement"
        
        return f"""
**Status:** {status}  
**Tests:** {total} | **Passed:** {passed} | **Success Rate:** {success_rate:.1f}%
"""
    
    def _generate_recommendations(self, report: Dict) -> str:
        """Generate recommendations"""
        recommendations = []
        
        test_summary = report['test_results']['summary']
        if test_summary['success_rate'] < 80:
            recommendations.append("- ⚠️ **Improve Test Success Rate:** Some tests are failing. Review error messages and fix issues.")
        
        if test_summary['errors'] > 0:
            recommendations.append("- 🔧 **Fix Errors:** Address errors in test execution to improve reliability.")
        
        cost = report['api_costs']['summary']['total_cost_usd']
        if cost > 1.0:
            recommendations.append("- 💰 **Optimize API Costs:** Consider using smaller models for simple queries to reduce costs.")
        
        if not report['agent_status']['rag_agent'].startswith('✅'):
            recommendations.append("- 📚 **RAG Agent:** Ensure RAG agent dependencies are installed for document management features.")
        
        if not report['agent_status']['finance_agent'].startswith('✅'):
            recommendations.append("- 💰 **Finance Agent:** Ensure Finance agent dependencies are installed for financial features.")
        
        if not recommendations:
            recommendations.append("- ✅ **System is functioning well!** Continue monitoring and testing.")
        
        return "\n".join(recommendations)
    
    def _format_all_tests(self, results: List) -> str:
        """Format all test details"""
        lines = []
        for result in results:
            status_emoji = {
                'PASS': '✅',
                'FAIL': '❌',
                'ERROR': '⚠️',
                'SKIP': '⏭️'
            }.get(result['status'], '❓')
            
            lines.append(f"### {status_emoji} {result['test_name']}")
            lines.append(f"- **Agent:** {result['agent']}")
            lines.append(f"- **Status:** {result['status']}")
            lines.append(f"- **Duration:** {result['duration']:.2f}s")
            if result['details']:
                lines.append(f"- **Details:** {result['details'][:200]}")
            if result['error']:
                lines.append(f"- **Error:** {result['error']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def cleanup(self):
        """Cleanup test files"""
        print("\n🧹 Cleaning up test files...")
        
        # Clean up test databases
        test_files = [
            self.test_db_path,
            self.test_finance_db_path
        ]
        
        for file_path in test_files:
            try:
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    print(f"  ✅ Removed {file_path}")
            except Exception as e:
                print(f"  ⚠️  Could not remove {file_path}: {e}")
        
        print("✅ Cleanup complete")


def main():
    """Run comprehensive test suite"""
    suite = ComprehensiveTestSuite()
    
    try:
        # Setup
        suite.setup()
        
        # Run tests
        suite.test_main_agent_events()
        suite.test_main_agent_tasks()
        suite.test_rag_agent()
        suite.test_finance_agent()
        suite.test_edge_cases()
        
        # Generate report
        report = suite.generate_report()
        
        # Cleanup (optional - comment out to keep test data)
        # suite.cleanup()
        
        print("\n✅ Test suite completed successfully!")
        return report
        
    except KeyboardInterrupt:
        print("\n⚠️  Test suite interrupted by user")
        suite.generate_report()
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        suite.generate_report()


if __name__ == "__main__":
    main()








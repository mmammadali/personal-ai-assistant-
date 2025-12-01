"""
Comprehensive test suite for Iranian Manager Assistant
Tests all functionality with the shortened prompt to ensure effectiveness
"""
import os
import sys
from agent import IranianManagerAssistant
from database import DatabaseManager
from config import OPENAI_API_KEY, DEFAULT_MODEL
import jdatetime
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.tests = []
    
    def add_pass(self, name, message=""):
        self.passed += 1
        self.tests.append(("PASS", name, message))
        print(f"{GREEN}✓ PASS:{END} {name}")
        if message:
            print(f"  → {message}")
    
    def add_fail(self, name, message=""):
        self.failed += 1
        self.tests.append(("FAIL", name, message))
        print(f"{RED}✗ FAIL:{END} {name}")
        if message:
            print(f"  → {message}")
    
    def add_warning(self, name, message=""):
        self.warnings += 1
        self.tests.append(("WARN", name, message))
        print(f"{YELLOW}⚠ WARN:{END} {name}")
        if message:
            print(f"  → {message}")
    
    def summary(self):
        total = self.passed + self.failed + self.warnings
        print("\n" + "="*80)
        print(f"{BOLD}TEST SUMMARY{END}")
        print("="*80)
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{END}")
        print(f"{RED}Failed: {self.failed}{END}")
        print(f"{YELLOW}Warnings: {self.warnings}{END}")
        
        if self.failed == 0:
            print(f"\n{GREEN}{BOLD}🎉 ALL TESTS PASSED! The shortened prompt is fully effective!{END}")
        else:
            print(f"\n{RED}{BOLD}❌ Some tests failed. The shortened prompt may need adjustment.{END}")
        
        return self.failed == 0


def print_section(title):
    print(f"\n{BLUE}{BOLD}{'='*80}{END}")
    print(f"{BLUE}{BOLD}{title}{END}")
    print(f"{BLUE}{BOLD}{'='*80}{END}\n")


def test_agent_response(assistant, test_name, user_input, expected_behavior, thread_id, results):
    """Test a single agent interaction"""
    print(f"\n{BOLD}Test:{END} {test_name}")
    print(f"{BOLD}Input:{END} '{user_input}'")
    
    try:
        response = assistant.chat(user_input, thread_id=thread_id)
        print(f"{BOLD}Response:{END} {response[:200]}...")
        
        # Check expected behavior
        if callable(expected_behavior):
            success, message = expected_behavior(response)
            if success:
                results.add_pass(test_name, message)
                return response, True
            else:
                results.add_fail(test_name, message)
                return response, False
        else:
            # Simple substring check
            if expected_behavior.lower() in response.lower():
                results.add_pass(test_name, f"Found expected: '{expected_behavior}'")
                return response, True
            else:
                results.add_fail(test_name, f"Expected '{expected_behavior}' not found in response")
                return response, False
    
    except Exception as e:
        results.add_fail(test_name, f"Exception: {str(e)}")
        return None, False


def main():
    print(f"\n{BOLD}{BLUE}{'='*80}{END}")
    print(f"{BOLD}{BLUE}🧪 COMPREHENSIVE TEST SUITE - Shortened Prompt Validation{END}")
    print(f"{BOLD}{BLUE}{'='*80}{END}\n")
    
    # Check for API key
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here":
        print(f"{RED}ERROR: Please set OPENAI_API_KEY in config or environment{END}")
        return False
    
    # Initialize
    print(f"Initializing assistant with model: {DEFAULT_MODEL}")
    assistant = IranianManagerAssistant(openai_api_key=OPENAI_API_KEY, model=DEFAULT_MODEL)
    db = DatabaseManager("test_assistant.db")
    results = TestResults()
    
    # Get current dates for testing
    today = jdatetime.datetime.now().date()
    tomorrow = today + jdatetime.timedelta(days=1)
    day_after = today + jdatetime.timedelta(days=2)
    
    print(f"Current Jalali date: {today.strftime('%Y-%m-%d')}")
    print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d')}")
    print(f"Day after: {day_after.strftime('%Y-%m-%d')}\n")
    
    # ==================== TEST 1: EVENT vs TASK DISTINCTION ====================
    print_section("TEST CATEGORY 1: Event vs Task Distinction")
    
    thread1 = "test_distinction_1"
    
    # Test 1.1: Clear event with meeting keyword
    def check_event_tool(response):
        if "create_event_tool" in response.lower() or "رویداد" in response or "جلسه" in response:
            return True, "Correctly identified as event"
        return False, "Failed to identify as event"
    
    response, _ = test_agent_response(
        assistant, 
        "1.1: Event with 'جلسه' keyword",
        f"فردا ساعت 10 جلسه با آقای احمدی",
        check_event_tool,
        thread1,
        results
    )
    
    # Test 1.2: Clear task with 'باید' keyword
    thread2 = "test_distinction_2"
    def check_task_tool(response):
        if "create_task_tool" in response.lower() or "وظیفه" in response or "تسک" in response:
            return True, "Correctly identified as task"
        return False, "Failed to identify as task"
    
    test_agent_response(
        assistant,
        "1.2: Task with 'باید' keyword",
        f"فردا باید به آقای احمدی زنگ بزنم",
        check_task_tool,
        thread2,
        results
    )
    
    # Test 1.3: Meeting with location
    thread3 = "test_distinction_3"
    test_agent_response(
        assistant,
        "1.3: Event with location",
        f"امروز ساعت 3 پرزنتیشن در سالن کنفرانس",
        check_event_tool,
        thread3,
        results
    )
    
    # Test 1.4: Task with action verb
    thread4 = "test_distinction_4"
    test_agent_response(
        assistant,
        "1.4: Task with action verb",
        f"فردا گزارش ماهانه را آماده کنم",
        check_task_tool,
        thread4,
        results
    )
    
    # ==================== TEST 2: DATE EXTRACTION ====================
    print_section("TEST CATEGORY 2: Date Extraction")
    
    # Test 2.1: 'امروز' (today)
    thread5 = "test_date_1"
    def check_today_date(response):
        today_str = today.strftime('%Y-%m-%d')
        if today_str in response:
            return True, f"Correctly extracted today's date: {today_str}"
        return False, f"Failed to extract today ({today_str})"
    
    test_agent_response(
        assistant,
        "2.1: Extract 'امروز' date",
        "امروز میتینگ تیم",
        check_today_date,
        thread5,
        results
    )
    
    # Test 2.2: 'فردا' (tomorrow)
    thread6 = "test_date_2"
    def check_tomorrow_date(response):
        tomorrow_str = tomorrow.strftime('%Y-%m-%d')
        if tomorrow_str in response:
            return True, f"Correctly extracted tomorrow's date: {tomorrow_str}"
        return False, f"Failed to extract tomorrow ({tomorrow_str})"
    
    test_agent_response(
        assistant,
        "2.2: Extract 'فردا' date",
        "فردا ملاقات با مشتری",
        check_tomorrow_date,
        thread6,
        results
    )
    
    # Test 2.3: 'پس‌فردا' (day after tomorrow)
    thread7 = "test_date_3"
    def check_day_after_date(response):
        day_after_str = day_after.strftime('%Y-%m-%d')
        if day_after_str in response:
            return True, f"Correctly extracted day after date: {day_after_str}"
        return False, f"Failed to extract day after ({day_after_str})"
    
    test_agent_response(
        assistant,
        "2.3: Extract 'پس‌فردا' date",
        "پس‌فردا قرار با طراح",
        check_day_after_date,
        thread7,
        results
    )
    
    # ==================== TEST 3: REQUIRED vs OPTIONAL FIELDS ====================
    print_section("TEST CATEGORY 3: Required vs Optional Fields")
    
    # Test 3.1: Event with all required fields (should execute immediately)
    thread8 = "test_fields_1"
    def check_immediate_execution(response):
        # Should request confirmation, not ask for more info
        if "تأیید" in response and "⚠️" in response:
            return True, "Correctly requested confirmation without asking for optional fields"
        if "مکان" in response and "؟" in response:
            return False, "Incorrectly asked for optional location field"
        return True, "Processed correctly"
    
    test_agent_response(
        assistant,
        "3.1: Complete required fields (should not ask for optional)",
        f"فردا ساعت 2 جلسه با آقای کریمی",
        check_immediate_execution,
        thread8,
        results
    )
    
    # Test 3.2: Event missing required field (should ask)
    thread9 = "test_fields_2"
    def check_asks_for_title(response):
        if "عنوان" in response and "؟" in response:
            return True, "Correctly asked for missing required field (title)"
        if "تأیید" in response:
            return False, "Incorrectly tried to execute without required field"
        return False, "Did not ask for required field"
    
    test_agent_response(
        assistant,
        "3.2: Missing required field (should ask)",
        "فردا یه جلسه بذار",
        check_asks_for_title,
        thread9,
        results
    )
    
    # Test 3.3: Task with all required fields
    thread10 = "test_fields_3"
    test_agent_response(
        assistant,
        "3.3: Task with complete required fields",
        f"فردا باید فایل پروپوزال را بررسی کنم",
        check_immediate_execution,
        thread10,
        results
    )
    
    # ==================== TEST 4: TITLE EXTRACTION ====================
    print_section("TEST CATEGORY 4: Title and Context Extraction")
    
    # Test 4.1: Extract complete title with context
    thread11 = "test_title_1"
    def check_title_extraction(response):
        if "جلسه با آقای احمدی" in response or "آقای احمدی" in response:
            return True, "Correctly extracted full title/context"
        return False, "Failed to extract complete title"
    
    test_agent_response(
        assistant,
        "4.1: Extract full title with attendee",
        f"برای فردا ساعت 10 صبح جلسه با آقای احمدی در دفتر مرکزی ثبت کن",
        check_title_extraction,
        thread11,
        results
    )
    
    # Test 4.2: Extract title from task description
    thread12 = "test_title_2"
    def check_task_description(response):
        if "گزارش" in response or "report" in response.lower():
            return True, "Correctly extracted task description"
        return False, "Failed to extract task description"
    
    test_agent_response(
        assistant,
        "4.2: Extract task description",
        f"فردا گزارش فروش ماهانه را تحویل بدهم",
        check_task_description,
        thread12,
        results
    )
    
    # ==================== TEST 5: APPROVAL FLOW ====================
    print_section("TEST CATEGORY 5: Human-in-the-Loop Approval")
    
    # Test 5.1: Create event and approve
    thread13 = "test_approval_1"
    response1, _ = test_agent_response(
        assistant,
        "5.1a: Request event creation (should ask for confirmation)",
        f"امروز ساعت 5 دیدار با مدیرعامل",
        lambda r: (True, "Initial request processed") if "تأیید" in r or "⚠️" in r else (False, "No confirmation request"),
        thread13,
        results
    )
    
    if response1 and ("تأیید" in response1 or "⚠️" in response1):
        # Approve the action
        response2, _ = test_agent_response(
            assistant,
            "5.1b: Approve event creation",
            "بله",
            lambda r: (True, "Successfully approved and executed") if "✅" in r or "موفقیت" in r else (False, "Approval not processed"),
            thread13,
            results
        )
    
    # Test 5.2: Create task and reject
    thread14 = "test_approval_2"
    response3, _ = test_agent_response(
        assistant,
        "5.2a: Request task creation",
        f"فردا باید به مهندس رضایی ایمیل بزنم",
        lambda r: (True, "Task creation requested") if "تأیید" in r or "⚠️" in r else (False, "No confirmation"),
        thread14,
        results
    )
    
    if response3 and ("تأیید" in response3 or "⚠️" in response3):
        # Reject the action
        response4, _ = test_agent_response(
            assistant,
            "5.2b: Reject task creation",
            "نه",
            lambda r: (True, "Successfully cancelled") if "لغو" in r or "❌" in r else (False, "Rejection not processed"),
            thread14,
            results
        )
    
    # ==================== TEST 6: SEARCH FUNCTIONALITY ====================
    print_section("TEST CATEGORY 6: Search Functionality")
    
    # First create some test data by approving creations
    thread15 = "test_search_setup"
    print("\nSetting up test data for search tests...")
    
    # Create event
    assistant.chat(f"امروز جلسه تست برای سرچ", thread_id=thread15)
    assistant.chat("بله", thread_id=thread15)
    
    # Create task
    thread16 = "test_search_setup2"
    assistant.chat(f"فردا باید تست سرچ را انجام دهم", thread_id=thread16)
    assistant.chat("بله", thread_id=thread16)
    
    # Test 6.1: Search events
    thread17 = "test_search_1"
    test_agent_response(
        assistant,
        "6.1: Search events (should execute immediately)",
        f"رویدادهای امروز را نشان بده",
        lambda r: (True, "Search executed") if "📅" in r or "event" in r.lower() or "رویداد" in r else (False, "Search failed"),
        thread17,
        results
    )
    
    # Test 6.2: Search tasks
    thread18 = "test_search_2"
    test_agent_response(
        assistant,
        "6.2: Search tasks (should execute immediately)",
        f"وظایف فردا چیه؟",
        lambda r: (True, "Task search executed") if "📋" in r or "task" in r.lower() or "وظیفه" in r else (False, "Task search failed"),
        thread18,
        results
    )
    
    # ==================== TEST 7: EDGE CASES ====================
    print_section("TEST CATEGORY 7: Edge Cases and Error Handling")
    
    # Test 7.1: Ambiguous input (missing date)
    thread19 = "test_edge_1"
    def check_asks_for_date(response):
        if "تاریخ" in response and "؟" in response:
            return True, "Correctly asked for missing date"
        return False, "Failed to handle missing date"
    
    test_agent_response(
        assistant,
        "7.1: Missing date (should ask)",
        "دیدار با مشتری در کافه نادری",
        check_asks_for_date,
        thread19,
        results
    )
    
    # Test 7.2: Clear distinction between similar phrases
    thread20 = "test_edge_2"
    test_agent_response(
        assistant,
        "7.2: 'زنگ بزنم' should be task, not event",
        f"فردا باید به خانم حسینی زنگ بزنم",
        check_task_tool,
        thread20,
        results
    )
    
    # Test 7.3: Meeting with 'با' should be event
    thread21 = "test_edge_3"
    test_agent_response(
        assistant,
        "7.3: 'جلسه با' should be event",
        f"پس‌فردا جلسه با تیم فروش",
        check_event_tool,
        thread21,
        results
    )
    
    # ==================== TEST 8: MULTILINGUAL ====================
    print_section("TEST CATEGORY 8: Multilingual Support")
    
    # Test 8.1: English event
    thread22 = "test_lang_1"
    test_agent_response(
        assistant,
        "8.1: English event creation",
        f"tomorrow meeting with CEO at 3pm",
        check_event_tool,
        thread22,
        results
    )
    
    # Test 8.2: Mixed Persian-English
    thread23 = "test_lang_2"
    test_agent_response(
        assistant,
        "8.2: Mixed language event",
        f"فردا meeting با team",
        check_event_tool,
        thread23,
        results
    )
    
    # ==================== FINAL SUMMARY ====================
    success = results.summary()
    
    # Cleanup
    print(f"\n{BOLD}Cleaning up test database...{END}")
    if os.path.exists("test_assistant.db"):
        os.remove("test_assistant.db")
        print("Test database removed.")
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Tests interrupted by user{END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{RED}FATAL ERROR: {str(e)}{END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


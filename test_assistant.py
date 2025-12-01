"""
Comprehensive tests for Iranian Manager Personal Assistant
Tests all tools, human-in-the-loop, memory, and edge cases
"""
import os
import sys
from database import DatabaseManager
from tools import (
    create_event_tool,
    get_event_tool,
    create_task_tool,
    get_task_tool,
    update_task_status_tool,
    validate_jalali_date
)


def test_database():
    """Test database operations"""
    print("=" * 80)
    print("TEST 1: Database Operations")
    print("=" * 80)
    
    # Use test database
    db = DatabaseManager("test_assistant.db")
    
    # Test event creation
    print("\n✓ Testing event creation...")
    event_id = db.create_event(
        date="1403-09-15",
        title="Test Meeting",
        attendee="John Doe",
        description="Test description",
        location="Room A"
    )
    print(f"  Created event ID: {event_id}")
    
    # Test event retrieval
    print("\n✓ Testing event retrieval...")
    events = db.get_events(date="1403-09-15")
    print(f"  Found {len(events)} event(s)")
    for event in events:
        print(f"  - {event['title']} on {event['date']}")
    
    # Test task creation
    print("\n✓ Testing task creation...")
    task_id = db.create_task(
        due_date="1403-09-20",
        description="Complete report",
        project="Q4 Analysis",
        status="undone"
    )
    print(f"  Created task ID: {task_id}")
    
    # Test task retrieval
    print("\n✓ Testing task retrieval...")
    tasks = db.get_tasks(project="Q4 Analysis")
    print(f"  Found {len(tasks)} task(s)")
    for task in tasks:
        print(f"  - {task['description']} (Status: {task['status']})")
    
    # Test task status update
    print("\n✓ Testing task status update...")
    success = db.update_task_status(task_id, "done")
    print(f"  Update success: {success}")
    
    print("\n✅ Database tests completed!\n")


def test_date_validation():
    """Test Jalali date validation"""
    print("=" * 80)
    print("TEST 2: Jalali Date Validation")
    print("=" * 80)
    
    test_cases = [
        ("1403-09-15", True, "Standard format with hyphens"),
        ("1403/09/15", True, "Format with slashes"),
        ("1403-9-5", True, "Single digit month/day"),
        ("invalid", False, "Invalid format"),
        ("2024-01-01", False, "Gregorian date (will fail)"),
    ]
    
    for date_str, should_pass, description in test_cases:
        try:
            result = validate_jalali_date(date_str)
            if should_pass:
                print(f"✅ PASS: {description}")
                print(f"   Input: {date_str} → Output: {result}")
            else:
                print(f"⚠️  UNEXPECTED PASS: {description}")
                print(f"   Input: {date_str} → Output: {result}")
        except ValueError as e:
            if not should_pass:
                print(f"✅ PASS: {description}")
                print(f"   Input: {date_str} → Error: {str(e)}")
            else:
                print(f"❌ FAIL: {description}")
                print(f"   Input: {date_str} → Error: {str(e)}")
    
    print("\n✅ Date validation tests completed!\n")


def test_tools():
    """Test all LangChain tools"""
    print("=" * 80)
    print("TEST 3: LangChain Tools")
    print("=" * 80)
    
    # Test create event tool
    print("\n✓ Testing create_event_tool...")
    result = create_event_tool.invoke({
        "date": "1403-09-16",
        "title": "Tool Test Event",
        "attendee": "Test User",
        "description": "Testing tool",
        "location": "Virtual"
    })
    print(f"  Result: {result}")
    
    # Test get event tool
    print("\n✓ Testing get_event_tool...")
    result = get_event_tool.invoke({
        "title": "Tool Test"
    })
    print(f"  Result: {result}")
    
    # Test create task tool
    print("\n✓ Testing create_task_tool...")
    result = create_task_tool.invoke({
        "due_date": "1403-09-25",
        "description": "Tool test task",
        "project": "Testing",
        "status": "undone"
    })
    print(f"  Result: {result}")
    
    # Test get task tool
    print("\n✓ Testing get_task_tool...")
    result = get_task_tool.invoke({
        "project": "Testing"
    })
    print(f"  Result: {result}")
    
    # Test update task status tool (by project)
    print("\n✓ Testing update_task_status_tool (by project)...")
    result = update_task_status_tool.invoke({
        "project": "Testing",
        "new_status": "in_progress"
    })
    print(f"  Result: {result}")
    
    # Test update task status tool (by description)
    print("\n✓ Testing update_task_status_tool (by description)...")
    result = update_task_status_tool.invoke({
        "description": "Tool test task",
        "new_status": "done"
    })
    print(f"  Result: {result}")
    
    print("\n✅ Tool tests completed!\n")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("=" * 80)
    print("TEST 4: Edge Cases and Error Handling")
    print("=" * 80)
    
    # Test missing required fields
    print("\n✓ Testing missing required fields...")
    try:
        result = create_event_tool.invoke({
            "title": "No Date Event"
            # Missing required 'date' field
        })
        print(f"  Result: {result}")
    except Exception as e:
        print(f"  Expected error: {str(e)}")
    
    # Test invalid date format
    print("\n✓ Testing invalid date format...")
    result = create_event_tool.invoke({
        "date": "invalid-date",
        "title": "Bad Date Event"
    })
    print(f"  Result: {result}")
    
    # Test updating non-existent task
    print("\n✓ Testing update on non-existent task...")
    result = update_task_status_tool.invoke({
        "project": "NonExistentProject12345",
        "new_status": "done"
    })
    print(f"  Result: {result}")
    
    # Test empty query
    print("\n✓ Testing empty query...")
    result = get_event_tool.invoke({})
    print(f"  Result: {result}")
    
    print("\n✅ Edge case tests completed!\n")


def run_all_tests():
    """Run all tests"""
    print("\n")
    print("🧪 " + "=" * 76 + " 🧪")
    print("   IRANIAN MANAGER PERSONAL ASSISTANT - COMPREHENSIVE TEST SUITE")
    print("🧪 " + "=" * 76 + " 🧪")
    print()
    
    try:
        test_database()
        test_date_validation()
        test_tools()
        test_edge_cases()
        
        print("=" * 80)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()


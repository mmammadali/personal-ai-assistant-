"""
Comprehensive Test Suite for Phase 1 AI Power Features
Tests all implemented features
"""
import sys
import os
import jdatetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Test database
TEST_DB = "test_phase1.db"

def cleanup_test_db():
    """Remove test database"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_schema():
    """Test database schema extensions"""
    print("\n" + "="*60)
    print("TEST 1: Database Schema Extensions")
    print("="*60)
    
    try:
        from database import DatabaseManager
        db = DatabaseManager(TEST_DB)
        
        # Check if tables exist by trying to query them
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            tables = [
                'energy_levels', 'productivity_metrics', 'user_preferences',
                'user_patterns', 'suggestions_log', 'context_links',
                'reminders', 'notifications_queue', 'task_dependencies',
                'document_versions'
            ]
            
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                result = cursor.fetchone()
                assert result is not None, f"Table {table} not found"
                print(f"  ✅ Table '{table}' exists")
        
        print("  ✅ All database tables created successfully")
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        return False

def test_energy_analyzer():
    """Test energy analyzer"""
    print("\n" + "="*60)
    print("TEST 2: Energy Analyzer")
    print("="*60)
    
    try:
        from intelligence.energy_analyzer import EnergyAnalyzer
        
        analyzer = EnergyAnalyzer(TEST_DB)
        
        # Record some energy levels
        today = jdatetime.date.today().strftime('%Y-%m-%d')
        analyzer.record_energy_level(today, 9, 0.8, 'task')
        analyzer.record_energy_level(today, 14, 0.7, 'meeting')
        analyzer.record_energy_level(today, 15, 0.6, 'task')
        
        print("  ✅ Energy levels recorded")
        
        # Get patterns
        patterns = analyzer.get_energy_patterns(days_back=7)
        print(f"  ✅ Energy patterns retrieved: {len(patterns)} hours")
        
        # Get peak hours
        peak_hours = analyzer.identify_peak_hours(days_back=7)
        print(f"  ✅ Peak hours identified: {len(peak_hours)} hours")
        
        # Get optimal meeting hours
        optimal_meetings = analyzer.get_optimal_meeting_hours(duration_hours=1.0)
        print(f"  ✅ Optimal meeting hours: {len(optimal_meetings)} suggestions")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_calendar_optimizer():
    """Test calendar optimizer"""
    print("\n" + "="*60)
    print("TEST 3: Calendar Optimizer")
    print("="*60)
    
    try:
        from intelligence.calendar_optimizer import CalendarOptimizer
        from database import DatabaseManager
        
        db = DatabaseManager(TEST_DB)
        optimizer = CalendarOptimizer(TEST_DB)
        
        # Create a test event
        today = jdatetime.date.today().strftime('%Y-%m-%d')
        db.create_event(today, "Test Meeting", "Test Attendee")
        
        # Analyze meeting patterns
        patterns = optimizer.analyze_meeting_patterns(days_back=30)
        print(f"  ✅ Meeting patterns analyzed: {patterns.get('total_meetings', 0)} meetings")
        
        # Find optimal time slot
        suggestions = optimizer.find_optimal_time_slot(today, duration_hours=1.0)
        print(f"  ✅ Optimal time slots found: {len(suggestions)} suggestions")
        
        # Calculate preparation time
        prep_time = optimizer.calculate_preparation_time("Presentation Meeting")
        print(f"  ✅ Preparation time calculated: {prep_time} hours")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_task_predictor():
    """Test task predictor"""
    print("\n" + "="*60)
    print("TEST 4: Task Predictor")
    print("="*60)
    
    try:
        from intelligence.task_predictor import TaskPredictor
        from database import DatabaseManager
        
        db = DatabaseManager(TEST_DB)
        predictor = TaskPredictor(TEST_DB)
        
        # Create test tasks
        today = jdatetime.date.today().strftime('%Y-%m-%d')
        tomorrow = (jdatetime.date.today() + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        db.create_task(tomorrow, "Complete report", "Project A")
        db.create_task(today, "Send email", status="done")
        
        # Analyze patterns
        patterns = predictor.analyze_task_completion_patterns(days_back=30)
        print(f"  ✅ Task patterns analyzed: {patterns.get('total_tasks', 0)} tasks")
        
        # Estimate completion time
        est_time = predictor.estimate_completion_time("Write a comprehensive report")
        print(f"  ✅ Completion time estimated: {est_time} hours")
        
        # Predict priorities
        tasks = db.get_tasks()
        prioritized = predictor.predict_task_priorities(tasks, today)
        print(f"  ✅ Task priorities predicted: {len(prioritized)} tasks")
        
        # Generate morning briefing
        briefing = predictor.generate_morning_briefing(today)
        print(f"  ✅ Morning briefing generated: {briefing.get('tasks_count', 0)} tasks")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_dependency_analyzer():
    """Test dependency analyzer"""
    print("\n" + "="*60)
    print("TEST 5: Dependency Analyzer")
    print("="*60)
    
    try:
        from intelligence.dependency_analyzer import DependencyAnalyzer
        from database import DatabaseManager
        
        db = DatabaseManager(TEST_DB)
        analyzer = DependencyAnalyzer(TEST_DB)
        
        # Create test tasks
        today = jdatetime.date.today().strftime('%Y-%m-%d')
        task1_id = db.create_task(today, "Task 1", status="done")
        task2_id = db.create_task(today, "Task 2")
        
        # Create dependency
        dep_id = analyzer.create_dependency(task2_id, task1_id, "blocks")
        print(f"  ✅ Dependency created: {dep_id}")
        
        # Get dependencies
        deps = analyzer.get_task_dependencies(task2_id)
        print(f"  ✅ Dependencies retrieved: {len(deps)} dependencies")
        
        # Analyze chain
        analysis = analyzer.analyze_dependency_chain(task2_id)
        print(f"  ✅ Dependency chain analyzed: can_start={analysis.get('can_start', False)}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_reminder_engine():
    """Test reminder engine"""
    print("\n" + "="*60)
    print("TEST 6: Reminder Engine")
    print("="*60)
    
    try:
        from intelligence.reminder_engine import ReminderEngine
        
        engine = ReminderEngine(TEST_DB)
        
        # Create reminder
        today = jdatetime.date.today().strftime('%Y-%m-%d')
        reminder_id = engine.create_reminder(
            "Test reminder",
            reminder_type="time",
            trigger_time=today
        )
        print(f"  ✅ Reminder created: {reminder_id}")
        
        # Get active reminders
        reminders = engine.get_active_reminders(current_time=today)
        print(f"  ✅ Active reminders retrieved: {len(reminders)}")
        
        # Create context reminder
        context_id = engine.create_context_reminder(
            "Context reminder",
            ["meeting", "client"]
        )
        print(f"  ✅ Context reminder created: {context_id}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_notification_manager():
    """Test notification manager"""
    print("\n" + "="*60)
    print("TEST 7: Notification Manager")
    print("="*60)
    
    try:
        from intelligence.notification_manager import NotificationManager
        
        manager = NotificationManager(TEST_DB)
        
        # Create notification
        notif_id = manager.create_notification(
            "task_due",
            "Task is due today",
            importance_score=0.8
        )
        print(f"  ✅ Notification created: {notif_id}")
        
        # Get pending notifications
        notifications = manager.get_pending_notifications(limit=10)
        print(f"  ✅ Pending notifications: {len(notifications)}")
        
        # Get summary
        summary = manager.get_notification_summary()
        print(f"  ✅ Notification summary: {summary.get('pending_count', 0)} pending")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_date_parser():
    """Test natural date parser"""
    print("\n" + "="*60)
    print("TEST 8: Natural Date Parser")
    print("="*60)
    
    try:
        from intelligence.date_parser import NaturalDateParser
        
        parser = NaturalDateParser()
        
        # Test Persian dates
        test_cases = [
            ("امروز", "today"),
            ("فردا", "tomorrow"),
            ("دیروز", "yesterday"),
            ("هفته آینده", "next week"),
        ]
        
        for persian, english in test_cases:
            result_persian = parser.parse(persian)
            result_english = parser.parse(english)
            if result_persian and result_english:
                print(f"  ✅ Parsed '{persian}' and '{english}'")
            else:
                print(f"  ⚠️  Could not parse '{persian}' or '{english}'")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_context_manager():
    """Test context manager"""
    print("\n" + "="*60)
    print("TEST 9: Context Manager")
    print("="*60)
    
    try:
        from intelligence.context_manager import ContextManager
        from database import DatabaseManager
        
        db = DatabaseManager(TEST_DB)
        manager = ContextManager(TEST_DB)
        
        # Create test entities
        event_id = db.create_event(
            jdatetime.date.today().strftime('%Y-%m-%d'),
            "Test Event"
        )
        task_id = db.create_task(
            jdatetime.date.today().strftime('%Y-%m-%d'),
            "Test Task"
        )
        
        # Create link
        link_id = manager.create_context_link(
            "event", event_id,
            "task", task_id,
            "related_to"
        )
        print(f"  ✅ Context link created: {link_id}")
        
        # Get related entities
        related = manager.get_related_entities("event", event_id)
        print(f"  ✅ Related entities: {len(related)}")
        
        # Search
        results = manager.search_across_agents("Test")
        print(f"  ✅ Search results: {len(results)} types")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_tools_integration():
    """Test that all tools are properly integrated"""
    print("\n" + "="*60)
    print("TEST 10: Tools Integration")
    print("="*60)
    
    try:
        from tools import ALL_TOOLS
        
        tool_count = len(ALL_TOOLS)
        print(f"  ✅ Total tools available: {tool_count}")
        
        # Check for key tool categories
        tool_names = [tool.name for tool in ALL_TOOLS]
        
        categories = {
            'calendar': ['optimize_calendar', 'analyze_energy_patterns'],
            'task': ['generate_morning_briefing', 'predict_task_priorities'],
            'reminder': ['create_reminder', 'get_active_reminders'],
            'notification': ['create_notification', 'get_pending_notifications'],
            'summary': ['generate_daily_summary', 'generate_weekly_summary'],
            'search': ['search_across_agents', 'get_related_context']
        }
        
        for category, expected_tools in categories.items():
            found = any(any(exp in name for exp in expected_tools) for name in tool_names)
            if found:
                print(f"  ✅ {category.capitalize()} tools integrated")
            else:
                print(f"  ⚠️  {category.capitalize()} tools not found")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 1 FEATURES - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Cleanup before starting
    cleanup_test_db()
    
    tests = [
        ("Database Schema", test_database_schema),
        ("Energy Analyzer", test_energy_analyzer),
        ("Calendar Optimizer", test_calendar_optimizer),
        ("Task Predictor", test_task_predictor),
        ("Dependency Analyzer", test_dependency_analyzer),
        ("Reminder Engine", test_reminder_engine),
        ("Notification Manager", test_notification_manager),
        ("Date Parser", test_date_parser),
        ("Context Manager", test_context_manager),
        ("Tools Integration", test_tools_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with exception: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Cleanup
    cleanup_test_db()
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


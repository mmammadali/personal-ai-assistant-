"""
Quick demo script to test the web interface components
Run this to verify all components are working before starting the server
"""
import os
import sys

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'flask',
        'langchain',
        'langchain_openai',
        'langgraph',
        'jdatetime',
        'pytz',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n⚠️  Missing packages detected!")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All dependencies installed!\n")
    return True


def check_api_key():
    """Check if OpenAI API key is set"""
    print("🔑 Checking OpenAI API key...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key or api_key == 'your-api-key-here':
        print("  ❌ OpenAI API key not set")
        print("\nPlease set your API key:")
        print("  Windows: set OPENAI_API_KEY=your-key-here")
        print("  Linux/Mac: export OPENAI_API_KEY=your-key-here")
        return False
    
    print(f"  ✅ API key set (starts with: {api_key[:8]}...)")
    print()
    return True


def check_file_structure():
    """Check if all required files exist"""
    print("📁 Checking file structure...")
    
    required_files = [
        'app.py',
        'agent.py',
        'tools.py',
        'database.py',
        'templates/chat.html',
        'static/css/style.css',
        'static/js/chat.js'
    ]
    
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(file_path):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} (missing)")
            missing_files.append(file)
    
    if missing_files:
        print("\n⚠️  Missing files detected!")
        return False
    
    print("\n✅ All files present!\n")
    return True


def test_database():
    """Test database operations"""
    print("🗄️  Testing database...")
    
    try:
        from database import DatabaseManager
        
        db = DatabaseManager()
        
        # Test event creation
        event_id = db.create_event(
            date="1403-09-15",
            title="Test Event",
            attendee="Test User"
        )
        print(f"  ✅ Event created (ID: {event_id})")
        
        # Test event retrieval
        events = db.get_events(title="Test Event")
        print(f"  ✅ Event retrieved ({len(events)} found)")
        
        # Test task creation
        task_id = db.create_task(
            due_date="1403-09-16",
            description="Test Task"
        )
        print(f"  ✅ Task created (ID: {task_id})")
        
        # Test task retrieval
        tasks = db.get_tasks(description="Test Task")
        print(f"  ✅ Task retrieved ({len(tasks)} found)")
        
        print("\n✅ Database working correctly!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {str(e)}\n")
        return False


def test_agent():
    """Test agent initialization"""
    print("🤖 Testing agent...")
    
    try:
        from agent import IranianManagerAssistant
        
        api_key = os.getenv('OPENAI_API_KEY', 'test-key')
        
        assistant = IranianManagerAssistant(
            openai_api_key=api_key,
            model="gpt-4o-mini"
        )
        
        print("  ✅ Agent initialized successfully")
        print("\n✅ Agent working correctly!\n")
        return True
        
    except Exception as e:
        print(f"  ❌ Agent error: {str(e)}\n")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("🚀 Iranian Manager Assistant - Web Interface Demo")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("API Key", check_api_key),
        ("File Structure", check_file_structure),
        ("Database", test_database),
        ("Agent", test_agent)
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"❌ {name} check failed: {str(e)}\n")
            results[name] = False
    
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to start the web interface.")
        print("\nRun the server:")
        print("  python app.py")
        print("\nThen open: http://127.0.0.1:5000")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before starting.")
    
    print()


if __name__ == "__main__":
    main()




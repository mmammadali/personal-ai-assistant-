"""
Environment Setup Helper
This script helps create a .env file for the project
"""
import os

def create_env_file():
    """Create a .env file with the provided API key"""
    
    env_content = """# OpenAI Configuration
OPENAI_API_KEY=your-api-key-here

# Application Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Model Configuration
DEFAULT_MODEL=gpt-5-mini
"""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_file = os.path.join(project_root, '.env')
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print("✅ .env file created successfully!")
        print(f"📁 Location: {env_file}")
        print("\n🔐 Your OpenAI API Key has been configured.")
        print("⚙️  You can now run the application.")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        print("\n📝 Manual setup:")
        print("Create a .env file in the project root with:")
        print(env_content)

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 Iranian Manager Assistant - Environment Setup")
    print("=" * 60)
    print()
    create_env_file()


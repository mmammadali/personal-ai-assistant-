"""
Example usage of Iranian Manager Personal Assistant
Demonstrates all features: events, tasks, human-in-the-loop, memory
"""
import os
from agent import IranianManagerAssistant


def main():
    """Run example conversations"""
    
    # Initialize assistant
    # Replace with your actual OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    
    assistant = IranianManagerAssistant(
        openai_api_key=api_key,
        model="gpt-4o-mini"  # or "gpt-4-turbo-preview" for better performance
    )
    
    print("=" * 80)
    print("🤖 IRANIAN MANAGER PERSONAL ASSISTANT")
    print("=" * 80)
    print("Features: Event Management, Task Management, Jalali Calendar Support")
    print("Type 'quit' or 'exit' to end the conversation")
    print("=" * 80)
    print()
    
    # Example interactions (uncomment to run automated examples)
    # run_automated_examples(assistant)
    
    # Interactive mode
    run_interactive_mode(assistant)


def run_automated_examples(assistant: IranianManagerAssistant):
    """Run automated example interactions"""
    
    examples = [
        # Create event example
        "I need to create a meeting for 1403-09-15 with title 'Budget Review Meeting' with attendee 'Ali Rezaei' at location 'Conference Room A'",
        
        # Get event example
        "Show me all events for 1403-09-15",
        
        # Create task example
        "Create a task: finish quarterly report by 1403-09-20 for project 'Q4 Financial Analysis'",
        
        # Get task example
        "Show me all tasks for the Q4 Financial Analysis project",
        
        # Update task status example
        "Mark the task for Q4 Financial Analysis project as done",
        
        # Memory test
        "What was the meeting I created earlier?",
    ]
    
    thread_id = "example_thread"
    
    for i, user_input in enumerate(examples, 1):
        print(f"\n{'=' * 80}")
        print(f"Example {i}")
        print(f"{'=' * 80}")
        print(f"👤 User: {user_input}")
        print()
        
        response = assistant.chat(user_input, thread_id=thread_id)
        print(f"🤖 Assistant: {response}")
        
        # If approval is needed, auto-approve for demo
        if "Confirmation Required" in response or "Do you approve" in response:
            print(f"\n👤 User: yes")
            print()
            approval_response = assistant.chat("yes", thread_id=thread_id)
            print(f"🤖 Assistant: {approval_response}")
    
    print(f"\n{'=' * 80}")
    print("Automated examples completed!")
    print(f"{'=' * 80}\n")


def run_interactive_mode(assistant: IranianManagerAssistant):
    """Run interactive chat mode"""
    
    thread_id = "interactive_thread"
    
    print("💬 Interactive Mode Started")
    print("Example commands:")
    print("  - 'Create an event for tomorrow at 10 AM titled Team Standup'")
    print("  - 'Show me all events for this week'")
    print("  - 'Add a task to finish the presentation by Friday'")
    print("  - 'Show me all undone tasks'")
    print("  - 'Mark task 1 as done'")
    print()
    
    while True:
        try:
            # Get user input
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'خروج']:
                print("\n👋 Goodbye! Have a productive day!")
                break
            
            # Get assistant response
            response = assistant.chat(user_input, thread_id=thread_id)
            print(f"\n🤖 Assistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Conversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


if __name__ == "__main__":
    main()


"""
Example Usage Script for RAG Agent
Demonstrates document upload, querying, and summarization
"""
import os
from pathlib import Path
from rag_agent import RAGAgent
from config import OPENAI_API_KEY, RAG_MODEL, RAG_VECTOR_STORE_TYPE, RAG_CHROMA_PERSIST_DIR, RAG_COLLECTION_NAME


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Main example function"""
    
    print_section("🚀 RAG Agent Example - Document Management System")
    
    # Initialize RAG agent
    print("📦 Initializing RAG Agent...")
    agent = RAGAgent(
        openai_api_key=OPENAI_API_KEY,
        model=RAG_MODEL,
        vector_store_type=RAG_VECTOR_STORE_TYPE,
        persist_directory=RAG_CHROMA_PERSIST_DIR,
        collection_name=RAG_COLLECTION_NAME
    )
    print("✅ RAG Agent initialized successfully!")
    
    # Example 1: List existing documents
    print_section("📋 Example 1: List Existing Documents")
    response = agent.chat("لیست اسناد من را نشان بده", thread_id="example_1")
    print(response)
    
    # Example 2: Upload a document (if you have a sample file)
    print_section("📤 Example 2: Upload Document")
    print("Note: To upload a document, place a file (PDF, DOCX, TXT) in the current directory")
    print("and update the file path below.")
    
    # Check if there's a sample file
    sample_files = list(Path(".").glob("*.pdf")) + list(Path(".").glob("*.txt")) + list(Path(".").glob("*.docx"))
    
    if sample_files:
        sample_file = str(sample_files[0].absolute())
        print(f"Found sample file: {sample_file}")
        
        response = agent.chat(
            f"لطفاً این فایل را بارگذاری کن: {sample_file}",
            thread_id="example_2"
        )
        print(response)
    else:
        print("⚠️ No sample files found. Create a test.txt file to try uploading.")
        print("\nExample command to create a test file:")
        print("echo 'این یک سند تستی است. تاریخ: 1403/09/15. مبلغ: 1000000 تومان' > test.txt")
    
    # Example 3: Query a document
    print_section("💬 Example 3: Ask Questions About Documents")
    response = agent.chat(
        "آیا سندی درباره بودجه یا مالی دارم؟",
        thread_id="example_3"
    )
    print(response)
    
    # Example 4: Summarize a document
    print_section("📝 Example 4: Get Document Summary")
    print("Note: This requires a document to be already uploaded")
    print("First, let's list documents to get a document_id...")
    
    response = agent.chat("لیست اسناد را نشان بده", thread_id="example_4")
    print(response)
    
    print("\nTo get a summary, use the document ID from the list above:")
    print("Example: 'خلاصه سند با شناسه [DOCUMENT_ID] را بده'")
    
    # Example 5: Delete a document
    print_section("🗑️ Example 5: Delete Document")
    print("Note: Use the document ID from the list to delete")
    print("Example: 'سند با شناسه [DOCUMENT_ID] را حذف کن'")
    
    # Interactive mode
    print_section("🎯 Interactive Mode")
    print("You can now chat with the RAG agent interactively!")
    print("Commands:")
    print("  - 'لیست' or 'list' : Show all documents")
    print("  - 'خروج' or 'exit' : Exit")
    print("  - Any other text: Ask questions about your documents")
    print("\n" + "-" * 80 + "\n")
    
    thread_id = "interactive"
    
    while True:
        try:
            user_input = input("شما: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'خروج', 'خارج']:
                print("\n👋 خداحافظ!")
                break
            
            # Send to agent
            print("\n🤖 در حال پردازش...\n")
            response = agent.chat(user_input, thread_id=thread_id)
            print(f"دستیار: {response}\n")
            print("-" * 80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 خداحافظ!")
            break
        except Exception as e:
            print(f"\n❌ خطا: {str(e)}\n")


if __name__ == "__main__":
    # Check if API key is set
    if not OPENAI_API_KEY:
        print("❌ خطا: OPENAI_API_KEY تنظیم نشده است!")
        print("لطفاً کلید API خود را در فایل .env یا متغیرهای محیطی تنظیم کنید.")
        exit(1)
    
    try:
        main()
    except Exception as e:
        print(f"\n❌ خطای کلی: {str(e)}")
        import traceback
        traceback.print_exc()

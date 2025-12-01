"""
Flask web application for Iranian Manager Personal Assistant
Professional chat interface with real-time messaging
"""
import os
from flask import Flask, render_template, request, jsonify, session
from agent import IranianManagerAssistant
import uuid
from datetime import datetime
from config import OPENAI_API_KEY, DEFAULT_MODEL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize the assistant using centralized configuration
assistant = IranianManagerAssistant(
    openai_api_key=OPENAI_API_KEY,
    model=DEFAULT_MODEL
)

# Store active sessions
sessions = {}


@app.route('/')
def index():
    """Render the main chat interface"""
    # Create a unique session ID for each user
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('chat.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the user"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'پیام خالی است'}), 400
        
        # Get or create thread ID for this user
        user_id = session.get('user_id', 'default')
        thread_id = sessions.get(user_id, f"thread_{user_id}")
        sessions[user_id] = thread_id
        
        # Get response from assistant
        print(f"[DEBUG] User message: {user_message}")
        response = assistant.chat(user_message, thread_id=thread_id)
        print(f"[DEBUG] Assistant response: {response[:100]}...")
        
        # Check if we need to clear the thread (after successful tool execution)
        if response.startswith("__CLEAR_THREAD__|"):
            # Extract actual response
            response = response.replace("__CLEAR_THREAD__|", "")
            # Generate new thread ID for next interaction
            sessions[user_id] = f"thread_{uuid.uuid4()}"
            print(f"[INFO] Thread cleared for user {user_id}")
        
        # Check if this is a confirmation request (English and Persian)
        is_confirmation = (
            "Confirmation Required" in response or 
            "Do you approve" in response or
            "تأیید" in response or
            "آیا تأیید می‌کنید" in response or
            "⚠️" in response
        )
        
        return jsonify({
            'response': response,
            'is_confirmation': is_confirmation,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    
    except Exception as e:
        print(f"[ERROR] Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا: {str(e)}'}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get conversation history for the current user"""
    try:
        user_id = session.get('user_id', 'default')
        thread_id = sessions.get(user_id, f"thread_{user_id}")
        
        history = assistant.get_conversation_history(thread_id=thread_id)
        
        return jsonify({
            'history': history
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def clear_session():
    """Clear the current conversation session"""
    try:
        user_id = session.get('user_id', 'default')
        
        # Create a new thread ID
        new_thread_id = f"thread_{uuid.uuid4()}"
        sessions[user_id] = new_thread_id
        
        return jsonify({
            'success': True,
            'message': 'گفتگو پاک شد'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Iranian Manager Assistant'})


if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    
    print("=" * 80)
    print("🚀 Iranian Manager Personal Assistant - Web Interface")
    print("=" * 80)
    print(f"🌐 Server starting at: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"🤖 AI Model: {DEFAULT_MODEL}")
    print("📱 Features: Modern Chat UI, Jalali Calendar, Task & Event Management")
    print("=" * 80)
    
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)




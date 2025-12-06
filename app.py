"""
Flask web application for Iranian Manager Personal Assistant
Professional chat interface with real-time messaging
Supports both Task/Event Management and RAG Document Agent
"""
import os
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from pathlib import Path
import uuid
from datetime import datetime

from agent import IranianManagerAssistant
from config import (
    OPENAI_API_KEY, DEFAULT_MODEL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
    UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_MB
)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Create upload folder
UPLOAD_PATH = Path(UPLOAD_FOLDER)
UPLOAD_PATH.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_PATH)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE_MB * 1024 * 1024  # MB to bytes

# Initialize the task/event assistant
assistant = IranianManagerAssistant(
    openai_api_key=OPENAI_API_KEY,
    model=DEFAULT_MODEL
)

# Initialize the RAG agent (optional - will fail gracefully if dependencies missing)
rag_agent = None
try:
    from rag_agent import RAGAgent
    from config import (
        RAG_VECTOR_STORE_TYPE, RAG_CHROMA_PERSIST_DIR, RAG_FAISS_PERSIST_DIR, 
        RAG_COLLECTION_NAME, RAG_MODEL
    )
    
    # Select correct persist directory based on vector store type
    persist_dir = RAG_CHROMA_PERSIST_DIR
    if RAG_VECTOR_STORE_TYPE.lower() == "faiss":
        persist_dir = RAG_FAISS_PERSIST_DIR
    
    rag_agent = RAGAgent(
        openai_api_key=OPENAI_API_KEY,
        model=RAG_MODEL,
        vector_store_type=RAG_VECTOR_STORE_TYPE,
        persist_directory=persist_dir,
        collection_name=RAG_COLLECTION_NAME
    )
    print(f"✅ RAG Agent initialized successfully with {RAG_VECTOR_STORE_TYPE}")
except Exception as e:
    print(f"⚠️ RAG Agent not available: {str(e)}")
    print("   Task/Event Management Agent is still available")

# Initialize Finance Agent (optional - will fail gracefully if dependencies missing)
finance_agent = None
try:
    from finance_agent import FinanceAgent
    from config import FINANCE_DB_PATH, FINANCE_MODEL
    
    finance_agent = FinanceAgent(
        openai_api_key=OPENAI_API_KEY,
        model=FINANCE_MODEL,
        db_path=FINANCE_DB_PATH
    )
    print(f"✅ Finance Agent initialized successfully with {FINANCE_MODEL}")
except Exception as e:
    print(f"⚠️ Finance Agent not available: {str(e)}")
    print("   Task/Event and RAG Agents are still available")

# Store active sessions for all agents
sessions = {}
rag_sessions = {}
finance_sessions = {}


@app.route('/')
def index():
    """Render the main chat interface (Task/Event Management)"""
    # Create a unique session ID for each user
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('index.html')


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


# ===================== RAG AGENT ROUTES =====================

def allowed_file(filename):
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@app.route('/rag')
def rag_index():
    """Render the RAG agent chat interface"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    return render_template('rag_chat.html')


@app.route('/api/rag/chat', methods=['POST'])
def rag_chat():
    """Handle chat messages for RAG agent"""
    if rag_agent is None:
        return jsonify({
            'error': 'RAG Agent is not available. Please install required dependencies: chromadb, langchain-chroma'
        }), 503
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'پیام خالی است'}), 400
        
        # Get or create thread ID for this user
        user_id = session.get('user_id', 'default')
        thread_id = rag_sessions.get(user_id, f"rag_thread_{user_id}")
        rag_sessions[user_id] = thread_id
        
        # Get response from RAG agent
        print(f"[RAG DEBUG] User message: {user_message}")
        response = rag_agent.chat(user_message, thread_id=thread_id)
        print(f"[RAG DEBUG] Agent response: {response[:100]}...")
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        })
    
    except Exception as e:
        print(f"[RAG ERROR] Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا: {str(e)}'}), 500


@app.route('/api/rag/upload', methods=['POST'])
def upload_document():
    """Handle document upload for RAG agent"""
    if rag_agent is None:
        return jsonify({
            'error': 'RAG Agent is not available. Please install required dependencies: chromadb, langchain-chroma'
        }), 503
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_PATH / unique_filename
        
        file.save(str(filepath))
        print(f"[RAG INFO] File saved: {filepath}")
        
        # Process document with RAG agent
        user_id = session.get('user_id', 'default')
        thread_id = rag_sessions.get(user_id, f"rag_thread_{user_id}")
        rag_sessions[user_id] = thread_id
        
        # Use the upload tool through agent
        upload_message = f"لطفاً این فایل را بارگذاری کن: {filepath}"
        response = rag_agent.chat(upload_message, thread_id=thread_id)
        
        return jsonify({
            'success': True,
            'response': response,
            'filename': filename
        })
    
    except Exception as e:
        print(f"[RAG ERROR] Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا در بارگذاری: {str(e)}'}), 500


@app.route('/api/rag/clear', methods=['POST'])
def clear_rag_session():
    """Clear RAG agent conversation session"""
    if rag_agent is None:
        return jsonify({
            'error': 'RAG Agent is not available. Please install required dependencies: chromadb, langchain-chroma'
        }), 503
    
    try:
        user_id = session.get('user_id', 'default')
        
        # Create a new thread ID
        new_thread_id = f"rag_thread_{uuid.uuid4()}"
        rag_sessions[user_id] = new_thread_id
        
        # Reset conversation in agent
        rag_agent.reset_conversation(thread_id=new_thread_id)
        
        return jsonify({
            'success': True,
            'message': 'گفتگو پاک شد'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================== FINANCE AGENT ROUTES =====================

@app.route('/finance')
def finance_index():
    """Render Finance Assistant UI"""
    if finance_agent is None:
        return "Finance Agent is not available. Please check dependencies.", 503
    
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    
    # Initialize user if new
    user_id = session['user_id']
    finance_agent.init_user(user_id, name=f"User-{user_id[:8]}")
    
    return render_template('finance_chat.html')


@app.route('/api/finance/chat', methods=['POST'])
def finance_chat():
    """Finance chat endpoint"""
    if finance_agent is None:
        return jsonify({
            'error': 'Finance Agent is not available. Please check dependencies.'
        }), 503
    
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        if not user_message:
            return jsonify({'error': 'پیام خالی است'}), 400
        
        # Get or create thread ID for this user
        user_id = session.get('user_id', 'default')
        thread_id = finance_sessions.get(user_id, f"finance_{user_id}")
        finance_sessions[user_id] = thread_id
        
        # Store date parameters in session for report generation
        if date_from and date_to:
            if 'report_params' not in session:
                session['report_params'] = {}
            session['report_params'] = {
                'date_from': date_from,
                'date_to': date_to
            }
        
        # Get response from finance agent
        print(f"[FINANCE DEBUG] User message: {user_message}")
        if date_from and date_to:
            print(f"[FINANCE DEBUG] Date range: {date_from} to {date_to}")
        response = finance_agent.chat(user_message, thread_id=thread_id, user_id=user_id, date_from=date_from, date_to=date_to)
        print(f"[FINANCE DEBUG] Agent response: {response[:100]}...")
        
        # Check if this is a report selection request
        response_data = {
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M')
        }
        
        # Check if response indicates report selection needed
        user_msg_lower = user_message.lower()
        is_report_query = (
            "گزارش‌های مالی موجود" in response or 
            ("گزارش" in user_message and not any(keyword in user_msg_lower for keyword in [
                "سود و زیان", "profit", "loss", "expense", "cost", "income", "revenue",
                "cash flow", "جریان نقد", "vendor", "فروشنده", "monthly", "ماهانه",
                "tax", "مالیات", "vat", "ارزش افزوده"
            ]))
        )
        
        if is_report_query:
            # Get available reports
            from finance.agents.reporting_agent import ReportingAgent
            from finance.database import FinanceDatabase
            from langchain_openai import ChatOpenAI
            from config import FINANCE_MODEL, OPENAI_API_KEY
            
            reporting_agent = ReportingAgent(
                ChatOpenAI(api_key=OPENAI_API_KEY, model=FINANCE_MODEL),
                FinanceDatabase()
            )
            report_list = reporting_agent.list_available_reports()
            response_data['reports'] = report_list.get('reports', {})
            response_data['show_report_buttons'] = True
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"[FINANCE ERROR] Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا: {str(e)}'}), 500


@app.route('/api/finance/upload', methods=['POST'])
def finance_upload():
    """Upload receipt/invoice for processing"""
    if finance_agent is None:
        return jsonify({
            'error': 'Finance Agent is not available.'
        }), 503
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'فایلی انتخاب نشده است'}), 400
        
        # Validate file extension
        allowed_extensions = {'.pdf', '.jpg', '.jpeg', '.png'}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            return jsonify({
                'error': f'فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: {", ".join(allowed_extensions)}'
            }), 400
        
        # Save uploaded file temporarily
        from werkzeug.utils import secure_filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        temp_path = UPLOAD_PATH / unique_filename
        
        file.save(str(temp_path))
        print(f"[FINANCE INFO] File saved temporarily: {temp_path}")
        
        # Process document with finance agent
        user_id = session.get('user_id', 'default')
        result = finance_agent.upload_document(
            file_path=str(temp_path),
            user_id=user_id,
            doc_type="auto"
        )
        
        # Clean up temp file
        try:
            temp_path.unlink()
        except Exception as e:
            print(f"Warning: Could not delete temp file: {e}")
        
        if result.get('success'):
            # Format response message
            data = result.get('data', {})
            message = f"✅ سند با موفقیت پردازش شد!\n\n"
            
            if data.get('vendor'):
                message += f"📍 فروشنده: {data['vendor']}\n"
            if data.get('amount'):
                message += f"💰 مبلغ: {data['amount']:,} {data.get('currency', 'ریال')}\n"
            if data.get('date'):
                message += f"📅 تاریخ: {data['date']}\n"
            
            message += f"\n🎯 اطمینان: {result.get('confidence', 0)*100:.0f}%"
            
            return jsonify({
                'success': True,
                'response': message,
                'data': data,
                'document_id': result.get('document_id'),
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'response': result.get('message', 'خطا در پردازش سند'),
                'error': result.get('error')
            })
    
    except Exception as e:
        print(f"[FINANCE ERROR] Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا در بارگذاری: {str(e)}'}), 500


@app.route('/api/finance/transactions', methods=['GET'])
def get_finance_transactions():
    """Get transaction list with filters"""
    if finance_agent is None:
        return jsonify({'error': 'Finance Agent is not available.'}), 503
    
    try:
        user_id = session.get('user_id', 'default')
        filters = request.args.to_dict()
        
        transactions = finance_agent.get_transactions(filters, user_id=user_id)
        
        return jsonify({
            'transactions': transactions,
            'count': len(transactions)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/finance/balance', methods=['GET'])
def get_finance_balance():
    """Get current balance summary"""
    if finance_agent is None:
        return jsonify({'error': 'Finance Agent is not available.'}), 503
    
    try:
        user_id = session.get('user_id', 'default')
        balance = finance_agent.get_balance(user_id=user_id)
        
        return jsonify(balance)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/finance/clear', methods=['POST'])
def clear_finance_session():
    """Clear Finance agent conversation session"""
    if finance_agent is None:
        return jsonify({'error': 'Finance Agent is not available.'}), 503
    
    try:
        user_id = session.get('user_id', 'default')
        
        # Create a new thread ID
        new_thread_id = f"finance_{uuid.uuid4()}"
        finance_sessions[user_id] = new_thread_id
        
        # Reset conversation in agent
        finance_agent.reset_conversation(thread_id=new_thread_id)
        
        return jsonify({
            'success': True,
            'message': 'گفتگو پاک شد'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/finance/accounts', methods=['POST'])
def create_finance_account():
    """Create a new account"""
    if finance_agent is None:
        return jsonify({'error': 'Finance Agent is not available.'}), 503
    
    try:
        data = request.json
        user_id = session.get('user_id', 'default')
        
        name = data.get('name', '').strip()
        account_type = data.get('type', 'bank')  # bank, cash, credit_card
        currency = data.get('currency', 'IRR')
        initial_balance = float(data.get('initial_balance', 0))
        
        if not name:
            return jsonify({'error': 'نام حساب الزامی است'}), 400
        
        if account_type not in ['bank', 'cash', 'credit_card']:
            return jsonify({'error': 'نوع حساب نامعتبر است'}), 400
        
        result = finance_agent.create_account(
            user_id=user_id,
            name=name,
            account_type=account_type,
            currency=currency,
            initial_balance=initial_balance
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': result.get('message', 'حساب با موفقیت ایجاد شد'),
                'account': result.get('account')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'خطای نامشخص')
            }), 400
    
    except Exception as e:
        print(f"[FINANCE ERROR] Account creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'خطا در ایجاد حساب: {str(e)}'}), 500


@app.route('/api/finance/accounts', methods=['GET'])
def list_finance_accounts():
    """List all accounts"""
    if finance_agent is None:
        return jsonify({'error': 'Finance Agent is not available.'}), 503
    
    try:
        user_id = session.get('user_id', 'default')
        result = finance_agent.list_accounts(user_id=user_id)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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




"""
🔥 RAG Agent Web UI
Beautiful Flask-based web interface for document RAG agent
Supports file upload, chat interface, document management
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import uuid
from datetime import datetime

from rag_agent import get_rag_agent
from document_processor import get_document_processor, get_storage_manager
import rag_agent_config as config

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rag-agent-secret-key-' + str(uuid.uuid4())
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = config.UPLOAD_DIR

# Initialize agent
agent = get_rag_agent()
storage_manager = get_storage_manager()


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main page"""
    return render_template('rag_agent.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload document endpoint
    Accepts: multipart/form-data with 'file' field
    Returns: JSON with upload result
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'هیچ فایلی انتخاب نشده است'
            }), 400
        
        file = request.files['file']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'نام فایل خالی است'
            }), 400
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in config.SUPPORTED_FORMATS:
            return jsonify({
                'success': False,
                'error': f'فرمت فایل پشتیبانی نمی‌شود. فرمت‌های مجاز: {", ".join(config.SUPPORTED_FORMATS.keys())}'
            }), 400
        
        # Save file
        file_data = file.read()
        file_path = storage_manager.save_file(file_data, filename)
        
        # Upload to agent
        result = agent.upload_document(str(file_path))
        
        return jsonify({
            'success': result['success'],
            'message': result['response'],
            'document_id': result.get('document_id'),
            'filename': filename
        })
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return jsonify({
            'success': False,
            'error': f'خطا در آپلود فایل: {str(e)}'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat endpoint
    Accepts: JSON with 'query' and optional 'document_id'
    Returns: JSON with agent response
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'لطفاً یک سؤال وارد کنید'
            }), 400
        
        query = data['query'].strip()
        document_id = data.get('document_id')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'سؤال خالی است'
            }), 400
        
        # Process query
        result = agent.process_query(query, document_id)
        
        return jsonify({
            'success': True,
            'response': result['response'],
            'action_type': result['action_type'],
            'metadata': result['metadata']
        })
    
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            'success': False,
            'error': f'خطا در پردازش سؤال: {str(e)}'
        }), 500


@app.route('/api/documents', methods=['GET'])
def list_documents():
    """
    List all documents endpoint
    Returns: JSON with document list
    """
    try:
        result = agent.list_documents()
        
        return jsonify({
            'success': result['success'],
            'response': result['response']
        })
    
    except Exception as e:
        print(f"❌ List documents error: {e}")
        return jsonify({
            'success': False,
            'error': f'خطا در دریافت لیست اسناد: {str(e)}'
        }), 500


@app.route('/api/document/<document_id>/summary', methods=['POST'])
def summarize_document(document_id):
    """
    Summarize document endpoint
    Returns: JSON with summary
    """
    try:
        query = f"یک خلاصه جامع از سند با شناسه {document_id} ایجاد کن"
        
        result = agent.process_query(query, document_id)
        
        return jsonify({
            'success': True,
            'summary': result['response'],
            'metadata': result['metadata']
        })
    
    except Exception as e:
        print(f"❌ Summary error: {e}")
        return jsonify({
            'success': False,
            'error': f'خطا در ایجاد خلاصه: {str(e)}'
        }), 500


@app.route('/api/document/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """
    Delete document endpoint
    Returns: JSON with deletion result
    """
    try:
        query = f"حذف سند با شناسه {document_id}"
        
        result = agent.process_query(query, document_id)
        
        return jsonify({
            'success': True,
            'message': result['response']
        })
    
    except Exception as e:
        print(f"❌ Delete error: {e}")
        return jsonify({
            'success': False,
            'error': f'خطا در حذف سند: {str(e)}'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'agent': 'RAG Agent',
        'version': '1.0.0',
        'vector_db': config.VECTOR_DB_TYPE,
        'llm_model': config.LLM_MODEL
    })


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'صفحه مورد نظر یافت نشد'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطای داخلی سرور'}), 500


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'حجم فایل بیش از حد مجاز است (حداکثر 50MB)'}), 413


# ==================== MAIN ====================

def main():
    """Start Flask server"""
    print("\n" + "="*60)
    print("🔥 RAG AGENT WEB UI")
    print("="*60)
    print(f"\n✅ Server starting on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print(f"✅ Vector DB: {config.VECTOR_DB_TYPE}")
    print(f"✅ LLM Model: {config.LLM_MODEL}")
    print(f"\n📂 Upload directory: {config.UPLOAD_DIR}")
    print(f"🌐 Open your browser and navigate to: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    print("\n" + "="*60 + "\n")
    
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()


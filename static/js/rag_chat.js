/**
 * RAG Chat Interface JavaScript
 * Handles document uploads, chat messages, and UI interactions
 */

// DOM Elements
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const uploadBtn = document.getElementById('uploadBtn');
const fileInput = document.getElementById('fileInput');
const chatContainer = document.getElementById('chatContainer');
const loadingIndicator = document.getElementById('loadingIndicator');
const uploadModal = document.getElementById('uploadModal');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const themeToggle = document.getElementById('themeToggle');

// State
let isProcessing = false;

// ==================== THEME MANAGEMENT ====================
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.classList.toggle('dark-mode', savedTheme === 'dark');
    updateThemeIcon();
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const theme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    updateThemeIcon();
}

function updateThemeIcon() {
    const icon = themeToggle.querySelector('i');
    if (document.body.classList.contains('dark-mode')) {
        icon.className = 'fas fa-sun';
    } else {
        icon.className = 'fas fa-moon';
    }
}

// ==================== MESSAGE RENDERING ====================
function addMessage(content, isUser = false) {
    // Remove welcome section if exists
    const welcomeSection = chatContainer.querySelector('.welcome-section');
    if (welcomeSection) {
        welcomeSection.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? 
        '<i class="fas fa-user"></i>' : 
        '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Format content with markdown-style support
    const formattedContent = formatMessage(content);
    contentDiv.innerHTML = formattedContent;
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString('fa-IR', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    contentDiv.appendChild(timestamp);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

function formatMessage(content) {
    // Simple formatting
    let formatted = content
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Code blocks
        .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        // Line breaks
        .replace(/\n/g, '<br>');
    
    return formatted;
}

function showLoading() {
    loadingIndicator.style.display = 'flex';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

// ==================== CHAT FUNCTIONALITY ====================
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) return;
    
    isProcessing = true;
    messageInput.value = '';
    messageInput.style.height = 'auto';
    
    // Add user message
    addMessage(message, true);
    
    // Show loading
    showLoading();
    
    try {
        const response = await fetch('/api/rag/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('خطا در دریافت پاسخ');
        }
        
        const data = await response.json();
        
        // Add AI response
        addMessage(data.response, false);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage('❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.', false);
    } finally {
        hideLoading();
        isProcessing = false;
        messageInput.focus();
    }
}

// ==================== FILE UPLOAD ====================
function showUploadModal() {
    uploadModal.classList.add('active');
}

function hideUploadModal() {
    uploadModal.classList.remove('active');
}

function updateProgress(percent, text) {
    progressFill.style.width = percent + '%';
    progressText.textContent = text;
}

async function uploadFile(file) {
    if (!file) return;
    
    // Show upload modal
    showUploadModal();
    updateProgress(0, 'آماده‌سازی...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        updateProgress(30, 'در حال بارگذاری...');
        
        const response = await fetch('/api/rag/upload', {
            method: 'POST',
            body: formData
        });
        
        updateProgress(60, 'در حال پردازش سند...');
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'خطا در بارگذاری');
        }
        
        const data = await response.json();
        
        updateProgress(100, 'تکمیل شد!');
        
        // Hide modal after a short delay
        setTimeout(() => {
            hideUploadModal();
            
            // Add upload success message
            addMessage(`📤 فایل بارگذاری شد: ${data.filename}`, true);
            addMessage(data.response, false);
        }, 500);
        
    } catch (error) {
        console.error('Upload error:', error);
        hideUploadModal();
        addMessage(`❌ خطا در بارگذاری فایل: ${error.message}`, false);
    }
}

// ==================== CLEAR CHAT ====================
async function clearChat() {
    if (!confirm('آیا می‌خواهید گفتگو را پاک کنید؟')) {
        return;
    }
    
    try {
        const response = await fetch('/api/rag/clear', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Clear chat container
            chatContainer.innerHTML = '';
            
            // Re-add welcome section
            location.reload();
        }
    } catch (error) {
        console.error('Clear error:', error);
    }
}

// ==================== EVENT LISTENERS ====================

// Send message
sendBtn.addEventListener('click', sendMessage);

// Enter key to send (Shift+Enter for new line)
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Auto-resize textarea
messageInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 150) + 'px';
});

// Upload button
if (uploadBtn) {
    uploadBtn.addEventListener('click', function() {
        fileInput.click();
    });
}

// File input change
if (fileInput) {
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            uploadFile(file);
            // Reset input
            this.value = '';
        }
    });
}

// Clear button
clearBtn.addEventListener('click', clearChat);

// Theme toggle
themeToggle.addEventListener('click', toggleTheme);

// Quick action cards
document.addEventListener('click', function(e) {
    const actionCard = e.target.closest('.action-card');
    if (actionCard) {
        const prompt = actionCard.getAttribute('data-prompt');
        if (prompt) {
            messageInput.value = prompt;
            sendMessage();
        }
    }
});

// ==================== INITIALIZATION ====================
initTheme();
messageInput.focus();

// Welcome message hint
console.log('🤖 دستیار RAG آماده است!');
console.log('📄 شما می‌توانید اسناد را بارگذاری کرده و سوالات خود را بپرسید.');


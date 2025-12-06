// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
});

// ==================== VARIABLES ====================
const chatContainer = document.getElementById('chatContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const clearBtn = document.getElementById('clearBtn');
const themeToggle = document.getElementById('themeToggle');
const loadingIndicator = document.getElementById('loadingIndicator');

let isWaitingForResponse = false;
let messageHistory = [];

// ==================== INITIALIZE ====================
function initializeChat() {
    // Load theme preference
    loadThemePreference();
    
    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    clearBtn.addEventListener('click', clearConversation);
    themeToggle.addEventListener('click', toggleTheme);
    
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Auto-resize textarea
    messageInput.addEventListener('input', autoResizeTextarea);
    
    // Quick action buttons
    document.querySelectorAll('.action-card').forEach(card => {
        card.addEventListener('click', () => {
            const prompt = card.getAttribute('data-prompt');
            messageInput.value = prompt;
            sendMessage();
        });
    });
    
    // Focus on input
    messageInput.focus();
}

// ==================== THEME ====================
function toggleTheme() {
    const body = document.body;
    const isDarkMode = body.classList.toggle('dark-mode');
    
    // Update icon
    const icon = themeToggle.querySelector('i');
    icon.classList.toggle('fa-moon', !isDarkMode);
    icon.classList.toggle('fa-sun', isDarkMode);
    
    // Save preference
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
}

function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        const icon = themeToggle.querySelector('i');
        icon.classList.remove('fa-moon');
        icon.classList.add('fa-sun');
    }
}

// ==================== MESSAGE HANDLING ====================
async function sendMessage() {
    if (isWaitingForResponse) return;
    
    const message = messageInput.value.trim();
    if (!message) return;
    
    // Hide welcome section if visible
    const welcomeSection = document.querySelector('.welcome-section');
    if (welcomeSection) {
        welcomeSection.style.display = 'none';
    }
    
    // Clear input
    messageInput.value = '';
    autoResizeTextarea();
    
    // Add user message to UI
    addMessage(message, 'user');
    
    // Show loading
    showLoading();
    isWaitingForResponse = true;
    sendBtn.disabled = true;
    
    try {
        // Send to backend
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Hide loading
        hideLoading();
        
        // Add AI response to UI
        addMessage(data.response, 'ai', data.is_confirmation, data.timestamp);
        
        // Store in history
        messageHistory.push({
            user: message,
            ai: data.response,
            timestamp: data.timestamp
        });
        
    } catch (error) {
        hideLoading();
        addMessage('❌ متأسفم، خطایی رخ داد. لطفاً دوباره تلاش کنید.', 'ai', false);
        console.error('Error:', error);
    } finally {
        isWaitingForResponse = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
}

function addMessage(content, type, isConfirmation = false, timestamp = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    // Format content with markdown-style formatting
    bubble.innerHTML = formatMessage(content);
    
    // Add confirmation badge if needed
    if (isConfirmation) {
        const badge = document.createElement('div');
        badge.className = 'confirmation-badge';
        badge.innerHTML = '<i class="fas fa-exclamation-circle"></i> در انتظار تأیید';
        contentDiv.appendChild(badge);
    }
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = timestamp || getCurrentTime();
    
    contentDiv.appendChild(bubble);
    contentDiv.appendChild(timeDiv);
    
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentDiv);
    
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    scrollToBottom();
}

function formatMessage(text) {
    // Convert markdown-style formatting to HTML
    let formatted = text
        // Bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Emoji and icons
        .replace(/✅/g, '<span style="color: #10a37f;">✅</span>')
        .replace(/❌/g, '<span style="color: #ef4444;">❌</span>')
        .replace(/⚠️/g, '<span style="color: #f59e0b;">⚠️</span>')
        .replace(/📅/g, '<span style="color: #3b82f6;">📅</span>')
        .replace(/📋/g, '<span style="color: #8b5cf6;">📋</span>')
        // Preserve line breaks
        .replace(/\n/g, '<br>');
    
    return formatted;
}

function getCurrentTime() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
    });
}

// ==================== CLEAR CONVERSATION ====================
async function clearConversation() {
    if (!confirm('آیا مطمئن هستید که می‌خواهید گفتگو را پاک کنید؟')) {
        return;
    }
    
    try {
        const response = await fetch('/api/clear', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            // Clear messages
            const messages = chatContainer.querySelectorAll('.message');
            messages.forEach(msg => msg.remove());
            
            // Show welcome section again
            const welcomeSection = document.querySelector('.welcome-section');
            if (welcomeSection) {
                welcomeSection.style.display = 'block';
            }
            
            // Clear history
            messageHistory = [];
            
            // Show success message temporarily
            showNotification('گفتگو با موفقیت پاک شد!', 'success');
        }
    } catch (error) {
        console.error('Error clearing conversation:', error);
        showNotification('خطا در پاک کردن گفتگو', 'error');
    }
}

// ==================== UI UTILITIES ====================
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai loading-message';
    loadingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="message-bubble">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    scrollToBottom();
}

function hideLoading() {
    const loadingMessage = chatContainer.querySelector('.loading-message');
    if (loadingMessage) {
        loadingMessage.remove();
    }
}

function scrollToBottom() {
    setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 100);
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    messageInput.style.height = Math.min(messageInput.scrollHeight, 150) + 'px';
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10a37f' : '#ef4444'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== ANIMATIONS ====================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);









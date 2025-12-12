/**
 * Finance Chat Interface JavaScript
 * Handles receipt/invoice uploads, chat messages, and finance-specific UI interactions
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
const createAccountModal = document.getElementById('createAccountModal');
const createAccountBtn = document.getElementById('createAccountBtn');
const closeAccountModal = document.getElementById('closeAccountModal');
const cancelAccountBtn = document.getElementById('cancelAccountBtn');
const createAccountForm = document.getElementById('createAccountForm');

// Date Period Modal Elements
const datePeriodModal = document.getElementById('datePeriodModal');
const datePeriodForm = document.getElementById('datePeriodForm');
const dateFromInput = document.getElementById('dateFrom');
const dateToInput = document.getElementById('dateTo');
const closeDateModal = document.getElementById('closeDateModal');
const cancelDateBtn = document.getElementById('cancelDateBtn');
// Quick date buttons will be handled via event delegation

// Store current report request
let currentReportRequest = null;

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
    messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = isUser ? 
        '<i class="fas fa-user"></i>' : 
        '<i class="fas fa-coins"></i>';
    
    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content';

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.innerHTML = formatMessage(content);

    const timestamp = document.createElement('div');
    timestamp.className = 'message-time';
    timestamp.textContent = new Date().toLocaleTimeString('fa-IR', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    contentWrapper.appendChild(bubble);
    contentWrapper.appendChild(timestamp);
    messageDiv.appendChild(avatar);
    messageDiv.appendChild(contentWrapper);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

function formatMessage(content) {
    // Split into lines first to preserve structure
    const lines = content.split('\n');
    const formattedLines = [];
    
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        const originalLine = line;
        
        // Skip empty lines but preserve them
        if (line.trim() === '') {
            formattedLines.push('<br>');
            continue;
        }
        
        // Headers (lines with emoji at start like 📊 or 💡)
        if (/^[📊💡]/.test(line)) {
            // Apply markdown formatting first
            line = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            line = '<div style="margin: 16px 0 8px 0; font-weight: 600; font-size: 1.1em;">' + line + '</div>';
        }
        // Numbered list items with bold (e.g., **1. Report Name** (English))
        else if (/^\*\*\d+\.\s+/.test(originalLine)) {
            // Apply markdown formatting
            line = line
                .replace(/\*\*(\d+)\.\s+(.+?)\*\*\s*(\(.+?\))?/g, '<strong>$1. $2</strong> $3');
            line = '<div style="margin: 12px 0 4px 0; font-weight: 600; line-height: 1.6;">' + line + '</div>';
        }
        // Indented lines (descriptions starting with spaces or emoji like 📝)
        else if (/^\s{2,}/.test(originalLine) || /^[📝]/.test(originalLine)) {
            // Apply markdown formatting
            line = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            line = '<div style="margin: 4px 0 8px 24px; color: #666; font-size: 0.95em; line-height: 1.5;">' + line.trim() + '</div>';
        }
        // Bullet points
        else if (/^•\s+/.test(originalLine)) {
            // Apply markdown formatting
            line = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            line = '<div style="margin: 4px 0; padding-right: 16px; line-height: 1.5;">' + line + '</div>';
        }
        // Regular lines
        else {
            // Apply all markdown formatting
            line = line
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/```(.*?)```/gs, '<pre><code>$1</code></pre>')
                .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
            line = '<div style="margin: 4px 0; line-height: 1.5;">' + line + '</div>';
        }
        
        formattedLines.push(line);
    }
    
    return formattedLines.join('');
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
        const response = await fetch('/api/finance/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'خطا در دریافت پاسخ');
        }
        
        const data = await response.json();
        
        // Add AI response
        const messageDiv = addMessage(data.response, false);
        
        // If reports are available, add report selection buttons
        if (data.show_report_buttons && data.reports) {
            addReportButtons(messageDiv, data.reports);
        }
        
    } catch (error) {
        console.error('Error:', error);
        addMessage(`❌ خطایی رخ داد: ${error.message}`, false);
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
    
    // Validate file type
    const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
    if (!allowedTypes.includes(file.type)) {
        addMessage('❌ فرمت فایل پشتیبانی نمی‌شود. لطفاً فایل PDF یا تصویر (JPG, PNG) انتخاب کنید.', false);
        return;
    }
    
    // Show upload modal
    showUploadModal();
    updateProgress(0, 'آماده‌سازی...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        updateProgress(30, 'در حال بارگذاری...');
        
        const response = await fetch('/api/finance/upload', {
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
            addMessage(`📎 فایل بارگذاری شد: ${data.filename || file.name}`, true);
            
            // Display the response from finance agent
            if (data.success) {
                addMessage(data.response || '✅ سند با موفقیت پردازش شد!', false);
                
                // If there's extracted data, format it nicely
                if (data.data) {
                    let dataMessage = '📊 **اطلاعات استخراج شده:**\n\n';
                    if (data.data.vendor) dataMessage += `📍 فروشنده: ${data.data.vendor}\n`;
                    if (data.data.amount) dataMessage += `💰 مبلغ: ${data.data.amount.toLocaleString('fa-IR')} ${data.data.currency || 'ریال'}\n`;
                    if (data.data.date) dataMessage += `📅 تاریخ: ${data.data.date}\n`;
                    if (data.confidence) dataMessage += `\n🎯 اطمینان: ${(data.confidence * 100).toFixed(0)}%`;
                    addMessage(dataMessage, false);
                }
            } else {
                addMessage(data.response || data.message || '⚠️ خطا در پردازش سند', false);
            }
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
        const response = await fetch('/api/finance/clear', {
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
        addMessage('❌ خطا در پاک کردن گفتگو', false);
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

// ==================== ACCOUNT CREATION MODAL ====================
function showCreateAccountModal() {
    createAccountModal.classList.add('active');
    document.getElementById('accountName').focus();
}

function hideCreateAccountModal() {
    createAccountModal.classList.remove('active');
    createAccountForm.reset();
}

// Open account creation modal
if (createAccountBtn) {
    createAccountBtn.addEventListener('click', function(e) {
        e.preventDefault();
        showCreateAccountModal();
    });
}

// Close modal handlers
if (closeAccountModal) {
    closeAccountModal.addEventListener('click', hideCreateAccountModal);
}

if (cancelAccountBtn) {
    cancelAccountBtn.addEventListener('click', hideCreateAccountModal);
}

// Close modal on outside click
if (createAccountModal) {
    createAccountModal.addEventListener('click', function(e) {
        if (e.target === createAccountModal) {
            hideCreateAccountModal();
        }
    });
}

// Handle account creation form submission
if (createAccountForm) {
    createAccountForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('accountName').value.trim(),
            type: document.getElementById('accountType').value,
            currency: document.getElementById('accountCurrency').value,
            initial_balance: parseFloat(document.getElementById('initialBalance').value) || 0
        };
        
        // Convert toman to rial if needed
        const unit = document.getElementById('balanceUnit').value;
        if (unit === 'toman' && formData.currency === 'IRR') {
            formData.initial_balance = formData.initial_balance * 10;
        }
        
        if (!formData.name) {
            alert('لطفاً نام حساب را وارد کنید');
            return;
        }
        
        // Show loading
        const submitBtn = createAccountForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = 'در حال ایجاد...';
        
        try {
            const response = await fetch('/api/finance/accounts', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Close modal
                hideCreateAccountModal();
                
                // Remove welcome section
                const welcomeSection = chatContainer.querySelector('.welcome-section');
                if (welcomeSection) {
                    welcomeSection.remove();
                }
                
                // Show success message
                addMessage(`📝 درخواست ایجاد حساب: ${formData.name}`, true);
                addMessage(data.message || '✅ حساب با موفقیت ایجاد شد', false);
                
                // If account details provided, show them
                if (data.account) {
                    const accountInfo = `📊 **اطلاعات حساب:**\n\n` +
                        `- نام: ${data.account.name}\n` +
                        `- نوع: ${data.account.type === 'bank' ? 'بانکی' : data.account.type === 'cash' ? 'نقدی' : 'کارت اعتباری'}\n` +
                        `- موجودی: ${data.account.balance.toLocaleString('fa-IR')} ${data.account.currency}`;
                    addMessage(accountInfo, false);
                }
            } else {
                alert(`خطا: ${data.error || 'خطای نامشخص'}`);
            }
        } catch (error) {
            console.error('Account creation error:', error);
            alert(`خطا در ایجاد حساب: ${error.message}`);
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    });
}

// ==================== REPORT BUTTONS ====================
function addReportButtons(messageDiv, reports) {
    const buttonContainer = document.createElement('div');
    buttonContainer.className = 'report-buttons-container';
    buttonContainer.style.cssText = 'margin-top: 16px; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;';
    
    let reportNum = 1;
    for (const [reportId, reportInfo] of Object.entries(reports)) {
        const button = document.createElement('button');
        button.className = 'report-button';
        button.style.cssText = 'padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; text-align: right; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);';
        button.innerHTML = `<strong>${reportNum}. ${reportInfo.name}</strong><br><small style="font-size: 11px; opacity: 0.9;">${reportInfo.name_en}</small>`;
        
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        });
        
        button.addEventListener('click', function() {
            showDatePeriodModal(reportId, reportInfo.name);
        });
        
        buttonContainer.appendChild(button);
        reportNum++;
    }
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (contentDiv) {
        contentDiv.appendChild(buttonContainer);
    }
}

// ==================== DATE PERIOD SELECTOR ====================
let dateFromPicker = null;
let dateToPicker = null;

function showDatePeriodModal(reportType, reportName) {
    currentReportRequest = { reportType, reportName };
    
    // Set default dates (current month in Jalali)
    const today = new Date();
    const todayJalali = new persianDate(today);
    const currentYear = todayJalali.year();
    const currentMonth = todayJalali.month() + 1; // persianDate months are 0-11
    
    // Create first and last day of current month
    const firstDay = new persianDate([currentYear, currentMonth, 1]);
    const daysInMonth = firstDay.daysInMonth();
    const lastDay = new persianDate([currentYear, currentMonth, daysInMonth]);
    
    const firstDayStr = firstDay.format('YYYY/MM/DD');
    const lastDayStr = lastDay.format('YYYY/MM/DD');
    
    // Clean up existing pickers
    if (dateFromPicker) {
        try {
            if (typeof $ !== 'undefined' && $(dateFromInput).data('datepicker')) {
                $(dateFromInput).datepicker('destroy');
            }
        } catch(e) {
            console.log('Error destroying dateFromPicker:', e);
        }
        dateFromPicker = null;
    }
    if (dateToPicker) {
        try {
            if (typeof $ !== 'undefined' && $(dateToInput).data('datepicker')) {
                $(dateToInput).datepicker('destroy');
            }
        } catch(e) {
            console.log('Error destroying dateToPicker:', e);
        }
        dateToPicker = null;
    }
    
    dateFromInput.value = firstDayStr;
    dateToInput.value = lastDayStr;
    
    // Show modal first
    datePeriodModal.classList.add('active');
    
    // Initialize pickers after modal is shown and jQuery is ready
    setTimeout(() => {
        try {
            if (typeof $ !== 'undefined' && $.fn.pDatepicker) {
                // Use Bootstrap Persian DateTime Picker
                $(dateFromInput).pDatepicker({
                    format: 'YYYY/MM/DD',
                    altField: dateFromInput,
                    altFormat: 'YYYY/MM/DD',
                    observer: true,
                    calendarType: 'persian',
                    timePicker: {
                        enabled: false
                    },
                    initialValue: true,
                    onSelect: function(selectedDate) {
                        if (selectedDate) {
                            const pd = new persianDate(selectedDate);
                            dateFromInput.value = pd.format('YYYY/MM/DD');
                        }
                    }
                });
                
                $(dateToInput).pDatepicker({
                    format: 'YYYY/MM/DD',
                    altField: dateToInput,
                    altFormat: 'YYYY/MM/DD',
                    observer: true,
                    calendarType: 'persian',
                    timePicker: {
                        enabled: false
                    },
                    initialValue: true,
                    onSelect: function(selectedDate) {
                        if (selectedDate) {
                            const pd = new persianDate(selectedDate);
                            dateToInput.value = pd.format('YYYY/MM/DD');
                        }
                    }
                });
                
                dateFromPicker = $(dateFromInput);
                dateToPicker = $(dateToInput);
            } else if (typeof persianDate !== 'undefined') {
                // Fallback: Create custom calendar using persianDate
                console.log('Creating custom Jalali calendar picker');
                initializeCustomJalaliCalendar();
            } else {
                console.warn('No Persian date library found. Allowing manual input.');
                dateFromInput.removeAttribute('readonly');
                dateToInput.removeAttribute('readonly');
                dateFromInput.placeholder = '1403/01/01 (فرمت: سال/ماه/روز)';
                dateToInput.placeholder = '1403/01/31 (فرمت: سال/ماه/روز)';
            }
        } catch (error) {
            console.error('Error initializing date picker:', error);
            // Fallback: Use custom calendar
            initializeCustomJalaliCalendar();
        }
    }, 300);
    
    dateFromInput.focus();
}

// Custom Jalali Calendar Picker
function initializeCustomJalaliCalendar() {
    dateFromInput.addEventListener('click', function(e) {
        e.preventDefault();
        showJalaliCalendar(this);
    });
    dateToInput.addEventListener('click', function(e) {
        e.preventDefault();
        showJalaliCalendar(this);
    });
}

function showJalaliCalendar(inputElement) {
    // Remove existing calendar if any
    const existingCalendar = document.getElementById('jalaliCalendarPopup');
    if (existingCalendar) {
        existingCalendar.remove();
    }
    
    // Get current date or default
    let currentDate;
    if (inputElement.value && inputElement.value.trim()) {
        const parts = inputElement.value.split('/');
        if (parts.length === 3) {
            const year = parseInt(parts[0]);
            const month = parseInt(parts[1]);
            const day = parseInt(parts[2]);
            if (!isNaN(year) && !isNaN(month) && !isNaN(day) && year > 1300 && year < 1500) {
                currentDate = new persianDate([year, month, day]);
            } else {
                // Invalid date, use today
                const today = new Date();
                currentDate = new persianDate(today);
            }
        } else {
            // Invalid format, use today
            const today = new Date();
            currentDate = new persianDate(today);
        }
    } else {
        // No value, use today
        const today = new Date();
        currentDate = new persianDate(today);
    }
    
    // Validate the date is reasonable
    const year = currentDate.year();
    if (year < 1400 || year > 1500) {
        // Date seems wrong, force to today
        const today = new Date();
        currentDate = new persianDate(today);
    }
    
    // Create calendar popup
    const calendar = createJalaliCalendarHTML(currentDate, inputElement);
    document.body.appendChild(calendar);
    
    // Position calendar near input
    const rect = inputElement.getBoundingClientRect();
    calendar.style.position = 'fixed';
    calendar.style.top = (rect.bottom + 5) + 'px';
    calendar.style.left = Math.max(10, rect.left - 100) + 'px';
    calendar.style.zIndex = '10000';
    
    // Close calendar when clicking outside
    setTimeout(() => {
        document.addEventListener('click', function closeCalendar(e) {
            if (!calendar.contains(e.target) && e.target !== inputElement) {
                calendar.remove();
                document.removeEventListener('click', closeCalendar);
            }
        });
    }, 100);
}

function createJalaliCalendarHTML(currentDate, inputElement) {
    const calendar = document.createElement('div');
    calendar.id = 'jalaliCalendarPopup';
    calendar.className = 'jalali-calendar-popup';
    
    const year = currentDate.year();
    const month = currentDate.month() + 1; // persianDate months are 0-11
    const day = currentDate.date();
    
    // Persian month names
    const monthNames = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                       'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'];
    const weekDays = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
    
    // Get first day of month
    const firstDay = new persianDate([year, month, 1]);
    const firstDayOfWeek = firstDay.day(); // 0 = Saturday, 6 = Friday
    const daysInMonth = firstDay.daysInMonth();
    
    let html = `
        <div style="background: white; border: 2px solid var(--accent-primary); border-radius: 8px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); min-width: 300px; font-family: 'Vazirmatn', sans-serif; direction: rtl; z-index: 10000;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #e0e0e0;">
                <button class="calendar-nav-btn" data-action="prev-month" style="background: var(--accent-primary); color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600;">‹ قبلی</button>
                <div style="font-weight: 700; font-size: 18px; color: #1a1a1a;">
                    ${monthNames[month - 1]} ${year}
                </div>
                <button class="calendar-nav-btn" data-action="next-month" style="background: var(--accent-primary); color: white; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 600;">بعدی ›</button>
            </div>
            <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; margin-bottom: 12px;">
    `;
    
    // Week day headers
    for (let i = 0; i < 7; i++) {
        html += `<div style="text-align: center; font-weight: 700; padding: 10px 4px; font-size: 13px; color: #666; background: #f5f5f5; border-radius: 4px;">${weekDays[i]}</div>`;
    }
    
    // Empty cells for days before month starts
    for (let i = 0; i < firstDayOfWeek; i++) {
        html += `<div style="padding: 8px;"></div>`;
    }
    
    // Days of month
    const today = new Date();
    const todayJalali = new persianDate(today);
    const todayYear = todayJalali.year();
    const todayMonth = todayJalali.month() + 1;
    const todayDay = todayJalali.date();
    
    for (let d = 1; d <= daysInMonth; d++) {
        const isToday = (d === todayDay && month === todayMonth && year === todayYear);
        const cellStyle = isToday 
            ? 'background: var(--accent-primary); color: white; font-weight: 600;'
            : 'background: var(--bg-primary); color: var(--text-primary);';
        
        html += `
            <button class="calendar-day-btn" data-day="${d}" 
                style="${cellStyle} border: 1px solid var(--border-color); padding: 8px; border-radius: 4px; cursor: pointer; font-size: 14px; transition: all 0.2s;"
                onmouseover="this.style.background='var(--accent-primary)'; this.style.color='white';"
                onmouseout="this.style.background='${isToday ? 'var(--accent-primary)' : 'var(--bg-primary)'}'; this.style.color='${isToday ? 'white' : 'var(--text-primary)'}';">
                ${d}
            </button>
        `;
    }
    
    html += `
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border-color); text-align: center;">
                <button class="calendar-today-btn" style="background: var(--accent-primary); color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;">امروز</button>
            </div>
        </div>
    `;
    
    calendar.innerHTML = html;
    calendar.currentYear = year;
    calendar.currentMonth = month;
    calendar.inputElement = inputElement;
    
    // Add event listeners
    calendar.querySelectorAll('.calendar-day-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const selectedDay = parseInt(this.getAttribute('data-day'));
            const selectedDate = new persianDate([calendar.currentYear, calendar.currentMonth, selectedDay]);
            inputElement.value = selectedDate.format('YYYY/MM/DD');
            calendar.remove();
        });
    });
    
    calendar.querySelector('.calendar-today-btn').addEventListener('click', function() {
        const today = new Date();
        const todayJalali = new persianDate(today);
        inputElement.value = todayJalali.format('YYYY/MM/DD');
        calendar.remove();
    });
    
    calendar.querySelector('[data-action="prev-month"]').addEventListener('click', function() {
        let newMonth = calendar.currentMonth - 1;
        let newYear = calendar.currentYear;
        if (newMonth < 1) {
            newMonth = 12;
            newYear--;
        }
        const newDate = new persianDate([newYear, newMonth, 1]);
        const newCalendar = createJalaliCalendarHTML(newDate, inputElement);
        calendar.parentNode.replaceChild(newCalendar, calendar);
    });
    
    calendar.querySelector('[data-action="next-month"]').addEventListener('click', function() {
        let newMonth = calendar.currentMonth + 1;
        let newYear = calendar.currentYear;
        if (newMonth > 12) {
            newMonth = 1;
            newYear++;
        }
        const newDate = new persianDate([newYear, newMonth, 1]);
        const newCalendar = createJalaliCalendarHTML(newDate, inputElement);
        calendar.parentNode.replaceChild(newCalendar, calendar);
    });
    
    return calendar;
}

function hideDatePeriodModal() {
    datePeriodModal.classList.remove('active');
    currentReportRequest = null;
    
    // Remove calendar popup if exists
    const calendar = document.getElementById('jalaliCalendarPopup');
    if (calendar) {
        calendar.remove();
    }
    
    // Clean up pickers
    if (dateFromPicker && typeof $ !== 'undefined') {
        try {
            if ($(dateFromInput).data('pDatepicker')) {
                $(dateFromInput).pDatepicker('destroy');
            }
        } catch(e) {
            console.log('Error cleaning up dateFromPicker:', e);
        }
        dateFromPicker = null;
    }
    if (dateToPicker && typeof $ !== 'undefined') {
        try {
            if ($(dateToInput).data('pDatepicker')) {
                $(dateToInput).pDatepicker('destroy');
            }
        } catch(e) {
            console.log('Error cleaning up dateToPicker:', e);
        }
        dateToPicker = null;
    }
}

function formatJalaliDateForInput(jalaliDate) {
    // Input is already in Jalali format YYYY/MM/DD, convert to YYYY-MM-DD
    return jalaliDate.replace(/\//g, '-');
}

// Quick date button handlers (use event delegation since buttons are in modal)
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('btn-quick-date')) {
        const period = e.target.getAttribute('data-period');
        setQuickDatePeriod(period);
    }
});

function setQuickDatePeriod(period) {
    const today = new Date();
    const todayJalali = new persianDate(today);
    let fromDate, toDate;
    
    switch(period) {
        case 'today':
            fromDate = new persianDate([todayJalali.year(), todayJalali.month() + 1, todayJalali.date()]);
            toDate = new persianDate([todayJalali.year(), todayJalali.month() + 1, todayJalali.date()]);
            break;
        case 'week':
            // Get start of week (Saturday in Persian calendar)
            const dayOfWeek = todayJalali.day();
            const diff = dayOfWeek === 6 ? 0 : dayOfWeek + 1; // Saturday = 0, Sunday = 1, etc.
            const weekStart = todayJalali.subtract('day', diff);
            fromDate = new persianDate([weekStart.year(), weekStart.month() + 1, weekStart.date()]);
            toDate = new persianDate([todayJalali.year(), todayJalali.month() + 1, todayJalali.date()]);
            break;
        case 'month':
            fromDate = new persianDate([todayJalali.year(), todayJalali.month() + 1, 1]);
            const monthLastDay = new persianDate([todayJalali.year(), todayJalali.month() + 1, 1]).daysInMonth();
            toDate = new persianDate([todayJalali.year(), todayJalali.month() + 1, monthLastDay]);
            break;
        case 'last_month':
            const lastMonth = todayJalali.subtract('month', 1);
            fromDate = new persianDate([lastMonth.year(), lastMonth.month() + 1, 1]);
            const lastMonthLastDay = new persianDate([lastMonth.year(), lastMonth.month() + 1, 1]).daysInMonth();
            toDate = new persianDate([lastMonth.year(), lastMonth.month() + 1, lastMonthLastDay]);
            break;
        case 'quarter':
            // Persian quarters: 1-3, 4-6, 7-9, 10-12
            const quarter = Math.floor(todayJalali.month() / 3);
            const quarterStartMonth = quarter * 3;
            const quarterEndMonth = (quarter + 1) * 3 - 1;
            fromDate = new persianDate([todayJalali.year(), quarterStartMonth + 1, 1]);
            const quarterEnd = new persianDate([todayJalali.year(), quarterEndMonth + 1, 1]);
            toDate = new persianDate([todayJalali.year(), quarterEndMonth + 1, quarterEnd.daysInMonth()]);
            break;
        case 'year':
            fromDate = new persianDate([todayJalali.year(), 1, 1]);
            toDate = new persianDate([todayJalali.year(), 12, 29]); // Last day of Esfand
            break;
        default:
            return;
    }
    
    const fromStr = fromDate.format('YYYY/MM/DD');
    const toStr = toDate.format('YYYY/MM/DD');
    
    dateFromInput.value = fromStr;
    dateToInput.value = toStr;
    
    // Update pickers
    if (dateFromPicker) {
        dateFromPicker.setDate(fromDate.toDate());
    }
    if (dateToPicker) {
        dateToPicker.setDate(toDate.toDate());
    }
}

// Date period form submission
if (datePeriodForm) {
    datePeriodForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const dateFrom = dateFromInput.value;
        const dateTo = dateToInput.value;
        
        if (!dateFrom || !dateTo) {
            alert('لطفاً هر دو تاریخ را انتخاب کنید');
            return;
        }
        
        // Validate Jalali dates - parse from YYYY/MM/DD format
        const fromParts = dateFrom.split('/');
        const toParts = dateTo.split('/');
        
        if (fromParts.length !== 3 || toParts.length !== 3) {
            alert('لطفاً تاریخ‌ها را در فرمت صحیح وارد کنید (سال/ماه/روز)');
            return;
        }
        
        const fromDate = new persianDate([parseInt(fromParts[0]), parseInt(fromParts[1]), parseInt(fromParts[2])]);
        const toDate = new persianDate([parseInt(toParts[0]), parseInt(toParts[1]), parseInt(toParts[2])]);
        
        if (!fromDate.isValid() || !toDate.isValid()) {
            alert('لطفاً تاریخ‌های معتبر انتخاب کنید');
            return;
        }
        
        if (fromDate.isAfter(toDate)) {
            alert('تاریخ شروع باید قبل از تاریخ پایان باشد');
            return;
        }
        
        hideDatePeriodModal();
        
        if (currentReportRequest) {
            await generateReport(
                currentReportRequest.reportType,
                currentReportRequest.reportName,
                dateFrom,
                dateTo
            );
        }
    });
}

// Close date modal handlers
if (closeDateModal) {
    closeDateModal.addEventListener('click', hideDatePeriodModal);
}

if (cancelDateBtn) {
    cancelDateBtn.addEventListener('click', hideDatePeriodModal);
}

// Close modal on outside click
if (datePeriodModal) {
    datePeriodModal.addEventListener('click', function(e) {
        if (e.target === datePeriodModal) {
            hideDatePeriodModal();
        }
    });
}

async function generateReport(reportType, reportName, dateFrom = null, dateTo = null) {
    // Show loading
    showLoading();
    
    // Add user message showing selection
    let messageText = `گزارش ${reportName}`;
    if (dateFrom && dateTo) {
        // Dates are already in Jalali format (YYYY/MM/DD)
        messageText += ` (از ${dateFrom} تا ${dateTo})`;
    }
    addMessage(messageText, true);
    
    try {
        // Build message with date information
        let message = `${reportName} ${reportType}`;
        if (dateFrom && dateTo) {
            // Convert Jalali format from YYYY/MM/DD to YYYY-MM-DD for backend
            const dateFromFormatted = dateFrom.replace(/\//g, '-');
            const dateToFormatted = dateTo.replace(/\//g, '-');
            message += ` از تاریخ ${dateFromFormatted} تا ${dateToFormatted}`;
        }
        
        // Send request to generate the report
        const response = await fetch('/api/finance/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                message: message,
                date_from: dateFrom ? dateFrom.replace(/\//g, '-') : null,
                date_to: dateTo ? dateTo.replace(/\//g, '-') : null
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'خطا در تولید گزارش');
        }
        
        const data = await response.json();
        
        // Add AI response with report
        addMessage(data.response, false);
        
    } catch (error) {
        console.error('Error:', error);
        addMessage(`❌ خطایی رخ داد: ${error.message}`, false);
    } finally {
        hideLoading();
        messageInput.focus();
    }
}

// Quick action cards
document.addEventListener('click', function(e) {
    const actionCard = e.target.closest('.action-card');
    if (actionCard) {
        // Skip if it's the create account button (handled separately)
        if (actionCard.id === 'createAccountBtn') {
            return;
        }
        
        // Skip if it's the report quick access button (handled separately)
        if (actionCard.id === 'reportQuickAccessBtn') {
            return;
        }
        
        const prompt = actionCard.getAttribute('data-prompt');
        if (prompt) {
            messageInput.value = prompt;
            sendMessage();
        }
    }
});

// ==================== REPORT QUICK ACCESS ====================
const reportQuickAccessBtn = document.getElementById('reportQuickAccessBtn');
if (reportQuickAccessBtn) {
    reportQuickAccessBtn.addEventListener('click', async function() {
        // Show loading
        showLoading();
        
        try {
            const response = await fetch('/api/finance/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: 'گزارش' })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'خطا در دریافت پاسخ');
            }
            
            const data = await response.json();
            
            // Add AI response
            const messageDiv = addMessage(data.response, false);
            
            // If reports are available, add report selection buttons
            if (data.show_report_buttons && data.reports) {
                addReportButtons(messageDiv, data.reports);
            }
            
        } catch (error) {
            console.error('Error:', error);
            addMessage(`❌ خطایی رخ داد: ${error.message}`, false);
        } finally {
            hideLoading();
            messageInput.focus();
        }
    });
}

// ==================== INITIALIZATION ====================
initTheme();
messageInput.focus();

// Welcome message hint
console.log('💰 مدیر مالی هوشمند آماده است!');
console.log('📄 شما می‌توانید رسیدها و فاکتورها را بارگذاری کرده و سوالات مالی خود را بپرسید.');



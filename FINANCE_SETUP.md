# Finance Assistant - راهنمای نصب و راه‌اندازی

## نمای کلی

سیستم مدیر مالی هوشمند یک سیستم چند عاملی (Multi-Agent) برای مدیریت مالی کسب‌وکارهای ایرانی است.

### قابلیت‌های اصلی

✅ **پردازش اسناد (Document Processing)**
- OCR رسیدها و فاکتورها با پشتیبانی کامل از فارسی
- استخراج خودکار داده‌های مالی
- پردازش صورتحساب‌های بانکی

✅ **مدیریت تراکنش‌ها (Transaction Management)**
- ثبت، ویرایش، حذف و جستجوی تراکنش‌ها
- دسته‌بندی خودکار هوشمند
- پیگیری فروشندگان و تاریخچه

✅ **مدیریت نقدینگی (Cash Management)**
- پیگیری موجودی چند حسابی
- تبدیل ارز و نرخ‌های لحظه‌ای
- پیش‌بینی جریان نقدی

✅ **گزارش‌گیری (Reporting)**
- صورت سود و زیان
- گزارش هزینه‌ها
- تحلیل‌های مالی

### معماری سیستم

سیستم شامل 3 دستیار مستقل است:

1. **دستیار شخصی** (Personal Assistant) - مدیریت وظایف و رویدادها
2. **دستیار اسناد** (Document Assistant) - سؤال و جواب روی اسناد (RAG)
3. **مدیر مالی** (Finance Assistant) - مدیریت مالی چند عاملی ⭐ NEW

## پیش‌نیازها

### نیازمندی‌های سیستم

- Python 3.11 یا بالاتر
- 4GB RAM حداقل
- Windows/Linux/Mac

### نیازمندی‌های نرم‌افزاری

```bash
# Core dependencies (already installed)
langchain
langchain-openai
langgraph
flask

# NEW: Finance-specific dependencies
opencv-python
fuzzywuzzy
python-levenshtein
beautifulsoup4
requests
```

### اختیاری (برای OCR بهتر)

```bash
# For OCR capabilities (optional)
pytesseract  # Requires Tesseract installation
paddleocr    # Alternative OCR engine

# For PDF/Excel export (optional)
reportlab
openpyxl
arabic-reshaper
python-bidi
```

## نصب و راه‌اندازی

### مرحله 1: نصب وابستگی‌ها

```bash
# Install core finance dependencies
pip install opencv-python fuzzywuzzy python-levenshtein beautifulsoup4 requests

# Optional: For enhanced OCR
pip install pytesseract paddleocr

# Optional: For exports
pip install reportlab openpyxl arabic-reshaper python-bidi
```

### مرحله 2: نصب Tesseract OCR (اختیاری ولی توصیه می‌شود)

**Windows:**
1. دانلود از: https://github.com/UB-Mannheim/tesseract/wiki
2. نصب و اضافه کردن به PATH
3. دانلود Persian language pack: `fas.traineddata`

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fas
```

**Mac:**
```bash
brew install tesseract tesseract-lang
```

### مرحله 3: تنظیمات محیط

فایل `.env` را ویرایش کنید:

```env
OPENAI_API_KEY=your_openai_api_key_here

# Finance Configuration
FINANCE_DB_PATH=finance.db
FINANCE_MODEL=gpt-4o
TESSERACT_PATH=tesseract
```

### مرحله 4: راه‌اندازی دیتابیس

دیتابیس finance به صورت خودکار هنگام اولین اجرا ایجاد می‌شود.

```python
from finance_agent import FinanceAgent

# Initialize agent (creates database automatically)
agent = FinanceAgent(
    openai_api_key="your_key",
    model="gpt-4o"
)

# Initialize a user
agent.init_user("user_id_1", name="علی احمدی", email="ali@example.com")
```

### مرحله 5: اجرای سرور

```bash
python app.py
```

سرور روی آدرس زیر اجرا می‌شود:
- http://127.0.0.1:5000

دستیار مالی در آدرس زیر قابل دسترسی است:
- http://127.0.0.1:5000/finance

## استفاده

### رابط کاربری وب

1. به http://127.0.0.1:5000/finance بروید
2. از منوی بالا بین دستیارهای مختلف جابجا شوید
3. از دکمه‌های سمت راست برای عملیات سریع استفاده کنید

### نمونه تعاملات

**بارگذاری رسید:**
```
کاربر: [بارگذاری تصویر رسید]
سیستم: ✅ سند با موفقیت پردازش شد!
📍 فروشنده: دیجی‌کالا
💰 مبلغ: 2,500,000 ریال
📅 تاریخ: 1403/09/15
🎯 اطمینان: 85%
```

**ثبت تراکنش:**
```
کاربر: می‌خواهم یک هزینه ثبت کنم
سیستم: چه مبلغی و برای چه چیزی؟
کاربر: 5 میلیون تومان برای تبلیغات اینستاگرام
سیستم: ✅ تراکنش ثبت شد
دسته‌بندی خودکار: بازاریابی > تبلیغات دیجیتال
```

**جستجوی تراکنش‌ها:**
```
کاربر: تراکنش‌های ماه گذشته را نشان بده
سیستم: ✅ 45 تراکنش یافت شد
جمع درآمد: 150,000,000 ریال
جمع هزینه: 95,000,000 ریال
```

**موجودی و نرخ ارز:**
```
کاربر: موجودی من چقدر است؟
سیستم: 💰 موجودی کل: 125,000,000 ریال (12,500,000 تومان)

کاربر: نرخ دلار چقدر است؟
سیستم: 💱 نرخ دلار آمریکا:
- رسمی: 42,000 ریال
- بازار آزاد: 55,000 ریال
- نیما: 45,000 ریال
```

**گزارش‌گیری:**
```
کاربر: یک گزارش سود و زیان برای این ماه بده
سیستم: 📊 صورت سود و زیان
[گزارش کامل با تفکیک دسته‌بندی]
```

## ساختار فایل‌ها

```
ai agent/
├── finance/                      # Finance module
│   ├── agents/                   # Sub-agents
│   │   ├── document_agent.py     # OCR & extraction
│   │   ├── transaction_agent.py  # Transaction CRUD
│   │   ├── cash_agent.py         # Balance & currency
│   │   ├── reporting_agent.py    # Reports
│   │   └── conversation_agent.py # Dialogue
│   ├── tools/                    # Finance tools
│   │   ├── ocr_tools.py          # OCR functions
│   │   ├── database_tools.py     # Transaction operations
│   │   ├── exchange_rate_tools.py # Currency tools
│   │   ├── calculation_tools.py  # Financial metrics
│   │   ├── report_generators.py  # Report generation
│   │   └── file_storage.py       # Document storage
│   ├── models/                   # Data models
│   └── database.py               # Finance database
├── finance_agent.py              # Main finance agent
├── app.py                        # Flask application (updated)
├── config.py                     # Configuration (updated)
├── templates/
│   └── finance_chat.html         # Finance UI
└── finance.db                    # Finance database (auto-created)
```

## دیتابیس

### جداول اصلی

- `finance_users` - کاربران
- `finance_accounts` - حساب‌های بانکی
- `finance_transactions` - تراکنش‌ها
- `finance_categories` - دسته‌بندی‌ها
- `finance_vendors` - فروشندگان
- `finance_invoices` - فاکتورها
- `finance_documents` - اسناد بارگذاری شده
- `finance_budgets` - بودجه‌ها
- `finance_exchange_rates` - نرخ‌های ارز
- `finance_memory` - حافظه مکالمات

### دسته‌بندی‌های پیش‌فرض

**درآمد:**
- فروش محصولات
- ارائه خدمات
- سایر درآمدها

**هزینه:**
- حقوق و دستمزد
- بازاریابی (تبلیغات دیجیتال، رویدادها)
- عملیات (اجاره، آب و برق، لوازم اداری)
- لجستیک
- خدمات حرفه‌ای

## عیب‌یابی

### مشکل: OCR کار نمی‌کند

```bash
# Check if Tesseract is installed
tesseract --version

# Install Persian language pack
# Download fas.traineddata and place in tessdata folder
```

### مشکل: خطای دیتابیس

```bash
# Delete and recreate database
rm finance.db
python
>>> from finance_agent import FinanceAgent
>>> agent = FinanceAgent(openai_api_key="your_key")
>>> agent.init_user("test_user")
```

### مشکل: فونت‌های فارسی نمایش داده نمی‌شوند

فونت‌های فارسی (Vazir, Sahel) را در پوشه `fonts/` قرار دهید.

## محدودیت‌های نسخه فعلی

### قابلیت‌های کامل شده ✅
- ساختار پایه و دیتابیس
- پردازش اسناد با OCR
- مدیریت تراکنش‌ها
- دسته‌بندی خودکار
- مدیریت نقدینگی
- تبدیل ارز
- گزارش‌گیری پایه (P&L، هزینه‌ها)

### در دست توسعه 🚧
- OCR پیشرفته‌تر (PaddleOCR، GPT-4 Vision)
- PDF/Excel export با فونت فارسی
- پیش‌بینی جریان نقدی پیشرفته
- بودجه‌بندی و پیگیری
- یادگیری الگوهای دسته‌بندی (Vector DB)
- گزارش مالیاتی کامل
- پردازش صورتحساب بانکی

### نیازمند توسعه آینده 📋
- اتصال به بانک‌ها (Open Banking)
- رابط API برای اتصال سیستم‌های دیگر
- گزارش‌های پیشرفته‌تر
- نمودارهای تعاملی
- اپلیکیشن موبایل

## پشتیبانی

برای گزارش مشکلات یا درخواست قابلیت جدید، از Issues در GitHub استفاده کنید.

## مجوز

این پروژه تحت مجوز MIT منتشر شده است.

---

**نسخه:** 1.0.0  
**تاریخ:** دی ماه 1403  
**توسعه‌دهنده:** AI Agent System


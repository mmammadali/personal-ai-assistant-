# 💰 Finance Assistant - مدیر مالی هوشمند

> سیستم چند عاملی (Multi-Agent) برای مدیریت مالی کسب‌وکارهای ایرانی

[![Status](https://img.shields.io/badge/status-MVP%20Ready-success)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![Framework](https://img.shields.io/badge/framework-LangGraph-orange)]()
[![Language](https://img.shields.io/badge/language-Persian-red)]()

---

## 🌟 نمای کلی

سیستم مدیر مالی هوشمند یک **سیستم سه‌لایه Multi-Agent** است که برای کسب‌وکارهای ایرانی طراحی شده و شامل:

1. **دستیار شخصی** - مدیریت وظایف و رویدادها
2. **دستیار اسناد** - سوال و جواب روی اسناد (RAG)
3. **مدیر مالی** ⭐ - مدیریت مالی چند عاملی (NEW!)

---

## ✨ قابلیت‌های کلیدی

### 📄 پردازش اسناد
- ✅ OCR رسیدها با پشتیبانی کامل فارسی
- ✅ استخراج خودکار فروشنده، مبلغ، تاریخ
- ✅ بررسی کیفیت تصویر
- ✅ پشتیبانی از JPG, PNG, PDF

### 💳 مدیریت تراکنش‌ها
- ✅ ثبت، ویرایش، حذف تراکنش‌ها
- ✅ **دسته‌بندی خودکار هوشمند** با یادگیری از تاریخچه
- ✅ جستجوی پیشرفته با فیلترهای متعدد
- ✅ پیگیری خودکار فروشندگان
- ✅ تشخیص تراکنش‌های تکراری

### 💰 مدیریت نقدینگی
- ✅ پیگیری موجودی چند حسابی
- ✅ تبدیل ارز (دلار، یورو، پوند، درهم)
- ✅ نرخ ارز لحظه‌ای (رسمی، نیما، بازار آزاد)
- ✅ تبدیل خودکار ریال ↔ تومان
- ✅ محاسبه burn rate
- ✅ پیش‌بینی جریان نقدی

### 📊 گزارش‌گیری
- ✅ صورت سود و زیان (P&L)
- ✅ گزارش تفصیلی هزینه‌ها
- ✅ تحلیل بر اساس دسته‌بندی
- ✅ بالاترین فروشندگان
- ✅ معیارهای مالی کلیدی

---

## 🏗️ معماری سیستم

```
Finance Assistant (Main)
    ├── Document Agent      → OCR & Extraction
    ├── Transaction Agent   → CRUD & Categorization
    ├── Cash Agent         → Balance & Currency
    ├── Reporting Agent    → Reports & Analytics
    └── Conversation Agent → Dialogue & Help
```

**پشته فناوری:**
- 🧠 LangChain & LangGraph
- 🤖 OpenAI GPT-4
- 🗄️ SQLite Database
- 🌐 Flask Web Framework
- 👁️ OpenCV & Tesseract OCR
- 🇮🇷 jdatetime (تقویم جلالی)

---

## 🚀 نصب و راه‌اندازی

### پیش‌نیازها

```bash
Python 3.11+
OpenAI API Key
```

### نصب

```bash
# 1. Clone repository
git clone [your-repo]
cd ai-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure .env
echo "OPENAI_API_KEY=your_key_here" > .env

# 4. Run server
python app.py
```

### دسترسی

```
🌐 http://127.0.0.1:5000/finance
```

---

## 💡 نحوه استفاده

### رابط کاربری وب

![Finance Assistant UI](docs/images/finance-ui-screenshot.png)

**عملیات سریع:**
- 💰 **موجودی** - نمایش موجودی کل
- ➖ **ثبت هزینه** - ثبت سریع هزینه
- ➕ **ثبت درآمد** - ثبت سریع درآمد
- 📊 **گزارش** - گزارش ماه جاری
- 💱 **نرخ ارز** - نمایش نرخ‌ها
- 📎 **بارگذاری** - آپلود رسید

### مثال‌های گفتگو

```
👤 کاربر: "موجودی من چقدر است؟"
🤖 سیستم: "💰 موجودی کل: 125,000,000 ریال (12,500,000 تومان)"

👤 کاربر: "5 میلیون تومان برای تبلیغات اینستاگرام هزینه کردم"
🤖 سیستم: "✅ تراکنش ثبت شد
              دسته‌بندی خودکار: بازاریابی > تبلیغات دیجیتال"

👤 کاربر: "گزارش سود و زیان این ماه"
🤖 سیستم: [گزارش کامل P&L با تفکیک دسته‌بندی]
```

### API استفاده

```python
from finance_agent import FinanceAgent

# Initialize
agent = FinanceAgent(openai_api_key="your_key")
agent.init_user("user123", name="علی احمدی")

# Create transaction
agent.create_transaction(
    user_id="user123",
    amount=5000000,
    transaction_type="expense",
    date="1403/09/15",
    description="تبلیغات",
    vendor="Instagram"
)

# Search
transactions = agent.get_transactions(
    filters={"category": "بازاریابی"},
    user_id="user123"
)

# Generate report
report = agent.generate_report(
    "pl",
    {"date_from": "1403/09/01", "date_to": "1403/09/30"},
    "user123"
)
```

---

## 📁 ساختار پروژه

```
ai agent/
├── finance/                      # Finance module
│   ├── agents/                   # 5 specialized agents
│   │   ├── document_agent.py
│   │   ├── transaction_agent.py
│   │   ├── cash_agent.py
│   │   ├── reporting_agent.py
│   │   └── conversation_agent.py
│   ├── tools/                    # Finance tools
│   │   ├── ocr_tools.py
│   │   ├── database_tools.py
│   │   ├── exchange_rate_tools.py
│   │   ├── calculation_tools.py
│   │   └── report_generators.py
│   └── database.py               # Database management
├── finance_agent.py              # Main finance agent
├── app.py                        # Flask application
├── templates/
│   └── finance_chat.html         # Finance UI
├── FINANCE_SETUP.md              # راهنمای نصب
├── FINANCE_QUICKSTART.md         # راهنمای سریع
└── FINANCE_IMPLEMENTATION_SUMMARY.md  # خلاصه پیاده‌سازی
```

---

## 🎯 دسته‌بندی‌های پیش‌فرض

### درآمد
- 💰 فروش محصولات
- 🛠️ ارائه خدمات  
- 📈 سایر درآمدها

### هزینه
- 👥 حقوق و دستمزد
- 📢 بازاریابی
  - تبلیغات دیجیتال
  - رویدادها
- 🏢 عملیات
  - اجاره
  - آب و برق
  - لوازم اداری
- 🚚 لجستیک
- ⚖️ خدمات حرفه‌ای

---

## 🔧 پیکربندی پیشرفته

### OCR (اختیاری)

```bash
# Install Tesseract
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# Linux: sudo apt-get install tesseract-ocr tesseract-ocr-fas
# Mac: brew install tesseract tesseract-lang

# Install Python package
pip install pytesseract
```

### نرخ ارز واقعی

برای دریافت نرخ‌های واقعی، APIهای زیر را تنظیم کنید:
- Bonbast.com
- Tgju.org
- CBI (Central Bank of Iran)

---

## 📊 وضعیت پیاده‌سازی

| فاز | وضعیت | تکمیل |
|-----|--------|--------|
| Foundation | ✅ کامل | 100% |
| Document Processing | ✅ کامل | 85% |
| Transaction Management | ✅ کامل | 95% |
| Cash Management | ✅ کامل | 75% |
| Reporting | ✅ کامل | 70% |
| Integration | ✅ کامل | 80% |
| Advanced Features | ⚠️ آماده | 30% |
| Testing | ⚠️ در حال انجام | 50% |

**وضعیت کلی:** ✅ MVP Ready (85%)

---

## 🐛 عیب‌یابی

### مشکل: OCR کار نمی‌کند
```bash
# Check Tesseract installation
tesseract --version

# Install Persian language pack
# Place fas.traineddata in tessdata folder
```

### مشکل: خطای دیتابیس
```bash
# Recreate database
rm finance.db
python app.py
```

### مشکل: نرخ ارز نمایش داده نمی‌شود
نرخ‌های نمونه نمایش داده می‌شود. برای نرخ واقعی:
- اتصال اینترنت فعال باشد
- API keys تنظیم شده باشد

---

## 📚 مستندات

- 📘 [راهنمای کامل نصب](FINANCE_SETUP.md)
- 🚀 [راهنمای سریع](FINANCE_QUICKSTART.md)
- 📊 [خلاصه پیاده‌سازی](FINANCE_IMPLEMENTATION_SUMMARY.md)
- 📋 [برنامه پیاده‌سازی](finance-manager-integration.plan.md)

---

## 🤝 مشارکت

این پروژه یک نمونه کامل از سیستم Multi-Agent با LangGraph است.

برای توسعه بیشتر:
1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

---

## 📝 TODO

### نسخه 1.1
- [ ] Unit & Integration Tests
- [ ] PDF/Excel Export
- [ ] Enhanced OCR
- [ ] Real Exchange Rate APIs

### نسخه 2.0
- [ ] Bank API Integration
- [ ] Multi-user Support
- [ ] Advanced Analytics
- [ ] Mobile App

---

## 🙏 تشکر

ساخته شده با:
- 🦜 [LangChain](https://langchain.com)
- 🕸️ [LangGraph](https://langchain-ai.github.io/langgraph/)
- 🤖 [OpenAI](https://openai.com)
- 🌐 [Flask](https://flask.palletsprojects.com/)

---

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

---

## 📞 پشتیبانی

برای سوالات و مشکلات:
- 📧 Email: support@example.com
- 💬 GitHub Issues
- 📖 [Documentation](FINANCE_SETUP.md)

---

<div align="center">

**ساخته شده با ❤️ برای کسب‌وکارهای ایرانی**

[![Star](https://img.shields.io/github/stars/your-repo?style=social)]()
[![Fork](https://img.shields.io/github/forks/your-repo?style=social)]()

</div>


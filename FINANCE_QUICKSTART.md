# Finance Assistant - راهنمای سریع

## شروع سریع (5 دقیقه)

### 1. نصب وابستگی‌ها

```bash
pip install opencv-python fuzzywuzzy python-levenshtein beautifulsoup4 requests
```

### 2. راه‌اندازی

```bash
python app.py
```

### 3. دسترسی

باز کنید: http://127.0.0.1:5000/finance

## دستورات پرکاربرد

### 💰 موجودی
```
"موجودی من چقدر است؟"
"balance"
```

### ➕ ثبت درآمد
```
"درآمد 10 میلیون تومان از فروش محصول ثبت کن"
"add income 10 million from sales"
```

### ➖ ثبت هزینه
```
"هزینه 5 میلیون تومان برای تبلیغات اینستاگرام"
"expense 5M for Instagram ads"
```

### 📎 بارگذاری رسید
- کلیک روی دکمه "📎 بارگذاری رسید"
- انتخاب تصویر رسید (JPG, PNG, PDF)
- سیستم خودکار داده را استخراج می‌کند

### 🔍 جستجوی تراکنش‌ها
```
"تراکنش‌های ماه گذشته"
"last month transactions"

"هزینه‌های بازاریابی این ماه"
"marketing expenses this month"

"خریدهای دیجیکالا"
"digikala purchases"
```

### 💱 نرخ ارز
```
"نرخ دلار چقدر است؟"
"USD rate"

"500 دلار چند تومان است؟"
"convert 500 USD to IRR"
```

### 📊 گزارش
```
"گزارش سود و زیان این ماه"
"P&L report this month"

"گزارش هزینه‌ها"
"expense report"
```

## دکمه‌های سریع (Sidebar)

- 💰 **موجودی** - نمایش موجودی کل
- ➖ **ثبت هزینه** - ثبت سریع هزینه
- ➕ **ثبت درآمد** - ثبت سریع درآمد
- 📊 **گزارش** - دریافت گزارش ماه جاری
- 💱 **نرخ ارز** - نمایش نرخ ارزها
- ❓ **راهنما** - راهنمای استفاده

## API سریع

### ثبت تراکنش

```python
from finance_agent import FinanceAgent

agent = FinanceAgent(openai_api_key="your_key")

# Create transaction
result = agent.create_transaction(
    user_id="user123",
    amount=5000000,
    transaction_type="expense",
    date="1403/09/15",
    description="تبلیغات اینستاگرام",
    vendor="Instagram",
    payment_method="card",
    currency="IRR"
)
```

### جستجو

```python
# Search transactions
transactions = agent.get_transactions(
    filters={
        "date_from": "1403/08/01",
        "date_to": "1403/09/30",
        "category": "بازاریابی"
    },
    user_id="user123"
)
```

### پردازش رسید

```python
# Process receipt
result = agent.upload_document(
    file_path="receipt.jpg",
    user_id="user123",
    doc_type="receipt"
)

print(result['data'])  # Extracted vendor, amount, date
```

### گزارش

```python
# Generate report
report = agent.generate_report(
    report_type="pl",
    params={
        "date_from": "1403/07/01",
        "date_to": "1403/09/30"
    },
    user_id="user123"
)

print(report['message'])  # Formatted P&L statement
```

## نکات مهم

### 1. ریال یا تومان؟
سیستم همیشه در ریال ذخیره می‌کند اما تبدیل خودکار انجام می‌دهد:
- "5 میلیون تومان" → 50,000,000 ریال
- "50 میلیون ریال" → 5,000,000 تومان (در نمایش)

### 2. دسته‌بندی خودکار
سیستم خودکار بر اساس:
- تاریخچه فروشنده
- کلمات کلیدی در توضیحات
- الگوهای یادگرفته شده

### 3. فروشندگان متداول
سیستم این فروشندگان را می‌شناسد:
- دیجی‌کالا، اسنپ، تپسی
- Instagram، Google، Facebook
- و سایر فروشندگان بعد از اولین تراکنش

### 4. تاریخ‌ها
از تقویم جلالی استفاده کنید:
- "1403/09/15"
- "امروز"، "دیروز"، "فردا"
- "ماه گذشته"، "این ماه"

## عیب‌یابی سریع

### OCR کار نمی‌کند
```bash
pip install pytesseract
# Install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
```

### دیتابیس خراب شده
```bash
rm finance.db
python app.py  # Will recreate automatically
```

### نرخ ارز نمایش داده نمی‌شود
نرخ‌های نمونه نمایش داده می‌شود. برای نرخ واقعی:
- اتصال اینترنت فعال باشد
- سایت‌های تامین کننده نرخ در دسترس باشند

## مثال کامل

```python
# Initialize
from finance_agent import FinanceAgent
agent = FinanceAgent(openai_api_key="your_key")
agent.init_user("ali", name="علی احمدی")

# 1. Upload receipt
receipt = agent.upload_document("receipt.jpg", "ali")

# 2. Create manual transaction
agent.create_transaction(
    user_id="ali",
    amount=3000000,
    transaction_type="expense",
    date="1403/09/14",
    description="اجاره دفتر",
    category="expense-rent"
)

# 3. Search
results = agent.get_transactions(
    filters={"date_from": "1403/09/01"},
    user_id="ali"
)

# 4. Generate report
report = agent.generate_report(
    "pl",
    {"date_from": "1403/09/01", "date_to": "1403/09/30"},
    "ali"
)

print(report['message'])
```

## منابع بیشتر

- 📄 [راهنمای کامل نصب](FINANCE_SETUP.md)
- 🏗️ [معماری سیستم](ARCHITECTURE.md)
- 📝 [مستندات API](FINANCE_API.md)

---

**نکته:** اگر سوالی دارید، مستقیماً از دستیار بپرسید:
```
"چگونه می‌توانم یک هزینه ثبت کنم؟"
"چطور گزارش بگیرم؟"
```

سیستم به صورت هوشمند راهنمایی می‌کند! 🎯


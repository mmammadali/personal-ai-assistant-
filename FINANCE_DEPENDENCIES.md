# Finance Agent Dependencies Installation Guide

This document lists all dependencies required for full Finance Agent functionality, including OCR capabilities.

---

## Core Dependencies (Already Installed)

These are required for basic Finance Agent operation and are already installed:

- ✅ `langchain` - Core LangChain framework
- ✅ `langchain-openai` - OpenAI integration
- ✅ `langchain-community` - Community tools
- ✅ `langgraph` - Graph-based agent orchestration
- ✅ `flask` - Web framework
- ✅ `jdatetime` - Persian calendar support
- ✅ `pytz` - Timezone support
- ✅ `pydantic` - Data validation
- ✅ `python-dotenv` - Environment variable management

---

## OCR & Image Processing Dependencies

These are required for **full OCR functionality** (receipt/invoice processing):

### Critical OCR Dependencies:

1. **opencv-python** (cv2)
   - **Purpose:** Image processing, quality checking, preprocessing
   - **Version:** >= 4.8.0
   - **Install:** `pip install opencv-python`
   - **Status:** ⚠️ Needs installation
   - **Note:** Large package, may take time to install

2. **Pillow** (PIL)
   - **Purpose:** Image manipulation and opening
   - **Version:** >= 10.0.0
   - **Install:** `pip install Pillow`
   - **Status:** ✅ Installed

3. **numpy**
   - **Purpose:** Required by opencv-python for array operations
   - **Version:** >= 1.24.0
   - **Install:** `pip install numpy`
   - **Status:** ⚠️ May need installation (dependency of opencv-python)

### OCR Engine Options (Choose one or both):

4. **pytesseract**
   - **Purpose:** Tesseract OCR wrapper for text extraction
   - **Version:** >= 0.3.10
   - **Install:** `pip install pytesseract`
   - **Status:** ⚠️ Needs installation
   - **Note:** Also requires Tesseract OCR binary installed on system
   - **Tesseract Download:** https://github.com/UB-Mannheim/tesseract/wiki (Windows)

5. **paddleocr**
   - **Purpose:** Alternative OCR engine with better Persian support
   - **Version:** >= 2.7.0
   - **Install:** `pip install paddleocr`
   - **Status:** ⚠️ Needs installation
   - **Note:** Large package, includes ML models

6. **pdf2image**
   - **Purpose:** Convert PDF pages to images for OCR
   - **Version:** >= 1.16.0
   - **Install:** `pip install pdf2image`
   - **Status:** ⚠️ Needs installation
   - **Note:** Requires poppler-utils on system

---

## Web Scraping Dependencies (Exchange Rates)

7. **beautifulsoup4** (bs4)
   - **Purpose:** HTML parsing for exchange rate scraping
   - **Version:** >= 4.12.0
   - **Install:** `pip install beautifulsoup4`
   - **Status:** ✅ Installed

8. **lxml**
   - **Purpose:** XML/HTML parser (faster than default)
   - **Version:** >= 4.9.0
   - **Install:** `pip install lxml`
   - **Status:** ⚠️ Needs installation

9. **requests**
   - **Purpose:** HTTP requests for web scraping
   - **Version:** >= 2.31.0
   - **Install:** `pip install requests`
   - **Status:** ✅ Likely installed (common dependency)

---

## Fuzzy Matching Dependencies (Vendor Deduplication)

10. **fuzzywuzzy**
    - **Purpose:** Fuzzy string matching for vendor name matching
    - **Version:** >= 0.18.0
    - **Install:** `pip install fuzzywuzzy`
    - **Status:** ✅ Installed

11. **python-levenshtein**
    - **Purpose:** Fast Levenshtein distance calculation (speeds up fuzzywuzzy)
    - **Version:** >= 0.21.0
    - **Install:** `pip install python-levenshtein`
    - **Status:** ✅ Installed

---

## PDF/Excel Export Dependencies

12. **reportlab**
    - **Purpose:** PDF generation for financial reports
    - **Version:** >= 4.0.0
    - **Install:** `pip install reportlab`
    - **Status:** ⚠️ Needs installation

13. **openpyxl**
    - **Purpose:** Excel file reading/writing
    - **Version:** >= 3.1.0
    - **Install:** `pip install openpyxl`
    - **Status:** ✅ Likely installed (in requirements.txt)

14. **xlsxwriter**
    - **Purpose:** Excel file writing (alternative to openpyxl)
    - **Version:** >= 3.1.0
    - **Install:** `pip install xlsxwriter`
    - **Status:** ⚠️ Needs installation

---

## Persian Text Processing

15. **arabic-reshaper**
    - **Purpose:** Arabic/Persian text reshaping for proper display
    - **Version:** >= 3.0.0
    - **Install:** `pip install arabic-reshaper`
    - **Status:** ⚠️ Needs installation

16. **python-bidi**
    - **Purpose:** Bidirectional text support (RTL/LTR)
    - **Version:** >= 0.4.2
    - **Install:** `pip install python-bidi`
    - **Status:** ⚠️ Needs installation

---

## Financial & Data Analysis

17. **pandas**
    - **Purpose:** Data analysis and manipulation
    - **Version:** >= 2.0.0
    - **Install:** `pip install pandas`
    - **Status:** ⚠️ Needs installation

18. **numpy** (already mentioned above)
    - **Purpose:** Numerical computing
    - **Version:** >= 1.24.0
    - **Status:** ⚠️ Needs installation

19. **scikit-learn**
    - **Purpose:** Machine learning for categorization
    - **Version:** >= 1.3.0
    - **Install:** `pip install scikit-learn`
    - **Status:** ⚠️ Needs installation
    - **Note:** Large package, may take time

---

## Additional Utilities

20. **python-magic**
    - **Purpose:** File type detection
    - **Version:** >= 0.4.27
    - **Install:** `pip install python-magic` (or `python-magic-bin` on Windows)
    - **Status:** ⚠️ Needs installation

21. **python-dateutil**
    - **Purpose:** Advanced date parsing
    - **Version:** >= 2.8.2
    - **Install:** `pip install python-dateutil`
    - **Status:** ⚠️ Needs installation

---

## Installation Commands

### Quick Install (All OCR Dependencies):

```bash
# Core OCR dependencies
pip install opencv-python Pillow numpy

# OCR engines (choose at least one)
pip install pytesseract
# OR
pip install paddleocr

# PDF processing
pip install pdf2image

# Web scraping
pip install beautifulsoup4 lxml requests

# Fuzzy matching
pip install fuzzywuzzy python-levenshtein

# PDF/Excel export
pip install reportlab openpyxl xlsxwriter

# Persian text processing
pip install arabic-reshaper python-bidi

# Data analysis
pip install pandas scikit-learn

# Utilities
pip install python-magic python-dateutil
```

### One-Line Install (All Dependencies):

```bash
pip install opencv-python Pillow numpy pytesseract paddleocr pdf2image beautifulsoup4 lxml requests fuzzywuzzy python-levenshtein reportlab openpyxl xlsxwriter arabic-reshaper python-bidi pandas scikit-learn python-magic python-dateutil
```

### Install from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## System-Level Dependencies

Some packages require system-level binaries:

### Tesseract OCR (for pytesseract):
- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **Linux:** `sudo apt-get install tesseract-ocr tesseract-ocr-fas` (Persian language)
- **macOS:** `brew install tesseract tesseract-lang`

### Poppler (for pdf2image):
- **Windows:** Download from https://github.com/oschwartz10612/poppler-windows/releases
- **Linux:** `sudo apt-get install poppler-utils`
- **macOS:** `brew install poppler`

---

## Priority Installation Order

### Phase 1: Essential OCR (Minimum for basic OCR)
1. `opencv-python` - Image processing
2. `Pillow` - Image handling ✅ (already installed)
3. `numpy` - Array operations
4. `pytesseract` OR `paddleocr` - OCR engine

### Phase 2: Enhanced Features
5. `beautifulsoup4` ✅ (already installed)
6. `fuzzywuzzy` ✅ (already installed)
7. `python-levenshtein` ✅ (already installed)
8. `lxml` - Faster HTML parsing
9. `pdf2image` - PDF processing

### Phase 3: Export & Reporting
10. `reportlab` - PDF reports
11. `openpyxl` / `xlsxwriter` - Excel export
12. `pandas` - Data analysis
13. `scikit-learn` - ML categorization

### Phase 4: Persian Text Support
14. `arabic-reshaper` - Text reshaping
15. `python-bidi` - RTL support

---

## Verification

After installation, verify with:

```python
# Test OCR dependencies
try:
    import cv2
    print(f"✅ OpenCV: {cv2.__version__}")
except ImportError:
    print("❌ OpenCV not installed")

try:
    from PIL import Image
    print(f"✅ Pillow: {Image.__version__}")
except ImportError:
    print("❌ Pillow not installed")

try:
    import numpy as np
    print(f"✅ NumPy: {np.__version__}")
except ImportError:
    print("❌ NumPy not installed")

try:
    import pytesseract
    print("✅ pytesseract installed")
except ImportError:
    print("❌ pytesseract not installed")

try:
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup4 installed")
except ImportError:
    print("❌ BeautifulSoup4 not installed")

try:
    from fuzzywuzzy import fuzz
    print("✅ fuzzywuzzy installed")
except ImportError:
    print("❌ fuzzywuzzy not installed")
```

---

## Current Status Summary

### ✅ Already Installed:
- Pillow
- beautifulsoup4
- fuzzywuzzy
- python-levenshtein

### ⚠️ Needs Installation:
- opencv-python (critical for OCR)
- numpy (dependency of opencv-python)
- pytesseract OR paddleocr (OCR engine)
- pdf2image (for PDF processing)
- lxml (for faster HTML parsing)
- reportlab (for PDF reports)
- xlsxwriter (for Excel export)
- arabic-reshaper (for Persian text)
- python-bidi (for RTL support)
- pandas (for data analysis)
- scikit-learn (for ML)
- python-magic (for file detection)
- python-dateutil (for date parsing)

---

## Notes

1. **opencv-python** is the largest package and may take several minutes to install
2. **paddleocr** includes ML models and is also large (~500MB+)
3. **scikit-learn** is large and may take time to compile
4. Some packages may require compilation (especially on Windows)
5. System-level binaries (Tesseract, Poppler) must be installed separately

---

**Last Updated:** December 4, 2025











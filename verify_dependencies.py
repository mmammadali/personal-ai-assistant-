#!/usr/bin/env python3
"""Verify that all Finance Agent dependencies are installed."""

import sys

dependencies = {
    "opencv-python": ("cv2", "OpenCV"),
    "numpy": ("numpy", "NumPy"),
    "pytesseract": ("pytesseract", "pytesseract"),
    "pdf2image": ("pdf2image", "pdf2image"),
    "lxml": ("lxml", "lxml"),
    "reportlab": ("reportlab", "reportlab"),
    "xlsxwriter": ("xlsxwriter", "xlsxwriter"),
    "arabic-reshaper": ("arabic_reshaper", "arabic-reshaper"),
    "python-bidi": ("bidi", "python-bidi"),
    "pandas": ("pandas", "pandas"),
    "scikit-learn": ("sklearn", "scikit-learn"),
    "Pillow": ("PIL", "Pillow"),
    "beautifulsoup4": ("bs4", "BeautifulSoup4"),
    "requests": ("requests", "requests"),
    "fuzzywuzzy": ("fuzzywuzzy", "fuzzywuzzy"),
    "python-levenshtein": ("Levenshtein", "python-levenshtein"),
    "python-dateutil": ("dateutil", "python-dateutil"),
    "python-magic-bin": ("magic", "python-magic-bin"),
}

optional = {
    "paddleocr": ("paddleocr", "paddleocr"),
}

print("=" * 60)
print("Finance Agent Dependencies Verification")
print("=" * 60)
print()

all_installed = True
installed_count = 0
missing_count = 0

# Check required dependencies
print("Required Dependencies:")
print("-" * 60)
for package_name, (import_name, display_name) in dependencies.items():
    try:
        __import__(import_name)
        print(f"✅ {display_name:25s} - Installed")
        installed_count += 1
    except ImportError:
        print(f"❌ {display_name:25s} - MISSING")
        missing_count += 1
        all_installed = False

print()
print("Optional Dependencies:")
print("-" * 60)
for package_name, (import_name, display_name) in optional.items():
    try:
        __import__(import_name)
        print(f"✅ {display_name:25s} - Installed")
        installed_count += 1
    except ImportError:
        print(f"⚠️  {display_name:25s} - Not installed (optional)")

print()
print("=" * 60)
print(f"Summary: {installed_count} packages installed, {missing_count} missing")
print("=" * 60)

if all_installed:
    print("\n✅ All required dependencies are installed!")
    sys.exit(0)
else:
    print("\n❌ Some required dependencies are missing. Please install them.")
    sys.exit(1)











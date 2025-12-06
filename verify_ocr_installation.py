#!/usr/bin/env python3
"""Verify Tesseract OCR and Poppler installations for Finance Agent."""

import sys
import subprocess
import os

def check_tesseract_system():
    """Check if Tesseract is installed and in PATH."""
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ Tesseract OCR (System): {version_line}")
            return True
        else:
            print("❌ Tesseract OCR (System): Command failed")
            return False
    except FileNotFoundError:
        print("❌ Tesseract OCR (System): Not found in PATH")
        print("   → Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   → Add to PATH: C:\\Program Files\\Tesseract-OCR")
        return False
    except Exception as e:
        print(f"❌ Tesseract OCR (System): Error - {e}")
        return False

def check_tesseract_python():
    """Check if pytesseract can access Tesseract."""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR (Python): Version {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR (Python): {e}")
        print("   → Make sure Tesseract is installed and in PATH")
        return False

def check_poppler_system():
    """Check if Poppler is installed and in PATH."""
    try:
        result = subprocess.run(
            ['pdftoppm', '-h'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 or 'pdftoppm' in result.stderr.lower():
            print("✅ Poppler (System): Installed and accessible")
            return True
        else:
            print("❌ Poppler (System): Command failed")
            return False
    except FileNotFoundError:
        print("❌ Poppler (System): Not found in PATH")
        print("   → Download from: https://github.com/oschwartz10612/poppler-windows/releases")
        print("   → Extract to: C:\\poppler")
        print("   → Add to PATH: C:\\poppler\\bin")
        return False
    except Exception as e:
        print(f"❌ Poppler (System): Error - {e}")
        return False

def check_poppler_python():
    """Check if pdf2image can access Poppler."""
    try:
        from pdf2image import convert_from_path
        print("✅ Poppler (Python): pdf2image can access Poppler")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if 'poppler' in error_msg or 'pdftoppm' in error_msg:
            print(f"❌ Poppler (Python): {e}")
            print("   → Make sure Poppler is installed and bin folder is in PATH")
        else:
            print(f"❌ Poppler (Python): {e}")
        return False

def check_opencv():
    """Check if OpenCV is installed."""
    try:
        import cv2
        print(f"✅ OpenCV: Version {cv2.__version__}")
        return True
    except ImportError:
        print("❌ OpenCV: Not installed")
        print("   → Install: pip install opencv-python")
        return False

def check_pillow():
    """Check if Pillow is installed."""
    try:
        from PIL import Image
        print(f"✅ Pillow: Version {Image.__version__}")
        return True
    except ImportError:
        print("❌ Pillow: Not installed")
        print("   → Install: pip install Pillow")
        return False

def main():
    print("=" * 70)
    print("OCR Dependencies Verification for Finance Agent")
    print("=" * 70)
    print()
    
    results = {
        "Tesseract (System)": check_tesseract_system(),
        "Tesseract (Python)": check_tesseract_python(),
        "Poppler (System)": check_poppler_system(),
        "Poppler (Python)": check_poppler_python(),
        "OpenCV": check_opencv(),
        "Pillow": check_pillow(),
    }
    
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    
    all_ok = all(results.values())
    passed = sum(results.values())
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    print()
    
    if all_ok:
        print("✅ All OCR dependencies are properly installed and configured!")
        print()
        print("Your Finance Agent is ready for OCR functionality:")
        print("  • Receipt scanning")
        print("  • Invoice processing")
        print("  • PDF document OCR")
        return 0
    else:
        print("❌ Some dependencies need installation or configuration.")
        print()
        print("Please refer to: MOBILE_OCR_GUIDE.md for installation instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())




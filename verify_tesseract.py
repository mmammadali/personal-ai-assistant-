"""
Verify Tesseract OCR Installation
Checks if Tesseract is properly installed and configured
"""
import os
import sys
from pathlib import Path

def find_tesseract():
    """Find Tesseract installation"""
    # Common Windows installation paths
    common_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    # Check PATH
    path_dirs = os.environ.get('PATH', '').split(os.pathsep)
    for path_dir in path_dirs:
        tesseract_path = os.path.join(path_dir, 'tesseract.exe')
        if os.path.exists(tesseract_path):
            return tesseract_path
    
    # Check common paths
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def verify_tesseract():
    """Verify Tesseract installation and configuration"""
    print("="*60)
    print("Tesseract OCR Verification")
    print("="*60)
    
    # Find Tesseract
    tesseract_path = find_tesseract()
    
    if tesseract_path:
        print(f"✅ Found Tesseract at: {tesseract_path}")
        
        # Try to get version
        try:
            import subprocess
            result = subprocess.run(
                [tesseract_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"✅ Version: {version_line}")
            else:
                print(f"⚠️  Could not get version: {result.stderr}")
        except Exception as e:
            print(f"⚠️  Error checking version: {e}")
        
        # Check if pytesseract can use it
        try:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
            # Try to get version via pytesseract
            version = pytesseract.get_tesseract_version()
            print(f"✅ pytesseract can access Tesseract (version: {version})")
            
            # Check for Persian language support
            try:
                langs = pytesseract.get_languages()
                if 'fas' in langs or 'per' in langs:
                    print("✅ Persian language support found")
                else:
                    print("⚠️  Persian language support not found")
                    print(f"   Available languages: {', '.join(langs[:10])}")
            except Exception as e:
                print(f"⚠️  Could not check languages: {e}")
            
            return True, tesseract_path
        except ImportError:
            print("❌ pytesseract not installed. Install with: pip install pytesseract")
            return False, tesseract_path
        except Exception as e:
            print(f"⚠️  pytesseract error: {e}")
            print(f"   Try setting: pytesseract.pytesseract.tesseract_cmd = r'{tesseract_path}'")
            return False, tesseract_path
    else:
        print("❌ Tesseract not found in PATH or common locations")
        print("\nTo fix:")
        print("1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install it (default: C:\\Program Files\\Tesseract-OCR)")
        print("3. Add to PATH: C:\\Program Files\\Tesseract-OCR")
        print("4. Restart your terminal/IDE")
        print("\nOr set manually in config.py:")
        print(f"   TESSERACT_PATH = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
        return False, None

if __name__ == "__main__":
    success, path = verify_tesseract()
    
    if success and path:
        print("\n" + "="*60)
        print("✅ Tesseract is properly configured!")
        print("="*60)
        print(f"\nTo use in your code, add to config.py:")
        print(f"TESSERACT_PATH = r'{path}'")
        print("\nOr set in your code:")
        print(f"import pytesseract")
        print(f"pytesseract.pytesseract.tesseract_cmd = r'{path}'")
    else:
        print("\n" + "="*60)
        print("❌ Tesseract needs configuration")
        print("="*60)
        sys.exit(1)


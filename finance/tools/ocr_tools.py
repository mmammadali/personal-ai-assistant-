"""
OCR Tools for Document Processing
Extracts data from receipts, invoices, and bank statements
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from langchain.tools import tool
from langchain_core.tools import Tool

# Configure Tesseract path if available
try:
    from config import TESSERACT_PATH
    import pytesseract
    # Set Tesseract path if it's a full path (not just "tesseract")
    if TESSERACT_PATH and TESSERACT_PATH != "tesseract" and Path(TESSERACT_PATH).exists():
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
except (ImportError, AttributeError):
    pass
except Exception:
    pass

# Optional imports for OCR functionality
try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    cv2 = None
    np = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None


# ===================== IMAGE QUALITY CHECKER =====================

@tool
def check_image_quality(image_path: str) -> dict:
    """
    Check image quality before OCR processing
    
    Args:
        image_path: Path to image file
        
    Returns:
        Quality assessment with score and recommendations
    """
    if not CV2_AVAILABLE:
        return {
            "success": False,
            "error": "OpenCV (cv2) is not installed. Please install opencv-python for OCR functionality.",
            "quality_score": 0,
            "issues": ["OpenCV not available"],
            "recommendations": ["Install opencv-python: pip install opencv-python"]
        }
    
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return {
                "success": False,
                "quality_score": 0,
                "issues": ["Cannot read image file"],
                "recommendations": ["Check file format and integrity"]
            }
        
        height, width = img.shape[:2]
        issues = []
        recommendations = []
        quality_score = 100
        
        # Check resolution
        if width < 800 or height < 600:
            issues.append(f"Low resolution: {width}x{height}")
            recommendations.append("Use higher resolution image (min 800x600)")
            quality_score -= 30
        
        # Check blur (Laplacian variance)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 100:
            issues.append(f"Image is blurry (variance: {laplacian_var:.2f})")
            recommendations.append("Take a sharper photo with better focus")
            quality_score -= 25
        
        # Check brightness
        mean_brightness = np.mean(gray)
        if mean_brightness < 50:
            issues.append("Image is too dark")
            recommendations.append("Improve lighting conditions")
            quality_score -= 20
        elif mean_brightness > 200:
            issues.append("Image is too bright/overexposed")
            recommendations.append("Reduce lighting or flash")
            quality_score -= 15
        
        # Check contrast
        std_brightness = np.std(gray)
        if std_brightness < 30:
            issues.append("Low contrast")
            recommendations.append("Ensure good lighting contrast")
            quality_score -= 15
        
        return {
            "success": True,
            "quality_score": max(0, quality_score),
            "resolution": f"{width}x{height}",
            "blur_score": float(laplacian_var),
            "brightness": float(mean_brightness),
            "contrast": float(std_brightness),
            "issues": issues,
            "recommendations": recommendations,
            "acceptable": quality_score >= 50
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "quality_score": 0,
            "issues": [f"Error processing image: {str(e)}"],
            "recommendations": ["Check file format and try again"]
        }


# ===================== RECEIPT OCR TOOL =====================

@tool
def extract_receipt_data(image_path: str) -> dict:
    """
    Extract structured data from receipt images using OCR
    Supports Persian and English text
    
    Args:
        image_path: Path to receipt image
        
    Returns:
        Extracted receipt data with vendor, amount, date, items
    """
    try:
        # First check image quality (if OpenCV available)
        if CV2_AVAILABLE:
            quality_check = check_image_quality(image_path)
            if not quality_check.get("acceptable", False):
                return {
                    "success": False,
                    "message": "تصویر با کیفیت مناسب نیست",
                    "quality_issues": quality_check.get("issues", []),
                    "recommendations": quality_check.get("recommendations", [])
                }
        
        # Try Tesseract OCR (if available)
        if not PIL_AVAILABLE:
            return {
                "success": False,
                "message": "PIL (Pillow) is not installed. Please install Pillow for OCR functionality.",
                "data": {}
            }
        
        try:
            import pytesseract
            
            img = Image.open(image_path)
            # Persian + English OCR
            text = pytesseract.image_to_string(img, lang='fas+eng')
            
            # Parse extracted text (simple pattern matching for now)
            # TODO: Enhance with LLM-based extraction for better accuracy
            extracted_data = _parse_receipt_text(text)
            
            return {
                "success": True,
                "document_type": "receipt",
                "data": extracted_data,
                "raw_text": text,
                "confidence": 0.75,
                "method": "tesseract"
            }
        
        except ImportError:
            # Tesseract not available, try PaddleOCR
            try:
                from paddleocr import PaddleOCR
                
                ocr = PaddleOCR(use_angle_cls=True, lang='fa')
                result = ocr.ocr(image_path, cls=True)
                
                # Extract text from PaddleOCR result
                text = "\n".join([line[1][0] for line in result[0]]) if result and result[0] else ""
                extracted_data = _parse_receipt_text(text)
                
                return {
                    "success": True,
                    "document_type": "receipt",
                    "data": extracted_data,
                    "raw_text": text,
                    "confidence": 0.80,
                    "method": "paddleocr"
                }
            
            except ImportError:
                # No OCR available, return placeholder
                return {
                    "success": False,
                    "message": "OCR engines not available. Please install pytesseract or paddleocr.",
                    "data": {}
                }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در پردازش رسید: {str(e)}"
        }


def _parse_receipt_text(text: str) -> dict:
    """Parse receipt text to extract structured data"""
    import re
    from datetime import datetime
    
    data = {
        "vendor": None,
        "amount": None,
        "currency": "IRR",
        "date": None,
        "items": [],
        "confidence": 0.6
    }
    
    # Try to extract amount (Persian and English numbers)
    amount_patterns = [
        r'(?:جمع|total|مبلغ|amount)[:\s]*(\d[\d,]+)',
        r'(\d[\d,]+)\s*(?:ریال|تومان|rial|toman)',
        r'(?:قیمت|price)[:\s]*(\d[\d,]+)'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                data["amount"] = float(amount_str)
                break
            except ValueError:
                pass
    
    # Try to extract date
    date_patterns = [
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4}/\d{2}/\d{2})'  # Jalali date
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            data["date"] = match.group(1)
            break
    
    # Try to extract vendor name (first line often)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        data["vendor"] = lines[0][:50]  # First line, max 50 chars
    
    return data


# ===================== INVOICE EXTRACTOR TOOL =====================

@tool
def extract_invoice_data(file_path: str) -> dict:
    """
    Extract structured data from invoices (PDF or image)
    Uses LLM-based extraction for better accuracy
    
    Args:
        file_path: Path to invoice file (PDF or image)
        
    Returns:
        Extracted invoice data
    """
    try:
        # Check file type
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png']:
            # Image invoice
            if CV2_AVAILABLE:
                quality_check = check_image_quality(file_path)
                if not quality_check.get("acceptable", False):
                    return {
                        "success": False,
                        "message": "تصویر با کیفیت مناسب نیست"
                    }
            
            # TODO: Implement image-based invoice extraction
            return {
                "success": False,
                "message": "استخراج فاکتور از تصویر در حال توسعه است"
            }
        
        elif file_ext == '.pdf':
            # PDF invoice
            # TODO: Implement PDF invoice extraction
            return {
                "success": False,
                "message": "استخراج فاکتور از PDF در حال توسعه است"
            }
        
        else:
            return {
                "success": False,
                "message": f"فرمت فایل پشتیبانی نمی‌شود: {file_ext}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در پردازش فاکتور: {str(e)}"
        }


# ===================== BANK STATEMENT PARSER TOOL =====================

@tool
def parse_bank_statement(file_path: str) -> dict:
    """
    Parse bank statements and extract transaction list
    Supports major Iranian banks (Melli, Mellat, Tejarat, Pasargad)
    
    Args:
        file_path: Path to bank statement PDF
        
    Returns:
        List of transactions from statement
    """
    try:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext != '.pdf':
            return {
                "success": False,
                "message": "فقط فایل PDF پشتیبانی می‌شود"
            }
        
        # TODO: Implement PDF table extraction and bank format detection
        return {
            "success": False,
            "message": "پردازش صورتحساب بانکی در حال توسعه است",
            "transactions": []
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در پردازش صورتحساب: {str(e)}"
        }


# ===================== IMAGE PREPROCESSOR =====================

def preprocess_image(image_path: str, output_path: Optional[str] = None) -> str:
    """
    Preprocess image to improve OCR accuracy
    - Deskew
    - Enhance contrast
    - Noise reduction
    - Binarization
    
    Args:
        image_path: Input image path
        output_path: Output image path (optional)
        
    Returns:
        Path to preprocessed image
    """
    if not CV2_AVAILABLE:
        return image_path  # Return original if OpenCV not available
    
    try:
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Enhance contrast (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Binarization (Otsu's method)
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Save preprocessed image
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('.preprocessed.png'))
        
        cv2.imwrite(output_path, binary)
        return output_path
    
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return image_path  # Return original if preprocessing fails


# ===================== TOOL EXPORTS =====================

# Export as LangChain tools
OCR_TOOLS = [
    check_image_quality,
    extract_receipt_data,
    extract_invoice_data,
    parse_bank_statement
]


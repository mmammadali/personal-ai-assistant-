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

# Optional imports for PDF processing
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False
        PdfReader = None


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


def _parse_invoice_text(text: str) -> dict:
    """Parse invoice text to extract structured data (more detailed than receipt)"""
    import re
    from datetime import datetime
    
    data = {
        "vendor": None,
        "invoice_number": None,
        "amount": None,
        "subtotal": None,
        "tax": None,
        "tax_rate": None,
        "currency": "IRR",
        "date": None,
        "due_date": None,
        "items": [],
        "confidence": 0.65
    }
    
    text_lower = text.lower()
    
    # Try to extract invoice number
    invoice_patterns = [
        r'(?:شماره|number|invoice\s*#?|فاکتور\s*#?)[:\s]*([A-Z0-9\-]+)',
        r'(?:INV|FAK|FAC)[:\s]*([0-9\-]+)',
        r'#\s*([0-9]+)'
    ]
    
    for pattern in invoice_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data["invoice_number"] = match.group(1).strip()
            break
    
    # Try to extract total amount (more patterns for invoices)
    amount_patterns = [
        r'(?:جمع کل|total|مبلغ کل|amount|قیمت کل)[:\s]*(\d[\d,]+)',
        r'(\d[\d,]+)\s*(?:ریال|تومان|rial|toman)',
        r'(?:قیمت|price)[:\s]*(\d[\d,]+)',
        r'total[:\s]*(\d[\d,]+)',
        r'جمع[:\s]*(\d[\d,]+)'
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '').replace('،', '')
            try:
                data["amount"] = float(amount_str)
                break
            except ValueError:
                pass
    
    # Try to extract subtotal
    subtotal_patterns = [
        r'(?:جمع|subtotal|قبل از مالیات)[:\s]*(\d[\d,]+)',
        r'subtotal[:\s]*(\d[\d,]+)'
    ]
    
    for pattern in subtotal_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '').replace('،', '')
            try:
                data["subtotal"] = float(amount_str)
                break
            except ValueError:
                pass
    
    # Try to extract tax/VAT
    tax_patterns = [
        r'(?:مالیات|tax|vat|ارزش افزوده)[:\s]*(\d[\d,]+)',
        r'(?:مالیات|tax)[:\s]*(\d+)%',
        r'vat[:\s]*(\d[\d,]+)'
    ]
    
    for pattern in tax_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            tax_str = match.group(1).replace(',', '').replace('،', '')
            try:
                if '%' in match.group(0):
                    data["tax_rate"] = float(tax_str)
                else:
                    data["tax"] = float(tax_str)
                break
            except ValueError:
                pass
    
    # Default tax rate for Iran (9%)
    if not data["tax_rate"] and not data["tax"]:
        data["tax_rate"] = 9.0
    
    # Try to extract dates (invoice date and due date)
    date_patterns = [
        r'(?:تاریخ|date)[:\s]*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4}/\d{2}/\d{2})'  # Jalali date
    ]
    
    dates_found = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            dates_found.append(match)
    
    if dates_found:
        data["date"] = dates_found[0]
        if len(dates_found) > 1:
            data["due_date"] = dates_found[1]
    
    # Try to extract vendor name (usually in header)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        # First few lines often contain vendor info
        for i, line in enumerate(lines[:5]):
            # Skip common invoice headers
            if not any(word in line.lower() for word in ['invoice', 'فاکتور', 'receipt', 'رسید', 'date', 'تاریخ']):
                if len(line) > 3 and len(line) < 100:
                    data["vendor"] = line[:80]
                    break
    
    # Try to extract items (simple line-by-line extraction)
    # Look for lines with numbers that might be items
    item_pattern = r'(.+?)\s+(\d[\d,]+)\s*(?:ریال|تومان|rial|toman)?'
    potential_items = re.findall(item_pattern, text, re.IGNORECASE)
    
    items = []
    for item_name, item_price in potential_items[:10]:  # Limit to 10 items
        item_name = item_name.strip()
        if len(item_name) > 2 and len(item_name) < 100:
            try:
                price = float(item_price.replace(',', '').replace('،', ''))
                if 1000 <= price <= 1000000000:  # Reasonable price range
                    items.append({
                        "name": item_name,
                        "price": price,
                        "quantity": 1
                    })
            except ValueError:
                pass
    
    if items:
        data["items"] = items
    
    return data


# ===================== INVOICE EXTRACTOR TOOL =====================

@tool
def extract_invoice_data(file_path: str) -> dict:
    """
    Extract structured data from invoices (PDF or image)
    Supports Persian and English invoices
    
    Args:
        file_path: Path to invoice file (PDF or image)
        
    Returns:
        Extracted invoice data with vendor, amount, date, items, tax
    """
    try:
        # Check file type
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png']:
            # Image invoice - use OCR similar to receipt extraction
            if not PIL_AVAILABLE:
                return {
                    "success": False,
                    "message": "PIL (Pillow) is not installed. Please install Pillow for OCR functionality.",
                    "data": {}
                }
            
            # Check image quality if OpenCV available
            if CV2_AVAILABLE:
                quality_check = check_image_quality(file_path)
                if not quality_check.get("acceptable", False):
                    # Still try to extract, but warn user
                    pass
            
            # Preprocess image if OpenCV available
            processed_image_path = file_path
            if CV2_AVAILABLE:
                try:
                    processed_image_path = preprocess_image(file_path)
                except Exception:
                    processed_image_path = file_path
            
            # Try Tesseract OCR first
            try:
                import pytesseract
                img = Image.open(processed_image_path)
                # Persian + English OCR
                text = pytesseract.image_to_string(img, lang='fas+eng')
                method = "tesseract"
            except (ImportError, Exception):
                # Try PaddleOCR
                try:
                    from paddleocr import PaddleOCR
                    ocr = PaddleOCR(use_angle_cls=True, lang='fa')
                    result = ocr.ocr(processed_image_path, cls=True)
                    text = "\n".join([line[1][0] for line in result[0]]) if result and result[0] else ""
                    method = "paddleocr"
                except ImportError:
                    return {
                        "success": False,
                        "message": "OCR engines not available. Please install pytesseract or paddleocr.",
                        "data": {}
                    }
            
            # Parse invoice text
            extracted_data = _parse_invoice_text(text)
            
            return {
                "success": True,
                "document_type": "invoice",
                "data": extracted_data,
                "raw_text": text,
                "confidence": 0.75,
                "method": method
            }
        
        elif file_ext == '.pdf':
            # PDF invoice - try text extraction first, then OCR if needed
            text_content = ""
            extracted_data = {}
            
            # First, try to extract text directly from PDF
            if PYPDF_AVAILABLE:
                try:
                    reader = PdfReader(file_path)
                    text_content = ""
                    for page in reader.pages:
                        text_content += page.extract_text() + "\n"
                    
                    if text_content.strip():
                        # Text extraction successful
                        extracted_data = _parse_invoice_text(text_content)
                        return {
                            "success": True,
                            "document_type": "invoice",
                            "data": extracted_data,
                            "raw_text": text_content,
                            "confidence": 0.85,
                            "method": "pypdf_text"
                        }
                except Exception as e:
                    print(f"PDF text extraction failed: {e}, trying OCR...")
            
            # If text extraction failed or not available, try OCR on PDF pages
            if PDF2IMAGE_AVAILABLE and PIL_AVAILABLE:
                try:
                    # Convert PDF pages to images
                    images = convert_from_path(file_path, dpi=300, first_page=1, last_page=3)
                    
                    all_text = ""
                    for i, image in enumerate(images):
                        # Try Tesseract
                        try:
                            import pytesseract
                            page_text = pytesseract.image_to_string(image, lang='fas+eng')
                            all_text += page_text + "\n"
                        except (ImportError, Exception):
                            # Try PaddleOCR
                            try:
                                from paddleocr import PaddleOCR
                                ocr = PaddleOCR(use_angle_cls=True, lang='fa')
                                result = ocr.ocr(image, cls=True)
                                page_text = "\n".join([line[1][0] for line in result[0]]) if result and result[0] else ""
                                all_text += page_text + "\n"
                            except ImportError:
                                return {
                                    "success": False,
                                    "message": "OCR engines not available. Please install pytesseract or paddleocr.",
                                    "data": {}
                                }
                    
                    extracted_data = _parse_invoice_text(all_text)
                    
                    return {
                        "success": True,
                        "document_type": "invoice",
                        "data": extracted_data,
                        "raw_text": all_text,
                        "confidence": 0.70,
                        "method": "pdf_ocr"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "message": f"خطا در پردازش PDF: {str(e)}. ممکن است نیاز به نصب Poppler باشد."
                    }
            else:
                return {
                    "success": False,
                    "message": "PDF processing requires pdf2image and/or pypdf. Please install: pip install pdf2image pypdf",
                    "data": {}
                }
        
        else:
            return {
                "success": False,
                "message": f"فرمت فایل پشتیبانی نمی‌شود: {file_ext}. فرمت‌های مجاز: JPG, PNG, PDF"
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
        
        transactions = []
        text_content = ""
        
        # First, try to extract text directly from PDF
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(file_path)
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
            except Exception as e:
                print(f"PDF text extraction failed: {e}")
        
        # If text extraction failed or not available, try OCR
        if not text_content.strip() and PDF2IMAGE_AVAILABLE and PIL_AVAILABLE:
            try:
                # Convert first few pages to images
                images = convert_from_path(file_path, dpi=200, first_page=1, last_page=5)
                
                all_text = ""
                for image in images:
                    # Try Tesseract
                    try:
                        import pytesseract
                        page_text = pytesseract.image_to_string(image, lang='fas+eng')
                        all_text += page_text + "\n"
                    except (ImportError, Exception):
                        # Try PaddleOCR
                        try:
                            from paddleocr import PaddleOCR
                            ocr = PaddleOCR(use_angle_cls=True, lang='fa')
                            result = ocr.ocr(image, cls=True)
                            page_text = "\n".join([line[1][0] for line in result[0]]) if result and result[0] else ""
                            all_text += page_text + "\n"
                        except ImportError:
                            return {
                                "success": False,
                                "message": "OCR engines not available. Please install pytesseract or paddleocr.",
                                "transactions": []
                            }
                
                text_content = all_text
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"خطا در پردازش PDF: {str(e)}. ممکن است نیاز به نصب Poppler باشد."
                }
        
        if not text_content.strip():
            return {
                "success": False,
                "message": "نمی‌توان محتوای PDF را استخراج کرد. لطفاً مطمئن شوید که PDF قابل خواندن است.",
                "transactions": []
            }
        
        # Parse transactions from text
        transactions = _parse_bank_statement_text(text_content)
        
        if transactions:
            return {
                "success": True,
                "document_type": "bank_statement",
                "transactions": transactions,
                "transaction_count": len(transactions),
                "message": f"✅ {len(transactions)} تراکنش با موفقیت استخراج شد"
            }
        else:
            return {
                "success": False,
                "message": "نمی‌توان تراکنش‌ها را از صورتحساب استخراج کرد. ممکن است فرمت بانک پشتیبانی نشود.",
                "transactions": []
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"خطا در پردازش صورتحساب: {str(e)}"
        }


def _parse_bank_statement_text(text: str) -> list:
    """Parse bank statement text to extract transactions"""
    import re
    
    transactions = []
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Common patterns for Iranian bank statements
    # Pattern 1: Date, Description, Amount (Debit/Credit)
    # Pattern 2: Date | Description | Debit | Credit | Balance
    
    # Look for transaction lines (usually contain dates and amounts)
    date_pattern = r'(\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}[/-]\d{1,2}[/-]\d{4})'
    amount_pattern = r'(\d[\d,]+)\s*(?:ریال|تومان|rial|toman)?'
    
    for i, line in enumerate(lines):
        # Check if line contains a date
        date_match = re.search(date_pattern, line)
        if not date_match:
            continue
        
        # Check if line contains an amount
        amount_matches = re.findall(amount_pattern, line, re.IGNORECASE)
        if not amount_matches:
            continue
        
        # Try to extract transaction details
        date = date_match.group(1)
        
        # Extract description (text between date and amount)
        description = line
        for amount_str in amount_matches:
            description = description.replace(amount_str, '').strip()
        description = re.sub(date_pattern, '', description).strip()
        description = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', description).strip()
        
        # Extract amounts
        amounts = []
        for amount_str in amount_matches:
            try:
                amount = float(amount_str.replace(',', '').replace('،', ''))
                if 1000 <= amount <= 100000000000:  # Reasonable range
                    amounts.append(amount)
            except ValueError:
                pass
        
        if amounts and description:
            # Determine transaction type (debit/credit)
            # Usually the last amount is the balance, second-to-last is the transaction amount
            if len(amounts) >= 2:
                transaction_amount = amounts[-2]  # Second to last
            else:
                transaction_amount = amounts[0]
            
            # Try to determine if it's debit or credit based on context
            # This is a simplified approach - can be enhanced
            transaction_type = "expense"  # Default to expense
            
            # Look for keywords
            if any(word in line.lower() for word in ['واریز', 'deposit', 'دریافت', 'credit', 'افزایش']):
                transaction_type = "income"
            elif any(word in line.lower() for word in ['برداشت', 'withdrawal', 'پرداخت', 'debit', 'کاهش']):
                transaction_type = "expense"
            
            transaction = {
                "date": date,
                "description": description[:200],  # Limit description length
                "amount": transaction_amount,
                "type": transaction_type,
                "currency": "IRR"
            }
            
            transactions.append(transaction)
            
            # Limit to reasonable number of transactions
            if len(transactions) >= 100:
                break
    
    return transactions


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


# ===================== DEPENDENCY CHECKER =====================

def check_ocr_dependencies() -> dict:
    """
    Check which OCR and PDF processing dependencies are available
    
    Returns:
        Dictionary with availability status of each dependency
    """
    status = {
        "opencv": CV2_AVAILABLE,
        "pillow": PIL_AVAILABLE,
        "pytesseract": False,
        "paddleocr": False,
        "pdf2image": PDF2IMAGE_AVAILABLE,
        "pypdf": PYPDF_AVAILABLE,
        "recommendations": []
    }
    
    # Check Tesseract
    try:
        import pytesseract
        status["pytesseract"] = True
    except ImportError:
        status["recommendations"].append("Install pytesseract: pip install pytesseract")
    
    # Check PaddleOCR
    try:
        from paddleocr import PaddleOCR
        status["paddleocr"] = True
    except ImportError:
        status["recommendations"].append("Install paddleocr: pip install paddleocr")
    
    # Check OpenCV
    if not CV2_AVAILABLE:
        status["recommendations"].append("Install opencv-python: pip install opencv-python")
    
    # Check Pillow
    if not PIL_AVAILABLE:
        status["recommendations"].append("Install Pillow: pip install Pillow")
    
    # Check PDF2Image
    if not PDF2IMAGE_AVAILABLE:
        status["recommendations"].append("Install pdf2image: pip install pdf2image (also requires Poppler)")
    
    # Check PyPDF
    if not PYPDF_AVAILABLE:
        status["recommendations"].append("Install pypdf: pip install pypdf")
    
    # Determine OCR capability
    status["ocr_available"] = status["pytesseract"] or status["paddleocr"]
    status["pdf_processing_available"] = PDF2IMAGE_AVAILABLE or PYPDF_AVAILABLE
    
    return status


# ===================== TOOL EXPORTS =====================

# Export as LangChain tools
OCR_TOOLS = [
    check_image_quality,
    extract_receipt_data,
    extract_invoice_data,
    parse_bank_statement
]


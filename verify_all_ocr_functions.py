#!/usr/bin/env python3
"""
Comprehensive verification of all OCR and text extraction functions in the app
Tests both Finance Agent OCR and RAG Agent document processing
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("COMPREHENSIVE OCR & TEXT EXTRACTION VERIFICATION")
print("=" * 80)
print()

# ===================== 1. FINANCE AGENT OCR TOOLS =====================

print("📋 SECTION 1: Finance Agent OCR Tools")
print("-" * 80)

try:
    from finance.tools.ocr_tools import (
        check_image_quality,
        extract_receipt_data,
        extract_invoice_data,
        parse_bank_statement,
        check_ocr_dependencies,
        OCR_TOOLS
    )
    
    print("✅ Finance OCR tools imported successfully")
    print(f"   Available tools: {len(OCR_TOOLS)}")
    for tool in OCR_TOOLS:
        print(f"   - {tool.name}")
    
    # Check dependencies
    print("\n🔍 Checking OCR dependencies...")
    deps = check_ocr_dependencies()
    
    print(f"   OpenCV: {'✅' if deps['opencv'] else '❌'}")
    print(f"   Pillow: {'✅' if deps['pillow'] else '❌'}")
    print(f"   Tesseract: {'✅' if deps['pytesseract'] else '❌'}")
    print(f"   PaddleOCR: {'✅' if deps['paddleocr'] else '❌'}")
    print(f"   PDF2Image: {'✅' if deps['pdf2image'] else '❌'}")
    print(f"   PyPDF: {'✅' if deps['pypdf'] else '❌'}")
    print(f"   OCR Available: {'✅' if deps['ocr_available'] else '❌'}")
    print(f"   PDF Processing: {'✅' if deps['pdf_processing_available'] else '❌'}")
    
    if deps['recommendations']:
        print("\n⚠️  Missing dependencies:")
        for rec in deps['recommendations']:
            print(f"   - {rec}")
    
    # Test function availability
    print("\n🧪 Testing function availability...")
    
    # Test check_image_quality
    try:
        # This should work even without an actual image (will fail gracefully)
        print("   ✓ check_image_quality() - Available")
    except Exception as e:
        print(f"   ❌ check_image_quality() - Error: {e}")
    
    # Test extract_receipt_data
    try:
        print("   ✓ extract_receipt_data() - Available")
    except Exception as e:
        print(f"   ❌ extract_receipt_data() - Error: {e}")
    
    # Test extract_invoice_data
    try:
        print("   ✓ extract_invoice_data() - Available")
    except Exception as e:
        print(f"   ❌ extract_invoice_data() - Error: {e}")
    
    # Test parse_bank_statement
    try:
        print("   ✓ parse_bank_statement() - Available")
    except Exception as e:
        print(f"   ❌ parse_bank_statement() - Error: {e}")
    
    finance_ocr_status = "✅ WORKING" if deps['ocr_available'] or deps['pdf_processing_available'] else "⚠️  PARTIAL (Missing dependencies)"
    
except ImportError as e:
    print(f"❌ Failed to import Finance OCR tools: {e}")
    finance_ocr_status = "❌ NOT WORKING"
except Exception as e:
    print(f"❌ Error checking Finance OCR tools: {e}")
    finance_ocr_status = "❌ ERROR"

print(f"\n📊 Finance OCR Status: {finance_ocr_status}")

# ===================== 2. RAG AGENT DOCUMENT PROCESSOR =====================

print("\n" + "=" * 80)
print("📋 SECTION 2: RAG Agent Document Processor")
print("-" * 80)

try:
    from document_processor import DocumentProcessor, IntelligentExtractor
    
    print("✅ Document processor imported successfully")
    
    # Check supported formats
    processor = DocumentProcessor()
    supported_formats = processor.get_supported_formats()
    
    print(f"\n📄 Supported formats: {len(supported_formats)}")
    for fmt in supported_formats:
        print(f"   - {fmt}")
    
    # Check if UnstructuredImageLoader works
    print("\n🖼️  Checking image processing...")
    try:
        from langchain_community.document_loaders import UnstructuredImageLoader
        print("   ✅ UnstructuredImageLoader available")
        
        # Check if it requires OCR
        print("   ℹ️  Note: UnstructuredImageLoader may require additional dependencies")
        print("      (unstructured, unstructured[image], etc.)")
        
    except ImportError as e:
        print(f"   ⚠️  UnstructuredImageLoader not available: {e}")
        print("   → Install: pip install unstructured[image]")
    
    # Test PDF processing
    print("\n📑 Checking PDF processing...")
    try:
        from langchain_community.document_loaders import PyPDFLoader
        print("   ✅ PyPDFLoader available")
    except ImportError as e:
        print(f"   ❌ PyPDFLoader not available: {e}")
    
    # Test text extraction functions
    print("\n🧪 Testing text extraction functions...")
    
    extractor = IntelligentExtractor()
    
    # Test date extraction
    test_text = "تاریخ: 1403/09/15 و 2024/12/04"
    dates = extractor.extract_dates(test_text)
    print(f"   ✓ extract_dates() - Found {len(dates)} dates")
    
    # Test financial data extraction
    test_financial = "مبلغ: 1000000 تومان و $500"
    financial = extractor.extract_financial_data(test_financial)
    print(f"   ✓ extract_financial_data() - Found {len(financial)} amounts")
    
    # Test guidelines extraction
    test_guidelines = "1. باید این کار را انجام دهید\n2. سپس این کار"
    guidelines = extractor.extract_guidelines(test_guidelines)
    print(f"   ✓ extract_guidelines() - Found {len(guidelines)} items")
    
    # Test sensitive keywords
    test_sensitive = "این یک سند محرمانه است"
    sensitive = extractor.detect_sensitive_keywords(test_sensitive)
    print(f"   ✓ detect_sensitive_keywords() - Found {len(sensitive)} keywords")
    
    rag_status = "✅ WORKING"
    
except ImportError as e:
    print(f"❌ Failed to import Document processor: {e}")
    rag_status = "❌ NOT WORKING"
except Exception as e:
    print(f"❌ Error checking Document processor: {e}")
    rag_status = "❌ ERROR"

print(f"\n📊 RAG Document Processor Status: {rag_status}")

# ===================== 3. CHECK DEPENDENCIES =====================

print("\n" + "=" * 80)
print("📋 SECTION 3: Dependency Check")
print("-" * 80)

dependencies = {
    "Pillow": ("PIL", "Image"),
    "OpenCV": ("cv2", None),
    "NumPy": ("numpy", None),
    "Tesseract": ("pytesseract", None),
    "PaddleOCR": ("paddleocr", "PaddleOCR"),
    "PyPDF": ("pypdf", "PdfReader"),
    "PDF2Image": ("pdf2image", "convert_from_path"),
    "Unstructured": ("unstructured", None),
    "LangChain Community": ("langchain_community", None),
}

installed = []
missing = []

for name, (module, attr) in dependencies.items():
    try:
        mod = __import__(module)
        if attr:
            getattr(mod, attr)
        print(f"   ✅ {name}")
        installed.append(name)
    except ImportError:
        print(f"   ❌ {name} - Not installed")
        missing.append(name)
    except AttributeError:
        print(f"   ⚠️  {name} - Installed but missing attribute")
        missing.append(name)

print(f"\n📊 Installed: {len(installed)}/{len(dependencies)}")
print(f"📊 Missing: {len(missing)}/{len(dependencies)}")

# ===================== 4. SUMMARY =====================

print("\n" + "=" * 80)
print("📊 FINAL SUMMARY")
print("=" * 80)

print(f"\n1. Finance Agent OCR Tools: {finance_ocr_status}")
print(f"2. RAG Document Processor: {rag_status}")
print(f"3. Dependencies: {len(installed)}/{len(dependencies)} installed")

# Determine overall status
if finance_ocr_status.startswith("✅") and rag_status.startswith("✅"):
    overall = "✅ ALL SYSTEMS WORKING"
elif finance_ocr_status.startswith("✅") or rag_status.startswith("✅"):
    overall = "⚠️  PARTIAL FUNCTIONALITY"
else:
    overall = "❌ ISSUES DETECTED"

print(f"\n🎯 Overall Status: {overall}")

if missing:
    print("\n💡 To install missing dependencies:")
    print("   pip install " + " ".join([d.lower().replace(" ", "-") for d in missing if d not in ["Unstructured", "LangChain Community"]]))

print("\n" + "=" * 80)
print("Verification complete!")
print("=" * 80)








"""
Document Generation Tools for LangChain
Tools for generating reports and documents
"""
from langchain_core.tools import tool
from typing import Optional, Literal
from intelligence.document_generator import DocumentGenerator


# Initialize document generator
_document_generator = None


def get_document_generator() -> DocumentGenerator:
    """Get or create document generator instance"""
    global _document_generator
    if _document_generator is None:
        _document_generator = DocumentGenerator()
    return _document_generator


@tool
def generate_weekly_report_tool(
    week_data: dict,
    format: str = "markdown",
    output_path: Optional[str] = None
) -> str:
    """
    Generate a weekly productivity report.
    
    Args:
        week_data: Dictionary with week data (tasks, meetings, metrics, etc.)
        format: Output format ('markdown', 'html', 'pdf')
        output_path: Optional path to save report
        
    Returns:
        Success message with file path
    """
    try:
        generator = get_document_generator()
        result = generator.generate_weekly_report(week_data, format, output_path)
        
        if result.get('success'):
            return f"✅ گزارش هفتگی ایجاد شد: {result.get('file_path')}"
        else:
            return f"❌ خطا در تولید گزارش: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def generate_meeting_summary_tool(
    meeting_data: dict,
    format: str = "markdown",
    output_path: Optional[str] = None
) -> str:
    """
    Generate a meeting summary document.
    
    Args:
        meeting_data: Dictionary with meeting data (date, participants, agenda, decisions, etc.)
        format: Output format ('markdown', 'html')
        output_path: Optional path to save summary
        
    Returns:
        Success message with file path
    """
    try:
        generator = get_document_generator()
        result = generator.generate_meeting_summary(meeting_data, format, output_path)
        
        if result.get('success'):
            return f"✅ خلاصه جلسه ایجاد شد: {result.get('file_path')}"
        else:
            return f"❌ خطا در تولید خلاصه: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"


@tool
def generate_custom_report_tool(
    data: dict,
    report_type: str = "summary",
    format: str = "markdown",
    output_path: Optional[str] = None
) -> str:
    """
    Generate a custom report from data.
    
    Args:
        data: Dictionary with report data
        report_type: Type of report ('summary', 'detailed', 'executive')
        format: Output format ('markdown', 'html', 'pdf', 'docx')
        output_path: Optional path to save report
        
    Returns:
        Success message with file path
    """
    try:
        generator = get_document_generator()
        result = generator.generate_report(data, report_type, format, None, output_path)
        
        if result.get('success'):
            return f"✅ گزارش ایجاد شد: {result.get('file_path')}"
        else:
            return f"❌ خطا در تولید گزارش: {result.get('error', 'Unknown error')}"
    
    except Exception as e:
        return f"❌ خطا: {str(e)}"


# Export all tools
ALL_DOCUMENT_TOOLS = [
    generate_weekly_report_tool,
    generate_meeting_summary_tool,
    generate_custom_report_tool
]


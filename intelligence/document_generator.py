"""
Document Generator
Auto-generates reports, summaries, and documents in multiple formats
"""
from typing import List, Dict, Any, Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from config import OPENAI_API_KEY, DEFAULT_MODEL
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class DocumentGenerator:
    """Generates documents in various formats"""
    
    def __init__(self, model_name: str = None):
        self.llm = ChatOpenAI(
            model=model_name or DEFAULT_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3
        )
    
    def generate_report(
        self,
        data: Dict[str, Any],
        report_type: str = "summary",
        format: Literal["markdown", "html", "pdf", "docx"] = "markdown",
        template: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a report document
        
        Args:
            data: Data to include in report
            report_type: Type of report ('summary', 'detailed', 'executive')
            format: Output format
            template: Optional template to use
            output_path: Path to save document
            
        Returns:
            Generation result
        """
        try:
            # Generate content
            content = self._generate_content(data, report_type, template)
            
            # Save in requested format
            if format == "markdown":
                file_path = self._save_markdown(content, output_path)
            elif format == "html":
                file_path = self._save_html(content, output_path)
            elif format == "pdf":
                file_path = self._save_pdf(content, output_path)
            elif format == "docx":
                file_path = self._save_docx(content, output_path)
            else:
                file_path = self._save_markdown(content, output_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'format': format,
                'report_type': report_type
            }
        
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_weekly_report(
        self,
        week_data: Dict[str, Any],
        format: Literal["markdown", "html", "pdf"] = "markdown",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate weekly productivity report"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a comprehensive weekly productivity report.

Include:
- Executive summary
- Key metrics and statistics
- Accomplishments
- Challenges
- Recommendations
- Next week priorities"""),
            ("human", """Week Data:
{data}

Generate a professional weekly report.""")
        ])
        
        try:
            data_text = json.dumps(week_data, ensure_ascii=False, indent=2)
            
            response = self.llm.invoke(
                prompt.format_messages(data=data_text)
            )
            
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Save in requested format
            if format == "html":
                file_path = self._save_html(content, output_path or "weekly_report.html")
            elif format == "pdf":
                file_path = self._save_pdf(content, output_path or "weekly_report.pdf")
            else:
                file_path = self._save_markdown(content, output_path or "weekly_report.md")
            
            return {
                'success': True,
                'file_path': file_path,
                'format': format
            }
        
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_meeting_summary(
        self,
        meeting_data: Dict[str, Any],
        format: Literal["markdown", "html"] = "markdown",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate meeting summary document"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a professional meeting summary.

Include:
- Meeting details (date, participants, agenda)
- Key discussion points
- Decisions made
- Action items with owners
- Next steps"""),
            ("human", """Meeting Data:
{data}

Generate meeting summary.""")
        ])
        
        try:
            data_text = json.dumps(meeting_data, ensure_ascii=False, indent=2)
            
            response = self.llm.invoke(
                prompt.format_messages(data=data_text)
            )
            
            content = response.content if hasattr(response, 'content') else str(response)
            
            if format == "html":
                file_path = self._save_html(content, output_path or "meeting_summary.html")
            else:
                file_path = self._save_markdown(content, output_path or "meeting_summary.md")
            
            return {
                'success': True,
                'file_path': file_path,
                'format': format
            }
        
        except Exception as e:
            logger.error(f"Error generating meeting summary: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_content(
        self,
        data: Dict[str, Any],
        report_type: str,
        template: Optional[str]
    ) -> str:
        """Generate document content"""
        if template:
            # Use custom template
            prompt = ChatPromptTemplate.from_template(template)
        else:
            # Use default template based on report type
            if report_type == "executive":
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Generate an executive summary report."),
                    ("human", "Data: {data}")
                ])
            elif report_type == "detailed":
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Generate a detailed comprehensive report."),
                    ("human", "Data: {data}")
                ])
            else:  # summary
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "Generate a concise summary report."),
                    ("human", "Data: {data}")
                ])
        
        data_text = json.dumps(data, ensure_ascii=False, indent=2)
        
        response = self.llm.invoke(
            prompt.format_messages(data=data_text)
        )
        
        return response.content if hasattr(response, 'content') else str(response)
    
    def _save_markdown(self, content: str, output_path: Optional[str]) -> str:
        """Save as Markdown"""
        if not output_path:
            output_path = "report.md"
        
        Path(output_path).write_text(content, encoding='utf-8')
        return output_path
    
    def _save_html(self, content: str, output_path: Optional[str]) -> str:
        """Save as HTML"""
        if not output_path:
            output_path = "report.html"
        
        # Convert markdown to HTML (simple conversion)
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1, h2, h3 {{ color: #333; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
{self._markdown_to_html(content)}
</body>
</html>"""
        
        Path(output_path).write_text(html_content, encoding='utf-8')
        return output_path
    
    def _save_pdf(self, content: str, output_path: Optional[str]) -> str:
        """Save as PDF"""
        if not output_path:
            output_path = "report.pdf"
        
        try:
            # Try to use reportlab or weasyprint
            try:
                from weasyprint import HTML
                html_content = self._markdown_to_html(content)
                HTML(string=html_content).write_pdf(output_path)
            except ImportError:
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet
                    
                    doc = SimpleDocTemplate(output_path, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = []
                    
                    for line in content.split('\n'):
                        if line.strip():
                            story.append(Paragraph(line, styles['Normal']))
                            story.append(Spacer(1, 12))
                    
                    doc.build(story)
                except ImportError:
                    # Fallback: save as HTML and note PDF requires library
                    logger.warning("PDF libraries not available. Install weasyprint or reportlab.")
                    html_path = output_path.replace('.pdf', '.html')
                    self._save_html(content, html_path)
                    return html_path
        
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            # Fallback to HTML
            html_path = output_path.replace('.pdf', '.html')
            return self._save_html(content, html_path)
        
        return output_path
    
    def _save_docx(self, content: str, output_path: Optional[str]) -> str:
        """Save as DOCX"""
        if not output_path:
            output_path = "report.docx"
        
        try:
            from docx import Document
            
            doc = Document()
            
            for line in content.split('\n'):
                if line.strip():
                    if line.startswith('#'):
                        # Heading
                        level = len(line) - len(line.lstrip('#'))
                        text = line.lstrip('#').strip()
                        doc.add_heading(text, level=min(level, 9))
                    else:
                        doc.add_paragraph(line)
            
            doc.save(output_path)
        
        except ImportError:
            logger.warning("python-docx not available. Install: pip install python-docx")
            # Fallback to markdown
            return self._save_markdown(content, output_path.replace('.docx', '.md'))
        except Exception as e:
            logger.error(f"Error saving DOCX: {e}")
            return self._save_markdown(content, output_path.replace('.docx', '.md'))
        
        return output_path
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion"""
        # Very basic conversion - can be enhanced with markdown library
        html = markdown
        
        # Headers
        html = html.replace('### ', '<h3>').replace('\n###', '</h3>\n')
        html = html.replace('## ', '<h2>').replace('\n##', '</h2>\n')
        html = html.replace('# ', '<h1>').replace('\n#', '</h1>\n')
        
        # Bold
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        
        # Line breaks
        html = html.replace('\n', '<br>\n')
        
        return html


"""
Analysis Agent
Extracts action items, generates summaries, and analyzes meeting content using LLM
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import Dict, Any, List, Optional
import logging
import json
import re

from meeting.database import MeetingDatabase

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent for analyzing meeting transcripts and extracting insights"""
    
    def __init__(self, llm: ChatOpenAI, db: MeetingDatabase):
        """
        Initialize analysis agent
        
        Args:
            llm: Language model instance
            db: MeetingDatabase instance
        """
        self.llm = llm
        self.db = db
    
    def extract_action_items(
        self,
        transcript: str,
        meeting_id: int
    ) -> List[Dict[str, Any]]:
        """
        Extract action items from transcript
        
        Args:
            transcript: Meeting transcript text
            meeting_id: Meeting ID
            
        Returns:
            List of action items
        """
        try:
            prompt = f"""از متن رونویسی جلسه زیر، تمام اقدامات و وظایف (action items) را استخراج کن.

متن رونویسی:
{transcript[:5000]}

برای هر اقدام، این اطلاعات را استخراج کن:
1. توضیحات اقدام (description)
2. مسئول (assignee) - اگر ذکر شده
3. مهلت (due_date) - اگر ذکر شده (به صورت تاریخ جلالی YYYY-MM-DD)

خروجی را به صورت JSON برگردان با این فرمت:
{{
    "action_items": [
        {{
            "description": "توضیحات اقدام",
            "assignee": "نام مسئول یا null",
            "due_date": "1403-09-15 یا null"
        }}
    ]
}}

فقط JSON برگردان، هیچ متن اضافی نه."""

            system_prompt = """شما یک متخصص استخراج اقدامات از جلسات هستید.
- فقط اقدامات مشخص و قابل اجرا را استخراج کنید
- اگر مهلت ذکر نشده، null بگذارید
- اگر مسئول مشخص نشده، null بگذارید
- تاریخ‌ها را به فرمت جلالی YYYY-MM-DD تبدیل کنید
- فقط JSON برگردانید"""

            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Parse JSON from response
            response_text = response.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    action_items = data.get("action_items", [])
                    
                    # Store action items in database
                    stored_items = []
                    for item in action_items:
                        item_id = self.db.add_action_item(
                            meeting_id=meeting_id,
                            description=item.get("description", ""),
                            assignee=item.get("assignee"),
                            due_date=item.get("due_date"),
                            status="pending"
                        )
                        stored_items.append({
                            "id": item_id,
                            **item
                        })
                    
                    logger.info(f"Extracted {len(stored_items)} action items for meeting {meeting_id}")
                    return stored_items
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
                    return []
            else:
                logger.warning("No JSON found in LLM response")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting action items: {e}", exc_info=True)
            return []
    
    def generate_summary(
        self,
        transcript: str,
        meeting_id: int
    ) -> str:
        """
        Generate meeting summary
        
        Args:
            transcript: Meeting transcript text
            meeting_id: Meeting ID
            
        Returns:
            Summary text
        """
        try:
            prompt = f"""از متن رونویسی جلسه زیر، یک خلاصه جامع و حرفه‌ای بنویس.

متن رونویسی:
{transcript[:8000]}

خلاصه باید شامل این بخش‌ها باشد:
1. **خلاصه اجرایی**: خلاصه کوتاه از مباحث اصلی
2. **نکات کلیدی**: مهم‌ترین نکات مطرح شده
3. **تصمیمات**: تصمیمات گرفته شده در جلسه
4. **اقدامات**: اقدامات مورد نیاز (action items)
5. **نتیجه‌گیری**: نتیجه نهایی جلسه

خلاصه را به فارسی و به صورت ساختاریافته بنویس."""

            system_prompt = """شما یک متخصص خلاصه‌نویسی جلسات هستید.
- خلاصه باید واضح، مختصر و مفید باشد
- تمام نکات مهم را پوشش دهید
- تصمیمات و اقدامات را به وضوح مشخص کنید
- به فارسی و به صورت حرفه‌ای بنویسید"""

            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            summary = response.content.strip()
            
            # Store summary in database
            self.db.update_meeting(meeting_id, summary=summary)
            
            logger.info(f"Generated summary for meeting {meeting_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            return "خطا در تولید خلاصه جلسه"
    
    def extract_decisions(self, transcript: str) -> List[str]:
        """
        Extract decisions made in the meeting
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            List of decisions
        """
        try:
            prompt = f"""از متن رونویسی جلسه زیر، تمام تصمیمات گرفته شده را استخراج کن.

متن رونویسی:
{transcript[:5000]}

هر تصمیم را در یک خط جداگانه بنویس.
فقط تصمیمات مشخص و قطعی را استخراج کن، نه پیشنهادات یا بحث‌ها."""

            system_prompt = """شما یک متخصص استخراج تصمیمات از جلسات هستید.
- فقط تصمیمات قطعی و مشخص را استخراج کنید
- هر تصمیم را در یک خط بنویسید
- به فارسی بنویسید"""

            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Parse decisions (one per line)
            decisions = [
                line.strip()
                for line in response.content.strip().split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error extracting decisions: {e}")
            return []
    
    def extract_key_points(self, transcript: str) -> List[str]:
        """
        Extract key discussion points
        
        Args:
            transcript: Meeting transcript text
            
        Returns:
            List of key points
        """
        try:
            prompt = f"""از متن رونویسی جلسه زیر، مهم‌ترین نکات و موضوعات مطرح شده را استخراج کن.

متن رونویسی:
{transcript[:5000]}

هر نکته کلیدی را در یک خط جداگانه بنویس."""

            system_prompt = """شما یک متخصص استخراج نکات کلیدی از جلسات هستید.
- فقط نکات مهم و مرتبط را استخراج کنید
- هر نکته را در یک خط بنویسید
- به فارسی بنویسید"""

            response = self.llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=prompt)
            ])
            
            # Parse key points (one per line)
            key_points = [
                line.strip()
                for line in response.content.strip().split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            return key_points
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
    
    def analyze_meeting(
        self,
        meeting_id: int,
        extract_actions: bool = True,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Complete meeting analysis
        
        Args:
            meeting_id: Meeting ID
            extract_actions: Whether to extract action items
            generate_summary: Whether to generate summary
            
        Returns:
            Analysis results
        """
        try:
            # Get transcript
            segments = self.db.get_transcript(meeting_id)
            if not segments:
                return {
                    "success": False,
                    "error": "No transcript found for this meeting"
                }
            
            transcript = " ".join([seg.get("text", "") for seg in segments])
            
            result = {
                "success": True,
                "meeting_id": meeting_id,
                "action_items": [],
                "summary": None,
                "decisions": [],
                "key_points": []
            }
            
            # Extract action items
            if extract_actions:
                result["action_items"] = self.extract_action_items(transcript, meeting_id)
            
            # Generate summary
            if generate_summary:
                result["summary"] = self.generate_summary(transcript, meeting_id)
            
            # Extract decisions
            result["decisions"] = self.extract_decisions(transcript)
            
            # Extract key points
            result["key_points"] = self.extract_key_points(transcript)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing meeting: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


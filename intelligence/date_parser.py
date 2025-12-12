"""
Natural Date Parser
Parses natural language dates in Persian and English with Jalali awareness
"""
import jdatetime
import pytz
import re
from typing import Optional, Tuple


def _get_tehran_today() -> jdatetime.date:
    """Return today's Jalali date in Tehran timezone."""
    tehran_tz = pytz.timezone("Asia/Tehran")
    return jdatetime.datetime.now(tz=tehran_tz).date()


class NaturalDateParser:
    """Parses natural language dates in Persian and English."""
    
    def __init__(self):
        self.today = _get_tehran_today()
        self.weekday_map = {
            # Persian
            "شنبه": 5, "شنبه‌ی": 5, "شنبه‌": 5,
            "یکشنبه": 6, "یک‌شنبه": 6,
            "دوشنبه": 0,
            "سه‌شنبه": 1, "سه شنبه": 1,
            "چهارشنبه": 2,
            "پنجشنبه": 3, "پنج‌شنبه": 3,
            "جمعه": 4,
            # English
            "saturday": 5,
            "sunday": 6,
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
        }
        
        self.month_map = {
            "فروردین": 1, "اردیبهشت": 2, "خرداد": 3, "تیر": 4, "مرداد": 5, "شهریور": 6,
            "مهر": 7, "آبان": 8, "آذر": 9, "دی": 10, "بهمن": 11, "اسفند": 12,
            "azar": 9, "mehr": 7, "aban": 8, "esfand": 12, "bahman": 11, "dey": 10,
            "farvardin": 1, "ordibehesht": 2, "khordad": 3, "tir": 4, "mordad": 5, "shahrivar": 6
        }
        
        self.ordinal_map = {
            "اول": 1, "دوم": 2, "سوم": 3, "چهارم": 4, "پنجم": 5, "ششم": 6, "هفتم": 7, "هشتم": 8,
            "نهم": 9, "دهم": 10, "یازدهم": 11, "دوازدهم": 12, "سیزدهم": 13, "چهاردهم": 14,
            "پانزدهم": 15, "شانزدهم": 16, "هفدهم": 17, "هجدهم": 18, "نوزدهم": 19, "بیستم": 20,
            "بیست و یکم": 21, "بیست‌ویکم": 21, "بیست و دوم": 22, "بیست‌ودوم": 22, "بیست و سوم": 23,
            "بیست‌وسوم": 23, "بیست و چهارم": 24, "بیست‌وچهارم": 24, "بیست و پنجم": 25,
            "بیست‌وپنجم": 25, "بیست و ششم": 26, "بیست‌وششم": 26, "بیست و هفتم": 27,
            "بیست‌وهفتم": 27, "بیست و هشتم": 28, "بیست‌وهشتم": 28, "بیست و نهم": 29,
            "بیست‌ونهم": 29, "سی‌ام": 30, "سی و یکم": 31
        }
    
    def parse(self, date_string: str) -> Optional[str]:
        """Parse natural language date string to Jalali format (YYYY-MM-DD)."""
        # Refresh "today" on every parse to avoid stale dates in long sessions
        self.today = _get_tehran_today()
        date_string = date_string.strip().lower()
        
        result = self._parse_persian(date_string)
        if result:
            return result
        
        result = self._parse_english(date_string)
        if result:
            return result
        
        return self._parse_direct_format(date_string)
    
    def _parse_persian(self, date_string: str) -> Optional[str]:
        """Parse Persian date expressions."""
        if any(word in date_string for word in ['امروز', 'الان', 'حالا']):
            return self.today.strftime('%Y-%m-%d')
        
        if 'پس فردا' in date_string or 'پس‌فردا' in date_string:
            return (self.today + jdatetime.timedelta(days=2)).strftime('%Y-%m-%d')
        if 'فردا' in date_string:
            return (self.today + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        if 'دیروز' in date_string:
            return (self.today - jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        has_weekday = any(name in date_string for name in self.weekday_map.keys())
        if not has_weekday:
            if 'هفته آینده' in date_string or 'هفته بعد' in date_string:
                return (self.today + jdatetime.timedelta(days=7)).strftime('%Y-%m-%d')
            if 'هفته قبل' in date_string or 'هفته گذشته' in date_string:
                return (self.today - jdatetime.timedelta(days=7)).strftime('%Y-%m-%d')
        
        if 'ماه آینده' in date_string or 'ماه بعد' in date_string:
            return self._shift_months(1)
        if 'ماه قبل' in date_string or 'ماه گذشته' in date_string:
            return self._shift_months(-1)
        
        weekday_result = self._parse_weekday(date_string, language="fa")
        if weekday_result:
            return weekday_result
        
        match = re.search(r'(\d+)\s*روز\s*(بعد|دیگر|آینده)', date_string)
        if match:
            days = int(match.group(1))
            return (self.today + jdatetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        day_month_result = self._parse_day_month(date_string)
        if day_month_result:
            return day_month_result
        
        match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_string)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                date = jdatetime.date(year, month, day)
                return date.strftime('%Y-%m-%d')
            except:
                pass
        
        return None
    
    def _parse_english(self, date_string: str) -> Optional[str]:
        """Parse English date expressions."""
        if any(word in date_string for word in ['today', 'now']):
            return self.today.strftime('%Y-%m-%d')
        
        if 'day after tomorrow' in date_string:
            return (self.today + jdatetime.timedelta(days=2)).strftime('%Y-%m-%d')
        if 'tomorrow' in date_string:
            return (self.today + jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        if 'yesterday' in date_string:
            return (self.today - jdatetime.timedelta(days=1)).strftime('%Y-%m-%d')
        
        has_weekday = any(name in date_string for name in self.weekday_map.keys())
        if not has_weekday:
            if 'next week' in date_string:
                return (self.today + jdatetime.timedelta(days=7)).strftime('%Y-%m-%d')
            if 'last week' in date_string or 'previous week' in date_string:
                return (self.today - jdatetime.timedelta(days=7)).strftime('%Y-%m-%d')
        if 'next month' in date_string:
            return self._shift_months(1)
        if 'last month' in date_string or 'previous month' in date_string:
            return self._shift_months(-1)
        
        weekday_result = self._parse_weekday(date_string, language="en")
        if weekday_result:
            return weekday_result
        
        match = re.search(r'(\d+)\s*days?\s*(from now|later|ahead)?', date_string)
        if match:
            days = int(match.group(1))
            return (self.today + jdatetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_string)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                date = jdatetime.date(year, month, day)
                return date.strftime('%Y-%m-%d')
            except:
                pass
        
        return None
    
    def _parse_direct_format(self, date_string: str) -> Optional[str]:
        """Parse direct date formats."""
        match = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', date_string)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                date = jdatetime.date(year, month, day)
                return date.strftime('%Y-%m-%d')
            except:
                pass
        return None
    
    def parse_with_time(self, date_time_string: str) -> Optional[Tuple[str, Optional[str]]]:
        """Parse date and time string."""
        time_match = re.search(r'(\d{1,2}):(\d{2})', date_time_string)
        time_str = None
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            time_str = f"{hour:02d}:{minute:02d}"
        
        date_only = re.sub(r'\d{1,2}:\d{2}', '', date_time_string).strip()
        date_str = self.parse(date_only)
        
        if date_str:
            return (date_str, time_str)
        
        return None
    
    def parse_relative_date(self, date_string: str) -> Optional[str]:
        """Parse relative date expressions (fallback)."""
        match = re.search(r'(\d+)\s*(روز|day)', date_string, re.IGNORECASE)
        if match:
            days = int(match.group(1))
            return (self.today + jdatetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        match = re.search(r'(\d+)\s*(هفته|week)', date_string, re.IGNORECASE)
        if match:
            weeks = int(match.group(1))
            return (self.today + jdatetime.timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        
        return None
    
    # ---------- helpers ----------
    def _shift_months(self, delta: int) -> str:
        """Shift Jalali month by delta (can be negative)."""
        year, month, day = self.today.year, self.today.month, self.today.day
        new_month = month + delta
        new_year = year
        while new_month > 12:
            new_month -= 12
            new_year += 1
        while new_month < 1:
            new_month += 12
            new_year -= 1
        # Clamp day to month length (approximate)
        try:
            jalali_first = jdatetime.date(new_year, new_month, 1)
            days_in_month = (jalali_first.togregorian().replace(day=28) + jdatetime.timedelta(days=4)).day
        except Exception:
            days_in_month = 29
        safe_day = min(day, days_in_month)
        return jdatetime.date(new_year, new_month, safe_day).strftime('%Y-%m-%d')
    
    def _parse_weekday(self, date_string: str, language: str) -> Optional[str]:
        """Parse expressions involving weekdays like 'next Saturday' or 'شنبه هفته بعد'."""
        for name, wd in self.weekday_map.items():
            if name in date_string:
                target_wd = wd
                today_wd = self._jalali_weekday(self.today)
                
                if language == "fa":
                    is_next = any(term in date_string for term in ["هفته بعد", "هفته آینده", "هفته ی بعد", "هفته‌ی بعد", "آینده"])
                    is_this = "این" in date_string or "همین" in date_string
                else:
                    is_next = "next" in date_string
                    is_this = "this" in date_string
                
                # Normalize week anchors (Jalali weeks start on Saturday)
                has_next_week = is_next or (language == "fa" and any(term in date_string for term in ["هفته اینده", "هفته اينده", "هفته آینده", "هفته بعد", "هفته‌ی بعد", "هفته‌ بعد"]))
                has_this_week = is_this or (language == "fa" and any(term in date_string for term in ["این هفته", "همین هفته"]))
                
                days_since_last_saturday = (today_wd - 5 + 7) % 7
                current_week_start = self.today - jdatetime.timedelta(days=days_since_last_saturday)
                
                if has_next_week:
                    base = current_week_start + jdatetime.timedelta(days=7)
                elif has_this_week:
                    base = current_week_start
                else:
                    base = current_week_start
                
                offset_from_saturday = (target_wd - 5 + 7) % 7
                candidate = base + jdatetime.timedelta(days=offset_from_saturday)
                
                # If no explicit this/next and candidate already passed, move to following week
                if not (has_next_week or has_this_week) and candidate <= self.today:
                    candidate = candidate + jdatetime.timedelta(days=7)
                
                return candidate.strftime('%Y-%m-%d')
        return None
    
    def _parse_day_month(self, date_string: str) -> Optional[str]:
        """Parse expressions like '20 آذر' or 'بیستم آذر'."""
        for month_name, month_num in self.month_map.items():
            if month_name in date_string:
                num_match = re.search(r'(\d{1,2})', date_string)
                day_val = None
                if num_match:
                    day_val = int(num_match.group(1))
                else:
                    for word, val in self.ordinal_map.items():
                        if word in date_string:
                            day_val = val
                            break
                if day_val:
                    year = self.today.year
                    try:
                        date_obj = jdatetime.date(year, month_num, day_val)
                    except ValueError:
                        return None
                    if date_obj < self.today:
                        try:
                            date_obj = jdatetime.date(year + 1, month_num, day_val)
                        except ValueError:
                            return None
                    return date_obj.strftime('%Y-%m-%d')
        return None
    
    @staticmethod
    def _jalali_weekday(date_obj: jdatetime.date) -> int:
        """Return weekday with Monday=0 ... Sunday=6 to align with datetime weekday."""
        return date_obj.togregorian().weekday()


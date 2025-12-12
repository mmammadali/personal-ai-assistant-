"""
Analytics Agent
Calculates meeting analytics: talk time, participation, word count, etc.
"""
from typing import Dict, Any, List, Optional
import logging
from collections import defaultdict

from meeting.database import MeetingDatabase

logger = logging.getLogger(__name__)


class AnalyticsAgent:
    """Agent for calculating meeting analytics"""
    
    def __init__(self, db: MeetingDatabase):
        """
        Initialize analytics agent
        
        Args:
            db: MeetingDatabase instance
        """
        self.db = db
    
    def calculate_talk_time(self, meeting_id: int) -> Dict[str, Any]:
        """
        Calculate talk time per speaker
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Talk time statistics
        """
        try:
            segments = self.db.get_transcript(meeting_id)
            if not segments:
                return {
                    "success": False,
                    "error": "No transcript found for this meeting"
                }
            
            # Calculate talk time per speaker
            speaker_times = defaultdict(float)
            speaker_segments = defaultdict(int)
            
            for segment in segments:
                speaker_name = segment.get("speaker_name") or "Unknown"
                start_time = segment.get("start_time")
                end_time = segment.get("end_time")
                
                if start_time is not None and end_time is not None:
                    duration = end_time - start_time
                    speaker_times[speaker_name] += duration
                    speaker_segments[speaker_name] += 1
                elif segment.get("text"):
                    # Estimate based on text length (average speaking rate: ~150 words/min)
                    word_count = len(segment.get("text", "").split())
                    estimated_time = (word_count / 150.0) * 60  # Convert to seconds
                    speaker_times[speaker_name] += estimated_time
                    speaker_segments[speaker_name] += 1
            
            # Convert to seconds and format
            total_time = sum(speaker_times.values())
            talk_time_data = []
            
            for speaker_name, time_seconds in speaker_times.items():
                time_int = int(time_seconds)
                percentage = (time_seconds / total_time * 100) if total_time > 0 else 0
                
                talk_time_data.append({
                    "speaker_name": speaker_name,
                    "talk_time_seconds": time_int,
                    "talk_time_minutes": round(time_int / 60, 2),
                    "percentage": round(percentage, 2),
                    "segments_count": speaker_segments[speaker_name]
                })
                
                # Store in database
                word_count = sum(
                    len(seg.get("text", "").split())
                    for seg in segments
                    if (seg.get("speaker_name") or "Unknown") == speaker_name
                )
                
                self.db.add_analytics(
                    meeting_id=meeting_id,
                    speaker_name=speaker_name,
                    talk_time=time_int,
                    word_count=word_count,
                    participation_score=percentage
                )
            
            # Sort by talk time (descending)
            talk_time_data.sort(key=lambda x: x["talk_time_seconds"], reverse=True)
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "total_time_seconds": int(total_time),
                "total_time_minutes": round(total_time / 60, 2),
                "speakers": talk_time_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating talk time: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def calculate_participation_score(self, meeting_id: int) -> Dict[str, Any]:
        """
        Calculate participation scores for each speaker
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Participation scores
        """
        try:
            talk_time_result = self.calculate_talk_time(meeting_id)
            if not talk_time_result.get("success"):
                return talk_time_result
            
            speakers = talk_time_result.get("speakers", [])
            total_time = talk_time_result.get("total_time_seconds", 0)
            
            # Calculate participation scores (normalized 0-100)
            participation_data = []
            for speaker in speakers:
                # Participation score based on talk time percentage
                participation_score = speaker.get("percentage", 0)
                
                # Additional factors could be added:
                # - Number of segments (more segments = more engagement)
                # - Distribution of speaking (even distribution = better)
                
                participation_data.append({
                    "speaker_name": speaker["speaker_name"],
                    "participation_score": round(participation_score, 2),
                    "talk_time_seconds": speaker["talk_time_seconds"],
                    "segments_count": speaker["segments_count"]
                })
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "total_participants": len(participation_data),
                "participation": participation_data
            }
            
        except Exception as e:
            logger.error(f"Error calculating participation score: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_word_count(self, meeting_id: int) -> Dict[str, Any]:
        """
        Get word count statistics
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Word count statistics
        """
        try:
            segments = self.db.get_transcript(meeting_id)
            if not segments:
                return {
                    "success": False,
                    "error": "No transcript found for this meeting"
                }
            
            total_words = 0
            speaker_words = defaultdict(int)
            
            for segment in segments:
                text = segment.get("text", "")
                words = len(text.split())
                total_words += words
                
                speaker_name = segment.get("speaker_name") or "Unknown"
                speaker_words[speaker_name] += words
            
            word_count_data = [
                {
                    "speaker_name": speaker,
                    "word_count": count,
                    "percentage": round((count / total_words * 100) if total_words > 0 else 0, 2)
                }
                for speaker, count in speaker_words.items()
            ]
            
            word_count_data.sort(key=lambda x: x["word_count"], reverse=True)
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "total_words": total_words,
                "speakers": word_count_data
            }
            
        except Exception as e:
            logger.error(f"Error getting word count: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_speaking_frequency(self, meeting_id: int) -> Dict[str, Any]:
        """
        Get speaking frequency (how often each speaker spoke)
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Speaking frequency statistics
        """
        try:
            segments = self.db.get_transcript(meeting_id)
            if not segments:
                return {
                    "success": False,
                    "error": "No transcript found for this meeting"
                }
            
            speaker_frequency = defaultdict(int)
            
            for segment in segments:
                speaker_name = segment.get("speaker_name") or "Unknown"
                speaker_frequency[speaker_name] += 1
            
            frequency_data = [
                {
                    "speaker_name": speaker,
                    "frequency": count,
                    "percentage": round((count / len(segments) * 100) if segments else 0, 2)
                }
                for speaker, count in speaker_frequency.items()
            ]
            
            frequency_data.sort(key=lambda x: x["frequency"], reverse=True)
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "total_segments": len(segments),
                "speakers": frequency_data
            }
            
        except Exception as e:
            logger.error(f"Error getting speaking frequency: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_comprehensive_analytics(self, meeting_id: int) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Complete analytics data
        """
        try:
            talk_time = self.calculate_talk_time(meeting_id)
            participation = self.calculate_participation_score(meeting_id)
            word_count = self.get_word_count(meeting_id)
            frequency = self.get_speaking_frequency(meeting_id)
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "talk_time": talk_time,
                "participation": participation,
                "word_count": word_count,
                "speaking_frequency": frequency
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive analytics: {e}")
            return {
                "success": False,
                "error": str(e)
            }


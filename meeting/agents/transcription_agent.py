"""
Transcription Agent
Handles audio transcription via Soniox service
"""
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from meeting.database import MeetingDatabase
from meeting.services.soniox_service import SonioxService
from meeting.services.audio_processor import AudioProcessor

logger = logging.getLogger(__name__)


class TranscriptionAgent:
    """Agent for handling meeting transcriptions"""
    
    def __init__(self, db: MeetingDatabase):
        """
        Initialize transcription agent
        
        Args:
            db: MeetingDatabase instance
        """
        self.db = db
        self.soniox_service = SonioxService()
        self.audio_processor = AudioProcessor()
    
    def transcribe_meeting(
        self,
        audio_path: str,
        meeting_id: int,
        user_id: str,
        enable_diarization: bool = True,
        enable_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe a meeting audio file
        
        Args:
            audio_path: Path to audio file
            meeting_id: Meeting ID
            user_id: User identifier
            enable_diarization: Enable speaker diarization
            enable_timestamps: Enable word-level timestamps
            
        Returns:
            Transcription result dictionary
        """
        try:
            # Validate audio file
            validation = self.audio_processor.validate_audio_file(audio_path)
            if not validation["valid"]:
                return {
                    "success": False,
                    "error": validation.get("error", "Invalid audio file"),
                    "meeting_id": meeting_id
                }
            
            # Get audio metadata
            metadata = self.audio_processor.get_audio_metadata(audio_path)
            duration = int(metadata.get("duration", 0)) if metadata.get("duration") else None
            
            # Update meeting with duration if available
            if duration:
                self.db.update_meeting(meeting_id, duration=duration)
            
            # Transcribe using Soniox
            transcription_result = self.soniox_service.transcribe_file(
                audio_path,
                language="fa-IR",
                enable_diarization=enable_diarization,
                enable_timestamps=enable_timestamps
            )
            
            if not transcription_result.get("success"):
                return {
                    "success": False,
                    "error": transcription_result.get("error", "Transcription failed"),
                    "meeting_id": meeting_id
                }
            
            # Store transcript segments in database
            segments = transcription_result.get("segments", [])
            transcript_text = transcription_result.get("transcript", "")
            
            # If no segments but we have transcript text, create a single segment
            if not segments and transcript_text:
                segment_id = self.db.add_transcript_segment(
                    meeting_id=meeting_id,
                    text=transcript_text,
                    speaker_id=None,
                    speaker_name=None,
                    start_time=None,
                    end_time=None,
                    confidence=None
                )
                segments = [{"id": segment_id, "text": transcript_text}]
            else:
                # Store each segment
                for segment in segments:
                    self.db.add_transcript_segment(
                        meeting_id=meeting_id,
                        text=segment.get("text", ""),
                        speaker_id=segment.get("speaker_id"),
                        speaker_name=f"Speaker {segment.get('speaker_id')}" if segment.get("speaker_id") else None,
                        start_time=segment.get("start_time"),
                        end_time=segment.get("end_time"),
                        confidence=segment.get("confidence")
                    )
            
            # Save transcript to file
            transcript_path = self._save_transcript_to_file(meeting_id, transcript_text)
            if transcript_path:
                self.db.update_meeting(meeting_id, transcript_path=transcript_path)
            
            # Extract and store participants from speakers
            speakers = transcription_result.get("speakers", [])
            for speaker_id in speakers:
                speaker_name = f"Speaker {speaker_id}"
                # Check if participant already exists
                participants = self.db.get_participants(meeting_id)
                existing = [p for p in participants if p.get("name") == speaker_name]
                if not existing:
                    self.db.add_participant(
                        meeting_id=meeting_id,
                        name=speaker_name,
                        email=None,
                        role=None
                    )
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "transcript": transcript_text,
                "segments_count": len(segments),
                "speakers_count": len(speakers),
                "duration": duration,
                "transcript_path": transcript_path
            }
            
        except Exception as e:
            logger.error(f"Error transcribing meeting: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "meeting_id": meeting_id
            }
    
    def _save_transcript_to_file(self, meeting_id: int, transcript_text: str) -> Optional[str]:
        """
        Save transcript to file
        
        Args:
            meeting_id: Meeting ID
            transcript_text: Transcript text
            
        Returns:
            Path to saved transcript file
        """
        try:
            from config import MEETING_TRANSCRIPTS_FOLDER
            transcripts_folder = Path(MEETING_TRANSCRIPTS_FOLDER)
            transcripts_folder.mkdir(parents=True, exist_ok=True)
            
            transcript_path = transcripts_folder / f"meeting_{meeting_id}_transcript.txt"
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            
            logger.info(f"Saved transcript to: {transcript_path}")
            return str(transcript_path)
            
        except Exception as e:
            logger.error(f"Error saving transcript to file: {e}")
            return None
    
    def get_transcript(self, meeting_id: int) -> Dict[str, Any]:
        """
        Get transcript for a meeting
        
        Args:
            meeting_id: Meeting ID
            
        Returns:
            Transcript data
        """
        try:
            segments = self.db.get_transcript(meeting_id)
            
            if not segments:
                return {
                    "success": False,
                    "error": "No transcript found for this meeting",
                    "meeting_id": meeting_id
                }
            
            # Combine segments into full transcript
            full_text = " ".join([seg.get("text", "") for seg in segments])
            
            return {
                "success": True,
                "meeting_id": meeting_id,
                "transcript": full_text,
                "segments": segments,
                "segments_count": len(segments)
            }
            
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return {
                "success": False,
                "error": str(e),
                "meeting_id": meeting_id
            }


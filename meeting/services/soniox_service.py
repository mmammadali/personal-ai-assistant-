"""
Soniox API Service
Handles transcription via Soniox API for Farsi/Persian
"""
import os
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SonioxService:
    """Service for interacting with Soniox transcription API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Soniox service
        
        Args:
            api_key: Soniox API key (if None, reads from config)
        """
        from config import SONIOX_API_KEY
        
        self.api_key = api_key or SONIOX_API_KEY
        if not self.api_key:
            raise ValueError("Soniox API key is required. Set SONIOX_API_KEY in config or .env file")
        
        # Initialize Soniox client
        try:
            from soniox.speech_service import SpeechClient
            self.client = SpeechClient(api_key=self.api_key)
            logger.info("Soniox client initialized successfully")
        except ImportError:
            logger.error("soniox package not installed. Install with: pip install soniox")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Soniox client: {e}")
            raise
    
    def transcribe_file(
        self,
        audio_path: str,
        language: str = "fa-IR",
        enable_diarization: bool = True,
        enable_timestamps: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe an audio file
        
        Args:
            audio_path: Path to audio file
            language: Language code (default: fa-IR for Farsi)
            enable_diarization: Enable speaker diarization
            enable_timestamps: Enable word-level timestamps
            
        Returns:
            Dictionary with transcription results
        """
        try:
            # Read audio file
            audio_path_obj = Path(audio_path)
            if not audio_path_obj.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            # Prepare transcription request
            # Note: Soniox API structure may vary, adjust based on actual SDK
            try:
                # Try with diarization and timestamps
                if enable_diarization and enable_timestamps:
                    response = self.client.transcribe(
                        audio_data,
                        language=language,
                        diarization=True,
                        timestamps=True
                    )
                elif enable_diarization:
                    response = self.client.transcribe(
                        audio_data,
                        language=language,
                        diarization=True
                    )
                elif enable_timestamps:
                    response = self.client.transcribe(
                        audio_data,
                        language=language,
                        timestamps=True
                    )
                else:
                    response = self.client.transcribe(
                        audio_data,
                        language=language
                    )
                
                # Parse response
                result = {
                    "success": True,
                    "transcript": "",
                    "segments": [],
                    "speakers": [],
                    "language": language
                }
                
                # Extract transcript text
                if hasattr(response, 'transcript'):
                    result["transcript"] = response.transcript
                elif hasattr(response, 'text'):
                    result["transcript"] = response.text
                elif isinstance(response, str):
                    result["transcript"] = response
                else:
                    # Try to get text from results
                    if hasattr(response, 'results') and response.results:
                        result["transcript"] = " ".join([r.text for r in response.results if hasattr(r, 'text')])
                
                # Extract segments with speaker info
                if hasattr(response, 'results') and response.results:
                    for idx, segment in enumerate(response.results):
                        segment_data = {
                            "index": idx,
                            "text": getattr(segment, 'text', ''),
                            "start_time": getattr(segment, 'start_time', None),
                            "end_time": getattr(segment, 'end_time', None),
                            "speaker_id": getattr(segment, 'speaker', None) or getattr(segment, 'speaker_id', None),
                            "confidence": getattr(segment, 'confidence', None)
                        }
                        
                        # Extract word-level timestamps if available
                        if hasattr(segment, 'words') and segment.words:
                            segment_data["words"] = [
                                {
                                    "text": getattr(word, 'text', ''),
                                    "start_time": getattr(word, 'start_time', None),
                                    "end_time": getattr(word, 'end_time', None),
                                    "confidence": getattr(word, 'confidence', None)
                                }
                                for word in segment.words
                            ]
                        
                        result["segments"].append(segment_data)
                
                # Extract unique speakers
                speakers = set()
                for segment in result["segments"]:
                    if segment.get("speaker_id"):
                        speakers.add(segment["speaker_id"])
                result["speakers"] = sorted(list(speakers))
                
                logger.info(f"Transcription completed: {len(result['segments'])} segments, {len(result['speakers'])} speakers")
                return result
                
            except Exception as api_error:
                # Fallback: try simple transcription
                logger.warning(f"Advanced transcription failed, trying simple: {api_error}")
                response = self.client.transcribe(audio_data, language=language)
                
                result = {
                    "success": True,
                    "transcript": response.transcript if hasattr(response, 'transcript') else str(response),
                    "segments": [],
                    "speakers": [],
                    "language": language
                }
                return result
                
        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_path}")
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}",
                "transcript": "",
                "segments": [],
                "speakers": []
            }
        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "transcript": "",
                "segments": [],
                "speakers": []
            }
    
    def transcribe_with_diarization(self, audio_path: str, language: str = "fa-IR") -> Dict[str, Any]:
        """Transcribe with speaker diarization"""
        return self.transcribe_file(audio_path, language, enable_diarization=True, enable_timestamps=True)
    
    def transcribe_with_timestamps(self, audio_path: str, language: str = "fa-IR") -> Dict[str, Any]:
        """Transcribe with word-level timestamps"""
        return self.transcribe_file(audio_path, language, enable_diarization=False, enable_timestamps=True)
    
    def get_transcript_text(self, audio_path: str, language: str = "fa-IR") -> str:
        """
        Get simple transcript text without detailed metadata
        
        Args:
            audio_path: Path to audio file
            language: Language code
            
        Returns:
            Transcript text
        """
        result = self.transcribe_file(audio_path, language, enable_diarization=False, enable_timestamps=False)
        return result.get("transcript", "")


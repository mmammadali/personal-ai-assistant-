"""
Audio Processor Service
Handles audio file validation, conversion, and metadata extraction
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Service for processing audio files"""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma', '.mp4', '.webm'}
    
    def __init__(self, recordings_folder: str = "meeting_recordings"):
        """
        Initialize audio processor
        
        Args:
            recordings_folder: Folder to store recordings
        """
        from config import MEETING_RECORDINGS_FOLDER
        self.recordings_folder = Path(recordings_folder or MEETING_RECORDINGS_FOLDER)
        self.recordings_folder.mkdir(parents=True, exist_ok=True)
    
    def validate_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate audio file format and existence
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": False,
            "error": None,
            "format": None,
            "size": None
        }
        
        try:
            path = Path(file_path)
            
            # Check if file exists
            if not path.exists():
                result["error"] = f"File not found: {file_path}"
                return result
            
            # Check file extension
            ext = path.suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                result["error"] = f"Unsupported format: {ext}. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
                return result
            
            # Check file size
            size = path.stat().st_size
            max_size = 500 * 1024 * 1024  # 500 MB
            if size > max_size:
                result["error"] = f"File too large: {size / (1024*1024):.2f} MB. Maximum: {max_size / (1024*1024)} MB"
                return result
            
            result["valid"] = True
            result["format"] = ext
            result["size"] = size
            return result
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            result["error"] = str(e)
            return result
    
    def get_audio_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract audio metadata (duration, sample rate, etc.)
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "duration": None,
            "sample_rate": None,
            "channels": None,
            "bitrate": None,
            "format": None
        }
        
        try:
            # Try using pydub if available
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(file_path)
                metadata["duration"] = len(audio) / 1000.0  # Convert to seconds
                metadata["sample_rate"] = audio.frame_rate
                metadata["channels"] = audio.channels
                metadata["bitrate"] = audio.frame_width * 8 * audio.frame_rate
                metadata["format"] = Path(file_path).suffix.lower()
            except ImportError:
                logger.warning("pydub not installed, cannot extract detailed metadata")
                # Fallback: just get file info
                path = Path(file_path)
                metadata["format"] = path.suffix.lower()
                metadata["size"] = path.stat().st_size
            except Exception as e:
                logger.warning(f"Could not extract metadata with pydub: {e}")
                # Fallback
                path = Path(file_path)
                metadata["format"] = path.suffix.lower()
                metadata["size"] = path.stat().st_size
                
        except Exception as e:
            logger.error(f"Error getting audio metadata: {e}")
        
        return metadata
    
    def save_uploaded_file(
        self,
        source_path: str,
        user_id: str,
        meeting_title: Optional[str] = None
    ) -> str:
        """
        Save uploaded audio file to recordings folder
        
        Args:
            source_path: Source file path
            user_id: User identifier
            meeting_title: Optional meeting title for filename
            
        Returns:
            Path to saved file
        """
        try:
            source = Path(source_path)
            if not source.exists():
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in (meeting_title or "meeting") if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
            safe_title = safe_title.replace(' ', '_')
            
            filename = f"{user_id}_{safe_title}_{timestamp}{source.suffix}"
            dest_path = self.recordings_folder / filename
            
            # Copy file
            import shutil
            shutil.copy2(source, dest_path)
            
            logger.info(f"Saved audio file: {dest_path}")
            return str(dest_path)
            
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            raise
    
    def convert_audio_format(
        self,
        input_path: str,
        output_format: str = "wav",
        output_path: Optional[str] = None
    ) -> str:
        """
        Convert audio to different format (requires pydub)
        
        Args:
            input_path: Input audio file path
            output_format: Target format (wav, mp3, etc.)
            output_path: Optional output path
            
        Returns:
            Path to converted file
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(input_path)
            
            if not output_path:
                input_path_obj = Path(input_path)
                output_path = str(input_path_obj.with_suffix(f".{output_format}"))
            
            # Export to new format
            audio.export(output_path, format=output_format)
            
            logger.info(f"Converted audio: {input_path} -> {output_path}")
            return output_path
            
        except ImportError:
            raise ImportError("pydub is required for audio conversion. Install with: pip install pydub")
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            raise


"""
Validation utilities for file uploads and data.
Custom validators for video files, metadata, and requests.
"""
from pathlib import Path
from typing import Tuple, Optional

from config import settings


class VideoValidator:
    """Validates video and audio files for processing."""
    
    @staticmethod
    def validate_file_extension(filename: str) -> Tuple[bool, str, str]:
        """
        Validate file extension.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, file_type, message)
        """
        ext = Path(filename).suffix.lower().lstrip(".")
        
        if not ext:
            return False, "unknown", "File has no extension"
        
        if ext in settings.allowed_video_formats_list:
            return True, "video", f"Valid video format: {ext}"
        elif ext in settings.allowed_audio_formats_list:
            return True, "audio", f"Valid audio format: {ext}"
        else:
            allowed = ", ".join(
                settings.allowed_video_formats_list + settings.allowed_audio_formats_list
            )
            return False, "unknown", f"Invalid format '{ext}'. Allowed: {allowed}"
    
    @staticmethod
    def validate_file_size(file_size: int) -> Tuple[bool, str]:
        """
        Validate file size.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            Tuple of (is_valid, message)
        """
        max_size = settings.max_upload_size_bytes
        max_size_mb = settings.max_upload_size_mb
        
        if file_size <= 0:
            return False, "File is empty"
        
        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB). Maximum: {max_size_mb}MB"
        
        return True, f"Valid file size: {file_size / (1024 * 1024):.2f}MB"
    
    @staticmethod
    def validate_duration(duration_seconds: float, max_duration: int = 7200) -> Tuple[bool, str]:
        """
        Validate video/audio duration.
        
        Args:
            duration_seconds: Duration in seconds
            max_duration: Maximum allowed duration in seconds (default: 2 hours)
            
        Returns:
            Tuple of (is_valid, message)
        """
        if duration_seconds <= 0:
            return False, "Invalid duration: must be greater than 0"
        
        if duration_seconds > max_duration:
            max_hours = max_duration / 3600
            duration_hours = duration_seconds / 3600
            return False, f"Duration too long ({duration_hours:.2f}h). Maximum: {max_hours:.2f}h"
        
        duration_minutes = duration_seconds / 60
        return True, f"Valid duration: {duration_minutes:.2f} minutes"
    
    @staticmethod
    def validate_upload(
        filename: str,
        file_size: int,
        duration_seconds: Optional[float] = None,
    ) -> Tuple[bool, list[str]]:
        """
        Comprehensive upload validation.
        
        Args:
            filename: Filename to validate
            file_size: File size in bytes
            duration_seconds: Optional duration in seconds
            
        Returns:
            Tuple of (is_valid, list of messages)
        """
        messages = []
        is_valid = True
        
        # Validate extension
        ext_valid, file_type, ext_msg = VideoValidator.validate_file_extension(filename)
        messages.append(ext_msg)
        if not ext_valid:
            is_valid = False
        
        # Validate size
        size_valid, size_msg = VideoValidator.validate_file_size(file_size)
        messages.append(size_msg)
        if not size_valid:
            is_valid = False
        
        # Validate duration if provided
        if duration_seconds is not None:
            duration_valid, duration_msg = VideoValidator.validate_duration(duration_seconds)
            messages.append(duration_msg)
            if not duration_valid:
                is_valid = False
        
        return is_valid, messages
    
    @staticmethod
    def estimate_processing_time(duration_seconds: float, file_type: str = "video") -> int:
        """
        Estimate processing time for a file.
        
        Args:
            duration_seconds: File duration in seconds
            file_type: Type of file ('video' or 'audio')
            
        Returns:
            Estimated processing time in seconds
        """
        # Rough estimates:
        # - Audio extraction: 0.1x duration
        # - Transcription: 0.5x duration
        # - Summarization: 30-60 seconds
        # Total: ~0.6x duration + 60 seconds
        
        if file_type == "video":
            # Need to extract audio first
            extraction_time = duration_seconds * 0.1
            transcription_time = duration_seconds * 0.5
            summarization_time = 60
            total = extraction_time + transcription_time + summarization_time
        else:
            # Audio file, skip extraction
            transcription_time = duration_seconds * 0.5
            summarization_time = 60
            total = transcription_time + summarization_time
        
        # Add 20% buffer
        return int(total * 1.2)
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to remove potentially dangerous characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove path separators and other dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        max_length = 255
        if len(sanitized) > max_length:
            ext = Path(sanitized).suffix
            name = Path(sanitized).stem
            sanitized = name[:max_length - len(ext)] + ext
        
        return sanitized


class MetadataValidator:
    """Validates meeting metadata."""
    
    @staticmethod
    def validate_participants(participants: list[str]) -> Tuple[bool, str]:
        """
        Validate participants list.
        
        Args:
            participants: List of participant names
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not participants:
            return False, "At least one participant is required"
        
        if len(participants) > 50:
            return False, "Too many participants (maximum: 50)"
        
        # Check for empty names
        empty_names = [p for p in participants if not p.strip()]
        if empty_names:
            return False, "Participant names cannot be empty"
        
        return True, f"Valid participants list: {len(participants)} participants"
    
    @staticmethod
    def validate_case_id(case_id: Optional[str]) -> Tuple[bool, str]:
        """
        Validate case ID format.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Tuple of (is_valid, message)
        """
        if case_id is None:
            return True, "No case ID provided (optional)"
        
        if not case_id.strip():
            return False, "Case ID cannot be empty if provided"
        
        if len(case_id) > 100:
            return False, "Case ID too long (maximum: 100 characters)"
        
        return True, f"Valid case ID: {case_id}"

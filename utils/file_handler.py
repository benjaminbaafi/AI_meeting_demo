"""
File handling utilities for video and audio files.
Handles upload, storage, validation, and cleanup.
"""
import os
import uuid
import aiofiles
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import logging

from config import settings


logger = logging.getLogger(__name__)


class FileHandler:
    """Handles file operations for uploaded videos and audio files."""
    
    def __init__(self):
        """Initialize file handler with configured directories."""
        self.upload_dir = settings.upload_dir
        self.temp_dir = settings.temp_dir
        self.output_dir = settings.output_dir
        
        # Ensure directories exist
        for directory in [self.upload_dir, self.temp_dir, self.output_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        logger.info("FileHandler initialized")
    
    async def save_uploaded_file(
        self,
        file_content: bytes,
        original_filename: str,
        job_id: Optional[str] = None,
    ) -> Tuple[str, Path]:
        """
        Save uploaded file to disk.
        
        Args:
            file_content: File content as bytes
            original_filename: Original filename
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            Tuple of (job_id, file_path)
        """
        try:
            # Generate job ID if not provided
            if not job_id:
                job_id = self.generate_job_id()
            
            # Get file extension
            file_ext = Path(original_filename).suffix.lower()
            
            # Create filename with job_id
            filename = f"{job_id}{file_ext}"
            file_path = self.upload_dir / filename
            
            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(file_content)
            
            logger.info(f"File saved: {file_path} ({len(file_content)} bytes)")
            return job_id, file_path
            
        except Exception as e:
            logger.error(f"Failed to save file: {str(e)}")
            raise
    
    def generate_job_id(self) -> str:
        """
        Generate a unique job ID.
        
        Returns:
            Unique job identifier
        """
        return f"job_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}"
    
    def get_file_path(self, job_id: str, extension: str) -> Path:
        """
        Get file path for a job ID.
        
        Args:
            job_id: Job identifier
            extension: File extension (with or without dot)
            
        Returns:
            Path to file
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        
        return self.upload_dir / f"{job_id}{extension}"
    
    def get_temp_path(self, job_id: str, suffix: str = "") -> Path:
        """
        Get temporary file path for a job.
        
        Args:
            job_id: Job identifier
            suffix: Optional suffix for temp file
            
        Returns:
            Path to temporary file
        """
        return self.temp_dir / f"{job_id}{suffix}"
    
    def get_output_path(self, job_id: str, output_type: str, extension: str) -> Path:
        """
        Get output file path for a job.
        
        Args:
            job_id: Job identifier
            output_type: Type of output (e.g., 'transcript', 'summary')
            extension: File extension
            
        Returns:
            Path to output file
        """
        if not extension.startswith("."):
            extension = f".{extension}"
        
        return self.output_dir / f"{job_id}_{output_type}{extension}"
    
    async def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA256 hash of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    def get_file_size(self, file_path: Path) -> int:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in bytes
        """
        return file_path.stat().st_size
    
    def validate_file_size(self, file_size: int) -> bool:
        """
        Validate file size against maximum allowed.
        
        Args:
            file_size: File size in bytes
            
        Returns:
            True if valid, False otherwise
        """
        max_size = settings.max_upload_size_bytes
        return file_size <= max_size
    
    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate file extension.
        
        Args:
            filename: Filename to validate
            
        Returns:
            Tuple of (is_valid, file_type) where file_type is 'video' or 'audio'
        """
        ext = Path(filename).suffix.lower().lstrip(".")
        
        if ext in settings.allowed_video_formats_list:
            return True, "video"
        elif ext in settings.allowed_audio_formats_list:
            return True, "audio"
        else:
            return False, "unknown"
    
    async def cleanup_temp_files(self, job_id: str):
        """
        Clean up temporary files for a job.
        
        Args:
            job_id: Job identifier
        """
        try:
            # Find all temp files for this job
            temp_files = list(self.temp_dir.glob(f"{job_id}*"))
            
            for temp_file in temp_files:
                temp_file.unlink()
                logger.info(f"Deleted temp file: {temp_file}")
            
        except Exception as e:
            logger.warning(f"Failed to cleanup temp files for {job_id}: {str(e)}")
    
    async def delete_job_files(self, job_id: str):
        """
        Delete all files associated with a job.
        
        Args:
            job_id: Job identifier
        """
        try:
            # Delete from all directories
            for directory in [self.upload_dir, self.temp_dir, self.output_dir]:
                job_files = list(directory.glob(f"{job_id}*"))
                for job_file in job_files:
                    job_file.unlink()
                    logger.info(f"Deleted file: {job_file}")
            
        except Exception as e:
            logger.error(f"Failed to delete files for {job_id}: {str(e)}")
            raise
    
    def get_file_info(self, file_path: Path) -> dict:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        stat = file_path.stat()
        
        return {
            "filename": file_path.name,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(stat.st_ctime),
            "modified_at": datetime.fromtimestamp(stat.st_mtime),
            "extension": file_path.suffix.lower(),
        }


# Global file handler instance
_file_handler: Optional[FileHandler] = None


def get_file_handler() -> FileHandler:
    """
    Get or create the global file handler instance.
    
    Returns:
        FileHandler instance
    """
    global _file_handler
    if _file_handler is None:
        _file_handler = FileHandler()
    return _file_handler

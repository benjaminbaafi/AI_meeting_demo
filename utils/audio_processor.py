"""
Audio processing utilities.
Handles audio extraction from video, format conversion, and quality enhancement.
"""
import subprocess
import shutil
import os
import ffmpeg
from pathlib import Path
from typing import Optional, Tuple
import logging

from config import settings


logger = logging.getLogger(__name__)


class AudioProcessor:
    """Processes audio files for transcription."""
    
    @staticmethod
    async def extract_audio_from_video(
        video_path: Path,
        output_path: Optional[Path] = None,
        sample_rate: int = 16000,
    ) -> Tuple[Path, float]:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to video file
            output_path: Optional output path (generated if not provided)
            sample_rate: Audio sample rate (Hz)
            
        Returns:
            Tuple of (audio_path, duration_seconds)
            
        Raises:
            Exception: If extraction fails
        """
        try:
            if not output_path:
                output_path = video_path.with_suffix(".mp3")
            
            logger.info(f"Extracting audio from: {video_path}")
            
            # Get video duration
            probe = ffmpeg.probe(str(video_path))
            duration = float(probe['format']['duration'])
            
            # Extract audio
            stream = ffmpeg.input(str(video_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='libmp3lame',  # MP3
                ac=1,  # Mono
                ar=sample_rate,  # Sample rate
                audio_bitrate='64k',  # 64kbps
                loglevel='error',
            )
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"Audio extracted: {output_path} ({duration:.2f}s)")
            return output_path, duration
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode() if e.stderr else str(e)}")
            raise Exception(f"Failed to extract audio: {str(e)}")
        except Exception as e:
            logger.error(f"Audio extraction failed: {str(e)}")
            raise
    
    @staticmethod
    async def convert_audio_format(
        input_path: Path,
        output_path: Path,
        target_format: str = "wav",
        sample_rate: int = 16000,
    ) -> Path:
        """
        Convert audio to target format.
        
        Args:
            input_path: Input audio file
            output_path: Output audio file
            target_format: Target format (wav, mp3, etc.)
            sample_rate: Sample rate (Hz)
            
        Returns:
            Path to converted file
            
        Raises:
            Exception: If conversion fails
        """
        try:
            logger.info(f"Converting {input_path} to {target_format}")
            
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec='pcm_s16le' if target_format == 'wav' else 'libmp3lame',
                ac=1,  # Mono
                ar=sample_rate,
                loglevel='error',
            )
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"Audio converted: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Audio conversion failed: {str(e)}")
            raise
    
    @staticmethod
    async def get_audio_duration(audio_path: Path) -> float:
        """
        Get audio file duration.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            probe = ffmpeg.probe(str(audio_path))
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.error(f"Failed to get audio duration: {str(e)}")
            raise
    
    @staticmethod
    async def normalize_audio(
        input_path: Path,
        output_path: Path,
        target_level: float = -20.0,
    ) -> Path:
        """
        Normalize audio levels.
        
        Args:
            input_path: Input audio file
            output_path: Output audio file
            target_level: Target loudness level (dB)
            
        Returns:
            Path to normalized file
        """
        try:
            logger.info(f"Normalizing audio: {input_path}")
            
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.filter(stream, 'loudnorm', I=target_level)
            stream = ffmpeg.output(stream, str(output_path), loglevel='error')
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"Audio normalized: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Audio normalization failed: {str(e)}")
            raise
    
    @staticmethod
    async def reduce_noise(
        input_path: Path,
        output_path: Path,
    ) -> Path:
        """
        Apply noise reduction to audio.
        
        Args:
            input_path: Input audio file
            output_path: Output audio file
            
        Returns:
            Path to processed file
        """
        try:
            logger.info(f"Reducing noise: {input_path}")
            
            # Apply highpass and lowpass filters to reduce noise
            stream = ffmpeg.input(str(input_path))
            stream = ffmpeg.filter(stream, 'highpass', f=200)  # Remove low frequency noise
            stream = ffmpeg.filter(stream, 'lowpass', f=3000)  # Remove high frequency noise
            stream = ffmpeg.output(stream, str(output_path), loglevel='error')
            ffmpeg.run(stream, overwrite_output=True)
            
            logger.info(f"Noise reduced: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Noise reduction failed: {str(e)}")
            raise
    
    @staticmethod
    async def split_audio_chunks(
        audio_path: Path,
        chunk_duration_seconds: int = 900,  # 15 minutes
    ) -> list[Path]:
        """
        Split audio into chunks using smart silence detection.
        Cuts at silence points to avoid splitting words.
        
        Args:
            audio_path: Path to audio file
            chunk_duration_seconds: Target duration of each chunk (default: 15 minutes)
            
        Returns:
            List of chunk file paths
        """
        try:
            from pydub import AudioSegment
            
            logger.info(f"Smart chunking audio: {audio_path}")
            
            # Load audio
            audio = AudioSegment.from_file(str(audio_path))
            
            # Constants (in milliseconds)
            MIN_CHUNK_MS = int(chunk_duration_seconds * 0.67 * 1000)  # ~10 mins for 15 min target
            MAX_CHUNK_MS = int(chunk_duration_seconds * 1000)  # 15 mins
            SILENCE_THRESHOLD_DB = -40  # dBFS threshold for silence
            SILENCE_SEARCH_STEP_MS = 1000  # Search backwards in 1-second steps
            
            chunks = []
            start_time = 0
            total_duration = len(audio)
            chunk_count = 0
            
            while start_time < total_duration:
                # Define the window where we want to cut (between MIN and MAX from start)
                end_window_start = start_time + MIN_CHUNK_MS
                end_window_end = min(start_time + MAX_CHUNK_MS, total_duration)
                
                # If remaining audio is less than MAX, just take the rest
                if total_duration - start_time < MAX_CHUNK_MS:
                    end_time = total_duration
                else:
                    # Search backwards from MAX limit for silence
                    found_cut = False
                    search_point = end_window_end
                    
                    while search_point > end_window_start:
                        # Check a 1-second slice for silence
                        slice_start = max(0, search_point - SILENCE_SEARCH_STEP_MS)
                        slice_audio = audio[slice_start:search_point]
                        
                        # Check if this slice is silent
                        if slice_audio.dBFS < SILENCE_THRESHOLD_DB:
                            end_time = search_point
                            found_cut = True
                            logger.info(f"Found silence at {search_point/1000:.1f}s for chunk {chunk_count}")
                            break
                        
                        search_point -= SILENCE_SEARCH_STEP_MS
                    
                    # If no silence found, force cut at MAX (hard cut fallback)
                    if not found_cut:
                        logger.warning(f"No silence found for chunk {chunk_count}, using hard cut")
                        end_time = end_window_end
                
                # Create the chunk
                chunk = audio[start_time:end_time]
                chunk_path = audio_path.parent / f"{audio_path.stem}_chunk_{chunk_count}{audio_path.suffix}"
                
                # Export with same format and bitrate
                export_format = audio_path.suffix[1:]  # Remove the dot
                chunk.export(
                    str(chunk_path),
                    format=export_format,
                    bitrate="64k" if export_format == "mp3" else None,
                )
                
                chunks.append(chunk_path)
                logger.info(
                    f"Created chunk {chunk_count}: {start_time/1000/60:.2f}m to {end_time/1000/60:.2f}m"
                )
                
                # Update loop
                start_time = end_time
                chunk_count += 1
            
            logger.info(f"Smart chunking complete: {len(chunks)} chunks created")
            return chunks
            
        except Exception as e:
            logger.error(f"Smart audio chunking failed: {str(e)}")
            raise
    
    @staticmethod
    def find_ffmpeg_path() -> Optional[str]:
        """
        Find FFmpeg executable path.
        
        Checks:
        1. Config setting (ffmpeg_path)
        2. PATH environment variable
        3. Common Windows installation locations
        
        Returns:
            Path to ffmpeg executable or None if not found
        """
        # Check config setting first
        if settings.ffmpeg_path:
            if Path(settings.ffmpeg_path).exists():
                return str(settings.ffmpeg_path)
            logger.warning("Configured ffmpeg_path does not exist: %s", settings.ffmpeg_path)
        
        # Check PATH using shutil.which (more reliable)
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return ffmpeg_path
        
        # Check common Windows locations
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
            os.path.expanduser(r"~\ffmpeg\bin\ffmpeg.exe"),
        ]
        
        for path in common_paths:
            if Path(path).exists():
                logger.info("Found FFmpeg at: %s", path)
                return path
        
        return None
    
    @staticmethod
    def check_ffmpeg_installed() -> bool:
        """
        Check if FFmpeg is installed and available.
        
        Returns:
            True if FFmpeg is available, False otherwise
        """
        ffmpeg_path = AudioProcessor.find_ffmpeg_path()
        if not ffmpeg_path:
            return False
        
        try:
            # Test if ffmpeg works
            result = subprocess.run(
                [ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=5,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False


# Verify FFmpeg is installed on module import
_ffmpeg_path = AudioProcessor.find_ffmpeg_path()
if not _ffmpeg_path or not AudioProcessor.check_ffmpeg_installed():
    logger.warning(
        "FFmpeg not found! Audio processing will fail. "
        "Please install FFmpeg: https://ffmpeg.org/download.html\n"
        "If FFmpeg is installed but not detected, try:\n"
        "1. Restart your IDE/terminal\n"
        "2. Add FFMPEG_PATH to your .env file pointing to ffmpeg.exe\n"
        "3. Verify FFmpeg is in your system PATH"
    )
else:
    logger.info("FFmpeg found at: %s", _ffmpeg_path)

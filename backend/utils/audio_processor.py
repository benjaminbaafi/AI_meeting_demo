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
        Split audio into chunks using ROBUST iterative silence detection.
        
        PRODUCTION-READY ALGORITHM:
        1. Tries to find silence at multiple threshold levels (-50dB to -25dB)
        2. Uses 5-second safety overlap for hard cuts to prevent word loss
        3. Optimized for Azure OpenAI Whisper 25MB limit
        
        Args:
            audio_path: Path to audio file
            chunk_duration_seconds: Target max duration (default: 15 minutes)
            
        Returns:
            List of chunk file paths
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import detect_silence
            
            logger.info(f"🎵 Starting ROBUST chunking: {audio_path}")
            
            # Load audio
            audio = AudioSegment.from_file(str(audio_path))
            total_len = len(audio)
            
            # Constants (in milliseconds)
            MIN_MS = int(chunk_duration_seconds * 0.67 * 1000)  # 10 minutes
            MAX_MS = int(chunk_duration_seconds * 1000)  # 15 minutes
            OVERLAP_MS = 5 * 1000  # 5-second safety overlap for hard cuts
            MIN_SILENCE_LEN = 500  # Minimum silence duration to detect (500ms)
            
            # Iterative silence thresholds (quiet room → noisy room → breaths/pauses)
            SILENCE_THRESHOLDS = [-50, -40, -35, -30, -25]
            
            chunks_paths = []
            start_time = 0
            chunk_count = 0
            
            while start_time < total_len:
                end_window_start = start_time + MIN_MS
                end_window_end = min(start_time + MAX_MS, total_len)
                
                # If we're near the end, just finish
                if total_len - start_time <= MAX_MS:
                    end_time = total_len
                    next_start_time = total_len  # No next chunk
                    logger.info(f"  📌 Chunk {chunk_count}: Final chunk (remaining audio)")
                else:
                    # EXTRACT THE SEARCH WINDOW (10-15 min danger zone)
                    search_audio = audio[end_window_start:end_window_end]
                    
                    # --- STRATEGY 1: ITERATIVE SILENCE SEARCH ---
                    found_silence = False
                    cut_point_relative = 0
                    used_threshold = None
                    
                    # Try thresholds from strict (-50dB) to lenient (-25dB)
                    for threshold in SILENCE_THRESHOLDS:
                        silence_ranges = detect_silence(
                            search_audio,
                            min_silence_len=MIN_SILENCE_LEN,
                            silence_thresh=threshold
                        )
                        
                        if silence_ranges:
                            # Pick the LAST silence in the window to maximize chunk size
                            last_silence = silence_ranges[-1]
                            # Cut in the MIDDLE of that silence
                            cut_point_relative = (last_silence[0] + last_silence[1]) / 2
                            used_threshold = threshold
                            found_silence = True
                            logger.info(
                                f"  ✂️  Chunk {chunk_count}: Found silence at {threshold}dB "
                                f"(cut at {(end_window_start + cut_point_relative)/60000:.2f}m)"
                            )
                            break
                    
                    if found_silence:
                        # Clean cut at silence - no overlap needed
                        end_time = int(end_window_start + cut_point_relative)
                        next_start_time = end_time
                    else:
                        # --- STRATEGY 2: HARD CUT WITH SAFETY OVERLAP ---
                        logger.warning(
                            f"  ⚠️  Chunk {chunk_count}: No silence found (even at -25dB). "
                            f"Using HARD CUT with 5-second overlap."
                        )
                        end_time = end_window_end
                        # CRITICAL: Backtrack next chunk by 5 seconds to ensure no word loss
                        next_start_time = end_time - OVERLAP_MS
                
                # Export chunk
                chunk_name = f"{audio_path.stem}_chunk_{chunk_count}{audio_path.suffix}"
                chunk_path = audio_path.parent / chunk_name
                
                logger.info(
                    f"  💾 Exporting {chunk_name} "
                    f"({start_time/60000:.1f}m - {end_time/60000:.1f}m)"
                )
                
                # Extract and export chunk
                chunk = audio[start_time:end_time]
                export_format = audio_path.suffix[1:]  # Remove the dot
                
                chunk.export(
                    str(chunk_path),
                    format=export_format,
                    bitrate="64k" if export_format == "mp3" else None,
                    parameters=["-ac", "1", "-ar", "16000"]  # Mono, 16kHz
                )
                
                chunks_paths.append(chunk_path)
                
                # Move forward (with overlap if hard cut was used)
                start_time = int(next_start_time)
                chunk_count += 1
            
            logger.info(f"✅ Robust chunking complete: {len(chunks_paths)} chunks created")
            return chunks_paths
            
        except Exception as e:
            logger.error(f"❌ Robust audio chunking failed: {str(e)}")
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

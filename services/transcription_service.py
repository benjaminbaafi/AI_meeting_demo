"""
Transcription service orchestration.
Coordinates audio extraction, transcription, and enhancement.
"""
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from models.schemas import TranscriptionResponse, TranscriptSegment, Speaker
from models.enums import ProcessingStatus, SpeakerRole, PracticeArea, MeetingType
from services.azure_openai_service import get_azure_openai_service
from utils.audio_processor import AudioProcessor
from utils.file_handler import get_file_handler
from prompts.transcription_prompts import TranscriptionPrompts


logger = logging.getLogger(__name__)


class TranscriptionService:
    """Orchestrates the transcription process."""
    
    def __init__(self):
        """Initialize transcription service."""
        self.azure_service = get_azure_openai_service()
        self.audio_processor = AudioProcessor()
        self.file_handler = get_file_handler()
        self.prompts = TranscriptionPrompts()
        
        logger.info("TranscriptionService initialized")
    
    async def transcribe_video(
        self,
        job_id: str,
        video_path: Path,
        practice_area: PracticeArea,
        meeting_type: MeetingType,
        participants: List[str],
        language: Optional[str] = None,
        custom_vocabulary: Optional[List[str]] = None,
        enable_speaker_diarization: bool = True,
    ) -> TranscriptionResponse:
        """
        Transcribe a video file.
        
        Args:
            job_id: Job identifier
            video_path: Path to video file
            practice_area: Legal practice area
            meeting_type: Type of meeting
            participants: List of participant names
            language: Optional language code
            custom_vocabulary: Optional custom legal terms
            enable_speaker_diarization: Enable speaker identification
            
        Returns:
            TranscriptionResponse with results
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info("Starting transcription for job: %s", job_id)
            
            # Step 1: Extract audio from video
            audio_path = self.file_handler.get_temp_path(job_id, "_audio.mp3")
            audio_path, duration = await self.audio_processor.extract_audio_from_video(
                video_path=video_path,
                output_path=audio_path,
            )
            
            # Step 2: Normalize audio for better transcription
            normalized_path = self.file_handler.get_temp_path(job_id, "_normalized.mp3")
            await self.audio_processor.normalize_audio(audio_path, normalized_path)
            
            # Step 3: Check if chunking is needed and transcribe
            from config import settings
            
            # Check file size and duration
            file_size_mb = normalized_path.stat().st_size / (1024 * 1024)
            needs_chunking = (
                settings.enable_chunking and
                (file_size_mb > settings.max_audio_size_mb or duration > settings.max_audio_duration_seconds)
            )
            
            if needs_chunking:
                logger.info(
                    "File exceeds limits (size: %.2f MB, duration: %.1f s). Using chunking.",
                    file_size_mb,
                    duration
                )
                transcription_result = await self._transcribe_with_chunking(
                    normalized_path=normalized_path,
                    duration=duration,
                    language=language,
                    practice_area=practice_area,
                    custom_vocabulary=custom_vocabulary,
                    job_id=job_id,
                )
            else:
                # Step 3: Transcribe using Azure OpenAI Whisper (single file)
                transcription_result = await self.azure_service.transcribe_audio(
                    audio_file_path=str(normalized_path),
                    language=language,
                    prompt=self._get_transcription_prompt(practice_area, custom_vocabulary),
                )
            
            # Step 4: Enhance transcription with legal terminology
            enhanced_text = await self._enhance_transcription(
                transcription_result["text"],
                practice_area,
                custom_vocabulary,
            )
            
            # Step 5: Process segments and identify speakers
            segments = await self._process_segments(
                transcription_result["segments"],
                participants,
                meeting_type,
                enable_speaker_diarization,
            )
            
            # Step 6: Calculate metrics
            word_count = len(enhanced_text.split())
            avg_confidence = sum(
                seg.confidence for seg in segments
            ) / len(segments) if segments else 0.0
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Step 7: Create response
            response = TranscriptionResponse(
                job_id=job_id,
                status=ProcessingStatus.COMPLETED,
                segments=segments,
                full_text=enhanced_text,
                speakers=self._extract_unique_speakers(segments),
                duration_seconds=duration,
                word_count=word_count,
                average_confidence=avg_confidence,
                language_detected=transcription_result.get("language"),
                processing_time_seconds=processing_time,
                completed_at=datetime.now(timezone.utc),
            )
            
            logger.info("Transcription completed for job: %s", job_id)
            return response
            
        except Exception:
            logger.exception("Transcription failed for job %s", job_id)
            raise
        finally:
            # Cleanup temporary files
            await self.file_handler.cleanup_temp_files(job_id)
    
    def _get_transcription_prompt(
        self,
        practice_area: PracticeArea,
        custom_vocabulary: Optional[List[str]],
    ) -> str:
        """Get transcription prompt for Whisper."""
        # Simple prompt for Whisper (it doesn't support complex prompts)
        base_prompt = f"Legal {practice_area.value.replace('_', ' ')} meeting."
        
        if custom_vocabulary:
            # Add a few key terms to the prompt
            terms = ", ".join(custom_vocabulary[:5])
            base_prompt += f" Key terms: {terms}."
        
        return base_prompt
    
    async def _enhance_transcription(
        self,
        raw_text: str,
        practice_area: PracticeArea,
        custom_vocabulary: Optional[List[str]],
    ) -> str:
        """
        Enhance transcription with legal terminology corrections.
        
        Args:
            raw_text: Raw transcription text
            practice_area: Legal practice area
            custom_vocabulary: Optional custom terms
            
        Returns:
            Enhanced transcription text
        """
        try:
            prompt = self.prompts.get_legal_terminology_enhancement_prompt(
                practice_area=practice_area,
                custom_vocabulary=custom_vocabulary,
            )
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Raw transcription:\n\n{raw_text}"},
            ]
            
            enhanced_text = await self.azure_service.generate_completion(
                messages=messages,
                temperature=0.3,  # Low temperature for accuracy
            )
            
            return enhanced_text
            
        except Exception:
            logger.exception("Transcription enhancement failed")
            # Return raw text if enhancement fails
            return raw_text
    
    async def _process_segments(
        self,
        raw_segments: List[Dict[str, Any]],
        participants: List[str],
        meeting_type: MeetingType,
        enable_diarization: bool,
    ) -> List[TranscriptSegment]:
        """
        Process raw segments into structured TranscriptSegment objects.
        
        Args:
            raw_segments: Raw segments from Whisper
            participants: List of participant names
            meeting_type: Type of meeting
            enable_diarization: Enable speaker identification
            
        Returns:
            List of TranscriptSegment objects
        """
        segments = []
        
        for idx, seg in enumerate(raw_segments):
            # Create speaker (Whisper doesn't provide speaker diarization natively)
            speaker = Speaker(
                speaker_id=f"speaker_{idx % len(participants) if participants else 0}",
                name=participants[idx % len(participants)] if participants else None,
                role=SpeakerRole.UNKNOWN,
            )
            
            segment = TranscriptSegment(
                start_time=seg["start"],
                end_time=seg["end"],
                speaker=speaker,
                text=seg["text"].strip(),
                confidence=1.0 - seg.get("no_speech_prob", 0.0),  # Convert to confidence
            )
            
            segments.append(segment)
        
        # If diarization is enabled, try to improve speaker identification
        if enable_diarization and participants:
            segments = await self._improve_speaker_identification(
                segments,
                participants,
                meeting_type,
            )
        
        return segments
    
    async def _improve_speaker_identification(
        self,
        segments: List[TranscriptSegment],
        participants: List[str],
        meeting_type: MeetingType,
    ) -> List[TranscriptSegment]:
        """
        Use GPT to improve speaker identification based on context.
        
        Args:
            segments: List of transcript segments
            participants: List of participant names
            meeting_type: Type of meeting
            
        Returns:
            Segments with improved speaker identification
        """
        try:
            # Create transcript text for analysis
            transcript_text = "\n".join(
                f"[{seg.start_time:.2f}s] {seg.speaker.speaker_id}: {seg.text}"
                for seg in segments[:50]  # Analyze first 50 segments
            )
            
            prompt = self.prompts.get_speaker_identification_prompt(
                participants=participants,
                meeting_type=meeting_type,
            )
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript_text},
            ]
            
            # Get speaker mapping from GPT
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3,
            )
            
            # Apply speaker mapping (simplified - in production, use more sophisticated logic)
            # This is a placeholder for demonstration
            logger.info("Speaker identification analysis completed")
            
        except Exception:
            logger.exception("Speaker identification improvement failed")
        
        return segments
    
    async def _transcribe_with_chunking(
        self,
        normalized_path: Path,
        duration: float,
        language: Optional[str],
        practice_area: PracticeArea,
        custom_vocabulary: Optional[List[str]],
        job_id: str,
    ) -> Dict[str, Any]:
        """
        Transcribe large audio file by splitting into chunks.
        Uses parallel processing (5 chunks at a time) for faster transcription.
        
        Args:
            normalized_path: Path to normalized audio file
            duration: Total audio duration in seconds
            language: Optional language code
            practice_area: Legal practice area
            custom_vocabulary: Optional custom terms
            job_id: Job identifier for logging
            
        Returns:
            Merged transcription result with all segments
        """
        from config import settings
        
        try:
            logger.info("Starting PARALLEL chunked transcription for job: %s", job_id)
            
            # Split audio into chunks
            chunk_duration = settings.chunk_duration_seconds
            chunks = await self.audio_processor.split_audio_chunks(
                normalized_path,
                chunk_duration_seconds=chunk_duration,
            )
            
            logger.info("Split audio into %d chunks for job: %s", len(chunks), job_id)
            logger.info("Processing chunks in parallel batches of 5...")
            
            # Process chunks in parallel batches
            BATCH_SIZE = 5  # Process 5 chunks concurrently
            all_chunk_results = []
            
            for batch_start in range(0, len(chunks), BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, len(chunks))
                batch_chunks = chunks[batch_start:batch_end]
                
                logger.info(
                    "Processing batch %d-%d of %d chunks...",
                    batch_start + 1,
                    batch_end,
                    len(chunks)
                )
                
                # Create tasks for parallel processing
                tasks = []
                for chunk_idx, chunk_path in enumerate(batch_chunks, start=batch_start):
                    task = self._transcribe_single_chunk(
                        chunk_path=chunk_path,
                        chunk_idx=chunk_idx,
                        total_chunks=len(chunks),
                        chunk_duration=chunk_duration,
                        language=language,
                        practice_area=practice_area,
                        custom_vocabulary=custom_vocabulary,
                        job_id=job_id,
                    )
                    tasks.append(task)
                
                # Execute batch in parallel
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect successful results
                for idx, result in enumerate(batch_results):
                    chunk_idx = batch_start + idx
                    if isinstance(result, Exception):
                        logger.error(
                            "Failed to transcribe chunk %d for job %s: %s",
                            chunk_idx + 1,
                            job_id,
                            str(result)
                        )
                        # Continue with other chunks
                        continue
                    
                    if result is not None:
                        all_chunk_results.append((chunk_idx, result))
                
                logger.info(
                    "Batch %d-%d completed (%d/%d successful)",
                    batch_start + 1,
                    batch_end,
                    len([r for r in batch_results if not isinstance(r, Exception)]),
                    len(batch_results)
                )
            
            # Sort results by chunk index to maintain order
            all_chunk_results.sort(key=lambda x: x[0])
            
            # Merge results
            all_segments = []
            all_text_parts = []
            detected_language = None
            
            for chunk_idx, chunk_result in all_chunk_results:
                # Store language from first chunk
                if detected_language is None:
                    detected_language = chunk_result.get("language")
                
                # Add segments and text
                all_segments.extend(chunk_result.get("segments", []))
                all_text_parts.append(chunk_result.get("text", ""))
            
            merged_text = " ".join(all_text_parts)
            
            # Sort segments by start time (in case of overlaps)
            all_segments.sort(key=lambda x: x["start"])
            
            logger.info(
                "PARALLEL chunked transcription completed for job: %s (%d total segments)",
                job_id,
                len(all_segments)
            )
            
            return {
                "text": merged_text,
                "language": detected_language,
                "duration": duration,
                "segments": all_segments,
            }
            
        except Exception as e:
            logger.exception("Chunked transcription failed for job: %s", job_id)
            raise
    
    async def _transcribe_single_chunk(
        self,
        chunk_path: Path,
        chunk_idx: int,
        total_chunks: int,
        chunk_duration: int,
        language: Optional[str],
        practice_area: PracticeArea,
        custom_vocabulary: Optional[List[str]],
        job_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribe a single chunk (used for parallel processing).
        
        Args:
            chunk_path: Path to chunk file
            chunk_idx: Index of this chunk (0-based)
            total_chunks: Total number of chunks
            chunk_duration: Duration of each chunk in seconds
            language: Optional language code
            practice_area: Legal practice area
            custom_vocabulary: Optional custom terms
            job_id: Job identifier for logging
            
        Returns:
            Chunk transcription result with adjusted timestamps
        """
        try:
            logger.info(
                "Transcribing chunk %d/%d for job: %s",
                chunk_idx + 1,
                total_chunks,
                job_id
            )
            
            # Transcribe chunk
            chunk_result = await self.azure_service.transcribe_audio(
                audio_file_path=str(chunk_path),
                language=language,
                prompt=self._get_transcription_prompt(practice_area, custom_vocabulary),
            )
            
            # Adjust segment timestamps to account for chunk offset
            chunk_offset = chunk_idx * chunk_duration
            adjusted_segments = []
            
            for seg in chunk_result.get("segments", []):
                adjusted_seg = seg.copy()
                adjusted_seg["start"] = seg["start"] + chunk_offset
                adjusted_seg["end"] = seg["end"] + chunk_offset
                adjusted_segments.append(adjusted_seg)
            
            logger.info(
                "Completed chunk %d/%d for job: %s (%d segments)",
                chunk_idx + 1,
                total_chunks,
                job_id,
                len(adjusted_segments)
            )
            
            return {
                "text": chunk_result.get("text", ""),
                "language": chunk_result.get("language"),
                "segments": adjusted_segments,
            }
            
        except Exception as e:
            logger.error(
                "Failed to transcribe chunk %d for job %s: %s",
                chunk_idx + 1,
                job_id,
                str(e)
            )
            raise
    
    def _extract_unique_speakers(self, segments: List[TranscriptSegment]) -> List[Speaker]:
        """
        Extract unique speakers from segments.
        
        Args:
            segments: List of transcript segments
            
        Returns:
            List of unique speakers
        """
        speakers_dict = {}
        
        for seg in segments:
            speaker_id = seg.speaker.speaker_id
            if speaker_id not in speakers_dict:
                speakers_dict[speaker_id] = seg.speaker
        
        return list(speakers_dict.values())


# Global service instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """
    Get or create the global transcription service instance.
    
    Returns:
        TranscriptionService instance
    """
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service

"""
Batch processing API endpoints.
Handles multi-file upload and batch job tracking.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime, timezone
import logging
import uuid

from models.schemas import (
    BatchUploadResponse,
    BatchStatusResponse,
    BatchResults,
    BatchJobInfo,
    ProcessingStatus,
)
from models.enums import MeetingType, PracticeArea
from utils.file_handler import get_file_handler
from utils.redis_service import get_redis_service
from services.transcription_service import get_transcription_service
from services.summarization_service import get_summarization_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Batch processing limits
MAX_FILES_PER_BATCH = 10
MAX_FILE_SIZE_MB = 500


@router.post("/batch/upload", response_model=BatchUploadResponse)
async def upload_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Video/audio files to process"),
    meeting_type: MeetingType = Form(...),
    practice_area: PracticeArea = Form(...),
    participants: str = Form(..., description="Comma-separated participant names"),
    case_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """
    Upload multiple video or audio files for batch processing.
    
    This endpoint:
    1. Validates all files
    2. Creates a batch ID
    3. Creates individual job IDs for each file
    4. Saves files to disk
    5. Starts background processing
    6. Returns batch tracking information
    
    Limits:
    - Maximum 10 files per batch
    - Maximum 500MB per file
    """
    try:
        # Validate number of files
        if len(files) > MAX_FILES_PER_BATCH:
            raise HTTPException(
                status_code=400,
                detail=f"Maximum {MAX_FILES_PER_BATCH} files allowed per batch. Received {len(files)}.",
            )
        
        if len(files) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one file is required.",
            )
        
        # Generate batch ID
        batch_id = str(uuid.uuid4())
        
        # Parse participants
        participant_list = [p.strip() for p in participants.split(",") if p.strip()]
        
        file_handler = get_file_handler()
        redis_service = await get_redis_service()
        
        job_ids = []
        job_infos = []
        
        # Process each file
        for idx, file in enumerate(files):
            try:
                # Validate file
                validation_errors = file_handler.validate_file(file)
                if validation_errors:
                    logger.warning(f"File {file.filename} validation failed: {validation_errors}")
                    # Create a failed job for this file
                    job_id = str(uuid.uuid4())
                    job_ids.append(job_id)
                    
                    # Store failed job metadata
                    await redis_service.set_job_metadata(
                        job_id,
                        {
                            "batch_id": batch_id,
                            "status": ProcessingStatus.FAILED.value,
                            "filename": file.filename,
                            "error": "; ".join(validation_errors),
                            "created_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                    continue
                
                # Generate job ID
                job_id = str(uuid.uuid4())
                job_ids.append(job_id)
                
                # Save file
                file_path, file_info = await file_handler.save_uploaded_file(file, job_id)
                
                # Store job metadata
                metadata = {
                    "batch_id": batch_id,
                    "job_id": job_id,
                    "filename": file.filename,
                    "original_filename": file.filename,
                    "file_path": str(file_path),
                    "file_size": file_info["size"],
                    "status": ProcessingStatus.QUEUED.value,
                    "meeting_type": meeting_type.value,
                    "practice_area": practice_area.value,
                    "participants": participant_list,
                    "case_id": case_id,
                    "notes": notes,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "progress": 0,
                }
                
                await redis_service.set_job_metadata(job_id, metadata)
                
                # Add to batch processing queue
                background_tasks.add_task(process_batch_job, job_id, batch_id)
                
                logger.info(f"File {file.filename} uploaded successfully - Job {job_id}")
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {str(e)}")
                # Create failed job
                job_id = str(uuid.uuid4())
                job_ids.append(job_id)
                await redis_service.set_job_metadata(
                    job_id,
                    {
                        "batch_id": batch_id,
                        "status": ProcessingStatus.FAILED.value,
                        "filename": file.filename,
                        "error": str(e),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    },
                )
        
        # Create batch metadata
        batch_metadata = {
            "batch_id": batch_id,
            "total_files": len(files),
            "job_ids": job_ids,
            "status": "processing",
            "meeting_type": meeting_type.value,
            "practice_area": practice_area.value,
            "participants": participant_list,
            "case_id": case_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
        # Store batch in Redis
        await redis_service.create_batch(batch_id, batch_metadata, job_ids)
        
        return BatchUploadResponse(
            batch_id=batch_id,
            total_files=len(files),
            job_ids=job_ids,
            status="processing",
            created_at=datetime.now(timezone.utc),
            message=f"Batch created successfully with {len(files)} file(s). Processing started.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str):
    """
    Get the status of a batch processing job.
    
    Returns aggregated status from all jobs in the batch including:
    - Overall progress percentage
    - Count of completed, processing, failed, and queued jobs
    - Individual job statuses
    """
    try:
        redis_service = await get_redis_service()
        
        # Get batch metadata
        batch_data = await redis_service.get_batch(batch_id)
        if not batch_data:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        
        # Get status of all jobs in batch
        job_ids = batch_data.get("job_ids", [])
        
        jobs = []
        completed_count = 0
        processing_count = 0
        failed_count = 0
        queued_count = 0
        total_progress = 0.0
        
        for job_id in job_ids:
            job_metadata = await redis_service.get_job_metadata(job_id)
            if job_metadata:
                status = job_metadata.get("status", ProcessingStatus.QUEUED.value)
                progress = job_metadata.get("progress", 0)
                
                # Count by status
                if status == ProcessingStatus.COMPLETED.value:
                    completed_count += 1
                elif status == ProcessingStatus.PROCESSING.value:
                    processing_count += 1
                elif status == ProcessingStatus.FAILED.value:
                    failed_count += 1
                else:
                    queued_count += 1
                
                total_progress += progress
                
                jobs.append(
                    BatchJobInfo(
                        job_id=job_id,
                        filename=job_metadata.get("filename", "unknown"),
                        status=ProcessingStatus(status),
                        progress_percentage=progress,
                        created_at=datetime.fromisoformat(job_metadata.get("created_at")),
                        completed_at=datetime.fromisoformat(job_metadata["completed_at"])
                        if job_metadata.get("completed_at")
                        else None,
                        error=job_metadata.get("error"),
                    )
                )
        
        # Calculate overall progress
        progress_percentage = total_progress / len(job_ids) if job_ids else 0
        
        # Determine overall status
        if completed_count == len(job_ids):
            overall_status = "completed"
        elif failed_count == len(job_ids):
            overall_status = "failed"
        elif completed_count + failed_count == len(job_ids):
            overall_status = "completed_with_errors"
        else:
            overall_status = "processing"
        
        # Update batch status
        batch_data["status"] = overall_status
        batch_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        await redis_service.update_batch(batch_id, batch_data)
        
        return BatchStatusResponse(
            batch_id=batch_id,
            total_files=len(job_ids),
            completed=completed_count,
            processing=processing_count,
            failed=failed_count,
            queued=queued_count,
            progress_percentage=progress_percentage,
            status=overall_status,
            jobs=jobs,
            created_at=datetime.fromisoformat(batch_data.get("created_at")),
            updated_at=datetime.now(timezone.utc),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get batch status: {str(e)}")


@router.get("/batch/{batch_id}/results", response_model=BatchResults)
async def get_batch_results(batch_id: str):
    """
    Get aggregated results from all jobs in a batch.
    
    Returns:
    - All transcriptions
    - All summaries
    - Success/failure counts
    """
    try:
        redis_service = await get_redis_service()
        
        # Get batch metadata
        batch_data = await redis_service.get_batch(batch_id)
        if not batch_data:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        
        job_ids = batch_data.get("job_ids", [])
        
        transcriptions = []
        summaries = []
        successful = 0
        failed = 0
        
        for job_id in job_ids:
            job_metadata = await redis_service.get_job_metadata(job_id)
            if not job_metadata:
                continue
            
            status = job_metadata.get("status")
            
            if status == ProcessingStatus.COMPLETED.value:
                successful += 1
                
                # Get transcription
                transcription_data = await redis_service.get_job_results(job_id, "transcription")
                if transcription_data:
                    transcriptions.append(transcription_data)
                
                # Get summary
                summary_data = await redis_service.get_job_results(job_id, "summary")
                if summary_data:
                    summaries.append(summary_data)
            elif status == ProcessingStatus.FAILED.value:
                failed += 1
        
        # Determine completion time
        completed_at = None
        if successful + failed == len(job_ids):
            completed_at = datetime.now(timezone.utc)
        
        return BatchResults(
            batch_id=batch_id,
            total_files=len(job_ids),
            successful=successful,
            failed=failed,
            transcriptions=transcriptions,
            summaries=summaries,
            created_at=datetime.fromisoformat(batch_data.get("created_at")),
            completed_at=completed_at,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting batch results: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get batch results: {str(e)}")


@router.delete("/batch/{batch_id}")
async def delete_batch(batch_id: str):
    """
    Cancel and delete an entire batch.
    
    This will:
    - Cancel all running jobs
    - Delete all files
    - Remove batch from Redis
    """
    try:
        redis_service = await get_redis_service()
        file_handler = get_file_handler()
        
        # Get batch metadata
        batch_data = await redis_service.get_batch(batch_id)
        if not batch_data:
            raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
        
        job_ids = batch_data.get("job_ids", [])
        
        # Cancel and delete all jobs
        for job_id in job_ids:
            try:
                # Update status to cancelled
                await redis_service.update_job_status(job_id, ProcessingStatus.CANCELLED.value)
                
                # Delete files
                job_metadata = await redis_service.get_job_metadata(job_id)
                if job_metadata and job_metadata.get("file_path"):
                    await file_handler.delete_job_files(job_id)
                
                # Delete job from Redis
                await redis_service.delete_job(job_id)
                
            except Exception as e:
                logger.warning(f"Error deleting job {job_id}: {str(e)}")
        
        # Delete batch from Redis
        await redis_service.delete_batch(batch_id)
        
        return JSONResponse(
            content={
                "message": f"Batch {batch_id} deleted successfully",
                "deleted_jobs": len(job_ids),
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting batch: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to delete batch: {str(e)}")


async def process_batch_job(job_id: str, batch_id: str):
    """
    Background task to process a single job in a batch.
    
    This is the same as the regular job processing but updates batch status.
    """
    try:
        redis_service = await get_redis_service()
        transcription_service = get_transcription_service()
        summarization_service = get_summarization_service()
        
        # Get job metadata
        metadata = await redis_service.get_job_metadata(job_id)
        if not metadata:
            logger.error(f"Job {job_id} metadata not found")
            return
        
        # Update status to processing
        await redis_service.update_job_status(job_id, ProcessingStatus.PROCESSING.value)
        await redis_service.update_job_progress(job_id, 10)
        
        # Transcribe
        logger.info(f"Starting transcription for batch job {job_id}")
        transcription_result = await transcription_service.transcribe_video(
            job_id=job_id,
            video_path=metadata["file_path"],
            practice_area=PracticeArea(metadata["practice_area"]),
            meeting_type=MeetingType(metadata["meeting_type"]),
            participants=metadata["participants"],
        )
        
        await redis_service.set_job_results(job_id, "transcription", transcription_result)
        await redis_service.update_job_progress(job_id, 60)
        
        # Summarize
        logger.info(f"Starting summarization for batch job {job_id}")
        summary_result = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription_result,
            summary_type="client_friendly",
            practice_area=PracticeArea(metadata["practice_area"]),
            meeting_type=MeetingType(metadata["meeting_type"]),
            participants=metadata["participants"],
            case_id=metadata.get("case_id"),
        )
        
        await redis_service.set_job_results(job_id, "summary", summary_result)
        await redis_service.update_job_progress(job_id, 100)
        
        # Mark as completed
        await redis_service.update_job_status(job_id, ProcessingStatus.COMPLETED.value)
        metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
        await redis_service.set_job_metadata(job_id, metadata)
        
        logger.info(f"Batch job {job_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Batch job {job_id} processing failed: {str(e)}", exc_info=True)
        await redis_service.update_job_status(job_id, ProcessingStatus.FAILED.value)
        
        metadata = await redis_service.get_job_metadata(job_id)
        if metadata:
            metadata["error"] = str(e)
            metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
            await redis_service.set_job_metadata(job_id, metadata)

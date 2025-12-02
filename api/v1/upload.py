"""
Video upload API endpoints.
Handles file upload, validation, and job creation.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from datetime import datetime

from models.schemas import VideoUploadResponse, JobStatus, ErrorResponse
from models.enums import ProcessingStatus, MeetingType, PracticeArea
from utils.file_handler import get_file_handler
from utils.validators import VideoValidator, MetadataValidator
from utils.redis_service import get_redis_service
from services.transcription_service import get_transcription_service
from services.summarization_service import get_summarization_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video or audio file"),
    meeting_type: MeetingType = Form(...),
    practice_area: PracticeArea = Form(...),
    participants: str = Form(..., description="Comma-separated participant names"),
    case_id: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
):
    """
    Upload a video or audio file for processing.
    
    This endpoint:
    1. Validates the file
    2. Saves it to disk
    3. Creates a processing job
    4. Returns job ID for status tracking
    
    The actual transcription happens in the background.
    """
    try:
        # Parse participants
        participant_list = [p.strip() for p in participants.split(",") if p.strip()]
        
        # Validate participants
        valid, msg = MetadataValidator.validate_participants(participant_list)
        if not valid:
            raise HTTPException(status_code=400, detail=msg)
        
        # Validate case ID if provided
        if case_id:
            valid, msg = MetadataValidator.validate_case_id(case_id)
            if not valid:
                raise HTTPException(status_code=400, detail=msg)
        
        # Read file content
        file_content = await file.read()
        file_size = len(file_content)
        
        # Validate file
        is_valid, messages = VideoValidator.validate_upload(
            filename=file.filename,
            file_size=file_size,
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=400,
                detail={"message": "File validation failed", "errors": messages},
            )
        
        # Save file
        file_handler = get_file_handler()
        job_id, file_path = await file_handler.save_uploaded_file(
            file_content=file_content,
            original_filename=file.filename,
        )
        
        # Determine file type
        _, file_type, _ = VideoValidator.validate_file_extension(file.filename)
        
        # Estimate processing time (will be updated after audio extraction)
        estimated_time = VideoValidator.estimate_processing_time(
            duration_seconds=300,  # Placeholder, will update after extraction
            file_type=file_type,
        )
        
        # Create job entry
        job = {
            "job_id": job_id,
            "status": ProcessingStatus.QUEUED.value,
            "filename": file.filename,
            "file_size_bytes": file_size,
            "file_path": str(file_path),
            "meeting_type": meeting_type.value,
            "practice_area": practice_area.value,
            "participants": participant_list,
            "case_id": case_id,
            "notes": notes,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Store in Redis
        redis_service = await get_redis_service()
        await redis_service.set_job(job_id, job)
        
        # Schedule background processing
        background_tasks.add_task(
            process_video_job,
            job_id=job_id,
        )
        
        logger.info(f"Video uploaded successfully: {job_id}")
        
        return VideoUploadResponse(
            job_id=job_id,
            status=ProcessingStatus.QUEUED,
            filename=file.filename,
            file_size_bytes=file_size,
            estimated_processing_time_seconds=estimated_time,
            message="File uploaded successfully. Processing will begin shortly.",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/upload/{job_id}/status", response_model=JobStatus)
async def get_job_status(job_id: str):
    """
    Get the status of a processing job.
    
    Returns current status, progress, and any errors.
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Calculate progress percentage
    status_str = job.get("status", "queued")
    try:
        status = ProcessingStatus(status_str)
    except ValueError:
        status = ProcessingStatus.QUEUED
    
    if status == ProcessingStatus.QUEUED:
        progress = 0
    elif status == ProcessingStatus.PROCESSING:
        progress = job.get("progress", 50)
    elif status == ProcessingStatus.COMPLETED:
        progress = 100
    elif status == ProcessingStatus.FAILED:
        progress = job.get("progress", 0)
    else:
        progress = 0
    
    # Parse datetime strings
    created_at = datetime.fromisoformat(job["created_at"]) if isinstance(job.get("created_at"), str) else job.get("created_at")
    updated_at = datetime.fromisoformat(job["updated_at"]) if isinstance(job.get("updated_at"), str) else job.get("updated_at")
    
    return JobStatus(
        job_id=job_id,
        status=status,
        progress_percentage=progress,
        current_step=job.get("current_step", "Initializing"),
        message=job.get("message", "Processing"),
        created_at=created_at,
        updated_at=updated_at,
        estimated_completion_time=job.get("estimated_completion_time"),
        error=job.get("error"),
    )


@router.delete("/upload/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a processing job and delete associated files.
    
    Note: Jobs that are already processing may not be immediately cancelled.
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Update status
    await redis_service.update_job(job_id, {
        "status": ProcessingStatus.CANCELLED.value,
        "updated_at": datetime.utcnow().isoformat(),
    })
    
    # Delete files
    try:
        file_handler = get_file_handler()
        await file_handler.delete_job_files(job_id)
    except Exception as e:
        logger.warning("Failed to delete files for job %s: %s", job_id, str(e))
    
    logger.info("Job cancelled: %s", job_id)
    
    return {"message": f"Job {job_id} cancelled successfully"}


async def process_video_job(job_id: str):
    """
    Background task to process video.
    
    This runs transcription and summarization in sequence.
    """
    redis_service = await get_redis_service()
    
    try:
        job = await redis_service.get_job(job_id)
        if not job:
            logger.error("Job %s not found in Redis", job_id)
            return
        
        # Update status to processing
        await redis_service.update_job(job_id, {
            "status": ProcessingStatus.PROCESSING.value,
            "current_step": "Starting processing",
            "updated_at": datetime.utcnow().isoformat(),
        })
        
        logger.info("Starting processing for job: %s", job_id)
        
        # Get services
        transcription_service = get_transcription_service()
        
        # Update progress
        await redis_service.update_job(job_id, {
            "progress": 10,
            "current_step": "Transcribing audio",
        })
        
        # Parse enums from stored values
        from models.enums import PracticeArea, MeetingType
        practice_area = PracticeArea(job["practice_area"])
        meeting_type = MeetingType(job["meeting_type"])
        
        # Transcribe
        from pathlib import Path
        transcription = await transcription_service.transcribe_video(
            job_id=job_id,
            video_path=Path(job["file_path"]),
            practice_area=practice_area,
            meeting_type=meeting_type,
            participants=job["participants"],
        )
        
        # Store transcription (serialize Pydantic model)
        import json
        transcription_dict = transcription.model_dump() if hasattr(transcription, 'model_dump') else transcription.dict()
        
        await redis_service.update_job(job_id, {
            "transcription": json.dumps(transcription_dict, default=str),
            "progress": 70,
            "current_step": "Generating summary",
        })
        
        # Generate summary
        summarization_service = get_summarization_service()
        summary = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription,
            summary_type="client_friendly",
            practice_area=practice_area,
            meeting_type=meeting_type,
            participants=job["participants"],
            case_id=job.get("case_id"),
        )
        
        # Store summary (serialize Pydantic model)
        summary_dict = summary.model_dump() if hasattr(summary, 'model_dump') else summary.dict()
        
        await redis_service.update_job(job_id, {
            "summary": json.dumps(summary_dict, default=str),
            "progress": 100,
            "status": ProcessingStatus.COMPLETED.value,
            "current_step": "Completed",
            "message": "Processing completed successfully",
            "updated_at": datetime.utcnow().isoformat(),
        })
        
        logger.info("Processing completed for job: %s", job_id)
        
    except Exception as e:
        logger.exception("Processing failed for job %s", job_id)
        await redis_service.update_job(job_id, {
            "status": ProcessingStatus.FAILED.value,
            "message": f"Processing failed: {str(e)}",
            "error": json.dumps({"message": str(e)}),
            "updated_at": datetime.utcnow().isoformat(),
        })

"""
Summary API endpoints.
Handles summary generation and retrieval.
"""
from fastapi import APIRouter, HTTPException
import logging

from models.schemas import SummaryResponse
from models.enums import SummaryType
from utils.redis_service import get_redis_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/summary/{job_id}", response_model=SummaryResponse)
async def get_summary(job_id: str):
    """
    Get summary results for a completed job.
    
    Returns the generated summary with action items, decisions, and risks.
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if "summary" not in job:
        raise HTTPException(
            status_code=400,
            detail="Summary not yet available. Check job status.",
        )
    
    # Deserialize summary from JSON string
    import json
    summary_data = json .loads(job["summary"]) if isinstance(job["summary"], str) else job["summary"]
    return SummaryResponse(**summary_data)


@router.post("/summary/{job_id}/regenerate", response_model=SummaryResponse)
async def regenerate_summary_with_history(job_id: str, summary_type: SummaryType):
    """
    Regenerate summary with a different type while preserving history.
    
    Previous summaries are saved in version history.
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if "transcription" not in job:
        raise HTTPException(
            status_code=400,
            detail="Transcription not available. Cannot generate summary.",
        )
    
    try:
        from services.summarization_service import get_summarization_service
        from models.schemas import TranscriptionResponse
        from models.enums import PracticeArea, MeetingType
        from datetime import datetime, timezone
        import json
        
        summarization_service = get_summarization_service()
        
        # Save current summary to history before regenerating
        if "summary" in job:
            current_summary = json.loads(job["summary"]) if isinstance(job["summary"], str) else job["summary"]
            current_summary["archived_at"] = datetime.now(timezone.utc).isoformat()
            
            # Get existing history or create new
            history_data = await redis_service.get_job_results(job_id, "summary_history")
            if not history_data:
                history_data = []
            
            history_data.append(current_summary)
            await redis_service.set_job_results(job_id, "summary_history", history_data)
        
        # Deserialize transcription
        transcription_data = json.loads(job["transcription"]) if isinstance(job["transcription"], str) else job["transcription"]
        transcription = TranscriptionResponse(**transcription_data)
        
        # Parse enums
        practice_area = PracticeArea(job["practice_area"])
        meeting_type = MeetingType(job["meeting_type"])
        
        # Generate new summary
        summary = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription,
            summary_type=summary_type,
            practice_area=practice_area,
            meeting_type=meeting_type,
            participants=job["participants"],
            case_id=job.get("case_id"),
        )
        
        # Store new summary
        summary_dict = summary.model_dump() if hasattr(summary, 'model_dump') else summary.dict()
        await redis_service.set_job_results(job_id, "summary", summary_dict)
        
        logger.info("Summary regenerated for job %s with type %s", job_id, summary_type)
        
        return summary
        
    except Exception as e:
        logger.exception("Summary regeneration failed for job %s", job_id)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.get("/summary/{job_id}/history")
async def get_summary_history(job_id: str):
    """
    Get version history of summaries for a job.
    
    Returns all previous versions of summaries that were generated.
    """
    redis_service = await get_redis_service()
    
    # Check job exists
    job = await redis_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    # Get history
    history_data = await redis_service.get_job_results(job_id, "summary_history")
    
    if not history_data:
        return {"job_id": job_id, "versions": [], "total": 0}
    
    return {
        "job_id": job_id,
        "versions": history_data,
        "total": len(history_data)
    }


@router.get("/summary/{job_id}/export")
async def export_summary(job_id: str, format: str = "pdf"):
    """
    Export summary in various formats.
    
    Supported formats:
    - pdf: Professional PDF document
    - docx: Microsoft Word document
    - json: JSON with full metadata
    """
    redis_service = await get_redis_service()
    
    # Get summary from Redis
    summary_data = await redis_service.get_job_results(job_id, "summary")
    
    if not summary_data:
        raise HTTPException(status_code=404, detail="Summary not found")
    
    from fastapi.responses import Response
    from utils.export_utils import get_export_utils
    
    export_utils = get_export_utils()
    
    if format == "pdf":
        content = export_utils.export_summary_pdf(summary_data)
        media_type = "application/pdf"
        filename = f"{job_id}_summary.pdf"
    elif format == "docx":
        content = export_utils.export_summary_docx(summary_data)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{job_id}_summary.docx"
    elif format == "json":
        content = export_utils.export_summary_json(summary_data)
        media_type = "application/json"
        filename = f"{job_id}_summary.json"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

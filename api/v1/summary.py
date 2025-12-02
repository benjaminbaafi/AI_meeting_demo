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
    summary_data = json.loads(job["summary"]) if isinstance(job["summary"], str) else job["summary"]
    return SummaryResponse(**summary_data)


@router.post("/summary/{job_id}/regenerate", response_model=SummaryResponse)
async def regenerate_summary(job_id: str, summary_type: SummaryType):
    """
    Regenerate summary with a different type.
    
    Allows generating client-friendly, lawyer-professional, or executive summaries
    from the same transcription.
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
        import json
        
        summarization_service = get_summarization_service()
        
        # Deserialize transcription from JSON string
        transcription_data = json.loads(job["transcription"]) if isinstance(job["transcription"], str) else job["transcription"]
        transcription = TranscriptionResponse(**transcription_data)
        
        # Parse enums
        practice_area = PracticeArea(job["practice_area"])
        meeting_type = MeetingType(job["meeting_type"])
        
        summary = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription,
            summary_type=summary_type,
            practice_area=practice_area,
            meeting_type=meeting_type,
            participants=job["participants"],
            case_id=job.get("case_id"),
        )
        
        # Store new summary (serialize Pydantic model)
        summary_dict = summary.model_dump() if hasattr(summary, 'model_dump') else summary.dict()
        await redis_service.update_job(job_id, {
            "summary": json.dumps(summary_dict, default=str),
        })
        
        logger.info("Summary regenerated for job %s with type %s", job_id, summary_type)
        
        return summary
        
    except Exception as e:
        logger.exception("Summary regeneration failed for job %s", job_id)
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

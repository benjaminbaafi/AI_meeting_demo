"""
Transcription API endpoints.
Handles transcription requests and results retrieval.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import logging

from models.schemas import TranscriptionResponse
from utils.redis_service import get_redis_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/transcribe/{job_id}", response_model=TranscriptionResponse)
async def get_transcription(job_id: str):
    """
    Get transcription results for a completed job.
    
    Returns the full transcription with segments, speakers, and metadata.
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if "transcription" not in job:
        raise HTTPException(
            status_code=400,
            detail="Transcription not yet available. Check job status.",
        )
    
    # Deserialize transcription from JSON string
    import json
    transcription_data = json.loads(job["transcription"]) if isinstance(job["transcription"], str) else job["transcription"]
    return TranscriptionResponse(**transcription_data)


@router.get("/transcribe/{job_id}/download")
async def download_transcript(job_id: str, format: str = "txt"):
    """
    Download transcript in various formats.
    
    Supported formats:
    - txt: Plain text
    - json: JSON with full metadata
    - vtt: WebVTT subtitle format
    - pdf: Professional PDF document
    - docx: Microsoft Word document
    """
    redis_service = await get_redis_service()
    job = await redis_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if "transcription" not in job:
        raise HTTPException(
            status_code=400,
            detail="Transcription not yet available",
        )
    
    # Deserialize transcription from JSON string
    import json
    from fastapi.responses import Response
    from utils.export_utils import get_export_utils
    
    transcription_data = json.loads(job["transcription"]) if isinstance(job["transcription"], str) else job["transcription"]
    transcription = TranscriptionResponse(**transcription_data)
    
    export_utils = get_export_utils()
    
    if format == "txt":
        content = transcription.full_text
        media_type = "text/plain"
        filename = f"{job_id}_transcript.txt"
    elif format == "json":
        content = export_utils.export_transcription_json(transcription.model_dump())
        media_type = "application/json"
        filename = f"{job_id}_transcript.json"
    elif format == "vtt":
        content = _generate_vtt(transcription)
        media_type = "text/vtt"
        filename = f"{job_id}_transcript.vtt"
    elif format == "pdf":
        content = export_utils.export_transcription_pdf(transcription.model_dump())
        media_type = "application/pdf"
        filename = f"{job_id}_transcript.pdf"
        return Response(content=content, media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    elif format == "docx":
        content = export_utils.export_transcription_docx(transcription.model_dump())
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{job_id}_transcript.docx"
        return Response(content=content, media_type=media_type, headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    
    # Save to temp file and return (for text formats)
    from pathlib import Path
    from utils.file_handler import get_file_handler
    
    file_handler = get_file_handler()
    output_path = file_handler.get_output_path(job_id, "transcript", f".{format}")
    
    if isinstance(content, bytes):
        output_path.write_bytes(content)
    else:
        output_path.write_text(content, encoding="utf-8")
    
    return FileResponse(
        path=output_path,
        media_type=media_type,
        filename=filename,
    )


def _generate_vtt(transcription: TranscriptionResponse) -> str:
    """Generate WebVTT format from transcription."""
    vtt_lines = ["WEBVTT", ""]
    
    for idx, segment in enumerate(transcription.segments, 1):
        start = _format_timestamp(segment.start_time)
        end = _format_timestamp(segment.end_time)
        speaker = segment.speaker.name or segment.speaker.speaker_id
        
        vtt_lines.append(f"{idx}")
        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(f"<v {speaker}>{segment.text}</v>")
        vtt_lines.append("")
    
    return "\n".join(vtt_lines)


def _format_timestamp(seconds: float) -> str:
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

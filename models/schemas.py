"""
Pydantic schemas for request/response validation.
All models include comprehensive validation and documentation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from models.enums import (
    ProcessingStatus,
    MeetingType,
    PracticeArea,
    SummaryType,
    ActionItemPriority,
    SpeakerRole,
)


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        use_enum_values=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )


# ============================================================================
# Video Upload Schemas
# ============================================================================

class VideoUploadRequest(BaseSchema):
    """Request for uploading a video file."""
    meeting_type: MeetingType = Field(..., description="Type of meeting")
    practice_area: PracticeArea = Field(..., description="Legal practice area")
    participants: List[str] = Field(..., min_length=1, description="List of participant names")
    case_id: Optional[str] = Field(None, description="Associated case/matter ID")
    meeting_date: Optional[datetime] = Field(None, description="Date of the meeting")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    
    @field_validator("participants")
    @classmethod
    def validate_participants(cls, v: List[str]) -> List[str]:
        """Ensure participants list is not empty and names are valid."""
        if not v:
            raise ValueError("At least one participant is required")
        return [name.strip() for name in v if name.strip()]


class VideoUploadResponse(BaseSchema):
    """Response after video upload."""
    job_id: str = Field(..., description="Unique job identifier")
    status: ProcessingStatus = Field(..., description="Current processing status")
    filename: str = Field(..., description="Original filename")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Video duration")
    estimated_processing_time_seconds: Optional[int] = Field(None, description="Estimated processing time")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    message: str = Field(..., description="Status message")


# ============================================================================
# Transcription Schemas
# ============================================================================

class Speaker(BaseSchema):
    """Speaker information in a transcript."""
    speaker_id: str = Field(..., description="Unique speaker identifier")
    name: Optional[str] = Field(None, description="Speaker name if identified")
    role: SpeakerRole = Field(default=SpeakerRole.UNKNOWN, description="Speaker role")


class TranscriptSegment(BaseSchema):
    """A segment of the transcript with timing information."""
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    end_time: float = Field(..., ge=0, description="End time in seconds")
    speaker: Speaker = Field(..., description="Speaker information")
    text: str = Field(..., min_length=1, description="Transcript text")
    confidence: float = Field(..., ge=0, le=1, description="Transcription confidence score")
    
    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: float, info) -> float:
        """Ensure end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be greater than start_time")
        return v


class TranscriptionRequest(BaseSchema):
    """Request for transcription."""
    job_id: str = Field(..., description="Job ID from upload")
    enable_speaker_diarization: bool = Field(default=True, description="Enable speaker identification")
    language: Optional[str] = Field(None, description="Language code (auto-detect if None)")
    custom_vocabulary: Optional[List[str]] = Field(None, description="Custom legal terms to recognize")


class TranscriptionResponse(BaseSchema):
    """Response with transcription results."""
    job_id: str = Field(..., description="Job identifier")
    status: ProcessingStatus = Field(..., description="Processing status")
    segments: List[TranscriptSegment] = Field(default_factory=list, description="Transcript segments")
    full_text: str = Field(default="", description="Complete transcript text")
    speakers: List[Speaker] = Field(default_factory=list, description="List of identified speakers")
    duration_seconds: float = Field(..., ge=0, description="Total duration")
    word_count: int = Field(..., ge=0, description="Total word count")
    average_confidence: float = Field(..., ge=0, le=1, description="Average confidence score")
    language_detected: Optional[str] = Field(None, description="Detected language")
    processing_time_seconds: float = Field(..., ge=0, description="Time taken to process")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ============================================================================
# Summary Schemas
# ============================================================================

class ActionItem(BaseSchema):
    """An action item extracted from the meeting."""
    description: str = Field(..., min_length=1, description="Action item description")
    assignee: Optional[str] = Field(None, description="Person responsible")
    deadline: Optional[datetime] = Field(None, description="Due date")
    priority: ActionItemPriority = Field(default=ActionItemPriority.MEDIUM)
    completed: bool = Field(default=False, description="Completion status")
    notes: Optional[str] = Field(None, description="Additional notes")


class KeyDecision(BaseSchema):
    """A key decision made during the meeting."""
    decision: str = Field(..., description="The decision made")
    rationale: Optional[str] = Field(None, description="Reasoning behind the decision")
    timestamp: Optional[float] = Field(None, description="When in the meeting this was decided")


class RiskFlag(BaseSchema):
    """A potential risk or compliance issue identified."""
    description: str = Field(..., description="Risk description")
    severity: str = Field(..., description="Severity level")
    recommendation: Optional[str] = Field(None, description="Recommended action")


class SummaryRequest(BaseSchema):
    """Request for summary generation."""
    job_id: str = Field(..., description="Job ID from transcription")
    summary_type: SummaryType = Field(..., description="Type of summary to generate")
    include_action_items: bool = Field(default=True)
    include_key_decisions: bool = Field(default=True)
    include_risk_flags: bool = Field(default=True)
    max_length_words: Optional[int] = Field(None, ge=50, le=2000, description="Maximum summary length")


class SummaryResponse(BaseSchema):
    """Response with summary results."""
    job_id: str = Field(..., description="Job identifier")
    status: ProcessingStatus = Field(..., description="Processing status")
    summary_type: SummaryType = Field(..., description="Type of summary")
    
    # Summary content
    executive_summary: str = Field(default="", description="High-level overview")
    detailed_summary: str = Field(default="", description="Detailed summary")
    action_items: List[ActionItem] = Field(default_factory=list)
    key_decisions: List[KeyDecision] = Field(default_factory=list)
    risk_flags: List[RiskFlag] = Field(default_factory=list)
    
    # Topics and themes
    main_topics: List[str] = Field(default_factory=list, description="Main discussion topics")
    legal_entities_mentioned: List[str] = Field(default_factory=list)
    deadlines_mentioned: List[datetime] = Field(default_factory=list)
    
    # Metadata
    word_count: int = Field(..., ge=0)
    processing_time_seconds: float = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


# ============================================================================
# Real-time Streaming Schemas
# ============================================================================

class StreamingMessage(BaseSchema):
    """Message for real-time streaming communication."""
    message_type: str = Field(..., description="Type of message (transcript_update, status, error)")
    session_id: str = Field(..., description="Streaming session ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict, description="Message payload")


class StreamStartRequest(BaseSchema):
    """Request to start a streaming session."""
    meeting_type: MeetingType = Field(..., description="Type of meeting")
    practice_area: PracticeArea = Field(..., description="Legal practice area")
    participants: List[str] = Field(..., min_length=1)
    language: Optional[str] = Field(None, description="Expected language")


class StreamStartResponse(BaseSchema):
    """Response when starting a stream."""
    session_id: str = Field(..., description="Unique session identifier")
    websocket_url: str = Field(..., description="WebSocket connection URL")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(..., description="Session expiration time")


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorDetail(BaseSchema):
    """Detailed error information."""
    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")


class ErrorResponse(BaseSchema):
    """Standard error response."""
    status: str = Field(default="error")
    message: str = Field(..., description="Human-readable error message")
    details: List[ErrorDetail] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = Field(None, description="Request identifier for tracking")


# ============================================================================
# Job Status Schema
# ============================================================================

class JobStatus(BaseSchema):
    """Generic job status response."""
    job_id: str = Field(..., description="Job identifier")
    status: ProcessingStatus = Field(..., description="Current status")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current processing step")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation time")
    updated_at: datetime = Field(..., description="Last update time")
    estimated_completion_time: Optional[datetime] = Field(None)
    error: Optional[ErrorDetail] = Field(None, description="Error if failed")

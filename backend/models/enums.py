"""
Enumerations for the AI Meeting Participant system.
Provides type-safe constants for various domain concepts.
"""
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of a processing job."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MeetingType(str, Enum):
    """Type of legal meeting."""
    CONSULTATION = "consultation"
    DEPOSITION = "deposition"
    CLIENT_UPDATE = "client_update"
    STRATEGY_SESSION = "strategy_session"
    DOCUMENT_REVIEW = "document_review"
    COURT_HEARING = "court_hearing"
    MEDIATION = "mediation"
    OTHER = "other"


class PracticeArea(str, Enum):
    """Legal practice area."""
    FAMILY_LAW = "family_law"
    CORPORATE_LAW = "corporate_law"
    LITIGATION = "litigation"
    REAL_ESTATE = "real_estate"
    ESTATE_PLANNING = "estate_planning"
    CRIMINAL_DEFENSE = "criminal_defense"
    IMMIGRATION = "immigration"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    EMPLOYMENT_LAW = "employment_law"
    TAX_LAW = "tax_law"
    BANKRUPTCY = "bankruptcy"
    PERSONAL_INJURY = "personal_injury"
    OTHER = "other"


class SummaryType(str, Enum):
    """Type of summary to generate."""
    CLIENT_FRIENDLY = "client_friendly"
    LAWYER_PROFESSIONAL = "lawyer_professional"
    EXECUTIVE = "executive"
    COURT_READY = "court_ready"
    ACTION_ITEMS_ONLY = "action_items_only"


class ActionItemPriority(str, Enum):
    """Priority level for action items."""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SpeakerRole(str, Enum):
    """Role of a speaker in the meeting."""
    LAWYER = "lawyer"
    CLIENT = "client"
    PARALEGAL = "paralegal"
    EXPERT_WITNESS = "expert_witness"
    OPPOSING_COUNSEL = "opposing_counsel"
    JUDGE = "judge"
    MEDIATOR = "mediator"
    OTHER = "other"
    UNKNOWN = "unknown"

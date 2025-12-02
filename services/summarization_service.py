"""
Summarization service.
Generates summaries, extracts action items, and identifies key decisions.
"""
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

from models.schemas import (
    SummaryResponse,
    ActionItem,
    KeyDecision,
    RiskFlag,
    TranscriptionResponse,
)
from models.enums import (
    ProcessingStatus,
    SummaryType,
    PracticeArea,
    MeetingType,
    ActionItemPriority,
)
from services.azure_openai_service import get_azure_openai_service
from prompts.summary_prompts import SummaryPrompts
from prompts.action_item_prompts import ActionItemPrompts


logger = logging.getLogger(__name__)


class SummarizationService:
    """Generates summaries and extracts structured information from transcripts."""
    
    def __init__(self):
        """Initialize summarization service."""
        self.azure_service = get_azure_openai_service()
        self.summary_prompts = SummaryPrompts()
        self.action_prompts = ActionItemPrompts()
        
        logger.info("SummarizationService initialized")
    
    async def generate_summary(
        self,
        job_id: str,
        transcription: TranscriptionResponse,
        summary_type: SummaryType,
        practice_area: PracticeArea,
        meeting_type: MeetingType,
        participants: List[str],
        case_id: Optional[str] = None,
        include_action_items: bool = True,
        include_key_decisions: bool = True,
        include_risk_flags: bool = True,
    ) -> SummaryResponse:
        """
        Generate a summary from transcription.
        
        Args:
            job_id: Job identifier
            transcription: Transcription result
            summary_type: Type of summary to generate
            practice_area: Legal practice area
            meeting_type: Type of meeting
            participants: List of participants
            case_id: Optional case identifier
            include_action_items: Extract action items
            include_key_decisions: Extract key decisions
            include_risk_flags: Identify risks
            
        Returns:
            SummaryResponse with generated summary
        """
        start_time = datetime.now(timezone.utc)
        
        try:
            logger.info("Generating %s summary for job: %s", summary_type, job_id)
            
            # Generate main summary based on type
            if summary_type == SummaryType.CLIENT_FRIENDLY:
                summary_text = await self._generate_client_summary(
                    transcription.full_text,
                    meeting_type,
                    practice_area,
                    participants,
                )
            elif summary_type == SummaryType.LAWYER_PROFESSIONAL:
                summary_text = await self._generate_lawyer_summary(
                    transcription.full_text,
                    meeting_type,
                    practice_area,
                    case_id,
                )
            elif summary_type == SummaryType.EXECUTIVE:
                summary_text = await self._generate_executive_summary(
                    transcription.full_text,
                    meeting_type,
                )
            else:
                summary_text = await self._generate_generic_summary(
                    transcription.full_text
                )
            
            # Extract action items
            action_items = []
            if include_action_items:
                action_items = await self._extract_action_items(
                    transcription.full_text,
                    practice_area,
                    participants,
                )
            
            # Extract key decisions
            key_decisions = []
            if include_key_decisions:
                key_decisions = await self._extract_key_decisions(
                    transcription.full_text
                )
            
            # Identify risks
            risk_flags = []
            if include_risk_flags:
                risk_flags = await self._identify_risks(
                    transcription.full_text,
                    practice_area,
                )
            
            # Extract topics and entities
            main_topics = await self._extract_topics(transcription.full_text)
            legal_entities = await self._extract_legal_entities(transcription.full_text)
            deadlines = await self._extract_deadlines(transcription.full_text)
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Create response
            response = SummaryResponse(
                job_id=job_id,
                status=ProcessingStatus.COMPLETED,
                summary_type=summary_type,
                executive_summary=summary_text[:500],  # First 500 chars as executive summary
                detailed_summary=summary_text,
                action_items=action_items,
                key_decisions=key_decisions,
                risk_flags=risk_flags,
                main_topics=main_topics,
                legal_entities_mentioned=legal_entities,
                deadlines_mentioned=deadlines,
                word_count=len(summary_text.split()),
                processing_time_seconds=processing_time,
                completed_at=datetime.now(timezone.utc),
            )
            
            logger.info("Summary generation completed for job: %s", job_id)
            return response
            
        except Exception:
            logger.exception("Summary generation failed for job %s", job_id)
            raise
    
    async def _generate_client_summary(
        self,
        transcript: str,
        meeting_type: MeetingType,
        practice_area: PracticeArea,
        participants: List[str],
    ) -> str:
        """Generate client-friendly summary."""
        prompt = self.summary_prompts.get_client_friendly_summary_prompt(
            meeting_type=meeting_type,
            practice_area=practice_area,
            participant_names=participants,
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Meeting transcript:\n\n{transcript}"},
        ]
        
        return await self.azure_service.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
    
    async def _generate_lawyer_summary(
        self,
        transcript: str,
        meeting_type: MeetingType,
        practice_area: PracticeArea,
        case_id: Optional[str],
    ) -> str:
        """Generate lawyer-professional summary."""
        prompt = self.summary_prompts.get_lawyer_professional_summary_prompt(
            meeting_type=meeting_type,
            practice_area=practice_area,
            case_id=case_id,
        )
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Meeting transcript:\n\n{transcript}"},
        ]
        
        return await self.azure_service.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=3000,
        )
    
    async def _generate_executive_summary(
        self,
        transcript: str,
        meeting_type: MeetingType,
    ) -> str:
        """Generate executive summary."""
        prompt = self.summary_prompts.get_executive_summary_prompt(meeting_type)
        
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Meeting transcript:\n\n{transcript}"},
        ]
        
        return await self.azure_service.generate_completion(
            messages=messages,
            temperature=0.5,
            max_tokens=500,
        )
    
    async def _generate_generic_summary(self, transcript: str) -> str:
        """Generate generic summary."""
        messages = [
            {
                "role": "system",
                "content": "Provide a concise summary of this meeting transcript.",
            },
            {"role": "user", "content": transcript},
        ]
        
        return await self.azure_service.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
        )
    
    async def _extract_action_items(
        self,
        transcript: str,
        practice_area: PracticeArea,
        participants: List[str],
    ) -> List[ActionItem]:
        """Extract action items from transcript."""
        try:
            prompt = self.action_prompts.get_comprehensive_extraction_prompt(practice_area)
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"},
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3,
            )
            
            # Parse action items
            action_items = []
            for item_data in result.get("action_items", []):
                try:
                    action_item = ActionItem(
                        description=item_data.get("description", ""),
                        assignee=item_data.get("assignee"),
                        deadline=item_data.get("deadline"),
                        priority=ActionItemPriority(item_data.get("priority", "medium")),
                        notes=item_data.get("notes"),
                    )
                    action_items.append(action_item)
                except Exception:
                    logger.exception("Failed to parse action item")
            
            return action_items
            
        except Exception:
            logger.exception("Action item extraction failed")
            return []
    
    async def _extract_key_decisions(self, transcript: str) -> List[KeyDecision]:
        """Extract key decisions from transcript."""
        try:
            prompt = self.summary_prompts.get_key_decisions_extraction_prompt()
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"},
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3,
            )
            
            # Parse decisions
            decisions = []
            for decision_data in result.get("decisions", []):
                try:
                    decision = KeyDecision(
                        decision=decision_data.get("decision", ""),
                        rationale=decision_data.get("rationale"),
                        timestamp=decision_data.get("timestamp"),
                    )
                    decisions.append(decision)
                except Exception:
                    logger.exception("Failed to parse decision")
            
            return decisions
            
        except Exception:
            logger.exception("Decision extraction failed")
            return []
    
    async def _identify_risks(
        self,
        transcript: str,
        practice_area: PracticeArea,
    ) -> List[RiskFlag]:
        """Identify risks and compliance issues."""
        try:
            prompt = self.summary_prompts.get_risk_assessment_prompt(practice_area)
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript:\n\n{transcript}"},
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3,
            )
            
            # Parse risks
            risks = []
            for risk_data in result.get("risks", []):
                try:
                    risk = RiskFlag(
                        description=risk_data.get("description", ""),
                        severity=risk_data.get("severity", "medium"),
                        recommendation=risk_data.get("recommendation"),
                    )
                    risks.append(risk)
                except Exception:
                    logger.exception("Failed to parse risk")
            
            return risks
            
        except Exception:
            logger.exception("Risk identification failed")
            return []
    
    async def _extract_topics(self, transcript: str) -> List[str]:
        """Extract main topics from transcript."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Extract the main topics discussed in this meeting. Return as JSON array of strings.",
                },
                {"role": "user", "content": transcript[:2000]},  # First 2000 chars
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.5,
            )
            
            return result.get("topics", [])
            
        except Exception:
            logger.exception("Topic extraction failed")
            return []
    
    async def _extract_legal_entities(self, transcript: str) -> List[str]:
        """Extract legal entities mentioned."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Extract all legal entities (companies, organizations, case names) mentioned. Return as JSON array.",
                },
                {"role": "user", "content": transcript[:2000]},
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3,
            )
            
            return result.get("entities", [])
            
        except Exception:
            logger.exception("Entity extraction failed")
            return []
    
    async def _extract_deadlines(self, transcript: str) -> List[datetime]:
        """Extract deadlines mentioned."""
        # Simplified - in production, use more sophisticated date extraction
        return []


# Global service instance
_summarization_service: Optional[SummarizationService] = None


def get_summarization_service() -> SummarizationService:
    """
    Get or create the global summarization service instance.
    
    Returns:
        SummarizationService instance
    """
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service

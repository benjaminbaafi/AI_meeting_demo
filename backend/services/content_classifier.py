"""
Content Classification Service.
Automatically detects the type of video content and selects appropriate processing strategies.
"""
import logging
from typing import Dict, Any, Optional
from models.enums import MeetingType, PracticeArea
from services.azure_openai_service import AzureOpenAIService

logger = logging.getLogger(__name__)


class ContentType:
    """Detected content types beyond legal meetings."""
    LEGAL_MEETING = "legal_meeting"
    EDUCATIONAL = "educational"
    BUSINESS_MEETING = "business_meeting"
    PODCAST = "podcast"
    PRESENTATION = "presentation"
    INTERVIEW = "interview"
    LECTURE = "lecture"
    WEBINAR = "webinar"
    OTHER = "other"


class ContentClassifier:
    """Automatically classifies video content and selects appropriate prompts."""
    
    def __init__(self):
        """Initialize the content classifier."""
        self.azure_service = AzureOpenAIService()
        logger.info("ContentClassifier initialized")
    
    async def classify_content(
        self,
        transcript_sample: str,
        max_sample_length: int = 3000
    ) -> Dict[str, Any]:
        """
        Analyze a transcript sample and classify the content type.
        
        Args:
            transcript_sample: First portion of the transcript
            max_sample_length: Maximum characters to analyze (default: 3000)
            
        Returns:
            Dict with classification results:
            {
                "content_type": str,
                "meeting_type": MeetingType (if legal),
                "practice_area": PracticeArea (if legal),
                "confidence": float,
                "reasoning": str,
                "suggested_prompts": str
            }
        """
        try:
            # Truncate sample if too long
            sample = transcript_sample[:max_sample_length]
            
            # Create classification prompt
            prompt = self._get_classification_prompt()
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript to classify:\n\n{sample}"}
            ]
            
            # Get classification from GPT
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3
            )
            
            logger.info(f"Content classified as: {result.get('content_type')}")
            
            # Parse and validate the result
            classification = self._parse_classification(result)
            
            return classification
            
        except Exception as e:
            logger.error(f"Content classification failed: {str(e)}")
            # Return safe defaults
            return {
                "content_type": ContentType.OTHER,
                "meeting_type": MeetingType.OTHER,
                "practice_area": PracticeArea.OTHER,
                "confidence": 0.0,
                "reasoning": "Classification failed, using defaults",
                "suggested_prompts": "general"
            }
    
    def _get_classification_prompt(self) -> str:
        """Generate the classification prompt."""
        return """You are an expert content analyzer. Your task is to classify the type of video content based on the transcript.

Analyze the transcript and determine:

1. **Content Type** (choose one):
   - legal_meeting: Depositions, client meetings, court hearings, legal consultations
   - educational: Tutorials, courses, how-to videos, educational content
   - business_meeting: Corporate meetings, team discussions, project reviews
   - podcast: Conversational podcasts, interviews with hosts
   - presentation: Conference talks, keynotes, formal presentations
   - interview: Job interviews, media interviews, Q&A sessions
   - lecture: Academic lectures, university classes
   - webinar: Online seminars, training sessions
   - other: Anything that doesn't fit above

2. **If Legal Content**, also identify:
   - meeting_type: consultation, deposition, client_update, strategy_session, court_hearing, mediation, other
   - practice_area: family_law, corporate_law, litigation, real_estate, criminal_defense, immigration, etc.

3. **Confidence Level** (0.0 to 1.0):
   - How confident are you in this classification?

4. **Reasoning**:
   - What specific clues led to this classification?

5. **Suggested Prompts**:
   - legal: Use legal-specific prompts
   - educational: Use educational content prompts
   - business: Use business meeting prompts
   - general: Use general-purpose prompts

**IMPORTANT**: Return your analysis as a valid JSON object with this structure:
{
    "content_type": "legal_meeting",
    "meeting_type": "deposition",
    "practice_area": "litigation",
    "confidence": 0.95,
    "reasoning": "Transcript contains legal terminology like 'deposition', 'counsel', 'objection'. Formal Q&A structure typical of depositions.",
    "suggested_prompts": "legal",
    "key_indicators": [
        "Legal terminology present",
        "Formal question-answer structure",
        "References to court procedures"
    ]
}

For non-legal content, set meeting_type and practice_area to "other".
"""
    
    def _parse_classification(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate the classification result."""
        content_type = result.get("content_type", ContentType.OTHER)
        
        # Convert string values to enums if legal content
        if content_type == ContentType.LEGAL_MEETING:
            try:
                meeting_type = MeetingType(result.get("meeting_type", "other"))
            except ValueError:
                meeting_type = MeetingType.OTHER
            
            try:
                practice_area = PracticeArea(result.get("practice_area", "other"))
            except ValueError:
                practice_area = PracticeArea.OTHER
        else:
            meeting_type = MeetingType.OTHER
            practice_area = PracticeArea.OTHER
        
        return {
            "content_type": content_type,
            "meeting_type": meeting_type,
            "practice_area": practice_area,
            "confidence": float(result.get("confidence", 0.5)),
            "reasoning": result.get("reasoning", "No reasoning provided"),
            "suggested_prompts": result.get("suggested_prompts", "general"),
            "key_indicators": result.get("key_indicators", [])
        }


# Global service instance
_content_classifier: Optional[ContentClassifier] = None


def get_content_classifier() -> ContentClassifier:
    """
    Get or create the global content classifier instance.
    
    Returns:
        ContentClassifier instance
    """
    global _content_classifier
    if _content_classifier is None:
        _content_classifier = ContentClassifier()
    return _content_classifier

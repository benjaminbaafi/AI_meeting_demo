"""
Smart content detection service.
Automatically detects the topic/domain of transcribed content and selects appropriate summary style.
"""
import logging
from typing import Dict, Any, Optional
from services.azure_openai_service import get_azure_openai_service

logger = logging.getLogger(__name__)


class ContentDetectionService:
    """Detects content type and domain from transcripts."""
    
    def __init__(self):
        """Initialize content detection service."""
        self.azure_service = get_azure_openai_service()
        logger.info("ContentDetectionService initialized")
    
    async def detect_content_type(self, transcript: str) -> Dict[str, Any]:
        """
        Detect the content type, domain, and topic from transcript.
        
        Args:
            transcript: Transcription text
            
        Returns:
            Dict with detected domain, topics, meeting_type, and suggested_summary_style
        """
        try:
            # Use first 3000 characters for analysis
            sample = transcript[:3000]
            
            prompt = """Analyze this transcript and identify:
1. Primary domain/industry (e.g., legal, technology, education, business, healthcare, etc.)
2. Main topics discussed
3. Type of content (meeting, lecture, presentation, conversation, etc.)
4. Suggested summary style (professional, technical, educational, client-friendly, etc.)

Return as JSON:
{
  "domain": "the primary domain/industry",
  "topics": ["topic1", "topic2", "topic3"],
  "content_type": "meeting/lecture/presentation/etc",
  "is_legal": true/false,
  "suggested_summary_style": "professional/technical/educational/client-friendly",
  "confidence": 0.0-1.0,
  "key_themes": ["theme1", "theme2"]
}"""
            
            messages = [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Transcript:\n\n{sample}"}
            ]
            
            result = await self.azure_service.generate_json_completion(
                messages=messages,
                temperature=0.3
            )
            
            logger.info(f"Detected domain: {result.get('domain')} (confidence: {result.get('confidence')})")
            return result
            
        except Exception:
            logger.exception("Content detection failed, using generic fallback")
            return {
                "domain": "general",
                "topics": [],
                "content_type": "meeting",
                "is_legal": False,
                "suggested_summary_style": "professional",
                "confidence": 0.5,
                "key_themes": []
            }
    
    async def generate_smart_summary_prompt(
        self,
        transcript: str,
        content_metadata: Dict[str, Any]
    ) -> str:
        """
        Generate a domain-appropriate summary prompt.
        
        Args:
            transcript: Full transcript
            content_metadata: Result from detect_content_type()
            
        Returns:
            Tailored summary prompt
        """
        domain = content_metadata.get("domain", "general")
        topics = content_metadata.get("topics", [])
        content_type = content_metadata.get("content_type", "meeting")
        
        # Build domain-specific prompt
        if domain.lower() in ["legal", "law"]:
            prompt = f"""You are summarizing a legal {content_type} transcript.
            
Focus on:
- Legal issues and implications
- Key decisions and arguments
- Action items and follow-ups
- Compliance matters
- Deadlines and commitments

Provide a clear, professional summary suitable for legal professionals."""

        elif domain.lower() in ["technology", "software", "engineering", "tech"]:
            prompt = f"""You are summarizing a technical {content_type} transcript about {', '.join(topics[:3])}.
            
Focus on:
- Technical concepts and implementations
- Architectural decisions
- Action items and next steps
- Challenges and solutions
- Technical specifications

Provide a clear summary suitable for technical professionals."""

        elif domain.lower() in ["education", "academic", "teaching", "tutorial"]:
            prompt = f"""You are summarizing an educational {content_type} about {', '.join(topics[:3])}.
            
Focus on:
- Main concepts taught
- Key learning points
- Examples and explanations
- Q&A highlights
- Practical applications

Provide a clear summary suitable for learners and educators."""

        elif domain.lower() in ["business", "sales", "marketing", "finance"]:
            prompt = f"""You are summarizing a business {content_type} about {', '.join(topics[:3])}.
            
Focus on:
- Business objectives and goals
- Key decisions and strategies
- Action items and ownership
- Metrics and targets
- Follow-up items

Provide an executive-style summary."""

        elif domain.lower() in ["healthcare", "medical", "clinical"]:
            prompt = f"""You are summarizing a healthcare {content_type} about {', '.join(topics[:3])}.
            
Focus on:
- Clinical discussions
- Patient care considerations
- Medical decisions and protocols
- Action items
- Compliance and safety

Provide a professional medical summary."""

        else:
            # Generic professional summary
            prompt = f"""You are summarizing a {content_type} about {', '.join(topics[:3])}.
            
Focus on:
- Main topics discussed: {', '.join(topics)}
- Key decisions made
- Action items and next steps
- Important points raised
- Outcomes and conclusions

Provide a clear, professional summary."""

        return prompt


# Global instance
_content_detection_service: Optional[ContentDetectionService] = None


def get_content_detection_service() -> ContentDetectionService:
    """Get or create the global content detection service instance."""
    global _content_detection_service
    if _content_detection_service is None:
        _content_detection_service = ContentDetectionService()
    return _content_detection_service

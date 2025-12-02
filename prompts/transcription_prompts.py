"""
Premium prompt templates for transcription enhancement.
These prompts are used with Azure OpenAI GPT models to improve transcription quality.
"""
from typing import List, Optional
from models.enums import PracticeArea, MeetingType


class TranscriptionPrompts:
    """Professional prompt templates for transcription processing."""
    
    @staticmethod
    def get_legal_terminology_enhancement_prompt(
        practice_area: PracticeArea,
        custom_vocabulary: Optional[List[str]] = None
    ) -> str:
        """
        Generate a prompt for enhancing transcription with legal terminology.
        
        Args:
            practice_area: The legal practice area
            custom_vocabulary: Optional custom legal terms
            
        Returns:
            Formatted prompt for GPT
        """
        base_prompt = f"""You are an expert legal transcription editor specializing in {practice_area.value.replace('_', ' ')}.

Your task is to review and enhance the raw transcription by:
1. Correcting legal terminology and jargon specific to {practice_area.value.replace('_', ' ')}
2. Properly formatting case names, statutes, and legal citations
3. Ensuring consistent capitalization of legal entities and proper nouns
4. Maintaining the exact meaning and intent of the original speech
5. Preserving all timestamps and speaker labels

CRITICAL RULES:
- Do NOT add information that wasn't in the original transcription
- Do NOT remove or summarize any content
- Do NOT change the meaning or intent of any statement
- Only correct obvious transcription errors and improve legal terminology accuracy

"""
        
        if custom_vocabulary:
            vocab_list = "\n".join(f"- {term}" for term in custom_vocabulary)
            base_prompt += f"""
CUSTOM LEGAL TERMS TO RECOGNIZE:
{vocab_list}

Ensure these terms are correctly identified and formatted in the transcription.
"""
        
        base_prompt += """
Return the enhanced transcription maintaining the original structure and timing information.
"""
        return base_prompt
    
    @staticmethod
    def get_speaker_identification_prompt(
        participants: List[str],
        meeting_type: MeetingType
    ) -> str:
        """
        Generate a prompt for improving speaker identification.
        
        Args:
            participants: List of participant names
            meeting_type: Type of meeting
            
        Returns:
            Formatted prompt for speaker diarization enhancement
        """
        participants_list = "\n".join(f"- {name}" for name in participants)
        
        return f"""You are analyzing a {meeting_type.value.replace('_', ' ')} transcript with the following participants:

{participants_list}

Your task is to:
1. Identify which speaker corresponds to which participant based on context clues
2. Assign consistent speaker labels throughout the transcript
3. Note any role indicators (e.g., "Your Honor" suggests a judge, "Counsel" suggests a lawyer)
4. Maintain speaker anonymity if names cannot be confidently determined

For each speaker segment, provide:
- Speaker ID (consistent throughout)
- Confidence level (high/medium/low)
- Suggested name if identifiable
- Role if determinable

Be conservative - only assign names when highly confident based on contextual evidence.
"""
    
    @staticmethod
    def get_timestamp_formatting_prompt() -> str:
        """Generate a prompt for consistent timestamp formatting."""
        return """Format all timestamps in the transcription using the following standard:

[HH:MM:SS] Speaker Name: Transcript text

Example:
[00:05:23] Attorney Johnson: We need to review the discovery documents by next Friday.
[00:05:45] Client Smith: I understand. I'll gather all the requested materials.

Ensure:
- Timestamps are in 24-hour format
- Timestamps are accurate to the second
- Each speaker turn starts on a new line
- Speaker names are consistent throughout
"""
    
    @staticmethod
    def get_context_aware_correction_prompt(practice_area: PracticeArea) -> str:
        """
        Generate a prompt for context-aware transcription corrections.
        
        Args:
            practice_area: The legal practice area
            
        Returns:
            Formatted prompt for contextual corrections
        """
        return f"""You are reviewing a legal transcription in the {practice_area.value.replace('_', ' ')} domain.

Apply context-aware corrections for common transcription errors:

LEGAL HOMOPHONES (correct these based on context):
- "cite/site/sight" → use "cite" for legal citations
- "council/counsel" → use "counsel" for legal advice/attorney
- "principal/principle" → use based on legal context
- "statue/statute" → use "statute" for laws
- "precedent/president" → use "precedent" for legal precedent
- "plaintiff/plaintive" → use "plaintiff" for the party
- "defendant/dependant" → use "defendant" for the accused party

COMMON LEGAL PHRASES:
- "pro say" → "pro se"
- "habius corpus" → "habeas corpus"
- "res ipsa loquitor" → "res ipsa loquitur"
- "summary judgement" → "summary judgment"
- "statue of limitations" → "statute of limitations"

FORMATTING:
- Case names should be italicized: Smith v. Jones
- Statutes should be properly formatted: 18 U.S.C. § 1001
- Legal terms in Latin should be italicized: in rem, ex parte

Make corrections only when contextually certain. Preserve the original if uncertain.
"""
    
    @staticmethod
    def get_quality_assessment_prompt() -> str:
        """Generate a prompt for assessing transcription quality."""
        return """Assess the quality of this transcription and provide:

1. OVERALL QUALITY SCORE (0-100):
   - Accuracy of legal terminology
   - Completeness of content
   - Clarity of speaker identification
   - Timestamp accuracy

2. IDENTIFIED ISSUES:
   - Sections with low confidence
   - Unclear audio segments
   - Potential misidentified speakers
   - Missing or unclear legal terms

3. RECOMMENDATIONS:
   - Sections requiring human review
   - Suggested improvements
   - Areas needing clarification

4. CONFIDENCE METRICS:
   - Percentage of high-confidence segments
   - Percentage requiring review
   - Overall reliability score

Provide your assessment in structured JSON format.
"""

"""
Premium prompt templates for summary generation.
Specialized prompts for different summary types and audiences.
"""
from typing import List, Optional
from models.enums import SummaryType, PracticeArea, MeetingType


class SummaryPrompts:
    """Professional prompt templates for summary generation."""
    
    @staticmethod
    def get_client_friendly_summary_prompt(
        meeting_type: MeetingType,
        practice_area: PracticeArea,
        participant_names: List[str]
    ) -> str:
        """
        Generate a prompt for creating a client-friendly summary.
        
        Args:
            meeting_type: Type of meeting
            practice_area: Legal practice area
            participant_names: List of participants
            
        Returns:
            Formatted prompt for client summary
        """
        return f"""You are creating a summary of a {meeting_type.value.replace('_', ' ')} in {practice_area.value.replace('_', ' ')} for the CLIENT.

AUDIENCE: Non-lawyer client who needs to understand what happened and what they need to do next.

TONE: Professional but accessible, avoid legal jargon, explain concepts in plain English.

STRUCTURE YOUR SUMMARY AS FOLLOWS:

## What We Discussed
Provide a clear, concise overview of the main topics covered in plain language. Avoid legal jargon.

## Key Points You Should Know
List the most important takeaways the client needs to understand. Use bullet points.

## What Happens Next
Clearly explain the next steps in the legal process in chronological order.

## What You Need to Do
List specific action items for the client with:
- Clear description of what they need to do
- Why it's important
- When it needs to be done
- What happens if they don't do it

## Important Dates
List all deadlines and important dates mentioned, with context for why each date matters.

## Questions to Consider
Suggest questions the client might want to ask based on the discussion.

GUIDELINES:
- Use simple, everyday language
- Explain legal terms when you must use them
- Be encouraging and supportive in tone
- Focus on practical implications for the client
- Highlight urgency appropriately without causing panic
- Make action items crystal clear

PARTICIPANTS:
{', '.join(participant_names)}

Generate a comprehensive but readable summary that empowers the client to understand their situation and take appropriate action.
"""
    
    @staticmethod
    def get_lawyer_professional_summary_prompt(
        meeting_type: MeetingType,
        practice_area: PracticeArea,
        case_id: Optional[str] = None
    ) -> str:
        """
        Generate a prompt for creating a lawyer-professional summary.
        
        Args:
            meeting_type: Type of meeting
            practice_area: Legal practice area
            case_id: Optional case identifier
            
        Returns:
            Formatted prompt for lawyer summary
        """
        case_context = f"\nCASE ID: {case_id}" if case_id else ""
        
        return f"""You are creating a professional legal summary of a {meeting_type.value.replace('_', ' ')} in {practice_area.value.replace('_', ' ')} for LEGAL PROFESSIONALS.{case_context}

AUDIENCE: Attorneys, paralegals, and legal staff who need detailed, actionable information.

TONE: Professional, precise, using appropriate legal terminology.

STRUCTURE YOUR SUMMARY AS FOLLOWS:

## Executive Summary
Concise overview of the meeting's purpose and outcomes (2-3 sentences).

## Discussion Points
Detailed breakdown of topics discussed, organized logically:
- Legal issues addressed
- Client concerns and questions
- Strategy discussions
- Evidence or documentation reviewed

## Legal Analysis
- Relevant statutes, regulations, or case law discussed
- Legal theories or arguments considered
- Potential risks or challenges identified
- Strengths and weaknesses of the case

## Decisions Made
Document all decisions with rationale:
- Strategic decisions
- Procedural decisions
- Settlement considerations
- Next steps agreed upon

## Action Items
Detailed task list with:
- Specific task description
- Assigned to (attorney/paralegal/client)
- Deadline
- Priority level
- Dependencies

## Deadlines & Court Dates
All time-sensitive matters with:
- Date and time
- Type of deadline (filing, hearing, discovery, etc.)
- Consequences of missing deadline
- Responsible party

## Billable Time Analysis
- Meeting duration
- Key topics by time allocation
- Suggested billing categories
- Notable time expenditures

## Follow-up Required
- Client communications needed
- Research to be conducted
- Documents to be drafted
- Third parties to contact

## Risk Assessment
- Identified risks or compliance issues
- Recommended mitigation strategies
- Urgency level

## Notes for File
Any additional context, observations, or considerations for the case file.

GUIDELINES:
- Use precise legal terminology
- Cite specific statutes, rules, or cases mentioned
- Be thorough and detailed
- Organize information for easy reference
- Flag urgent or high-priority items
- Include timestamps for critical statements

Generate a comprehensive professional summary suitable for the case file and team coordination.
"""
    
    @staticmethod
    def get_executive_summary_prompt(meeting_type: MeetingType) -> str:
        """
        Generate a prompt for creating an executive summary.
        
        Args:
            meeting_type: Type of meeting
            
        Returns:
            Formatted prompt for executive summary
        """
        return f"""You are creating an EXECUTIVE SUMMARY of a {meeting_type.value.replace('_', ' ')}.

AUDIENCE: Senior partners, managing attorneys, or executives who need high-level insights.

TONE: Concise, strategic, focused on key decisions and business implications.

STRUCTURE (MAXIMUM 1 PAGE):

## Overview
One paragraph summarizing the meeting's purpose and outcome.

## Key Decisions
3-5 most important decisions made, with brief rationale.

## Critical Action Items
Top 3-5 action items that require attention, with owners and deadlines.

## Risks & Opportunities
- Major risks identified
- Opportunities to pursue
- Recommended strategic direction

## Resource Requirements
- Budget implications
- Staffing needs
- Timeline considerations

## Immediate Next Steps
What needs to happen in the next 24-48 hours.

GUIDELINES:
- Maximum 300 words total
- Focus on strategic implications
- Highlight only the most critical information
- Use bullet points for scannability
- Emphasize business impact
- Flag anything requiring executive decision or approval

Generate a concise, high-impact summary for executive review.
"""
    
    @staticmethod
    def get_action_items_extraction_prompt() -> str:
        """Generate a prompt specifically for extracting action items."""
        return """Extract ALL action items from this meeting transcript.

For each action item, identify:

1. DESCRIPTION: What needs to be done (be specific and actionable)
2. ASSIGNEE: Who is responsible (name or role)
3. DEADLINE: When it's due (extract exact date/time if mentioned, or relative timeframe)
4. PRIORITY: Assess urgency (Urgent/High/Medium/Low) based on:
   - Explicit urgency indicators in the conversation
   - Proximity of deadline
   - Legal consequences of delay
   - Dependencies on other tasks

5. CONTEXT: Why this is important (brief explanation)
6. DEPENDENCIES: What else must happen first
7. DELIVERABLE: What the completed task produces

CLASSIFICATION:
- Client action items (things the client must do)
- Attorney action items (legal work to be done)
- Paralegal/staff action items (administrative tasks)
- Third-party action items (requiring external parties)

EXTRACTION RULES:
- Include explicit action items ("I need you to...")
- Include implicit commitments ("I'll get that to you by...")
- Include conditional actions ("If X happens, then we need to...")
- Capture follow-up items ("Let's revisit this next week...")

FORMAT:
Return as structured JSON array with all fields populated.

Be thorough - missing an action item could have serious consequences.
"""
    
    @staticmethod
    def get_key_decisions_extraction_prompt() -> str:
        """Generate a prompt for extracting key decisions."""
        return """Extract all KEY DECISIONS made during this meeting.

A key decision is:
- A choice between alternatives
- A strategic direction selected
- An approach or methodology agreed upon
- A settlement position established
- A procedural decision made

For each decision, document:

1. THE DECISION: What was decided (clear, specific statement)
2. ALTERNATIVES CONSIDERED: What other options were discussed
3. RATIONALE: Why this decision was made
4. WHO DECIDED: Decision maker(s)
5. IMPLICATIONS: What this means going forward
6. REVERSIBILITY: Can this be changed later? How easily?
7. TIMESTAMP: When in the meeting this was decided

CATEGORIES:
- Strategic decisions (case strategy, approach)
- Procedural decisions (how to proceed, what to file)
- Settlement decisions (offers, counteroffers, positions)
- Resource decisions (budget, staffing, timeline)
- Client decisions (what the client chose to do)

CRITICAL: Distinguish between:
- Firm decisions (agreed and final)
- Tentative decisions (subject to further review)
- Recommendations (suggested but not yet decided)

Return as structured JSON with clear categorization.
"""
    
    @staticmethod
    def get_risk_assessment_prompt(practice_area: PracticeArea) -> str:
        """
        Generate a prompt for identifying risks and compliance issues.
        
        Args:
            practice_area: Legal practice area
            
        Returns:
            Formatted prompt for risk assessment
        """
        return f"""Analyze this {practice_area.value.replace('_', ' ')} meeting transcript for RISKS and COMPLIANCE ISSUES.

IDENTIFY:

1. LEGAL RISKS:
   - Statute of limitations concerns
   - Missed deadlines or time-sensitive matters
   - Potential malpractice issues
   - Conflicts of interest
   - Privilege concerns
   - Evidence preservation issues

2. CLIENT RISKS:
   - Unrealistic expectations
   - Lack of understanding of process
   - Potential non-compliance with requirements
   - Financial constraints affecting case
   - Communication challenges

3. CASE RISKS:
   - Weaknesses in legal position
   - Evidentiary challenges
   - Adverse precedent
   - Opposing party strengths
   - Procedural vulnerabilities

4. COMPLIANCE ISSUES:
   - Regulatory requirements mentioned
   - Court rules or deadlines
   - Professional responsibility concerns
   - Documentation requirements
   - Disclosure obligations

For each risk identified, provide:
- SEVERITY: Critical/High/Medium/Low
- LIKELIHOOD: Probable/Possible/Unlikely
- IMPACT: What could happen if not addressed
- MITIGATION: Recommended action to address
- URGENCY: Immediate/Soon/Monitor
- RESPONSIBLE PARTY: Who should handle this

FLAG IMMEDIATELY:
- Any statute of limitations issues
- Imminent court deadlines
- Potential malpractice concerns
- Ethical violations discussed

Return as structured JSON with risk scoring and prioritization.
"""

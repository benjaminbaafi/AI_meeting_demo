"""
Premium prompt templates for action item extraction and management.
Specialized prompts for identifying, categorizing, and prioritizing action items.
"""
from typing import List, Optional
from models.enums import PracticeArea


class ActionItemPrompts:
    """Professional prompt templates for action item extraction."""
    
    @staticmethod
    def get_comprehensive_extraction_prompt(practice_area: PracticeArea) -> str:
        """
        Generate a comprehensive prompt for extracting all action items.
        
        Args:
            practice_area: Legal practice area for context
            
        Returns:
            Formatted prompt for action item extraction
        """
        return f"""You are an expert legal project manager analyzing a {practice_area.value.replace('_', ' ')} meeting transcript.

EXTRACT ALL ACTION ITEMS with meticulous attention to detail.

ACTION ITEM TYPES TO IDENTIFY:

1. EXPLICIT COMMITMENTS:
   - "I will [do something] by [date]"
   - "You need to [do something]"
   - "We should [do something]"

2. IMPLICIT COMMITMENTS:
   - Agreements to follow up
   - Promises to provide information
   - Scheduled next steps

3. CONDITIONAL ACTIONS:
   - "If X happens, then we need to Y"
   - Contingency plans
   - Alternative scenarios

4. RECURRING TASKS:
   - Regular check-ins
   - Periodic updates
   - Ongoing monitoring

For EACH action item, extract:

**REQUIRED FIELDS:**
- **Task Description**: Clear, specific, actionable statement (start with verb)
- **Assignee**: Person or role responsible (Attorney/Client/Paralegal/Other)
- **Deadline**: Specific date/time or relative timeframe
- **Priority**: Urgent/High/Medium/Low
- **Category**: Legal Work/Client Task/Administrative/Communication/Research/Filing

**CONTEXTUAL FIELDS:**
- **Why Important**: Business or legal reason for this task
- **Consequences**: What happens if not completed
- **Dependencies**: What must be done first
- **Deliverable**: Expected output or result
- **Estimated Effort**: Time/complexity estimate
- **Notes**: Any additional context

**PRIORITY ASSESSMENT CRITERIA:**

URGENT (do immediately):
- Court deadlines within 48 hours
- Statute of limitations concerns
- Emergency filings
- Time-sensitive client needs

HIGH (this week):
- Court deadlines within 2 weeks
- Critical case development
- Important client deliverables
- Significant strategic tasks

MEDIUM (this month):
- Standard deadlines
- Routine legal work
- Regular client updates
- Administrative tasks

LOW (as time permits):
- Nice-to-have items
- Long-term planning
- Optional improvements

**SPECIAL ATTENTION TO:**
- Court filing deadlines (always URGENT or HIGH)
- Discovery deadlines
- Client document requests
- Opposing counsel commitments
- Third-party dependencies

**OUTPUT FORMAT:**
Return as JSON array with all fields. Group by assignee and priority.

**QUALITY CHECKS:**
- Ensure no action item is missed
- Verify all deadlines are captured
- Confirm assignees are clear
- Validate priority levels are appropriate

Be exhaustive - missing an action item could have serious legal consequences.
"""
    
    @staticmethod
    def get_deadline_extraction_prompt() -> str:
        """Generate a prompt specifically for extracting deadlines."""
        return """Extract ALL DEADLINES and TIME-SENSITIVE MATTERS from this meeting transcript.

TYPES OF DEADLINES TO IDENTIFY:

1. COURT DEADLINES:
   - Filing deadlines
   - Hearing dates
   - Trial dates
   - Discovery cutoffs
   - Motion deadlines

2. CONTRACTUAL DEADLINES:
   - Agreement expiration dates
   - Option periods
   - Notice requirements
   - Performance deadlines

3. STATUTORY DEADLINES:
   - Statute of limitations
   - Regulatory filing deadlines
   - Appeal periods
   - Statutory notice periods

4. INTERNAL DEADLINES:
   - Client deliverables
   - Team commitments
   - Follow-up dates
   - Review dates

For EACH deadline, provide:

- **Date/Time**: Exact deadline (or best estimate)
- **Type**: Court/Contractual/Statutory/Internal
- **Description**: What is due
- **Responsible Party**: Who must meet this deadline
- **Consequences**: What happens if missed
- **Buffer Needed**: Recommended advance completion time
- **Reminder Schedule**: When to send reminders
- **Jurisdiction**: If applicable (different courts have different rules)

**CRITICAL CALCULATIONS:**
- Count backward from court deadlines to account for:
  - Service requirements
  - Filing time (end of business day vs midnight)
  - Weekends and holidays
  - Mail time if applicable

**PRIORITY FLAGGING:**
- 🚨 CRITICAL: Statute of limitations, jurisdictional deadlines
- ⚠️ URGENT: Court deadlines within 2 weeks
- ⏰ IMPORTANT: All other firm deadlines
- 📅 ROUTINE: Internal target dates

Return as JSON array sorted by date (earliest first) with visual priority indicators.
"""
    
    @staticmethod
    def get_assignee_identification_prompt(participants: List[str]) -> str:
        """
        Generate a prompt for identifying task assignees.
        
        Args:
            participants: List of meeting participants
            
        Returns:
            Formatted prompt for assignee identification
        """
        participants_list = "\n".join(f"- {name}" for name in participants)
        
        return f"""Identify WHO is responsible for each action item in this meeting.

MEETING PARTICIPANTS:
{participants_list}

ASSIGNMENT INDICATORS:

1. EXPLICIT ASSIGNMENTS:
   - "John, you need to..."
   - "I'll handle the..."
   - "Can you take care of...?"

2. IMPLICIT ASSIGNMENTS (by role):
   - Attorneys typically handle: legal research, filings, court appearances
   - Clients typically handle: document gathering, decision-making, payments
   - Paralegals typically handle: administrative tasks, scheduling, document prep
   - Experts typically handle: analysis, reports, testimony prep

3. SHARED RESPONSIBILITIES:
   - Identify when multiple people are responsible
   - Note primary vs supporting roles
   - Clarify coordination requirements

For EACH action item, determine:

- **Primary Assignee**: Main person responsible
- **Supporting Assignees**: Others who need to help
- **Confidence Level**: High/Medium/Low (how certain is the assignment)
- **Assignment Source**: Explicit statement / Implied by role / Inferred from context
- **Needs Clarification**: Flag if assignment is ambiguous

**AMBIGUITY HANDLING:**
If assignee is unclear:
- Note it as "NEEDS CLARIFICATION"
- Suggest most likely assignee based on context
- Recommend follow-up to confirm

**ROLE-BASED DEFAULTS:**
When not explicitly stated, assign based on typical responsibilities:
- Legal research → Attorney
- Court filings → Attorney (with paralegal support)
- Document collection → Client
- Scheduling → Paralegal
- Expert analysis → Expert witness

Return as JSON with clear assignment tracking and confidence scoring.
"""
    
    @staticmethod
    def get_dependency_mapping_prompt() -> str:
        """Generate a prompt for mapping action item dependencies."""
        return """Analyze the DEPENDENCIES between action items in this meeting.

DEPENDENCY TYPES:

1. SEQUENTIAL DEPENDENCIES:
   - Task B cannot start until Task A is complete
   - Example: Can't file motion until research is done

2. INFORMATIONAL DEPENDENCIES:
   - Task B needs information from Task A
   - Example: Can't draft contract until client provides terms

3. RESOURCE DEPENDENCIES:
   - Tasks competing for same resources (person, budget, time)
   - Example: Same attorney handling multiple urgent matters

4. CONDITIONAL DEPENDENCIES:
   - Task B only happens if Task A has certain outcome
   - Example: File appeal only if motion is denied

For EACH action item, identify:

- **Depends On**: What must be completed first (list task IDs)
- **Blocks**: What is waiting for this task (list task IDs)
- **Dependency Type**: Sequential/Informational/Resource/Conditional
- **Criticality**: Is this on the critical path?
- **Risk**: What happens if dependency is delayed

**CRITICAL PATH ANALYSIS:**
- Identify the longest sequence of dependent tasks
- Calculate total time needed
- Flag bottlenecks
- Suggest parallelization opportunities

**DEPENDENCY VISUALIZATION:**
Create a dependency graph showing:
- Task nodes
- Dependency arrows
- Critical path highlighted
- Parallel tracks identified

**RISK ASSESSMENT:**
- Single points of failure
- Resource conflicts
- Deadline compression risks
- Dependency chain vulnerabilities

Return as JSON with:
- Dependency matrix
- Critical path identification
- Risk flags
- Recommended sequencing
"""
    
    @staticmethod
    def get_follow_up_tracking_prompt() -> str:
        """Generate a prompt for tracking follow-up requirements."""
        return """Identify all FOLLOW-UP REQUIREMENTS from this meeting.

FOLLOW-UP CATEGORIES:

1. CLIENT FOLLOW-UPS:
   - Information requests
   - Decision points
   - Status updates
   - Document requests

2. OPPOSING PARTY FOLLOW-UPS:
   - Responses expected
   - Negotiations to continue
   - Information exchanges

3. COURT FOLLOW-UPS:
   - Hearing results to check
   - Filing confirmations
   - Clerk communications

4. INTERNAL FOLLOW-UPS:
   - Team check-ins
   - Progress reviews
   - Strategy sessions

5. THIRD-PARTY FOLLOW-UPS:
   - Expert consultations
   - Vendor deliverables
   - External research

For EACH follow-up, specify:

- **What**: What needs to be followed up on
- **Who**: Who is responsible for following up
- **When**: When to follow up (specific date or trigger)
- **How**: Method of follow-up (email, call, meeting, etc.)
- **Expected Response**: What we're waiting for
- **Escalation**: What to do if no response
- **Reminder Schedule**: When to send reminders

**TRIGGER-BASED FOLLOW-UPS:**
Identify follow-ups triggered by events:
- "After we receive the discovery..."
- "Once the court rules..."
- "When the client decides..."

**RECURRING FOLLOW-UPS:**
Identify ongoing monitoring needs:
- Weekly status checks
- Monthly reviews
- Quarterly assessments

**FOLLOW-UP TEMPLATES:**
Suggest communication templates for:
- Client update emails
- Opposing counsel requests
- Court inquiries
- Expert consultations

Return as JSON with follow-up schedule and tracking mechanisms.
"""

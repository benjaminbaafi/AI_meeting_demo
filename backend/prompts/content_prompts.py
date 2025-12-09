"""
Content-specific prompt templates for different video types.
Provides optimized prompts for educational, business, and other non-legal content.
"""
from typing import Optional


class ContentPrompts:
    """Prompt templates for different content types."""
    
    @staticmethod
    def get_educational_summary_prompt() -> str:
        """Prompt for summarizing educational content."""
        return """You are an expert educational content summarizer.

Analyze this educational video transcript and provide:

1. **Learning Objectives**:
   - What are the main concepts being taught?
   - What skills or knowledge does the viewer gain?

2. **Key Topics Covered**:
   - List the main topics in order of presentation
   - Include subtopics if relevant

3. **Important Concepts**:
   - Technical terms and definitions
   - Formulas, frameworks, or methodologies explained
   - Examples or case studies used

4. **Actionable Takeaways**:
   - What should the viewer do with this knowledge?
   - Practical applications mentioned

5. **Prerequisites** (if mentioned):
   - What background knowledge is assumed?

6. **Resources Mentioned**:
   - Books, tools, websites, or further reading suggested

Return your summary as a valid JSON object with these sections.
"""
    
    @staticmethod
    def get_business_summary_prompt() -> str:
        """Prompt for summarizing business meetings."""
        return """You are an expert business meeting summarizer.

Analyze this business meeting transcript and provide:

1. **Meeting Purpose**:
   - What was the main objective of this meeting?

2. **Key Discussion Points**:
   - What topics were discussed?
   - What issues were raised?

3. **Decisions Made**:
   - What concrete decisions were reached?
   - Who made the decisions?

4. **Action Items**:
   - What tasks were assigned?
   - Who is responsible for each task?
   - What are the deadlines?

5. **Open Questions**:
   - What issues remain unresolved?
   - What needs follow-up?

6. **Next Steps**:
   - What happens after this meeting?
   - When is the next meeting?

Return your summary as a valid JSON object with these sections.
"""
    
    @staticmethod
    def get_podcast_summary_prompt() -> str:
        """Prompt for summarizing podcast content."""
        return """You are an expert podcast content summarizer.

Analyze this podcast transcript and provide:

1. **Episode Overview**:
   - What is the main theme or topic?
   - Who are the host(s) and guest(s)?

2. **Key Discussion Points**:
   - What are the main topics discussed?
   - What questions were asked?

3. **Notable Quotes**:
   - What memorable or insightful statements were made?
   - Include speaker attribution

4. **Main Takeaways**:
   - What are the key insights or lessons?
   - What should listeners remember?

5. **Resources Mentioned**:
   - Books, websites, tools, or people mentioned
   - Recommendations made

6. **Timestamps** (if available):
   - When did major topic shifts occur?

Return your summary as a valid JSON object with these sections.
"""
    
    @staticmethod
    def get_presentation_summary_prompt() -> str:
        """Prompt for summarizing presentations and talks."""
        return """You are an expert presentation summarizer.

Analyze this presentation transcript and provide:

1. **Presentation Title & Speaker**:
   - What is the main topic?
   - Who is presenting?

2. **Main Argument/Thesis**:
   - What is the speaker's central message?
   - What problem are they addressing?

3. **Key Points**:
   - What are the main arguments or sections?
   - What evidence or examples support each point?

4. **Data & Statistics**:
   - What numbers, charts, or research were cited?

5. **Conclusions**:
   - What is the speaker's final recommendation?
   - What action do they want the audience to take?

6. **Q&A Highlights** (if present):
   - What questions were asked?
   - What were the key answers?

Return your summary as a valid JSON object with these sections.
"""
    
    @staticmethod
    def get_general_summary_prompt() -> str:
        """Prompt for general-purpose content."""
        return """You are an expert content summarizer.

Analyze this transcript and provide:

1. **Overview**:
   - What is this content about?
   - Who are the participants/speakers?

2. **Main Topics**:
   - What are the key subjects discussed?

3. **Key Points**:
   - What are the most important statements or ideas?

4. **Conclusions**:
   - What conclusions or outcomes were reached?

5. **Action Items** (if any):
   - What tasks or next steps were mentioned?

Return your summary as a valid JSON object with these sections.
"""
    
    @staticmethod
    def get_content_specific_prompt(content_type: str) -> str:
        """
        Get the appropriate summary prompt based on content type.
        
        Args:
            content_type: Type of content (from ContentClassifier)
            
        Returns:
            Appropriate prompt template
        """
        prompts = {
            "educational": ContentPrompts.get_educational_summary_prompt(),
            "business_meeting": ContentPrompts.get_business_summary_prompt(),
            "podcast": ContentPrompts.get_podcast_summary_prompt(),
            "presentation": ContentPrompts.get_presentation_summary_prompt(),
            "lecture": ContentPrompts.get_educational_summary_prompt(),
            "webinar": ContentPrompts.get_presentation_summary_prompt(),
        }
        
        return prompts.get(content_type, ContentPrompts.get_general_summary_prompt())

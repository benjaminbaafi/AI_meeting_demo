"""Prompt templates package."""
from prompts.transcription_prompts import TranscriptionPrompts
from prompts.summary_prompts import SummaryPrompts
from prompts.action_item_prompts import ActionItemPrompts

__all__ = [
    "TranscriptionPrompts",
    "SummaryPrompts",
    "ActionItemPrompts",
]

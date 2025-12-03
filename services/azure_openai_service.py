"""
Azure OpenAI Service integration.
Handles communication with Azure OpenAI API for Whisper and GPT models.
"""
import asyncio
import json
from typing import Optional, List, Dict, Any, AsyncGenerator
from openai import AsyncAzureOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import logging

from config import settings


logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """
    Service for interacting with Azure OpenAI API.
    Implements retry logic, error handling, and rate limiting.
    """
    
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.whisper_deployment = settings.azure_openai_whisper_deployment
        self.gpt_deployment = settings.azure_openai_gpt_deployment
        
        logger.info("Azure OpenAI Service initialized")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Azure OpenAI Whisper.
        
        Args:
            audio_file_path: Path to audio file
            language: Optional language code (e.g., 'en')
            prompt: Optional prompt to guide transcription
            
        Returns:
            Transcription result with text and metadata
            
        Raises:
            Exception: If transcription fails after retries
        """
        try:
            logger.info("Starting transcription for: %s", audio_file_path)
            
            with open(audio_file_path, "rb") as audio_file:
                response = await self.client.audio.transcriptions.create(
                    model=self.whisper_deployment,
                    file=audio_file,
                    language=language,
                    prompt=prompt,
                    response_format="verbose_json",  # Get detailed response with timestamps
                    timestamp_granularities=["segment"],
                )
            
            result = {
                "text": response.text,
                "language": response.language,
                "duration": response.duration,
                "segments": [
                    {
                        "id": getattr(seg, 'id', idx),
                        "start": getattr(seg, 'start', seg.get('start', 0)),
                        "end": getattr(seg, 'end', seg.get('end', 0)),
                        "text": getattr(seg, 'text', seg.get('text', '')),
                        "tokens": getattr(seg, 'tokens', seg.get('tokens', [])),
                        "temperature": getattr(seg, 'temperature', seg.get('temperature', 0)),
                        "avg_logprob": getattr(seg, 'avg_logprob', seg.get('avg_logprob', 0)),
                        "compression_ratio": getattr(seg, 'compression_ratio', seg.get('compression_ratio', 0)),
                        "no_speech_prob": getattr(seg, 'no_speech_prob', seg.get('no_speech_prob', 0)),
                    }
                    for idx, seg in enumerate(response.segments)
                ],
            }
            
            logger.info("Transcription completed: %d characters", len(result["text"]))
            return result
            
        except Exception:
            logger.exception("Transcription failed for %s", audio_file_path)
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True,
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Generate completion using Azure OpenAI GPT model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            response_format: Optional response format (e.g., {"type": "json_object"})
            
        Returns:
            Generated text completion
            
        Raises:
            Exception: If completion fails after retries
        """
        try:
            logger.info("Generating completion with %d messages", len(messages))
            
            kwargs = {
                "model": self.gpt_deployment,
                "messages": messages,
                "temperature": temperature,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            if response_format:
                kwargs["response_format"] = response_format
            
            response = await self.client.chat.completions.create(**kwargs)
            
            completion = response.choices[0].message.content
            
            logger.info("Completion generated: %d characters", len(completion))
            return completion
            
        except Exception:
            logger.exception("Completion generation failed")
            raise
    
    async def generate_completion_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming completion using Azure OpenAI GPT model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Chunks of generated text
            
        Raises:
            Exception: If streaming fails
        """
        try:
            logger.info(
                "Starting streaming completion with %d messages", len(messages)
            )
            
            kwargs = {
                "model": self.gpt_deployment,
                "messages": messages,
                "temperature": temperature,
                "stream": True,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            
            stream = await self.client.chat.completions.create(**kwargs)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
            
            logger.info("Streaming completion finished")
            
        except Exception:
            logger.exception("Streaming completion failed")
            raise
    
    async def generate_json_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate JSON-formatted completion.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            
        Returns:
            Parsed JSON response
            
        Raises:
            Exception: If completion fails or JSON parsing fails
        """
        try:
            completion = await self.generate_completion(
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            
            return json.loads(completion)
            
        except json.JSONDecodeError:
            logger.exception("Failed to parse JSON response")
            raise ValueError("Invalid JSON response")
    
    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
            
        Note:
            This is a rough estimate. For accurate counting, use tiktoken library.
        """
        # Rough estimate: ~4 characters per token for English
        return len(text) // 4
    
    async def close(self):
        """Close the Azure OpenAI client."""
        await self.client.close()
        logger.info("Azure OpenAI Service closed")


# Global service instance
_azure_openai_service: Optional[AzureOpenAIService] = None


def get_azure_openai_service() -> AzureOpenAIService:
    """
    Get or create the global Azure OpenAI service instance.
    
    Returns:
        AzureOpenAIService instance
    """
    global _azure_openai_service
    if _azure_openai_service is None:
        _azure_openai_service = AzureOpenAIService()
    return _azure_openai_service

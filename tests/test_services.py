"""
Tests for transcription and summarization services.
Validates AI processing logic and data transformations.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from models.enums import PracticeArea, MeetingType, SummaryType
from services.transcription_service import TranscriptionService
from services.summarization_service import SummarizationService


class TestTranscriptionService:
    """Test suite for transcription service."""
    
    @pytest.mark.asyncio
    @patch("services.transcription_service.get_azure_openai_service")
    @patch("services.transcription_service.AudioProcessor")
    async def test_transcribe_video_success(
        self,
        mock_audio_processor,
        mock_azure_service,
        sample_job_data,
        temp_dir,
    ):
        """Test successful video transcription."""
        # Setup mocks
        mock_azure = Mock()
        mock_azure.transcribe_audio = AsyncMock(return_value={
            "text": "This is a test transcription.",
            "language": "en",
            "duration": 120.0,
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 5.0,
                    "text": "This is a test.",
                    "tokens": [1, 2, 3],
                    "temperature": 0.0,
                    "avg_logprob": -0.5,
                    "compression_ratio": 1.2,
                    "no_speech_prob": 0.1,
                }
            ],
        })
        mock_azure.generate_completion = AsyncMock(
            return_value="Enhanced transcription text"
        )
        mock_azure_service.return_value = mock_azure
        
        # Setup audio processor mock
        mock_processor = Mock()
        mock_processor.extract_audio_from_video = AsyncMock(
            return_value=(temp_dir / "audio.wav", 120.0)
        )
        mock_processor.normalize_audio = AsyncMock(
            return_value=temp_dir / "normalized.wav"
        )
        mock_audio_processor.return_value = mock_processor
        
        # Create test video file
        video_path = temp_dir / "test.mp4"
        video_path.write_bytes(b"fake video")
        
        # Run transcription
        service = TranscriptionService()
        result = await service.transcribe_video(
            job_id="test_job",
            video_path=video_path,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
            meeting_type=MeetingType.CONSULTATION,
            participants=["Attorney", "Client"],
        )
        
        # Assertions
        assert result.job_id == "test_job"
        assert result.status == "completed"
        assert result.duration_seconds == 120.0
        assert len(result.segments) > 0
        assert result.word_count > 0
    
    def test_extract_unique_speakers(self):
        """Test extracting unique speakers from segments."""
        from models.schemas import TranscriptSegment, Speaker
        from models.enums import SpeakerRole
        
        segments = [
            TranscriptSegment(
                start_time=0.0,
                end_time=5.0,
                speaker=Speaker(speaker_id="speaker_1", name="John", role=SpeakerRole.LAWYER),
                text="Hello",
                confidence=0.95,
            ),
            TranscriptSegment(
                start_time=5.0,
                end_time=10.0,
                speaker=Speaker(speaker_id="speaker_2", name="Jane", role=SpeakerRole.CLIENT),
                text="Hi",
                confidence=0.92,
            ),
            TranscriptSegment(
                start_time=10.0,
                end_time=15.0,
                speaker=Speaker(speaker_id="speaker_1", name="John", role=SpeakerRole.LAWYER),
                text="How are you?",
                confidence=0.94,
            ),
        ]
        
        service = TranscriptionService()
        unique_speakers = service._extract_unique_speakers(segments)
        
        assert len(unique_speakers) == 2
        speaker_ids = [s.speaker_id for s in unique_speakers]
        assert "speaker_1" in speaker_ids
        assert "speaker_2" in speaker_ids


class TestSummarizationService:
    """Test suite for summarization service."""
    
    @pytest.mark.asyncio
    @patch("services.summarization_service.get_azure_openai_service")
    async def test_generate_client_summary(
        self,
        mock_azure_service,
        sample_transcript,
    ):
        """Test generating client-friendly summary."""
        # Setup mock
        mock_azure = Mock()
        mock_azure.generate_completion = AsyncMock(
            return_value="Client-friendly summary of the meeting."
        )
        mock_azure.generate_json_completion = AsyncMock(
            return_value={
                "action_items": [
                    {
                        "description": "Provide documents by Friday",
                        "assignee": "Client",
                        "priority": "high",
                    }
                ],
                "decisions": [],
                "risks": [],
            }
        )
        mock_azure_service.return_value = mock_azure
        
        # Create mock transcription
        from models.schemas import TranscriptionResponse
        from models.enums import ProcessingStatus
        from datetime import datetime
        
        transcription = TranscriptionResponse(
            job_id="test_job",
            status=ProcessingStatus.COMPLETED,
            segments=[],
            full_text=sample_transcript,
            speakers=[],
            duration_seconds=180.0,
            word_count=len(sample_transcript.split()),
            average_confidence=0.95,
            processing_time_seconds=10.0,
            created_at=datetime.utcnow(),
        )
        
        # Generate summary
        service = SummarizationService()
        result = await service.generate_summary(
            job_id="test_job",
            transcription=transcription,
            summary_type=SummaryType.CLIENT_FRIENDLY,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
            meeting_type=MeetingType.CONSULTATION,
            participants=["Attorney Johnson", "Client Smith"],
        )
        
        # Assertions
        assert result.job_id == "test_job"
        assert result.status == "completed"
        assert result.summary_type == SummaryType.CLIENT_FRIENDLY
        assert len(result.detailed_summary) > 0
        assert len(result.action_items) > 0
    
    @pytest.mark.asyncio
    @patch("services.summarization_service.get_azure_openai_service")
    async def test_extract_action_items(
        self,
        mock_azure_service,
        sample_transcript,
    ):
        """Test action item extraction."""
        # Setup mock
        mock_azure = Mock()
        mock_azure.generate_json_completion = AsyncMock(
            return_value={
                "action_items": [
                    {
                        "description": "Research non-compete enforceability",
                        "assignee": "Attorney Johnson",
                        "deadline": None,
                        "priority": "high",
                        "notes": "Focus on California law",
                    },
                    {
                        "description": "Provide job description and performance reviews",
                        "assignee": "Client Smith",
                        "deadline": "2024-12-15T00:00:00",
                        "priority": "urgent",
                        "notes": "Due by next Friday",
                    },
                ]
            }
        )
        mock_azure_service.return_value = mock_azure
        
        service = SummarizationService()
        action_items = await service._extract_action_items(
            transcript=sample_transcript,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
            participants=["Attorney Johnson", "Client Smith"],
        )
        
        # Assertions
        assert len(action_items) == 2
        assert action_items[0].description == "Research non-compete enforceability"
        assert action_items[0].assignee == "Attorney Johnson"
        assert action_items[1].priority.value == "urgent"
    
    @pytest.mark.asyncio
    @patch("services.summarization_service.get_azure_openai_service")
    async def test_identify_risks(
        self,
        mock_azure_service,
        sample_transcript,
    ):
        """Test risk identification."""
        # Setup mock
        mock_azure = Mock()
        mock_azure.generate_json_completion = AsyncMock(
            return_value={
                "risks": [
                    {
                        "description": "Broad non-compete clause may be unenforceable",
                        "severity": "medium",
                        "recommendation": "Conduct thorough legal research",
                    }
                ]
            }
        )
        mock_azure_service.return_value = mock_azure
        
        service = SummarizationService()
        risks = await service._identify_risks(
            transcript=sample_transcript,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
        )
        
        # Assertions
        assert len(risks) > 0
        assert risks[0].severity == "medium"
        assert "non-compete" in risks[0].description.lower()


class TestPromptGeneration:
    """Test suite for prompt generation."""
    
    def test_client_summary_prompt(self):
        """Test client-friendly summary prompt generation."""
        from prompts.summary_prompts import SummaryPrompts
        
        prompt = SummaryPrompts.get_client_friendly_summary_prompt(
            meeting_type=MeetingType.CONSULTATION,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
            participant_names=["Attorney", "Client"],
        )
        
        assert "client" in prompt.lower()
        assert "plain language" in prompt.lower()
        assert "employment law" in prompt.lower()
    
    def test_lawyer_summary_prompt(self):
        """Test lawyer-professional summary prompt generation."""
        from prompts.summary_prompts import SummaryPrompts
        
        prompt = SummaryPrompts.get_lawyer_professional_summary_prompt(
            meeting_type=MeetingType.DEPOSITION,
            practice_area=PracticeArea.LITIGATION,
            case_id="CASE-2024-001",
        )
        
        assert "legal professionals" in prompt.lower()
        assert "litigation" in prompt.lower()
        assert "CASE-2024-001" in prompt
    
    def test_action_item_extraction_prompt(self):
        """Test action item extraction prompt."""
        from prompts.action_item_prompts import ActionItemPrompts
        
        prompt = ActionItemPrompts.get_comprehensive_extraction_prompt(
            practice_area=PracticeArea.CORPORATE_LAW
        )
        
        assert "action item" in prompt.lower()
        assert "corporate law" in prompt.lower()
        assert "deadline" in prompt.lower()
        assert "priority" in prompt.lower()
    
    def test_legal_terminology_enhancement_prompt(self):
        """Test legal terminology enhancement prompt."""
        from prompts.transcription_prompts import TranscriptionPrompts
        
        prompt = TranscriptionPrompts.get_legal_terminology_enhancement_prompt(
            practice_area=PracticeArea.FAMILY_LAW,
            custom_vocabulary=["custody", "alimony", "visitation"],
        )
        
        assert "family law" in prompt.lower()
        assert "custody" in prompt
        assert "legal terminology" in prompt.lower()


class TestDataValidation:
    """Test suite for Pydantic model validation."""
    
    def test_video_upload_request_validation(self):
        """Test VideoUploadRequest validation."""
        from models.schemas import VideoUploadRequest
        from models.enums import MeetingType, PracticeArea
        
        # Valid request
        request = VideoUploadRequest(
            meeting_type=MeetingType.CONSULTATION,
            practice_area=PracticeArea.EMPLOYMENT_LAW,
            participants=["Attorney", "Client"],
        )
        
        assert request.meeting_type == MeetingType.CONSULTATION
        assert len(request.participants) == 2
    
    def test_transcript_segment_validation(self):
        """Test TranscriptSegment validation."""
        from models.schemas import TranscriptSegment, Speaker
        from models.enums import SpeakerRole
        import pytest
        
        # Valid segment
        segment = TranscriptSegment(
            start_time=0.0,
            end_time=5.0,
            speaker=Speaker(speaker_id="s1", role=SpeakerRole.LAWYER),
            text="Hello",
            confidence=0.95,
        )
        
        assert segment.start_time < segment.end_time
        
        # Invalid segment (end_time before start_time)
        with pytest.raises(ValueError):
            TranscriptSegment(
                start_time=10.0,
                end_time=5.0,  # Invalid
                speaker=Speaker(speaker_id="s1", role=SpeakerRole.LAWYER),
                text="Hello",
                confidence=0.95,
            )
    
    def test_action_item_validation(self):
        """Test ActionItem validation."""
        from models.schemas import ActionItem
        from models.enums import ActionItemPriority
        
        action_item = ActionItem(
            description="Complete legal research",
            assignee="Attorney Johnson",
            priority=ActionItemPriority.HIGH,
        )
        
        assert action_item.description == "Complete legal research"
        assert action_item.priority == ActionItemPriority.HIGH
        assert action_item.completed is False  # Default value

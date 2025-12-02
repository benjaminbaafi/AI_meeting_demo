"""
Pytest configuration and fixtures.
Provides reusable test fixtures for all tests.
"""
import pytest
import asyncio
from pathlib import Path
from typing import Generator
import tempfile
import shutil

from fastapi.testclient import TestClient
from app import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client() -> Generator:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_video_file(temp_dir: Path) -> Path:
    """Create a sample video file for testing."""
    video_path = temp_dir / "sample_meeting.mp4"
    
    # Create a minimal valid MP4 file (just for testing file handling)
    # In production tests, use actual video files
    video_path.write_bytes(b"fake video content for testing")
    
    return video_path


@pytest.fixture
def sample_audio_file(temp_dir: Path) -> Path:
    """Create a sample audio file for testing."""
    audio_path = temp_dir / "sample_audio.wav"
    audio_path.write_bytes(b"fake audio content for testing")
    return audio_path


@pytest.fixture
def sample_transcript() -> str:
    """Sample transcript text for testing."""
    return """
    [00:00:05] Attorney Johnson: Good morning, Mr. Smith. Thank you for meeting with me today.
    
    [00:00:10] Client Smith: Good morning. Thanks for seeing me on short notice.
    
    [00:00:15] Attorney Johnson: Of course. I understand you're facing some issues with your employment contract. Can you tell me more about that?
    
    [00:00:25] Client Smith: Yes, my employer is trying to enforce a non-compete clause that I believe is unreasonable. It would prevent me from working in my field for two years across the entire state.
    
    [00:00:40] Attorney Johnson: I see. That does sound quite broad. Let's review the contract together. Do you have a copy with you?
    
    [00:00:48] Client Smith: Yes, I brought it. Here it is.
    
    [00:00:52] Attorney Johnson: Thank you. Let me take a look... Okay, I can see the clause you're referring to. This is Section 7.2. In California, non-compete clauses are generally unenforceable, but there are some exceptions.
    
    [00:01:15] Client Smith: So does that mean I don't have to worry about it?
    
    [00:01:20] Attorney Johnson: Not necessarily. We need to analyze this carefully. I recommend we do three things: First, I'll research the specific enforceability of this clause under current California law. Second, we should gather documentation of your job responsibilities and the industry standards. Third, we may want to send a letter to your employer clarifying your position.
    
    [00:01:45] Client Smith: Okay, that sounds good. How long will this take?
    
    [00:01:50] Attorney Johnson: The research should take about a week. I'll need you to provide me with your job description, any performance reviews, and information about your new job offer by next Friday. Can you do that?
    
    [00:02:05] Client Smith: Yes, I can get those to you by Friday.
    
    [00:02:10] Attorney Johnson: Perfect. I'll have my paralegal send you a document request list today. We'll schedule a follow-up meeting for two weeks from now to discuss our strategy. In the meantime, don't sign anything or make any commitments to either employer without consulting me first.
    
    [00:02:30] Client Smith: Understood. I won't sign anything.
    
    [00:02:35] Attorney Johnson: Great. Do you have any other questions for me today?
    
    [00:02:40] Client Smith: No, I think that covers it. Thank you for your help.
    
    [00:02:45] Attorney Johnson: You're welcome. We'll get through this. Talk to you soon.
    """


@pytest.fixture
def mock_azure_openai_response():
    """Mock Azure OpenAI API response."""
    return {
        "text": "Sample transcription text",
        "language": "en",
        "duration": 180.5,
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 5.0,
                "text": "Hello, this is a test.",
                "tokens": [1, 2, 3],
                "temperature": 0.0,
                "avg_logprob": -0.5,
                "compression_ratio": 1.2,
                "no_speech_prob": 0.1,
            }
        ],
    }


@pytest.fixture
def sample_participants() -> list[str]:
    """Sample participant list."""
    return ["Attorney Johnson", "Client Smith"]


@pytest.fixture
def sample_job_data() -> dict:
    """Sample job data for testing."""
    from datetime import datetime
    from models.enums import ProcessingStatus, MeetingType, PracticeArea
    
    return {
        "job_id": "test_job_123",
        "status": ProcessingStatus.QUEUED,
        "filename": "test_meeting.mp4",
        "file_size_bytes": 1024000,
        "meeting_type": MeetingType.CONSULTATION,
        "practice_area": PracticeArea.EMPLOYMENT_LAW,
        "participants": ["Attorney Johnson", "Client Smith"],
        "case_id": "CASE-2024-001",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

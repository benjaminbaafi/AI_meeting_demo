"""
Tests for upload API endpoints.
Validates file upload, validation, and job creation.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from models.enums import MeetingType, PracticeArea


class TestUploadEndpoint:
    """Test suite for upload endpoint."""
    
    def test_upload_valid_video(self, client: TestClient):
        """Test uploading a valid video file."""
        # Create a fake video file
        video_content = b"fake video content" * 1000
        files = {"file": ("meeting.mp4", io.BytesIO(video_content), "video/mp4")}
        
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "Attorney Johnson, Client Smith",
            "case_id": "CASE-2024-001",
        }
        
        response = client.post("/api/v1/upload", files=files, data=data)
        
        # Assertions
        assert response.status_code == 200
        result = response.json()
        
        assert "job_id" in result
        assert result["status"] == "queued"
        assert result["filename"] == "meeting.mp4"
        assert result["file_size_bytes"] > 0
        assert "estimated_processing_time_seconds" in result
    
    def test_upload_invalid_format(self, client: TestClient):
        """Test uploading an invalid file format."""
        files = {"file": ("document.pdf", io.BytesIO(b"fake pdf"), "application/pdf")}
        
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "Attorney Johnson",
        }
        
        response = client.post("/api/v1/upload", files=files, data=data)
        
        # Should fail validation
        assert response.status_code == 400
        assert "validation failed" in response.json()["detail"]["message"].lower()
    
    def test_upload_empty_participants(self, client: TestClient):
        """Test uploading with empty participants list."""
        files = {"file": ("meeting.mp4", io.BytesIO(b"fake video"), "video/mp4")}
        
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "",  # Empty
        }
        
        response = client.post("/api/v1/upload", files=files, data=data)
        
        # Should fail validation
        assert response.status_code == 400
    
    def test_upload_too_large_file(self, client: TestClient):
        """Test uploading a file that exceeds size limit."""
        # Create a file larger than the limit (assuming 500MB limit)
        # For testing, we'll just check the validation logic
        large_content = b"x" * (600 * 1024 * 1024)  # 600MB
        files = {"file": ("large.mp4", io.BytesIO(large_content), "video/mp4")}
        
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "Attorney Johnson",
        }
        
        response = client.post("/api/v1/upload", files=files, data=data)
        
        # Should fail validation
        assert response.status_code == 400
    
    def test_get_job_status(self, client: TestClient, sample_job_data: dict):
        """Test retrieving job status."""
        # First upload a file to create a job
        files = {"file": ("meeting.mp4", io.BytesIO(b"fake video"), "video/mp4")}
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "Attorney Johnson",
        }
        
        upload_response = client.post("/api/v1/upload", files=files, data=data)
        job_id = upload_response.json()["job_id"]
        
        # Get status
        status_response = client.get(f"/api/v1/upload/{job_id}/status")
        
        assert status_response.status_code == 200
        status = status_response.json()
        
        assert status["job_id"] == job_id
        assert "status" in status
        assert "progress_percentage" in status
        assert status["progress_percentage"] >= 0
        assert status["progress_percentage"] <= 100
    
    def test_get_nonexistent_job_status(self, client: TestClient):
        """Test retrieving status for non-existent job."""
        response = client.get("/api/v1/upload/nonexistent_job_id/status")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_cancel_job(self, client: TestClient):
        """Test cancelling a job."""
        # Upload a file
        files = {"file": ("meeting.mp4", io.BytesIO(b"fake video"), "video/mp4")}
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.EMPLOYMENT_LAW.value,
            "participants": "Attorney Johnson",
        }
        
        upload_response = client.post("/api/v1/upload", files=files, data=data)
        job_id = upload_response.json()["job_id"]
        
        # Cancel the job
        cancel_response = client.delete(f"/api/v1/upload/{job_id}")
        
        assert cancel_response.status_code == 200
        assert "cancelled successfully" in cancel_response.json()["message"].lower()
    
    def test_upload_with_case_id(self, client: TestClient):
        """Test uploading with a case ID."""
        files = {"file": ("meeting.mp4", io.BytesIO(b"fake video"), "video/mp4")}
        data = {
            "meeting_type": MeetingType.CONSULTATION.value,
            "practice_area": PracticeArea.LITIGATION.value,
            "participants": "Attorney Smith, Client Jones",
            "case_id": "LIT-2024-12345",
            "notes": "Initial consultation regarding contract dispute",
        }
        
        response = client.post("/api/v1/upload", files=files, data=data)
        
        assert response.status_code == 200
        result = response.json()
        assert "job_id" in result


class TestFileValidation:
    """Test suite for file validation logic."""
    
    def test_validate_video_extension(self):
        """Test video file extension validation."""
        from utils.validators import VideoValidator
        
        # Valid extensions
        for ext in ["mp4", "mov", "avi", "webm"]:
            is_valid, file_type, msg = VideoValidator.validate_file_extension(f"video.{ext}")
            assert is_valid is True
            assert file_type == "video"
    
    def test_validate_audio_extension(self):
        """Test audio file extension validation."""
        from utils.validators import VideoValidator
        
        # Valid extensions
        for ext in ["mp3", "wav", "m4a"]:
            is_valid, file_type, msg = VideoValidator.validate_file_extension(f"audio.{ext}")
            assert is_valid is True
            assert file_type == "audio"
    
    def test_validate_invalid_extension(self):
        """Test invalid file extension."""
        from utils.validators import VideoValidator
        
        is_valid, file_type, msg = VideoValidator.validate_file_extension("document.pdf")
        assert is_valid is False
        assert file_type == "unknown"
    
    def test_validate_file_size(self):
        """Test file size validation."""
        from utils.validators import VideoValidator
        
        # Valid size (10MB)
        is_valid, msg = VideoValidator.validate_file_size(10 * 1024 * 1024)
        assert is_valid is True
        
        # Invalid size (0 bytes)
        is_valid, msg = VideoValidator.validate_file_size(0)
        assert is_valid is False
        
        # Too large (1000MB, assuming 500MB limit)
        is_valid, msg = VideoValidator.validate_file_size(1000 * 1024 * 1024)
        assert is_valid is False
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from utils.validators import VideoValidator
        
        # Dangerous filename
        dangerous = "../../../etc/passwd"
        sanitized = VideoValidator.sanitize_filename(dangerous)
        
        assert ".." not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized
    
    def test_estimate_processing_time(self):
        """Test processing time estimation."""
        from utils.validators import VideoValidator
        
        # 10 minute video
        duration = 600  # seconds
        estimated = VideoValidator.estimate_processing_time(duration, "video")
        
        assert estimated > 0
        assert estimated > duration * 0.5  # Should be at least 0.5x duration


class TestMetadataValidation:
    """Test suite for metadata validation."""
    
    def test_validate_participants_valid(self):
        """Test valid participants list."""
        from utils.validators import MetadataValidator
        
        participants = ["Attorney Johnson", "Client Smith", "Paralegal Davis"]
        is_valid, msg = MetadataValidator.validate_participants(participants)
        
        assert is_valid is True
    
    def test_validate_participants_empty(self):
        """Test empty participants list."""
        from utils.validators import MetadataValidator
        
        is_valid, msg = MetadataValidator.validate_participants([])
        assert is_valid is False
    
    def test_validate_participants_too_many(self):
        """Test too many participants."""
        from utils.validators import MetadataValidator
        
        participants = [f"Person {i}" for i in range(100)]
        is_valid, msg = MetadataValidator.validate_participants(participants)
        
        assert is_valid is False
    
    def test_validate_case_id(self):
        """Test case ID validation."""
        from utils.validators import MetadataValidator
        
        # Valid case ID
        is_valid, msg = MetadataValidator.validate_case_id("CASE-2024-001")
        assert is_valid is True
        
        # None is valid (optional)
        is_valid, msg = MetadataValidator.validate_case_id(None)
        assert is_valid is True
        
        # Empty string is invalid
        is_valid, msg = MetadataValidator.validate_case_id("")
        assert is_valid is False

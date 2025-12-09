"""
Configuration management using Pydantic Settings.
Loads environment variables and provides type-safe configuration access.
"""
from typing import List, Optional
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: str = Field(..., description="Azure OpenAI endpoint URL")
    azure_openai_api_key: str = Field(..., description="Azure OpenAI API key")
    azure_openai_api_version: str = Field(default="2024-02-15-preview")
    azure_openai_whisper_deployment: str = Field(default="whisper")
    azure_openai_gpt_deployment: str = Field(default="gpt-4")
    
    # Application Settings
    app_name: str = Field(default="AI Meeting Participant")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    environment: str = Field(default="production")
    
    # File Upload Settings
    max_upload_size_mb: int = Field(default=500, ge=1, le=2000)
    allowed_video_formats: str = Field(default="mp4,mov,avi,webm,mkv")
    allowed_audio_formats: str = Field(default="mp3,wav,m4a,aac,flac")
    
    # FFmpeg Settings
    ffmpeg_path: Optional[str] = Field(default=None, description="Optional path to ffmpeg executable (auto-detected if not set)")
    
    # Storage Settings
    upload_dir: Path = Field(default=Path("./uploads"))
    temp_dir: Path = Field(default=Path("./temp"))
    output_dir: Path = Field(default=Path("./outputs"))
    
    # Processing Settings
    max_concurrent_jobs: int = Field(default=5, ge=1, le=20)
    transcription_timeout_seconds: int = Field(default=3600, ge=60)
    summary_timeout_seconds: int = Field(default=300, ge=30)
    
    # Chunking Settings (for large files)
    enable_chunking: bool = Field(default=True, description="Enable automatic chunking for large files")
    chunk_duration_seconds: int = Field(default=900, ge=60, description="Duration of each chunk in seconds (default: 15 minutes)")
    max_audio_size_mb: float = Field(default=20.0, ge=1.0, description="Maximum audio file size before chunking (MB)")
    max_audio_duration_seconds: int = Field(default=1500, ge=60, description="Maximum audio duration before chunking (seconds, default: 25 minutes)")
    
    # Real-time Streaming Settings
    websocket_timeout_seconds: int = Field(default=300, ge=30)
    stream_chunk_size_bytes: int = Field(default=4096, ge=1024)
    
    # Security Settings
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8000")
    secret_key: str = Field(..., description="Secret key for security")
    
    # Database
    database_url: str = Field(default="sqlite:///./ai_meeting.db")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://redis:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=10, ge=1, le=100)
    redis_job_ttl_seconds: int = Field(default=86400 * 7, description="Job TTL in seconds (default: 7 days)")
    
    # Logging
    log_level: str = Field(default="INFO")
    log_file: Path = Field(default=Path("./logs/app.log"))
    
    @field_validator("azure_openai_endpoint")
    @classmethod
    def validate_endpoint(cls, v: str) -> str:
        """Ensure endpoint ends with /"""
        if not v.endswith("/"):
            return f"{v}/"
        return v
    
    @field_validator("upload_dir", "temp_dir", "output_dir", mode="before")
    @classmethod
    def create_directories(cls, v: Path | str) -> Path:
        """Create directories if they don't exist."""
        path = Path(v) if isinstance(v, str) else v
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @property
    def allowed_video_formats_list(self) -> List[str]:
        """Get allowed video formats as a list."""
        return [fmt.strip().lower() for fmt in self.allowed_video_formats.split(",")]
    
    @property
    def allowed_audio_formats_list(self) -> List[str]:
        """Get allowed audio formats as a list."""
        return [fmt.strip().lower() for fmt in self.allowed_audio_formats.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_upload_size_bytes(self) -> int:
        """Get max upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()


# Ensure log directory exists
settings.log_file.parent.mkdir(parents=True, exist_ok=True)

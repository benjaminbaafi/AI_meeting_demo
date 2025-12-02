# AI Meeting Participant System

A production-ready AI-powered system for automated meeting transcription, summarization, and action item extraction using Azure OpenAI (Whisper + GPT-4).

## Features

✨ **Dual Processing Flows**
- **Pre-recorded**: Upload video/audio files for batch processing
- **Real-time**: Live streaming transcription (coming soon)

🎯 **AI-Powered Analysis**
- Accurate transcription using Azure OpenAI Whisper
- Speaker diarization and identification
- Legal terminology enhancement
- Multiple summary types (client-friendly, lawyer-professional, executive)
- Automatic action item extraction with deadlines and priorities
- Key decision identification
- Risk and compliance flagging

🏗️ **Professional Architecture**
- FastAPI backend with async/await
- Pydantic v2 for data validation
- Comprehensive error handling and retry logic
- Modular OOP design
- Extensive test coverage

## Prerequisites

- Python 3.10+
- FFmpeg (for audio/video processing)
- Azure OpenAI account with Whisper and GPT-4 deployments

## Installation

### 1. Clone the repository

```bash
cd AI_meerting_demo
```

### 2. Install dependencies with uv

```powershell
# Install uv if you haven't already
# pip install uv

# Install dependencies (uv is much faster than pip)
uv pip install -r requirements.txt
```

Alternatively, using traditional pip:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Install FFmpeg

**Windows:**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Add to PATH

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:

```bash
copy .env.example .env
```

Edit `.env`:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_WHISPER_DEPLOYMENT=whisper
AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4
SECRET_KEY=your-secret-key-change-in-production
```

## Usage

### Start the server

```bash
python app.py
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs: `http://localhost:8000/docs`

### Upload and Process a Video

```python
import requests

# Upload video
files = {"file": open("meeting.mp4", "rb")}
data = {
    "meeting_type": "consultation",
    "practice_area": "employment_law",
    "participants": "Attorney Johnson, Client Smith",
    "case_id": "CASE-2024-001"
}

response = requests.post("http://localhost:8000/api/v1/upload", files=files, data=data)
job_id = response.json()["job_id"]

# Check status
status = requests.get(f"http://localhost:8000/api/v1/upload/{job_id}/status")
print(status.json())

# Get transcription
transcription = requests.get(f"http://localhost:8000/api/v1/transcribe/{job_id}")
print(transcription.json())

# Get summary
summary = requests.get(f"http://localhost:8000/api/v1/summary/{job_id}")
print(summary.json())
```

## Project Structure

```
AI_meerting_demo/
├── api/
│   └── v1/
│       ├── upload.py          # Upload endpoints
│       ├── transcription.py   # Transcription endpoints
│       └── summary.py          # Summary endpoints
├── models/
│   ├── enums.py               # Enumerations
│   └── schemas.py             # Pydantic models
├── prompts/
│   ├── transcription_prompts.py  # Transcription prompts
│   ├── summary_prompts.py        # Summary prompts
│   └── action_item_prompts.py    # Action item prompts
├── services/
│   ├── azure_openai_service.py   # Azure OpenAI integration
│   ├── transcription_service.py  # Transcription orchestration
│   └── summarization_service.py  # Summary generation
├── utils/
│   ├── file_handler.py        # File operations
│   ├── audio_processor.py     # Audio processing
│   └── validators.py          # Validation utilities
├── tests/
│   ├── conftest.py            # Test fixtures
│   ├── test_upload.py         # Upload tests
│   └── test_services.py       # Service tests
├── app.py                     # Main FastAPI application
├── config.py                  # Configuration management
└── requirements.txt           # Python dependencies
```

## API Endpoints

### Upload
- `POST /api/v1/upload` - Upload video/audio file
- `GET /api/v1/upload/{job_id}/status` - Get job status
- `DELETE /api/v1/upload/{job_id}` - Cancel job

### Transcription
- `GET /api/v1/transcribe/{job_id}` - Get transcription
- `GET /api/v1/transcribe/{job_id}/download?format=txt|json|vtt` - Download transcript

### Summary
- `GET /api/v1/summary/{job_id}` - Get summary
- `POST /api/v1/summary/{job_id}/regenerate` - Regenerate with different type

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_upload.py -v
```

## Configuration

### File Upload Limits
- Maximum file size: 500MB (configurable in `.env`)
- Supported video formats: MP4, MOV, AVI, WebM, MKV
- Supported audio formats: MP3, WAV, M4A, AAC, FLAC

### Processing Settings
- Max concurrent jobs: 5
- Transcription timeout: 1 hour
- Summary timeout: 5 minutes

## Prompt Engineering

The system uses premium, specialized prompts for different tasks:

### Transcription Enhancement
- Legal terminology correction
- Speaker identification
- Context-aware corrections
- Timestamp formatting

### Summary Generation
- **Client-friendly**: Plain language, action-focused
- **Lawyer-professional**: Legal terminology, detailed analysis
- **Executive**: Concise, strategic overview

### Action Item Extraction
- Comprehensive extraction (explicit, implicit, conditional)
- Priority assessment (urgent, high, medium, low)
- Deadline identification
- Assignee detection

## Error Handling

The system includes comprehensive error handling:
- Automatic retries with exponential backoff
- Detailed error messages
- Validation at multiple levels
- Graceful degradation

## Performance

Typical processing times:
- Audio extraction: ~0.1x video duration
- Transcription: ~0.5x audio duration
- Summarization: 30-60 seconds

Example: A 30-minute video takes approximately 15-20 minutes to process completely.

## Security

- File validation and sanitization
- Size limits enforcement
- Secure file storage
- API key protection via environment variables
- CORS configuration

## Development

### Code Quality Tools

```bash
# Format code
black .

# Sort imports
isort .

# Lint
flake8 .

# Type checking
mypy .
```

### Adding New Features

1. Create feature branch
2. Add tests first (TDD)
3. Implement feature
4. Update documentation
5. Run all tests
6. Submit PR

## Troubleshooting

### FFmpeg not found
```
Error: FFmpeg not found!
Solution: Install FFmpeg and add to PATH
```

### Azure OpenAI authentication failed
```
Error: Authentication failed
Solution: Check AZURE_OPENAI_API_KEY in .env file
```

### File too large
```
Error: File too large
Solution: Increase MAX_UPLOAD_SIZE_MB in .env or compress video
```

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Create an issue on GitHub
- Check API documentation at `/docs`
- Review test files for usage examples

## Roadmap

- [ ] Real-time streaming transcription via WebSocket
- [ ] Database integration for persistent storage
- [ ] User authentication and authorization
- [ ] Multi-language support
- [ ] Video moment extraction
- [ ] Integration with calendar systems
- [ ] Email notifications
- [ ] Advanced analytics dashboard

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Acknowledgments

- Azure OpenAI for Whisper and GPT-4
- FastAPI framework
- FFmpeg for audio/video processing
- Pydantic for data validation

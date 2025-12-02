# Quick Start with UV

This guide uses [uv](https://github.com/astral-sh/uv) - an extremely fast Python package installer (10-100x faster than pip).

## Prerequisites

- Python 3.10+
- FFmpeg
- Azure OpenAI account

## Setup (5 minutes)

### 1. Install uv

```powershell
pip install uv
```

### 2. Install dependencies

```powershell
cd AI_meerting_demo
uv pip install -r requirements.txt
```

This takes ~30 seconds instead of 5+ minutes with pip!

### 3. Install FFmpeg

**Windows:**
```powershell
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 4. Configure Azure OpenAI

```powershell
# Copy example config
copy .env.example .env

# Edit .env with your credentials
notepad .env
```

Required variables:
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_WHISPER_DEPLOYMENT=whisper
AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4
SECRET_KEY=your-secret-key-change-in-production
```

### 5. Verify setup

```powershell
uv run python verify_setup.py
```

### 6. Start the server

```powershell
uv run python app.py
```

Server starts at: **http://localhost:8000**

API docs at: **http://localhost:8000/docs**

## Quick Test

### Upload a video via API

```python
import requests

files = {"file": open("meeting.mp4", "rb")}
data = {
    "meeting_type": "consultation",
    "practice_area": "employment_law",
    "participants": "Attorney Johnson, Client Smith",
}

response = requests.post("http://localhost:8000/api/v1/upload", files=files, data=data)
job_id = response.json()["job_id"]
print(f"Job ID: {job_id}")
```

### Check status

```python
status = requests.get(f"http://localhost:8000/api/v1/upload/{job_id}/status")
print(status.json())
```

### Get results

```python
# Transcription
transcription = requests.get(f"http://localhost:8000/api/v1/transcribe/{job_id}")
print(transcription.json()["full_text"][:200])

# Summary
summary = requests.get(f"http://localhost:8000/api/v1/summary/{job_id}")
print(f"Action items: {len(summary.json()['action_items'])}")
```

## Common Commands

### Development

```powershell
# Run server
uv run python app.py

# Run tests
uv run pytest tests/ -v

# Format code
uv run black .

# Lint
uv run flake8 .
```

### Testing

```powershell
# All tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ -v --cov=. --cov-report=html

# Specific test
uv run pytest tests/test_upload.py -v
```

## Troubleshooting

### FFmpeg not found
```
Error: FFmpeg not found
Solution: Install FFmpeg and ensure it's in PATH
Verify: ffmpeg -version
```

### Azure OpenAI error
```
Error: Authentication failed
Solution: Check .env file has correct AZURE_OPENAI_API_KEY
```

### Import errors
```
Error: ModuleNotFoundError
Solution: uv pip install -r requirements.txt
```

## Performance

With `uv`:
- **Dependency installation**: ~30 seconds (vs 5+ minutes with pip)
- **Package resolution**: ~4 seconds (vs 30+ seconds with pip)
- **Server startup**: ~2 seconds

## Next Steps

1. ✅ Upload a test video
2. ✅ Review transcription accuracy
3. ✅ Check action item extraction
4. ✅ Test different summary types
5. 🔄 Integrate with your workflow

See [README.md](README.md) for complete documentation.

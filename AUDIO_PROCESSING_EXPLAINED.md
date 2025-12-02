# Audio Processing & Chunking Explained

## Current Implementation

### 1. Audio Extraction from Video ✅

**How it works:**
- Video file uploaded → FFmpeg extracts audio track
- Audio converted to WAV format (16kHz, mono, PCM 16-bit)
- Audio normalized for better transcription quality
- Sent to Azure OpenAI Whisper API

**Code:** `utils/audio_processor.py` → `extract_audio_from_video()`

**Process Flow:**
```
Video File (MP4/MOV/etc.)
    ↓
FFmpeg: Extract audio track
    ↓
WAV file (16kHz, mono, PCM 16-bit)
    ↓
Audio Normalization (loudness adjustment)
    ↓
Azure OpenAI Whisper API
```

**FFmpeg Command Equivalent:**
```bash
ffmpeg -i video.mp4 -acodec pcm_s16le -ac 1 -ar 16000 audio.wav
```

---

### 2. Chunking for Large Files ✅

**Current Status:** ✅ **IMPLEMENTED**

**What happens now:**
- System automatically detects large files (>20MB or >25 minutes)
- Large files are split into chunks (10 minutes each)
- Each chunk is transcribed separately
- Results are merged with correct timestamps
- If one chunk fails, others continue processing

**Implementation:**
- `_transcribe_with_chunking()` method in `transcription_service.py`
- Uses `split_audio_chunks()` from `audio_processor.py`
- Automatically adjusts timestamps for merged segments

**Benefits:**
- ✅ Files of any size can be processed
- ✅ Better error handling (partial success possible)
- ✅ Configurable chunk size
- ✅ Automatic fallback for large files

---

## Azure OpenAI Whisper Limits

| Limit | Value | Impact |
|-------|-------|--------|
| **File Size** | 25MB | Files larger than this will fail |
| **Duration** | ~25 minutes (at 16kHz) | Approximate max duration |
| **Format** | MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM | Supported formats |

**Note:** 25MB ≈ ~25 minutes of audio at 16kHz mono WAV

---

## How to Add Chunking Support

If you want to support large files, we need to:

1. **Check file size/duration** before processing
2. **Split audio into chunks** if it exceeds limits
3. **Transcribe each chunk** separately
4. **Merge results** back together

### Implementation Plan

```python
# Pseudo-code for chunking implementation

if audio_file_size > 25MB or duration > 25_minutes:
    # Split into chunks
    chunks = split_audio_chunks(audio_path, chunk_duration=600)  # 10 min chunks
    
    # Transcribe each chunk
    all_segments = []
    for chunk in chunks:
        result = transcribe_audio(chunk)
        all_segments.extend(result.segments)
    
    # Merge segments (adjust timestamps)
    merged_segments = merge_segments(all_segments)
else:
    # Process normally (current behavior)
    result = transcribe_audio(audio_path)
```

---

## Current File Size Limits

**From `config.py`:**
- `max_upload_size_mb`: 500MB (default)
- This is the **upload limit**, not processing limit

**Actual Processing Limit:**
- Azure OpenAI Whisper: **25MB** (hard limit)
- This means videos longer than ~25 minutes may fail

---

## Recommendations

### Option 1: Keep Current Behavior (Simple)
- ✅ Works for videos < 25 minutes
- ❌ Will fail for longer videos
- **Best for:** Short meetings, consultations

### Option 2: Add Chunking (Recommended)
- ✅ Supports videos of any length
- ✅ Better error handling
- ✅ Can process chunks in parallel
- **Best for:** Long meetings, depositions, full-day sessions

### Option 3: Add File Size Validation
- ✅ Reject files > 25MB upfront
- ✅ Better error messages
- ❌ Still can't process long videos
- **Best for:** Quick fix, prevent failures

---

## Chunking Support ✅ IMPLEMENTED

Chunking support has been added! The system will now:

1. ✅ Automatically detect large files (>20MB or >25 minutes)
2. ✅ Split audio into manageable chunks (10 minutes each, configurable)
3. ✅ Transcribe each chunk separately
4. ✅ Merge results with correct timestamps
5. ✅ Handle errors gracefully (continues if one chunk fails)

**Configuration (in `.env`):**
```env
ENABLE_CHUNKING=true
CHUNK_DURATION_SECONDS=600  # 10 minutes
MAX_AUDIO_SIZE_MB=20.0      # Chunk if larger than 20MB
MAX_AUDIO_DURATION_SECONDS=1500  # Chunk if longer than 25 minutes
```

**Benefits:**
- ✅ Support videos of any length
- ✅ Better reliability
- ✅ Automatic fallback for large files
- ✅ Better progress tracking (can see chunk progress)

**How it works:**
- Small files (<20MB, <25 min): Processed normally (fast)
- Large files: Automatically split into chunks, each transcribed separately, then merged

---

## Technical Details

### Audio Extraction (Current)

**Location:** `utils/audio_processor.py:23-65`

**FFmpeg Parameters:**
- `acodec='pcm_s16le'`: PCM 16-bit little-endian
- `ac=1`: Mono (1 audio channel)
- `ar=16000`: 16kHz sample rate
- `loglevel='error'`: Suppress FFmpeg output

**Why these settings?**
- 16kHz is optimal for speech recognition
- Mono reduces file size
- PCM 16-bit is high quality, uncompressed

### Chunking Function (Available but Unused)

**Location:** `utils/audio_processor.py:200-239`

**Parameters:**
- `chunk_duration_seconds`: 600 (10 minutes default)
- Uses FFmpeg `ss` (start time) and `t` (duration) filters

**Example:**
```python
# Split 30-minute audio into 3 chunks
chunks = await AudioProcessor.split_audio_chunks(
    audio_path,
    chunk_duration_seconds=600  # 10 minutes
)
# Returns: [chunk_0.wav, chunk_1.wav, chunk_2.wav]
```

---

## Questions?

- **Q: Why extract audio from video?**
  - A: Azure OpenAI Whisper works with audio files. Video files are larger and unnecessary for transcription.

- **Q: Why normalize audio?**
  - A: Ensures consistent volume levels, improving transcription accuracy.

- **Q: Can I process multiple videos at once?**
  - A: Yes, up to `max_concurrent_jobs` (default: 5) can run simultaneously.

- **Q: What happens if a file is too large?**
  - A: Currently, it will fail with an error. Chunking would solve this.


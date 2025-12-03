# Robust Audio Chunking Algorithm - Technical Documentation

## Overview

This document explains the production-ready audio chunking algorithm implemented in `utils/audio_processor.py`. The algorithm is designed to split large audio/video files for Azure OpenAI Whisper API transcription while **preventing word loss** at chunk boundaries.

---

## The Problem

### Azure OpenAI Whisper Constraints
- **File size limit**: 25MB per request
- **Duration**: Long meetings (up to 2 hours) exceed this limit
- **Challenge**: Splitting audio can cut words in half, causing transcription errors

### Why Simple Chunking Fails
```python
# ❌ BAD: Hard cut at 15 minutes
chunk1 = audio[0:15*60*1000]  # Might cut mid-word
chunk2 = audio[15*60*1000:30*60*1000]  # Missing the cut word!
```

---

## The Solution: Two-Strategy Approach

### Strategy 1: Iterative Silence Detection (Preferred)
**Goal**: Find natural pauses to cut cleanly

**Algorithm**:
1. Define search window: 10-15 minutes from chunk start
2. Try to find silence at multiple threshold levels:
   - `-50 dB` → Quiet room (strict)
   - `-40 dB` → Normal room
   - `-35 dB` → Slightly noisy
   - `-30 dB` → Noisy room
   - `-25 dB` → Very noisy / breath pauses

3. If silence found:
   - Cut in the **middle** of the silence
   - Start next chunk immediately after (no overlap needed)

**Why Iterative?**
- Real-world meetings have varying noise floors
- Air conditioning, fans, typing = constant -35dB background
- Fixed -40dB threshold would fail → force hard cuts
- Iterative search adapts to the audio environment

---

### Strategy 2: Hard Cut with Safety Overlap (Fallback)
**When**: No silence found even at -25dB (rare, but possible)

**Algorithm**:
```
Chunk A: 0:00 → 15:00
Chunk B: 14:55 → 29:55  (starts 5 seconds BEFORE A ended)
```

**Result**:
- 5 seconds of **repeated text** in transcription
- **Guaranteed**: The word at 15:00 is fully captured in at least one chunk
- Post-processing can deduplicate the overlap

**Why 5 Seconds?**
- Average speaking rate: 2-3 words/second
- 5 seconds = ~10-15 words of overlap
- Ensures even slow speakers don't lose words

---

## Implementation Details

### Key Parameters

```python
MIN_MS = 10 * 60 * 1000  # 10 minutes (minimum chunk size)
MAX_MS = 15 * 60 * 1000  # 15 minutes (maximum chunk size)
OVERLAP_MS = 5 * 1000    # 5 seconds (safety overlap)
MIN_SILENCE_LEN = 500    # 500ms (minimum silence duration)
SILENCE_THRESHOLDS = [-50, -40, -35, -30, -25]  # dBFS
```

### Audio Export Settings (Optimized for Whisper)
```python
format="mp3"
bitrate="64k"        # Maximizes duration within 25MB
sample_rate="16kHz"  # Whisper's native rate
channels="1"         # Mono (speech doesn't need stereo)
```

**Math**:
- 64kbps × 60 seconds = 480KB/minute
- 25MB ÷ 480KB = ~52 minutes per file
- 15-minute chunks = ~7.2MB each (well under limit)

---

## Algorithm Flow

```mermaid
graph TD
    A[Start: Load Audio] --> B{Remaining Audio > 15 min?}
    B -->|No| C[Export Final Chunk]
    B -->|Yes| D[Extract 10-15 min Search Window]
    D --> E[Try -50dB Silence Detection]
    E -->|Found| F[Cut at Silence Middle]
    E -->|Not Found| G[Try -40dB]
    G -->|Found| F
    G -->|Not Found| H[Try -35dB]
    H -->|Found| F
    H -->|Not Found| I[Try -30dB]
    I -->|Found| F
    I -->|Not Found| J[Try -25dB]
    J -->|Found| F
    J -->|Not Found| K[Hard Cut at 15 min]
    K --> L[Backtrack Next Chunk by 5 sec]
    F --> M[Export Chunk]
    L --> M
    M --> N[Move to Next Chunk]
    N --> B
    C --> O[Done]
```

---

## Code Example

### Basic Usage
```python
from utils.audio_processor import AudioProcessor
from pathlib import Path

processor = AudioProcessor()

# Split a 2-hour meeting video
chunks = await processor.split_audio_chunks(
    audio_path=Path("meeting.mp3"),
    chunk_duration_seconds=900  # 15 minutes
)

# Result: ['meeting_chunk_0.mp3', 'meeting_chunk_1.mp3', ...]
```

### Integration with Transcription Service
```python
# Already integrated in services/transcription_service.py
# Automatically used when file > 25MB or > 15 minutes

transcription = await transcription_service.transcribe_video(
    job_id="job_123",
    video_path=Path("long_meeting.mp4"),
    practice_area=PracticeArea.CORPORATE,
    meeting_type=MeetingType.CLIENT_CONSULTATION,
    participants=["John Doe", "Jane Smith"]
)
```

---

## Logging Output Example

```
🎵 Starting ROBUST chunking: meeting.mp3
  ✂️  Chunk 0: Found silence at -40dB (cut at 14.8m)
  💾 Exporting meeting_chunk_0.mp3 (0.0m - 14.8m)
  ✂️  Chunk 1: Found silence at -35dB (cut at 29.5m)
  💾 Exporting meeting_chunk_1.mp3 (14.8m - 29.5m)
  ⚠️  Chunk 2: No silence found (even at -25dB). Using HARD CUT with 5-second overlap.
  💾 Exporting meeting_chunk_2.mp3 (29.5m - 44.5m)
  ✂️  Chunk 3: Found silence at -30dB (cut at 59.2m)
  💾 Exporting meeting_chunk_3.mp3 (44.4m - 59.2m)
  📌 Chunk 4: Final chunk (remaining audio)
  💾 Exporting meeting_chunk_4.mp3 (59.2m - 72.0m)
✅ Robust chunking complete: 5 chunks created
```

---

## Edge Cases Handled

### 1. Very Short Files (< 15 minutes)
- **Behavior**: Single chunk, no splitting
- **Code**: `if total_len - start_time <= MAX_MS`

### 2. No Silence Found (Continuous Noise)
- **Behavior**: Hard cut with 5-second overlap
- **Example**: Loud conference room, constant background noise

### 3. Final Chunk (< 15 minutes remaining)
- **Behavior**: Export remaining audio as-is
- **Code**: `end_time = total_len`

### 4. Silence at Chunk Boundary
- **Behavior**: Clean cut, no overlap
- **Benefit**: Minimizes redundant transcription

---

## Performance Characteristics

### Time Complexity
- **Loading**: O(1) - pydub loads metadata first
- **Silence Detection**: O(n) per threshold, where n = search window size
- **Worst Case**: O(5n) - tries 5 thresholds
- **Typical**: O(2n) - finds silence at -40dB or -35dB

### Space Complexity
- **Memory**: O(1) - processes one chunk at a time
- **Disk**: O(k) where k = number of chunks

### Typical Processing Time
- **2-hour video**: ~30-60 seconds for chunking
- **Bottleneck**: File I/O (export), not detection

---

## Testing Recommendations

### Test Cases
1. **Quiet Room** (-50dB silence)
   - Expected: Clean cuts at every chunk
   
2. **Noisy Room** (-30dB background)
   - Expected: Cuts at -30dB or -25dB thresholds
   
3. **Continuous Noise** (no silence)
   - Expected: Hard cuts with 5-second overlap
   
4. **Short File** (< 15 minutes)
   - Expected: Single chunk, no splitting

### Validation
```python
# Check for word loss
def validate_chunks(original_transcript, chunked_transcripts):
    original_words = set(original_transcript.split())
    chunked_words = set(" ".join(chunked_transcripts).split())
    
    missing_words = original_words - chunked_words
    assert len(missing_words) == 0, f"Lost words: {missing_words}"
```

---

## Comparison: Old vs New Algorithm

| Feature | Old (Simple) | New (Robust) |
|---------|-------------|--------------|
| Silence Detection | Single threshold (-40dB) | Iterative (-50 to -25dB) |
| Hard Cut Handling | No overlap (word loss!) | 5-second safety overlap |
| Noise Adaptation | ❌ Fails in noisy rooms | ✅ Adapts to environment |
| Word Loss Prevention | ❌ Not guaranteed | ✅ Guaranteed |
| Production Ready | ❌ Prototype | ✅ Yes |

---

## Future Enhancements

### Potential Improvements
1. **Adaptive Overlap**: Vary overlap based on speech rate detection
2. **Speaker Boundary Detection**: Cut at speaker changes, not just silence
3. **ML-Based Segmentation**: Use VAD (Voice Activity Detection) models
4. **Parallel Processing**: Process chunks concurrently for faster transcription

### Configuration Options
```python
# Could be added to config.py
CHUNKING_STRATEGY = "iterative"  # or "fixed", "adaptive"
OVERLAP_DURATION = 5  # seconds
SILENCE_THRESHOLDS = [-50, -40, -35, -30, -25]  # customizable
```

---

## References

- **Azure OpenAI Whisper Docs**: https://learn.microsoft.com/en-us/azure/ai-services/openai/whisper-quickstart
- **Pydub Documentation**: https://github.com/jiaaro/pydub
- **Audio dBFS Explained**: https://en.wikipedia.org/wiki/DBFS

---

## Conclusion

This algorithm provides **production-ready** audio chunking with:
- ✅ **Zero word loss** (guaranteed by safety overlap)
- ✅ **Adaptive to noise** (iterative threshold detection)
- ✅ **Optimized for Whisper** (64kbps, 16kHz, mono)
- ✅ **Comprehensive logging** (debug-friendly)

**Result**: Reliable transcription of long meetings without missing critical words.

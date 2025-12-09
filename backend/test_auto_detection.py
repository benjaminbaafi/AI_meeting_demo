"""
Test the content auto-detection pipeline.
This script demonstrates how the system automatically detects content type
and applies the appropriate prompts.
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone

# Import services
from services.transcription_service import get_transcription_service
from services.summarization_service import get_summarization_service
from services.content_classifier import get_content_classifier
from models.enums import MeetingType, PracticeArea

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_auto_detection():
    """Test the auto-detection pipeline."""
    
    print("=" * 80)
    print("CONTENT AUTO-DETECTION TEST")
    print("=" * 80)
    print()
    
    # Use the educational video
    video_path = Path("uploads/Do you ACTUALLY NEED math for Machine Learning_.mp4")
    
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return
    
    job_id = f"auto_detect_test_{int(datetime.now(timezone.utc).timestamp())}"
    print(f"[JOB ID] {job_id}")
    print(f"[VIDEO] {video_path.name}")
    print()
    
    # Step 1: Transcribe (without specifying content type)
    print("=" * 80)
    print("STEP 1: TRANSCRIPTION")
    print("=" * 80)
    print()
    
    transcription_service = get_transcription_service()
    
    print("Transcribing video...")
    transcription_result = await transcription_service.transcribe_video(
        job_id=job_id,
        video_path=video_path,
        practice_area=PracticeArea.OTHER,  # We don't know yet
        meeting_type=MeetingType.OTHER,    # We don't know yet
        participants=["Unknown"],           # We don't know yet
        enable_speaker_diarization=True
    )
    
    print(f"Transcription complete! ({transcription_result.duration_seconds:.1f}s)")
    print()
    
    # Step 2: Auto-detect content type
    print("=" * 80)
    print("STEP 2: AUTO-DETECTION")
    print("=" * 80)
    print()
    
    classifier = get_content_classifier()
    
    print("Analyzing content type...")
    classification = await classifier.classify_content(
        transcript_sample=transcription_result.full_text
    )
    
    print()
    print("-" * 80)
    print("CLASSIFICATION RESULTS:")
    print("-" * 80)
    print(f"Content Type: {classification['content_type']}")
    print(f"Confidence: {classification['confidence']:.1%}")
    print(f"Reasoning: {classification['reasoning']}")
    print()
    
    if classification['key_indicators']:
        print("Key Indicators:")
        for indicator in classification['key_indicators']:
            print(f"  - {indicator}")
        print()
    
    print(f"Suggested Prompts: {classification['suggested_prompts']}")
    print()
    
    # Step 3: Summarize using detected content type
    print("=" * 80)
    print("STEP 3: CONTENT-AWARE SUMMARIZATION")
    print("=" * 80)
    print()
    
    summarization_service = get_summarization_service()
    
    print(f"Generating summary using '{classification['suggested_prompts']}' prompts...")
    
    # Use the detected meeting type and practice area
    summary_result = await summarization_service.generate_summary(
        job_id=job_id,
        transcription=transcription_result,
        practice_area=classification['practice_area'],
        meeting_type=classification['meeting_type'],
        participants=["Presenter"],  # Could also be auto-detected
        summary_type="executive",
        include_action_items=True,
        include_key_decisions=True,
        include_risk_flags=False  # Not relevant for educational content
    )
    
    print("Summary complete!")
    print()
    
    # Display results
    print("-" * 80)
    print("SUMMARY:")
    print("-" * 80)
    print(summary_result.executive_summary)
    print()
    
    if summary_result.main_topics:
        print("-" * 80)
        print(f"MAIN TOPICS ({len(summary_result.main_topics)}):")
        print("-" * 80)
        for topic in summary_result.main_topics:
            print(f"  - {topic}")
        print()
    
    # Save results
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save classification result
    import json
    classification_path = output_dir / f"{job_id}_classification.json"
    with open(classification_path, 'w', encoding='utf-8') as f:
        json.dump(classification, indent=2, fp=f, default=str)
    
    print("=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print()
    print(f"Results saved to outputs/")
    print(f"  - {job_id}_classification.json")
    print()
    print("SUMMARY:")
    print(f"  Detected: {classification['content_type']}")
    print(f"  Confidence: {classification['confidence']:.1%}")
    print(f"  Processing Time: {transcription_result.processing_time_seconds + summary_result.processing_time_seconds:.2f}s")
    print()


if __name__ == "__main__":
    asyncio.run(test_auto_detection())

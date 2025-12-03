"""
Test the AI Meeting Demo pipeline with a new video.
This script will:
1. Transcribe the video using Azure OpenAI Whisper
2. Generate a summary with action items and key decisions
3. Save all results to the outputs folder
"""
import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone

# Import services
from services.transcription_service import get_transcription_service
from services.summarization_service import get_summarization_service
from models.enums import MeetingType, PracticeArea, SummaryType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_new_video():
    """Test pipeline with the new video."""
    
    print("=" * 80)
    print("AI MEETING DEMO - PIPELINE TEST")
    print("=" * 80)
    print()
    
    # 1. Setup - Use the new video
    video_path = Path("uploads/Do you ACTUALLY NEED math for Machine Learning_.mp4")
    
    if not video_path.exists():
        logger.error(f"[ERROR] Video file not found: {video_path}")
        print("\nAvailable videos in uploads/:")
        for f in Path("uploads").glob("*.mp4"):
            print(f"  - {f.name}")
        return
    
    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"[VIDEO] {video_path.name}")
    print(f"[SIZE] {file_size_mb:.2f} MB")
    print()
    
    job_id = f"test_job_{int(datetime.now(timezone.utc).timestamp())}"
    print(f"[JOB ID] {job_id}")
    print()
    
    # 2. Transcription
    print("=" * 80)
    print("STEP 1: TRANSCRIPTION")
    print("=" * 80)
    print()
    
    transcription_service = get_transcription_service()
    
    try:
        print(" Starting transcription...")
        print("   This may take a few minutes depending on video length...")
        print()
        
        transcription_result = await transcription_service.transcribe_video(
            job_id=job_id,
            video_path=video_path,
            practice_area=PracticeArea.OTHER,
            meeting_type=MeetingType.OTHER,
            participants=["Presenter"],  # Single speaker for educational video
            enable_speaker_diarization=True
        )
        
        print(" Transcription complete!")
        print()
        print(f"  Duration: {transcription_result.duration_seconds:.2f}s ({transcription_result.duration_seconds/60:.2f} minutes)")
        print(f" Word count: {transcription_result.word_count}")
        print(f"  Speakers found: {len(transcription_result.speakers)}")
        print(f" Average confidence: {transcription_result.average_confidence:.1%}")
        print(f" Language detected: {transcription_result.language_detected}")
        print()
        
        # Print transcript snippet
        print("-" * 80)
        print("TRANSCRIPT SNIPPET (first 500 characters):")
        print("-" * 80)
        print(transcription_result.full_text[:500])
        if len(transcription_result.full_text) > 500:
            print("...")
        print()
        
    except Exception as e:
        logger.error(f" Transcription failed: {e}", exc_info=True)
        return
    
    # Save transcript to files
    print(" Saving transcript to files...")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON (full data)
    json_path = output_dir / f"{job_id}_transcript.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        import json
        f.write(json.dumps(transcription_result.model_dump(), indent=2, default=str))
    print(f"    JSON: {json_path}")
    
    # Save as TXT (readable format)
    txt_path = output_dir / f"{job_id}_transcript.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== TRANSCRIPT ===\n")
        f.write(f"Job ID: {job_id}\n")
        f.write(f"Video: {video_path.name}\n")
        f.write(f"Duration: {transcription_result.duration_seconds:.2f}s\n")
        f.write(f"Word Count: {transcription_result.word_count}\n")
        f.write(f"Speakers: {len(transcription_result.speakers)}\n")
        f.write(f"Confidence: {transcription_result.average_confidence:.1%}\n")
        f.write(f"\n{'='*50}\n\n")
        f.write(transcription_result.full_text)
    print(f"    TXT: {txt_path}")
    print()
    
    # 3. Summarization
    print("=" * 80)
    print("STEP 2: SUMMARIZATION")
    print("=" * 80)
    print()
    
    summarization_service = get_summarization_service()
    
    try:
        print(" Generating summary...")
        print()
        
        summary_result = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription_result,
            practice_area=PracticeArea.OTHER,
            meeting_type=MeetingType.OTHER,
            participants=["Presenter"],
            summary_type=SummaryType.EXECUTIVE,
            include_action_items=True,
            include_key_decisions=True,
            include_risk_flags=True
        )
        
        print(" Summarization complete!")
        print()
        
        # Display results
        print("-" * 80)
        print("EXECUTIVE SUMMARY:")
        print("-" * 80)
        print(summary_result.executive_summary)
        print()
        
        if summary_result.main_topics:
            print("-" * 80)
            print(f"MAIN TOPICS ({len(summary_result.main_topics)}):")
            print("-" * 80)
            for topic in summary_result.main_topics:
                print(f"   {topic}")
            print()
        
        if summary_result.action_items:
            print("-" * 80)
            print(f"ACTION ITEMS ({len(summary_result.action_items)}):")
            print("-" * 80)
            for i, item in enumerate(summary_result.action_items, 1):
                print(f"  {i}. [{item.priority.upper()}] {item.description}")
                if item.assignee:
                    print(f"     Assignee: {item.assignee}")
            print()
        
        if summary_result.key_decisions:
            print("-" * 80)
            print(f"KEY DECISIONS ({len(summary_result.key_decisions)}):")
            print("-" * 80)
            for i, decision in enumerate(summary_result.key_decisions, 1):
                print(f"  {i}. {decision.decision}")
            print()
        
        if summary_result.risk_flags:
            print("-" * 80)
            print(f"RISK FLAGS ({len(summary_result.risk_flags)}):")
            print("-" * 80)
            for i, risk in enumerate(summary_result.risk_flags, 1):
                print(f"  {i}. [{risk.severity.upper()}] {risk.description}")
            print()
        
    except Exception as e:
        logger.error(f" Summarization failed: {e}", exc_info=True)
        return
    
    # Save summary to files
    print(" Saving summary to files...")
    
    # Save as JSON (full data)
    json_path = output_dir / f"{job_id}_summary.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        import json
        f.write(json.dumps(summary_result.model_dump(), indent=2, default=str))
    print(f"    JSON: {json_path}")
    
    # Save as TXT (readable format)
    txt_path = output_dir / f"{job_id}_summary.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== EXECUTIVE SUMMARY ===\n\n")
        f.write(summary_result.executive_summary)
        f.write(f"\n\n{'='*50}\n")
        f.write(f"\n=== DETAILED SUMMARY ===\n\n")
        f.write(summary_result.detailed_summary)
        f.write(f"\n\n{'='*50}\n")
        
        if summary_result.main_topics:
            f.write(f"\n=== MAIN TOPICS ({len(summary_result.main_topics)}) ===\n\n")
            for topic in summary_result.main_topics:
                f.write(f" {topic}\n")
            f.write(f"\n{'='*50}\n")
        
        if summary_result.action_items:
            f.write(f"\n=== ACTION ITEMS ({len(summary_result.action_items)}) ===\n\n")
            for i, item in enumerate(summary_result.action_items, 1):
                f.write(f"{i}. [{item.priority.upper()}] {item.description}\n")
                if item.assignee:
                    f.write(f"   Assignee: {item.assignee}\n")
                if item.deadline:
                    f.write(f"   Deadline: {item.deadline}\n")
                f.write("\n")
            f.write(f"{'='*50}\n")
        
        if summary_result.key_decisions:
            f.write(f"\n=== KEY DECISIONS ({len(summary_result.key_decisions)}) ===\n\n")
            for i, decision in enumerate(summary_result.key_decisions, 1):
                f.write(f"{i}. {decision.decision}\n")
                if decision.rationale:
                    f.write(f"   Rationale: {decision.rationale}\n")
                f.write("\n")
    print(f"    TXT: {txt_path}")
    print()
    
    # Final summary
    print("=" * 80)
    print("TEST COMPLETE! ")
    print("=" * 80)
    print()
    print(f" Results saved to outputs/:")
    print(f"    {job_id}_transcript.json")
    print(f"    {job_id}_transcript.txt")
    print(f"    {job_id}_summary.json")
    print(f"    {job_id}_summary.txt")
    print()
    print(f"  Total processing time:")
    print(f"    Transcription: {transcription_result.processing_time_seconds:.2f}s")
    print(f"    Summarization: {summary_result.processing_time_seconds:.2f}s")
    print(f"    Total: {transcription_result.processing_time_seconds + summary_result.processing_time_seconds:.2f}s")
    print()


if __name__ == "__main__":
    asyncio.run(test_new_video())

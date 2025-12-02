import asyncio
import logging
from pathlib import Path
from datetime import datetime, timezone

# Import services
from services.transcription_service import get_transcription_service
from services.summarization_service import get_summarization_service
from models.enums import MeetingType, PracticeArea, SummaryType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_pipeline():
    """Run end-to-end test pipeline."""
    
    # 1. Setup
    video_path = Path("uploads/mock_meeting.mp4")
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return

    job_id = f"test_job_{int(datetime.now(timezone.utc).timestamp())}"
    logger.info(f"Starting test job: {job_id}")

    # 2. Transcription
    logger.info("--- Step 1: Transcription ---")
    transcription_service = get_transcription_service()
    
    try:
        transcription_result = await transcription_service.transcribe_video(
            job_id=job_id,
            video_path=video_path,
            practice_area=PracticeArea.CORPORATE_LAW, # Default for mock meeting
            meeting_type=MeetingType.STRATEGY_SESSION,
            participants=["Alice", "Bob", "Charlie", "David"], # Hypothetical participants
            enable_speaker_diarization=True
        )
        
        logger.info(f"Transcription complete. Duration: {transcription_result.duration_seconds}s")
        logger.info(f"Word count: {transcription_result.word_count}")
        logger.info(f"Speakers found: {[s.speaker_id for s in transcription_result.speakers]}")
        
        # Print a snippet of the transcript
        print("\n--- Transcript Snippet ---")
        print(transcription_result.full_text[:500] + "...\n")

    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return

    # Save transcript to files
    logger.info("Saving transcript to files...")
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    # Save as JSON (full data)
    json_path = output_dir / f"{job_id}_transcript.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        import json
        f.write(json.dumps(transcription_result.model_dump(), indent=2, default=str))
    logger.info(f"Saved JSON transcript to: {json_path}")
    
    # Save as TXT (readable format)
    txt_path = output_dir / f"{job_id}_transcript.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== TRANSCRIPT ===\n")
        f.write(f"Job ID: {job_id}\n")
        f.write(f"Duration: {transcription_result.duration_seconds:.2f}s\n")
        f.write(f"Word Count: {transcription_result.word_count}\n")
        f.write(f"Speakers: {len(transcription_result.speakers)}\n")
        f.write(f"\n{'='*50}\n\n")
        f.write(transcription_result.full_text)
    logger.info(f"Saved TXT transcript to: {txt_path}")

    # 3. Summarization
    logger.info("--- Step 2: Summarization ---")
    summarization_service = get_summarization_service()
    
    try:
        summary_result = await summarization_service.generate_summary(
            job_id=job_id,
            transcription=transcription_result,
            practice_area=PracticeArea.CORPORATE_LAW,
            meeting_type=MeetingType.STRATEGY_SESSION,
            participants=["Alice", "Bob", "Charlie", "David"],
            summary_type=SummaryType.EXECUTIVE,
            include_action_items=True,
            include_key_decisions=True,
            include_risk_flags=True
        )
        
        logger.info("Summarization complete.")
        
        print("\n--- Executive Summary ---")
        print(summary_result.executive_summary)
        
        print("\n--- Action Items ---")
        for item in summary_result.action_items:
            print(f"- [Priority: {item.priority}] {item.description} (Assignee: {item.assignee})")

    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return

    # Save summary to files
    logger.info("Saving summary to files...")
    
    # Save as JSON (full data)
    json_path = output_dir / f"{job_id}_summary.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        import json
        f.write(json.dumps(summary_result.model_dump(), indent=2, default=str))
    logger.info(f"Saved JSON summary to: {json_path}")
    
    # Save as TXT (readable format)
    txt_path = output_dir / f"{job_id}_summary.txt"
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== EXECUTIVE SUMMARY ===\n\n")
        f.write(summary_result.executive_summary)
        f.write(f"\n\n{'='*50}\n")
        f.write(f"\n=== DETAILED SUMMARY ===\n\n")
        f.write(summary_result.detailed_summary)
        f.write(f"\n\n{'='*50}\n")
        f.write(f"\n=== ACTION ITEMS ({len(summary_result.action_items)}) ===\n\n")
        for i, item in enumerate(summary_result.action_items, 1):
            f.write(f"{i}. [{item.priority.upper()}] {item.description}\n")
            if item.assignee:
                f.write(f"   Assignee: {item.assignee}\n")
            if item.deadline:
                f.write(f"   Deadline: {item.deadline}\n")
            f.write("\n")
        f.write(f"\n{'='*50}\n")
        f.write(f"\n=== KEY DECISIONS ({len(summary_result.key_decisions)}) ===\n\n")
        for i, decision in enumerate(summary_result.key_decisions, 1):
            f.write(f"{i}. {decision.decision}\n")
            if decision.rationale:
                f.write(f"   Rationale: {decision.rationale}\n")
            f.write("\n")
    logger.info(f"Saved TXT summary to: {txt_path}")

    logger.info(f"Test job {job_id} completed successfully.")
    logger.info(f"\nResults saved to:")
    logger.info(f"  - {output_dir / f'{job_id}_transcript.json'}")
    logger.info(f"  - {output_dir / f'{job_id}_transcript.txt'}")
    logger.info(f"  - {output_dir / f'{job_id}_summary.json'}")
    logger.info(f"  - {output_dir / f'{job_id}_summary.txt'}")


if __name__ == "__main__":
    asyncio.run(test_pipeline())

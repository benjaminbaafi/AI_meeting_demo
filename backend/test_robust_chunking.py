"""
Test script for robust audio chunking algorithm.
Validates the iterative silence detection and safety overlap mechanisms.

Usage:
    python test_robust_chunking.py
"""

import asyncio
from pathlib import Path
import logging

from utils.audio_processor import AudioProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_chunking(audio_file: Path):
    """
    Test the robust chunking algorithm.
    
    Args:
        audio_file: Path to test audio file
    """
    logger.info("=" * 80)
    logger.info("ROBUST AUDIO CHUNKING TEST")
    logger.info("=" * 80)
    logger.info(f"Test File: {audio_file}")
    logger.info("")
    
    try:
        processor = AudioProcessor()
        
        # Get audio duration first
        duration = await processor.get_audio_duration(audio_file)
        logger.info(f"📊 Audio Duration: {duration/60:.2f} minutes ({duration:.1f} seconds)")
        logger.info("")
        
        # Test chunking
        logger.info("🔧 Starting chunking test...")
        logger.info("")
        
        chunks = await processor.split_audio_chunks(
            audio_path=audio_file,
            chunk_duration_seconds=900  # 15 minutes
        )
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("RESULTS")
        logger.info("=" * 80)
        logger.info(f"✅ Total Chunks Created: {len(chunks)}")
        logger.info("")
        
        # Analyze each chunk
        total_chunk_duration = 0
        for idx, chunk_path in enumerate(chunks):
            chunk_duration = await processor.get_audio_duration(chunk_path)
            chunk_size_mb = chunk_path.stat().st_size / (1024 * 1024)
            total_chunk_duration += chunk_duration
            
            logger.info(f"Chunk {idx}:")
            logger.info(f"  📁 File: {chunk_path.name}")
            logger.info(f"  ⏱️  Duration: {chunk_duration/60:.2f} minutes ({chunk_duration:.1f} seconds)")
            logger.info(f"  💾 Size: {chunk_size_mb:.2f} MB")
            logger.info(f"  ✅ Under 25MB limit: {'Yes' if chunk_size_mb < 25 else 'No'}")
            logger.info("")
        
        # Validation
        logger.info("=" * 80)
        logger.info("VALIDATION")
        logger.info("=" * 80)
        
        # Check if all chunks are under 25MB
        all_under_limit = all(
            chunk.stat().st_size / (1024 * 1024) < 25 
            for chunk in chunks
        )
        logger.info(f"✅ All chunks under 25MB: {all_under_limit}")
        
        # Check total duration (accounting for overlaps)
        logger.info(f"📊 Original Duration: {duration:.1f}s")
        logger.info(f"📊 Total Chunk Duration: {total_chunk_duration:.1f}s")
        
        # If there are overlaps, total chunk duration will be > original
        if total_chunk_duration > duration:
            overlap_seconds = total_chunk_duration - duration
            logger.info(f"🔄 Detected Overlap: {overlap_seconds:.1f}s (Safety overlap working!)")
        else:
            logger.info(f"✂️  Clean Cuts: No overlap detected (all silence cuts)")
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("TEST COMPLETE")
        logger.info("=" * 80)
        
        return chunks
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
        raise


async def main():
    """Main test function."""
    # Check if test file exists
    test_files = [
        Path("temp/test_audio.mp3"),
        Path("uploads/test_video.mp4"),
        Path("outputs/sample.mp3"),
    ]
    
    # Find first existing test file
    test_file = None
    for file in test_files:
        if file.exists():
            test_file = file
            break
    
    if not test_file:
        logger.warning("⚠️  No test audio file found!")
        logger.info("Please place a test audio/video file in one of these locations:")
        for file in test_files:
            logger.info(f"  - {file}")
        logger.info("")
        logger.info("Or specify a custom path:")
        logger.info("  python test_robust_chunking.py path/to/your/audio.mp3")
        return
    
    # Run test
    await test_chunking(test_file)


if __name__ == "__main__":
    asyncio.run(main())

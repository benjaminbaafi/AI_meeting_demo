"""
Test script for batch processing API.
Demonstrates uploading multiple files and tracking batch status.
"""
import requests
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_batch_upload():
    """Test batch upload endpoint."""
    print("=" * 60)
    print("BATCH PROCESSING TEST")
    print("=" * 60)
    print()
    
    # Prepare test files (use existing test files or create dummy ones)
    test_files = []
    
    # Option 1: Use existing files if available
    existing_files = list(Path("uploads").glob("*.mp4"))[:3]
    if existing_files:
        print(f"Using {len(existing_files)} existing files for test:")
        for f in existing_files:
            print(f"  - {f.name}")
            test_files.append(("files", (f.name, open(f, "rb"), "video/mp4")))
    
    # Option 2: If no files, provide instructions
    if not test_files:
        print("No test files found in uploads/ directory.")
        print("Please place some MP4 files in the uploads/ directory and run again.")
        print()
        print("For testing purposes, you can:")
        print("1. Copy some test videos to the uploads/ folder")
        print("2. Or modify this script to point to your test files")
        return
    
    print()
    
    # Upload batch
    print("1. UPLOADING BATCH...")
    data = {
        "meeting_type": "consultation",
        "practice_area": "employment_law",
        "participants": "Attorney Johnson, Client Smith",
        "case_id": "CASE-BATCH-001",
        "notes": "Test batch processing"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/batch/upload",
            files=test_files,
            data=data
        )
        response.raise_for_status()
        batch_data = response.json()
        
        print(f"✅ Batch created: {batch_data['batch_id']}")
        print(f"   Total files: {batch_data['total_files']}")
        print(f"   Job IDs: {', '.join(batch_data['job_ids'][:3])}...")
        print()
        
        batch_id = batch_data['batch_id']
        
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        return
    finally:
        # Close file handles
        for _, (_, file_obj, _) in test_files:
            file_obj.close()
    
    # Monitor batch status
    print("2. MONITORING BATCH STATUS...")
    print()
    
    max_iterations = 60  # Max 5 minutes
    iteration = 0
    
    while iteration < max_iterations:
        try:
            response = requests.get(f"{BASE_URL}/batch/{batch_id}/status")
            response.raise_for_status()
            status_data = response.json()
            
            # Display status
            print(f"   Progress: {status_data['progress_percentage']:.1f}%")
            print(f"   Status: {status_data['status']}")
            print(f"   Completed: {status_data['completed']}/{status_data['total_files']}")
            print(f"   Processing: {status_data['processing']}")
            print(f"   Failed: {status_data['failed']}")
            print()
            
            # Show individual job statuses
            for job in status_data['jobs']:
                status_icon = {
                    "completed": "✅",
                    "processing": "⏳",
                    "failed": "❌",
                    "queued": "⏸️"
                }.get(job['status'], "❓")
                
                print(f"   {status_icon} {job['filename']}: {job['status']} ({job['progress_percentage']:.1f}%)")
            print()
            
            # Check if batch is complete
            if status_data['status'] in ['completed', 'completed_with_errors']:
                print(f"✅ Batch processing complete!")
                break
            elif status_data['status'] == 'failed':
                print(f"❌ Batch processing failed")
                break
            
        except Exception as e:
            print(f"❌ Error checking status: {str(e)}")
            break
        
        # Wait before next check
        time.sleep(5)
        iteration += 1
    
    # Get batch results
    print("\n3. RETRIEVING BATCH RESULTS...")
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/batch/{batch_id}/results")
        response.raise_for_status()
        results = response.json()
        
        print(f"   Batch ID: {results['batch_id']}")
        print(f"   Total files: {results['total_files']}")
        print(f"   Successful: {results['successful']}")
        print(f"   Failed: {results['failed']}")
        print()
        
        # Show transcription summary
        if results['transcriptions']:
            print(f"   📄 Transcriptions: {len(results['transcriptions'])}")
            for trans in results['transcriptions'][:2]:  # Show first 2
                print(f"      - Job {trans['job_id']}: {trans['word_count']} words")
        
        # Show summary summary
        if results['summaries']:
            print(f"   📊 Summaries: {len(results['summaries'])}")
            for summary in results['summaries'][:2]:  # Show first 2
                print(f"      - Job {summary['job_id']}: {len(summary.get('action_items', []))} action items")
        
        print()
        print("=" * 60)
        print("✅ BATCH PROCESSING TEST COMPLETE!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error retrieving results: {str(e)}")


def test_batch_status_only():
    """Test checking status of an existing batch."""
    batch_id = input("Enter batch ID to check: ").strip()
    
    if not batch_id:
        print("No batch ID provided")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/batch/{batch_id}/status")
        response.raise_for_status()
        status_data = response.json()
        
        print(f"\nBatch Status:")
        print(f"  ID: {status_data['batch_id']}")
        print(f"  Progress: {status_data['progress_percentage']:.1f}%")
        print(f"  Status: {status_data['status']}")
        print(f"  Total: {status_data['total_files']}")
        print(f"  Completed: {status_data['completed']}")
        print(f"  Processing: {status_data['processing']}")
        print(f"  Failed: {status_data['failed']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    print("\nBatch Processing API Test")
    print("1. Test full batch upload and processing")
    print("2. Check status of existing batch")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice == "1":
        test_batch_upload()
    elif choice == "2":
        test_batch_status_only()
    else:
        print("Invalid choice")

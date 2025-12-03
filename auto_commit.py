import time
import subprocess
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class GitAutoCommitHandler(FileSystemEventHandler):
    """Handler for file system events that triggers git commits."""
    
    def __init__(self, repo_path: Path, debounce_seconds: int = 5):
        self.repo_path = repo_path
        self.debounce_seconds = debounce_seconds
        self.last_commit_time = 0
        self.pending_changes = False
        
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
        
        # Ignore git files and other non-source files
        ignored_patterns = [
            '.git', '__pycache__', '.pyc', '.pyo', 
            'logs/', 'temp/', 'outputs/', 'uploads/'
        ]
        
        if any(pattern in event.src_path for pattern in ignored_patterns):
            return
        
        print(f"📝 File changed: {event.src_path}")
        self.pending_changes = True
        self._try_commit()
    
    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return
        
        print(f"✨ File created: {event.src_path}")
        self.pending_changes = True
        self._try_commit()
    
    def on_deleted(self, event):
        """Called when a file is deleted."""
        if event.is_directory:
            return
        
        print(f"🗑️  File deleted: {event.src_path}")
        self.pending_changes = True
        self._try_commit()
    
    def _try_commit(self):
        """Try to commit changes if debounce period has passed."""
        current_time = time.time()
        
        # Debounce: only commit if enough time has passed since last commit
        if current_time - self.last_commit_time < self.debounce_seconds:
            return
        
        if not self.pending_changes:
            return
        
        self.last_commit_time = current_time
        self.pending_changes = False
        self._commit_and_push()
    
    def _commit_and_push(self):
        """Commit and push changes to GitHub."""
        try:
            # Check if there are changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                print("ℹ️  No changes to commit")
                return
            
            # Add all changes
            print("📦 Adding changes...")
            subprocess.run(
                ['git', 'add', '.'],
                cwd=self.repo_path,
                check=True
            )
            
            # Create commit with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-commit: {timestamp}"
            
            print(f"💾 Committing: {commit_message}")
            subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Push to GitHub
            print("🚀 Pushing to GitHub...")
            subprocess.run(
                ['git', 'push'],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            print("✅ Successfully committed and pushed!\n")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def main():
    """Main function to start the file watcher."""
    repo_path = Path(__file__).parent
    
    print("=" * 60)
    print("🔍 Git Auto-Commit Watcher Started")
    print("=" * 60)
    print(f"📂 Monitoring: {repo_path}")
    print(f"⏱️  Debounce: 5 seconds")
    print(f"🌐 Remote: https://github.com/benjaminbaafi/AI_meeting_demo.git")
    print("\n💡 Changes will be automatically committed and pushed.")
    print("⚠️  Press Ctrl+C to stop monitoring.\n")
    print("=" * 60)
    print()
    
    event_handler = GitAutoCommitHandler(repo_path, debounce_seconds=5)
    observer = Observer()
    observer.schedule(event_handler, str(repo_path), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping auto-commit watcher...")
        observer.stop()
    
    observer.join()
    print("✅ Auto-commit watcher stopped.")


if __name__ == "__main__":
    main()

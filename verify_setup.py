"""
Setup verification script.
Checks that all dependencies and requirements are met.
"""
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        print("[OK] FFmpeg installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[FAIL] FFmpeg not found - please install from https://ffmpeg.org/download.html")
        return False


def check_env_file():
    """Check if .env file exists."""
    env_path = Path(".env")
    if env_path.exists():
        print("[OK] .env file exists")
        
        # Check for required variables
        env_content = env_path.read_text()
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_WHISPER_DEPLOYMENT",
            "AZURE_OPENAI_GPT_DEPLOYMENT",
        ]
        
        missing = []
        for var in required_vars:
            if var not in env_content or f"{var}=your-" in env_content:
                missing.append(var)
        
        if missing:
            print(f"[WARN] Please configure these variables in .env: {', '.join(missing)}")
            return False
        
        print("[OK] All required environment variables configured")
        return True
    else:
        print("[FAIL] .env file not found - copy .env.example to .env and configure")
        return False


def check_dependencies():
    """Check if key dependencies are installed."""
    try:
        import fastapi
        import pydantic
        import openai
        import ffmpeg
        
        print("[OK] All Python dependencies installed")
        return True
    except ImportError as e:
        print(f"[FAIL] Missing dependency: {e.name}")
        print("   Run: uv pip install -r requirements.txt")
        return False


def check_directories():
    """Check if required directories exist."""
    dirs = ["uploads", "temp", "outputs", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
    print("[OK] Required directories created")
    return True


def main():
    """Run all checks."""
    print("AI Meeting Participant - Setup Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("FFmpeg", check_ffmpeg),
        ("Environment File", check_env_file),
        ("Python Dependencies", check_dependencies),
        ("Directories", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append(result)
        except Exception as e:
            print(f"[FAIL] {name} check failed: {str(e)}")
            results.append(False)
        print()
    
    print("=" * 50)
    if all(results):
        print("[SUCCESS] All checks passed! You're ready to run the application.")
        print("\nStart the server with:")
        print("  python app.py")
        print("\nThen visit: http://localhost:8000/docs")
    else:
        print("[WARNING] Some checks failed. Please fix the issues above.")
        print("\nSetup steps:")
        print("1. Install FFmpeg: https://ffmpeg.org/download.html")
        print("2. Copy .env.example to .env")
        print("3. Configure Azure OpenAI credentials in .env")
        print("4. Run: uv pip install -r requirements.txt")
    print("=" * 50)


if __name__ == "__main__":
    main()

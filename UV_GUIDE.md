# UV-Optimized AI Meeting Participant

## Why UV?

[uv](https://github.com/astral-sh/uv) is **10-100x faster** than pip:
- Dependency installation: **30 seconds** (vs 5+ minutes with pip)
- Package resolution: **4 seconds** (vs 30+ seconds)
- Written in Rust for maximum performance

## Quick Commands

### Setup
```powershell
# Install dependencies
uv pip install -r requirements.txt

# Verify setup
uv run python verify_setup.py
```

### Run Application
```powershell
# Quick start (recommended)
.\start.bat

# Or manually
uv run python app.py
```

### Testing
```powershell
# Run all tests with coverage
.\run_tests.bat

# Or manually
uv run pytest tests/ -v
uv run pytest tests/ -v --cov=. --cov-report=html
```

### Development
```powershell
# Format code
uv run black .

# Sort imports
uv run isort .

# Lint
uv run flake8 .

# Type check
uv run mypy .
```

## Convenience Scripts

We've created Windows batch scripts for common tasks:

### `start.bat`
- Checks if `uv` is installed
- Installs dependencies if needed
- Checks for `.env` configuration
- Starts the server

### `run_tests.bat`
- Runs all tests with `uv`
- Generates coverage report
- Opens results in browser

### `verify_setup.py`
- Checks Python version
- Verifies FFmpeg installation
- Validates `.env` configuration
- Confirms dependencies

## Performance Comparison

| Task | pip | uv | Speedup |
|------|-----|----|----|
| Install dependencies | 5-8 min | 30 sec | **10-16x** |
| Resolve packages | 30 sec | 4 sec | **7.5x** |
| Reinstall (cached) | 2 min | 5 sec | **24x** |

## File Structure

```
AI_meerting_demo/
├── start.bat              # Quick start script (UV)
├── run_tests.bat          # Run tests script (UV)
├── verify_setup.py        # Setup verification
├── QUICKSTART.md          # UV-specific quick start
├── README.md              # Full documentation
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
└── app.py                 # Main application
```

## Next Steps

1. **First time setup**:
   ```powershell
   uv pip install -r requirements.txt
   copy .env.example .env
   # Edit .env with your Azure OpenAI credentials
   ```

2. **Start developing**:
   ```powershell
   .\start.bat
   ```

3. **Run tests**:
   ```powershell
   .\run_tests.bat
   ```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

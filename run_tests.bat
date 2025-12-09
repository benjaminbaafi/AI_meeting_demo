@echo off
REM Run tests with UV

echo ========================================
echo Running Tests with UV
echo ========================================
echo.

cd backend

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv is not installed!
    echo Install uv with: pip install uv
    pause
    exit /b 1
)

REM Run tests
echo Running all tests...
echo.
uv run pytest tests/ -v --cov=. --cov-report=html --cov-report=term

echo.
echo ========================================
echo Tests complete!
echo.
echo Coverage report saved to: htmlcov/index.html
echo ========================================
pause

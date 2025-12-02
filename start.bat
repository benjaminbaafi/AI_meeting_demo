@echo off
REM Quick start script for AI Meeting Participant using UV

echo ========================================
echo AI Meeting Participant - Quick Start
echo ========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] uv is not installed!
    echo.
    echo Install uv with: pip install uv
    echo.
    pause
    exit /b 1
)

echo [1/3] Checking dependencies...
uv pip list | findstr "fastapi" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [INFO] Installing dependencies with uv...
    uv pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [OK] Dependencies already installed
)

echo.
echo [2/3] Checking configuration...
if not exist .env (
    echo [WARN] .env file not found!
    echo [INFO] Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit .env with your Azure OpenAI credentials
    echo Then run this script again.
    echo.
    pause
    exit /b 0
)

echo [OK] Configuration file found
echo.
echo [3/3] Starting server...
echo.
echo Server will start at: http://localhost:8000
echo API docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

uv run python app.py

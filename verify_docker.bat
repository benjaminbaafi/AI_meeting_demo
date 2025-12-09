@echo off
REM Docker Verification Script for AI Meeting Demo
REM Checks Docker installation and builds/runs the container

echo ================================================
echo AI Meeting Demo - Docker Verification
echo ================================================
echo.

REM Check if Docker is installed
echo [1/5] Checking Docker installation...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed or not in PATH
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)
docker --version
echo [OK] Docker is installed
echo.

REM Check if Docker daemon is running
echo [2/5] Checking Docker daemon...
docker ps >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)
echo [OK] Docker daemon is running
echo.

REM Check if .env file exists
echo [3/5] Checking environment configuration...
if not exist .env (
    echo [WARNING] .env file not found
    echo Please copy .env.example to .env and configure your Azure OpenAI credentials
    echo.
    choice /C YN /M "Continue anyway?"
    if ERRORLEVEL 2 exit /b 1
) else (
    echo [OK] .env file found
)
echo.

REM Build Docker images
echo [4/5] Building Docker images...
docker-compose build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker build failed
    pause
    exit /b 1
)
echo [OK] Docker images built successfully
echo.

REM Start services
echo [5/5] Starting services...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started successfully
echo.

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 5 /nobreak >nul

REM Check service health
echo.
echo Checking service health...
docker-compose ps
echo.

REM Test API endpoint
echo Testing API endpoint...
curl -f http://localhost:8000/health 2>nul
if %ERRORLEVEL% EQ 0 (
    echo.
    echo [SUCCESS] API is responding
) else (
    echo.
    echo [WARNING] API health check failed - service may still be starting
    echo Run: docker-compose logs app
)
echo.

echo ================================================
echo Docker Setup Complete!
echo ================================================
echo.
echo Services running:
echo - API: http://localhost:8000
echo - API Docs: http://localhost:8000/docs
echo - Redis: localhost:6379
echo.
echo Useful commands:
echo   docker-compose logs -f          - View all logs
echo   docker-compose logs -f app      - View app logs
echo   docker-compose stop             - Stop services
echo   docker-compose down             - Stop and remove containers
echo   docker-compose restart          - Restart services
echo.
pause

@echo off
REM Quick commit and push script
REM Usage: Just double-click this file or run it from command line

echo ========================================
echo Git Quick Push
echo ========================================
echo.

REM Add all changes
echo [1/3] Adding changes...
git add .

REM Commit with timestamp
echo [2/3] Committing...
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/:" %%a in ('time /t') do (set mytime=%%a:%%b)
git commit -m "Quick commit: %mydate% %mytime%"

REM Push to GitHub
echo [3/3] Pushing to GitHub...
git push

echo.
echo ========================================
echo Done!
echo ========================================
pause

@echo off
REM Quick Start Script for Phase-3 Testing
REM This script helps you start both servers and run tests

echo ========================================
echo Phase-3 Chat Implementation - Quick Start
echo ========================================
echo.

echo Checking if backend is already running...
curl -s http://localhost:8000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is already running
) else (
    echo [INFO] Backend not running. Please start it manually:
    echo        cd backend
    echo        uvicorn app.main:app --reload
    echo.
    pause
)

echo.
echo Checking if frontend is already running...
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is already running
) else (
    echo [INFO] Frontend not running. Please start it manually:
    echo        cd frontend
    echo        npm run dev
    echo.
    pause
)

echo.
echo ========================================
echo Running Backend Tests
echo ========================================
python test_implementation.py

echo.
echo ========================================
echo Manual Testing Instructions
echo ========================================
echo.
echo 1. Open browser: http://localhost:3000
echo 2. Log in to the application
echo 3. Look for blue chat icon (bottom-right)
echo 4. Click icon to open chat
echo 5. Send a test message
echo 6. Verify you receive a response
echo.
echo For detailed testing, see: TESTING_GUIDE.md
echo.
pause

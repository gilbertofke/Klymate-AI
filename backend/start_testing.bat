@echo off
REM Klymate AI Backend - Quick Testing Startup Script for Windows
REM This script sets up and starts the testing environment

echo ========================================
echo 🚀 Klymate AI Backend Testing Setup
echo ========================================

REM Change to backend directory
cd /d "%~dp0"

echo.
echo 📋 Step 1: Setting up test environment...
python test_setup.py

echo.
echo ⏳ Waiting for server to start (10 seconds)...
timeout /t 10 /nobreak > nul

echo.
echo 🧪 Step 2: Running quick API tests...
python quick_test.py

echo.
echo 📊 Step 3: Opening useful links...
echo 🌐 API Documentation: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo 📈 Test Coverage: file://%CD%/htmlcov/index.html

echo.
echo ✅ Testing environment ready!
echo.
echo 💡 Next Steps:
echo    1. Import postman_environment.json into Postman
echo    2. Use the comprehensive testing guide
echo    3. Test critical API endpoints
echo.
echo Press any key to open API documentation in browser...
pause > nul

REM Open API docs in default browser
start http://localhost:8000/docs

echo.
echo 🎉 Happy Testing!
pause
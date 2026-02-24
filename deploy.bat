@echo off
echo ===================================================
echo KavachG Safety Monitoring System Deployment Script
echo ===================================================
echo.

REM Check prerequisites
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in the PATH. Please install Python 3.8 or higher.
    exit /b 1
)

where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Node.js is not installed or not in the PATH. Please install Node.js.
    exit /b 1
)

echo Checking MongoDB...
mongod --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo WARNING: MongoDB does not appear to be installed. The ML system needs MongoDB.
    echo Please ensure MongoDB is running or install it from https://www.mongodb.com/try/download/community
    echo.
    set /p CONTINUE=Do you want to continue anyway? (y/n): 
    if /i "%CONTINUE%" neq "y" exit /b 1
)

echo.
echo Deploying KavachG Safety Monitoring System...
echo.

REM Setup environment variables
set KAVACHG_ROOT=%CD%
set BACKEND_PATH=%KAVACHG_ROOT%\backend
set FRONTEND_PATH=%KAVACHG_ROOT%\FrontEnd\FrontEnd
set ML_PATH=%KAVACHG_ROOT%\ML

REM Start Backend (SQLite)
echo Starting Backend (SQLite)...
start cmd /k "cd %BACKEND_PATH% && echo === BACKEND SERVER === && npm install && node src/server-sqlite.js"
timeout /t 5 /nobreak > NUL

REM Start Frontend
echo Starting Frontend...
start cmd /k "cd %FRONTEND_PATH% && echo === FRONTEND SERVER === && npm install && npm run dev"
timeout /t 5 /nobreak > NUL

REM Setup and start ML system
echo Setting up ML environment...
start cmd /k "cd %ML_PATH% && echo === ML SYSTEM === && python setup_env.py && python run_safety_system.py"

echo.
echo =======================================================
echo KavachG System deployed successfully! Access points:
echo =======================================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:5000
echo ML System: Running in separate terminal
echo.
echo * Default admin login:
echo   Email: admin@example.com
echo   Password: admin123
echo.
echo * To view system logs, check the terminal windows.
echo * Press Ctrl+C in each terminal to stop the services.
echo ======================================================= 
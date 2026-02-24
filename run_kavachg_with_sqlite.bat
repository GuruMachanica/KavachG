@echo off
echo KavachG Safety Monitoring System - SQLite Edition
echo ==================================================
echo.

if "%1"=="" (
    echo Usage:
    echo   run_kavachg_with_sqlite.bat [command]
    echo.
    echo Available commands:
    echo   servers        - Start both backend (SQLite) and frontend servers
    echo   backend        - Start only backend server with SQLite
    echo   frontend       - Start only frontend server
    echo   fire           - Run fire detection on sample fire video
    echo   fall           - Run fall detection on sample fall video
    echo   ppe            - Run PPE detection (hard hat, vest detection)
    echo   all            - Run all-in-one detection with fire, fall, and PPE models
    echo   camera         - Run detection on webcam feed
    echo.
    echo Example: run_kavachg_with_sqlite.bat servers
    exit /b
)

REM Server commands
if "%1"=="servers" (
    echo Starting both backend and frontend servers...
    call start_servers_sqlite.bat
    exit /b
)

if "%1"=="backend" (
    echo Starting backend server with SQLite...
    cd backend && npm run start:sqlite
    exit /b
)

if "%1"=="frontend" (
    echo Starting frontend server...
    cd FrontEnd/FrontEnd && npm run dev
    exit /b
)

REM Detection commands
if "%1"=="fire" (
    echo Running Fire Detection with SQLite...
    call run_detection_sqlite.bat fire
    exit /b
)

if "%1"=="fall" (
    echo Running Fall Detection with SQLite...
    call run_detection_sqlite.bat fall
    exit /b
)

if "%1"=="ppe" (
    echo Running PPE Detection with SQLite...
    call run_detection_sqlite.bat ppe
    exit /b
)

if "%1"=="all" (
    echo Running All-in-One Detection with SQLite...
    call run_detection_sqlite.bat all
    exit /b
)

if "%1"=="camera" (
    echo Running Camera Feed Detection with SQLite...
    call run_detection_sqlite.bat camera
    exit /b
)

echo Unknown command: %1
echo Run 'run_kavachg_with_sqlite.bat' without arguments to see available commands.
exit /b 
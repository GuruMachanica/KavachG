@echo off
echo KavachG Safety Monitoring System (SQLite)
echo ===============================

if "%1"=="" (
    echo Usage:
    echo   run_detection_sqlite.bat [mode]
    echo.
    echo Available modes:
    echo   fire           - Run fire detection on sample fire video
    echo   fall           - Run fall detection on sample fall video
    echo   ppe            - Run PPE detection (hard hat, vest detection)
    echo   all            - Run all-in-one detection with fire, fall, and PPE models
    echo   camera         - Run detection on webcam feed
    echo.
    echo Example: run_detection_sqlite.bat fire
    exit /b
)

if "%1"=="fire" (
    echo Running Fire Detection with SQLite...
    cd ML && python run_safety_system_sqlite.py --source sample_test/Fire.mp4 --show --sector fire-detection
    exit /b
)

if "%1"=="fall" (
    echo Running Fall Detection with SQLite...
    cd ML && python run_safety_system_sqlite.py --source sample_test/fall.mp4 --show --sector fall-detection
    exit /b
)

if "%1"=="ppe" (
    echo Running PPE Detection with SQLite...
    cd ML && python run_safety_system_sqlite.py --source sample_test/Construct.mp4 --show --sector ppe-detection
    exit /b
)

if "%1"=="all" (
    echo Running All-in-One Detection with SQLite...
    cd ML && python run_safety_system_sqlite.py --source sample_test/Fire.mp4 --show --sector all-detections
    exit /b
)

if "%1"=="camera" (
    echo Running Camera Feed Detection with SQLite...
    cd ML && python run_safety_system_sqlite.py --source 0 --show --sector camera-feed
    exit /b
)

echo Unknown mode: %1
echo Run 'run_detection_sqlite.bat' without arguments to see available modes.
exit /b 
@echo off
echo KavachG Safety Monitoring System
echo ===============================
echo.

cd ML

IF "%1"=="fire" (
    echo Running Fire Detection...
    python run_safety_system.py --source sample_test/Fire.mp4 --show --sector fire-detection
) ELSE IF "%1"=="fall" (
    echo Running Fall Detection...
    python run_safety_system.py --source sample_test/fall.mp4 --show --sector fall-detection
) ELSE IF "%1"=="ppe" (
    echo Running PPE Detection...
    python run_safety_system.py --source sample_test/Construct.mp4 --show --sector ppe-detection
) ELSE IF "%1"=="all" (
    echo Running All-in-One Detector...
    python all_in_one_detector.py --source sample_test/Fire.mp4 --sector combined-detection
) ELSE IF "%1"=="camera" (
    echo Running Camera Feed Detection...
    python run_safety_system.py --source 0 --show --sector camera-feed
) ELSE (
    echo Usage: run_detection.bat [fire^|fall^|ppe^|all^|camera]
    echo.
    echo Examples:
    echo   run_detection.bat fire    - Run fire detection on Fire.mp4
    echo   run_detection.bat fall    - Run fall detection on fall.mp4
    echo   run_detection.bat ppe     - Run PPE detection on Construct.mp4
    echo   run_detection.bat all     - Run all-in-one detector
    echo   run_detection.bat camera  - Run detection on camera feed
)

cd ..
echo.
echo Detection complete. 
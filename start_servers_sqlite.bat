@echo off
echo KavachG Safety Monitoring System (SQLite)
echo ===============================

echo Starting backend server (SQLite)...
start cmd /k "cd backend && npm run start:sqlite"

echo Starting frontend server...
start cmd /k "cd FrontEnd/FrontEnd && npm run dev"

echo Servers started successfully!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Use Ctrl+C in the server windows to stop them.
echo. 
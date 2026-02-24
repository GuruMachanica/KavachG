@echo off
echo KavachG Server Startup
echo ====================
echo.

echo Starting Backend Server...
start cmd /k "cd backend && npm start"

echo Starting Frontend Server...
start cmd /k "cd FrontEnd/FrontEnd && npm start"

echo.
echo Servers started. You can access the dashboard at http://localhost:3000 
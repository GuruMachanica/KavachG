#!/bin/bash

echo "==================================================="
echo "KavachG Safety Monitoring System Deployment Script"
echo "==================================================="
echo

# Check prerequisites
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js."
    exit 1
fi

echo "Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "WARNING: MongoDB does not appear to be installed. The ML system needs MongoDB."
    echo "Please ensure MongoDB is running or install it:"
    echo "  - Ubuntu: sudo apt install mongodb"
    echo "  - macOS: brew install mongodb-community"
    echo
    read -p "Do you want to continue anyway? (y/n): " CONTINUE
    if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
        exit 1
    fi
fi

echo
echo "Deploying KavachG Safety Monitoring System..."
echo

# Setup environment variables
KAVACHG_ROOT=$(pwd)
BACKEND_PATH="$KAVACHG_ROOT/backend"
FRONTEND_PATH="$KAVACHG_ROOT/FrontEnd/FrontEnd"
ML_PATH="$KAVACHG_ROOT/ML"

# Start Backend (SQLite)
echo "Starting Backend (SQLite)..."
gnome-terminal -- bash -c "cd $BACKEND_PATH && echo '=== BACKEND SERVER ===' && npm install && node src/server-sqlite.js; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$BACKEND_PATH' && echo === BACKEND SERVER === && npm install && node src/server-sqlite.js"' 2>/dev/null || \
xterm -e "cd $BACKEND_PATH && echo === BACKEND SERVER === && npm install && node src/server-sqlite.js" 2>/dev/null || \
konsole --new-tab -e "cd $BACKEND_PATH && echo === BACKEND SERVER === && npm install && node src/server-sqlite.js" 2>/dev/null || \
(echo "Could not open a new terminal window. Starting in background..." && 
 cd "$BACKEND_PATH" && npm install && node src/server-sqlite.js &)

sleep 5

# Start Frontend
echo "Starting Frontend..."
gnome-terminal -- bash -c "cd $FRONTEND_PATH && echo '=== FRONTEND SERVER ===' && npm install && npm run dev; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$FRONTEND_PATH' && echo === FRONTEND SERVER === && npm install && npm run dev"' 2>/dev/null || \
xterm -e "cd $FRONTEND_PATH && echo === FRONTEND SERVER === && npm install && npm run dev" 2>/dev/null || \
konsole --new-tab -e "cd $FRONTEND_PATH && echo === FRONTEND SERVER === && npm install && npm run dev" 2>/dev/null || \
(echo "Could not open a new terminal window. Starting in background..." && 
 cd "$FRONTEND_PATH" && npm install && npm run dev &)

sleep 5

# Setup and start ML system
echo "Setting up ML environment..."
gnome-terminal -- bash -c "cd $ML_PATH && echo '=== ML SYSTEM ===' && python3 setup_env.py && python3 run_safety_system.py; bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd '$ML_PATH' && echo === ML SYSTEM === && python3 setup_env.py && python3 run_safety_system.py"' 2>/dev/null || \
xterm -e "cd $ML_PATH && echo === ML SYSTEM === && python3 setup_env.py && python3 run_safety_system.py" 2>/dev/null || \
konsole --new-tab -e "cd $ML_PATH && echo === ML SYSTEM === && python3 setup_env.py && python3 run_safety_system.py" 2>/dev/null || \
(echo "Could not open a new terminal window. Starting in background..." && 
 cd "$ML_PATH" && python3 setup_env.py && python3 run_safety_system.py &)

echo
echo "======================================================="
echo "KavachG System deployed successfully! Access points:"
echo "======================================================="
echo
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:5000"
echo "ML System: Running in separate terminal or background"
echo
echo "* Default admin login:"
echo "  Email: admin@example.com"
echo "  Password: admin123"
echo
echo "* To view system logs, check the terminal windows."
echo "* Press Ctrl+C in each terminal to stop the services."
echo "=======================================================" 
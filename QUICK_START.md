# KavachG Quick Start Guide

This guide provides the fastest way to get the KavachG Safety Monitoring System up and running.

## 1. Prerequisites Installation

### Windows

1. Install Node.js: Download and install from [nodejs.org](https://nodejs.org/)
2. Install Python: Download and install from [python.org](https://www.python.org/downloads/)
3. Install MongoDB: Download and install from [mongodb.com](https://www.mongodb.com/try/download/community)

### Linux (Ubuntu/Debian)

```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Python
sudo apt-get install -y python3 python3-pip python3-venv

# Install MongoDB
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### macOS

```bash
# Using Homebrew
brew install node
brew install python
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

## 2. Clone Repository

```bash
git clone https://github.com/yourusername/KavachG.git
cd KavachG
```

## 3. Deploy the System

### Easiest Method (Script)

#### Windows
```
deploy.bat
```

#### Linux/macOS
```bash
chmod +x deploy.sh
./deploy.sh
```

### Alternative: Manual Startup

Open three separate terminal windows:

#### Terminal 1 - Backend
```bash
cd backend
npm install
node src/server-sqlite.js
```

#### Terminal 2 - Frontend
```bash
cd FrontEnd/FrontEnd
npm install
npm run dev
```

#### Terminal 3 - ML System
```bash
cd ML
python setup_env.py
python run_safety_system.py
```

## 4. Access the Dashboard

1. Open your web browser
2. Navigate to: http://localhost:3000
3. Log in with default credentials:
   - Email: admin@example.com
   - Password: admin123

## 5. Test the System

1. Go to the "Monitoring" tab to see live video feeds
2. Go to the "Incidents" tab to view detected safety incidents
3. Try creating a test incident:
   ```bash
   cd FrontEnd/FrontEnd
   node test-api.js
   ```

## 6. Next Steps

1. Configure video sources in `ML/.env`
2. Add additional users through the settings page
3. Customize alert thresholds in the ML system config

## Troubleshooting

If you encounter issues:
1. Check that MongoDB is running
2. Verify all services are running in their respective terminals
3. Check browser console for frontend errors
4. Review `ML/logs/safety_system.log` for ML system errors

For more detailed instructions, refer to the full [README.md](README.md) file. 
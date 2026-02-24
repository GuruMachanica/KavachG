# KavachG Safety Monitoring System

KavachG is an integrated safety monitoring system that combines real-time AI-based detection with a user-friendly dashboard for workplace safety monitoring.

## System Components

The KavachG system consists of three main components:

1. **Backend** - Node.js/Express API server with SQLite or MongoDB database
2. **Frontend** - HTML/CSS/JavaScript web application with dashboard
3. **ML System** - Python-based machine learning system for detecting safety incidents

## Prerequisites

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **MongoDB** (v4.4 or higher) - Required for ML component
- **Camera** or video input sources (for production deployment)

## Deployment Options

There are multiple ways to deploy the KavachG system:

### 1. Using Deployment Scripts

#### Windows

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the KavachG root directory
3. Run the deployment script:
   ```
   deploy.bat
   ```

#### Linux/macOS

1. Open Terminal
2. Navigate to the KavachG root directory
3. Make the deployment script executable:
   ```
   chmod +x deploy.sh
   ```
4. Run the deployment script:
   ```
   ./deploy.sh
   ```

### 2. Using Docker Compose

For containerized deployment:

1. Install Docker and Docker Compose
2. Navigate to the KavachG root directory
3. Build and start the containers:
   ```
   docker-compose up -d
   ```
4. To stop the containers:
   ```
   docker-compose down
   ```

### 3. Manual Deployment

#### Backend (SQLite)

```bash
cd backend
npm install
node src/server-sqlite.js
```

#### Frontend

```bash
cd FrontEnd/FrontEnd
npm install
npm run dev
```

#### ML System

```bash
cd ML
python setup_env.py
python run_safety_system.py
```

## Accessing the System

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api-docs (if enabled)

## Default Login Credentials

- **Email**: admin@example.com
- **Password**: admin123

## System Configuration

### Backend Configuration

Environment variables for the backend can be set in a `.env` file in the backend directory:

```
PORT=5000
JWT_SECRET=your_jwt_secret
MONGODB_URI=mongodb://localhost:27017/safety_monitoring
```

### ML System Configuration

The ML system configuration is stored in `.env` file in the ML directory:

```
MONGODB_URI=mongodb://localhost:27017/safety_monitoring
BACKEND_URL=http://localhost:5000
VIDEO_SOURCE=0  # Use 0 for webcam, or provide a file path for video file
```

## Development Setup

For development, you can run each component separately:

1. Start MongoDB (needed for ML system)
2. Start the backend in development mode
3. Start the frontend in development mode
4. Start the ML system with test videos

## Troubleshooting

### Common Issues

1. **MongoDB Connection Issues**: Ensure MongoDB is running and accessible
2. **Video Source Not Found**: Check camera connections or video file paths
3. **Authentication Errors**: Verify the JWT_SECRET is consistent

### Logs

- Backend logs are output to the console or log files in the backend directory
- ML system logs are stored in the `ML/logs` directory

## License

Copyright (c) 2025 KavachG - All Rights Reserved 
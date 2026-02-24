# KavachG Comprehensive Deployment Guide

This guide provides detailed instructions for deploying the entire KavachG Safety Monitoring System, including all components: Frontend, Backend, and ML System.

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Deployment Options](#deployment-options)
3. [Basic Deployment (Script-based)](#basic-deployment-script-based)
4. [Manual Component Deployment](#manual-component-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Production Deployment Considerations](#production-deployment-considerations)
7. [Verification and Testing](#verification-and-testing)
8. [Troubleshooting](#troubleshooting)

## System Requirements

### Minimum Hardware Requirements
- **CPU**: Dual-core 2.0 GHz or higher
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 10 GB free space
- **Camera**: USB webcam or IP camera (for production)

### Software Prerequisites
- **Operating System**: Windows 10/11, Ubuntu 20.04+, or macOS 11+
- **Node.js**: Version 14.x or higher
- **Python**: Version 3.8 or higher
- **MongoDB**: Version 4.4 or higher (required for ML system)
- **Git**: For cloning the repository

## Deployment Options

The KavachG system can be deployed in several ways:

1. **Basic Deployment (Script-based)**: Easiest method using the provided deployment scripts
2. **Manual Component Deployment**: Running each component separately
3. **Docker Deployment**: Using Docker Compose for containerized deployment

## Basic Deployment (Script-based)

### On Windows

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the KavachG root directory
3. Run the deployment script:
   ```
   deploy.bat
   ```
4. Follow any on-screen prompts

### On Linux/macOS

1. Open Terminal
2. Navigate to the KavachG root directory
3. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```
4. Run the deployment script:
   ```bash
   ./deploy.sh
   ```
5. Follow any on-screen prompts

## Manual Component Deployment

For more control over the deployment process, you can deploy each component manually.

### 1. Start MongoDB (for ML System)

#### Windows
```
"C:\Program Files\MongoDB\Server\<version>\bin\mongod.exe" --dbpath="C:\data\db"
```

#### Linux
```bash
sudo systemctl start mongodb
```

#### macOS
```bash
brew services start mongodb-community
```

### 2. Deploy Backend Server

```bash
cd backend
npm install
node src/server-sqlite.js
```

The backend will be accessible at http://localhost:5000.

### 3. Deploy Frontend Server

```bash
cd FrontEnd/FrontEnd
npm install
npm run dev
```

The frontend will be accessible at http://localhost:3000.

### 4. Deploy ML System

```bash
cd ML
python setup_env.py
python run_safety_system.py
```

## Docker Deployment

For containerized deployment:

1. Ensure Docker and Docker Compose are installed
2. Navigate to the KavachG root directory
3. Build and start the containers:
   ```bash
   docker-compose up -d
   ```
4. To view logs for a specific service:
   ```bash
   docker-compose logs -f <service-name>
   ```
   Where `<service-name>` can be: `frontend`, `backend`, `mongodb`, or `ml-system`
5. To stop the containers:
   ```bash
   docker-compose down
   ```

## Production Deployment Considerations

For deploying in a production environment, consider the following additional steps:

### Security

1. **Use HTTPS**: Configure SSL certificates for both frontend and backend
2. **Environment Variables**: Store sensitive information in environment variables
3. **Firewall**: Configure firewalls to restrict access to necessary ports only
4. **Change Default Credentials**: Update default admin credentials immediately

### Performance

1. **Database Optimization**: Configure MongoDB for production use
2. **Load Balancing**: Set up a load balancer for the backend API
3. **Static Assets**: Use a CDN for static frontend assets

### Reliability

1. **Monitoring**: Set up system monitoring (e.g., Prometheus/Grafana)
2. **Backup**: Implement regular database backups
3. **Log Management**: Centralize logs using tools like ELK stack

## Verification and Testing

After deployment, verify that all components are working correctly:

```bash
python verify_deployment.py
```

This script checks:
- If all required processes are running
- If the MongoDB database is accessible
- If the backend API is responding
- If the frontend server is accessible
- If authentication is working

## Troubleshooting

### Common Issues

#### MongoDB Connection Errors
- Verify MongoDB is installed and running
- Check MongoDB connection URI in configuration files
- Ensure MongoDB port (27017) is not blocked by a firewall

#### Backend API Issues
- Check if the Node.js server is running
- Verify port 5000 is not in use by another application
- Check backend logs for error messages

#### Frontend Issues
- Ensure Node.js and npm are correctly installed
- Check if port 3000 is free
- Verify the frontend is configured to connect to the correct backend URL

#### ML System Issues
- Verify Python and required packages are installed
- Check ML system logs at `ML/logs/safety_system.log`
- Verify camera or video sources are accessible

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs for each component
2. Refer to component-specific documentation
3. Check the GitHub repository issues section
4. Contact the KavachG support team

---

For more information, see [README.md](README.md) and [QUICK_START.md](QUICK_START.md). 
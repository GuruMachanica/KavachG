FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MONGODB_URI=mongodb://admin:kavachg_admin_pwd@mongodb:27017/safety_monitoring?authSource=admin
ENV BACKEND_URL=http://backend:5000

# Run setup script
RUN python setup_env.py

# Start the ML system
CMD ["python", "run_safety_system.py"] 
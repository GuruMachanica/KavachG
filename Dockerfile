FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies (using libgl1 instead of obsolete libgl1-mesa-glx)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY Backend/requirements.txt /app/Backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/Backend/requirements.txt

COPY Backend/ /app/Backend/
COPY Models/ /app/Models/
COPY Database/ /app/Database/
COPY Frontend/ /app/Frontend/

EXPOSE 8000 5500

WORKDIR /app/Backend
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]

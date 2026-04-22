# Multi-stage Dockerfile for WhatsApp KYC System
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies for EasyOCR and image processing
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p data uploads logs

# Expose port for webhook service
EXPOSE 8000

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "src.webhook.app:app", "--host", "0.0.0.0", "--port", "8000"]

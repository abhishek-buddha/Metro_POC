# Metro KYC — single container: FastAPI + Extraction Worker + Redis
FROM python:3.11-slim

WORKDIR /app

# System dependencies: OpenCV libs + Redis server + Supervisor
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgl1 \
    redis-server \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create runtime directories
RUN mkdir -p data uploads logs

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/metro.conf

EXPOSE 8000

# Single entrypoint: supervisord manages Redis + API + Worker
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/metro.conf"]

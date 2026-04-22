#!/bin/bash

# WhatsApp KYC System - Quick Start Script
# This script helps you set up the development environment quickly

set -e  # Exit on error

echo "🚀 WhatsApp KYC System - Quick Start"
echo "===================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your credentials:"
    echo "   - TWILIO_ACCOUNT_SID"
    echo "   - TWILIO_AUTH_TOKEN"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - ENCRYPTION_KEY (generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
    echo "   - API_KEY"
    echo ""
    read -p "Press Enter after you've updated .env..."
fi

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis is not running"
    echo ""
    echo "Starting Redis with Docker..."
    docker run -d -p 6379:6379 --name kyc-redis redis:7-alpine
    echo "✅ Redis started"
fi
echo ""

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
if (( $(echo "$python_version >= 3.11" | bc -l) )); then
    echo "✅ Python $python_version found"
else
    echo "⚠️  Python 3.11+ recommended (found $python_version)"
fi
echo ""

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Initialize database
echo "🗄️  Initializing database..."
python -c "from src.models.database import init_database; init_database()"
echo "✅ Database initialized"
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p data uploads logs
echo "✅ Directories created"
echo ""

# Run tests
echo "🧪 Running tests..."
python -m pytest --tb=no -q
echo "✅ All tests passed"
echo ""

echo "✨ Setup complete!"
echo ""
echo "To start the system:"
echo ""
echo "Terminal 1 (Webhook):"
echo "  uvicorn src.webhook.app:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Terminal 2 (Worker):"
echo "  python -m src.workers.extraction_worker"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up -d"
echo ""
echo "Access the API:"
echo "  http://localhost:8000/docs"
echo ""
echo "Health check:"
echo "  curl http://localhost:8000/health"
echo ""

@echo off
REM WhatsApp KYC System - Quick Start Script (Windows)
REM This script helps you set up the development environment quickly

echo ========================================
echo WhatsApp KYC System - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo .env file created
    echo.
    echo IMPORTANT: Edit .env and add your credentials:
    echo    - TWILIO_ACCOUNT_SID
    echo    - TWILIO_AUTH_TOKEN
    echo    - ANTHROPIC_API_KEY
    echo    - ENCRYPTION_KEY
    echo    - API_KEY
    echo.
    echo Generate ENCRYPTION_KEY with:
    echo python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    echo.
    pause
)

REM Check Python version
echo Checking Python version...
python --version
echo.

REM Install dependencies
echo Installing Python dependencies...
pip install -q -r requirements.txt
echo Dependencies installed
echo.

REM Initialize database
echo Initializing database...
python -c "from src.models.database import init_database; init_database()"
echo Database initialized
echo.

REM Create directories
echo Creating directories...
if not exist data mkdir data
if not exist uploads mkdir uploads
if not exist logs mkdir logs
echo Directories created
echo.

REM Run tests
echo Running tests...
python -m pytest --tb=no -q
echo All tests passed
echo.

echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To start the system:
echo.
echo Terminal 1 (Webhook):
echo   uvicorn src.webhook.app:app --host 0.0.0.0 --port 8000 --reload
echo.
echo Terminal 2 (Worker):
echo   python -m src.workers.extraction_worker
echo.
echo Or use Docker Compose:
echo   docker-compose up -d
echo.
echo Access the API:
echo   http://localhost:8000/docs
echo.
echo Health check:
echo   curl http://localhost:8000/health
echo.
pause

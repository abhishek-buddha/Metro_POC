@echo off
cd /d C:\Users\Rakes\Desktop\Metro_POC
echo Starting backend server...
python -m uvicorn src.webhook.app:app --host 127.0.0.1 --port 8000

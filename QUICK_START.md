# Quick Start Guide

## 5-Minute Setup (Development)

### Step 1: Get Your API Keys

1. **Twilio (WhatsApp):**
   - Sign up at https://www.twilio.com/try-twilio
   - Get Account SID and Auth Token from Console Dashboard
   - Join WhatsApp Sandbox: Send "join <code>" to +1 415 523 8886

2. **Anthropic (Claude Vision):**
   - Sign up at https://console.anthropic.com/
   - Create API key (starts with `sk-ant-api03-`)

### Step 2: Configure Environment

```bash
# Copy template
cp .env.example .env

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Edit .env and paste your credentials
```

### Step 3: Run Setup Script

**Windows:**
```cmd
quick-start.bat
```

**Linux/Mac:**
```bash
chmod +x quick-start.sh
./quick-start.sh
```

### Step 4: Start Services

**Option A: Docker (Recommended)**
```bash
docker-compose up -d
```

**Option B: Manual**
```bash
# Terminal 1 - Start webhook
uvicorn src.webhook.app:app --reload

# Terminal 2 - Start worker
python -m src.workers.extraction_worker
```

### Step 5: Test It

```bash
# Health check
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", "redis": "connected", "database": "connected"}
```

### Step 6: Configure Twilio Webhook

1. Go to Twilio Console → Messaging → WhatsApp sandbox settings
2. Set webhook URL to: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`
3. Or use ngrok: `ngrok http 8000`

### Step 7: Send Test Document

Send a WhatsApp message with a document photo to your Twilio sandbox number!

---

## What Happens Next?

1. **User sends document** → Twilio receives it
2. **Webhook receives message** → Downloads document, creates job in Redis
3. **Worker picks up job** → Classifies document (PAN/Aadhaar/Bank)
4. **Extracts data** → Using OCR or AI
5. **Validates & encrypts** → Stores in database
6. **Sends confirmation** → WhatsApp message to user

---

## View Results

**REST API:**
```bash
# List all submissions
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions

# Get specific submission
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions/{id}

# API Documentation
open http://localhost:8000/docs
```

**Database:**
```bash
# View SQLite database
sqlite3 data/kyc.db

# Query submissions
SELECT * FROM kyc_submissions;

# Query documents
SELECT * FROM documents;
```

**Logs:**
```bash
# Webhook logs
docker-compose logs -f webhook

# Worker logs
docker-compose logs -f worker-1

# All logs
docker-compose logs -f
```

---

## Architecture Overview

```
┌─────────────┐
│  WhatsApp   │ User sends document
│    User     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Twilio    │ Forwards to webhook
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ Receives, downloads, queues
│  Webhook    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Redis     │ Job queue
│   Queue     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Worker    │ Classify → Extract → Store
│  (3x Pool)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │ Encrypted storage
│  (SQLite)   │
└─────────────┘
```

---

## Troubleshooting

### "Redis connection failed"
```bash
# Start Redis with Docker
docker run -d -p 6379:6379 --name kyc-redis redis:7-alpine
```

### "Environment variable not set"
```bash
# Verify .env file exists and has correct values
cat .env
```

### "Twilio signature validation failed"
- Check TWILIO_AUTH_TOKEN is correct
- Ensure webhook URL matches exactly
- Check Twilio console webhook configuration

### "Worker not processing jobs"
```bash
# Check worker is running
ps aux | grep extraction_worker

# Check Redis queue
redis-cli LLEN kyc:jobs

# Manually start worker
python -m src.workers.extraction_worker
```

---

## Production Deployment

See **DEPLOYMENT.md** for:
- Production server setup
- PostgreSQL migration
- Monitoring & logging
- Backup strategies
- Scaling guidelines
- Security hardening

---

## Need Help?

1. Check **DEPLOYMENT.md** for detailed instructions
2. Review logs: `docker-compose logs -f`
3. Test endpoints: http://localhost:8000/docs
4. Check Redis: `redis-cli MONITOR`
5. View database: `sqlite3 data/kyc.db`

---

## Next Steps

1. ✅ System is running locally
2. 📱 Test with real WhatsApp messages
3. 🔐 Review security settings in DEPLOYMENT.md
4. 🚀 Deploy to production server
5. 📊 Set up monitoring and alerts
6. 🎯 Integrate with your HRMS via REST API

**Your WhatsApp KYC system is ready!** 🎉

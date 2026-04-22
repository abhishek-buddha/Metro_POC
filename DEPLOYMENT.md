# WhatsApp KYC System - Deployment Guide

## Quick Start (Local Development)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd C:\Users\Rakes\Desktop\Metro_POC

# Install Python packages
pip install -r requirements.txt

# Install EasyOCR (if not already installed)
pip install easyocr
```

### Step 2: Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886  # Twilio Sandbox number

# Anthropic API (Claude Vision)
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# Security
ENCRYPTION_KEY=your-32-byte-fernet-key-here
API_KEY=your-api-key-for-rest-endpoints

# Redis
REDIS_URL=redis://localhost:6379/0

# Database
DATABASE_PATH=data/kyc.db

# Storage
UPLOADS_PATH=uploads

# Logging
LOG_LEVEL=INFO
```

### Step 3: Generate Encryption Key

```bash
# Generate a Fernet encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Copy the output to ENCRYPTION_KEY in .env
```

### Step 4: Start Redis

**Option A: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name kyc-redis redis:7-alpine
```

**Option B: Windows Redis**
```bash
# Download from: https://github.com/microsoftarchive/redis/releases
# Or use WSL2 and install redis-server
```

**Option C: Use Memurai (Redis for Windows)**
```bash
# Download from: https://www.memurai.com/
```

### Step 5: Initialize Database

```bash
# Run database initialization
python -c "from src.models.database import init_database; init_database()"
```

### Step 6: Start the Services

**Terminal 1 - Webhook Service:**
```bash
uvicorn src.webhook.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Worker Process:**
```bash
python -m src.workers.extraction_worker
```

**Terminal 3 (Optional) - Additional Workers:**
```bash
python -m src.workers.extraction_worker
python -m src.workers.extraction_worker
```

### Step 7: Test the System

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "database": "connected"
}
```

---

## Production Deployment with Docker

### Step 1: Configure Production Environment

Create `.env` with production credentials (see Step 2 above).

### Step 2: Build and Start Services

```bash
# Build Docker image
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Services Started:**
- `kyc-redis` - Redis (port 6379)
- `kyc-webhook` - FastAPI (port 8000)
- `kyc-worker-1, kyc-worker-2, kyc-worker-3` - Background workers

### Step 3: View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f webhook
docker-compose logs -f worker-1
```

### Step 4: Stop Services

```bash
# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Twilio WhatsApp Setup

### Option A: Twilio Sandbox (Testing)

1. **Create Twilio Account:**
   - Go to https://www.twilio.com/try-twilio
   - Sign up for free trial

2. **Access WhatsApp Sandbox:**
   - Go to Console → Messaging → Try it out → Send a WhatsApp message
   - Join sandbox: Send "join <your-code>" to +1 415 523 8886

3. **Configure Webhook:**
   - In Twilio Console → Messaging → Settings → WhatsApp sandbox settings
   - Set "When a message comes in" to: `https://your-domain.com/webhook/whatsapp`
   - Method: POST

4. **Get Credentials:**
   ```
   TWILIO_ACCOUNT_SID: Found in Console Dashboard
   TWILIO_AUTH_TOKEN: Found in Console Dashboard (click "Show")
   TWILIO_WHATSAPP_NUMBER: whatsapp:+14155238886
   ```

### Option B: Meta WhatsApp Business API (Production)

1. **Prerequisites:**
   - Facebook Business Manager account
   - Verified business
   - Phone number not already on WhatsApp

2. **Setup Steps:**
   - Go to https://business.facebook.com/
   - Create WhatsApp Business Account
   - Apply for WhatsApp Business API access
   - Configure messaging templates (requires approval)
   - Get API credentials

3. **Update Configuration:**
   ```env
   TWILIO_WHATSAPP_NUMBER=whatsapp:+91YOUR_BUSINESS_NUMBER
   ```

---

## Anthropic API Setup

1. **Create Account:**
   - Go to https://console.anthropic.com/
   - Sign up and verify email

2. **Generate API Key:**
   - Go to API Keys section
   - Click "Create Key"
   - Copy the key (starts with `sk-ant-api03-`)

3. **Add to .env:**
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
   ```

4. **Verify Access:**
   ```bash
   python -c "from anthropic import Anthropic; client = Anthropic(api_key='YOUR_KEY'); print('API Key Valid')"
   ```

---

## Exposing Webhook to Internet

Twilio needs to reach your webhook. Choose one option:

### Option A: ngrok (Development/Testing)

```bash
# Install ngrok: https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Set in Twilio: https://abc123.ngrok.io/webhook/whatsapp
```

### Option B: Production Server

**Using DigitalOcean/AWS/Azure:**

1. Deploy Docker Compose to server
2. Set up nginx reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Enable HTTPS with Let's Encrypt:
```bash
certbot --nginx -d your-domain.com
```

### Option C: Railway/Render/Fly.io

**Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway up
```

**Render:**
1. Connect GitHub repo
2. Create new Web Service
3. Set environment variables
4. Deploy

---

## Testing End-to-End Flow

### 1. Send Document via WhatsApp

Send a message with photo to your Twilio number:
```
Message: "Here is my PAN card"
Attachment: [PAN card photo]
```

### 2. Check Webhook Logs

```bash
docker-compose logs -f webhook
```

Look for:
```
INFO: Webhook received from +919876543210
INFO: Media downloaded: uploads/+919876543210/abc123.jpg
INFO: Job created: job-abc123
```

### 3. Check Worker Logs

```bash
docker-compose logs -f worker-1
```

Look for:
```
INFO: Processing job job-abc123
INFO: Classification complete: PAN_CARD (confidence: 0.95)
INFO: Extraction complete
INFO: Data stored in database
INFO: Confirmation sent
```

### 4. Verify Database

```bash
# Access SQLite database
sqlite3 data/kyc.db

# Check submissions
SELECT * FROM kyc_submissions;

# Check documents
SELECT * FROM documents;
```

### 5. Test REST API

```bash
# List submissions
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions

# Get specific submission
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/submissions/{id}

# Review submission
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"status": "APPROVED", "notes": "All documents verified"}' \
  http://localhost:8000/api/submissions/{id}/review
```

---

## Production Checklist

### Security

- [ ] Change default API_KEY
- [ ] Generate strong ENCRYPTION_KEY
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set up firewall rules
- [ ] Restrict database access
- [ ] Enable Redis authentication
- [ ] Set up VPN for admin access

### Monitoring

- [ ] Set up health check monitoring (UptimeRobot, Pingdom)
- [ ] Configure log aggregation (ELK, Datadog)
- [ ] Set up error alerts (Sentry, Rollbar)
- [ ] Monitor Redis memory usage
- [ ] Monitor disk space for uploads/

### Backup

- [ ] Set up daily database backups
- [ ] Back up encryption keys securely
- [ ] Back up uploaded documents to S3/Azure Blob
- [ ] Test restore procedure

### Scaling

- [ ] Migrate to PostgreSQL (production database)
- [ ] Set up Redis cluster (high availability)
- [ ] Add load balancer for webhook
- [ ] Scale worker count based on queue depth
- [ ] Set up CDN for document delivery

### Compliance

- [ ] Document data retention policy
- [ ] Set up audit log retention
- [ ] Configure automatic PII deletion
- [ ] Implement GDPR/DPDP compliance
- [ ] Regular security audits

---

## Upgrading to Production Database (PostgreSQL)

### 1. Install PostgreSQL

**Docker:**
```bash
docker run -d \
  --name kyc-postgres \
  -e POSTGRES_DB=kyc \
  -e POSTGRES_USER=kycuser \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15
```

### 2. Update Configuration

```env
DATABASE_PATH=postgresql://kycuser:secure_password@localhost:5432/kyc
```

### 3. Update docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: kyc
      POSTGRES_USER: kycuser
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres-data:
```

### 4. Migrate Data

```bash
# Export from SQLite
sqlite3 data/kyc.db .dump > backup.sql

# Convert and import to PostgreSQL
# (Manual conversion needed for SQLite → PostgreSQL syntax)
```

---

## Troubleshooting

### Problem: "Redis connection failed"

**Solution:**
```bash
# Check Redis is running
docker ps | grep redis

# Test Redis connection
redis-cli ping

# Restart Redis
docker restart kyc-redis
```

### Problem: "TWILIO_ACCOUNT_SID not set"

**Solution:**
```bash
# Verify .env file exists
ls -la .env

# Check environment variables are loaded
python -c "from src.utils.config import config; print(config.TWILIO_ACCOUNT_SID)"
```

### Problem: "EasyOCR model download fails"

**Solution:**
```bash
# Download models manually
mkdir -p ~/.EasyOCR/model

# Models will be downloaded on first use
# Ensure internet connection and sufficient disk space
```

### Problem: "Twilio webhook returns 401"

**Solution:**
- Check Twilio signature verification
- Verify webhook URL in Twilio console
- Check logs for signature validation errors
- Ensure TWILIO_AUTH_TOKEN is correct

### Problem: "Worker not processing jobs"

**Solution:**
```bash
# Check worker is running
docker-compose ps

# Check Redis queue
redis-cli LLEN kyc:jobs

# Check worker logs
docker-compose logs worker-1

# Manually pop job for debugging
redis-cli BLPOP kyc:jobs 0
```

---

## Cost Estimates

### Development/Testing (10-50 employees)

- **Twilio Sandbox:** Free
- **Anthropic API:** ~$0.01 per bank document
- **Server:** $0 (local) or $5-10/month (cloud)
- **Redis:** $0 (self-hosted Docker)
- **Total:** ~$10-20/month

### Production (100-1000 employees)

- **Twilio WhatsApp Business:** $0.005 per message
- **Anthropic API:** ~$0.01 per bank document
- **Server:** $20-50/month (2GB RAM, 2 vCPU)
- **PostgreSQL:** $15/month (managed database)
- **Redis:** $10/month (managed Redis)
- **S3 Storage:** $5/month (for documents)
- **Total:** ~$50-100/month + usage

---

## Support & Documentation

- **Project GitHub:** (Your repository)
- **API Documentation:** http://localhost:8000/docs (FastAPI auto-generated)
- **Twilio Docs:** https://www.twilio.com/docs/whatsapp
- **Anthropic Docs:** https://docs.anthropic.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/

---

## Next Features (Future Enhancements)

1. **Web Dashboard:** React/Vue.js UI for HRMS staff
2. **Bulk Upload:** CSV import for employee data
3. **Email Notifications:** Alternative to WhatsApp
4. **Multi-language:** Support for regional languages
5. **Mobile App:** Native iOS/Android apps
6. **Analytics:** Usage statistics and reporting
7. **Webhook Events:** Real-time updates for HRMS
8. **Document Templates:** Customizable extraction rules

---

**Need Help?** Check logs, review error messages, and consult the troubleshooting section above.

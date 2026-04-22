# WhatsApp KYC Automation System

Production-ready Know Your Customer (KYC) automation system using WhatsApp, OCR, and AI document analysis. Automates the collection and verification of identity documents (PAN, Aadhaar) and bank statements through conversational WhatsApp interactions.

## Features

- **WhatsApp Integration**: Native WhatsApp chat interface via Twilio
- **Document OCR**: Automatic extraction of PAN and Aadhaar card data using EasyOCR
- **AI Document Analysis**: Bank statement processing using Claude Vision API
- **REST API**: Complete REST API for integration with external systems
- **Job Queue**: Redis-based async job processing with status tracking
- **Database**: SQLite with structured KYC submission records
- **Security**: AES encryption for sensitive data, API key authentication
- **Docker Deployment**: Complete Docker Compose setup for production deployment

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for containerized deployment)
- Twilio account with WhatsApp enabled
- Anthropic API key (Claude Vision)

### Local Development Setup

1. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd whatsapp-kyc-system
```

2. Create Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your actual credentials:
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER
# - ANTHROPIC_API_KEY
# - ENCRYPTION_KEY (generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
# - API_KEY (any secure string for API authentication)
```

5. Create required directories:
```bash
mkdir -p data uploads
```

6. Initialize the database:
```bash
python src/initialize_db.py
```

7. Start Redis (using Docker):
```bash
docker run -d -p 6379:6379 redis:latest
```

8. Run the application:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

9. Start the job worker (in another terminal):
```bash
python src/workers/job_worker.py
```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

### Docker Deployment

Build and run using Docker Compose:
```bash
docker-compose up -d
```

The system will be available at `http://localhost:8000`.

## API Endpoints

### WhatsApp Webhook
- `POST /webhook/whatsapp` - Receive and process WhatsApp messages

### KYC Submissions
- `GET /api/submissions` - List all submissions
- `GET /api/submissions/{submission_id}` - Get submission details
- `POST /api/submissions` - Create new submission
- `GET /api/submissions/{submission_id}/status` - Get submission processing status
- `POST /api/submissions/{submission_id}/process` - Trigger manual processing

### Documents
- `GET /api/submissions/{submission_id}/documents` - List submission documents
- `POST /api/submissions/{submission_id}/documents` - Upload document
- `GET /api/documents/{document_id}` - Get document details
- `DELETE /api/documents/{document_id}` - Delete document

### Processing Jobs
- `GET /api/jobs/{job_id}` - Get job status and results
- `GET /api/jobs/submission/{submission_id}` - Get jobs for submission

### Health
- `GET /health` - System health check

## Tech Stack

- **Backend**: FastAPI 0.109.0, Python 3.11
- **Database**: SQLite with SQLAlchemy ORM
- **Task Queue**: Redis 5.0.1
- **OCR**: EasyOCR 1.7.0, OpenCV
- **AI**: Anthropic Claude Vision API (anthropic==0.18.1)
- **WhatsApp**: Twilio 8.11.1
- **Security**: Cryptography (AES encryption)
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest, pytest-asyncio, httpx

## Architecture

```
whatsapp-kyc-system/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database setup
│   ├── models/                # SQLAlchemy models
│   │   ├── submission.py      # KYC submission model
│   │   └── document.py        # Document model
│   ├── services/              # Business logic
│   │   ├── ocr_service.py     # PAN/Aadhaar extraction
│   │   ├── document_analyzer.py # Bank statement analysis
│   │   ├── kyc_service.py     # KYC processing
│   │   └── encryption_service.py # Data encryption
│   ├── utils/                 # Utility functions
│   │   └── validators.py      # Data validation
│   ├── webhook/               # WhatsApp webhook handlers
│   │   └── whatsapp.py        # Twilio webhook
│   └── workers/               # Background job workers
│       └── job_worker.py      # Redis job processor
├── tests/                     # Test suite
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## Environment Variables

All configuration is managed through environment variables (see `.env.example`):

| Variable | Description | Example |
|----------|-------------|---------|
| TWILIO_ACCOUNT_SID | Twilio account ID | ACxxxxx... |
| TWILIO_AUTH_TOKEN | Twilio authentication token | your_token |
| TWILIO_WHATSAPP_NUMBER | Your Twilio WhatsApp number | whatsapp:+14155238886 |
| ANTHROPIC_API_KEY | Claude API key | sk-ant-api03-... |
| ENCRYPTION_KEY | Fernet encryption key for sensitive data | Base64 encoded key |
| API_KEY | API authentication key | any-secure-string |
| REDIS_URL | Redis connection URL | redis://localhost:6379 |
| DATABASE_PATH | SQLite database file path | ./data/kyc.db |
| UPLOADS_PATH | Directory for document uploads | ./uploads |
| LOG_LEVEL | Logging level | INFO |

## Usage Example

### WhatsApp Interaction Flow

1. User sends a WhatsApp message: "I want to submit KYC"
2. Bot responds with document requirements
3. User uploads PAN card image
4. System extracts PAN details using OCR
5. User uploads Aadhaar card image
6. System extracts Aadhaar details using OCR
7. User uploads bank statement
8. System analyzes statement using Claude Vision API
9. System validates all documents and data
10. System returns verification results

### REST API Usage

**Create a KYC submission:**
```bash
curl -X POST http://localhost:8000/api/submissions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "phone_number": "919876543210",
    "document_types": ["PAN", "AADHAAR", "BANK_STATEMENT"]
  }'
```

**Upload a document:**
```bash
curl -X POST http://localhost:8000/api/submissions/{submission_id}/documents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@path/to/document.jpg" \
  -F "document_type=PAN"
```

**Check processing status:**
```bash
curl -X GET http://localhost:8000/api/submissions/{submission_id}/status \
  -H "Authorization: Bearer YOUR_API_KEY"
```

## Testing

Run the test suite:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=src tests/
```

Run specific test file:
```bash
pytest tests/test_ocr_service.py -v
```

## Security Considerations

- All sensitive data (PAN, Aadhaar) is encrypted at rest using AES encryption
- API endpoints require authentication via API_KEY header
- WhatsApp messages are signed and verified using Twilio tokens
- Environment variables must never be committed to version control
- Production deployment should use environment-specific .env files
- Enable HTTPS/TLS in production
- Implement rate limiting on API endpoints
- Regular security audits recommended

## Troubleshooting

### Redis Connection Error
Ensure Redis is running:
```bash
docker run -d -p 6379:6379 redis:latest
```

### Database Locked Error
Stop any other instances and delete `.db-journal` file:
```bash
rm data/kyc.db-journal
```

### OCR Model Download
EasyOCR automatically downloads models on first use (requires internet connection and disk space).

### WhatsApp Webhook Not Receiving Messages
- Verify Twilio webhook URL is publicly accessible
- Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env
- Ensure firewall allows inbound connections on port 8000

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "Add your feature"`
3. Push to remote: `git push origin feature/your-feature`
4. Open pull request

## License

Proprietary - All rights reserved

## Support

For issues, questions, or contributions, please contact the development team.

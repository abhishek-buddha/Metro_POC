# Developer Setup Guide
## Accessing KYC Database

---

## 🎯 Two Ways to Access Data

### **Option A: Local Database Access** (Offline, Full SQL Access)

**Use when:** Testing locally, writing queries, debugging

**Setup:**
1. You should have received `kyc.db` file
2. Place it in: `Metro_POC/data/kyc.db`
3. Install DB Browser: https://sqlitebrowser.org/dl/
4. Open DB Browser → Open Database → Select `data/kyc.db`
5. Browse tables and run queries

**Connection String (Python):**
```python
from sqlalchemy import create_engine
engine = create_engine('sqlite:///data/kyc.db')
```

**No credentials needed!** It's just a file.

---

### **Option B: Remote API Access** (Real-time, Live Data)

**Use when:** Need latest data, testing integrations

**Setup:**
1. Get API URL from team lead (e.g., `http://192.168.1.100:8000`)
2. Get API Key: `metro-kyc-secure-key-2026`
3. Install Postman: https://www.postman.com/downloads/
4. Import collection: `KYC_API_Postman_Collection.json`
5. Set `base_url` variable to API URL
6. Test: `GET /health`

**Example API Call:**
```bash
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://192.168.1.100:8000/api/submissions
```

---

## 📊 Database Schema

**Tables:**
```
employees         - Employee records (phone_number is unique ID)
kyc_submissions   - KYC data (one per employee)
documents         - Document metadata and file paths
audit_logs        - All system actions
```

**Key Relationships:**
```
employees (1) ──→ (1) kyc_submissions
             └──→ (many) documents
```

---

## 🔍 Useful Queries

**View all submissions:**
```sql
SELECT
  e.phone_number,
  s.aadhaar_name,
  s.pan_name,
  s.bank_holder_name,
  s.status,
  s.overall_confidence
FROM kyc_submissions s
JOIN employees e ON s.employee_id = e.id;
```

**Count by status:**
```sql
SELECT status, COUNT(*)
FROM kyc_submissions
GROUP BY status;
```

**Recent submissions:**
```sql
SELECT
  e.phone_number,
  s.submitted_at,
  s.status
FROM kyc_submissions s
JOIN employees e ON s.employee_id = e.id
ORDER BY s.submitted_at DESC
LIMIT 10;
```

---

## 🔐 Encrypted Fields

These fields are encrypted in the database:
- `pan_number_encrypted` - Encrypted PAN number
- `bank_account_encrypted` - Encrypted bank account

**You'll see gibberish like:**
```
gAAAAABm1x2Y3kK9mN... (encrypted data)
```

**To decrypt (Python):**
```python
from src.services.encryption import decrypt_field
decrypted = decrypt_field(encrypted_value)
```

**Note:** You need the `ENCRYPTION_KEY` from `.env` to decrypt.

---

## 🚀 Running the System Locally

If you want to run the full system:

**Prerequisites:**
- Python 3.11+
- Redis (Docker or local)
- OpenAI API key

**Setup:**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your keys

# 3. Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# 4. Start webhook (Terminal 1)
python -m uvicorn src.webhook.app:app --reload

# 5. Start worker (Terminal 2)
python -m src.workers.extraction_worker
```

---

## 📞 Support

**Questions?** Ask on team Slack/Teams

**Issues?** Check:
- Is database file in correct location?
- Is API URL correct?
- Is API key correct?

---

## 🔒 Security Notes

**DO:**
- ✅ Keep API key secure
- ✅ Only use on trusted networks
- ✅ Delete test database after use

**DON'T:**
- ❌ Commit database file to public Git
- ❌ Share API key publicly
- ❌ Use production data for testing

---

**Document Version:** 1.0
**Last Updated:** 2026-04-17

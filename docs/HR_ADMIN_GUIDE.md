# HR/Admin KYC Management Guide
## System Administration & Review Process

---

## 🎯 Overview

This guide is for HR personnel and administrators who review and manage employee KYC submissions.

**System Capabilities:**
- Automated document classification (Aadhaar/PAN/Bank)
- AI-powered data extraction using OpenAI GPT-4 Vision
- Encrypted storage of sensitive information
- RESTful API for accessing submissions
- WhatsApp notifications to employees

---

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Reviewing Submissions](#reviewing-submissions)
3. [API Reference](#api-reference)
4. [Troubleshooting](#troubleshooting)
5. [Security Guidelines](#security-guidelines)

---

## 🔄 Daily Operations

### Step 1: Check for New Submissions

**Via API:**
```bash
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://localhost:8000/api/submissions
```

**Response:**
```json
{
  "submissions": [
    {
      "id": "abc-123-xyz",
      "phone_number": "+919063555464",
      "status": "PENDING",
      "overall_confidence": 0.9,
      "submitted_at": "2026-04-17T10:03:36"
    }
  ],
  "total": 1
}
```

### Step 2: Review Each Submission

For each pending submission, review the extracted data and documents.

---

## 🔍 Reviewing Submissions

### Get Submission Details

**API Call:**
```bash
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://localhost:8000/api/submissions/abc-123-xyz
```

**Response Includes:**

#### Aadhaar Data:
- `aadhaar_last4`: Last 4 digits (e.g., "8182")
- `aadhaar_name`: Full name
- `aadhaar_dob`: Date of birth (DD/MM/YYYY)
- `aadhaar_gender`: Male/Female
- `aadhaar_address`: Full address
- `aadhaar_confidence`: 0.0 to 1.0

#### PAN Data:
- `pan_number_encrypted`: Encrypted PAN (decrypt when needed)
- `pan_name`: Name on PAN card
- `pan_father_name`: Father's name
- `pan_dob`: Date of birth
- `pan_confidence`: 0.0 to 1.0

#### Bank Data:
- `bank_account_encrypted`: Encrypted account number
- `bank_holder_name`: Account holder name
- `bank_ifsc`: IFSC code
- `bank_name`: Bank name
- `bank_branch`: Branch name
- `bank_account_type`: Savings/Current
- `bank_confidence`: 0.0 to 1.0

#### Overall:
- `name_match_score`: Cross-document name matching (0.0 to 1.0)
- `overall_confidence`: Combined confidence score
- `status`: PENDING, APPROVED, or REJECTED

### Review Checklist

For each submission, verify:

#### 1. **Identity Verification**
- [ ] Aadhaar name matches PAN name (≥80% match)
- [ ] Aadhaar name matches bank holder name (≥80% match)
- [ ] Date of birth is consistent across documents
- [ ] Photo quality is acceptable

#### 2. **Document Validity**
- [ ] Aadhaar number is valid (12 digits)
- [ ] PAN format is correct (ABCDE1234F)
- [ ] IFSC code is valid (11 characters)
- [ ] All required fields are present

#### 3. **Confidence Scores**
- [ ] Overall confidence ≥ 0.7 (acceptable)
- [ ] If confidence < 0.7, manually verify document images
- [ ] Check individual document confidences

#### 4. **Red Flags** ⚠️
- Name mismatch across documents (< 80% match)
- Blurry or unclear document images
- Missing critical information
- Suspiciously low confidence scores
- Inconsistent dates of birth

---

## 📊 Approval Process

### Option 1: Approve Submission

**API Call:**
```bash
curl -X POST \
  -H "X-API-Key: metro-kyc-secure-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "APPROVED",
    "reviewed_by": "hr@company.com",
    "review_notes": "All documents verified and approved"
  }' \
  http://localhost:8000/api/submissions/abc-123-xyz/review
```

**Result:**
- Status changes to APPROVED
- Employee receives WhatsApp notification
- Audit log entry created

### Option 2: Reject Submission

**API Call:**
```bash
curl -X POST \
  -H "X-API-Key: metro-kyc-secure-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "REJECTED",
    "reviewed_by": "hr@company.com",
    "review_notes": "Aadhaar photo unclear, PAN name mismatch"
  }' \
  http://localhost:8000/api/submissions/abc-123-xyz/review
```

**Result:**
- Status changes to REJECTED
- Review notes saved for reference
- Employee should be contacted to resubmit

### Option 3: Request Resubmission

If documents need to be resubmitted:
1. Reject the submission with clear notes
2. Contact employee via WhatsApp/email
3. Explain which documents need resubmission
4. Employee sends new photos (creates new submission)

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000
```

### Authentication
All API calls require header:
```
X-API-Key: metro-kyc-secure-key-2026
```

### Endpoints

#### 1. List All Submissions
```bash
GET /api/submissions?status=PENDING&limit=50&offset=0
```

**Query Parameters:**
- `status`: PENDING, APPROVED, or REJECTED (optional)
- `limit`: Max results (default: 50)
- `offset`: Pagination offset (default: 0)

#### 2. Get Submission Details
```bash
GET /api/submissions/{submission_id}
```

Returns complete submission data including all documents.

#### 3. Get Employee Details
```bash
GET /api/employees/{phone_number}
```

Returns employee profile and all their submissions.

#### 4. Review Submission
```bash
POST /api/submissions/{submission_id}/review
Content-Type: application/json

{
  "status": "APPROVED|REJECTED",
  "reviewed_by": "reviewer@company.com",
  "review_notes": "Optional notes"
}
```

#### 5. Health Check
```bash
GET /health
```

Returns system status (Redis, Database connectivity).

#### 6. Get Audit Logs
```bash
GET /api/audit-logs?employee_id={id}&limit=100
```

Returns audit trail for compliance.

---

## 📈 Monitoring & Reports

### Daily Report

**Get today's submissions:**
```bash
# Count by status
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     "http://localhost:8000/api/submissions?status=PENDING" | \
     jq '.total'

# Export to CSV (example)
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     "http://localhost:8000/api/submissions?limit=1000" | \
     jq -r '.submissions[] | [.phone_number, .status, .overall_confidence, .submitted_at] | @csv'
```

### Key Metrics to Track

1. **Submission Volume**
   - Total submissions per day
   - Pending vs Approved vs Rejected

2. **Processing Quality**
   - Average confidence score
   - Rejection rate
   - Common rejection reasons

3. **Response Time**
   - Time from submission to review
   - Time to approval/rejection

4. **System Health**
   - API uptime
   - Processing errors
   - WhatsApp delivery rate

---

## 🔧 Troubleshooting

### Issue: Low Confidence Scores

**Symptoms:** Multiple submissions with confidence < 0.7

**Causes:**
1. Poor photo quality from employees
2. OCR failing, AI not triggering
3. Unusual document formats

**Solutions:**
1. Send photo guidelines to employees (use EMPLOYEE_KYC_GUIDE.md)
2. Check worker logs for AI fallback activation
3. Manually review document images
4. Request clearer photos from employee

### Issue: Name Mismatch Alerts

**Symptoms:** `name_match_score` < 0.8

**Causes:**
1. Spelling variations (e.g., "Rakesh" vs "Rakesh Kumar")
2. Name change after marriage
3. Shortened names on documents

**Solutions:**
1. Manually verify names are for same person
2. Check middle name variations
3. Contact employee for clarification if needed
4. Document reason in review notes

### Issue: System Not Processing Documents

**Check:**
```bash
# 1. Check webhook status
curl http://localhost:8000/health

# 2. Check Redis connectivity
redis-cli ping

# 3. Check worker logs
tail -f logs/worker.log

# 4. Check for stuck jobs
redis-cli LLEN kyc:jobs
```

### Issue: WhatsApp Messages Not Sending

**Check:**
1. Twilio account balance
2. WhatsApp sandbox still active
3. Webhook logs for Twilio errors
4. Phone number format (must include +91)

---

## 🔒 Security Guidelines

### Access Control

**Who Has Access:**
- HR personnel: Review and approve submissions
- System Admin: Full system access, API key management
- Auditors: Read-only access to audit logs

**API Key Security:**
- Store API key in secure password manager
- Never commit API key to git
- Rotate key every 90 days
- Use different keys for dev/staging/production

### Data Protection

**Sensitive Data:**
- Aadhaar numbers: Encrypted at rest, only last 4 visible
- PAN numbers: Encrypted at rest
- Bank account numbers: Encrypted at rest

**Decryption:**
Only decrypt when absolutely necessary for verification.

**Document Storage:**
- Original images stored in `uploads/` directory
- Restrict file system access
- Regular backups to secure location

### Compliance

**Data Retention:**
- Keep KYC records for 5 years (as per regulations)
- Delete records after retention period
- Document all deletions in audit log

**Audit Trail:**
- All reviews logged with timestamp
- Reviewer identity recorded
- Changes tracked in audit log
- Logs immutable (append-only)

---

## 📞 Escalation

### When to Escalate

**To Senior HR:**
- Name mismatch >20% but documents appear genuine
- Suspicious documents
- Repeated rejections for same employee

**To System Admin:**
- API errors persisting >1 hour
- System downtime
- Data integrity issues
- Security incidents

**To Legal/Compliance:**
- Suspected fraud
- Document forgery
- Regulatory compliance questions

---

## 🎓 Training Checklist

New HR personnel should:

- [ ] Read this guide completely
- [ ] Understand photo quality requirements
- [ ] Know how to access API
- [ ] Practice reviewing test submissions
- [ ] Understand approval/rejection criteria
- [ ] Know escalation procedures
- [ ] Complete compliance training

---

## 📝 Quick Reference

**Common Commands:**

```bash
# List pending submissions
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     "http://localhost:8000/api/submissions?status=PENDING"

# Get submission details
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     "http://localhost:8000/api/submissions/SUBMISSION_ID"

# Approve submission
curl -X POST -H "X-API-Key: metro-kyc-secure-key-2026" \
     -H "Content-Type: application/json" \
     -d '{"status":"APPROVED","reviewed_by":"hr@company.com"}' \
     "http://localhost:8000/api/submissions/SUBMISSION_ID/review"

# Check system health
curl http://localhost:8000/health
```

---

**Document Version:** 1.0
**Last Updated:** 2026-04-17
**For Support:** Contact System Administrator

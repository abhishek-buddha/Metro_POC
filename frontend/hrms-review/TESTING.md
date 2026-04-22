# HRMS Auto-Population Integration Testing

## Prerequisites

1. Backend server running on port 8000
2. Frontend dev server on port 5173
3. At least one APPROVED submission in database

## Running Tests

### Automated Build Test
```bash
./test-integration.sh
```

### Manual End-to-End Test

1. **Start Backend**
   ```bash
   cd C:\Users\Rakes\Desktop\Metro_POC
   python -m src.webhook.app
   ```

2. **Get Test Submission ID**
   ```bash
   curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/submissions | jq '.[] | select(.status=="APPROVED") | .id' | head -1
   ```

3. **Start Frontend**
   ```bash
   cd frontend/hrms-review
   npm run dev
   ```

4. **Open in Browser**
   Navigate to: `http://localhost:5173?id={submission_id}`

5. **Verify Display**
   - [ ] Organization Elements section loads
   - [ ] Personal Details section shows extracted data
   - [ ] Financial Details shows masked Aadhaar and PAN
   - [ ] Bank Details displays account information
   - [ ] Submit button is enabled

6. **Test Submission**
   - Click "Submit" button
   - Verify button shows "Submitting..." with spinner
   - Verify success message appears with employee ID
   - Verify button changes to "Submitted ✓" and is disabled

7. **Database Verification**
   ```bash
   sqlite3 metro_kyc.db "SELECT id, status, hrms_employee_id, finalized_at FROM kyc_submissions WHERE id='{submission_id}';"
   ```

8. **Error Handling Test**
   - Refresh page
   - Try submitting again
   - Verify error: "Submission already finalized"

## Expected Results

- All form sections display correctly
- Data is properly masked (Aadhaar shows only last 4 digits)
- Submit creates employee ID in format EMP{YEAR}{SEQUENCE}
- Database updates correctly with FINALIZED status
- Error handling works for duplicate submissions

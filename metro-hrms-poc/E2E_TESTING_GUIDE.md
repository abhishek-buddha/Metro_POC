# Metro HRMS POC - End-to-End Testing Guide

## Overview
This guide covers testing the complete flow from WhatsApp document submission to HRMS form completion.

---

## Prerequisites

### Services Running
✅ **Redis** - Port 6379
✅ **Backend API** - Port 8000
✅ **Metro HRMS Frontend** - Port 5174

### Check Services
```bash
# Check Redis
redis-cli ping
# Should return: PONG

# Check Backend
curl http://localhost:8000/health
# Should return: {"status":"healthy","redis":"connected","database":"connected"}

# Check Frontend
# Open browser: http://localhost:5174
```

---

## Complete End-to-End Flow

### Phase 1: WhatsApp Document Submission (Already Done)

**What happened:**
1. ✅ Employee sent documents via WhatsApp:
   - PAN Card PDF
   - Aadhaar PDF
   - Bank Statement PDF

2. ✅ Backend processed documents:
   - Extracted data using OCR
   - Stored in database with status "PENDING"
   - Created employee record with phone number

3. ✅ HR reviewed and approved:
   - Changed status from "PENDING" to "APPROVED"
   - Employee now appears as "In Progress" in HRMS

### Phase 2: HRMS Interface Testing (Current Phase)

#### Step 1: Access Employee List

1. **Open Metro HRMS:**
   ```
   http://localhost:5174
   ```

2. **What you should see:**
   - Metro logo (purple "m" icon) in sidebar
   - Navigation icons on left
   - "Add Employees List" header
   - Tab navigation with "Onboarding" active (purple underline)
   - Filter panel on left side
   - Employee table with columns:
     - EMPLOYEE NAME
     - TEMP ID
     - EMPLOYEE ID
     - ENTITY NAME
     - SUBMISSION STATUS
     - SUBMISSION LEVEL
     - Actions (⋮)

3. **Expected Data:**
   - At least 1 employee row showing
   - Status badge:
     - If "APPROVED" → Orange "In Progress"
     - If "FINALIZED" → Green "Completed"
   - TEMP ID: Generated from employee ID
   - Entity Name: "Metro Brands Limited"

#### Step 2: Filter Employees

1. **Use Filter Panel (left side):**
   - Submission Status dropdown
   - Submission Level dropdown
   - Click "Apply" button

2. **Test Filters:**
   - Select status "In Progress" or "Completed"
   - Select level "Basic Info"
   - Click Apply
   - Table should update with filtered results

3. **Reset Filters:**
   - Click "Reset" link
   - All employees should reappear

#### Step 3: Open Employee Form

1. **Click three-dot menu (⋮)** on any employee row

2. **Menu options appear:**
   - View Details
   - **Proceed** ← Click this
   - Cancel (red text)

3. **Click "Proceed"**
   - Should navigate to form page
   - URL changes to: `/employee/{id}/form`

#### Step 4: Review Auto-Populated Form

**Multi-Step Stepper:**
- ① Personal Details (active - purple)
- ② Company Structure & Policies (inactive - gray)
- ③ Payroll (inactive - gray)

**Section 1: Personal Details**

All fields should be auto-populated from WhatsApp extraction:

| Field | Source | Example Value |
|-------|--------|---------------|
| First Name | Aadhaar Name | MANDADI SAMPATH REDDY |
| Full Name | PAN Name | BOPPISETTI RAKESH |
| Date of Birth | PAN/Aadhaar DOB | 24 Dec, 2001 |
| Gender | Aadhaar Gender | Male |
| Official Contact | Employee Phone | +919063555464 |
| Personal Contact | Employee Phone | +919063555464 |
| Address Line 1 | Aadhaar Address | (if available) |
| Age | Auto-calculated | 24 year(s) 3 month(s) 20 day(s) |

**Section 2: Financial Details**

| Field | Source | Example Value |
|-------|--------|---------------|
| E Aadhar Card Upload | Document link | EMPLOYEE_AADHAAR.pdf |
| Father Name | PAN | RAJESWAR RAO BOPPISETTI |
| Pan Card Upload | Document link | EMPLOYEE_PAN.pdf |
| E Aadhar Password | Password field | (to be entered) |

**Section 3: Bank Details**

| Field | Source | Example Value |
|-------|--------|---------------|
| Account Number | Bank Statement | (if extracted) |
| IFSC Code | Bank Statement | (if extracted) |
| Bank Name | Bank Statement | (if extracted) |
| Bank Branch | Bank Statement | (if extracted) |

**Section 4: Other Details**
- Resume Upload (optional)
- Educational Documents Upload
- Profile Photo Upload (JPG/JPEG only)
- NAPS Authorization Letter
- Signature Attachment

#### Step 5: Test Document Viewer

1. **Click on any uploaded document link** (e.g., "E Aadhar Card Upload")

2. **Modal should open:**
   - Title: "View Document"
   - Filename displayed
   - PDF/Image viewer

3. **If password-protected:**
   - Password prompt appears
   - Enter password
   - Click "OK"
   - Document displays

4. **Close modal:**
   - Click X or outside modal
   - Returns to form

#### Step 6: Complete and Submit Form

1. **Fill any missing fields:**
   - Blood Group (optional)
   - Marital Status (optional)
   - Spouse Name (if married)
   - Education details (optional)

2. **Upload any missing documents:**
   - Click "Upload Attachment" buttons
   - Select files (respect format restrictions)
   - File name appears next to field

3. **Click "Submit" button** (bottom right)

4. **Expected result:**
   - Success message
   - Employee ID generated: EMP2026XXX
   - Status changes: APPROVED → FINALIZED
   - Redirects back to employee list

5. **Verify in database:**
   ```sql
   sqlite3 metro_kyc.db "SELECT id, status, generated_employee_id, finalized_at FROM submissions;"
   ```
   - Status should be "FINALIZED"
   - generated_employee_id should be set
   - finalized_at timestamp should be present

---

## Current Test Data

### Existing Submission
```
ID: aacc95cb-d37a-4d55-89c9-addf5741ddda
Employee ID: 8175e62d-9acf-45da-9843-d128d0c59bb1
Phone: +919063555464
Status: FINALIZED (already submitted in previous test)
PAN Name: BOPPISETTI RAKESH
PAN Number: CRCPB7940R
Aadhaar Name: MANDADI SAMPATH REDDY
Aadhaar Last 4: 8000
```

### To Create New Test Data

**Option 1: Via WhatsApp**
1. Send new documents via WhatsApp
2. Wait for processing
3. Manually approve via database:
   ```sql
   UPDATE kyc_submissions
   SET status = 'APPROVED'
   WHERE id = '<new-submission-id>';
   ```

**Option 2: Via Database Insert**
```sql
-- Create employee
INSERT INTO employees (id, phone_number, created_at)
VALUES ('new-uuid', '+919999999999', datetime('now'));

-- Create submission
INSERT INTO kyc_submissions (
  id, employee_id, status, phone_number,
  pan_name, pan_number, pan_father_name, pan_dob,
  aadhaar_name, aadhaar_dob, aadhaar_gender, aadhaar_last4,
  created_at
) VALUES (
  'new-uuid-2',
  'new-uuid',
  'APPROVED',
  '+919999999999',
  'TEST NAME',
  'ABCDE1234F',
  'FATHER NAME',
  '01/01/1990',
  'TEST AADHAAR NAME',
  '01/01/1990',
  'Male',
  '1234',
  datetime('now')
);
```

---

## Troubleshooting

### Issue 1: "Failed to fetch submissions"

**Cause:** CORS or API not accessible

**Fix:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS allows port 5174 in `src/webhook/app.py`
3. Restart backend if needed
4. Clear browser cache and refresh

### Issue 2: No employees showing

**Cause:** No APPROVED submissions in database

**Fix:**
1. Check database:
   ```sql
   SELECT id, status FROM kyc_submissions;
   ```
2. Change status to APPROVED:
   ```sql
   UPDATE kyc_submissions SET status = 'APPROVED' WHERE id = '<id>';
   ```
3. Refresh page

### Issue 3: Form fields empty

**Cause:** API response missing data

**Fix:**
1. Check API response:
   ```bash
   curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://localhost:8000/api/submissions/<id>
   ```
2. Verify data exists in database
3. Check field mapping in `EmployeeForm.tsx`

### Issue 4: Documents not viewable

**Cause:** Document files not stored

**Fix:**
- Currently, only extracted text is stored
- Actual PDF files need to be saved during WhatsApp processing
- For POC, document viewer shows placeholder

### Issue 5: UI broken or logos missing

**Cause:** Vite build cache or missing assets

**Fix:**
```bash
cd metro-hrms-poc
rm -rf node_modules/.vite
npm run dev
```

---

## API Endpoints Reference

### GET /api/submissions
**Returns:** List of all submissions
```json
{
  "submissions": [
    {
      "id": "uuid",
      "employee_id": "uuid",
      "phone_number": "+91...",
      "status": "APPROVED|FINALIZED",
      "pan_name": "...",
      "pan_number": "...",
      ...
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### GET /api/submissions/{id}
**Returns:** Single submission with all details
```json
{
  "id": "uuid",
  "employee": {
    "id": "uuid",
    "phone_number": "+91..."
  },
  "status": "APPROVED",
  "pan_name": "...",
  "pan_number": "...",
  "aadhaar_name": "...",
  "bank_account": "...",
  ...
}
```

### POST /api/submissions/{id}/finalize
**Body:** Form data (optional, can be empty)
**Returns:**
```json
{
  "message": "Submission finalized successfully",
  "employee_id": "EMP2026001",
  "submission_id": "uuid"
}
```

---

## Success Criteria

✅ **Employee List Screen:**
- Displays all APPROVED/FINALIZED submissions
- Filters work correctly
- Three-dot menu shows options
- Clicking "Proceed" navigates to form

✅ **Employee Form Screen:**
- All fields auto-populated from backend
- Age calculated correctly from DOB
- Document upload fields functional
- Stepper navigation works
- Submit button creates FINALIZED status

✅ **Data Flow:**
- WhatsApp → Backend → Database → HRMS
- All extracted data appears in form
- Submit generates Employee ID
- Status transitions work correctly

---

## Known Limitations (POC Scope)

1. **Document Storage:** Actual PDF files not stored, only extracted text
2. **Password Protection:** PDF passwords not validated
3. **Step 2 & 3:** Only Step 1 (Personal Details) is fully implemented
4. **Validation:** Basic validation only
5. **Edit Mode:** Cannot edit after finalization
6. **Audit Trail:** Limited logging

---

## Next Steps After POC

1. Implement actual PDF file storage
2. Add PDF password validation
3. Complete Step 2 (Company Structure) and Step 3 (Payroll)
4. Add comprehensive validation
5. Implement edit workflow
6. Add email notifications
7. Export to Excel/CSV
8. Add audit trail dashboard
9. Bulk upload functionality
10. Mobile responsive design

---

## Contact

For issues or questions:
- Check backend logs: `tail -f C:\Users\Rakes\AppData\Local\Temp\claude\...\bc6ec24.output`
- Check frontend console: Browser DevTools → Console tab
- Check database: `sqlite3 metro_kyc.db`

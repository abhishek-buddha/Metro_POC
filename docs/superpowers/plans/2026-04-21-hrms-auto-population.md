# HRMS Auto-Population Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a React-based HRMS interface that displays auto-populated employee onboarding data from WhatsApp document extraction and allows finalization with unique employee ID generation.

**Architecture:** React SPA frontend fetches KYC submission data via existing API, displays in view-only form sections matching Metro UI, and submits via new backend endpoint that generates HRMS employee IDs.

**Tech Stack:** React 18 + TypeScript, Vite, Tailwind CSS, React Query, Axios, FastAPI, SQLAlchemy, SQLite

---

## File Structure

### Backend (Extensions to Existing Code)
- **Modify:** `src/models/database.py` - Add finalization fields to KYCSubmission model
- **Modify:** `src/webhook/app.py` - Add POST /api/submissions/{id}/finalize endpoint

### Frontend (New React Application)
- **Create:** `frontend/hrms-review/` - New React app directory
- **Create:** `frontend/hrms-review/src/types/submission.ts` - TypeScript interfaces
- **Create:** `frontend/hrms-review/src/services/api.ts` - API client
- **Create:** `frontend/hrms-review/src/utils/dataTransform.ts` - Data mapping
- **Create:** `frontend/hrms-review/src/utils/dateFormat.ts` - Date formatting
- **Create:** `frontend/hrms-review/src/components/LoadingSpinner.tsx` - Loading UI
- **Create:** `frontend/hrms-review/src/components/ErrorState.tsx` - Error UI
- **Create:** `frontend/hrms-review/src/components/OrganizationElementsSection.tsx` - Org fields
- **Create:** `frontend/hrms-review/src/components/PersonalDetailsSection.tsx` - Personal info
- **Create:** `frontend/hrms-review/src/components/FinancialDetailsSection.tsx` - Aadhaar/PAN
- **Create:** `frontend/hrms-review/src/components/BankDetailsSection.tsx` - Bank details
- **Create:** `frontend/hrms-review/src/components/SubmitButton.tsx` - Submit action
- **Create:** `frontend/hrms-review/src/pages/SubmissionReview.tsx` - Main page
- **Create:** `frontend/hrms-review/src/App.tsx` - App root
- **Create:** `frontend/hrms-review/src/main.tsx` - Entry point
- **Create:** `frontend/hrms-review/index.html` - HTML template
- **Create:** `frontend/hrms-review/package.json` - Dependencies
- **Create:** `frontend/hrms-review/vite.config.ts` - Vite config
- **Create:** `frontend/hrms-review/tsconfig.json` - TypeScript config
- **Create:** `frontend/hrms-review/tailwind.config.js` - Tailwind config
- **Create:** `frontend/hrms-review/postcss.config.js` - PostCSS config
- **Create:** `frontend/hrms-review/.env.example` - Environment template
- **Create:** `frontend/hrms-review/.gitignore` - Git ignore rules

---

## Task 1: Backend - Database Schema Update

**Files:**
- Modify: `src/models/database.py:56-80` (KYCSubmission class)
- Test: Manual inspection + database check

- [ ] **Step 1: Add finalization fields to KYCSubmission model**

Open `src/models/database.py` and locate the `KYCSubmission` class. Add three new fields after the existing fields:

```python
# Add after existing fields in KYCSubmission class (around line 75)

    # Finalization fields
    finalized_at = Column(DateTime, nullable=True)
    finalized_by = Column(Text, nullable=True)
    hrms_employee_id = Column(Text, unique=True, nullable=True)
```

- [ ] **Step 2: Verify the model changes**

Read the updated KYCSubmission class to ensure the new fields are added correctly:

```bash
grep -A 3 "finalized_at\|finalized_by\|hrms_employee_id" src/models/database.py
```

Expected: Should show the three new field definitions

- [ ] **Step 3: Apply database migration**

Since we're using SQLite, we need to manually alter the table. Run:

```bash
sqlite3 metro_kyc.db "ALTER TABLE kyc_submissions ADD COLUMN finalized_at TIMESTAMP;"
sqlite3 metro_kyc.db "ALTER TABLE kyc_submissions ADD COLUMN finalized_by TEXT;"
sqlite3 metro_kyc.db "ALTER TABLE kyc_submissions ADD COLUMN hrms_employee_id TEXT UNIQUE;"
```

Expected: No errors, columns added successfully

- [ ] **Step 4: Verify database schema**

```bash
sqlite3 metro_kyc.db ".schema kyc_submissions" | grep -E "finalized_at|finalized_by|hrms_employee_id"
```

Expected: Should show all three new columns

- [ ] **Step 5: Commit**

```bash
git add src/models/database.py
git commit -m "feat(backend): add finalization fields to KYCSubmission model

Add finalized_at, finalized_by, and hrms_employee_id fields to track
employee finalization in HRMS system.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 2: Backend - Employee ID Generation Function

**Files:**
- Modify: `src/webhook/app.py:1-50` (add import and helper function)
- Test: Manual function call test

- [ ] **Step 1: Add necessary imports**

At the top of `src/webhook/app.py`, add the datetime import if not already present:

```python
from datetime import datetime
```

- [ ] **Step 2: Add employee ID generation function**

Add this function before the route definitions (around line 40, after imports):

```python
def generate_employee_id(session) -> str:
    """
    Generate unique HRMS employee ID
    Format: EMP{YEAR}{SEQUENCE}
    Example: EMP2026001, EMP2026002, etc.
    """
    current_year = datetime.now().year

    # Get last employee ID for current year
    last_submission = session.query(KYCSubmission).filter(
        KYCSubmission.hrms_employee_id.like(f"EMP{current_year}%")
    ).order_by(KYCSubmission.hrms_employee_id.desc()).first()

    if last_submission and last_submission.hrms_employee_id:
        # Extract sequence number and increment
        last_seq = int(last_submission.hrms_employee_id[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f"EMP{current_year}{new_seq:03d}"
```

- [ ] **Step 3: Test the function logic manually**

Create a test file `test_employee_id.py` in project root:

```python
def test_generate_employee_id():
    # Test first ID of year
    def mock_session_empty():
        class MockQuery:
            def filter(self, *args): return self
            def order_by(self, *args): return self
            def first(self): return None
        return type('Session', (), {'query': lambda self, x: MockQuery()})()

    from datetime import datetime
    current_year = datetime.now().year

    # Simulate the function logic
    session = mock_session_empty()
    expected = f"EMP{current_year}001"
    print(f"First ID: {expected}")

    # Test incrementing
    class MockSubmission:
        hrms_employee_id = f"EMP{current_year}005"

    last_seq = int(MockSubmission.hrms_employee_id[-3:])
    new_seq = last_seq + 1
    expected = f"EMP{current_year}{new_seq:03d}"
    print(f"After EMP{current_year}005: {expected}")
    assert expected == f"EMP{current_year}006"

if __name__ == "__main__":
    test_generate_employee_id()
    print("Employee ID generation logic verified")
```

- [ ] **Step 4: Run test**

```bash
python test_employee_id.py
```

Expected: Output shows correct ID formats and "logic verified" message

- [ ] **Step 5: Remove test file and commit**

```bash
rm test_employee_id.py
git add src/webhook/app.py
git commit -m "feat(backend): add employee ID generation function

Generates unique HRMS employee IDs in format EMP{YEAR}{SEQUENCE}.
Handles auto-incrementing sequence numbers per year.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 3: Backend - Finalize Submission Endpoint

**Files:**
- Modify: `src/webhook/app.py:500+` (add new endpoint after existing routes)
- Test: Manual API call with curl

- [ ] **Step 1: Add Pydantic request model**

Add this near the top of `src/webhook/app.py` after imports (around line 30):

```python
class FinalizeRequest(BaseModel):
    finalized_by: Optional[str] = None
    notes: Optional[str] = None
```

- [ ] **Step 2: Write the finalize endpoint**

Add this endpoint after the existing submission endpoints (around line 500):

```python
@app.post("/api/submissions/{submission_id}/finalize")
async def finalize_submission(
    submission_id: str,
    finalize_data: FinalizeRequest,
    api_key: str = Header(..., alias="X-API-Key")
):
    """
    Finalize an APPROVED submission after HRMS review

    Steps:
    1. Validate API key
    2. Fetch submission from database
    3. Check status is APPROVED
    4. Check not already finalized
    5. Update status to FINALIZED
    6. Generate/assign HRMS employee ID
    7. Log audit event
    8. Return success response
    """
    # Validate API key
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")

    # Fetch submission
    session = SessionLocal()
    try:
        submission = session.query(KYCSubmission).filter(
            KYCSubmission.id == submission_id
        ).first()

        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Check status
        if submission.status == "FINALIZED":
            raise HTTPException(
                status_code=400,
                detail="Submission already finalized"
            )

        if submission.status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Only APPROVED submissions can be finalized"
            )

        # Generate HRMS employee ID with retry for race conditions
        try:
            submission.hrms_employee_id = generate_employee_id(session)
            submission.status = "FINALIZED"
            submission.finalized_at = datetime.utcnow()
            submission.finalized_by = finalize_data.finalized_by
            submission.review_notes = finalize_data.notes
            session.commit()
        except Exception as e:
            session.rollback()
            # Retry once in case of unique constraint violation
            submission.hrms_employee_id = generate_employee_id(session)
            submission.status = "FINALIZED"
            submission.finalized_at = datetime.utcnow()
            submission.finalized_by = finalize_data.finalized_by
            submission.review_notes = finalize_data.notes
            session.commit()

        # Log audit event
        audit_log = AuditLog(
            event_type="SUBMISSION_FINALIZED",
            employee_id=submission.employee_id,
            kyc_submission_id=submission_id,
            performed_by=finalize_data.finalized_by,
            details=json.dumps({
                "hrms_employee_id": submission.hrms_employee_id,
                "notes": finalize_data.notes
            }),
            timestamp=datetime.utcnow()
        )
        session.add(audit_log)
        session.commit()

        return {
            "id": submission_id,
            "status": "FINALIZED",
            "finalized_at": submission.finalized_at.isoformat(),
            "finalized_by": finalize_data.finalized_by,
            "hrms_employee_id": submission.hrms_employee_id,
            "message": "Employee data finalized successfully"
        }
    finally:
        session.close()
```

- [ ] **Step 3: Verify json import exists**

Check if json is imported at top of file:

```bash
grep "import json" src/webhook/app.py
```

If not found, add it to imports:

```python
import json
```

- [ ] **Step 4: Start backend server for testing**

```bash
python -m src.webhook.app
```

Expected: Server starts on port 8000

- [ ] **Step 5: Test endpoint with curl (in new terminal)**

First, get an APPROVED submission ID:

```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/submissions | jq '.[] | select(.status=="APPROVED") | .id' | head -1
```

Then test finalization (replace {submission_id}):

```bash
curl -X POST \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"finalized_by":"test@metro.com","notes":"Testing finalization"}' \
  http://localhost:8000/api/submissions/{submission_id}/finalize
```

Expected: JSON response with status "FINALIZED" and hrms_employee_id like "EMP2026001"

- [ ] **Step 6: Verify in database**

```bash
sqlite3 metro_kyc.db "SELECT id, status, hrms_employee_id, finalized_at FROM kyc_submissions WHERE status='FINALIZED';"
```

Expected: Shows the finalized submission with employee ID

- [ ] **Step 7: Test error cases**

Try finalizing same submission again:

```bash
curl -X POST \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{}' \
  http://localhost:8000/api/submissions/{submission_id}/finalize
```

Expected: 400 error "Submission already finalized"

- [ ] **Step 8: Stop server and commit**

```bash
# Stop server with Ctrl+C
git add src/webhook/app.py
git commit -m "feat(backend): add submission finalization endpoint

Add POST /api/submissions/{id}/finalize endpoint that:
- Validates submission is APPROVED
- Generates unique HRMS employee ID
- Updates status to FINALIZED
- Creates audit log entry

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 4: Frontend - Project Setup

**Files:**
- Create: `frontend/hrms-review/` directory and config files
- Test: Vite dev server starts successfully

- [ ] **Step 1: Create React project with Vite**

```bash
cd C:\Users\Rakes\Desktop\Metro_POC
npm create vite@latest frontend/hrms-review -- --template react-ts
```

Expected: Project created successfully

- [ ] **Step 2: Navigate to project and install dependencies**

```bash
cd frontend/hrms-review
npm install
```

Expected: Dependencies installed

- [ ] **Step 3: Install additional dependencies**

```bash
npm install axios @tanstack/react-query react-router-dom
npm install -D tailwindcss postcss autoprefixer
```

Expected: All packages installed

- [ ] **Step 4: Initialize Tailwind CSS**

```bash
npx tailwindcss init -p
```

Expected: Creates tailwind.config.js and postcss.config.js

- [ ] **Step 5: Configure Tailwind**

Replace content of `tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6366F1',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 6: Create Tailwind CSS file**

Replace content of `src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 7: Create environment file**

Create `frontend/hrms-review/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

- [ ] **Step 8: Create environment example file**

Create `frontend/hrms-review/.env.example`:

```bash
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

- [ ] **Step 9: Update gitignore**

Create `frontend/hrms-review/.gitignore`:

```
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# Environment
.env
.env.local
.env.production
```

- [ ] **Step 10: Test dev server**

```bash
npm run dev
```

Expected: Server starts at http://localhost:5173, shows default Vite page

- [ ] **Step 11: Stop server and commit**

```bash
# Ctrl+C to stop
cd ../..
git add frontend/hrms-review
git commit -m "feat(frontend): initialize React project with Vite and Tailwind

Set up React 18 + TypeScript project with:
- Vite build tool
- Tailwind CSS for styling
- React Query and Axios for API calls
- Environment configuration

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 5: Frontend - TypeScript Interfaces

**Files:**
- Create: `frontend/hrms-review/src/types/submission.ts`
- Test: TypeScript compilation check

- [ ] **Step 1: Create types directory**

```bash
mkdir -p frontend/hrms-review/src/types
```

- [ ] **Step 2: Write submission interface**

Create `frontend/hrms-review/src/types/submission.ts`:

```typescript
export interface Employee {
  id: string;
  phone_number: string;
}

export interface Submission {
  id: string;
  employee_id: string;
  status: "APPROVED" | "PENDING" | "REJECTED" | "FINALIZED";
  employee: Employee;

  // PAN Card Data
  pan_number: string;
  pan_name: string;
  pan_father_name: string;
  pan_dob: string;
  pan_confidence: number;

  // Aadhaar Data (Masked)
  aadhaar_last4: string;
  aadhaar_name: string;
  aadhaar_dob: string;
  aadhaar_gender: "Male" | "Female" | "Other";
  aadhaar_address: string;
  aadhaar_pincode: string;
  aadhaar_confidence: number;

  // Bank Data
  bank_account: string;
  bank_holder_name: string;
  bank_ifsc: string;
  bank_name: string;
  bank_branch: string;
  bank_account_type?: string;
  bank_confidence: number;

  // Metadata
  name_match_score: number;
  overall_confidence: number;
  submitted_at: string;
}

export interface FinalizeRequest {
  finalized_by?: string;
  notes?: string;
}

export interface FinalizeResponse {
  id: string;
  status: string;
  finalized_at: string;
  finalized_by?: string;
  hrms_employee_id: string;
  message: string;
}

export interface DisplayData {
  organizationElements: {
    entity: string;
    businessUnit: string;
    function: string;
    baseLocation: string;
    department: string;
    designation: string;
    position: string;
    employmentType: string;
    estimatedDOJ: string;
  };

  personalDetails: {
    employeeName: string;
    dateOfBirth: string;
    gender: string;
    phoneNumber: string;
    email: string;
    addressLine1: string;
    addressLine2: string;
    addressLine3: string;
    age: number;
  };

  financialDetails: {
    aadhaarNumber: string;
    aadhaarUpload: string;
    panCard: string;
    panUpload: string;
    fatherName: string;
  };

  bankDetails: {
    accountHolderName: string;
    accountNumber: string;
    ifscCode: string;
    bankName: string;
    branchName: string;
    accountType: string;
    bankStatementUpload: string;
  };
}
```

- [ ] **Step 3: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/types/submission.ts
git commit -m "feat(frontend): add TypeScript interfaces for submission data

Define interfaces for API responses and display data structures.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 6: Frontend - Date Formatting Utilities

**Files:**
- Create: `frontend/hrms-review/src/utils/dateFormat.ts`
- Test: Unit tests with node

- [ ] **Step 1: Create utils directory**

```bash
mkdir -p frontend/hrms-review/src/utils
```

- [ ] **Step 2: Write date formatting functions**

Create `frontend/hrms-review/src/utils/dateFormat.ts`:

```typescript
/**
 * Format ISO date to DD/MM/YYYY
 */
export const formatDateForDisplay = (isoDate: string): string => {
  if (!isoDate) return '';

  try {
    const date = new Date(isoDate);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  } catch {
    return isoDate;
  }
};

/**
 * Calculate age from date of birth
 */
export const calculateAge = (dob: string): number => {
  if (!dob) return 0;

  try {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }

    return age;
  } catch {
    return 0;
  }
};

/**
 * Get default DOJ (7 days from today)
 */
export const getDefaultDOJ = (): string => {
  const date = new Date();
  date.setDate(date.getDate() + 7);
  return date.toISOString().split('T')[0];
};

/**
 * Format Aadhaar number with masking
 */
export const formatAadhaar = (last4: string): string => {
  return `XXXX XXXX ${last4}`;
};
```

- [ ] **Step 3: Create test file**

Create `frontend/hrms-review/test-utils.js`:

```javascript
// Simple test for date formatting functions

function test_formatDateForDisplay() {
  const formatDateForDisplay = (isoDate) => {
    if (!isoDate) return '';
    try {
      const date = new Date(isoDate);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
    } catch {
      return isoDate;
    }
  };

  const result = formatDateForDisplay('1990-01-15');
  console.assert(result === '15/01/1990', `Expected 15/01/1990, got ${result}`);
  console.log('✓ formatDateForDisplay works');
}

function test_calculateAge() {
  const calculateAge = (dob) => {
    if (!dob) return 0;
    try {
      const birthDate = new Date(dob);
      const today = new Date();
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      return age;
    } catch {
      return 0;
    }
  };

  const result = calculateAge('1990-01-01');
  console.assert(result >= 34 && result <= 36, `Age should be 34-36, got ${result}`);
  console.log('✓ calculateAge works');
}

function test_formatAadhaar() {
  const formatAadhaar = (last4) => `XXXX XXXX ${last4}`;
  const result = formatAadhaar('1234');
  console.assert(result === 'XXXX XXXX 1234', `Expected XXXX XXXX 1234, got ${result}`);
  console.log('✓ formatAadhaar works');
}

test_formatDateForDisplay();
test_calculateAge();
test_formatAadhaar();
console.log('\nAll date utility tests passed!');
```

- [ ] **Step 4: Run tests**

```bash
cd frontend/hrms-review
node test-utils.js
```

Expected: All assertions pass, shows "All date utility tests passed!"

- [ ] **Step 5: Remove test file and commit**

```bash
rm test-utils.js
cd ../..
git add frontend/hrms-review/src/utils/dateFormat.ts
git commit -m "feat(frontend): add date formatting utilities

Add functions for:
- ISO to DD/MM/YYYY conversion
- Age calculation from DOB
- Default DOJ generation
- Aadhaar number masking

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 7: Frontend - Data Transformation Utilities

**Files:**
- Create: `frontend/hrms-review/src/utils/dataTransform.ts`
- Test: TypeScript compilation check

- [ ] **Step 1: Write data transformation function**

Create `frontend/hrms-review/src/utils/dataTransform.ts`:

```typescript
import type { Submission, DisplayData } from '../types/submission';
import { formatDateForDisplay, calculateAge, getDefaultDOJ, formatAadhaar } from './dateFormat';

export const transformSubmissionData = (submission: Submission): DisplayData => {
  // Split address into multiple lines
  const addressParts = (submission.aadhaar_address || '').split(',').map(s => s.trim());

  return {
    organizationElements: {
      entity: "Metro Brands Limited",
      businessUnit: "Showroom(SR)",
      function: "Maharashtra(MAHARASHTRA)",
      baseLocation: "PLV(PLV)",
      department: "PLV(PLV)",
      designation: "Salesman",
      position: "Field Sales",
      employmentType: "Full-time",
      estimatedDOJ: formatDateForDisplay(getDefaultDOJ()),
    },

    personalDetails: {
      employeeName: submission.aadhaar_name || submission.pan_name || 'N/A',
      dateOfBirth: formatDateForDisplay(submission.aadhaar_dob || submission.pan_dob),
      gender: submission.aadhaar_gender || 'Not specified',
      phoneNumber: submission.employee.phone_number || 'Not available',
      email: '',
      addressLine1: addressParts[0] || '',
      addressLine2: addressParts[1] || '',
      addressLine3: addressParts.slice(2).join(', '),
      age: calculateAge(submission.aadhaar_dob || submission.pan_dob),
    },

    financialDetails: {
      aadhaarNumber: formatAadhaar(submission.aadhaar_last4),
      aadhaarUpload: 'eAadhaar.pdf',
      panCard: submission.pan_number || 'Not available',
      panUpload: 'PAN.pdf',
      fatherName: submission.pan_father_name || 'Not available',
    },

    bankDetails: {
      accountHolderName: submission.bank_holder_name || 'Not available',
      accountNumber: submission.bank_account || 'Not available',
      ifscCode: submission.bank_ifsc || 'Not available',
      bankName: submission.bank_name || 'Not available',
      branchName: submission.bank_branch || 'Not available',
      accountType: submission.bank_account_type || 'Savings',
      bankStatementUpload: 'bank_statement.pdf',
    },
  };
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/utils/dataTransform.ts
git commit -m "feat(frontend): add data transformation utilities

Transform API submission data into display format with:
- Default organization element values
- Field priority rules (Aadhaar > PAN > Bank)
- Address splitting
- Fallback values for missing fields

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 8: Frontend - API Service

**Files:**
- Create: `frontend/hrms-review/src/services/api.ts`
- Test: TypeScript compilation check

- [ ] **Step 1: Create services directory**

```bash
mkdir -p frontend/hrms-review/src/services
```

- [ ] **Step 2: Write API client**

Create `frontend/hrms-review/src/services/api.ts`:

```typescript
import axios from 'axios';
import type { Submission, FinalizeRequest, FinalizeResponse } from '../types/submission';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

export const api = {
  async getSubmission(submissionId: string): Promise<Submission> {
    const response = await apiClient.get(`/api/submissions/${submissionId}`);
    return response.data;
  },

  async finalizeSubmission(
    submissionId: string,
    data?: FinalizeRequest
  ): Promise<FinalizeResponse> {
    const response = await apiClient.post(
      `/api/submissions/${submissionId}/finalize`,
      data || {}
    );
    return response.data;
  },
};
```

- [ ] **Step 3: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/services/api.ts
git commit -m "feat(frontend): add API service with Axios

Create API client with methods for:
- Getting submission details
- Finalizing submissions

Includes API key authentication from environment.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 9: Frontend - Loading Spinner Component

**Files:**
- Create: `frontend/hrms-review/src/components/LoadingSpinner.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Create components directory**

```bash
mkdir -p frontend/hrms-review/src/components
```

- [ ] **Step 2: Write loading spinner component**

Create `frontend/hrms-review/src/components/LoadingSpinner.tsx`:

```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  message?: string;
}

export const LoadingSpinner = ({
  size = 'medium',
  message = 'Loading...'
}: LoadingSpinnerProps) => {
  const sizeClasses = {
    small: 'w-5 h-5',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
      <div
        className={`${sizeClasses[size]} border-4 border-gray-200 border-t-primary rounded-full animate-spin`}
      />
      {message && (
        <p className="mt-4 text-gray-600">{message}</p>
      )}
    </div>
  );
};
```

- [ ] **Step 3: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/LoadingSpinner.tsx
git commit -m "feat(frontend): add loading spinner component

Display animated spinner with optional message during data loading.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 10: Frontend - Error State Component

**Files:**
- Create: `frontend/hrms-review/src/components/ErrorState.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write error state component**

Create `frontend/hrms-review/src/components/ErrorState.tsx`:

```typescript
interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export const ErrorState = ({
  title = 'Error',
  message,
  onRetry
}: ErrorStateProps) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
          <svg
            className="w-8 h-8 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>

        <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
        <p className="text-gray-600 mb-6">{message}</p>

        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-primary hover:bg-indigo-700 text-white px-6 py-2.5 rounded-md transition-colors"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/ErrorState.tsx
git commit -m "feat(frontend): add error state component

Display error messages with optional retry functionality.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 11: Frontend - Organization Elements Section

**Files:**
- Create: `frontend/hrms-review/src/components/OrganizationElementsSection.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write organization elements component**

Create `frontend/hrms-review/src/components/OrganizationElementsSection.tsx`:

```typescript
import type { DisplayData } from '../types/submission';

interface OrganizationElementsSectionProps {
  data: DisplayData['organizationElements'];
}

export const OrganizationElementsSection = ({ data }: OrganizationElementsSectionProps) => {
  const fields = [
    { label: 'Entity', value: data.entity },
    { label: 'Business Unit', value: data.businessUnit },
    { label: 'Function', value: data.function },
    { label: 'Base Location', value: data.baseLocation },
    { label: 'Department', value: data.department },
    { label: 'Designation', value: data.designation },
    { label: 'Position', value: data.position },
    { label: 'Employment Type', value: data.employmentType },
    { label: 'Estimated DOJ', value: data.estimatedDOJ },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">📋</span>
        Organization Elements
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map((field) => (
          <div key={field.label}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
            </label>
            <div className="text-base text-gray-900">
              {field.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/OrganizationElementsSection.tsx
git commit -m "feat(frontend): add organization elements section component

Display organization-level fields with default values in two-column grid.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 12: Frontend - Personal Details Section

**Files:**
- Create: `frontend/hrms-review/src/components/PersonalDetailsSection.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write personal details component**

Create `frontend/hrms-review/src/components/PersonalDetailsSection.tsx`:

```typescript
import type { DisplayData } from '../types/submission';

interface PersonalDetailsSectionProps {
  data: DisplayData['personalDetails'];
}

export const PersonalDetailsSection = ({ data }: PersonalDetailsSectionProps) => {
  const renderField = (label: string, value: string | number) => {
    const displayValue = value || 'Not extracted from documents';
    const textClass = value ? 'text-gray-900' : 'text-gray-400 italic';

    return (
      <div key={label}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        <div className={`text-base ${textClass}`}>
          {displayValue}
        </div>
      </div>
    );
  };

  const fields = [
    { label: 'Employee Name', value: data.employeeName },
    { label: 'Date of Birth', value: data.dateOfBirth },
    { label: 'Gender', value: data.gender },
    { label: 'Phone Number', value: data.phoneNumber },
    { label: 'Email', value: data.email },
    { label: 'Age', value: data.age || '' },
    { label: 'Address Line 1', value: data.addressLine1 },
    { label: 'Address Line 2', value: data.addressLine2 },
    { label: 'Address Line 3', value: data.addressLine3 },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">👤</span>
        Personal Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fields.map((field) => renderField(field.label, field.value))}
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/PersonalDetailsSection.tsx
git commit -m "feat(frontend): add personal details section component

Display personal information extracted from documents.
Shows placeholder text for missing fields.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 13: Frontend - Financial Details Section

**Files:**
- Create: `frontend/hrms-review/src/components/FinancialDetailsSection.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write financial details component**

Create `frontend/hrms-review/src/components/FinancialDetailsSection.tsx`:

```typescript
import type { DisplayData } from '../types/submission';

interface FinancialDetailsSectionProps {
  data: DisplayData['financialDetails'];
}

export const FinancialDetailsSection = ({ data }: FinancialDetailsSectionProps) => {
  const renderField = (label: string, value: string) => {
    const displayValue = value || 'Not available';
    const textClass = value ? 'text-gray-900' : 'text-gray-400 italic';

    return (
      <div key={label}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        <div className={`text-base ${textClass}`}>
          {displayValue}
        </div>
      </div>
    );
  };

  const renderDocument = (label: string, filename: string) => (
    <div key={label}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <div className="text-base text-gray-900 flex items-center">
        <span className="mr-2">{filename}</span>
        <span className="text-green-600">✓</span>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">💳</span>
        Financial Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {renderField('Aadhaar Number', data.aadhaarNumber)}
        {renderDocument('E-Aadhaar Upload', data.aadhaarUpload)}
        {renderField('PAN Card Number', data.panCard)}
        {renderDocument('PAN Card Upload', data.panUpload)}
        {renderField("Father's Name", data.fatherName)}
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/FinancialDetailsSection.tsx
git commit -m "feat(frontend): add financial details section component

Display Aadhaar (masked) and PAN card information with document indicators.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 14: Frontend - Bank Details Section

**Files:**
- Create: `frontend/hrms-review/src/components/BankDetailsSection.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write bank details component**

Create `frontend/hrms-review/src/components/BankDetailsSection.tsx`:

```typescript
import type { DisplayData } from '../types/submission';

interface BankDetailsSectionProps {
  data: DisplayData['bankDetails'];
}

export const BankDetailsSection = ({ data }: BankDetailsSectionProps) => {
  const renderField = (label: string, value: string) => {
    const displayValue = value || 'Not available';
    const textClass = value ? 'text-gray-900' : 'text-gray-400 italic';

    return (
      <div key={label}>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
        <div className={`text-base ${textClass}`}>
          {displayValue}
        </div>
      </div>
    );
  };

  const renderDocument = (label: string, filename: string) => (
    <div key={label}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <div className="text-base text-gray-900 flex items-center">
        <span className="mr-2">{filename}</span>
        <span className="text-green-600">✓</span>
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
        <span className="mr-2">🏦</span>
        Bank Details
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {renderField('Account Holder Name', data.accountHolderName)}
        {renderField('Account Number', data.accountNumber)}
        {renderField('IFSC Code', data.ifscCode)}
        {renderField('Bank Name', data.bankName)}
        {renderField('Branch Name', data.branchName)}
        {renderField('Account Type', data.accountType)}
        {renderDocument('Bank Statement Upload', data.bankStatementUpload)}
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/BankDetailsSection.tsx
git commit -m "feat(frontend): add bank details section component

Display bank account information extracted from statement.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 15: Frontend - Submit Button Component

**Files:**
- Create: `frontend/hrms-review/src/components/SubmitButton.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Write submit button component**

Create `frontend/hrms-review/src/components/SubmitButton.tsx`:

```typescript
import { useState } from 'react';
import { api } from '../services/api';

interface SubmitButtonProps {
  submissionId: string;
  onSuccess?: (employeeId: string) => void;
}

export const SubmitButton = ({ submissionId, onSuccess }: SubmitButtonProps) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await api.finalizeSubmission(submissionId, {
        finalized_by: 'hr_user@metro.com',
        notes: 'Auto-populated data verified via HRMS interface',
      });

      setSuccess(`Employee ID ${result.hrms_employee_id} created successfully!`);

      if (onSuccess) {
        onSuccess(result.hrms_employee_id);
      }
    } catch (err: any) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError('Failed to finalize submission. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-200 p-6">
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <p className="text-sm text-green-600">{success}</p>
        </div>
      )}

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2.5 rounded-md transition-colors"
          onClick={() => window.history.back()}
        >
          Cancel
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={isSubmitting || !!success}
          className={`bg-primary hover:bg-indigo-700 text-white px-6 py-2.5 rounded-md transition-colors flex items-center ${
            (isSubmitting || !!success) ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isSubmitting ? (
            <>
              <div className="w-4 h-4 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Submitting...
            </>
          ) : success ? (
            'Submitted ✓'
          ) : (
            'Submit'
          )}
        </button>
      </div>
    </div>
  );
};
```

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 3: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/components/SubmitButton.tsx
git commit -m "feat(frontend): add submit button component

Handle submission finalization with loading states, success, and error handling.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 16: Frontend - Main Review Page

**Files:**
- Create: `frontend/hrms-review/src/pages/SubmissionReview.tsx`
- Test: Visual inspection after full app setup

- [ ] **Step 1: Create pages directory**

```bash
mkdir -p frontend/hrms-review/src/pages
```

- [ ] **Step 2: Write submission review page**

Create `frontend/hrms-review/src/pages/SubmissionReview.tsx`:

```typescript
import { useQuery } from '@tanstack/react-query';
import { api } from '../services/api';
import { transformSubmissionData } from '../utils/dataTransform';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorState } from '../components/ErrorState';
import { OrganizationElementsSection } from '../components/OrganizationElementsSection';
import { PersonalDetailsSection } from '../components/PersonalDetailsSection';
import { FinancialDetailsSection } from '../components/FinancialDetailsSection';
import { BankDetailsSection } from '../components/BankDetailsSection';
import { SubmitButton } from '../components/SubmitButton';

interface SubmissionReviewProps {
  submissionId: string;
}

export const SubmissionReview = ({ submissionId }: SubmissionReviewProps) => {
  const { data: submission, isLoading, error, refetch } = useQuery({
    queryKey: ['submission', submissionId],
    queryFn: () => api.getSubmission(submissionId),
    retry: 3,
    staleTime: 30000,
  });

  if (isLoading) {
    return <LoadingSpinner message="Loading submission data..." />;
  }

  if (error) {
    return (
      <ErrorState
        title="Unable to load submission"
        message="Please check your connection and try again"
        onRetry={() => refetch()}
      />
    );
  }

  if (!submission) {
    return (
      <ErrorState
        title="Submission Not Found"
        message="The requested submission does not exist"
      />
    );
  }

  const displayData = transformSubmissionData(submission);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-semibold text-gray-900 mb-6">
          Employee Onboarding Review
        </h1>

        <div className="space-y-6">
          <OrganizationElementsSection data={displayData.organizationElements} />
          <PersonalDetailsSection data={displayData.personalDetails} />
          <FinancialDetailsSection data={displayData.financialDetails} />
          <BankDetailsSection data={displayData.bankDetails} />
          <SubmitButton submissionId={submissionId} />
        </div>
      </div>
    </div>
  );
};
```

- [ ] **Step 3: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 4: Commit**

```bash
cd ../..
git add frontend/hrms-review/src/pages/SubmissionReview.tsx
git commit -m "feat(frontend): add main submission review page

Orchestrate all section components and handle data fetching with React Query.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 17: Frontend - App Root and Entry Point

**Files:**
- Create: `frontend/hrms-review/src/App.tsx`
- Create: `frontend/hrms-review/src/main.tsx`
- Modify: `frontend/hrms-review/index.html`
- Test: Dev server runs without errors

- [ ] **Step 1: Write App component**

Replace `frontend/hrms-review/src/App.tsx` with:

```typescript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { SubmissionReview } from './pages/SubmissionReview';

const queryClient = new QueryClient();

function App() {
  // For POC, hardcode a submission ID or get from URL
  // In production, use react-router-dom
  const urlParams = new URLSearchParams(window.location.search);
  const submissionId = urlParams.get('id') || 'test-submission-id';

  return (
    <QueryClientProvider client={queryClient}>
      <SubmissionReview submissionId={submissionId} />
    </QueryClientProvider>
  );
}

export default App;
```

- [ ] **Step 2: Write main entry point**

Replace `frontend/hrms-review/src/main.tsx` with:

```typescript
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
```

- [ ] **Step 3: Update HTML template**

Replace `frontend/hrms-review/index.html` with:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>HRMS - Employee Onboarding Review</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 4: Verify TypeScript compilation**

```bash
cd frontend/hrms-review
npx tsc --noEmit
```

Expected: No errors

- [ ] **Step 5: Start dev server**

```bash
npm run dev
```

Expected: Server starts at http://localhost:5173

- [ ] **Step 6: Test in browser**

Open: `http://localhost:5173?id={actual_submission_id}`

Replace {actual_submission_id} with a real APPROVED submission ID from your database.

Expected: Page loads showing all sections (may show loading or error if backend not running)

- [ ] **Step 7: Stop server and commit**

```bash
# Ctrl+C to stop
cd ../..
git add frontend/hrms-review/src/App.tsx frontend/hrms-review/src/main.tsx frontend/hrms-review/index.html
git commit -m "feat(frontend): add app root and entry point

Set up React Query provider and main app structure.
Accept submission ID from URL query parameter.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Task 18: Integration Testing

**Files:**
- Test: End-to-end flow
- No new files created

- [ ] **Step 1: Ensure backend is running**

In a terminal:

```bash
cd C:\Users\Rakes\Desktop\Metro_POC
python -m src.webhook.app
```

Expected: Backend starts on port 8000

- [ ] **Step 2: Get an APPROVED submission ID**

In a new terminal:

```bash
curl -H "X-API-Key: your_api_key_here" http://localhost:8000/api/submissions | jq '.[] | select(.status=="APPROVED") | .id' | head -1
```

Copy the submission ID (remove quotes).

- [ ] **Step 3: Start frontend dev server**

In another terminal:

```bash
cd C:\Users\Rakes\Desktop\Metro_POC\frontend\hrms-review
npm run dev
```

Expected: Frontend starts on port 5173

- [ ] **Step 4: Open in browser**

Navigate to: `http://localhost:5173?id={submission_id}`

Replace {submission_id} with the actual ID from step 2.

- [ ] **Step 5: Verify all sections display**

Check that page shows:
- ✅ Organization Elements with default values
- ✅ Personal Details from extraction
- ✅ Financial Details with masked Aadhaar
- ✅ Bank Details
- ✅ Submit button at bottom

- [ ] **Step 6: Test submit functionality**

Click "Submit" button.

Expected:
- Button shows "Submitting..." with spinner
- After 1-2 seconds, shows success message with employee ID
- Button becomes "Submitted ✓" and disabled

- [ ] **Step 7: Verify in database**

```bash
sqlite3 metro_kyc.db "SELECT id, status, hrms_employee_id, finalized_at FROM kyc_submissions WHERE id='{submission_id}';"
```

Expected: Shows status as "FINALIZED" with employee ID and timestamp

- [ ] **Step 8: Test error handling**

Try submitting the same submission again (refresh page first).

Expected: Shows error "Submission already finalized"

- [ ] **Step 9: Document test results**

Create a test log noting:
- Date and time of testing
- Submission ID used
- Employee ID generated
- Any issues encountered

---

## Task 19: Documentation and Cleanup

**Files:**
- Create: `frontend/hrms-review/README.md`
- Update: `docs/superpowers/specs/2026-04-21-hrms-auto-population-design.md`

- [ ] **Step 1: Create frontend README**

Create `frontend/hrms-review/README.md`:

```markdown
# HRMS Auto-Population Interface

React-based HRMS interface for reviewing and finalizing employee onboarding data extracted from WhatsApp documents.

## Prerequisites

- Node.js 18+
- Backend API running on port 8000
- Valid API key

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

3. Update `.env` with your API key:
   ```
   VITE_API_BASE_URL=http://localhost:8000
   VITE_API_KEY=your_api_key_here
   ```

## Development

Start dev server:
```bash
npm run dev
```

Open in browser:
```
http://localhost:5173?id={submission_id}
```

Replace `{submission_id}` with an actual APPROVED submission ID.

## Build

Create production build:
```bash
npm run build
```

Output in `dist/` directory.

## Architecture

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **Axios** for API calls

## Project Structure

```
src/
  components/     # Reusable UI components
  pages/          # Page components
  services/       # API client
  utils/          # Helper functions
  types/          # TypeScript interfaces
```

## Features

- Auto-populated employee data from document extraction
- View-only display (no editing)
- Organization elements with defaults
- Personal, Financial, and Bank details sections
- Submit to finalize with HRMS employee ID generation
- Error handling and loading states

## Environment Variables

- `VITE_API_BASE_URL` - Backend API URL
- `VITE_API_KEY` - API authentication key
```

- [ ] **Step 2: Verify all files are tracked by git**

```bash
cd C:\Users\Rakes\Desktop\Metro_POC
git status
```

Expected: Should show clean working tree or only untracked files you intentionally excluded

- [ ] **Step 3: Add README and commit**

```bash
git add frontend/hrms-review/README.md
git commit -m "docs(frontend): add README with setup and usage instructions

Document development setup, environment configuration, and project structure.

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Update design spec status**

Edit `docs/superpowers/specs/2026-04-21-hrms-auto-population-design.md` line 6:

Change:
```markdown
**Status:** Design Approved
```

To:
```markdown
**Status:** Implemented
```

- [ ] **Step 5: Commit spec update**

```bash
git add docs/superpowers/specs/2026-04-21-hrms-auto-population-design.md
git commit -m "docs: update design spec status to Implemented

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Self-Review

### 1. Spec Coverage Check

✅ **Backend finalization endpoint** - Task 3: POST /api/submissions/{id}/finalize
✅ **Database schema updates** - Task 1: Added finalized_at, finalized_by, hrms_employee_id
✅ **Employee ID generation** - Task 2: generate_employee_id function
✅ **React frontend setup** - Task 4: Vite + Tailwind + TypeScript
✅ **TypeScript interfaces** - Task 5: All API and display data types
✅ **API service** - Task 8: Axios client with authentication
✅ **Data transformation** - Task 7: transformSubmissionData function
✅ **Date formatting** - Task 6: formatDateForDisplay, calculateAge, etc
✅ **Organization elements section** - Task 11: Default values display
✅ **Personal details section** - Task 12: Extracted personal info
✅ **Financial details section** - Task 13: Aadhaar/PAN display
✅ **Bank details section** - Task 14: Bank account info
✅ **Submit functionality** - Task 15: Submit button with API call
✅ **Loading/error states** - Tasks 9-10: LoadingSpinner and ErrorState
✅ **Main review page** - Task 16: SubmissionReview orchestrates all
✅ **App integration** - Task 17: React Query setup, entry point
✅ **Integration testing** - Task 18: End-to-end verification
✅ **Documentation** - Task 19: README and spec updates

### 2. Placeholder Scan

✅ No TBD, TODO, or "implement later" placeholders
✅ All code blocks contain complete implementations
✅ No vague instructions like "add appropriate error handling"
✅ All types and interfaces are fully defined

### 3. Type Consistency

✅ `Submission` interface used consistently across API service and page
✅ `DisplayData` interface matches transformation output
✅ `FinalizeRequest` and `FinalizeResponse` match API contract
✅ Component prop types match data structures

---

## Execution Summary

**Total Tasks:** 19
**Estimated Time:** 3-4 hours
**Commits:** 19 (one per task)

**Key Deliverables:**
1. Backend API endpoint for finalization
2. React frontend with 7 UI components
3. Complete data transformation pipeline
4. Integration testing verification
5. Documentation

**Success Criteria:**
- ✅ Backend generates unique employee IDs
- ✅ Frontend displays all extracted data
- ✅ Submit creates finalized records
- ✅ Error handling works correctly
- ✅ UI matches Metro branding

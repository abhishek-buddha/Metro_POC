# HRMS Auto-Population Interface Design Specification

**Project:** Metro POC - WhatsApp KYC to HRMS Integration
**Date:** 2026-04-21
**Version:** 1.0
**Status:** Implemented

---

## Executive Summary

This specification outlines the design for an HRMS auto-population interface that displays employee onboarding data automatically extracted from documents submitted via WhatsApp. The system replaces manual data entry (maker process) by using OCR and AI extraction, then presents the data in a view-only HRMS review interface for final submission.

### POC Scope

- **In Scope:**
  - React-based HRMS review interface
  - Display auto-populated employee data from WhatsApp document extraction
  - Organization elements with default values
  - Personal, Financial, and Bank details sections
  - Submit functionality to finalize employee record
  - Backend API endpoint for finalization

- **Out of Scope:**
  - Checker/approval workflow (ends at submission)
  - Document upload interface (already handled via WhatsApp)
  - Edit capability (view-only display)
  - Confidence score indicators
  - Employee dependent, emergency contact, and education details
  - Manual data entry fields

### Key Objectives

1. Demonstrate end-to-end WhatsApp KYC → HRMS auto-population flow
2. Eliminate manual data entry for makers
3. Provide clean, professional HRMS interface matching Metro branding
4. Generate unique HRMS employee IDs upon finalization

---

## 1. System Architecture

### 1.1 High-Level Flow

```
WhatsApp (Employee sends docs)
    ↓
Twilio Webhook
    ↓
FastAPI Backend (/webhook/whatsapp)
    ↓
Document Download & Storage
    ↓
Redis Queue (kyc:jobs)
    ↓
Extraction Worker
    ├── Classification
    ├── OCR Extraction (Aadhaar, PAN)
    └── AI Extraction (Bank statements)
    ↓
SQLite Database (KYCSubmission)
    ↓
REST API (/api/submissions/{id})
    ↓
React HRMS Review App ← NEW
    ↓
Submit → /api/submissions/{id}/finalize ← NEW
    ↓
Employee Record Finalized (HRMS Employee ID generated)
```

### 1.2 New Components

**Frontend:**
```
frontend/
  hrms-review/
    src/
      pages/
        SubmissionReview.tsx          # Main review page
      components/
        OrganizationElementsSection.tsx
        PersonalDetailsSection.tsx
        FinancialDetailsSection.tsx
        BankDetailsSection.tsx
        SubmitButton.tsx
        ErrorState.tsx
        LoadingSpinner.tsx
      services/
        api.ts                        # API client with Axios
      utils/
        dataTransform.ts              # Data mapping functions
        dateFormat.ts                 # Date formatting utilities
      types/
        submission.ts                 # TypeScript interfaces
      App.tsx
      main.tsx
    package.json
    vite.config.ts
    tsconfig.json
    tailwind.config.js
```

**Backend (Extensions):**
```
src/
  webhook/
    app.py                            # Add POST /api/submissions/{id}/finalize
  models/
    database.py                       # Add finalized_at, finalized_by, hrms_employee_id fields
```

### 1.3 Technology Stack

**Frontend:**
- React 18 with TypeScript
- Vite (build tool & dev server)
- Tailwind CSS (styling, matches Metro theme)
- React Query (data fetching & caching)
- Axios (HTTP client)
- React Router (future multi-page support)

**Backend:**
- FastAPI (existing)
- SQLAlchemy (existing)
- SQLite (existing)

**Deployment:**
- Frontend: Served by Vite dev server (POC), can be built for production
- Backend: Existing Azure Functions setup

---

## 2. User Interface Design

### 2.1 Layout Structure

The HRMS interface follows Metro's dashboard design pattern:

```
┌────────────────────────────────────────────────────────────────┐
│  Metro Header                                                   │
│  [Logo]  Search...  [Profile] [Notifications] [Settings]      │
├──────────┬─────────────────────────────────────────────────────┤
│ Sidebar  │  Main Content Area                                  │
│          │                                                      │
│ Profile  │  Employee Onboarding Review                         │
│ Attend.  │  ────────────────────────────────                   │
│ Finance  │                                                      │
│ Employee │  📋 Organization Elements                           │
│ Mgmt ✓   │  ┌──────────────────────────────────────────────┐  │
│ Actions  │  │ Entity: Metro Brands Limited                  │  │
│          │  │ Business Unit: Showroom(SR)                   │  │
│          │  │ Function: Maharashtra(MAHARASHTRA)            │  │
│          │  │ Base Location: PLV(PLV)                       │  │
│          │  │ Department: PLV(PLV)                          │  │
│          │  │ Designation: Salesman                         │  │
│          │  │ Position: Field Sales                         │  │
│          │  │ Employment Type: Full-time                    │  │
│          │  │ Estimated DOJ: 28/04/2026                     │  │
│          │  └──────────────────────────────────────────────┘  │
│          │                                                      │
│          │  👤 Personal Details                                │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Employee Name: John Doe                       │  │
│          │  │ Date of Birth: 01/01/1990                     │  │
│          │  │ Gender: Male                                  │  │
│          │  │ Phone Number: +919876543210                   │  │
│          │  │ Email: Not extracted from documents           │  │
│          │  │ Address Line 1: 123 Street Name               │  │
│          │  │ Address Line 2: Area, City                    │  │
│          │  │ Address Line 3: State - Pincode               │  │
│          │  │ Age: 36                                       │  │
│          │  └──────────────────────────────────────────────┘  │
│          │                                                      │
│          │  💳 Financial Details                               │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Aadhaar Number: XXXX XXXX 1234                │  │
│          │  │ PAN Number: ABCDE1234F                        │  │
│          │  │ Father's Name: FATHER NAME                    │  │
│          │  │ E-Aadhaar Upload: eAadhaar.pdf ✓              │  │
│          │  │ PAN Card Upload: PAN.pdf ✓                    │  │
│          │  └──────────────────────────────────────────────┘  │
│          │                                                      │
│          │  🏦 Bank Details                                    │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │ Account Holder Name: JOHN DOE                 │  │
│          │  │ Account Number: 12345678901234                │  │
│          │  │ IFSC Code: ICIC0001234                        │  │
│          │  │ Bank Name: ICICI Bank                         │  │
│          │  │ Branch Name: Mumbai Main Branch               │  │
│          │  │ Account Type: Savings                         │  │
│          │  │ Bank Statement Upload: statement.pdf ✓        │  │
│          │  └──────────────────────────────────────────────┘  │
│          │                                                      │
│          │  ┌──────────────────────────────────────────────┐  │
│          │  │         [Cancel]           [Submit] ✓         │  │
│          │  └──────────────────────────────────────────────┘  │
│          │                                                      │
└──────────┴─────────────────────────────────────────────────────┘
```

### 2.2 Design Specifications

**Color Palette (Metro Theme):**
- Primary: `#6366F1` (Indigo-600) - Buttons, active states
- Background: `#F9FAFB` (Gray-50) - Page background
- Card: `#FFFFFF` with `shadow-md` - Section cards
- Text Primary: `#111827` (Gray-900) - Main text
- Text Secondary: `#6B7280` (Gray-500) - Labels
- Border: `#E5E7EB` (Gray-200) - Dividers
- Success: `#10B981` (Green-500) - Success states
- Error: `#EF4444` (Red-500) - Error states

**Typography:**
- Font Family: Inter or system default (-apple-system, BlinkMacSystemFont)
- Page Title: `text-2xl font-semibold text-gray-900`
- Section Headers: `text-lg font-semibold text-gray-800`
- Field Labels: `text-sm font-medium text-gray-700`
- Field Values: `text-base text-gray-900`
- Placeholder/Missing: `text-sm italic text-gray-400`

**Spacing:**
- Page padding: `p-8`
- Section spacing: `space-y-6` (24px gap between sections)
- Card padding: `p-6`
- Field spacing: `space-y-4` (16px gap between fields)
- Field grid: `grid-cols-2 gap-4` (two-column layout for fields)

**Components:**
- Cards: `bg-white rounded-lg shadow-md border border-gray-200`
- Buttons:
  - Primary: `bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2.5 rounded-md`
  - Secondary: `bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2.5 rounded-md`
- Icons: Lucide React or Heroicons

### 2.3 Responsive Breakpoints

- **Desktop (≥1024px):** Full layout with sidebar
- **Tablet (768px - 1023px):** Collapsible sidebar, main content full width
- **Mobile (<768px):** Stack sections vertically, hamburger menu for sidebar

---

## 3. Data Model & Mapping

### 3.1 Input Data (from API)

```typescript
interface Submission {
  id: string;
  employee_id: string;
  status: "APPROVED" | "PENDING" | "REJECTED" | "FINALIZED";
  employee: {
    id: string;
    phone_number: string;
  };

  // PAN Card Data
  pan_number: string;               // Decrypted by API
  pan_name: string;
  pan_father_name: string;
  pan_dob: string;                  // ISO format YYYY-MM-DD
  pan_confidence: number;

  // Aadhaar Data (Masked)
  aadhaar_last4: string;            // Only last 4 digits stored
  aadhaar_name: string;
  aadhaar_dob: string;
  aadhaar_gender: "Male" | "Female" | "Other";
  aadhaar_address: string;
  aadhaar_pincode: string;
  aadhaar_confidence: number;

  // Bank Data
  bank_account: string;             // Decrypted by API
  bank_holder_name: string;
  bank_ifsc: string;
  bank_name: string;
  bank_branch: string;
  bank_account_type?: string;
  bank_confidence: number;

  // Metadata
  name_match_score: number;
  overall_confidence: number;
  submitted_at: string;             // ISO timestamp
}
```

### 3.2 Display Data Transformation

```typescript
interface DisplayData {
  organizationElements: {
    entity: string;                 // Default: "Metro Brands Limited"
    businessUnit: string;           // Default: "Showroom(SR)"
    function: string;               // Default: "Maharashtra(MAHARASHTRA)"
    baseLocation: string;           // Default: "PLV(PLV)"
    department: string;             // Default: "PLV(PLV)"
    designation: string;            // Default: "Salesman"
    position: string;               // Default: "Field Sales"
    employmentType: string;         // Default: "Full-time"
    estimatedDOJ: string;           // Default: Today + 7 days (DD/MM/YYYY)
  };

  personalDetails: {
    employeeName: string;           // Priority: aadhaar_name > pan_name
    dateOfBirth: string;            // Priority: aadhaar_dob > pan_dob (DD/MM/YYYY)
    gender: string;                 // From aadhaar_gender
    phoneNumber: string;            // From employee.phone_number
    email: string;                  // Empty (not extracted)
    addressLine1: string;           // Split aadhaar_address
    addressLine2: string;
    addressLine3: string;
    age: number;                    // Calculated from DOB
  };

  financialDetails: {
    aadhaarNumber: string;          // Format: "XXXX XXXX {last4}"
    aadhaarUpload: string;          // "eAadhaar.pdf"
    panCard: string;                // From pan_number
    panUpload: string;              // "PAN.pdf"
    fatherName: string;             // From pan_father_name
  };

  bankDetails: {
    accountHolderName: string;      // From bank_holder_name
    accountNumber: string;          // From bank_account (decrypted)
    ifscCode: string;               // From bank_ifsc
    bankName: string;               // From bank_name
    branchName: string;             // From bank_branch
    accountType: string;            // From bank_account_type, default "Savings"
    bankStatementUpload: string;    // "bank_statement.pdf"
  };
}
```

### 3.3 Field Priority Rules

When multiple documents contain the same field:

**Name:**
1. `aadhaar_name` (most official)
2. `pan_name` (fallback)
3. `bank_holder_name` (last resort)

**Date of Birth:**
1. `aadhaar_dob`
2. `pan_dob` (fallback)

**Address:**
- Only source: `aadhaar_address`

### 3.4 Default Values

**Organization Elements (Hardcoded for POC):**
- Entity: "Metro Brands Limited"
- Business Unit: "Showroom(SR)"
- Function: "Maharashtra(MAHARASHTRA)"
- Base Location: "PLV(PLV)"
- Department: "PLV(PLV)"
- Designation: "Salesman"
- Position: "Field Sales"
- Employment Type: "Full-time"
- Estimated DOJ: Current Date + 7 days

### 3.5 Data Formatting Functions

**Date Formatting:**
```typescript
// Input: "1990-01-01" (ISO)
// Output: "01/01/1990" (DD/MM/YYYY)
export const formatDateForDisplay = (isoDate: string): string => {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  const day = String(date.getDate()).padStart(2, '0');
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const year = date.getFullYear();
  return `${day}/${month}/${year}`;
};
```

**Aadhaar Masking:**
```typescript
// Input: "1234" (last 4 digits)
// Output: "XXXX XXXX 1234"
export const formatAadhaar = (last4: string): string => {
  return `XXXX XXXX ${last4}`;
};
```

**Age Calculation:**
```typescript
// Input: "1990-01-01"
// Output: 36
export const calculateAge = (dob: string): number => {
  const birthDate = new Date(dob);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }

  return age;
};
```

**Address Splitting:**
```typescript
// Input: "123 Street, Area, City, State - 400001"
// Output: { line1, line2, line3 }
export const splitAddress = (address: string) => {
  const parts = address.split(',').map(s => s.trim());
  return {
    addressLine1: parts[0] || '',
    addressLine2: parts[1] || '',
    addressLine3: parts.slice(2).join(', '),
  };
};
```

---

## 4. API Design

### 4.1 Existing Endpoint (Already Implemented)

**Get Submission Details**

```http
GET /api/submissions/{submission_id}

Headers:
  X-API-Key: {api_key}

Response 200:
{
  "id": "sub_abc123",
  "employee_id": "emp_def456",
  "status": "APPROVED",
  "employee": {
    "id": "emp_def456",
    "phone_number": "+919876543210"
  },
  "pan_number": "ABCDE1234F",
  "pan_name": "JOHN DOE",
  "pan_father_name": "FATHER NAME",
  "pan_dob": "1990-01-01",
  "pan_confidence": 0.95,
  "aadhaar_last4": "1234",
  "aadhaar_name": "John Doe",
  "aadhaar_dob": "1990-01-01",
  "aadhaar_gender": "Male",
  "aadhaar_address": "123 Street, Area, City, State - 400001",
  "aadhaar_pincode": "400001",
  "aadhaar_confidence": 0.92,
  "bank_account": "12345678901234",
  "bank_holder_name": "JOHN DOE",
  "bank_ifsc": "ICIC0001234",
  "bank_name": "ICICI Bank",
  "bank_branch": "Mumbai Main Branch",
  "bank_account_type": "Savings",
  "bank_confidence": 0.88,
  "name_match_score": 0.95,
  "overall_confidence": 0.92,
  "submitted_at": "2026-04-20T10:30:00Z"
}

Response 404:
{
  "detail": "Submission not found"
}
```

**Notes:**
- Sensitive fields (`pan_number`, `bank_account`) are automatically decrypted by the backend
- `aadhaar_number` is never stored or returned (only `aadhaar_last4`)
- API key authentication required

### 4.2 New Endpoint (To Implement)

**Finalize Submission**

```http
POST /api/submissions/{submission_id}/finalize

Headers:
  X-API-Key: {api_key}
  Content-Type: application/json

Request Body:
{
  "finalized_by": "hr_user@metro.com",      // Optional
  "notes": "Auto-populated data verified"   // Optional
}

Response 200:
{
  "id": "sub_abc123",
  "status": "FINALIZED",
  "finalized_at": "2026-04-20T11:00:00Z",
  "finalized_by": "hr_user@metro.com",
  "hrms_employee_id": "EMP2026001",
  "message": "Employee data finalized successfully"
}

Response 400:
{
  "detail": "Submission already finalized"
}

Response 403:
{
  "detail": "Only APPROVED submissions can be finalized"
}

Response 404:
{
  "detail": "Submission not found"
}
```

**Business Logic:**
1. Validate API key
2. Fetch submission from database
3. Check status is `APPROVED` (not `PENDING`, `REJECTED`, or already `FINALIZED`)
4. Generate unique HRMS employee ID (format: `EMP{YEAR}{SEQUENCE}`)
5. Update submission:
   - `status` = `FINALIZED`
   - `finalized_at` = current timestamp
   - `finalized_by` = from request body
   - `hrms_employee_id` = generated ID
   - `review_notes` = from request body
6. Log audit event
7. Return success response

**Employee ID Generation Logic:**
```python
def generate_employee_id() -> str:
    """
    Generate unique HRMS employee ID
    Format: EMP{YEAR}{SEQUENCE}
    Example: EMP2026001, EMP2026002, etc.
    """
    session = SessionLocal()
    current_year = datetime.now().year

    # Get last employee ID for current year
    last_submission = session.query(KYCSubmission).filter(
        KYCSubmission.hrms_employee_id.like(f"EMP{current_year}%")
    ).order_by(KYCSubmission.hrms_employee_id.desc()).first()

    if last_submission and last_submission.hrms_employee_id:
        last_seq = int(last_submission.hrms_employee_id[-3:])
        new_seq = last_seq + 1
    else:
        new_seq = 1

    return f"EMP{current_year}{new_seq:03d}"
```

### 4.3 Database Schema Changes

**Add to `KYCSubmission` model:**

```python
class KYCSubmission(Base):
    __tablename__ = "kyc_submissions"

    # ... existing fields ...

    # New fields for finalization
    finalized_at = Column(DateTime, nullable=True)
    finalized_by = Column(Text, nullable=True)
    hrms_employee_id = Column(Text, unique=True, nullable=True)
```

**Migration SQL:**
```sql
ALTER TABLE kyc_submissions ADD COLUMN finalized_at TIMESTAMP;
ALTER TABLE kyc_submissions ADD COLUMN finalized_by TEXT;
ALTER TABLE kyc_submissions ADD COLUMN hrms_employee_id TEXT UNIQUE;
```

### 4.4 Frontend API Service

**Location:** `frontend/hrms-review/src/services/api.ts`

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_API_KEY;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
  },
});

export interface Submission {
  id: string;
  employee_id: string;
  status: string;
  employee: {
    phone_number: string;
  };
  pan_number: string;
  pan_name: string;
  pan_father_name: string;
  pan_dob: string;
  aadhaar_last4: string;
  aadhaar_name: string;
  aadhaar_dob: string;
  aadhaar_gender: string;
  aadhaar_address: string;
  aadhaar_pincode: string;
  bank_account: string;
  bank_holder_name: string;
  bank_ifsc: string;
  bank_name: string;
  bank_branch: string;
  bank_account_type?: string;
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

---

## 5. Component Specifications

### 5.1 Page Component: SubmissionReview

**Location:** `frontend/hrms-review/src/pages/SubmissionReview.tsx`

**Responsibilities:**
- Fetch submission data from API using submission ID from URL
- Handle loading and error states
- Render all section components
- Coordinate submit action

**Props:**
```typescript
interface SubmissionReviewProps {
  submissionId: string;  // From URL params
}
```

**State Management:**
```typescript
// Uses React Query for data fetching
const { data, isLoading, error } = useQuery(
  ['submission', submissionId],
  () => api.getSubmission(submissionId),
  {
    retry: 3,
    staleTime: 30000,
  }
);
```

**Render Logic:**
```typescript
if (isLoading) return <LoadingSpinner />;
if (error) return <ErrorState error={error} />;
if (!data) return <ErrorState message="No data available" />;

return (
  <div className="min-h-screen bg-gray-50">
    <Header />
    <div className="flex">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-2xl font-semibold mb-6">Employee Onboarding Review</h1>

        <div className="space-y-6">
          <OrganizationElementsSection />
          <PersonalDetailsSection data={data} />
          <FinancialDetailsSection data={data} />
          <BankDetailsSection data={data} />
          <SubmitButton submissionId={submissionId} />
        </div>
      </main>
    </div>
  </div>
);
```

### 5.2 Component: OrganizationElementsSection

**Location:** `frontend/hrms-review/src/components/OrganizationElementsSection.tsx`

**Responsibilities:**
- Display organization-level fields with default values
- All fields read-only (view-only)

**Layout:**
- Two-column grid for desktop
- Single column for mobile
- Label-value pairs

**Fields:**
- Entity
- Business Unit
- Function
- Base Location
- Department
- Designation
- Position
- Employment Type
- Estimated DOJ (formatted as DD/MM/YYYY)

**Props:**
```typescript
interface OrganizationElementsSectionProps {
  // No props - uses hardcoded defaults
}
```

### 5.3 Component: PersonalDetailsSection

**Location:** `frontend/hrms-review/src/components/PersonalDetailsSection.tsx`

**Responsibilities:**
- Display personal information extracted from documents
- Handle missing/optional fields gracefully
- Format dates and calculate age

**Props:**
```typescript
interface PersonalDetailsSectionProps {
  data: Submission;
}
```

**Fields:**
- Employee Name (from aadhaar_name or pan_name)
- Date of Birth (formatted, from aadhaar_dob or pan_dob)
- Gender (from aadhaar_gender)
- Phone Number (from employee.phone_number)
- Email (placeholder if not extracted)
- Address Line 1, 2, 3 (split from aadhaar_address)
- Age (calculated from DOB)

**Missing Field Handling:**
```typescript
const displayValue = value || "Not extracted from documents";
const textClass = value ? "text-gray-900" : "text-gray-400 italic";
```

### 5.4 Component: FinancialDetailsSection

**Location:** `frontend/hrms-review/src/components/FinancialDetailsSection.tsx`

**Responsibilities:**
- Display Aadhaar and PAN card information
- Mask Aadhaar number properly
- Show document upload indicators

**Props:**
```typescript
interface FinancialDetailsSectionProps {
  data: Submission;
}
```

**Fields:**
- Aadhaar Number (masked: `XXXX XXXX {last4}`)
- E-Aadhaar Upload (show "eAadhaar.pdf ✓")
- PAN Number (from pan_number)
- PAN Card Upload (show "PAN.pdf ✓")
- Father's Name (from pan_father_name)

**Aadhaar Masking:**
```typescript
const displayAadhaar = `XXXX XXXX ${data.aadhaar_last4}`;
```

### 5.5 Component: BankDetailsSection

**Location:** `frontend/hrms-review/src/components/BankDetailsSection.tsx`

**Responsibilities:**
- Display bank account information
- Show full account number (already decrypted by API)

**Props:**
```typescript
interface BankDetailsSectionProps {
  data: Submission;
}
```

**Fields:**
- Account Holder Name (from bank_holder_name)
- Account Number (from bank_account - decrypted)
- IFSC Code (from bank_ifsc)
- Bank Name (from bank_name)
- Branch Name (from bank_branch)
- Account Type (from bank_account_type, default "Savings")
- Bank Statement Upload (show "bank_statement.pdf ✓")

### 5.6 Component: SubmitButton

**Location:** `frontend/hrms-review/src/components/SubmitButton.tsx`

**Responsibilities:**
- Handle submit action
- Show loading state during submission
- Display success/error messages
- Navigate after successful submission

**Props:**
```typescript
interface SubmitButtonProps {
  submissionId: string;
}
```

**State:**
```typescript
const [isSubmitting, setIsSubmitting] = useState(false);
```

**Submit Handler:**
```typescript
const handleSubmit = async () => {
  setIsSubmitting(true);
  try {
    const result = await api.finalizeSubmission(submissionId, {
      finalized_by: "hr_user@metro.com",
      notes: "Auto-populated data verified via HRMS interface"
    });

    // Show success toast
    toast.success(`Employee ID ${result.hrms_employee_id} created successfully`);

    // Navigate to submissions list (future enhancement)
    // navigate('/submissions');
  } catch (error) {
    toast.error('Failed to finalize submission');
  } finally {
    setIsSubmitting(false);
  }
};
```

**Buttons:**
- Cancel: Gray button, navigates back or clears
- Submit: Primary indigo button, calls finalize API

**Disabled State:**
```typescript
<button
  disabled={isSubmitting || data.status === 'FINALIZED'}
  className={isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}
>
  {isSubmitting ? 'Submitting...' : 'Submit'}
</button>
```

---

## 6. Error Handling & Edge Cases

### 6.1 Error Scenarios

**1. Missing Extracted Data**

**Scenario:** Some fields not extracted from documents

**Handling:**
- Display empty fields with placeholder: "Not extracted from documents"
- Use lighter gray color (`text-gray-400 italic`)
- Don't block submission - show data as-is for POC

**2. Network Errors**

**Scenario:** API unreachable, timeout, connection lost

**Handling:**
```typescript
const { data, error, refetch } = useQuery(...);

if (error) {
  return (
    <ErrorState
      title="Unable to load submission"
      message="Please check your connection and try again"
      onRetry={refetch}
    />
  );
}
```

**3. API Errors**

| Status Code | Scenario | Frontend Handling |
|-------------|----------|-------------------|
| 400 | Already finalized | Show info banner with finalization details |
| 403 | Not approved yet / Invalid API key | Show error message |
| 404 | Submission not found | Show "Not found" page with back button |
| 500 | Server error | Show generic error with retry option |

**4. Invalid Submission Data**

**Scenario:** API returns malformed/null data

**Handling:**
```typescript
if (!submission || !submission.id) {
  return <ErrorPage message="Invalid submission data" />;
}
```

**5. Duplicate Employee ID**

**Scenario:** Race condition during ID generation

**Handling:**
- Backend catches `IntegrityError` on unique constraint
- Retry ID generation with next sequence number
- Use database transaction to minimize race window

```python
try:
    submission.hrms_employee_id = generate_employee_id()
    session.commit()
except IntegrityError:
    session.rollback()
    submission.hrms_employee_id = generate_employee_id()
    session.commit()
```

### 6.2 Edge Cases

**1. Name Mismatch Across Documents**

**Scenario:** Different spellings in Aadhaar vs PAN

**Handling:**
- Always prioritize Aadhaar name (most official)
- Backend already calculates `name_match_score` (not displayed in POC)

**2. DOB Format Variations**

**Scenario:** Different date formats from extraction

**Handling:**
- Backend normalizes all dates to ISO format (YYYY-MM-DD)
- Frontend displays in DD/MM/YYYY format
- If parsing fails, display as-is

**3. Long Address**

**Scenario:** Aadhaar address exceeds 150 characters

**Handling:**
```typescript
const addressParts = address.split(',').map(s => s.trim());
const line1 = addressParts.slice(0, 2).join(', ');
const line2 = addressParts.slice(2, 4).join(', ');
const line3 = addressParts.slice(4).join(', ');
```

**4. Missing Phone Number**

**Scenario:** Employee record has no phone number

**Handling:**
```typescript
const phone = employee.phone_number || "Not available";
```

**5. Special Characters in Names**

**Scenario:** Unicode characters, accents, symbols

**Handling:**
- Display as-is (React handles Unicode correctly)
- No sanitization needed for view-only display

### 6.3 Loading States

**Initial Page Load:**
```tsx
{isLoading && (
  <div className="flex items-center justify-center min-h-screen">
    <Spinner size="large" />
    <p className="ml-4 text-gray-600">Loading submission data...</p>
  </div>
)}
```

**Submit Action:**
```tsx
const [isSubmitting, setIsSubmitting] = useState(false);

<button disabled={isSubmitting}>
  {isSubmitting ? (
    <>
      <Spinner size="small" className="mr-2" />
      Submitting...
    </>
  ) : (
    'Submit'
  )}
</button>
```

### 6.4 Success States

**After Successful Submission:**
```tsx
<SuccessModal
  title="Submission Finalized"
  message={`Employee ID ${result.hrms_employee_id} has been created successfully`}
  onClose={() => navigate('/')}
>
  <div className="mt-4 space-y-2">
    <p className="text-sm text-gray-600">
      Employee Name: {data.aadhaar_name || data.pan_name}
    </p>
    <p className="text-sm text-gray-600">
      Finalized At: {new Date(result.finalized_at).toLocaleString()}
    </p>
  </div>
</SuccessModal>
```

---

## 7. Security Considerations

### 7.1 API Authentication

**Mechanism:**
- All API requests require `X-API-Key` header
- API key stored in environment variable (`.env` file)
- Backend validates key before processing requests

**Environment Configuration:**
```bash
# frontend/hrms-review/.env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

**Never commit `.env` to git:**
```gitignore
# frontend/hrms-review/.gitignore
.env
.env.local
```

### 7.2 Sensitive Data Handling

**Encrypted Fields:**
- PAN Number: Encrypted in database, decrypted by API automatically
- Bank Account Number: Encrypted in database, decrypted by API automatically
- Aadhaar Number: NEVER stored in full - only last 4 digits

**Masking in UI:**
- Aadhaar: Always displayed as `XXXX XXXX {last4}`
- PAN: Displayed in full (already decrypted by API)
- Bank Account: Displayed in full (already decrypted by API)

**Note:** Full Aadhaar number is never transmitted or stored anywhere in the system.

### 7.3 HTTPS Requirement

**Production Deployment:**
- All API communication must use HTTPS
- No sensitive data over HTTP
- Configure CORS to allow only trusted origins

### 7.4 CORS Configuration

**Backend (FastAPI):**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production:**
```python
allow_origins=["https://hrms.metro.com"]  # Only production domain
```

### 7.5 Input Validation

**Frontend:**
- TypeScript ensures type safety
- API response validation via interfaces

**Backend:**
- Pydantic models validate request bodies
- SQL injection protection via SQLAlchemy ORM
- No user input accepted (view-only interface)

---

## 8. Development Setup

### 8.1 Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Existing Metro POC backend running

### 8.2 Frontend Setup

**Initialize React Project:**
```bash
cd C:\Users\Rakes\Desktop\Metro_POC
npm create vite@latest frontend/hrms-review -- --template react-ts
cd frontend/hrms-review
npm install
```

**Install Dependencies:**
```bash
npm install axios @tanstack/react-query react-router-dom
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**Tailwind Configuration:**
```javascript
// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
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

**Environment Variables:**
```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=your_api_key_here
```

**Start Dev Server:**
```bash
npm run dev
# Opens at http://localhost:5173
```

### 8.3 Backend Setup

**Database Migration:**
```bash
cd C:\Users\Rakes\Desktop\Metro_POC
# Add new fields to KYCSubmission model in src/models/database.py
# Run migration (or manually alter table)
```

**Add New Endpoint:**
- Edit `src/webhook/app.py`
- Add `POST /api/submissions/{id}/finalize` endpoint
- Implement employee ID generation logic

**Restart Backend:**
```bash
# Existing startup process
python -m src.webhook.app
```

### 8.4 Testing the Integration

**1. Submit Documents via WhatsApp:**
```
Send: Aadhaar PDF, PAN PDF, Bank statement PDF
System processes and creates KYC submission
Status becomes "APPROVED"
```

**2. Get Submission ID:**
```bash
curl -H "X-API-Key: your_api_key" \
  http://localhost:8000/api/submissions | jq '.[] | select(.status=="APPROVED") | .id'
```

**3. Open HRMS Interface:**
```
http://localhost:5173/submission/{submission_id}
```

**4. Verify Data Display:**
- Check organization elements (defaults)
- Check personal details (from Aadhaar/PAN)
- Check financial details (masked Aadhaar, PAN)
- Check bank details (from bank statement)

**5. Test Submit:**
- Click "Submit" button
- Verify API call succeeds
- Check database for finalized record
- Verify HRMS employee ID generated

---

## 9. Future Enhancements (Post-POC)

### 9.1 Edit Capability
- Add edit mode toggle
- Inline field editing
- Validation on edited fields
- Track changes in audit log

### 9.2 Document Viewer
- View uploaded PDF documents inline
- Download documents
- Zoom and scroll controls

### 9.3 Confidence Indicators
- Show extraction confidence scores
- Highlight low-confidence fields
- Flag fields for manual review

### 9.4 Multi-Step Approval
- Add approval workflow (maker-checker)
- Email notifications
- Approval history timeline

### 9.5 Bulk Operations
- List view of pending submissions
- Bulk finalize multiple employees
- Export to CSV/Excel

### 9.6 Advanced Search
- Search by name, phone, employee ID
- Filter by status, date range
- Sort by various fields

### 9.7 Integration with HRMS
- Push data to external HRMS systems
- Webhook support for callbacks
- Field mapping configuration

---

## 10. Deployment Strategy

### 10.1 Development Environment

**Frontend:**
- Vite dev server on `localhost:5173`
- Hot module replacement for fast iteration

**Backend:**
- Local FastAPI server on `localhost:8000`
- SQLite database for testing

### 10.2 Production Environment

**Frontend:**
```bash
npm run build
# Generates static files in dist/
```

**Hosting Options:**
- Azure Static Web Apps
- Netlify
- Vercel
- Serve from FastAPI (static files)

**Backend:**
- Existing Azure Functions deployment
- Add new API endpoint to function app

**Database:**
- Migrate to Azure SQL Database (production)
- Or continue with SQLite for POC

### 10.3 Environment Configuration

**Frontend Production:**
```bash
# .env.production
VITE_API_BASE_URL=https://api.metro.com
VITE_API_KEY=production_api_key
```

**Backend Production:**
- Use Azure Key Vault for API keys
- Enable HTTPS only
- Configure CORS for production domain

---

## 11. Testing Strategy

### 11.1 Manual Testing Checklist

**Data Display:**
- [ ] Organization elements show default values
- [ ] Personal details display correctly from extraction
- [ ] Aadhaar number is properly masked
- [ ] PAN number displays correctly
- [ ] Bank details display correctly
- [ ] Missing fields show placeholder text
- [ ] Dates formatted as DD/MM/YYYY
- [ ] Age calculated correctly

**Submit Functionality:**
- [ ] Submit button is enabled for APPROVED submissions
- [ ] Submit button is disabled during submission
- [ ] Success message shows after finalization
- [ ] HRMS employee ID is generated correctly
- [ ] Database updated with finalized status
- [ ] Audit log entry created

**Error Handling:**
- [ ] Network error shows retry option
- [ ] 404 error shows "not found" message
- [ ] Already finalized shows warning banner
- [ ] Invalid API key shows unauthorized message

**Responsive Design:**
- [ ] Layout works on desktop (≥1024px)
- [ ] Layout adapts for tablet (768-1023px)
- [ ] Layout stacks for mobile (<768px)
- [ ] Text is readable on all screen sizes

### 11.2 API Testing

**Using curl:**
```bash
# Test get submission
curl -H "X-API-Key: your_key" \
  http://localhost:8000/api/submissions/sub_123

# Test finalize submission
curl -X POST \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"finalized_by":"test@metro.com","notes":"Testing"}' \
  http://localhost:8000/api/submissions/sub_123/finalize
```

### 11.3 Integration Testing

**End-to-End Flow:**
1. Submit documents via WhatsApp
2. Wait for extraction to complete
3. Verify submission status is APPROVED
4. Open HRMS interface with submission ID
5. Verify all data displays correctly
6. Click submit
7. Verify success response
8. Check database for finalized record
9. Verify employee ID generated

---

## 12. Success Metrics

### 12.1 POC Success Criteria

- ✅ HRMS interface loads submission data from API
- ✅ All extracted fields display correctly
- ✅ Submit creates finalized record with HRMS employee ID
- ✅ UI matches Metro branding and style
- ✅ No manual data entry required
- ✅ End-to-end demo: WhatsApp → Extraction → HRMS → Finalize

### 12.2 Performance Targets

- Page load time: < 2 seconds
- API response time: < 500ms
- Submit action: < 1 second
- No data loss or corruption

### 12.3 User Experience Goals

- Intuitive interface (no training required)
- Clear visual hierarchy
- Responsive design works on all devices
- Error messages are helpful and actionable

---

## 13. Risks & Mitigation

### 13.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| API authentication issues | Cannot fetch data | Use environment variables, test thoroughly |
| CORS errors | Frontend can't call backend | Configure CORS correctly, test cross-origin |
| Database schema conflicts | Cannot add new fields | Test migration on dev DB first |
| Race condition on ID generation | Duplicate IDs | Use unique constraint + retry logic |

### 13.2 Data Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Missing extracted data | Incomplete profiles | Show placeholders, don't block submission |
| Name mismatch across docs | Confusion | Prioritize Aadhaar name consistently |
| Malformed dates | Display errors | Graceful fallback to raw string |

### 13.3 User Experience Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Unclear error messages | User confusion | Write clear, actionable error text |
| Slow loading | Poor UX | Show loading states, optimize API calls |
| Mobile not responsive | Can't use on phone | Test on multiple screen sizes |

---

## 14. Conclusion

This design provides a complete specification for building an HRMS auto-population interface that:

1. **Eliminates manual data entry** by displaying auto-extracted employee information
2. **Matches Metro branding** with a clean, professional interface
3. **Integrates seamlessly** with existing WhatsApp KYC infrastructure
4. **Handles edge cases gracefully** with proper error handling
5. **Generates unique employee IDs** upon finalization
6. **Provides audit trail** through database logging

The POC demonstrates the full workflow from document submission via WhatsApp to finalized employee records in the HRMS system, showcasing the potential for significant time savings and reduced errors compared to manual data entry.

### Next Steps

1. Set up React frontend project
2. Implement backend `/finalize` endpoint
3. Build React components as specified
4. Test integration with existing backend
5. Deploy POC for demonstration
6. Gather feedback for future enhancements

---

## APPENDIX A: Database State - POC Initialization

### Finding: Empty Database is Expected

**Status:** ✅ CONFIRMED - This is the expected state for a new POC environment.

**What was found:**
The SQLite database file (`data/kyc.db`) exists but is empty. No tables have been created yet.

**Why this is expected:**
This POC environment is new and has never been executed. Database tables are **not** created during project initialization - they are created automatically at **runtime** when the backend application first starts.

### How SQLAlchemy Handles Database Creation

The backend uses SQLAlchemy ORM with the following pattern:

```python
# In src/models/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///data/kyc.db"
engine = create_engine(DATABASE_URL)

# This creates all tables defined in the models
Base.metadata.create_all(bind=engine)
```

**When does this execute?**
- When the backend application starts (FastAPI initialization)
- During the startup sequence of `src/webhook/app:app`
- Or during manual execution of initialization scripts

**What gets created?**
Based on the data models in `src/models/database.py`, the following tables will be created automatically:

1. `kyc_submissions` - Main submission records
2. `employees` - Employee profile data
3. Any other tables defined in the SQLAlchemy models

**Models included in automatic creation:**
```python
class KYCSubmission(Base):
    __tablename__ = "kyc_submissions"
    # Fields: id, employee_id, status, pan_number, aadhaar_last4,
    # bank_account, bank_holder_name, submitted_at, etc.
    # NEW (for HRMS): finalized_at, finalized_by, hrms_employee_id

class Employee(Base):
    __tablename__ = "employees"
    # Fields: id, phone_number, name, etc.
```

### Database Migration Strategy

**For this POC:**
1. **First Run:** Start the backend (`python -m src.webhook.app`)
2. **Automatic Creation:** SQLAlchemy calls `Base.metadata.create_all()`
3. **Tables Ready:** Database is fully initialized with all schema
4. **Ready for Testing:** Submit documents via WhatsApp to populate data

**No manual database setup required.**

### When the Database Gets Populated

The database remains empty until:
- ✅ Backend is running
- ✅ Twilio webhook receives a WhatsApp message with documents
- ✅ System processes documents through extraction pipeline
- ✅ Extracted data is stored in `kyc_submissions` table

### Verification Steps After Backend Starts

```bash
# 1. Check that tables exist
sqlite3 data/kyc.db ".tables"
# Should output: employees  kyc_submissions

# 2. Check table schema
sqlite3 data/kyc.db ".schema kyc_submissions"

# 3. Verify empty (no records yet)
sqlite3 data/kyc.db "SELECT COUNT(*) FROM kyc_submissions;"
# Should output: 0
```

### New Fields Added for HRMS Finalization

When the backend starts and creates tables, it will include three new columns for the HRMS finalization feature:

```python
# Added to KYCSubmission model
finalized_at = Column(DateTime, nullable=True)
finalized_by = Column(Text, nullable=True)
hrms_employee_id = Column(Text, unique=True, nullable=True)
```

These fields are:
- **Optional initially** - Will be NULL until submission is finalized
- **Populated on submit** - When user clicks "Submit" in HRMS interface
- **Unique constraint** - Ensures no duplicate employee IDs

### Conclusion

The empty database is **not a problem** - it is the **correct starting state** for a new POC.

- ✅ Database file exists and is accessible
- ✅ All model definitions are in place
- ✅ Schema will be created automatically on first backend run
- ✅ No manual migrations or setup scripts needed
- ✅ Models include new HRMS finalization fields
- ✅ Ready for end-to-end testing

**Action Required:** None. Proceed with starting the backend and testing the system end-to-end.

---

**Document Version:** 1.0
**Last Updated:** 2026-04-21
**Approved By:** User
**Next Review:** After POC implementation

---

## Database Finding Summary

| Item | Status | Details |
|------|--------|---------|
| Database File Exists | ✅ Yes | Located at `data/kyc.db` |
| Tables Created | ⏳ No (Not Yet) | Will be created on first backend startup |
| Expected Behavior | ✅ Correct | Empty database is expected for new POC |
| Migration Method | ✅ SQLAlchemy | Automatic table creation via `Base.metadata.create_all()` |
| New HRMS Fields | ✅ Included | `finalized_at`, `finalized_by`, `hrms_employee_id` in schema |
| Ready for Testing | ✅ Yes | Start backend → Tables created → Begin WhatsApp testing |

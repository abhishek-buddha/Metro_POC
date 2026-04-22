# Metro HRMS POC - Component Architecture Map

## Application Structure

```
App.tsx (Router)
└── MainLayout
    ├── Sidebar (60px fixed)
    ├── Header (top bar)
    └── Main Content
        └── Routes
            ├── / → EmployeeList
            └── /employee/:id/form → EmployeeForm
```

## Component Hierarchy

### Route 1: Employee List (`/`)

```
EmployeeList
├── Page Header
│   ├── Title: "Add Employees List"
│   └── Tabs (Onboarding active)
│       └── Sub-tabs (Add Employees, Bulk Uploads, Requests)
├── Content Layout (flex)
│   ├── FilterPanel (left, 256px)
│   │   ├── Submission Status dropdown
│   │   ├── Submission Level dropdown
│   │   └── Apply button
│   └── Table Container (flex-1)
│       ├── Table Header
│       │   ├── Title
│       │   └── "Add New" button
│       ├── Table
│       │   ├── Header Row
│       │   │   ├── Employee Name
│       │   │   ├── Temp ID
│       │   │   ├── Employee ID
│       │   │   ├── Entity Name
│       │   │   ├── Submission Status
│       │   │   ├── Submission Level
│       │   │   └── Actions
│       │   └── Body Rows (map)
│       │       ├── Avatar + Name
│       │       ├── Temp ID
│       │       ├── Employee ID
│       │       ├── Entity Name
│       │       ├── Status Badge
│       │       ├── Level Text
│       │       └── ThreeDotMenu
│       │           ├── View Details
│       │           ├── Proceed
│       │           └── Cancel
│       └── Pagination Footer
└── State Management
    ├── submissions (from API)
    ├── filteredSubmissions
    ├── filters (status, level)
    ├── loading
    └── error
```

### Route 2: Employee Form (`/employee/:id/form`)

```
EmployeeForm
├── Page Header
│   ├── Title: "Employee Form"
│   └── Subtitle: Temp ID | Name
├── Stepper Container
│   └── Steps (1-2-3)
│       ├── Step 1: Personal Details
│       │   ├── Number circle (active: indigo, completed: green)
│       │   └── Title text
│       ├── Connector Line
│       ├── Step 2: Company Structure & Policies
│       ├── Connector Line
│       └── Step 3: Payroll
├── Form Container
│   └── Step 1 Content
│       ├── Personal Details Section
│       │   ├── First Name input
│       │   ├── Full Name input
│       │   ├── DOB input (→ auto-calc age)
│       │   ├── Gender select
│       │   ├── Blood Group select
│       │   ├── Marital Status select
│       │   ├── Official Email input
│       │   ├── Official Contact input
│       │   ├── Personal Email input
│       │   ├── Personal Contact input
│       │   ├── Address Line 1 input
│       │   ├── Address Line 2 input
│       │   ├── Address Line 3 input
│       │   ├── Address Line 4 input
│       │   ├── Age input (read-only)
│       │   └── Spouse Name input
│       ├── Financial Details Section
│       │   ├── FileUpload (Aadhaar)
│       │   │   └── → opens DocumentViewer (with password)
│       │   ├── Father Name input
│       │   ├── FileUpload (PAN)
│       │   │   └── → opens DocumentViewer
│       │   └── E-Aadhar Password input
│       ├── Bank Details Section
│       │   ├── Account Number input
│       │   ├── IFSC Code input
│       │   ├── Bank Name input
│       │   ├── Bank Branch Address input
│       │   └── FileUpload (Cancelled Cheque)
│       │       └── → opens DocumentViewer
│       └── Other Details Section
│           ├── FileUpload (Resume)
│           ├── FileUpload (Educational Docs)
│           ├── FileUpload (Profile Photo)
│           ├── FileUpload (NAPS Letter)
│           ├── FileUpload (Signature)
│           ├── Grade select
│           ├── Division select
│           └── Category select
├── Form Actions
│   ├── Cancel button
│   ├── Back button (if step > 1)
│   └── Proceed/Submit button
├── DocumentViewer Modal (conditional)
│   ├── Header
│   │   ├── Title + Document name
│   │   └── Close button (X)
│   ├── Content
│   │   ├── Password Dialog (if required)
│   │   │   ├── Password input
│   │   │   ├── Cancel button
│   │   │   └── OK button
│   │   └── Document Display
│   │       ├── PDF iframe
│   │       └── Image tag
│   └── Footer
│       └── Close button
└── State Management
    ├── currentStep (1-3)
    ├── submission (from API)
    ├── formData (all fields)
    ├── documentViewer (isOpen, url, name, requiresPassword)
    └── loading
```

## Reusable Components Detail

### 1. MainLayout

**Props**: `{ children: ReactNode }`

**Structure**:
```
<div className="flex h-screen">
  <Sidebar />
  <div className="flex-1 flex flex-col">
    <Header />
    <main>{children}</main>
  </div>
</div>
```

**Features**:
- Fixed sidebar (60px width)
- Navigation icons with active states
- Search bar in header
- User profile section
- Notification icons

---

### 2. FilterPanel

**Props**: `{ filters, onFilterChange, onApply }`

**Structure**:
```
<div className="bg-white rounded-lg border p-4">
  <select>Submission Status</select>
  <select>Submission Level</select>
  <button>Apply</button>
</div>
```

**State**: Controlled by parent (EmployeeList)

---

### 3. ThreeDotMenu

**Props**: `{ onViewDetails, onProceed, onCancel }`

**Structure**:
```
<div className="relative">
  <button>⋮</button>
  {isOpen && (
    <div className="dropdown">
      <button onClick={onViewDetails}>View Details</button>
      <button onClick={onProceed}>Proceed</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  )}
</div>
```

**Features**:
- Click to toggle
- Click outside to close
- Three action options
- Positioned relative to button

---

### 4. FileUpload

**Props**: `{ label, value, onChange, onView, accept, required, maxSize, allowedFormats, existingFileUrl }`

**Structure**:
```
<div>
  <label>{label}</label>
  {hasFile ? (
    <div className="file-preview">
      <span>{filename}</span>
      <button onClick={onView}>👁</button>
      <button onClick={clear}>🗑</button>
    </div>
  ) : (
    <button onClick={triggerInput}>Upload</button>
  )}
  <input type="file" hidden />
</div>
```

**Features**:
- File selection
- Preview with name
- View action (opens DocumentViewer)
- Delete action
- File type validation

---

### 5. DocumentViewer

**Props**: `{ isOpen, onClose, documentUrl, documentName, requiresPassword }`

**Structure**:
```
{isOpen && (
  <div className="modal-overlay">
    <div className="modal">
      <header>
        <h2>{documentName}</h2>
        <button onClick={onClose}>×</button>
      </header>
      <div className="content">
        {requiresPassword && !isUnlocked ? (
          <PasswordDialog />
        ) : (
          <iframe src={documentUrl} />
        )}
      </div>
      <footer>
        <button onClick={onClose}>Close</button>
      </footer>
    </div>
  </div>
)}
```

**Features**:
- Modal overlay (fixed, full screen)
- Password protection dialog
- PDF/Image display
- Close functionality

---

## Data Flow

### Loading Employee List

```
1. EmployeeList mounts
   ↓
2. useEffect → fetchSubmissions()
   ↓
3. API call: GET /api/submissions
   ↓
4. Backend returns: [{ id, status: "APPROVED", ... }]
   ↓
5. setSubmissions(data)
   ↓
6. setFilteredSubmissions(data)
   ↓
7. Render table rows
   ↓
8. Map status: "APPROVED" → { text: "In Progress", color: "orange" }
```

### Filtering Employees

```
1. User selects filter → onFilterChange
   ↓
2. Update filters state
   ↓
3. User clicks Apply → applyFilters()
   ↓
4. Filter submissions array
   ↓
5. setFilteredSubmissions(filtered)
   ↓
6. Table re-renders with filtered data
```

### Opening Employee Form

```
1. User clicks "Proceed" → handleProceed(id)
   ↓
2. navigate(`/employee/${id}/form`)
   ↓
3. EmployeeForm mounts with :id param
   ↓
4. useEffect → fetchSubmission(id)
   ↓
5. API call: GET /api/submissions/:id
   ↓
6. Backend returns: { aadhaar_name, pan_name, pan_dob, ... }
   ↓
7. Map backend data → formData state
   ↓
8. Render form with pre-populated values
```

### Auto-Calculating Age

```
1. User changes DOB input → handleInputChange('dob', value)
   ↓
2. Update formData.dob
   ↓
3. useEffect [formData.dob] triggers
   ↓
4. calculateAge(formData.dob)
   ↓
5. Update formData.age
   ↓
6. Age input re-renders with calculated value
```

### Viewing Document

```
1. User clicks eye icon → handleViewDocument(url, name, requiresPassword)
   ↓
2. setDocumentViewer({ isOpen: true, url, name, requiresPassword })
   ↓
3. DocumentViewer renders
   ↓
4. If requiresPassword:
   a. Show password dialog
   b. User enters password
   c. Click OK → setIsUnlocked(true)
   d. Show document
   ↓
5. Display PDF in iframe or image in <img>
```

### Submitting Form

```
1. User completes steps → clicks Submit
   ↓
2. handleSubmit()
   ↓
3. API call: POST /api/submissions/:id/finalize
   ↓
4. Send formData in request body
   ↓
5. Backend processes and responds
   ↓
6. Show success alert
   ↓
7. navigate('/') → back to list
```

## State Management

### EmployeeList State

```typescript
{
  submissions: Submission[],           // All data from API
  filteredSubmissions: Submission[],   // After filtering
  loading: boolean,                    // API call status
  error: string | null,                // Error messages
  filters: {
    submissionStatus: string,          // Selected status
    submissionLevel: string            // Selected level
  },
  activeTab: string                    // Current tab name
}
```

### EmployeeForm State

```typescript
{
  currentStep: number,                 // 1, 2, or 3
  loading: boolean,                    // Fetching data
  submission: Submission | null,       // Original API data
  formData: EmployeeFormData,          // Form field values
  documentViewer: {
    isOpen: boolean,                   // Modal visible
    url: string,                       // Document URL
    name: string,                      // Display name
    requiresPassword: boolean          // Password needed
  }
}
```

### FilterPanel State

Controlled by parent - no internal state

### ThreeDotMenu State

```typescript
{
  isOpen: boolean                      // Dropdown visible
}
```

### FileUpload State

Props-driven - file value from parent

### DocumentViewer State

```typescript
{
  password: string,                    // User input
  showPasswordDialog: boolean,         // Dialog visible
  isUnlocked: boolean                  // Document unlocked
}
```

## API Integration Points

### 1. GET /api/submissions
- **Used in**: EmployeeList.tsx
- **Trigger**: Component mount
- **Response**: Array of Submission objects
- **Updates**: submissions and filteredSubmissions state

### 2. GET /api/submissions/:id
- **Used in**: EmployeeForm.tsx
- **Trigger**: Component mount with id param
- **Response**: Single Submission object
- **Updates**: submission and formData state

### 3. POST /api/submissions/:id/finalize
- **Used in**: EmployeeForm.tsx
- **Trigger**: Form submission (Step 3)
- **Request**: formData object
- **Response**: Success/error message
- **Action**: Navigate back to list

## Styling Architecture

### Tailwind Utility Classes Used

**Colors**:
- `bg-indigo-600` - Primary buttons, active states
- `text-indigo-600` - Primary text, active tabs
- `bg-orange-100` - In Progress badge background
- `text-orange-700` - In Progress badge text
- `bg-gray-50` - Page background
- `bg-white` - Cards, surfaces
- `text-gray-900` - Primary text
- `border-gray-200` - Borders

**Spacing**:
- `p-4, p-6` - Padding
- `space-y-4, space-y-6` - Vertical spacing
- `gap-6` - Grid gaps
- `mb-2, mb-4, mb-6` - Margins

**Layout**:
- `flex, flex-1` - Flexbox
- `grid grid-cols-2` - 2-column grids
- `w-full, h-full` - Full width/height
- `max-w-xl, max-w-4xl` - Max widths

**Interactive**:
- `hover:bg-gray-100` - Hover states
- `focus:outline-none` - Focus states
- `transition-colors` - Smooth transitions
- `cursor-pointer` - Pointer cursor

**Typography**:
- `text-sm, text-base, text-lg, text-xl, text-2xl` - Sizes
- `font-medium, font-semibold, font-bold` - Weights

## File Dependencies

```
App.tsx
├── imports: MainLayout, EmployeeList, EmployeeForm
├── imports: react-router-dom

MainLayout.tsx
├── imports: react-router-dom (Link, useLocation)
├── imports: lucide-react (icons)

EmployeeList.tsx
├── imports: react, react-router-dom
├── imports: lucide-react (Plus)
├── imports: FilterPanel, ThreeDotMenu
├── imports: utils/types (Submission, FilterState)
├── imports: utils/api (submissionApi, helpers)

EmployeeForm.tsx
├── imports: react, react-router-dom
├── imports: lucide-react (Check)
├── imports: FileUpload, DocumentViewer
├── imports: utils/types (Submission, EmployeeFormData)
├── imports: utils/api (submissionApi, calculateAge)

FilterPanel.tsx
├── imports: react
├── imports: utils/types (FilterState)

ThreeDotMenu.tsx
├── imports: react
├── imports: lucide-react (MoreVertical, Eye, ArrowRight, X)

DocumentViewer.tsx
├── imports: react
├── imports: lucide-react (X)
├── imports: utils/types (DocumentViewerProps)

FileUpload.tsx
├── imports: react
├── imports: lucide-react (Upload, Eye, Trash2)

utils/api.ts
├── imports: axios
├── imports: utils/types (Submission)
├── exports: apiClient, submissionApi, helpers

utils/types.ts
├── exports: interfaces (Submission, EmployeeFormData, etc.)
```

## Key Interactions

### 1. Click "Proceed" on Employee
```
EmployeeList → ThreeDotMenu.onProceed
  → handleProceed(id)
  → navigate(`/employee/${id}/form`)
  → EmployeeForm mounts with id
```

### 2. Apply Filters
```
FilterPanel → onFilterChange(filters)
  → EmployeeList.setFilters
  → onClick Apply → applyFilters()
  → setFilteredSubmissions
  → Table re-renders
```

### 3. Upload and View Document
```
FileUpload → user selects file
  → onChange(file)
  → EmployeeForm.handleInputChange
  → formData updates
  → onClick View → onView()
  → handleViewDocument
  → DocumentViewer opens
```

### 4. Step Through Form
```
EmployeeForm → onClick Proceed
  → handleProceed()
  → if step < 3: setCurrentStep(step + 1)
  → if step === 3: handleSubmit() → API call
```

---

**Visual Component Map Complete**

This document shows the complete component architecture, data flow, and interactions in the Metro HRMS POC application.

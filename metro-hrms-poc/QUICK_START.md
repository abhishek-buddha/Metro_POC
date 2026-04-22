# Quick Start Guide - Metro HRMS POC

## Getting Started in 3 Steps

### 1. Start the Backend Server

Make sure your backend server is running on port 8000:

```bash
cd C:\Users\Rakes\Desktop\Metro_POC
# Run your backend server (Python/FastAPI)
python backend/main.py
# or
python -m uvicorn backend.main:app --reload --port 8000
```

The backend should be accessible at: `http://localhost:8000`

### 2. Start the Frontend Development Server

```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run dev
```

The frontend will start at: `http://localhost:5173`

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## What You'll See

### Home Page - Employee List
- **Left Sidebar**: Navigation icons
- **Top Header**: Metro logo, search bar, notifications, user profile
- **Tabs**: Employee, Onboarding (active), Probation, etc.
- **Filter Panel** (Left):
  - Submission Status dropdown
  - Submission Level dropdown
  - Apply button
- **Employee Table**:
  - Employee names with purple circular avatars
  - Temp IDs and Employee IDs
  - Entity names
  - Orange "In Progress" status badges
  - Submission levels (Basic Info, Payroll, etc.)
  - Three-dot menu with actions

### Employee Form Page
- **Multi-Step Stepper**: Personal Details → Company Structure & Policies → Payroll
- **Step 1 - Personal Details**:
  - Personal information fields (auto-populated from WhatsApp data)
  - Financial details with document uploads (Aadhaar, PAN)
  - Bank details with cancelled cheque upload
  - Other details (Resume, Educational docs, Profile photo, NAPS letter)

## Key Features to Test

### 1. View Employee List
- The list automatically loads all submissions from the backend
- Each employee has a circular avatar with initials
- Status badges show submission progress

### 2. Filter Employees
- Use the filter panel on the left
- Select submission status (Pending, In Progress, Completed, Rejected)
- Select submission level (Basic Info, Payroll, Completed)
- Click "Apply" to filter

### 3. Employee Actions
- Click the three-dot menu on any employee row
- Options:
  - **View Details**: Opens the employee form
  - **Proceed**: Navigates to the employee form
  - **Cancel**: Confirms cancellation

### 4. Fill Employee Form
- Click "Proceed" on any employee
- Form auto-populates with data from backend
- Navigate through 3 steps using "Proceed" and "Back" buttons
- Upload documents or view existing ones
- Age auto-calculates from Date of Birth
- Submit completed form

### 5. View Documents
- Click the eye icon on any document upload
- Modal opens with document viewer
- For Aadhaar: Password protection dialog appears
- Enter password to unlock and view
- Click "Close" to exit viewer

## API Integration

The application connects to these endpoints:

```
GET  /api/submissions          → Fetch all employees
GET  /api/submissions/:id      → Get single employee details
POST /api/submissions/:id/finalize → Submit employee form
```

All requests include the API key header:
```
X-API-Key: metro-kyc-secure-key-2026
```

## Data Flow

1. **Page Load** → Fetches all submissions from backend
2. **Backend Returns** → Submissions with status "APPROVED"
3. **Frontend Displays** → Shows as "In Progress" (orange badge)
4. **Click Proceed** → Navigate to form with pre-populated data
5. **Submit Form** → Sends finalized data to backend

## Design Specifications Implemented

### Colors
- Primary: #6366F1 (Indigo-600) - Buttons, active tabs, badges
- Orange: #FB923C - "In Progress" status
- Gray: #F9FAFB - Background
- White: #FFFFFF - Cards and surfaces

### Typography
- Font: System font stack (San Francisco, Segoe UI, etc.)
- Sizes: 12px-24px
- Weights: Normal (400), Medium (500), Semibold (600), Bold (700)

### Spacing
- Sidebar: 60px width
- Content padding: 24px (1.5rem)
- Card spacing: 16px-24px gaps
- Form fields: 24px gap

### Components
- Circular avatars with initials
- Rounded buttons (border-radius: 8px)
- Status badges (rounded-full)
- Cards with subtle borders
- Dropdown menus with shadows

## Common Tasks

### Add a New Employee
Currently, this navigates to a form. Future implementation will create a new record.

### Edit Employee Information
Click "Proceed" or "View Details" from the three-dot menu.

### Filter by Status
Use the filter panel to show only employees with specific status.

### View Documents
Click the eye icon on uploaded documents to view in modal.

### Submit Employee Form
Complete all three steps and click "Submit" on the final step.

## Troubleshooting

### Can't See Employees?
- Check backend is running on port 8000
- Verify API key matches in `.env` and backend
- Check browser console for errors
- Ensure database has submissions with status "APPROVED"

### Form Not Loading?
- Check employee ID exists in backend
- Verify `/api/submissions/:id` endpoint works
- Check browser console for 404 or 500 errors

### Documents Not Showing?
- Verify document URLs in backend responses
- Check file paths are accessible
- Ensure CORS is enabled on backend

### Styling Issues?
- Clear browser cache
- Check Tailwind CSS is loading
- Verify no CSS conflicts

## Next Steps

1. Test with real backend data
2. Upload actual documents
3. Complete Step 2 and Step 3 form fields
4. Add form validation
5. Implement real file upload to backend
6. Test mobile responsiveness

## Support

For questions or issues, check:
- README.md for full documentation
- Browser console for error messages
- Backend logs for API issues
- Network tab for request/response details

---

Happy Testing!

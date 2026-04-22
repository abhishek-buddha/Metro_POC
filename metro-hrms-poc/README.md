# Metro HRMS POC - React/TypeScript Application

A complete Human Resource Management System Proof of Concept built with React, TypeScript, Vite, and Tailwind CSS. This application replicates the design specifications from the PDD document for managing employee onboarding and information.

## Features

### Employee List Management
- **Filter Panel**: Filter employees by submission status and submission level
- **Employee Table**: Display all employees with their details
- **Status Badges**: Visual status indicators (In Progress, Completed, etc.)
- **Action Menu**: Three-dot menu for View Details, Proceed, and Cancel actions
- **Pagination**: Navigate through employee records

### Multi-Step Employee Form
- **Step 1: Personal Details**
  - Basic information (name, DOB, gender, contact)
  - Financial details (Aadhaar, PAN)
  - Bank details (account number, IFSC, cheque)
  - Other details (resume, educational documents, photos)

- **Step 2: Company Structure & Policies**
- **Step 3: Payroll**

### Document Management
- **Document Viewer**: Modal viewer for PDFs and images
- **Password Protection**: Support for password-protected documents
- **File Upload**: Drag-and-drop file upload with preview

## Technology Stack

- **React 19.2.5**: UI library
- **TypeScript 6.0.2**: Type-safe JavaScript
- **Vite 8.0.9**: Fast build tool and dev server
- **Tailwind CSS 3.4.19**: Utility-first CSS framework
- **React Router DOM 7.14.2**: Client-side routing
- **Axios 1.15.1**: HTTP client for API requests
- **Lucide React 1.8.0**: Icon library

## Project Structure

```
metro-hrms-poc/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── DocumentViewer.tsx
│   │   ├── FileUpload.tsx
│   │   ├── FilterPanel.tsx
│   │   └── ThreeDotMenu.tsx
│   ├── layouts/            # Layout components
│   │   └── MainLayout.tsx
│   ├── pages/              # Page components
│   │   ├── EmployeeList.tsx
│   │   └── EmployeeForm.tsx
│   ├── utils/              # Utilities and helpers
│   │   ├── api.ts          # API service layer
│   │   └── types.ts        # TypeScript type definitions
│   ├── App.tsx             # Main app component with routing
│   ├── App.css             # App styles
│   ├── index.css           # Global styles with Tailwind
│   └── main.tsx            # App entry point
├── .env                    # Environment variables
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Setup and Installation

### Prerequisites
- Node.js (v18 or higher)
- npm or yarn package manager

### Installation Steps

1. Navigate to the project directory:
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
```

2. Install dependencies (already done):
```bash
npm install
```

3. Environment configuration:
The `.env` file is already configured with:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_KEY=metro-kyc-secure-key-2026
```

4. Start the development server:
```bash
npm run dev
```

5. Open your browser and navigate to:
```
http://localhost:5173
```

## Backend API Integration

The application connects to a backend API running on `http://localhost:8000`. Make sure the backend server is running before starting the frontend.

### API Endpoints Used

- `GET /api/submissions` - Fetch all employee submissions
- `GET /api/submissions/:id` - Get single employee submission
- `POST /api/submissions/:id/finalize` - Submit finalized employee form

### API Authentication

All API requests include the API key in headers:
```
X-API-Key: metro-kyc-secure-key-2026
```

## Design Specifications

### Color Palette
- **Primary Color**: #6366F1 (Indigo-600)
- **Status Badges**:
  - Orange (#FB923C) for "In Progress"
  - Green for "Completed"
  - Red for "Rejected"
- **Background**: #F9FAFB (Light Gray)
- **Text**: Gray-900, Gray-700, Gray-600

### Typography
- System font stack with fallback to sans-serif
- Font weights: Medium (500), Semibold (600), Bold (700)

### Layout
- **Sidebar**: 60px width with icon navigation
- **Header**: Full-width with search and user info
- **Content Area**: Responsive with proper spacing

## Available Scripts

### Development
```bash
npm run dev
```
Starts the development server with hot module replacement.

### Build
```bash
npm run build
```
Creates an optimized production build in the `dist` folder.

### Preview
```bash
npm run preview
```
Preview the production build locally.

### Lint
```bash
npm run lint
```
Run ESLint to check code quality.

## Component Documentation

### MainLayout
Provides the application layout with sidebar navigation and header.

### EmployeeList
Displays the list of employees with filtering and actions.
- Uses FilterPanel for filtering
- Uses ThreeDotMenu for row actions
- Integrates with API to fetch submissions

### EmployeeForm
Multi-step form for employee onboarding.
- Three-step wizard interface
- Auto-populated from backend data
- File upload support
- Document viewing capability

### DocumentViewer
Modal component for viewing documents.
- Supports PDF and image files
- Password protection for sensitive documents
- Full-screen viewing

### FileUpload
Reusable file upload component.
- File type validation
- Size limits
- Preview and delete functionality

### FilterPanel
Sidebar filter component.
- Submission status filter
- Submission level filter
- Apply button to trigger filtering

### ThreeDotMenu
Dropdown menu for row actions.
- View Details
- Proceed
- Cancel

## Data Flow

1. **Employee List**: Fetches submissions from API on mount
2. **Filtering**: Client-side filtering based on selected criteria
3. **Navigation**: Click "Proceed" or "View Details" to navigate to form
4. **Form Loading**: Fetches submission details and pre-populates form
5. **Form Submission**: Sends finalized data to API endpoint

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Development Notes

### Hot Module Replacement (HMR)
Vite provides fast HMR for instant feedback during development.

### Type Safety
All components are fully typed with TypeScript for better developer experience and fewer runtime errors.

### Responsive Design
The application is responsive and works on various screen sizes, though optimized for desktop use.

## Troubleshooting

### Backend Connection Issues
If you see API errors:
1. Verify backend server is running on port 8000
2. Check `.env` file has correct API base URL
3. Ensure API key matches backend configuration

### Build Errors
If you encounter build errors:
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Clear Vite cache: `rm -rf node_modules/.vite`

### Port Already in Use
If port 5173 is already in use:
1. Kill the process using the port
2. Or modify `vite.config.ts` to use a different port

## Future Enhancements

- [ ] Add Step 2 (Company Structure & Policies) form fields
- [ ] Add Step 3 (Payroll) form fields
- [ ] Implement real file upload to backend
- [ ] Add form validation with error messages
- [ ] Implement sorting in employee table
- [ ] Add export functionality (Excel, PDF)
- [ ] Implement real-time updates with WebSockets
- [ ] Add user authentication and authorization
- [ ] Implement role-based access control
- [ ] Add audit trail for form changes

## License

This is a Proof of Concept (POC) application for Metro HRMS.

## Support

For issues or questions, please contact the development team.

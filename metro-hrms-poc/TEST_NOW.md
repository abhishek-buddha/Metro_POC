# Test Now - Quick Reference Card

## Start the Application

### Option 1: Dev Mode (Recommended)
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run dev
```

### Option 2: Use Existing Build
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run preview
```

## Open Browser
```
http://localhost:5174
```

---

## What You'll See

### Employee List Screen
```
┌────────────────────────────────────────────────────────────┐
│  [m]  metro  BRANDS        [Search...]        [SR] User    │
├────────────────────────────────────────────────────────────┤
│  Add Employees List                                         │
│                                                              │
│  Employee | Onboarding | Probation | Access Mgmt | ...     │
│           └────────────┘ (purple underline)                 │
│                                                              │
│  Add Employees | Bulk Uploads | Requests                   │
│  └─────────────┘ (purple underline)                        │
├──────────┬─────────────────────────────────────────────────┤
│ Filters  │  Add Employees List              [+ Add New]    │
│  Reset   │                                                  │
│          │  EMPLOYEE NAME  TEMP ID   STATUS     ACTIONS    │
│ Status   │  [M]            TEMP9063  Completed     ⋮       │
│ ▼ All    │  MANDADI...                (green)              │
│          │                                                  │
│ Level    │                                                  │
│ ▼ All    │                                                  │
│          │                                                  │
│ [Apply]  │                                                  │
└──────────┴─────────────────────────────────────────────────┘
```

### Click Three Dots (⋮)
```
┌──────────────┐
│ 👁 View Details │
│ → Proceed    │ ← CLICK THIS
│ ✕ Cancel     │
└──────────────┘
```

### Employee Form Opens
```
┌────────────────────────────────────────────────────────────┐
│  Employee Form                                              │
│  TEMP9063555464 | MANDADI SAMPATH REDDY                    │
│                                                              │
│  ℹ️ Employee's information will become active next the date │
│     of onboarding                                           │
│                                                              │
│  ① Personal Details ──── ② Company ──── ③ Payroll         │
│  (purple • active)      (gray)         (gray)              │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Personal Details                                      │  │
│  │                                                       │  │
│  │ First Name*          Full Name*                      │  │
│  │ [MANDADI SAMPATH]    [BOPPISETTI RAKESH]            │  │
│  │                                                       │  │
│  │ DOB*                 Gender*                         │  │
│  │ [09/11/1995]         [Male ▼]                       │  │
│  │                                                       │  │
│  │ ... more fields ...                                  │  │
│  │                                                       │  │
│  │                       [Cancel] [Proceed]             │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

---

## Visual Checklist

Look for these PDD design elements:

### Employee List
- [ ] Purple "m" logo in sidebar (square with white letter)
- [ ] "metro BRANDS" header
- [ ] Active tab has purple text + 2px bottom border
- [ ] Filter panel shows "Filters" header with "Reset" link
- [ ] Blue "Apply" button in filter panel
- [ ] Employee avatars are 40px circles (purple with white initials)
- [ ] "Completed" badge is green
- [ ] Three-dot menu (⋮) on right side
- [ ] "+ Add New" button is purple

### Employee Form
- [ ] Light blue info banner with info icon
- [ ] Stepper shows: ① ──── ② ──── ③
- [ ] Active step is purple
- [ ] Input fields are 40px tall
- [ ] All fields have data (auto-populated)
- [ ] Age shows "X year(s) X month(s) X day(s)"
- [ ] "Proceed" button is purple with shadow
- [ ] Form has white background with shadow

---

## Interaction Test

### Test 1: Navigation
1. Open http://localhost:5174
2. See employee list
3. Click three dots (⋮)
4. Click "Proceed"
5. **Expected:** Form opens, no 404 error

### Test 2: Data Display
1. Form opens
2. Check First Name: Should show "MANDADI SAMPATH REDDY"
3. Check Full Name: Should show "BOPPISETTI RAKESH"
4. Check Phone: Should show "+919063555464"
5. Check Father Name: Should show "RAJESWAR RAO BOPPISETTI"
6. Check DOB: Should show "09/11/1995"
7. Check Age: Should auto-calculate
8. **Expected:** All fields populated

### Test 3: Filter
1. Go back to employee list
2. Click "Submission Status" dropdown
3. Select "Completed"
4. Click "Apply"
5. **Expected:** Table filters to show only completed submissions
6. Click "Reset" in filter panel
7. **Expected:** Filter clears

### Test 4: Form Steps
1. Open employee form
2. Current step is ① (purple)
3. Click "Proceed"
4. **Expected:** Move to step ② (Company Structure)
5. Click "Back"
6. **Expected:** Return to step ①

---

## Expected vs Actual

### If Everything Works
```
✅ Employee list loads instantly
✅ Data displays correctly
✅ No console errors
✅ Navigation works smoothly
✅ Form auto-populates
✅ UI matches PDD exactly
```

### If You See Issues

#### Issue: "Failed to fetch submissions"
```bash
# Check backend is running
curl http://localhost:8000/health

# Should return: {"status":"healthy"}
```

#### Issue: Empty table
```bash
# Check database
sqlite3 C:\Users\Rakes\Desktop\Metro_POC\metro_kyc.db
SELECT id, status FROM kyc_submissions;
```

#### Issue: 404 on form
```
Check browser console (F12)
Look for navigation URL
Should be: /employee/aacc95cb-d37a-4d55-89c9-addf5741ddda/form
```

---

## Browser Console

Open Developer Tools (F12) → Console tab

### Expected Output (Clean)
```
No errors
No warnings
Just normal React dev messages
```

### If You See Errors
```javascript
// BEFORE fix: Would see
"GET /api/submissions/123 404"
"Type error: id.toString is not a function"

// AFTER fix: Should see nothing
✅ Clean console
```

---

## Network Tab Check

Open Developer Tools (F12) → Network tab

### Expected Requests
```
GET /api/submissions
Status: 200 OK
Response: { submissions: [...] }

GET /api/submissions/aacc95cb-d37a-4d55-89c9-addf5741ddda
Status: 200 OK
Response: { id: "aacc...", pan_name: "...", ... }
```

### Check Headers
```
Request Headers:
  X-API-Key: metro-kyc-secure-key-2026 ✅

Response:
  Content-Type: application/json ✅
  Status: 200 ✅
```

---

## Visual Comparison

### Colors to Verify

**Purple (Primary):**
- Logo background: `#6366F1`
- Active tab text: `#6366F1`
- Avatar background: `#6366F1`
- Buttons: `#6366F1`

**Orange (In Progress):**
- Badge background: Light orange
- Badge text: `#FB923C`

**Blue (Info & Actions):**
- Info banner: Light blue (#EFF6FF)
- Apply button: Blue (#2563EB)

**Green (Completed):**
- Badge: Light green background
- Checkmark in stepper: Green

**Grays:**
- Background: #F9FAFB
- Text: #111827 (dark) to #6B7280 (muted)
- Borders: #E5E7EB

---

## Performance Check

### Load Times (Expected)
```
Initial load: < 1 second
Navigation: Instant
API calls: < 200ms
```

### Bundle Size
```
CSS: 14.82 kB (gzipped: 3.73 kB)
JS:  312.73 kB (gzipped: 97.78 kB)
```

---

## Success Criteria

All of these should be TRUE:

- [ ] Application starts without errors
- [ ] Employee list displays
- [ ] Table shows at least one employee
- [ ] Employee has purple avatar (40px)
- [ ] Status badge shows correct color
- [ ] Click three dots shows menu
- [ ] Click "Proceed" navigates to form
- [ ] Form shows info banner (blue)
- [ ] All form fields are populated
- [ ] Age is auto-calculated
- [ ] Stepper shows 3 steps
- [ ] Active step is purple
- [ ] "Proceed" button works
- [ ] No 404 errors in console
- [ ] UI matches PDD screenshots

---

## Quick Commands

### Rebuild if needed
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run build
```

### Check for errors
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run lint
```

### Test API directly
```bash
curl -H "X-API-Key: metro-kyc-secure-key-2026" http://localhost:8000/api/submissions
```

---

## Report Results

After testing, check:

1. **Visual Match:** Does UI match PDD? ___/10
2. **Functionality:** Does everything work? ___/10
3. **Performance:** Is it fast? ___/10
4. **Data:** Is data displaying? ___/10
5. **Navigation:** No errors? ___/10

**Total Score:** ___/50

If score < 45, report issues.
If score >= 45, **POC is production-ready!**

---

## Emergency Fixes

### If frontend won't start
```bash
rm -rf node_modules
npm install
npm run dev
```

### If backend is down
```bash
cd C:\Users\Rakes\Desktop\Metro_POC
python src/app.py
```

### If database is corrupt
```bash
# Check data
sqlite3 metro_kyc.db ".tables"

# Backup first
cp metro_kyc.db metro_kyc.db.backup
```

---

## You're Ready!

**Just run:**
```bash
cd C:\Users\Rakes\Desktop\Metro_POC\metro-hrms-poc
npm run dev
```

**Then open:**
```
http://localhost:5174
```

**And test the checklist above!**

All fixes have been applied. The POC should work perfectly and match the PDD design exactly.

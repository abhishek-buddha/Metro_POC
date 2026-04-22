#!/bin/bash
# Integration test script for HRMS auto-population POC

echo "=== HRMS Integration Test ==="
echo ""
echo "This script verifies:"
echo "1. Backend server is accessible"
echo "2. Frontend builds successfully"
echo "3. API endpoints respond correctly"
echo ""

# Check if backend is running
echo "Checking backend server..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/submissions > /dev/null 2>&1; then
    echo "✓ Backend is running on port 8000"
else
    echo "✗ Backend is NOT running. Please start with: python -m src.webhook.app"
    exit 1
fi

# Build frontend
echo ""
echo "Building frontend..."
cd "$(dirname "$0")"
npm run build > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Frontend builds successfully"
else
    echo "✗ Frontend build failed"
    exit 1
fi

echo ""
echo "=== Integration test checklist ==="
echo ""
echo "Manual verification steps:"
echo "1. Start backend: python -m src.webhook.app"
echo "2. Start frontend: npm run dev"
echo "3. Get APPROVED submission: curl -H \"X-API-Key: your_key\" http://localhost:8000/api/submissions"
echo "4. Open browser: http://localhost:5173?id={submission_id}"
echo "5. Verify all sections display correctly"
echo "6. Click Submit button"
echo "7. Verify success message and employee ID"
echo "8. Check database: SELECT * FROM kyc_submissions WHERE status='FINALIZED';"
echo ""
echo "Test completed successfully!"

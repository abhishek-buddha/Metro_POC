# Real-Time Testing Guide
## Watch Submissions as They Happen

---

## 🎯 Your Testing Scenario

**You:** Submit documents via WhatsApp
**Developer:** Sees data appear instantly in their terminal/browser

---

## ⚡ Best Method: Live Watcher Script (Recommended)

### **Setup for Developer:**

**1. Get the script:**
```bash
# Send them this file:
watch_submissions.py

# Or share entire project folder
```

**2. Install dependency:**
```bash
pip install requests
```

**3. Run the watcher:**
```bash
python watch_submissions.py
```

**4. Output:**
```
🔍 KYC Submission Watcher
📡 Connected to: http://192.168.1.49:8000
⏱️  Polling every 2 seconds
🛑 Press Ctrl+C to stop

👁️  Watching... (0 total submissions)
```

### **Testing Flow:**

```
Timeline:
--------
[You send Aadhaar to WhatsApp]
   ↓
[5 seconds later...]
   ↓
[Developer's terminal shows:]

🆕 NEW SUBMISSION DETECTED!
======================================================================
📋 Submission ID: 0ccc95a5...
📱 Phone: +919063555464
⏰ Submitted: 2026-04-17T10:03:36
📊 Status: PENDING
🎯 Confidence: 0.9
======================================================================

📄 Extracted Data:

  🆔 AADHAAR CARD:
     Name: Boppisetti Rakesh
     Last 4: 8182
     DOB: 09/11/1995
     Gender: Male
     Confidence: 0.9

👁️  Watching... (1 total submissions)
```

---

## 🌐 Alternative: Use Browser/Postman

### **Option A: Browser (Simple)**

**Developer opens in browser:**
```
http://192.168.1.49:8000/api/submissions
```

**Credentials popup (if appears):**
- Click "Cancel" or close it
- Browser will show error page
- That's expected! Use Option B instead

### **Option B: Postman (Better for Browser)**

**1. Install Postman:**
https://www.postman.com/downloads/

**2. Import collection:**
- File → Import → Select `KYC_API_Postman_Collection.json`

**3. Set base URL:**
- Click on collection → Variables
- Set `base_url` = `http://192.168.1.49:8000`

**4. Test endpoint:**
- Open "List All Submissions" request
- Click **Send**
- See results in response panel

**5. Refresh after each submission:**
- Just click **Send** again to see new data

---

## 🔄 Alternative: Manual curl Commands

**Developer runs this after each submission:**

```bash
# View all submissions
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://192.168.1.49:8000/api/submissions | jq

# Get specific submission details
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://192.168.1.49:8000/api/submissions/SUBMISSION_ID | jq
```

**Note:** Install `jq` for pretty JSON:
- Windows: `choco install jq` or download from https://jqlang.github.io/jq/
- Mac: `brew install jq`
- Linux: `sudo apt install jq`

---

## 📊 What Developer Will See

### **After Aadhaar Submission:**
```json
{
  "submissions": [
    {
      "id": "abc-123",
      "phone_number": "+919063555464",
      "aadhaar_name": "Boppisetti Rakesh",
      "aadhaar_last4": "8182",
      "pan_name": null,
      "bank_holder_name": null,
      "status": "PENDING",
      "overall_confidence": 0.9
    }
  ]
}
```

### **After PAN Submission (Same Submission ID!):**
```json
{
  "submissions": [
    {
      "id": "abc-123",  // SAME ID
      "phone_number": "+919063555464",
      "aadhaar_name": "Boppisetti Rakesh",
      "aadhaar_last4": "8182",
      "pan_name": "Boppisetti Rakesh",  // NEW!
      "bank_holder_name": null,
      "status": "PENDING",
      "overall_confidence": 0.9
    }
  ]
}
```

**Key Point:** Same submission ID gets UPDATED with each new document!

---

## ✅ Testing Checklist

**Before starting:**
- [ ] Your machine is running (webhook + worker)
- [ ] Both on same network (WiFi/LAN)
- [ ] Developer has API URL: `http://192.168.1.49:8000`
- [ ] Developer has API Key: `metro-kyc-secure-key-2026`

**Test 1: Connection**
- [ ] Developer tests: `curl http://192.168.1.49:8000/health`
- [ ] Should return: `{"status":"healthy",...}`

**Test 2: View Empty State**
- [ ] Developer checks submissions (should see 0 or existing ones)

**Test 3: Submit Aadhaar**
- [ ] You send Aadhaar photo to WhatsApp
- [ ] Developer refreshes/runs command
- [ ] Should see new submission with Aadhaar data

**Test 4: Submit PAN**
- [ ] You send PAN photo to WhatsApp
- [ ] Developer refreshes/runs command
- [ ] Should see SAME submission now has PAN data too

**Test 5: Submit Bank Doc**
- [ ] You send bank document to WhatsApp
- [ ] Developer refreshes/runs command
- [ ] Should see SAME submission now has all 3 documents

---

## 🔧 Troubleshooting

### "Connection refused" or "Can't connect"

**Check:**
```bash
# Test from your own machine first
curl http://192.168.1.49:8000/health

# If that works, problem is network/firewall
```

**Solutions:**
1. Check Windows Firewall (allow port 8000)
2. Same WiFi network?
3. Try with your computer's name instead of IP

### "No new data appearing"

**Check:**
```bash
# View worker logs (on your machine)
# Look for "Job processed successfully"

# Check if job was created
redis-cli LLEN kyc:jobs
```

### "Unauthorized" or 401 error

**Check:**
- API Key is correct: `metro-kyc-secure-key-2026`
- Header name is correct: `X-API-Key`

---

## 🎭 Demo Script

**Use this for testing:**

```
You (via WhatsApp):
  "Let me send test documents now"

Developer (runs watcher):
  python watch_submissions.py
  "Ready! Watching..."

You:
  [Send Aadhaar photo]

Developer:
  "🆕 NEW SUBMISSION DETECTED! I see Aadhaar data!"

You:
  [Send PAN photo]

Developer:
  "Updated! Now I see PAN data in same submission!"

You:
  [Send Bank document]

Developer:
  "Perfect! All 3 documents in one submission!"
```

---

## 📝 Summary

**For Real-Time Testing:**

| Method | Effort | Real-time | Best For |
|--------|--------|-----------|----------|
| **watch_submissions.py** | Low | Yes ✅ | Continuous monitoring |
| **Postman** | Medium | Manual refresh | Interactive testing |
| **curl + jq** | Low | Manual refresh | Command line users |
| **File Sharing** | High | Manual F5 | Direct DB access |

**Recommendation:** Use `watch_submissions.py` - it's the simplest!

---

**Ready to test?** Start the watcher and send a WhatsApp message!

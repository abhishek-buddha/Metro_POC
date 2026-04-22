# 📦 What to Share with Other Developers

---

## 🎯 Quick Answer

**SQLite has NO credentials!** Just share files.

---

## 📁 Package to Share

Create a folder with these files and send to your developer:

```
KYC_Dev_Package/
├── kyc.db                              ← Database file (copy from data/)
├── KYC_API_Postman_Collection.json     ← In docs/ folder
├── DEV_SETUP_GUIDE.md                  ← In docs/ folder
└── .env.example                        ← Project root
```

---

## 📋 Step-by-Step Instructions

### **Step 1: Prepare the Package**

```bash
# Create a folder
mkdir KYC_Dev_Package

# Copy database file
copy data\kyc.db KYC_Dev_Package\

# Copy developer docs
copy docs\KYC_API_Postman_Collection.json KYC_Dev_Package\
copy docs\DEV_SETUP_GUIDE.md KYC_Dev_Package\
copy .env.example KYC_Dev_Package\

# Zip it
# Right-click folder → Send to → Compressed (zipped) folder
```

### **Step 2: Share the Zip File**

Send `KYC_Dev_Package.zip` via:
- Email
- Slack/Teams
- Google Drive/Dropbox
- USB drive

---

## 💬 What to Tell the Developer

**Copy-paste this message:**

```
Hi [Developer Name],

I'm sharing the KYC system database access with you. Attached is a zip file with everything you need.

WHAT'S INCLUDED:
- kyc.db - Database file (SQLite, no credentials needed)
- KYC_API_Postman_Collection.json - API testing collection
- DEV_SETUP_GUIDE.md - Setup instructions
- .env.example - Environment variables template

TWO WAYS TO ACCESS DATA:

Option A - Local Database (Recommended):
1. Extract the zip file
2. Install DB Browser: https://sqlitebrowser.org/dl/
3. Open kyc.db in DB Browser
4. Browse tables and run queries
5. No credentials needed!

Option B - Remote API (Real-time data):
1. Install Postman: https://www.postman.com/downloads/
2. Import KYC_API_Postman_Collection.json
3. Set base_url to: http://192.168.1.XXX:8000 (I'll give you my IP)
4. API Key: metro-kyc-secure-key-2026

Read DEV_SETUP_GUIDE.md for detailed instructions.

Let me know if you have questions!
```

---

## 🌐 If They Need API Access

**Find your IP address:**

```bash
# Windows
ipconfig

# Look for "IPv4 Address" like: 192.168.1.100
```

**Tell them:**
```
API Base URL: http://192.168.1.100:8000
API Key: metro-kyc-secure-key-2026

Test it:
curl -H "X-API-Key: metro-kyc-secure-key-2026" http://192.168.1.100:8000/health
```

**Requirements for API access:**
- Your machine must be running (webhook + worker)
- Same network OR use ngrok/localtunnel
- Ports 8000 must be open

---

## 🔐 Security Checklist

Before sharing, verify:

- [ ] Removed real API keys from files (they should use .env.example)
- [ ] Database contains test data only (or trusted team member)
- [ ] Shared via secure channel (not public link)
- [ ] Told them to delete after testing

---

## ❓ FAQ

**Q: Do they need credentials to open kyc.db?**
A: No! SQLite files have no authentication. Anyone with the file can open it.

**Q: Can multiple people work on the same database?**
A: No, SQLite doesn't support concurrent writers. Each person gets their own copy.

**Q: How do they get updated data?**
A: Either:
  - You send them a fresh copy of kyc.db
  - They use the API for real-time access

**Q: Can they break my database?**
A: No, they have a copy. Even if they delete everything, your original is safe.

**Q: Do I need to set up user accounts?**
A: No, SQLite has no user system. For production with access control, use PostgreSQL.

---

## 🚀 Optional: Share Entire Project

If they want to run the system locally:

```bash
# Option 1: Git (if you have repo)
git clone [your-repo-url]
cd Metro_POC
pip install -r requirements.txt

# Option 2: Zip entire project
# Zip the whole Metro_POC folder and send it
```

**They'll need:**
- Python 3.11+
- Redis (via Docker)
- OpenAI API key (their own)
- Twilio account (for WhatsApp)

---

## 📊 Summary

**SQLite Access = Just Share the File**

| What | How |
|------|-----|
| **Credentials** | None needed |
| **Connection string** | `sqlite:///data/kyc.db` |
| **Authentication** | None |
| **Network** | Not required (it's a file) |
| **Tools** | DB Browser (free) |
| **Security** | File-level (OS permissions) |

**That's it!** No server setup, no passwords, no ports - just a file.

---

**Questions?** Read docs/DEV_SETUP_GUIDE.md or ask me.

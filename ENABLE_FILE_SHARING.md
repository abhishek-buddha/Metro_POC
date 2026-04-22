# Enable File Sharing for Real-Time Database Testing

---

## 🎯 Goal
Let another developer access your SQLite database in real-time over the network.

---

## 🔧 Setup Windows File Sharing (5 minutes)

### **Step 1: Enable File Sharing**

1. Open **File Explorer**
2. Navigate to: `C:\Users\Rakes\Desktop\Metro_POC`
3. Right-click on `Metro_POC` folder
4. Select **Properties**
5. Go to **Sharing** tab
6. Click **Share...**
7. In the dropdown, select **Everyone** (or specific user)
8. Click **Add**
9. Set Permission Level to **Read/Write**
10. Click **Share**
11. Copy the network path (e.g., `\\DESKTOP-ABC123\Metro_POC`)
12. Click **Done**

---

### **Step 2: Get Network Path**

The network path will look like:
```
\\192.168.1.49\Metro_POC
```

Or:
```
\\DESKTOP-ABC123\Metro_POC
```

---

### **Step 3: Share Path with Developer**

Tell them to access:
```
\\192.168.1.49\Metro_POC\data\kyc.db
```

---

## 👨‍💻 Developer Instructions

### **Windows:**
1. Open **File Explorer**
2. In address bar, type: `\\192.168.1.49\Metro_POC`
3. Press Enter
4. Navigate to `data\kyc.db`
5. Open in DB Browser
6. After each submission, press **F5** or click **Refresh**

### **Mac:**
1. Open **Finder**
2. Press **Cmd+K**
3. Enter: `smb://192.168.1.49/Metro_POC`
4. Click **Connect**
5. Navigate to `data/kyc.db`
6. Open in DB Browser
7. After each submission, click **Refresh**

---

## ⚠️ Important Notes

**Both of you CANNOT open the database at the same time for writing!**

SQLite only supports one writer at a time. If both have it open:
- ✅ You can run the system (webhook writes to DB)
- ❌ Developer can only READ (must close DB Browser when you're running system)

**Solution:** Developer should:
1. Keep DB Browser CLOSED normally
2. After you submit something, they:
   - Open DB Browser
   - View the data
   - Close DB Browser
   - Repeat

---

## 🔒 Security

After testing, REMOVE the share:
1. Right-click folder → Properties → Sharing
2. Click **Advanced Sharing**
3. Uncheck **Share this folder**
4. Click **OK**

---

## ⚡ Better Alternative: Use API

Instead of file sharing, use API access (no file sharing setup needed):

```bash
# Developer runs this after each submission:
curl -H "X-API-Key: metro-kyc-secure-key-2026" \
     http://192.168.1.49:8000/api/submissions
```

Much simpler and safer!

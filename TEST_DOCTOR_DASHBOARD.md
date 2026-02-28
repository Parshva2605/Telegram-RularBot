# 🧪 Quick Test - Doctor Dashboard

## 🚀 Quick Start

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

Or run main app and navigate to "👨‍⚕️ Doctor Dashboard" page.

---

## 📱 Test Login

### Test Credentials:
```
Phone: +919876543210
Access Code: TEST1234
```

Or use your registered doctor from @MediMindDoctorBot.

---

## ✅ Test Flow

### 1. Login
```
1. Enter phone: +919876543210
2. Enter code: TEST1234
3. Click "🔓 Login"
4. Should see: "✅ Welcome Dr. Shah!"
```

### 2. View Queue
```
1. Go to "📋 Live Queue" tab
2. Should see pending X-ray requests
3. Click "✅ Mark Reviewed" on a request
4. Verify it updates
```

### 3. View Reports
```
1. Go to "📊 My Reports" tab
2. Search for patient name
3. Filter by status
4. Expand a report card
5. View all details
```

### 4. View Statistics
```
1. Go to "📈 Statistics" tab
2. See metrics: Total/Pending/Reviewed/Sent
3. View status distribution chart
4. View requests over time chart
```

### 5. Logout
```
1. Click "🚪 Logout" in sidebar
2. Should return to login page
```

---

## 📸 Screenshot Checklist

- [ ] Login page
- [ ] Dashboard with queue
- [ ] Mark reviewed action
- [ ] Reports tab with search
- [ ] Statistics with charts
- [ ] Sidebar profile

---

## 🎯 Expected Results

### After Login:
- Sidebar shows doctor profile
- Name, phone, PHC, MCI, rating, cases
- Three tabs visible

### Live Queue:
- Shows pending requests
- Patient details visible
- Mark reviewed button works
- Bulk actions available

### My Reports:
- Shows all reports
- Search works
- Filter works
- Cards expand/collapse

### Statistics:
- Metrics display correctly
- Charts render properly
- Data matches database

---

## 🐛 Common Issues

### No pending requests?
**Create test request:**
```
@MediMindRuralBot → X-Ray Check → Fill form → Select doctor
```

### Login fails?
**Check:**
1. Doctor registered in database
2. Phone format: +919876543210
3. Access code correct (8 chars)

### Dashboard not loading?
**Install dependencies:**
```bash
cd dashboard
pip install -r requirements.txt
```

---

## ✅ Success Criteria

- ✅ Login works with phone + code
- ✅ Dashboard loads after login
- ✅ Queue shows pending requests
- ✅ Can mark requests as reviewed
- ✅ Reports tab shows history
- ✅ Search and filter work
- ✅ Statistics display correctly
- ✅ Logout works

---

## 📝 After Testing

Say: **"DOCTOR DASHBOARD READY - Login + queue screenshot"**

Share:
1. Screenshot of login page
2. Screenshot of live queue
3. Screenshot of statistics

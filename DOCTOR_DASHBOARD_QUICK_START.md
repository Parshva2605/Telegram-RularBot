# 🚀 Doctor Dashboard - Quick Start Card

## ⚡ 3 COMMANDS TO START

```bash
# 1. Verify credentials
python verify_and_create_test_doctor.py

# 2. Start dashboard
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py

# 3. Login with
Phone: +919876543210
Code: TEST1234
```

---

## 🔑 LOGIN CREDENTIALS

### Option 1 (Recommended)
```
Phone: +919876543210
Code: TEST1234
Name: Dr. Shah
```

### Option 2 (Test Account)
```
Phone: +919999999999
Code: TEST1234
Name: Dr. Test Kumar
```

---

## 📋 WHAT YOU'LL SEE

### Sidebar
- 👨‍⚕️ Doctor name
- 📱 Phone number
- 🏥 PHC name
- ⭐ Rating
- 📊 Total cases

### Tab 1: Live Queue
- Pending X-ray requests
- Mark as reviewed
- Cancel requests
- Bulk actions

### Tab 2: My Reports
- Search patients
- Filter by status
- View detailed reports
- Download PDFs

### Tab 3: Statistics
- Total cases
- Status counts
- Distribution chart
- Timeline chart

---

## 🐛 TROUBLESHOOTING

### Can't login?
```bash
python verify_and_create_test_doctor.py
```
Use the credentials it shows.

### Dashboard won't start?
```bash
pip install streamlit
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

### No data showing?
Run patient bot to submit test request:
```bash
python bot.py
```

---

## 📚 DETAILED GUIDES

- `START_DOCTOR_DASHBOARD.md` - Complete workflow
- `DASHBOARD_LOGIN_TEST.md` - Testing guide
- `database/insert_test_doctor.sql` - SQL to create test doctor
- `verify_and_create_test_doctor.py` - Verification script

---

## ✅ SUCCESS = 3 TABS WORKING

1. ✅ Live Queue loads
2. ✅ My Reports loads
3. ✅ Statistics loads

---

**That's it! Start testing now.** 🎉

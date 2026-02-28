# 🔐 Doctor Dashboard Login - Quick Test Guide

## ✅ WORKING CREDENTIALS (Already in Database!)

Use these credentials to login immediately:

```
Phone: +919876543210
Access Code: TEST1234
```

This doctor (Dr. Shah) already exists in your Supabase database!

---

## 🚀 Quick Start (3 Steps)

### Step 1: Start the Dashboard

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

### Step 2: Login

When the page opens:
- Enter Phone: `+919876543210`
- Enter Access Code: `TEST1234`
- Click "🔓 Login"

### Step 3: Verify Dashboard Works

You should see:
- ✅ Welcome message with doctor name
- 📋 Live Queue tab (shows pending X-ray requests)
- 📊 My Reports tab (shows all reports)
- 📈 Statistics tab (shows metrics)

---

## 🧪 Verify Database First (Optional)

If you want to verify the credentials exist before testing:

```bash
python test_doctor_login.py
```

This will show all doctors in your database and test the login credentials.

---

## 🔧 Alternative: Create New Test Doctor

If you want a fresh test doctor with phone `+919999999999`:

### Option A: Run SQL in Supabase

1. Go to Supabase Dashboard → SQL Editor
2. Paste this SQL:

```sql
INSERT INTO doctors (
    phone, 
    telegram_id, 
    access_code, 
    name, 
    mci_reg, 
    phc, 
    rating, 
    total_cases, 
    active
)
VALUES (
    '+919999999999',
    999999999,
    'TEST1234',
    'Dr. Test Kumar',
    'TEST12345',
    'Test PHC',
    5.0,
    0,
    true
)
ON CONFLICT (phone) DO UPDATE SET
    access_code = 'TEST1234',
    name = 'Dr. Test Kumar',
    active = true;
```

3. Click "Run"
4. Login with:
   - Phone: `+919999999999`
   - Access Code: `TEST1234`

### Option B: Use Existing SQL File

```bash
# The SQL file is already created at database/insert_test_doctor.sql
# Just run it in Supabase SQL Editor
```

---

## 📊 What You'll See After Login

### Sidebar (Doctor Profile)
- 👨‍⚕️ Doctor name
- 📱 Phone number
- 🏥 PHC name
- 🩺 MCI registration
- ⭐ Rating (out of 5.0)
- 📊 Total cases handled

### Tab 1: Live Queue
- Shows all pending X-ray requests assigned to you
- Each request shows:
  - Patient name and age
  - Village/location
  - Symptoms
  - Request date
  - X-ray image link (if uploaded)
- Actions:
  - ✅ Mark as Reviewed (individual)
  - ❌ Cancel request
  - ✅ Mark All as Reviewed (bulk action)

### Tab 2: My Reports
- Search by patient name
- Filter by status (reviewed, sent, cancelled)
- Expandable cards showing:
  - Patient details
  - Diseases detected
  - AI report
  - Doctor notes
  - PDF download link (if available)
  - X-ray image link

### Tab 3: Statistics
- Total cases count
- Pending requests count
- Reviewed count
- Sent count
- Cancelled count
- Status distribution chart
- Requests over time chart

---

## 🐛 Troubleshooting

### "Invalid phone number or access code"

**Solution 1: Use the working credentials**
```
Phone: +919876543210
Access Code: TEST1234
```

**Solution 2: Check what's in your database**
```bash
python test_doctor_login.py
```

This will show all doctors and their access codes.

**Solution 3: Update any doctor's access code**

Run this SQL in Supabase:
```sql
UPDATE doctors 
SET access_code = 'MYCODE123'
WHERE phone = '+919876543210';
```

Then login with:
```
Phone: +919876543210
Code: MYCODE123
```

### Dashboard doesn't load

**Check if Streamlit is running:**
```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

**Check if .env file exists:**
```bash
ls dashboard/.env
```

Should contain:
```
SUPABASE_URL=https://hpflwfpbloifbarekyrn.supabase.co
SUPABASE_KEY=sb_secret_dNm15TgaBEia8voG_Pny4g_bQ6C6E6F
```

### No pending requests in queue

This is normal if no patients have submitted X-ray requests yet. To test:

1. Run the patient bot: `python bot.py`
2. Open Telegram and message `@MediMindRuralBot`
3. Click "🩻 X-Ray Check"
4. Fill in patient details
5. Select the doctor (Dr. Shah)
6. Refresh the dashboard - request should appear!

---

## ✅ Success Checklist

- [ ] Dashboard starts without errors
- [ ] Login page appears
- [ ] Can login with `+919876543210` / `TEST1234`
- [ ] See doctor profile in sidebar
- [ ] Live Queue tab loads
- [ ] My Reports tab loads
- [ ] Statistics tab loads
- [ ] Can logout and login again

---

## 📸 Take Screenshots

After successful login, take screenshots of:
1. Login page
2. Doctor profile sidebar
3. Live Queue tab
4. My Reports tab
5. Statistics tab

---

## 🎯 Next Steps

After verifying the dashboard works:

1. Test the full workflow:
   - Patient submits X-ray request via bot
   - Doctor sees request in Live Queue
   - Doctor marks as reviewed
   - Check statistics update

2. Test with real X-ray images (when ready)

3. Test the Ollama VLM integration (doctor bot)

---

## 📝 Summary

**EASIEST WAY TO TEST:**

```bash
# Terminal 1: Start dashboard
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py

# Browser: Login with
Phone: +919876543210
Code: TEST1234
```

That's it! Should work immediately. ✅

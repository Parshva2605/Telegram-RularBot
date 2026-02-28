# 🚀 START DOCTOR DASHBOARD - Complete Guide

## ⚡ QUICK START (2 Steps)

### Step 1: Verify Test Doctor Exists

```bash
python verify_and_create_test_doctor.py
```

This will show you all available login credentials.

### Step 2: Start Dashboard

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

Then login with the credentials from Step 1.

---

## 🔑 LOGIN CREDENTIALS

You have TWO working options:

### ✅ OPTION 1: Dr. Shah (Recommended - Already in database)

```
Phone: +919876543210
Access Code: TEST1234
```

### ✅ OPTION 2: Dr. Test Kumar (Test account)

```
Phone: +919999999999
Access Code: TEST1234
```

**Note:** If Option 2 doesn't work, run the SQL in `database/insert_test_doctor.sql` in Supabase SQL Editor.

---

## 📋 COMPLETE WORKFLOW

### 1. Verify Database

```bash
python verify_and_create_test_doctor.py
```

**What it does:**
- Connects to Supabase
- Lists all doctors in database
- Shows their phone numbers and access codes
- Optionally creates test doctor if missing

**Expected output:**
```
✅ OPTION 1: Dr. Shah (Already exists!)
   Phone: +919876543210
   Access Code: TEST1234
   👉 USE THIS TO LOGIN NOW!
```

### 2. Start Dashboard

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

**What happens:**
- Streamlit server starts on http://localhost:8501
- Browser opens automatically
- Login page appears

### 3. Login

On the login page:
1. Enter Phone: `+919876543210`
2. Enter Access Code: `TEST1234`
3. Click "🔓 Login"

**Expected result:**
```
✅ Welcome Dr. Shah!
```

### 4. Explore Dashboard

After login, you'll see 3 tabs:

#### 📋 Tab 1: Live Queue
- Shows pending X-ray requests assigned to you
- Each request displays:
  - Patient name, age, village
  - Symptoms
  - Request date
  - X-ray image link (if uploaded)
- Actions available:
  - ✅ Mark as Reviewed (individual)
  - ❌ Cancel request
  - ✅ Mark All as Reviewed (bulk)

#### 📊 Tab 2: My Reports
- Search by patient name
- Filter by status (reviewed, sent, cancelled)
- View detailed report cards with:
  - Patient information
  - Diseases detected
  - AI analysis report
  - Doctor notes
  - PDF download link
  - X-ray image link

#### 📈 Tab 3: Statistics
- Total cases handled
- Pending requests count
- Reviewed count
- Sent count
- Cancelled count
- Status distribution chart
- Requests over time chart

### 5. Test Full Workflow (Optional)

To see the dashboard in action with real data:

**Terminal 1: Start Patient Bot**
```bash
python bot.py
```

**Terminal 2: Keep Dashboard Running**
```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

**Telegram: Submit X-ray Request**
1. Open Telegram
2. Message `@MediMindRuralBot`
3. Click "🩻 X-Ray Check"
4. Follow the step-by-step form:
   - Enter patient name
   - Enter age
   - Enter village
   - Describe symptoms
5. Select doctor (Dr. Shah)
6. Confirm submission

**Dashboard: See Request Appear**
1. Refresh the "Live Queue" tab
2. You should see the new request
3. Click "✅ Mark as Reviewed"
4. Check "Statistics" tab to see updated counts

---

## 🐛 TROUBLESHOOTING

### Problem: "Invalid phone number or access code"

**Solution 1: Use Dr. Shah (Easiest)**
```
Phone: +919876543210
Access Code: TEST1234
```

**Solution 2: Check what's in database**
```bash
python verify_and_create_test_doctor.py
```

This shows all doctors and their actual access codes.

**Solution 3: Update access code in Supabase**

1. Go to Supabase Dashboard
2. Click "SQL Editor"
3. Paste and run:
```sql
UPDATE doctors 
SET access_code = 'TEST1234'
WHERE phone = '+919876543210';
```

Or use the complete SQL file:
```sql
-- Run database/insert_test_doctor.sql in Supabase SQL Editor
```

### Problem: Dashboard doesn't start

**Check if Streamlit is installed:**
```bash
pip install streamlit
```

**Check if in correct directory:**
```bash
cd dashboard
ls pages/10_👨‍⚕️_Doctor_Dashboard.py
```

**Check if .env file exists:**
```bash
cat dashboard/.env
```

Should contain:
```
SUPABASE_URL=https://hpflwfpbloifbarekyrn.supabase.co
SUPABASE_KEY=sb_secret_dNm15TgaBEia8voG_Pny4g_bQ6C6E6F
```

### Problem: "No pending requests in queue"

This is normal if no patients have submitted requests yet.

**To test with sample data:**

1. Run patient bot: `python bot.py`
2. Submit X-ray request via Telegram
3. Refresh dashboard

**Or insert test data in Supabase:**
```sql
INSERT INTO xray_requests (
    patient_name, 
    age, 
    village, 
    symptoms, 
    doctor_phone, 
    status, 
    scan_type
)
VALUES (
    'Test Patient', 
    45, 
    'Test Village', 
    'Test symptoms', 
    '+919876543210', 
    'pending', 
    'X-ray'
);
```

### Problem: Supabase connection error

**Check environment variables:**
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv('dashboard/.env'); print('URL:', os.getenv('SUPABASE_URL')); print('KEY:', os.getenv('SUPABASE_KEY')[:30] + '...')"
```

**Test connection:**
```bash
python test_doctor_login.py
```

### Problem: RLS policy blocking updates

If you can't update doctor records, run this in Supabase SQL Editor:

```sql
-- Temporarily disable RLS for testing
ALTER TABLE doctors DISABLE ROW LEVEL SECURITY;

-- Update the doctor
UPDATE doctors 
SET access_code = 'TEST1234'
WHERE phone = '+919999999999';

-- Re-enable RLS
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
```

---

## ✅ SUCCESS CHECKLIST

After following this guide, you should have:

- [ ] Verified test doctor exists in database
- [ ] Started dashboard successfully
- [ ] Logged in with working credentials
- [ ] Seen doctor profile in sidebar
- [ ] Viewed Live Queue tab
- [ ] Viewed My Reports tab
- [ ] Viewed Statistics tab
- [ ] (Optional) Tested full workflow with patient bot

---

## 📸 SCREENSHOTS TO TAKE

For documentation:

1. **Verification script output** showing available credentials
2. **Login page** with phone and access code fields
3. **Welcome message** after successful login
4. **Doctor profile sidebar** with name, phone, PHC, rating
5. **Live Queue tab** (empty or with requests)
6. **My Reports tab** with search and filters
7. **Statistics tab** with metrics and charts

---

## 🎯 NEXT STEPS

After verifying the dashboard works:

### 1. Test with Real Data
- Submit X-ray requests via patient bot
- Review requests in dashboard
- Mark as reviewed
- Check statistics update

### 2. Test Doctor Bot (Ollama VLM)
```bash
# Make sure Ollama is running
ollama serve

# Start doctor bot
python doctor_bot.py
```

### 3. Test Full Integration
- Patient submits X-ray via `@MediMindRuralBot`
- Doctor receives Telegram notification
- Doctor reviews in web dashboard
- Doctor analyzes X-ray via `@MediMindDoctorBot`
- AI generates report with VLM
- Report sent back to patient

---

## 📚 RELATED FILES

- `verify_and_create_test_doctor.py` - Verification script
- `test_doctor_login.py` - Detailed login test
- `database/insert_test_doctor.sql` - SQL to create/update test doctor
- `dashboard/pages/10_👨‍⚕️_Doctor_Dashboard.py` - Dashboard implementation
- `DASHBOARD_LOGIN_TEST.md` - Detailed testing guide
- `WORKING_LOGIN_CREDENTIALS.md` - All available credentials

---

## 💡 TIPS

1. **Always verify first**: Run `verify_and_create_test_doctor.py` before starting dashboard
2. **Use Dr. Shah**: Phone `+919876543210` is the easiest option (already exists)
3. **Keep terminal open**: Don't close the terminal running Streamlit
4. **Refresh browser**: If data doesn't update, refresh the browser page
5. **Check logs**: Terminal shows any errors from Streamlit
6. **Test incrementally**: Verify each tab works before testing full workflow

---

## 🆘 STILL HAVING ISSUES?

1. **Run verification script**: `python verify_and_create_test_doctor.py`
2. **Check output**: Look for any error messages
3. **Try Dr. Shah first**: Use `+919876543210` / `TEST1234`
4. **Check Supabase**: Verify doctors table has data
5. **Run SQL**: Use `database/insert_test_doctor.sql` in Supabase
6. **Test connection**: Run `python test_doctor_login.py`

---

## ✅ SUMMARY

**Fastest way to test:**

```bash
# Step 1: Verify
python verify_and_create_test_doctor.py

# Step 2: Start
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py

# Step 3: Login
Phone: +919876543210
Code: TEST1234
```

**That's it!** The dashboard should work immediately. ✅

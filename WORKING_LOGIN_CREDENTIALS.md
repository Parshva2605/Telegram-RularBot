# ✅ WORKING LOGIN CREDENTIALS

## 🔑 Use These Credentials (Already in Database!)

### Option 1: Dr. Shah (Already exists)
```
Phone: +919876543210
Access Code: TEST1234
```

### Option 2: Dr. Test Kumar (Update required)
```
Phone: +919999999999
Access Code: TEST1234
```

---

## 🚀 Quick Test

### Step 1: Start Dashboard

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

### Step 2: Login with Option 1 (Easiest)

```
Phone: +919876543210
Access Code: TEST1234
```

This doctor already exists in your database!

---

## 🔧 If Option 1 Doesn't Work

Run this SQL in Supabase to update the test doctor:

```sql
UPDATE doctors 
SET access_code = 'TEST1234'
WHERE phone = '+919999999999';
```

Then use:
```
Phone: +919999999999
Access Code: TEST1234
```

---

## 📊 All Available Doctors

From your database, these doctors exist:

1. **Dr. Shah**
   - Phone: `+919876543210`
   - Code: `TEST1234` ✅

2. **Dr. Patel**
   - Phone: `+916223946485`
   - Code: `DPJ37PKT`

3. **Shah**
   - Phone: `+918200991740`
   - Code: `XR62L78K`

4. **Dr. Shah**
   - Phone: `+911155518443`
   - Code: `94CNU92G`

5. **Dr. Test Kumar**
   - Phone: `+919999999999`
   - Code: `TEST1111` (needs update to TEST1234)

---

## ✅ Recommended: Use Dr. Shah

**Easiest option - No SQL needed!**

```
Phone: +919876543210
Access Code: TEST1234
```

This is already in your database and should work immediately!

---

## 🧪 Test Script

To verify credentials work, run:

```bash
python test_doctor_login.py
```

This will show all doctors and test the login.

---

## 🐛 Troubleshooting

### "Invalid phone number or access code"

**Try Dr. Shah first:**
```
Phone: +919876543210
Code: TEST1234
```

**If that doesn't work, check Supabase:**

1. Go to Supabase Dashboard
2. Click "Table Editor"
3. Open "doctors" table
4. Find row with phone `+919876543210`
5. Check the `access_code` column
6. Use that exact code

### Still not working?

**Update any doctor's access code:**

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

---

## 📝 Summary

**EASIEST WAY:**
1. Start dashboard: `cd dashboard && streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py`
2. Use: Phone `+919876543210` / Code `TEST1234`
3. Should work immediately! ✅

If not, run the test script to see what's in your database:
```bash
python test_doctor_login.py
```

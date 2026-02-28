# 🔐 Create Test Doctor for Dashboard Login

## 📝 Quick Steps

### Step 1: Open Supabase SQL Editor

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on your project: `hpflwfpbloifbarekyrn`
3. Click "SQL Editor" in the left sidebar
4. Click "New query"

### Step 2: Run the SQL Script

Copy and paste this SQL:

```sql
-- Insert test doctor with known credentials
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
    mci_reg = 'TEST12345',
    phc = 'Test PHC',
    active = true;
```

### Step 3: Click "Run" or press Ctrl+Enter

You should see: "Success. No rows returned"

### Step 4: Verify the Doctor

Run this query to verify:

```sql
SELECT * FROM doctors WHERE phone = '+919999999999';
```

You should see the test doctor with:
- phone: +919999999999
- access_code: TEST1234
- name: Dr. Test Kumar

---

## 🔑 Login Credentials

Use these credentials in the Doctor Dashboard:

```
Phone: +919999999999
Access Code: TEST1234
```

---

## 🧪 Test the Dashboard

### Step 1: Start Dashboard

```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

### Step 2: Login

1. Enter Phone: `+919999999999`
2. Enter Access Code: `TEST1234`
3. Click "🔓 Login"

### Step 3: Verify

You should see:
- ✅ Welcome Dr. Test Kumar!
- Dashboard loads
- Sidebar shows doctor profile

---

## 🐛 Troubleshooting

### "Invalid phone number or access code"

**Check 1:** Verify doctor exists in database
```sql
SELECT * FROM doctors WHERE phone = '+919999999999';
```

**Check 2:** Verify access code is correct
```sql
SELECT phone, access_code, name FROM doctors WHERE phone = '+919999999999';
```

**Check 3:** Make sure phone has `+` prefix
- ✅ Correct: `+919999999999`
- ❌ Wrong: `919999999999`

### Doctor not found in database

**Solution:** Run the insert script again:
```sql
INSERT INTO doctors (phone, telegram_id, access_code, name, mci_reg, phc, rating, total_cases, active)
VALUES ('+919999999999', 999999999, 'TEST1234', 'Dr. Test Kumar', 'TEST12345', 'Test PHC', 5.0, 0, true)
ON CONFLICT (phone) DO UPDATE SET access_code = 'TEST1234';
```

### Dashboard shows error

**Check .env file:**
```bash
cd dashboard
cat .env
```

Should have:
```
SUPABASE_URL=https://hpflwfpbloifbarekyrn.supabase.co
SUPABASE_KEY=sb_secret_dNm15TgaBEia8voG_Pny4g_bQ6C6E6F
```

---

## 📊 Alternative: Check Existing Doctors

If you want to use an existing doctor instead:

```sql
-- List all doctors with their access codes
SELECT phone, access_code, name, phc FROM doctors WHERE active = true;
```

Use any phone + access_code combination from the results.

---

## ✅ Success Checklist

- [ ] SQL script run successfully in Supabase
- [ ] Doctor verified in database
- [ ] Dashboard started
- [ ] Login successful with test credentials
- [ ] Dashboard loads with doctor profile

---

## 🎯 Quick Copy-Paste

**SQL to run in Supabase:**
```sql
INSERT INTO doctors (phone, telegram_id, access_code, name, mci_reg, phc, rating, total_cases, active)
VALUES ('+919999999999', 999999999, 'TEST1234', 'Dr. Test Kumar', 'TEST12345', 'Test PHC', 5.0, 0, true)
ON CONFLICT (phone) DO UPDATE SET access_code = 'TEST1234';
```

**Login credentials:**
```
Phone: +919999999999
Code: TEST1234
```

**Start dashboard:**
```bash
cd dashboard
streamlit run pages/10_👨‍⚕️_Doctor_Dashboard.py
```

---

## 📝 Notes

- This is a test account for development
- Use for testing dashboard features
- Can be deleted after testing
- For production, use real doctor accounts from Telegram bot registration

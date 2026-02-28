# 🗄️ Supabase X-Ray Tables Setup Instructions

## ✅ Pre-Check

Before starting, verify:
- [ ] backup_live/ folder exists ✅
- [ ] git status clean (or only .env.doctor modified) ✅
- [ ] Supabase project is accessible

---

## 📋 Step-by-Step Setup

### 1️⃣ Open Supabase Dashboard

1. Go to https://supabase.com
2. Sign in to your account
3. Select your project: **hpflwfpbloifbarekyrn**
4. Click **SQL Editor** in left sidebar

### 2️⃣ Run the Schema Script

1. Click **New Query** button
2. Open the file: `database/schema_xray.sql`
3. **Copy ALL content** (Ctrl+A, Ctrl+C)
4. **Paste** into Supabase SQL Editor
5. Click **Run** button (or press Ctrl+Enter)

**Expected Output:**
```
Success. No rows returned
```

### 3️⃣ Verify Tables Created

1. Click **Table Editor** in left sidebar
2. You should see **2 NEW tables**:
   - ✅ `doctors`
   - ✅ `xray_requests`

3. Click on `doctors` table:
   - Should see 1 test row: Dr. Shah
   - Columns: id, phone, telegram_id, access_code, name, mci_reg, phc, rating, etc.

4. Click on `xray_requests` table:
   - Should see 1 test row: Ramesh Patel
   - Columns: id, patient_name, age, village, symptoms, image_url, etc.

### 4️⃣ Verify RLS (Row Level Security)

1. In Table Editor, look for **padlock icon** 🔒 next to table names
2. Both tables should show padlock (RLS enabled)
3. Click on table → **Policies** tab
4. Should see policies like:
   - "Doctors view own profile"
   - "Public insert xray requests"
   - "Admin full access"

### 5️⃣ Test Data Verification

Run this query in SQL Editor to verify:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('doctors', 'xray_requests');

-- Check RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('doctors', 'xray_requests');

-- Count records
SELECT 'doctors' as table_name, COUNT(*) as count FROM doctors
UNION ALL
SELECT 'xray_requests' as table_name, COUNT(*) as count FROM xray_requests;
```

**Expected Output:**
```
table_name      | count
----------------|------
doctors         | 1
xray_requests   | 1
```

---

## 📸 Screenshot Checklist

Take screenshots of:

1. **Table Editor** showing both new tables:
   - doctors (with test data)
   - xray_requests (with test data)

2. **RLS Status** showing padlock icons 🔒

3. **Test Query Results** showing counts

---

## ✅ Verification Checklist

- [ ] SQL script ran without errors
- [ ] `doctors` table exists with 1 test row
- [ ] `xray_requests` table exists with 1 test row
- [ ] RLS enabled on both tables (padlock icon)
- [ ] Policies visible in Policies tab
- [ ] Test queries return correct counts
- [ ] Screenshots taken

---

## 🚀 After Completion

1. Show Kiro the screenshots
2. Confirm: **"SUPABASE TABLES READY - 2 new tables + test data"**
3. Kiro will commit the schema file to git
4. Proceed to Step 3: Build bot code

---

## 🔧 Troubleshooting

### Error: "relation already exists"
- Tables already created, safe to ignore
- Or drop tables first: `DROP TABLE IF EXISTS doctors, xray_requests CASCADE;`

### Error: "policy already exists"
- Policies already created, safe to ignore
- Script includes `DROP POLICY IF EXISTS` to handle this

### No test data visible
- Check if INSERT statements ran
- Manually insert test data from schema_xray.sql

### RLS not showing
- Refresh page
- Check: `ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;` ran successfully

---

## 📊 Table Structure Summary

### doctors table (8 columns)
- id, phone, telegram_id, access_code
- name, mci_reg, phc, rating
- total_cases, active, created, last_login

### xray_requests table (18 columns)
- Patient: patient_name, age, village, symptoms
- Image: image_url, scan_type
- AI: model_used, diseases_detected, confidence_scores, ai_report
- Doctor: doctor_notes, doctor_phone, reviewed_at
- Output: hindi_patient, report_pdf_url
- Status: status, consent_time, created_at, updated_at

---

**Ready to proceed? Show Kiro the screenshots!** 📸

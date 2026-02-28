# 📸 Visual Guide - Supabase Setup

## 🎯 What You'll See

### Step 1: SQL Editor
```
┌─────────────────────────────────────────┐
│ Supabase Dashboard                      │
├─────────────────────────────────────────┤
│ [SQL Editor] ← Click here              │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ [+ New Query]                       │ │
│ │                                     │ │
│ │ Paste schema_xray.sql here          │ │
│ │                                     │ │
│ │ [▶ Run] ← Click to execute          │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Step 2: Table Editor
```
┌─────────────────────────────────────────┐
│ [Table Editor] ← Click here             │
├─────────────────────────────────────────┤
│ Tables:                                 │
│ ✅ appointments                         │
│ ✅ doctors          🔒 ← NEW + RLS      │
│ ✅ emergencies                          │
│ ✅ govt_schemes                         │
│ ✅ health_workers                       │
│ ✅ issues                               │
│ ✅ maternal                             │
│ ✅ reminders                            │
│ ✅ xray_requests    🔒 ← NEW + RLS      │
└─────────────────────────────────────────┘
```

### Step 3: doctors Table View
```
┌─────────────────────────────────────────────────────────┐
│ doctors                                        🔒 RLS    │
├─────────────────────────────────────────────────────────┤
│ id │ phone          │ telegram_id │ access_code │ name  │
├────┼────────────────┼─────────────┼─────────────┼───────┤
│ 1  │ +919876543210  │ 123456789   │ TEST1234    │ Dr... │
└─────────────────────────────────────────────────────────┘
```

### Step 4: xray_requests Table View
```
┌──────────────────────────────────────────────────────────┐
│ xray_requests                                   🔒 RLS   │
├──────────────────────────────────────────────────────────┤
│ id │ patient_name  │ age │ village │ symptoms    │ status│
├────┼───────────────┼─────┼─────────┼─────────────┼───────┤
│ 1  │ Ramesh Patel  │ 45  │ Anklav  │ Cough + ... │ pend..│
└──────────────────────────────────────────────────────────┘
```

---

## ✅ Success Indicators

### 1. SQL Execution Success
```
✅ Success. No rows returned
```

### 2. Tables Visible
- See "doctors" in table list
- See "xray_requests" in table list
- Both have 🔒 padlock icon

### 3. Test Data Present
- doctors: 1 row (Dr. Shah)
- xray_requests: 1 row (Ramesh Patel)

### 4. RLS Enabled
- Click table → Policies tab
- See 4 policies for doctors
- See 4 policies for xray_requests

---

## 📸 Screenshots to Take

### Screenshot 1: Table List
Show:
- Left sidebar with "Table Editor" selected
- Table list showing "doctors" and "xray_requests"
- Padlock icons 🔒 visible

### Screenshot 2: doctors Table
Show:
- doctors table selected
- Test data row visible (Dr. Shah)
- All columns visible

### Screenshot 3: xray_requests Table
Show:
- xray_requests table selected
- Test data row visible (Ramesh Patel)
- All columns visible

### Screenshot 4: RLS Policies (Optional)
Show:
- Policies tab
- List of policies for one table

---

## 🔍 Verification Checklist

Run this query and screenshot the result:

```sql
-- Quick verification
SELECT 
    'doctors' as table_name, 
    COUNT(*) as rows,
    (SELECT COUNT(*) FROM pg_policies WHERE tablename = 'doctors') as policies
FROM doctors
UNION ALL
SELECT 
    'xray_requests' as table_name, 
    COUNT(*) as rows,
    (SELECT COUNT(*) FROM pg_policies WHERE tablename = 'xray_requests') as policies
FROM xray_requests;
```

**Expected Result:**
```
table_name      | rows | policies
----------------|------|----------
doctors         | 1    | 4
xray_requests   | 1    | 4
```

---

## 🚨 Common Issues

### Issue: "relation already exists"
**Solution:** Tables already created, safe to ignore

### Issue: No test data visible
**Solution:** Run INSERT statements manually:
```sql
INSERT INTO doctors (phone, telegram_id, access_code, name, mci_reg, phc)
VALUES ('+919876543210', 123456789, 'TEST1234', 'Dr. Shah', 'GJMC12345', 'Anklav PHC');

INSERT INTO xray_requests (patient_name, age, village, symptoms, doctor_phone, status, scan_type)
VALUES ('Ramesh Patel', 45, 'Anklav', 'Cough + chest pain', '+919876543210', 'pending', 'X-ray');
```

### Issue: RLS not showing
**Solution:** Refresh page, check ALTER TABLE commands ran

---

**Ready? Take screenshots and show Kiro!** 📸

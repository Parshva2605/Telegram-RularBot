# 🧪 Quick Test - Patient X-Ray Feature

## 🚀 Quick Start

```bash
# 1. Start patient bot
python bot.py

# 2. Test in Telegram @MediMindRuralBot
```

---

## 📱 Test Flow (Copy-Paste)

### 1. Start Bot
```
/start
```

### 2. Select Language
Click: **English 🇺🇸**

### 3. Click X-Ray Button
Click: **🩻 X-Ray Check**

### 4. Give Consent
Click: **✅ I consent**

### 5. Enter Patient Form
```
Ramesh Patel|45|Anklav|Cough 5 days chest pain
```

### 6. Select Doctor
Click any doctor from the list (e.g., "Dr. Shah ⭐⭐⭐⭐⭐ (Anklav PHC)")

### 7. Check Status
```
/status
```

---

## ✅ Expected Results

### After Form Submission:
```
✅ Sent to doctor!

Use /status to check progress.

Doctor will send PDF report here.
```

### After /status Command:
```
📊 X-Ray Request Status:

⏳ Ramesh Patel (45y) - pending
   📍 Anklav
```

### Doctor Bot Notification:
```
🩻 NEW X-RAY REQUEST

👤 Ramesh Patel (45y)
📍 Anklav
🩺 Cough 5 days chest pain

📋 Check /status for details
```

### Supabase Database:
Check `xray_requests` table for new row:
- patient_name: "Ramesh Patel"
- age: 45
- village: "Anklav"
- symptoms: "Cough 5 days chest pain"
- status: "pending"
- doctor_phone: (selected doctor's phone)

---

## 📸 Screenshot Checklist

- [ ] Main menu with "🩻 X-Ray Check" button
- [ ] Consent screen
- [ ] Form entry
- [ ] Doctor selection list
- [ ] Success message
- [ ] `/status` output
- [ ] Supabase xray_requests table row
- [ ] Doctor bot notification

---

## 🐛 Common Issues

### "Wrong format!" error
**Fix:** Use pipe separator `|` not comma or space
```
✅ CORRECT: Ramesh Patel|45|Anklav|Cough 5 days
❌ WRONG: Ramesh Patel, 45, Anklav, Cough 5 days
```

### No doctors shown
**Fix:** Check doctors table has active doctors:
```sql
SELECT * FROM doctors WHERE active = true;
```

### Doctor not notified
**Fix:** Doctor needs telegram_id in database. Register doctor first using @MediMindDoctorBot

---

## 🎯 Success Criteria

✅ Patient can submit X-ray request
✅ Request saves to database
✅ Doctor receives notification
✅ Patient can check status
✅ All 3 languages work

---

## 📝 After Testing

Say: **"PATIENT X-RAY BUTTON READY - Screenshot + DB row"**

And share:
1. Screenshot of patient flow
2. Screenshot of Supabase xray_requests table
3. Screenshot of doctor notification

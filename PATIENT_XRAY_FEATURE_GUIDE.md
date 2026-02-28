# 🩻 Patient X-Ray Check Feature - Testing Guide

## ✅ COMPLETED: Patient Bot X-Ray Integration

The live patient bot (`@MediMindRuralBot`) now has the X-Ray Check feature that feeds doctor queue!

---

## 🎯 What Was Added

### 1. Environment Configuration (.env)
Added X-ray bot tokens:
```env
MEDIMIND_DOCTOR_TOKEN=8650401246:AAE7Ax1z2Z7fBjXLLcxGKvJ9STnMQoLYyjE
MEDIMIND_XRAY_REQ_TOKEN=8610315040:AAEtUAtz4lQmtrE2O1-qLQ5fQ3krJv8m7ig
```

### 2. Main Menu Button
Added "🩻 X-Ray Check" button to main menu in all 3 languages:
- English: "🩻 X-Ray Check"
- Hindi: "🩻 एक्स-रे जांच"
- Gujarati: "🩻 એક્સ-રે તપાસ"

### 3. X-Ray Workflow
Complete patient flow:
1. Click "🩻 X-Ray Check"
2. Consent screen with "✅ I consent" button
3. Form prompt: `Name|Age|Village|Symptoms`
4. Doctor selection (shows top 5 doctors by rating)
5. Request sent to doctor's queue
6. Doctor notified via Telegram
7. Patient can check status with `/status`

### 4. New Commands
- `/status` - Check X-ray request status (pending/reviewed/sent/cancelled)

### 5. Database Integration
- Inserts to `xray_requests` table with:
  - Patient info (name, age, village, symptoms)
  - Doctor assignment (doctor_phone)
  - Status tracking (pending → reviewed → sent)
  - Consent timestamp
  - User ID for tracking

### 6. Doctor Notification
- Real-time Telegram notification to assigned doctor
- Shows patient details and symptoms
- Prompts doctor to check `/status`

---

## 🧪 Testing Instructions

### Step 1: Start Patient Bot
```bash
python bot.py
```

### Step 2: Test in Telegram (@MediMindRuralBot)

1. **Start bot:**
   ```
   /start
   ```

2. **Select language** (English/Hindi/Gujarati)

3. **Click "🩻 X-Ray Check"** button in main menu

4. **Click "✅ I consent"**

5. **Enter patient form:**
   ```
   Ramesh Patel|45|Anklav|Cough 5 days chest pain
   ```

6. **Select a doctor** from the list (shows top 5 by rating)

7. **Verify success message:**
   ```
   ✅ Sent to doctor!
   
   Use /status to check progress.
   
   Doctor will send PDF report here.
   ```

8. **Check status:**
   ```
   /status
   ```
   
   Should show:
   ```
   📊 X-Ray Request Status:
   
   ⏳ Ramesh Patel (45y) - pending
      📍 Anklav
   ```

### Step 3: Verify Database Entry

Check Supabase `xray_requests` table:
- New row with patient details
- `status` = 'pending'
- `doctor_phone` = selected doctor's phone
- `consent_time` = current timestamp

### Step 4: Verify Doctor Notification

Check doctor's Telegram (@MediMindDoctorBot):
- Should receive notification:
  ```
  🩻 NEW X-RAY REQUEST
  
  👤 Ramesh Patel (45y)
  📍 Anklav
  🩺 Cough 5 days chest pain
  
  📋 Check /status for details
  ```

---

## 📸 Screenshots to Take

1. Main menu showing "🩻 X-Ray Check" button
2. Consent screen
3. Form entry example
4. Doctor selection list
5. Success message
6. `/status` output showing pending request
7. Supabase table row (xray_requests)
8. Doctor bot notification

---

## 🔍 Verification Checklist

- [ ] Patient bot starts without errors
- [ ] Main menu shows X-Ray Check button
- [ ] Consent screen appears
- [ ] Form accepts `Name|Age|Village|Symptoms` format
- [ ] Form rejects wrong format with error message
- [ ] Doctor list shows top 5 doctors by rating
- [ ] Request saves to Supabase xray_requests table
- [ ] Doctor receives Telegram notification
- [ ] `/status` command shows request status
- [ ] All 3 languages work (English/Hindi/Gujarati)

---

## 🐛 Troubleshooting

### "No doctors available"
**Solution:** Make sure doctors table has active doctors:
```sql
SELECT * FROM doctors WHERE active = true;
```

### Doctor not notified
**Solution:** Check doctor has `telegram_id` in database:
```sql
SELECT telegram_id FROM doctors WHERE phone = '+91XXXXXXXXXX';
```

### Form not accepted
**Solution:** Use exact format with pipe separator:
```
Name|Age|Village|Symptoms
```
Example:
```
Ramesh Patel|45|Anklav|Cough 5 days chest pain
```

### Status shows "No X-ray requests"
**Solution:** Make sure request was saved to database. Check Supabase logs.

---

## 🔗 Integration with Doctor Bot

The patient X-ray request now feeds directly into doctor's queue:

1. **Patient submits** → `xray_requests` table (status: pending)
2. **Doctor notified** → Telegram message to doctor
3. **Doctor checks** → `/status` in doctor bot shows pending queue
4. **Doctor analyzes** → Uploads X-ray image, gets AI analysis
5. **Doctor reviews** → Status changes to 'reviewed'
6. **Doctor sends** → PDF report sent to patient (status: 'sent')

---

## 📊 Database Schema

The `xray_requests` table structure:
```sql
CREATE TABLE xray_requests (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    username TEXT,
    patient_name TEXT,
    age INTEGER,
    village TEXT,
    symptoms TEXT,
    doctor_phone TEXT,
    status TEXT DEFAULT 'pending',
    consent_time TIMESTAMP,
    image_url TEXT,
    scan_type TEXT,
    diseases_detected JSONB,
    confidence_scores JSONB,
    ai_report TEXT,
    doctor_notes TEXT,
    reviewed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Next Steps

After testing patient bot:

1. Test doctor bot receiving requests
2. Test doctor analyzing X-ray images
3. Test AI model integration (14-diseases)
4. Test PDF report generation
5. Test sending report back to patient

---

## ✅ Commit Message

```bash
git add bot.py .env
git commit -m "Step7 MAJOR: Patient X-Ray Check button + form + doctor assign"
git push
```

---

## 📝 Summary

The patient bot now has a complete X-Ray Check workflow:
- ✅ Main menu button added
- ✅ Consent screen implemented
- ✅ Form validation (Name|Age|Village|Symptoms)
- ✅ Doctor selection from database
- ✅ Request saved to xray_requests table
- ✅ Doctor notified via Telegram
- ✅ Status tracking with `/status` command
- ✅ Multi-language support (EN/HI/GU)

Patients can now request X-ray analysis, and doctors receive real-time notifications in their queue!

# 🧪 Test Doctor Bot - Quick Guide

## ✅ Step 3 Complete - Doctor Bot Core Ready

### 📦 What Was Built

**File:** `doctor_bot.py` (420 lines)
- ✅ Doctor registration with MCI validation
- ✅ Access code generation (8-char alphanumeric)
- ✅ Main menu with 4 options
- ✅ Queue management (view pending X-rays)
- ✅ Old reports view
- ✅ Scan type selection (X-ray, CT, MRI, Skin)
- ✅ Code regeneration
- ✅ Status command

**File:** `requirements_doctor.txt`
- python-telegram-bot==21.0.1
- supabase==2.3.0
- python-dotenv==1.0.0

---

## 🚀 How to Test Locally

### 1. Install Dependencies
```bash
pip install -r requirements_doctor.txt
```

### 2. Set Environment Variables

**Option A: Export manually (Linux/Mac)**
```bash
export SUPABASE_URL="https://hpflwfpbloifbarekyrn.supabase.co"
export SUPABASE_KEY="your_supabase_key"
export MEDIMIND_DOCTOR_TOKEN="your_doctor_bot_token"
export ADMIN_TELEGRAM_ID="1155518443"
```

**Option B: Source .env.doctor (Linux/Mac)**
```bash
source .env.doctor
```

**Option C: PowerShell (Windows)**
```powershell
$env:SUPABASE_URL="https://hpflwfpbloifbarekyrn.supabase.co"
$env:SUPABASE_KEY="your_supabase_key"
$env:MEDIMIND_DOCTOR_TOKEN="your_doctor_bot_token"
$env:ADMIN_TELEGRAM_ID="1155518443"
```

### 3. Run the Bot
```bash
python doctor_bot.py
```

**Expected Output:**
```
INFO - Starting MediMind Doctor Bot...
INFO - Doctor bot is running...
```

---

## 📱 Test in Telegram

### Test 1: New Doctor Registration

1. Open Telegram
2. Search for `@MediMindDoctorBot`
3. Send `/start`

**Expected Response:**
```
👨‍⚕️ DOCTOR REGISTRATION

📱 Telegram ID: 123456789
📞 Phone: +91123456789

Please enter your details in this format:

Name | MCI Reg | PHC Name

Example:
Dr. Shah | GJMC12345 | Anklav PHC

Send your details now:
```

4. Send: `Dr. Test | GJMC99999 | Test PHC`

**Expected Response:**
```
✅ REGISTRATION SUCCESSFUL

👨‍⚕️ Dr. Test
🩺 MCI: GJMC99999
🏥 PHC: Test PHC

🔐 Access Code: X7K9P2M4

⚠️ Save this code! Use it to login on the website.

Choose an option below:
```

**Menu Buttons:**
- 📋 My Queue
- 🩻 Analyze Image
- 📋 Old Reports
- 🔐 Regen Code

### Test 2: Returning Doctor

1. Send `/start` again

**Expected Response:**
```
✅ Welcome back, Dr. Test!

🏥 PHC: Test PHC
🩺 MCI: GJMC99999
⭐ Rating: 0.0/5.0
📊 Cases: 0

Choose an option below:
```

### Test 3: My Queue

1. Click "📋 My Queue" button

**Expected Response:**
```
✅ No X-rays in your queue!

All cases reviewed.
```

(Will show X-rays once patients submit them)

### Test 4: Analyze Image

1. Click "🩻 Analyze Image" button

**Expected Response:**
```
🏥 SELECT SCAN TYPE

What type of scan do you want to analyze?
```

**Buttons:**
- 🫁 X-ray
- 🧠 CT Scan | 🩻 MRI
- 🩹 Skin
- 🔙 Back

### Test 5: Regen Code

1. Click "🔐 Regen Code" button

**Expected Response:**
```
🔐 NEW ACCESS CODE

Code: A8H3K9P2

Use this to login on the website.
```

### Test 6: Status Command

1. Send `/status`

**Expected Response:**
```
📊 QUEUE STATUS

🔴 Pending: 0
✅ Reviewed: 0
📈 Total Cases: 0
⭐ Rating: 0.0/5.0
```

---

## 📸 Screenshots to Take

1. **Registration Flow**
   - /start command
   - Profile input
   - Success message with access code

2. **Main Menu**
   - All 4 buttons visible
   - Clean layout

3. **Queue View**
   - Empty queue message (or with test data)

4. **Scan Type Selection**
   - All scan types visible

5. **Code Regeneration**
   - New code displayed

---

## ✅ Verification Checklist

- [ ] Bot starts without errors
- [ ] /start shows registration form
- [ ] Profile format validation works
- [ ] Access code generated (8 characters)
- [ ] Doctor saved to Supabase `doctors` table
- [ ] Main menu appears with 4 buttons
- [ ] Queue button works (shows empty or data)
- [ ] Analyze button shows scan types
- [ ] Old reports button works
- [ ] Regen code button generates new code
- [ ] /status command works
- [ ] /regen_code command works
- [ ] Back button returns to main menu

---

## 🔍 Check Supabase

After registration, verify in Supabase:

1. Go to Table Editor → `doctors`
2. Should see new row with:
   - telegram_id: Your Telegram ID
   - name: Dr. Test
   - mci_reg: GJMC99999
   - phc: Test PHC
   - access_code: 8-character code
   - rating: 0.0
   - total_cases: 0
   - active: true

---

## 🐛 Troubleshooting

### Bot doesn't start
- Check MEDIMIND_DOCTOR_TOKEN is set
- Verify token is correct from @BotFather
- Check internet connection

### "Error connecting to database"
- Verify SUPABASE_URL and SUPABASE_KEY
- Check Supabase project is active
- Run schema_xray.sql if tables don't exist

### Registration fails
- Check `doctors` table exists in Supabase
- Verify RLS policies are set
- Check format: `Name | MCI | PHC` (with pipes)

### Menu doesn't appear
- Check callback_query handlers
- Verify InlineKeyboardMarkup syntax
- Check logs for errors

---

## 🎯 Next Steps

After successful testing:
1. Take screenshots
2. Reply: **"DOCTOR BOT CORE READY - Screenshot attached"**
3. Proceed to Step 4: Build X-Ray Request Bot

---

**Bot is ready for testing!** 🚀

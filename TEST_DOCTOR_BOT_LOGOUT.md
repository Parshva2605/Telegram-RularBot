# 🧪 Test Doctor Bot - Logout & Phone Verification

## ⚡ QUICK TEST (3 Steps)

### Step 1: Start Doctor Bot
```bash
python doctor_bot.py
```

### Step 2: Test Logout
```
Telegram → @MediMindDoctorBot

1. /start
2. (If registered) Click "🚪 Logout"
3. Verify: "👋 LOGGED OUT" message
4. /start again to login
```

### Step 3: Test Phone Verification (New User)
```
Telegram → @MediMindDoctorBot (new account)

1. /start
2. Click "📱 Share Phone to Verify"
3. Approve Telegram permission
4. Verify: "✅ Phone verified via Telegram: +91..."
5. Enter name: Dr. Test Kumar
6. Enter MCI: TEST12345
7. Enter PHC: Test PHC
8. Verify: Registration success with verified badge
```

---

## ✅ EXPECTED RESULTS

### Logout Test
```
Before logout:
- Main menu visible
- All buttons work
- Profile accessible

After logout:
- "👋 LOGGED OUT" message
- Session cleared
- Must /start to login again
```

### Phone Verification Test
```
Step 1: Share phone
✅ Phone verified via Telegram: +919876543210

Step 2: Enter name
✅ Name saved: Dr. Test Kumar
🩺 Step 2/3: Enter your MCI Registration Number

Step 3: Enter MCI
✅ MCI saved: TEST12345
🏥 Step 3/3: Enter your PHC name

Step 4: Enter PHC
✅ REGISTRATION SUCCESSFUL

📱 Phone verified via Telegram ✅
👨‍⚕️ Dr. Test Kumar
📱 +919876543210
🩺 MCI: TEST12345
🏥 PHC: Test PHC

🔐 Access Code: ABC12345
```

---

## 🎯 MAIN MENU (Updated)

After login:
```
🎯 DOCTOR MENU

Choose an option:

[📋 My Queue]
[🩻 Analyze Image]
[📋 Old Reports]
[🔐 Regen Code]
[🚪 Logout]        ← NEW!
```

---

## 🐛 TROUBLESHOOTING

### Bot not starting
```bash
# Check if .env.doctor exists
cat .env.doctor

# Should have:
MEDIMIND_DOCTOR_TOKEN=your_token_here
SUPABASE_URL=https://...
SUPABASE_KEY=sb_secret_...
```

### Logout button not visible
- Make sure you're logged in first
- Use `/start` to login
- Check main menu appears

### Phone verification not working
- Use the "📱 Share Phone to Verify" button
- Don't manually send contact
- Approve Telegram permission when asked

---

## 📸 SCREENSHOTS TO TAKE

1. Main menu with logout button
2. Logout confirmation message
3. Phone verification request
4. Registration success with verified badge
5. Step-by-step progress (1/3, 2/3, 3/3)

---

## ✅ SUCCESS CHECKLIST

- [ ] Doctor bot starts without errors
- [ ] Main menu shows logout button
- [ ] Logout clears session
- [ ] Can login again after logout
- [ ] Phone verification button appears for new users
- [ ] Telegram verifies phone number
- [ ] Registration shows step progress (1/3, 2/3, 3/3)
- [ ] Success message shows verified badge
- [ ] Access code generated
- [ ] Main menu appears after registration

---

## 🚀 READY TO TEST

```bash
# Terminal: Start bot
python doctor_bot.py

# Telegram: Test features
/start → Test logout → Test registration
```

That's it! Test the new features now. 🎉

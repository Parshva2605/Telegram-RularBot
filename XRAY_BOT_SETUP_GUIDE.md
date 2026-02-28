# 🤖 MediMind X-Ray Bot Setup Guide

## ✅ Step 1: Create 3 New Telegram Bots

### Bot 1: X-Ray Request Bot (Patient-facing)

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. **Bot Name**: `MediMind Xray Req`
4. **Username**: `@MediMindXrayReqBot` (or similar if taken)
5. **Copy the TOKEN** immediately and save it
6. Send `/setdescription` and paste:
   ```
   Patient X-ray request bot for MediMind Rural. Upload X-ray images and get AI-powered analysis from doctors.
   ```
7. Send `/setcommands` and paste:
   ```
   start - Start X-ray request
   upload - Upload X-ray image
   status - Check X-ray status
   help - Get help
   ```
8. Send `/setuserpic` and upload a medical icon (optional)

### Bot 2: Doctor Bot (Doctor-facing)

1. Send `/newbot` to @BotFather again
2. **Bot Name**: `MediMind Doctor`
3. **Username**: `@MediMindDoctorBot` (or similar if taken)
4. **Copy the TOKEN** immediately and save it
5. Send `/setdescription` and paste:
   ```
   Doctor interface for MediMind Rural. Review X-ray requests, provide AI-assisted diagnosis, and manage patient cases.
   ```
6. Send `/setcommands` and paste:
   ```
   start - Start doctor dashboard
   pending - View pending X-rays
   history - View diagnosis history
   profile - Doctor profile
   help - Get help
   ```

### Bot 3: Backup Bot (Optional)

1. Send `/newbot` to @BotFather again
2. **Bot Name**: `MediMind Rural Xray`
3. **Username**: `@MediMindRuralBotXray` (or similar if taken)
4. **Copy the TOKEN** immediately and save it
5. Same description and commands as Bot 1

---

## 📝 Step 2: Save Tokens to .env.new

Open the `.env.new` file and paste your tokens:

```env
MEDIMIND_XRAY_REQ_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz-PASTE_HERE
MEDIMIND_DOCTOR_TOKEN=9876543210:XYZabcDEFghiJKLmnoQRStuv-PASTE_HERE
MEDIMIND_RURAL_BOT_XRAY_TOKEN=optional_backup_token_here
```

---

## ✅ Verification Checklist

- [ ] Bot 1 (@MediMindXrayReqBot) created
- [ ] Bot 2 (@MediMindDoctorBot) created
- [ ] Bot 3 (optional backup) created
- [ ] All 3 tokens copied
- [ ] Tokens pasted in .env.new
- [ ] Commands set for each bot
- [ ] Descriptions set for each bot

---

## 🚀 Next Steps

After completing this guide:

1. Show Kiro the .env.new file (with tokens masked)
2. Confirm: "3 NEW BOT TOKENS READY"
3. Wait for next prompt to build the X-Ray feature

**DO NOT modify the original bot.py or .env file yet!**

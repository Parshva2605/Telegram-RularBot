# 🤖 MediMind X-Ray Bot Setup - CORRECTED Guide

## 📋 Bot Architecture (Corrected)

### ✅ EXISTING Bot (LIVE - Don't Touch Yet)
- **@MediMindRuralBot** (BOT_TOKEN in .env)
- **Status**: LIVE and working
- **Will add**: "🩻 X-Ray Check" button later (Step 2)
- **DO NOT create this - it already exists!**

### 🆕 NEW Bots to Create (Only 2)

#### Bot 1: Doctor Bot
- **Purpose**: Doctor login, queue management, X-ray analysis
- **For**: Doctors and medical staff

#### Bot 2: X-Ray Request Bot  
- **Purpose**: Patient X-ray submission and status tracking
- **For**: Patients uploading X-rays

---

## 🎯 Step-by-Step: Create 2 NEW Bots

### 1️⃣ Create Doctor Bot

Open Telegram → Search **@BotFather** → Follow these steps:

```
You: /newbot

BotFather: Alright, a new bot. How are we going to call it? Please choose a name for your bot.

You: MediMind Doctor Bot

BotFather: Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.

You: MediMindDoctorBot

BotFather: Done! Congratulations on your new bot. You will find it at t.me/MediMindDoctorBot. You can now add a description...

✅ COPY THE TOKEN IMMEDIATELY! It looks like:
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Set Description:**
```
You: /setdescription

BotFather: Choose a bot to change description.

You: @MediMindDoctorBot

BotFather: Send me the new description for the bot.

You: Doctor X-ray analysis bot for MediMind Rural PHC. Login to review patient X-rays and provide AI-assisted diagnosis.
```

**Set Commands:**
```
You: /setcommands

BotFather: Choose a bot to set commands.

You: @MediMindDoctorBot

BotFather: Send me a list of commands for your bot.

You: 
start - Doctor login
regen_code - Generate new access code
status - Check queue
help - Get help
```

---

### 2️⃣ Create X-Ray Request Bot

```
You: /newbot

BotFather: Alright, a new bot. How are we going to call it?

You: MediMind Xray Request

BotFather: Good. Now let's choose a username for your bot.

You: MediMindXrayReqBot

BotFather: Done! Congratulations on your new bot. You will find it at t.me/MediMindXrayReqBot.

✅ COPY THE TOKEN IMMEDIATELY!
```

**Set Description:**
```
You: /setdescription

BotFather: Choose a bot.

You: @MediMindXrayReqBot

BotFather: Send me the new description.

You: Patient X-ray submission for doctor review. Upload X-ray images and track analysis status.
```

**Set Commands:**
```
You: /setcommands

BotFather: Choose a bot.

You: @MediMindXrayReqBot

BotFather: Send me a list of commands.

You:
start - Start X-ray request
status - Check status
help - Get help
```

---

## 📝 Step 3: Save Tokens to .env.doctor

Open the `.env.doctor` file and paste your tokens:

**Find these lines:**
```env
MEDIMIND_DOCTOR_TOKEN=paste_your_doctor_bot_token_here
MEDIMIND_XRAY_REQ_TOKEN=paste_your_xray_request_bot_token_here
```

**Replace with your actual tokens:**
```env
MEDIMIND_DOCTOR_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
MEDIMIND_XRAY_REQ_TOKEN=9876543210:XYZabcDEFghiJKLmnoQRStuv
```

---

## ✅ Verification Checklist

- [ ] Bot 1: @MediMindDoctorBot created
- [ ] Bot 1: Token copied
- [ ] Bot 1: Description set
- [ ] Bot 1: Commands set (start, regen_code, status, help)
- [ ] Bot 2: @MediMindXrayReqBot created
- [ ] Bot 2: Token copied
- [ ] Bot 2: Description set
- [ ] Bot 2: Commands set (start, status, help)
- [ ] Both tokens pasted in .env.doctor
- [ ] Screenshot taken of BotFather showing both bots

---

## 📸 What to Show Kiro

1. **Screenshot** of @BotFather showing both bots created
2. **Contents of .env.doctor** with tokens masked like this:
   ```
   MEDIMIND_DOCTOR_TOKEN=****************************xxGk
   MEDIMIND_XRAY_REQ_TOKEN=****************************yyyy
   ```
3. Say: **"2 NEW BOTS READY - tokens in .env.doctor"**

---

## 🚀 After Completion

Kiro will:
1. Commit .env.doctor to git
2. Push to GitHub
3. Proceed to Step 2: Build X-Ray feature code

**The existing @MediMindRuralBot stays LIVE and unchanged!** 🔒

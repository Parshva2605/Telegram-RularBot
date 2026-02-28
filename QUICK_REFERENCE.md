# 🎯 Quick Reference - Bot Creation

## What You Need to Do NOW

### Open Telegram → @BotFather

**Create Bot 1:**
```
/newbot
Name: MediMind Doctor Bot
Username: @MediMindDoctorBot
→ COPY TOKEN
```

**Create Bot 2:**
```
/newbot
Name: MediMind Xray Request
Username: @MediMindXrayReqBot
→ COPY TOKEN
```

### Paste Tokens in .env.doctor

Replace these lines:
```env
MEDIMIND_DOCTOR_TOKEN=paste_your_doctor_bot_token_here
MEDIMIND_XRAY_REQ_TOKEN=paste_your_xray_request_bot_token_here
```

### Show Kiro

1. Screenshot of both bots in @BotFather
2. .env.doctor with tokens (masked: ****xxxx)
3. Say: "2 NEW BOTS READY"

---

## Bot Summary

| Bot | Username | Purpose | Token Variable |
|-----|----------|---------|----------------|
| **EXISTING** | @MediMindRuralBot | Live patient services | BOT_TOKEN (don't touch) |
| **NEW #1** | @MediMindDoctorBot | Doctor X-ray review | MEDIMIND_DOCTOR_TOKEN |
| **NEW #2** | @MediMindXrayReqBot | Patient X-ray upload | MEDIMIND_XRAY_REQ_TOKEN |

---

**Full guide:** See `BOT_SETUP_GUIDE_CORRECTED.md`

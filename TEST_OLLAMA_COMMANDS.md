# 🧪 Quick Test Commands - Ollama VLM

## 🚀 Quick Start (Copy-Paste)

```bash
# 1. Start Ollama server (in background)
ollama serve &

# 2. Pull models (one-time setup)
ollama pull llava-llama3:8b
ollama pull llava:13b
ollama pull mashriram/sarvam-1

# 3. Install dependencies
pip install -r requirements_doctor.txt

# 4. Stop duplicate bot instances
ps aux | grep doctor_bot
# Then kill any running instances: kill <PID>

# 5. Start doctor bot
python doctor_bot.py
```

---

## 📱 Test in Telegram

1. Open `@MediMindDoctorBot`
2. Send `/start`
3. Share phone number
4. Register: `Dr. Test | TEST123 | Test PHC`
5. Click "🩻 Analyze Image"
6. Select "🫁 X-ray"
7. Choose mode (Fast/Detailed/14-Diseases)
8. Upload chest X-ray image
9. Wait for AI analysis

---

## ✅ What to Screenshot

Take screenshot showing:
- Real VLM output (not stub text like "Normal lungs, no acute findings")
- Should show detailed medical analysis
- For 14-diseases mode: Should show Hindi translation
- Timestamp showing it's real-time analysis

---

## 🔍 Verify Real Ollama (Not Stubs)

### ❌ OLD STUB OUTPUT:
```
⚡ FAST MODE: Normal lungs, no acute findings.
```

### ✅ NEW REAL OUTPUT:
```
⚡ FAST ANALYSIS:

The chest radiograph demonstrates bilateral lung fields with normal 
vascular markings. The cardiac silhouette appears within normal limits.
No focal consolidation, pleural effusion, or pneumothorax is identified...
```

---

## 🐛 Common Issues

### "Connection refused"
```bash
# Start Ollama first
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull llava:13b
```

### "Conflict: terminated by other getUpdates"
```bash
# Find and kill duplicate processes
ps aux | grep doctor_bot
kill <PID>
```

### Bot starts but no response
- Check Ollama is running: `ps aux | grep ollama`
- Check models are installed: `ollama list`
- Check bot logs for errors

---

## 📊 Model Sizes

- `llava-llama3:8b` → ~5GB download, 6GB VRAM
- `llava:13b` → ~8GB download, 9GB VRAM
- `mashriram/sarvam-1` → ~3GB download, 4GB VRAM

Your RTX 3070 (8GB VRAM) can run Fast mode easily, Detailed mode with care.

---

## 🎯 Success Criteria

- [ ] Ollama server running
- [ ] Models downloaded
- [ ] Bot starts without errors
- [ ] Can upload X-ray image
- [ ] Gets REAL AI analysis (not stub text)
- [ ] Analysis takes 10-30 seconds (real inference time)
- [ ] Screenshot shows detailed medical findings
- [ ] Hindi translation works (14-diseases mode)

---

## 📝 After Testing

Once you confirm real Ollama output, say:

**"OLLAMA VLM READY - Real AI screenshot"**

And share screenshot showing the actual VLM analysis output.

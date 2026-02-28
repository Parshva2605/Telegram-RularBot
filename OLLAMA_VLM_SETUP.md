# 🩻 Ollama VLM Integration - Setup & Testing Guide

## ✅ COMPLETED: Real Ollama VLM Integration

All stub functions have been replaced with **REAL RTX 3070 Ollama calls**:
- ⚡ Fast mode: `llava-llama3:8b` (6GB VRAM)
- 🔍 Detailed mode: `llava:13b` (9GB VRAM)  
- 🇮🇳 Hindi translation: `mashriram/sarvam-1`
- 🎯 14-disease: DL model stub + VLM reasoning + Hindi

---

## 📦 Step 1: Install Dependencies

```bash
pip install -r requirements_doctor.txt
```

This installs:
- `requests==2.31.0`
- `pillow==10.0.0`
- `ollama==0.1.7`

---

## 🤖 Step 2: Start Ollama Server

Run Ollama in background:

```bash
ollama serve &
```

Or in separate terminal:
```bash
ollama serve
```

---

## 📥 Step 3: Pull Required Models

```bash
# Fast mode (6GB VRAM)
ollama pull llava-llama3:8b

# Detailed mode (9GB VRAM)
ollama pull llava:13b

# Hindi translation (optional, ~4GB VRAM)
ollama pull mashriram/sarvam-1
```

**Note:** If `mashriram/sarvam-1` is not available, Hindi translation will show error message but other modes will work fine.

---

## 🧪 Step 4: Test Doctor Bot

1. **Stop any running instances:**
   ```bash
   # Find and kill duplicate processes
   ps aux | grep doctor_bot
   kill <PID>
   ```

2. **Start doctor bot:**
   ```bash
   python doctor_bot.py
   ```

3. **Test in Telegram:**
   - Open `@MediMindDoctorBot`
   - Send `/start`
   - Share phone → Register profile
   - Click "🩻 Analyze Image"
   - Select "🫁 X-ray"
   - Choose mode:
     - ⚡ FAST (llava-llama3:8b) - Quick analysis
     - 🔍 DETAILED (llava:13b) - Full report with ICD10
     - 🎯 14-DISEASES - DL scan + VLM + Hindi
   - Upload a chest X-ray image
   - Wait for AI analysis (10-30 seconds depending on mode)

---

## 📸 Expected Output Examples

### ⚡ Fast Mode:
```
⚡ FAST ANALYSIS:

The chest X-ray shows normal lung fields with no acute findings. 
Heart size is within normal limits. No pleural effusion detected...
```

### 🔍 Detailed Mode:
```
🔍 DETAILED REPORT:

1. Findings:
   • Mild cardiomegaly (ICD10: I51.7)
   • Cardiothoracic ratio: 0.52
   • Lung fields clear bilaterally

2. Risk Level: MEDIUM

3. Next Steps:
   • ECG evaluation
   • Blood pressure monitoring
   • Follow-up chest X-ray in 3 months

4. Medications (List A/B):
   • Consider ACE inhibitors if hypertensive
   • Beta-blockers if indicated
```

### 🎯 14-Diseases Mode:
```
🎯 14-DISEASES + VLM ANALYSIS:

📊 DL SCAN RESULTS:
• Pneumonia: 92%
• Cardiomegaly: 78%
• Effusion: 65%

🔍 AI CLINICAL REPORT:
Based on the deep learning detection of pneumonia (92% confidence),
clinical findings suggest bacterial pneumonia. ICD10: J18.9...

🇮🇳 HINDI (Patient):
फेफड़ों में संक्रमण (निमोनिया) पाया गया है। दिल का आकार बड़ा है...

---
[📝 EDIT] [✅ PDF & SEND]
```

---

## ⚠️ Troubleshooting

### Error: "Connection refused" or "Ollama not running"
**Solution:** Start Ollama server first:
```bash
ollama serve
```

### Error: "Model not found: llava:13b"
**Solution:** Pull the model:
```bash
ollama pull llava:13b
```

### Error: "Conflict: terminated by other getUpdates"
**Solution:** Stop duplicate bot instances:
```bash
ps aux | grep doctor_bot
kill <PID>
```

### Hindi translation shows error
**Solution:** This is optional. If `mashriram/sarvam-1` is not available, the bot will show an error message but continue working. You can:
- Try alternative model: `ollama pull sarvam/sarvam-1`
- Or skip Hindi translation (other modes work fine)

---

## 🎯 What Changed from Stubs

### Before (Stubs):
```python
def vlm_fast(image_path):
    return "⚡ FAST MODE: Normal lungs, no acute findings."
```

### After (Real Ollama):
```python
def vlm_fast(image_path):
    img_b64 = prepare_image_b64(image_path)
    response = ollama.chat(model='llava-llama3:8b', messages=[
        {
            'role': 'user',
            'content': 'Analyze this medical X-ray...',
            'images': [img_b64]
        }
    ])
    return f"⚡ FAST ANALYSIS:\n{response['message']['content']}"
```

---

## 📊 GPU Requirements

- **Fast mode:** 6GB VRAM (llava-llama3:8b)
- **Detailed mode:** 9GB VRAM (llava:13b)
- **14-diseases mode:** 9GB VRAM (llava:13b) + DL model
- **Hindi translation:** 4GB VRAM (sarvam-1)

Your RTX 3070 (8GB VRAM) can run:
- ✅ Fast mode (6GB)
- ⚠️ Detailed mode (9GB - may need to close other apps)
- ✅ 14-diseases without Hindi (6GB DL + VLM)

---

## ✅ Testing Checklist

- [ ] Ollama server running (`ollama serve`)
- [ ] Models pulled (llava:13b, llava-llama3:8b)
- [ ] Dependencies installed (`pip install -r requirements_doctor.txt`)
- [ ] No duplicate bot instances running
- [ ] Doctor bot starts without errors
- [ ] Can register with phone number
- [ ] Can select X-ray → Fast mode
- [ ] Can upload image and get AI analysis
- [ ] Screenshot of real VLM output (not stub text)

---

## 🚀 Next Steps (After Testing)

Once you verify real Ollama output:

```bash
# Update requirements with exact versions
pip freeze > requirements_doctor.txt

# Commit the changes
git add doctor_bot.py requirements_doctor.txt OLLAMA_VLM_SETUP.md
git commit -m "Step6 MAJOR: Real Ollama VLM (llava13b + sarvam1 Hindi)"
git push
```

---

## 📝 Notes

- The 14-disease DL model is still a stub (placeholder confidence scores)
- Next prompt will integrate your actual .onnx model
- VLM reasoning and Hindi translation are now REAL
- Temp files are automatically cleaned up after analysis
- Error messages guide users to fix Ollama issues

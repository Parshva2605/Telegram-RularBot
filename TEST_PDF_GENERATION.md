# 🧪 Test PDF Generation - Quick Guide

## ⚡ QUICK TEST (2 Methods)

### Method 1: Standalone Test (Fastest)

```bash
# Generate test PDF
python report_generator.py

# Check output
ls reports/test_report.pdf

# Open PDF to verify
start reports/test_report.pdf  # Windows
open reports/test_report.pdf   # Mac
xdg-open reports/test_report.pdf  # Linux
```

**Expected output:**
```
Generating test PDF...
✅ PDF generated: reports/test_report.pdf
File size: 3711 bytes
```

### Method 2: Full Workflow Test (Doctor Bot)

```bash
# Start doctor bot
python doctor_bot.py
```

**In Telegram (@MediMindDoctorBot):**
```
1. /start
2. Click "🩻 Analyze Image"
3. Click "🫁 X-ray"
4. Click "🔍 DETAILED (llava:13b)"
5. Upload X-ray image
6. Wait for analysis (30-60 seconds)
7. Click "📝 Edit Report"
8. Type: "Patient examined. Treatment prescribed."
9. Click "✅ Generate PDF"
10. Receive PDF in chat
```

---

## ✅ EXPECTED RESULTS

### Standalone Test
- ✅ PDF file created in `reports/` folder
- ✅ File size ~3-5 KB
- ✅ PDF opens without errors
- ✅ Contains all sections

### Doctor Bot Test
- ✅ Analysis completes successfully
- ✅ Action buttons appear
- ✅ Edit workflow works
- ✅ PDF generated message
- ✅ PDF sent to Telegram
- ✅ PDF can be downloaded

---

## 📄 PDF CONTENTS TO VERIFY

### Page 1: Header
```
MEDIMIND AI X-RAY REPORT
AI-Assisted Medical Decision Support System
```

### Sections
1. ✅ PATIENT INFORMATION
   - Name, Age, Village, Symptoms, Date

2. ✅ AI SCAN RESULTS
   - Diseases detected with percentages

3. ✅ AI CLINICAL ANALYSIS
   - Detailed findings
   - ICD-10 codes
   - Recommendations

4. ✅ DOCTOR'S ASSESSMENT
   - Doctor name, MCI, PHC
   - Doctor's notes

5. ✅ HINDI REPORT
   - Placeholder (Unicode support pending)

6. ✅ DISCLAIMER
   - MCI compliance notice

### Footer
```
Generated: 28/02/2026 15:30 | MCI Decision Support Only | ...
Page 1
```

---

## 🐛 TROUBLESHOOTING

### "fpdf2 not installed"
```bash
pip install fpdf2
```

### "reports folder not found"
```bash
mkdir reports
```

### "Permission denied"
```bash
# Windows: Run as administrator
# Linux/Mac: Check folder permissions
chmod 755 reports
```

### PDF shows warnings
- Deprecation warnings are normal
- PDF still generates correctly
- Can be ignored for now

### Ollama not running (Doctor Bot test)
```bash
# Start Ollama
ollama serve

# Pull models
ollama pull llava:13b
ollama pull llava-llama3:8b
```

### Bot not responding
- Check `.env.doctor` file exists
- Check `MEDIMIND_DOCTOR_TOKEN` is set
- Check internet connection

---

## 📸 SCREENSHOTS TO TAKE

1. **Standalone test output** - Terminal showing success
2. **PDF file in folder** - File explorer showing PDF
3. **PDF opened** - PDF viewer showing report
4. **Telegram analysis** - Bot showing analysis results
5. **Action buttons** - Edit/Generate PDF buttons
6. **Edit workflow** - Doctor entering notes
7. **PDF in Telegram** - PDF sent to chat
8. **PDF downloaded** - Downloaded PDF opened

---

## ✅ SUCCESS CHECKLIST

### Standalone Test
- [ ] `python report_generator.py` runs without errors
- [ ] PDF file created in `reports/` folder
- [ ] PDF opens in viewer
- [ ] All sections visible
- [ ] Header and footer present
- [ ] No corruption errors

### Doctor Bot Test
- [ ] Bot starts successfully
- [ ] Can analyze X-ray image
- [ ] Analysis completes
- [ ] Action buttons appear
- [ ] Edit report works
- [ ] Notes saved
- [ ] PDF generates
- [ ] PDF sent to Telegram
- [ ] PDF can be downloaded
- [ ] Temp files cleaned up

---

## 🎯 SAMPLE TEST DATA

### Test Report Data
```python
{
    'patient_name': 'Ramesh Patel',
    'age': 45,
    'village': 'Anklav',
    'symptoms': 'Cough for 5 days, chest pain',
    'diseases_detected': [
        'Pneumonia (92%)',
        'Cardiomegaly (78%)',
        'Effusion (65%)'
    ],
    'ai_report': 'Pneumonia detected in right lower lobe...',
    'doctor_notes': 'Treatment prescribed: Amoxicillin 625mg TDS',
    'doctor_name': 'Dr. Rajesh Shah',
    'doctor_mci': 'GJMC12345',
    'doctor_phc': 'Anklav PHC'
}
```

---

## 🚀 READY TO TEST

**Fastest way:**
```bash
python report_generator.py
start reports/test_report.pdf
```

**Full workflow:**
```bash
python doctor_bot.py
# Then test in Telegram
```

That's it! Test the PDF generation now. 📄✨

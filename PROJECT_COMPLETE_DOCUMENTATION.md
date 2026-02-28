# MediMind Rural Healthcare System - Complete Documentation

**Version:** 2.0  
**Last Updated:** February 28, 2026  
**Status:** Production Ready

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation & Setup](#installation--setup)
5. [User Guides](#user-guides)
6. [Admin Panel](#admin-panel)
7. [Doctor Bot System](#doctor-bot-system)
8. [X-Ray Request System](#x-ray-request-system)
9. [Contact Patient Feature](#contact-patient-feature)
10. [Reports Management](#reports-management)
11. [Database Schema](#database-schema)
12. [Troubleshooting](#troubleshooting)

---

## System Overview

MediMind is a comprehensive rural healthcare management system that connects patients, health workers, doctors, and administrators through Telegram bots and a web dashboard.

### Core Components

1. **Patient Bot** (@MediMindRuralBot) - Patient interactions
2. **Doctor Bot** (@MediMindDoctorBot) - Doctor workflow
3. **Admin Dashboard** - Web-based management interface
4. **X-Ray Analysis System** - AI-powered medical imaging
5. **Report Generation** - Bilingual PDF reports (English + Hindi)

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     MediMind System                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Patient Bot  │  │ Doctor Bot   │  │ Admin Panel  │    │
│  │ (Telegram)   │  │ (Telegram)   │  │ (Streamlit)  │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                  │                  │             │
│         └──────────────────┴──────────────────┘             │
│                            │                                │
│                    ┌───────▼────────┐                       │
│                    │   Supabase DB  │                       │
│                    └───────┬────────┘                       │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         │                  │                  │             │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐    │
│  │ Ollama AI    │  │ File Storage │  │ Telegram API │    │
│  │ (Local)      │  │ (Local)      │  │ (Cloud)      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Backend:** Python 3.8+
- **Bots:** python-telegram-bot
- **Dashboard:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **AI:** Ollama (llava, sarvam-1)
- **PDF:** ReportLab
- **Storage:** Local file system

---

## Features

### Patient Bot Features

✅ Emergency reporting with location  
✅ Appointment booking  
✅ Medicine reminders  
✅ Maternal health tracking  
✅ AI health chat  
✅ Government schemes information  
✅ X-ray request submission  
✅ Receive reports from doctors  

### Doctor Bot Features

✅ Secure login with access code  
✅ View pending X-ray requests  
✅ AI-powered X-ray analysis  
✅ Generate bilingual PDF reports  
✅ Contact patients (voice/text)  
✅ Personal dashboard  
✅ Request notifications  
✅ Logout functionality  

### Admin Panel Features

✅ Health worker management  
✅ Emergency monitoring  
✅ Appointment tracking  
✅ Reminder management  
✅ Maternal health records  
✅ Doctor management  
✅ X-ray request monitoring  
✅ Reports management  
✅ Statistics & analytics  

---

## Installation & Setup

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Ollama for AI
ollama --version

# Git
git --version
```

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd CVMU-chatbot
```

### Step 2: Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install Ollama models
ollama pull llava-llama3:8b
ollama pull llava:13b
ollama pull mashriram/sarvam-1
```

### Step 3: Configure Environment

Create `.env` file:
```env
BOT_TOKEN=your_patient_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_ID=your_telegram_id
```

Create `.env.doctor` file:
```env
MEDIMIND_DOCTOR_TOKEN=your_doctor_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Create `dashboard/.env` file:
```env
BOT_TOKEN=your_patient_bot_token
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
ADMIN_ID=your_telegram_id
```

### Step 4: Setup Database

Run SQL scripts in Supabase:
```bash
# 1. Create tables
database/schema_xray.sql

# 2. Add patient telegram ID field
database/add_patient_telegram_id.sql

# 3. (Optional) Create message tracking
database/create_doctor_patient_messages.sql

# 4. Insert test doctor
database/insert_test_doctor.sql
```

### Step 5: Create Folders

```bash
mkdir xray_images
mkdir reports
mkdir fonts
```

### Step 6: Download Fonts

Download Noto Sans Devanagari font for Hindi support:
- Place in `fonts/NotoSansDevanagari-Regular.ttf`

### Step 7: Start Services

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Patient Bot
python bot.py

# Terminal 3: Start Doctor Bot
python doctor_bot.py

# Terminal 4: Start Admin Dashboard
streamlit run dashboard/app.py
```

---

## User Guides

### For Patients

1. **Start Bot:** Open @MediMindRuralBot in Telegram
2. **Register:** Share contact to register
3. **Submit X-Ray:** 
   - Click "🩻 X-Ray Request"
   - Fill form (name, age, village, symptoms)
   - Upload X-ray image
   - Select doctor
4. **Receive Report:** Doctor will contact you with results

### For Doctors

1. **Register:** Open @MediMindDoctorBot
2. **Login:** Use phone + access code
3. **View Requests:** Click "📥 Requests"
4. **Analyze X-Ray:**
   - Click "🩻 Analyze This X-Ray"
   - Select analysis mode
   - Review AI results
   - Add your notes
5. **Generate Report:** Click "Generate PDF"
6. **Contact Patient:** 
   - Click "📞 Contact Patient"
   - Send voice note OR text message
   - Text auto-translates to Hindi

### For Admins

1. **Access Dashboard:** http://localhost:8501
2. **Manage Doctors:** Add/edit/delete doctors
3. **Monitor X-Rays:** View all requests, send reminders
4. **View Reports:** Download and export reports
5. **Analytics:** Track performance metrics

---

## Admin Panel

### Pages Overview

1. **Home** - Statistics dashboard
2. **👥 Health Workers** - Manage health workers
3. **🚨 Emergencies** - Monitor emergencies
4. **📅 Appointments** - Track appointments
5. **💊 Reminders** - Medicine reminders
6. **👶 Maternal Health** - Pregnancy tracking
7. **🧠 AI Chat** - Chat logs
8. **⚙️ CRUD Operations** - Database management
9. **🌿 Govt Schemes** - Schemes information
10. **🆘 Issues** - Issue tracking
11. **👨‍⚕️ Doctor Dashboard** - Doctor login portal
12. **👨‍⚕️ Manage Doctors** - Doctor management
13. **🩻 X-Ray Requests** - X-ray monitoring
14. **📄 Reports** - Reports management

### Running Dashboard

```bash
# IMPORTANT: Run from project root
cd "D:\CVMU - chatbot"
streamlit run dashboard/app.py
```

### Key Features

**Doctor Management:**
- Add new doctors with credentials
- Generate access codes
- View doctor statistics
- Filter and search

**X-Ray Monitoring:**
- View all requests
- Filter by doctor/date/status
- Send reminders to doctors
- Send custom messages
- Change request status
- Delete requests
- Bulk actions

**Reports Management:**
- View all generated reports
- Filter by doctor/date
- Download PDFs
- Export to CSV
- Doctor performance stats

---

## Doctor Bot System

### Registration Flow

```
Doctor opens @MediMindDoctorBot
         ↓
Click /start
         ↓
Share phone contact
         ↓
Enter name, PHC, MCI registration
         ↓
Receive 8-character access code
         ↓
Use code to login on dashboard
```

### Main Menu

- **📥 Requests** - View pending X-ray requests
- **📊 My Dashboard** - Personal statistics
- **🔍 Analyze** - Upload and analyze new images
- **📋 Old Reports** - View reviewed cases
- **🔐 Regenerate Code** - Get new access code
- **🚪 Logout** - Logout from bot

### X-Ray Analysis Modes

1. **⚡ FAST** - llava-llama3:8b (quick analysis)
2. **🔍 DETAILED** - llava:13b (comprehensive)
3. **🎯 14-DISEASES** - Custom model (specific diseases)

### Report Generation

1. AI analyzes X-ray
2. Doctor reviews results
3. Doctor adds notes
4. Click "Generate PDF"
5. Report saved to system
6. Contact patient button appears

### Contact Patient Options

**🎤 Voice Note:**
- Record voice in Telegram
- Forwarded to patient with caption
- Patient receives: "🎤 Voice Message from Dr. [Name]"

**💬 Text Message:**
- Type message in English
- Auto-translates to Hindi using Ollama
- Patient receives both versions
- Format: English + हिंदी

---

## X-Ray Request System

### Complete Workflow

```
PATIENT SIDE:
1. Patient opens @MediMindRuralBot
2. Clicks "🩻 X-Ray Request"
3. Fills form: Name, Age, Village, Symptoms
4. Uploads X-ray image (photo)
5. Selects doctor from list
6. Request submitted

         ↓

SYSTEM:
- Image saved to xray_images/ folder
- Request stored in database
- Notification sent to doctor

         ↓

DOCTOR SIDE:
1. Doctor receives notification in @MediMindDoctorBot
2. Clicks "📥 Requests"
3. Sees pending requests with images
4. Clicks "🩻 Analyze This X-Ray"
5. Selects analysis mode
6. Reviews AI results
7. Adds notes
8. Generates PDF report
9. Contacts patient

         ↓

PATIENT RECEIVES:
- Voice message OR text message from doctor
- Instructions and guidance
```

### Image Storage

**Location:** `xray_images/` folder  
**Format:** `xray_{user_id}_{file_id}.jpg`  
**Database:** Stores local file path (not Telegram file_id)

### Database Fields

```sql
xray_requests (
    id BIGINT PRIMARY KEY,
    patient_name TEXT,
    age INT,
    village TEXT,
    symptoms TEXT,
    image_url TEXT,              -- Local file path
    doctor_phone TEXT,
    patient_telegram_id BIGINT,  -- For contact feature
    status TEXT,                 -- pending/reviewed/sent/cancelled
    report_pdf_url TEXT,         -- PDF file path
    ai_report TEXT,
    doctor_notes TEXT,
    created_at TIMESTAMPTZ,
    reviewed_at TIMESTAMPTZ
)
```

---

## Contact Patient Feature

### Privacy Compliance

✅ Reports NOT automatically sent to patients  
✅ Doctor has full control  
✅ Medical law compliance  
✅ Audit trail (optional)  

### Implementation

**After Report Generation:**
```
✅ REPORT GENERATED SUCCESSFULLY

👤 Patient: Ramesh Patel
📄 Report saved to system
💾 File: report_20260228_Ramesh_Patel.pdf

📋 Status: Request marked as reviewed

🔒 Privacy: Report NOT sent to patient (medical compliance)

👉 Click 'Contact Patient' to communicate

[📞 Contact Patient]  [📥 Download Report]  [🔙 Main Menu]
```

**Communication Options:**

1. **Voice Note:**
   - Doctor records in Telegram
   - Bot forwards to patient
   - Caption: "🎤 Voice Message from Dr. [Name]"

2. **Text Message:**
   - Doctor types in English
   - Ollama translates to Hindi
   - Patient receives both versions
   - Format: English + हिंदी

### Translation System

**Model:** mashriram/sarvam-1 (Hindi translation)

**Example:**
```
Doctor types: "Please take rest and drink water"

Patient receives:
📨 Message from Dr. Rajesh Shah

English:
Please take rest and drink water.

हिंदी:
कृपया आराम करें और पानी पिएं।

━━━━━━━━━━━━━━━━━━━━
🏥 Please follow your doctor's instructions
```

---

## Reports Management

### Admin Reports Page

**Location:** Dashboard → 📄 Reports

**Features:**
- View all reports from all doctors
- Statistics (Total, Today, Last 7 Days, Last 30 Days)
- Filter by doctor
- Filter by date range
- Search by patient name
- Download PDFs
- Doctor performance table
- Export to CSV
- Monthly report generation

### Doctor Dashboard - My Reports

**Location:** Dashboard → 👨‍⚕️ Doctor Dashboard → Login → 📊 My Reports

**Features:**
- View ONLY your own reports
- Search by patient name
- Filter by date
- Download PDFs
- View X-ray images
- Turnaround time tracking
- Personal workspace

### Report Structure

**PDF Contains:**
- Patient information (name, age, village, symptoms)
- Doctor information (name, PHC, MCI registration)
- AI analysis results
- Doctor's notes
- Bilingual summary (English + Hindi)
- Date and signatures

**File Naming:** `report_YYYYMMDD_HHMMSS_PatientName.pdf`  
**Storage:** `reports/` folder

---

## Database Schema

### Main Tables

**doctors**
```sql
CREATE TABLE doctors (
    id BIGSERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE,
    phone TEXT UNIQUE,
    name TEXT,
    phc TEXT,
    mci_reg TEXT,
    access_code TEXT,
    rating DECIMAL DEFAULT 0,
    total_cases INT DEFAULT 0,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**xray_requests**
```sql
CREATE TABLE xray_requests (
    id BIGSERIAL PRIMARY KEY,
    patient_name TEXT,
    age INT,
    village TEXT,
    symptoms TEXT,
    image_url TEXT,
    doctor_phone TEXT,
    patient_telegram_id BIGINT,
    status TEXT DEFAULT 'pending',
    report_pdf_url TEXT,
    ai_report TEXT,
    doctor_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at TIMESTAMPTZ,
    consent_time TIMESTAMPTZ
);
```

**doctor_patient_messages** (Optional)
```sql
CREATE TABLE doctor_patient_messages (
    id BIGSERIAL PRIMARY KEY,
    request_id BIGINT,
    doctor_phone TEXT,
    doctor_telegram_id BIGINT,
    patient_telegram_id BIGINT,
    message_type TEXT,
    message_text TEXT,
    message_text_hindi TEXT,
    voice_file_id TEXT,
    voice_duration INT,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Troubleshooting

### Common Issues

**1. Database Connection Failed**
- **Cause:** Environment variables not loaded
- **Solution:** Run dashboard from project root: `streamlit run dashboard/app.py`

**2. Ollama Connection Error**
- **Cause:** Ollama not running
- **Solution:** Run `ollama serve` in separate terminal

**3. Image Not Found**
- **Cause:** Image path incorrect
- **Solution:** Verify `xray_images/` folder exists and has correct permissions

**4. PDF Not Generated**
- **Cause:** Font file missing
- **Solution:** Download Noto Sans Devanagari font to `fonts/` folder

**5. Doctor Login Failed**
- **Cause:** Invalid credentials
- **Solution:** Use test credentials: `+919876543210` / `TEST1234`

**6. Notification Not Received**
- **Cause:** Doctor not registered
- **Solution:** Doctor must use /start in @MediMindDoctorBot first

**7. Translation Not Working**
- **Cause:** sarvam-1 model not loaded
- **Solution:** Run `ollama pull mashriram/sarvam-1`

### Test Credentials

**Test Doctor:**
- Phone: `+919876543210`
- Access Code: `TEST1234`
- Name: Dr. Test Doctor
- PHC: Test PHC

---

## File Structure

```
CVMU-chatbot/
├── bot.py                          # Patient bot
├── doctor_bot.py                   # Doctor bot
├── report_generator.py             # PDF generation
├── .env                            # Patient bot config
├── .env.doctor                     # Doctor bot config
├── requirements.txt                # Python dependencies
├── README.md                       # Project readme
├── start.md                        # Quick start guide
│
├── dashboard/                      # Admin panel
│   ├── app.py                      # Main dashboard
│   ├── .env                        # Dashboard config
│   ├── supabase_wrapper.py         # Database wrapper
│   ├── telegram_helper.py          # Telegram integration
│   └── pages/                      # Dashboard pages
│       ├── 1_👥_Health_Workers.py
│       ├── 10_👨‍⚕️_Doctor_Dashboard.py
│       ├── 11_👨‍⚕️_Manage_Doctors.py
│       ├── 12_🩻_X-Ray_Requests.py
│       ├── 13_📄_Reports.py
│       └── ...
│
├── database/                       # SQL scripts
│   ├── schema_xray.sql
│   ├── add_patient_telegram_id.sql
│   ├── create_doctor_patient_messages.sql
│   └── insert_test_doctor.sql
│
├── xray_images/                    # X-ray storage
├── reports/                        # PDF storage
└── fonts/                          # Font files
    └── NotoSansDevanagari-Regular.ttf
```

---

## Quick Start Commands

```bash
# 1. Navigate to project
cd "D:\CVMU - chatbot"

# 2. Start Ollama
ollama serve

# 3. Start Patient Bot (new terminal)
python bot.py

# 4. Start Doctor Bot (new terminal)
python doctor_bot.py

# 5. Start Dashboard (new terminal)
streamlit run dashboard/app.py
```

---

## Support & Maintenance

### Regular Tasks

- Monitor database size
- Clean old X-ray images (optional)
- Backup database regularly
- Update Ollama models
- Check bot uptime

### Performance Optimization

- Use database indexes
- Implement pagination for large datasets
- Cache frequently accessed data
- Optimize image storage

### Security

- Keep access codes secure
- Rotate Telegram bot tokens periodically
- Use environment variables for secrets
- Implement rate limiting
- Regular security audits

---

## Version History

**v2.0** (February 2026)
- Added Contact Patient feature
- Added Reports management
- Added bilingual support
- Fixed image sharing between bots
- Enhanced notification system

**v1.0** (Initial Release)
- Patient bot with basic features
- Doctor bot with X-ray analysis
- Admin dashboard
- Database integration

---

## Credits

**Developed by:** MediMind Team  
**AI Models:** Ollama (llava, sarvam-1)  
**Database:** Supabase  
**Framework:** Python, Streamlit, python-telegram-bot

---

## License

[Your License Here]

---

**End of Documentation**

For the latest updates and detailed guides, refer to `start.md` and individual feature documentation.

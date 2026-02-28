# MediMind Rural Healthcare System

A comprehensive Telegram-based healthcare management system for rural areas, featuring AI-powered X-ray analysis, bilingual report generation, and real-time doctor-patient communication.

## 🌟 Features

### Patient Bot (@MediMindRuralBot)
- 🚨 Emergency reporting with location
- 📅 Appointment booking
- 💊 Medicine reminders
- 👶 Maternal health tracking
- 🧠 AI health chat
- 🩻 X-ray request submission
- 📄 Receive medical reports

### Doctor Bot (@MediMindDoctorBot)
- 🔐 Secure login with access codes
- 📥 View pending X-ray requests
- 🤖 AI-powered X-ray analysis (Ollama)
- 📄 Generate bilingual PDF reports (English + Hindi)
- 📞 Contact patients (voice/text with auto-translation)
- 📊 Personal dashboard
- 🔔 Real-time notifications

### Admin Dashboard (Streamlit)
- 👥 Health worker management
- 🚨 Emergency monitoring
- 📅 Appointment tracking
- 👨‍⚕️ Doctor management
- 🩻 X-ray request monitoring
- 📄 Reports management
- 📊 Statistics & analytics

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Ollama (for AI)
ollama --version
```

### Installation

```bash
# 1. Clone repository
git clone <repository-url>
cd CVMU-chatbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Install Ollama models
ollama pull llava-llama3:8b
ollama pull llava:13b
ollama pull mashriram/sarvam-1

# 4. Setup environment variables
# Create .env, .env.doctor, and dashboard/.env files
# (See PROJECT_COMPLETE_DOCUMENTATION.md for details)

# 5. Setup database
# Run SQL scripts in database/ folder on Supabase

# 6. Create folders
mkdir xray_images reports fonts

# 7. Download Hindi font
# Place NotoSansDevanagari-Regular.ttf in fonts/ folder
```

### Running the System

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

## 📚 Documentation

- **Complete Documentation:** [PROJECT_COMPLETE_DOCUMENTATION.md](PROJECT_COMPLETE_DOCUMENTATION.md)
- **Quick Start Guide:** [start.md](start.md)

## 🏗️ Architecture

```
Patient Bot (Telegram) ──┐
                         ├──> Supabase Database
Doctor Bot (Telegram) ───┤
                         │
Admin Dashboard (Web) ───┘
         │
         ├──> Ollama AI (Local)
         ├──> File Storage (Local)
         └──> Telegram API
```

## 🔧 Technology Stack

- **Backend:** Python 3.8+
- **Bots:** python-telegram-bot
- **Dashboard:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **AI:** Ollama (llava, sarvam-1)
- **PDF:** ReportLab
- **Translation:** Ollama sarvam-1 (Hindi)

## 📁 Project Structure

```
CVMU-chatbot/
├── bot.py                      # Patient bot
├── doctor_bot.py               # Doctor bot
├── report_generator.py         # PDF generation
├── dashboard/                  # Admin panel
│   ├── app.py
│   ├── pages/
│   │   ├── 10_👨‍⚕️_Doctor_Dashboard.py
│   │   ├── 11_👨‍⚕️_Manage_Doctors.py
│   │   ├── 12_🩻_X-Ray_Requests.py
│   │   └── 13_📄_Reports.py
│   └── supabase_wrapper.py
├── database/                   # SQL scripts
├── xray_images/               # X-ray storage
├── reports/                   # PDF storage
└── fonts/                     # Font files
```

## 🔑 Key Features

### X-Ray Request System
1. Patient submits X-ray through bot
2. Doctor receives notification
3. AI analyzes X-ray (3 modes: Fast, Detailed, 14-Diseases)
4. Doctor reviews and adds notes
5. Bilingual PDF report generated
6. Doctor contacts patient with results

### Contact Patient Feature
- **Voice Notes:** Record and send voice messages
- **Text Messages:** Auto-translate English to Hindi
- **Privacy Compliant:** Reports not auto-sent to patients
- **Doctor Control:** Full control over communication

### Reports Management
- **Admin View:** All reports from all doctors
- **Doctor View:** Only their own reports
- **Features:** Filter, search, download, export CSV
- **Analytics:** Performance metrics, turnaround time

## 🧪 Testing

### Test Credentials

**Doctor Login:**
- Phone: `+919876543210`
- Access Code: `TEST1234`

### Test Flow

1. **Patient Side:**
   - Open @MediMindRuralBot
   - Submit X-ray request
   - Upload image

2. **Doctor Side:**
   - Open @MediMindDoctorBot
   - View requests
   - Analyze X-ray
   - Generate report
   - Contact patient

3. **Admin Side:**
   - Open http://localhost:8501
   - Monitor requests
   - View reports
   - Check analytics

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Solution: Run from project root
cd "D:\CVMU - chatbot"
streamlit run dashboard/app.py
```

**Ollama Connection Error**
```bash
# Solution: Start Ollama
ollama serve
```

**Translation Not Working**
```bash
# Solution: Pull sarvam-1 model
ollama pull mashriram/sarvam-1
```

See [PROJECT_COMPLETE_DOCUMENTATION.md](PROJECT_COMPLETE_DOCUMENTATION.md) for more troubleshooting.

## 📊 Database Schema

### Main Tables
- `doctors` - Doctor profiles and credentials
- `xray_requests` - X-ray submissions and reports
- `doctor_patient_messages` - Communication audit trail (optional)

See `database/` folder for complete schema.

## 🔒 Security

- Environment variables for sensitive data
- Secure access codes for doctors
- Phone verification for registration
- Audit trail for communications
- Medical privacy compliance

## 🌐 Deployment

### Local Development
```bash
python bot.py
python doctor_bot.py
streamlit run dashboard/app.py
```

### Production Considerations
- Use cloud storage for images/PDFs
- Implement database backups
- Set up monitoring and logging
- Use process managers (PM2, systemd)
- Configure reverse proxy (nginx)

## 📝 License

[Your License Here]

## 👥 Contributors

MediMind Team

## 📧 Support

For issues and questions, refer to:
- [PROJECT_COMPLETE_DOCUMENTATION.md](PROJECT_COMPLETE_DOCUMENTATION.md)
- [start.md](start.md)

## 🎯 Roadmap

- [ ] Mobile app version
- [ ] Cloud storage integration
- [ ] Multi-language support (more languages)
- [ ] Advanced analytics dashboard
- [ ] Telemedicine video calls
- [ ] Prescription management
- [ ] Lab test integration

---

**Version:** 2.0  
**Last Updated:** February 28, 2026  
**Status:** Production Ready

For detailed documentation, see [PROJECT_COMPLETE_DOCUMENTATION.md](PROJECT_COMPLETE_DOCUMENTATION.md)

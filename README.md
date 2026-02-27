# 🏥 MediMind Rural - Healthcare Management System

> A comprehensive healthcare management system for rural Gujarat combining Telegram bot and web dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)]()

---

## 📋 Overview

MediMind Rural is a dual-interface healthcare management system designed specifically for rural areas in Gujarat, India. It provides:

- **Telegram Bot** for patients and health workers (mobile-first)
- **Web Dashboard** for administrators (desktop management)
- **Multi-language Support** (English, Hindi, Gujarati)
- **Real-time Notifications** and emergency alerts
- **AI-powered Assistant** using Sarvam-1 model

---

## ✨ Key Features

### 🤖 Telegram Bot (8 Features)

| Feature | Description | Status |
|---------|-------------|--------|
| 🏥 Hospital Finder | Find nearest hospitals within 10km | ✅ Working |
| 🚑 Emergency SOS | One-tap emergency alert with location | ✅ Working |
| 💊 Medicine Reminders | Daily medication notifications | ✅ Working |
| 📅 Appointment Booking | Schedule hospital visits | ✅ Working |
| 👶 Maternal Health | Pregnancy tracking & schemes | ✅ Working |
| 👩‍⚕️ Health Worker Mode | Registration & patient management | ✅ Working |
| 🌿 Government Schemes | Dynamic scheme information | ✅ Working |
| 📢 Raise Problem | Report issues to admin | ✅ Working |

### 🖥️ Admin Dashboard (9 Pages)

| Page | Description | Status |
|------|-------------|--------|
| 🏠 Home | Overview & live emergency map | ✅ Working |
| 👥 Health Workers | Approve/manage registrations | ✅ Working |
| 🚨 Emergencies | Monitor & resolve emergencies | ✅ Working |
| 📅 Appointments | View & manage appointments | ✅ Working |
| 💊 Reminders | Track medicine reminders | ✅ Working |
| 👶 Maternal Health | Pregnancy tracking records | ✅ Working |
| 🤖 AI Chat | Sarvam-1 AI assistant | ✅ Working |
| ⚙️ CRUD Operations | Full database management | ✅ Working |
| 🌿 Govt Schemes | Add/edit schemes (synced with bot) | ✅ Working |
| 🆘 Issues | View & resolve user problems | ✅ Working |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Telegram account
- Supabase account (free tier works)
- Ollama (for AI features)

### Installation (5 Minutes)

```bash
# 1. Clone repository
git clone <repository-url>
cd CVMU-chatbot

# 2. Install dependencies
pip install -r requirements.txt
cd dashboard && pip install -r requirements.txt && cd ..

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Setup database
# Go to Supabase → SQL Editor
# Run: create_table.sql

# 5. Install Ollama & Sarvam-1
# Download from: https://ollama.com
ollama run mashriram/sarvam-1

# 6. Start bot
python bot.py

# 7. Start dashboard (new terminal)
cd dashboard
streamlit run app.py
```

**Done!** 🎉
- Bot: Message your bot on Telegram
- Dashboard: Open http://localhost:8501

---

## 📖 Documentation

- **[Complete Documentation](DOCUMENTATION.md)** - Full system documentation
- **[Quick Start Guide](start.md)** - Get started in 5 minutes
- **[Database Schema](create_table.sql)** - All tables and policies

---

## 🔧 Configuration

### 1. Create `.env` File

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_ID=your_telegram_user_id

# Supabase Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 2. Create `dashboard/.env` File

```env
# Supabase Database (same as above)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### 3. Get Your Credentials

**Telegram Bot Token:**
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow instructions
3. Copy the token

**Admin ID:**
1. Message [@userinfobot](https://t.me/userinfobot)
2. Copy your user ID

**Supabase:**
1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Go to Settings → API
4. Copy URL and anon key

---

## 🗄️ Database Setup

### Run SQL Schema

1. Open [Supabase Dashboard](https://supabase.com/dashboard)
2. Go to SQL Editor
3. Copy contents of `create_table.sql`
4. Paste and click "Run"
5. Verify 7 tables created

### Tables Created

- `emergencies` - Emergency alerts
- `health_workers` - Worker registrations
- `appointments` - Hospital appointments
- `reminders` - Medicine reminders
- `maternal` - Pregnancy tracking
- `govt_schemes` - Government schemes
- `issues` - User-reported problems

### Important: Fix Emergency Updates

Run this SQL to enable resolve button:

```sql
CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE USING (true);
```

---

## 📱 Usage

### For Patients

1. **Start Bot:** Search for your bot on Telegram
2. **Select Language:** Choose English/Hindi/Gujarati
3. **Use Features:** Click any button from main menu
4. **Get Help:** Use "📢 Raise Problem" for issues

### For Health Workers

1. **Register:** Click "👩‍⚕️ Health Worker Mode" → Register
2. **Wait for Approval:** Admin will approve your registration
3. **Access Features:** View patients and schedule

### For Administrators

1. **Open Dashboard:** http://localhost:8501
2. **Monitor:** Check home page for overview
3. **Manage:** Use sidebar to navigate pages
4. **Respond:** Resolve emergencies and issues

---

## 🏗️ Architecture

```
┌─────────────┐         ┌─────────────┐
│  Telegram   │         │   Browser   │
│   (Users)   │         │  (Admins)   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│ Python Bot  │         │  Streamlit  │
│  (bot.py)   │◄───────►│ Dashboard   │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────────┬───────────┘
                   ▼
          ┌────────────────┐
          │    Supabase    │
          │   PostgreSQL   │
          └────────────────┘
                   │
                   ▼
          ┌────────────────┐
          │ External APIs  │
          │ • Overpass     │
          │ • Ollama       │
          └────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
- **Python 3.10+** - Core language
- **python-telegram-bot 21.0.1** - Telegram bot framework
- **Supabase** - PostgreSQL database
- **Ollama** - AI model hosting
- **Sarvam-1** - Hindi/Gujarati AI model

### Frontend
- **Streamlit** - Web dashboard framework
- **Folium** - Interactive maps
- **Pandas** - Data manipulation

### APIs
- **Overpass API** - Hospital location data
- **Telegram Bot API** - Bot communication
- **Supabase REST API** - Database operations

---

## 📊 Project Structure

```
CVMU-chatbot/
├── bot.py                    # Telegram bot (main)
├── requirements.txt          # Bot dependencies
├── .env                      # Bot configuration
├── create_table.sql         # Database schema
├── fix_emergency_update.sql # Emergency fix
├── start.md                 # Quick start
├── DOCUMENTATION.md         # Full docs
├── README.md                # This file
├── .gitignore              # Git ignore rules
│
└── dashboard/              # Admin dashboard
    ├── app.py              # Home page
    ├── requirements.txt    # Dashboard dependencies
    ├── .env               # Dashboard config
    ├── .env.example       # Example config
    │
    └── pages/             # Dashboard pages
        ├── 1_👥_Health_Workers.py
        ├── 2_🚨_Emergencies.py
        ├── 3_📅_Appointments.py
        ├── 4_💊_Reminders.py
        ├── 5_👶_Maternal_Health.py
        ├── 6_🤖_AI_Chat.py
        ├── 7_⚙️_CRUD_Operations.py
        ├── 8_🌿_Govt_Schemes.py
        └── 9_🆘_Issues.py
```

---

## 🐛 Troubleshooting

### Bot Not Starting

```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt

# Check .env file exists
cat .env
```

### Dashboard Not Loading

```bash
# Check Streamlit installed
streamlit --version

# Try different port
streamlit run app.py --server.port 8502

# Check Supabase connection
# Verify credentials in dashboard/.env
```

### Emergency Resolve Button Not Working

```sql
-- Run this in Supabase SQL Editor
CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE USING (true);
```

### AI Chat Not Working

```bash
# Start Ollama
ollama serve

# Run Sarvam-1 model
ollama run mashriram/sarvam-1

# Check endpoint in dashboard/pages/6_🤖_AI_Chat.py
# Should be: http://localhost:11434/api/generate
# Model: mashriram/sarvam-1
```

---

## 🔒 Security

### Best Practices

- ✅ Never commit `.env` files
- ✅ Use environment variables for secrets
- ✅ Enable Row Level Security (RLS) in Supabase
- ✅ Regularly update dependencies
- ✅ Monitor API usage
- ✅ Use HTTPS in production

### Production Checklist

- [ ] Change default passwords
- [ ] Enable 2FA on Supabase
- [ ] Set up SSL/TLS
- [ ] Configure firewall
- [ ] Enable logging
- [ ] Set up backups
- [ ] Monitor error rates
- [ ] Test disaster recovery

---

## 📈 Performance

### Optimization Tips

1. **Database Indexing** - Already configured in `create_table.sql`
2. **Caching** - Streamlit caching enabled
3. **Connection Pooling** - Supabase handles automatically
4. **Rate Limiting** - Telegram bot has built-in limits

### Monitoring

- **Bot Status:** Check terminal for logs
- **Dashboard:** Streamlit shows errors in UI
- **Database:** Monitor in Supabase dashboard
- **API Usage:** Check Supabase API logs

---

## 🚀 Deployment

### Option 1: VPS (Recommended)

```bash
# Ubuntu 20.04+ server
sudo apt update && sudo apt upgrade -y
sudo apt install python3.10 python3-pip -y

# Clone and setup
git clone <repo-url>
cd CVMU-chatbot
pip3 install -r requirements.txt

# Configure systemd services
sudo nano /etc/systemd/system/medimind-bot.service
sudo nano /etc/systemd/system/medimind-dashboard.service

# Start services
sudo systemctl start medimind-bot
sudo systemctl start medimind-dashboard
sudo systemctl enable medimind-bot
sudo systemctl enable medimind-dashboard
```

### Option 2: Docker

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Option 3: Streamlit Cloud (Dashboard Only)

1. Push to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect repository
4. Add secrets
5. Deploy

---

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dev dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If exists

# Run tests
pytest

# Format code
black .
```

---

## 📝 Changelog

### Version 2.1 (Current)
- ✅ Added Government Schemes sync (Dashboard ↔ Bot)
- ✅ Fixed Emergency resolve button
- ✅ Added Issues management page
- ✅ Cleaned sidebar UI
- ✅ Fixed AI Chat endpoint
- ✅ Added "Raise Problem" feature

### Version 2.0
- ✅ Complete admin dashboard (9 pages)
- ✅ AI Chat with Sarvam-1
- ✅ Government Schemes CRUD
- ✅ Multi-language support
- ✅ Health worker registration

### Version 1.0
- ✅ Basic Telegram bot (8 features)
- ✅ Supabase integration
- ✅ Hospital finder
- ✅ Emergency alerts
- ✅ Medicine reminders
- ✅ Appointment booking

---

## 📄 License

This project is for educational and healthcare purposes. 

**Restrictions:**
- Not for commercial use without permission
- Must credit original authors
- Cannot be used for harmful purposes

---

## 👥 Team

**Developed for:** Rural Gujarat Healthcare  
**Purpose:** Educational & Social Impact  
**Technology:** Python, Telegram, Streamlit, Supabase

---

## 🙏 Acknowledgments

- **Telegram Bot API** - Bot framework
- **Streamlit** - Dashboard framework
- **Supabase** - Database hosting
- **Ollama** - AI model hosting
- **Sarvam AI** - Hindi/Gujarati AI model
- **Overpass API** - Hospital location data
- **Gujarat Health Department** - Healthcare data

---

## 📞 Support

### Documentation
- [Complete Documentation](DOCUMENTATION.md)
- [Quick Start Guide](start.md)
- [Database Schema](create_table.sql)

### Common Issues
- Check [Troubleshooting](#-troubleshooting) section
- Review [DOCUMENTATION.md](DOCUMENTATION.md)
- Check Supabase logs
- Enable debug mode

### Contact
- **Issues:** Open GitHub issue
- **Questions:** Check documentation first
- **Bugs:** Report with logs and steps to reproduce

---

## 🎯 Roadmap

### Planned Features

- [ ] SMS notifications
- [ ] Email alerts
- [ ] Mobile app (React Native)
- [ ] Voice commands
- [ ] Offline mode
- [ ] Analytics dashboard
- [ ] Export reports (PDF/Excel)
- [ ] Multi-region support
- [ ] Video consultations
- [ ] Payment integration

---

## 📊 Statistics

- **Lines of Code:** ~5,000+
- **Features:** 17 (8 bot + 9 dashboard)
- **Languages:** 3 (English, Hindi, Gujarati)
- **Database Tables:** 7
- **API Integrations:** 3
- **Pages:** 10 (1 home + 9 management)

---

## ⭐ Star History

If this project helped you, please consider giving it a star! ⭐

---

## 📸 Screenshots

### Telegram Bot
- Multi-language interface
- 8 feature buttons
- Real-time notifications
- Location sharing

### Admin Dashboard
- Clean sidebar navigation
- Live emergency map
- Interactive charts
- CRUD operations

---

**Made with ❤️ for Rural Gujarat Healthcare**

**Version:** 2.1  
**Status:** Production Ready ✅  
**Last Updated:** February 22, 2026

---

[⬆ Back to Top](#-medimind-rural---healthcare-management-system)

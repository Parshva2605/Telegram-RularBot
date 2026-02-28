# 📚 MediMind Rural - Complete Documentation

**Version:** 2.1  
**Last Updated:** February 22, 2026  
**Status:** Production Ready

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Installation Guide](#installation-guide)
5. [Configuration](#configuration)
6. [Database Setup](#database-setup)
7. [Running the System](#running-the-system)
8. [User Guide](#user-guide)
9. [Admin Guide](#admin-guide)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)
12. [Development](#development)
13. [Deployment](#deployment)

---

## 🎯 Project Overview

MediMind Rural is a comprehensive healthcare management system designed for rural Gujarat, India. It combines a Telegram bot for users and health workers with a web-based admin dashboard.

### Key Components

1. **Telegram Bot** - User interface for patients and health workers
2. **Admin Dashboard** - Web-based management interface (Streamlit)
3. **Database** - Supabase (PostgreSQL) for data storage
4. **AI Assistant** - Sarvam-1 model via Ollama for intelligent responses

### Target Users

- **Patients** - Rural residents seeking healthcare information
- **Health Workers** - ASHA workers, nurses, physiotherapists
- **Administrators** - Healthcare facility managers

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USERS                                    │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   Telegram   │              │   Browser    │            │
│  │   (Mobile)   │              │  (Desktop)   │            │
│  └──────┬───────┘              └──────┬───────┘            │
└─────────┼──────────────────────────────┼──────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐
│   TELEGRAM BOT      │      │   ADMIN DASHBOARD   │
│   (Python)          │      │   (Streamlit)       │
│                     │      │                     │
│  • Multi-language   │      │  • 9 Management     │
│  • 8 Features       │      │    Pages            │
│  • Real-time        │      │  • Analytics        │
│  • Notifications    │      │  • CRUD Operations  │
└─────────┬───────────┘      └─────────┬───────────┘
          │                            │
          └────────────┬───────────────┘
                       ▼
          ┌────────────────────────┐
          │   SUPABASE DATABASE    │
          │   (PostgreSQL)         │
          │                        │
          │  • emergencies         │
          │  • health_workers      │
          │  • appointments        │
          │  • reminders           │
          │  • maternal            │
          │  • govt_schemes        │
          │  • issues              │
          └────────────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │   EXTERNAL SERVICES    │
          │                        │
          │  • Overpass API        │
          │    (Hospital finder)   │
          │  • Ollama/Sarvam-1     │
          │    (AI Assistant)      │
          └────────────────────────┘
```

---

## ✨ Features

### Telegram Bot Features

#### 1. 🏥 Nearest Hospital Finder
- Search by current location or city name
- Shows top 5 hospitals within 10km
- Distance calculation
- Google Maps integration
- Fallback to hardcoded hospitals

#### 2. 🚑 Emergency Help (SOS)
- One-tap location sharing
- Saves to database
- Forwards to admin immediately
- Real-time tracking

#### 3. 💊 Medicine Reminder
- Set multiple reminders
- Daily notifications
- View active reminders
- Delete reminders
- Hourly background checks

#### 4. 📅 Visit Planner (Appointments)
- Book hospital appointments
- Date/time selection
- Notes support
- 1-day advance reminder
- Cancel appointments

#### 5. 👶 Maternal Health
- Pregnancy week calculator
- Due date estimation
- ANC visit scheduling
- Baby growth tracker
- Gujarat mother schemes info

#### 6. 👩‍⚕️ Health Worker Mode
- Registration system
- Admin approval workflow
- Patient list access
- Schedule management
- Emergency notifications

#### 7. 🌿 Government Schemes
- Dynamic loading from database
- Multi-language support
- Detailed scheme information
- Phone numbers and links
- Up to 6 schemes displayed

#### 8. 📢 Raise Problem
- Report issues
- Category selection (User/Worker)
- Detailed description
- Forwards to admin
- Status tracking

### Admin Dashboard Features

#### 1. 🏠 Home Dashboard
- Overview statistics
- Live emergency map
- Recent activity feed
- Quick metrics cards

#### 2. 👥 Health Workers Management
- View all registrations
- Approve/reject workers
- Location map
- Worker statistics
- Category breakdown

#### 3. 🚨 Emergencies Management
- Active emergency list
- Resolve button (updates status)
- Emergency location map
- Resolved history
- Time elapsed tracking
- Auto-refresh option

#### 4. 📅 Appointments Management
- View all appointments
- Cancel appointments
- Date filtering
- User information

#### 5. 💊 Reminders Management
- Active reminders list
- Stop reminders
- User tracking

#### 6. 👶 Maternal Health Tracking
- Pregnancy records
- Due date tracking
- Week calculations

#### 7. 🤖 AI Chat Assistant
- Sarvam-1 integration
- Database-aware responses
- Chat history
- Quick questions
- Context-aware answers

#### 8. ⚙️ CRUD Operations
- Full database access
- Add/Edit/Delete records
- All tables management

#### 9. 🌿 Government Schemes CRUD
- Add new schemes
- Edit existing schemes
- Multi-language support
- Active/Inactive toggle
- Search functionality
- Statistics

#### 10. 🆘 Issues Management
- View reported problems
- Resolve issues
- Filter by status
- Category breakdown
- Time tracking

---

## 🚀 Installation Guide

### Prerequisites

1. **Python 3.10+**
   ```bash
   python --version
   ```

2. **pip** (Python package manager)
   ```bash
   pip --version
   ```

3. **Git** (optional, for cloning)
   ```bash
   git --version
   ```

4. **Supabase Account**
   - Sign up at https://supabase.com
   - Create a new project

5. **Telegram Bot Token**
   - Message @BotFather on Telegram
   - Create new bot
   - Save the token

6. **Ollama** (for AI Chat)
   - Download from https://ollama.com
   - Install Sarvam-1 model

### Step-by-Step Installation

#### 1. Clone or Download Project

```bash
# Option A: Clone with Git
git clone <repository-url>
cd CVMU-chatbot

# Option B: Download ZIP and extract
```

#### 2. Install Python Dependencies

```bash
# Install bot dependencies
pip install -r requirements.txt

# Install dashboard dependencies
cd dashboard
pip install -r requirements.txt
cd ..
```

#### 3. Install Ollama and Sarvam-1

**Windows:**
```bash
# Download installer from https://ollama.com/download
# Run installer
# Open terminal and run:
ollama run mashriram/sarvam-1
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run mashriram/sarvam-1
```

---

## ⚙️ Configuration

### 1. Create .env File

Create `.env` in root directory:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

### 2. Create Dashboard .env File

Create `dashboard/.env`:

```env
# Supabase Configuration (same as root)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

### 3. Get Configuration Values

#### Telegram Bot Token:
1. Open Telegram
2. Search for @BotFather
3. Send `/newbot`
4. Follow instructions
5. Copy token

#### Admin ID:
1. Search for @userinfobot on Telegram
2. Send any message
3. Copy your user ID

#### Supabase Credentials:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to Settings → API
4. Copy:
   - Project URL (SUPABASE_URL)
   - anon/public key (SUPABASE_KEY)

---

## 🗄️ Database Setup

### 1. Create Supabase Project

1. Go to https://supabase.com
2. Click "New Project"
3. Fill in details:
   - Name: MediMind Rural
   - Database Password: (save this!)
   - Region: Choose closest to Gujarat
4. Wait for project creation (~2 minutes)

### 2. Run SQL Schema

1. Go to SQL Editor in Supabase
2. Click "New Query"
3. Copy entire contents of `create_table.sql`
4. Paste and click "Run"
5. Verify success message

### 3. Verify Tables Created

Run this query to check:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should show:
- emergencies
- health_workers
- appointments
- reminders
- maternal
- govt_schemes
- issues

### 4. Fix Emergency Update Policy (Important!)

Run this to enable resolve button:

```sql
DROP POLICY IF EXISTS "Allow public updates" ON emergencies;

CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE
  USING (true);
```

---

## 🏃 Running the System

### Start Ollama (for AI Chat)

**Terminal 1:**
```bash
ollama serve
```

**Terminal 2:**
```bash
ollama run mashriram/sarvam-1
```

Keep these running in background.

### Start Telegram Bot

**Terminal 3:**
```bash
python bot.py
```

You should see:
```
✅ MediMind Rural bot is running...
🔔 Medicine reminder scheduler started
Press Ctrl+C to stop
```

### Start Admin Dashboard

**Terminal 4:**
```bash
cd dashboard
streamlit run app.py
```

Dashboard opens at: http://localhost:8501

### Verify Everything Works

1. **Bot:** Send `/start` to your bot on Telegram
2. **Dashboard:** Open http://localhost:8501
3. **AI Chat:** Go to AI Chat page, send test message
4. **Database:** Check Supabase dashboard for data

---

## 👤 User Guide

### For Patients

#### Getting Started

1. **Find Bot:** Search for your bot name on Telegram
2. **Start:** Send `/start`
3. **Select Language:** Choose English/Hindi/Gujarati
4. **Main Menu:** 8 feature buttons appear

#### Using Features

**Find Hospital:**
1. Click "🏥 Nearest Hospital"
2. Share location OR enter city name
3. View top 5 hospitals with distance
4. Click Google Maps link to navigate

**Emergency Help:**
1. Click "🚑 Emergency Help"
2. Share your location
3. Confirmation message appears
4. Admin receives alert immediately

**Set Medicine Reminder:**
1. Click "💊 Medicine Reminder"
2. Click "➕ Set New Reminder"
3. Enter medicine name
4. Enter time (e.g., "09:00 AM")
5. Enter dosage
6. Receive daily reminders

**Book Appointment:**
1. Click "📅 Visit Planner"
2. Click "➕ Book New Visit"
3. Enter hospital name
4. Enter date (DD-MM-YYYY)
5. Enter time
6. Add notes (optional)
7. Receive reminder 1 day before

**Pregnancy Calculator:**
1. Click "👶 Maternal Health"
2. Click "🤰 Pregnancy Week Calculator"
3. Enter LMP date (DD-MM-YYYY)
4. View weeks pregnant, due date, next ANC visit

**View Government Schemes:**
1. Click "🌿 Govt Schemes"
2. Browse available schemes
3. Click scheme for details
4. Note phone numbers and links

**Report Problem:**
1. Click "📢 Raise Problem"
2. Enter your name
3. Select category (User/Worker)
4. Enter age
5. Describe problem
6. Admin receives notification

### For Health Workers

#### Registration

1. Click "👩‍⚕️ Health Worker Mode"
2. Click "📝 Register as Health Worker"
3. Enter full name
4. Enter age
5. Select category (ASHA/Nurse/Physio)
6. Enter years of experience
7. Share location
8. Wait for admin approval

#### After Approval

1. Click "👩‍⚕️ Health Worker Mode"
2. Click "📍 My Patients Nearby" - View assigned patients
3. Click "📋 Today's Schedule" - View today's appointments

---

## 👨‍💼 Admin Guide

### Dashboard Overview

Access: http://localhost:8501

#### Home Page

- **Metrics Cards:** Emergencies, Workers, Appointments, Reminders
- **Emergency Map:** Live locations of all emergencies
- **Recent Activity:** Latest emergencies and appointments

#### Managing Health Workers

1. Go to "👥 Health Workers" page
2. View pending registrations
3. Click "✅ Approve" or "❌ Reject"
4. View worker locations on map
5. Check statistics

#### Managing Emergencies

1. Go to "🚨 Emergencies" page
2. View active emergencies
3. Click "✅ Resolve" to mark as resolved
4. Click "📞 Call 108" to dispatch ambulance
5. View resolved emergencies in "Resolved" tab
6. Check emergency map

#### Managing Appointments

1. Go to "📅 Appointments" page
2. View all appointments
3. Search by user or hospital
4. Click "❌ Cancel" to cancel appointment

#### Managing Reminders

1. Go to "💊 Reminders" page
2. View active reminders
3. Click "🛑 Stop" to deactivate reminder

#### Managing Government Schemes

1. Go to "🌿 Govt Schemes" page
2. **Add New Scheme:**
   - Click "Add New Scheme" tab
   - Fill English fields (required)
   - Fill Hindi/Gujarati (optional)
   - Add phone and link
   - Click "Add Scheme"
3. **Edit Scheme:**
   - Click "✏️ Edit" on any scheme
   - Update fields
   - Click "Update Scheme"
4. **Toggle Active/Inactive:**
   - Click "🔄 Activate/Deactivate"
5. **Delete Scheme:**
   - Click "🗑️ Delete"

#### Managing Issues

1. Go to "🆘 Issues" page
2. View open issues
3. Click "✅ Resolve" to close issue
4. Filter by status (Open/Closed/All)
5. Filter by category (User/Worker)
6. Check statistics

#### Using AI Chat

1. Go to "🤖 AI Chat" page
2. Type question in input box
3. Click "Send"
4. AI responds with database-aware answer
5. Use quick question buttons
6. Clear chat history if needed

#### CRUD Operations

1. Go to "⚙️ CRUD Operations" page
2. Select table from dropdown
3. View all records
4. Add new record
5. Edit existing record
6. Delete record

---

## 🔧 API Reference

### Supabase Tables

#### emergencies
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
lat FLOAT8 NOT NULL
lon FLOAT8 NOT NULL
timestamp TIMESTAMPTZ DEFAULT NOW()
status TEXT DEFAULT 'pending'
```

#### health_workers
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
name TEXT NOT NULL
age INT
category TEXT NOT NULL
experience INT
lat FLOAT8
lon FLOAT8
approved BOOLEAN DEFAULT false
created TIMESTAMPTZ DEFAULT NOW()
```

#### appointments
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
hospital TEXT NOT NULL
date TEXT NOT NULL
time TEXT NOT NULL
notes TEXT
reminder_sent BOOLEAN DEFAULT false
created TIMESTAMPTZ DEFAULT NOW()
```

#### reminders
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
medicine_name TEXT NOT NULL
time TEXT NOT NULL
dosage TEXT
active BOOLEAN DEFAULT true
created TIMESTAMPTZ DEFAULT NOW()
```

#### maternal
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
lmp_date TEXT NOT NULL
weeks_pregnant INT
due_date TEXT
created TIMESTAMPTZ DEFAULT NOW()
```

#### govt_schemes
```sql
id BIGSERIAL PRIMARY KEY
title_en TEXT NOT NULL
title_hi TEXT
title_gu TEXT
desc_en TEXT NOT NULL
desc_hi TEXT
desc_gu TEXT
phone TEXT
link TEXT
active BOOLEAN DEFAULT true
created TIMESTAMPTZ DEFAULT NOW()
```

#### issues
```sql
id BIGSERIAL PRIMARY KEY
user_id BIGINT NOT NULL
username TEXT
name TEXT NOT NULL
category TEXT NOT NULL
age INT
description TEXT NOT NULL
status TEXT DEFAULT 'open'
created TIMESTAMPTZ DEFAULT NOW()
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Bot Not Starting

**Error:** `BOT_TOKEN not found`
**Solution:** Check `.env` file exists and has correct token

**Error:** `ModuleNotFoundError`
**Solution:** Run `pip install -r requirements.txt`

#### 2. Dashboard Not Loading

**Error:** `Cannot connect to Supabase`
**Solution:** 
- Check `dashboard/.env` file
- Verify Supabase credentials
- Check internet connection

**Error:** `Port 8501 already in use`
**Solution:** 
```bash
streamlit run app.py --server.port 8502
```

#### 3. Emergency Resolve Button Not Working

**Error:** Button clicks but emergency stays active
**Solution:** Run this SQL in Supabase:
```sql
CREATE POLICY "Allow public updates" ON emergencies
  FOR UPDATE USING (true);
```

#### 4. AI Chat Not Working

**Error:** `Cannot connect to Ollama`
**Solution:**
```bash
# Start Ollama service
ollama serve

# In another terminal
ollama run mashriram/sarvam-1
```

**Error:** `404 Not Found`
**Solution:** Check model name is `mashriram/sarvam-1` not just `sarvam-1`

#### 5. Schemes Not Syncing

**Error:** Dashboard shows schemes but bot doesn't
**Solution:** Restart bot: `Ctrl+C` then `python bot.py`

**Error:** Bot shows old hardcoded schemes
**Solution:** Check Supabase connection in bot logs

#### 6. Database Connection Issues

**Error:** `permission denied for table`
**Solution:** Check RLS policies are created (run `create_table.sql`)

**Error:** `column does not exist`
**Solution:** Re-run `create_table.sql` to add missing columns

---

## 💻 Development

### Project Structure

```
CVMU-chatbot/
├── bot.py                      # Telegram bot main file
├── requirements.txt            # Bot dependencies
├── .env                        # Bot configuration
├── create_table.sql           # Database schema
├── fix_emergency_update.sql   # Emergency fix script
├── start.md                   # Quick start guide
├── DOCUMENTATION.md           # This file
├── README.md                  # Project readme
├── .gitignore                 # Git ignore rules
│
└── dashboard/                 # Admin dashboard
    ├── app.py                 # Dashboard home
    ├── requirements.txt       # Dashboard dependencies
    ├── .env                   # Dashboard configuration
    ├── .env.example          # Example configuration
    │
    └── pages/                 # Dashboard pages
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

### Adding New Features

#### Add New Bot Feature

1. Add translations to `TEXTS` dictionary
2. Add menu button to `MENU_BUTTONS`
3. Create keyboard function
4. Add callback handler in `button_callback()`
5. Add message handler in `handle_message()`
6. Test thoroughly

#### Add New Dashboard Page

1. Create `dashboard/pages/X_Name.py`
2. Follow existing page structure
3. Add Supabase queries
4. Add UI components
5. Test functionality

#### Add New Database Table

1. Add CREATE TABLE to `create_table.sql`
2. Add RLS policies
3. Run SQL in Supabase
4. Update bot/dashboard code
5. Test CRUD operations

---

## 🚀 Deployment

### Production Checklist

- [ ] Update `.env` with production credentials
- [ ] Enable HTTPS for dashboard
- [ ] Set up domain name
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test all features
- [ ] Load test system
- [ ] Set up error logging
- [ ] Create admin accounts

### Deployment Options

#### Option 1: VPS (Recommended)

**Requirements:**
- Ubuntu 20.04+ server
- 2GB RAM minimum
- Python 3.10+
- Domain name (optional)

**Steps:**
```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python
sudo apt install python3.10 python3-pip -y

# 3. Clone project
git clone <repo-url>
cd CVMU-chatbot

# 4. Install dependencies
pip3 install -r requirements.txt
cd dashboard && pip3 install -r requirements.txt

# 5. Configure .env files
nano .env
nano dashboard/.env

# 6. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama run mashriram/sarvam-1

# 7. Set up systemd services
sudo nano /etc/systemd/system/medimind-bot.service
sudo nano /etc/systemd/system/medimind-dashboard.service

# 8. Start services
sudo systemctl start medimind-bot
sudo systemctl start medimind-dashboard
sudo systemctl enable medimind-bot
sudo systemctl enable medimind-dashboard
```

#### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "bot.py"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  bot:
    build: .
    env_file: .env
    restart: always
  
  dashboard:
    build: ./dashboard
    ports:
      - "8501:8501"
    env_file: dashboard/.env
    restart: always
```

Run:
```bash
docker-compose up -d
```

#### Option 3: Streamlit Cloud (Dashboard Only)

1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect GitHub repository
4. Add secrets in dashboard
5. Deploy

---

## 📊 Monitoring & Maintenance

### Logs

**Bot Logs:**
```bash
tail -f bot.log
```

**Dashboard Logs:**
```bash
tail -f dashboard.log
```

### Database Maintenance

**Backup:**
```bash
# From Supabase dashboard
# Settings → Database → Backups
```

**Clean Old Data:**
```sql
-- Delete resolved emergencies older than 30 days
DELETE FROM emergencies 
WHERE status = 'resolved' 
AND timestamp < NOW() - INTERVAL '30 days';

-- Delete inactive reminders older than 90 days
DELETE FROM reminders 
WHERE active = false 
AND created < NOW() - INTERVAL '90 days';
```

### Performance Monitoring

**Check Bot Status:**
```bash
ps aux | grep bot.py
```

**Check Dashboard Status:**
```bash
ps aux | grep streamlit
```

**Monitor Database:**
- Go to Supabase Dashboard
- Check Database → Usage
- Monitor API requests

---

## 🤝 Contributing

### Code Style

- Follow PEP 8 for Python
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

### Testing

Before submitting:
1. Test all bot features
2. Test all dashboard pages
3. Check database operations
4. Verify multi-language support
5. Test error handling

---

## 📄 License

This project is for educational and healthcare purposes.

---

## 👥 Support

For issues or questions:
- Check this documentation
- Review troubleshooting section
- Check Supabase logs
- Test with debug mode enabled

---

## 🎉 Acknowledgments

- Telegram Bot API
- Streamlit Framework
- Supabase Database
- Ollama & Sarvam-1 AI
- Overpass API
- Gujarat Health Department

---

**Documentation Version:** 2.1  
**Last Updated:** February 22, 2026  
**Status:** Complete & Production Ready

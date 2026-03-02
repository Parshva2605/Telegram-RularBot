# 👨‍⚕️ MediMind Doctor Portal

Complete dashboard for doctors with all features from admin dashboard, plus appointments calendar.

## Features

### Pages Available:

1. **📅 My Appointments** - Calendar view of your scheduled appointments
2. **👨‍⚕️ Doctor Dashboard** - Login and access your X-ray queue, reports, and statistics
3. **🩻 X-Ray Requests** - View and manage X-ray analysis requests
4. **📄 Reports** - Access all generated PDF reports

### Doctor Dashboard Features:
- **Login System**: Secure login with phone + access code
- **Live Queue**: View pending X-ray requests assigned to you
- **My Reports**: Access all PDF reports you've generated
- **Statistics**: Performance metrics and charts
- **Bulk Actions**: Mark multiple requests as reviewed

## Setup

1. Install dependencies:
```bash
cd doc_dashboard
pip install -r requirements.txt
```

2. Configure `.env` file (already configured)

3. Run the dashboard:
```bash
streamlit run app.py
```

## Login Credentials

Doctors can get their access code from the Doctor Bot:
- Open @MediMindDoctorBot on Telegram
- Click "🔐 Regen Code" to get/regenerate access code
- Use phone number and access code to login

## Difference from Admin Dashboard

- **Doctor Portal** (`doc_dashboard/`): Individual doctors see only THEIR data (appointments, X-rays, reports)
- **Admin Dashboard** (`dashboard/`): Admin sees ALL data from ALL doctors

## Access

- Doctor Portal: http://localhost:8501
- Admin Dashboard: http://localhost:8502 (if running both)

To run both simultaneously:
```bash
# Terminal 1 - Admin Dashboard
cd dashboard
streamlit run app.py --server.port 8502

# Terminal 2 - Doctor Portal
cd doc_dashboard
streamlit run app.py --server.port 8501
```

## Features Copied from Admin Dashboard

All doctor-specific features from the admin dashboard have been copied:
- Doctor Dashboard page (with login, queue, reports, statistics)
- X-Ray Requests page
- Reports page
- Plus new Appointments calendar page

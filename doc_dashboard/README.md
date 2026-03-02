# 👨‍⚕️ MediMind Doctor Dashboard

Separate dashboard for doctors to view their appointments and statistics.

## Features

- **Login System**: Doctors login with phone number and access code
- **Dashboard**: View pending requests, reviewed cases, and scheduled appointments
- **Calendar View**: Visual calendar showing appointments with patient names
- **Appointment Details**: Full details of each appointment

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

## Pages

1. **Home (app.py)**: Dashboard with statistics
2. **My Appointments**: Calendar view of doctor's appointments

## Difference from Admin Dashboard

- **Doctor Dashboard** (`doc_dashboard/`): Individual doctors see only THEIR appointments
- **Admin Dashboard** (`dashboard/`): Admin sees ALL appointments from ALL doctors

## Access

- Doctor Dashboard: http://localhost:8501
- Admin Dashboard: http://localhost:8502 (if running both)

To run both simultaneously:
```bash
# Terminal 1 - Admin Dashboard
cd dashboard
streamlit run app.py --server.port 8502

# Terminal 2 - Doctor Dashboard
cd doc_dashboard
streamlit run app.py --server.port 8501
```

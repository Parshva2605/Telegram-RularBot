# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client
import pandas as pd
from datetime import datetime, timedelta
import calendar

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="My Appointments",
    page_icon="📅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    [data-testid="stSidebar"] {background-color: #262730;}
    [data-testid="stSidebarNav"] {max-height: none !important;}
    [data-testid="stSidebarNavCollapseIcon"] {display: none !important;}
    button[kind="header"] {display: none !important;}
    
    /* Calendar styling */
    .calendar-day {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        min-height: 80px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid #333;
    }
    .calendar-day-number {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .calendar-day-today {
        background-color: #2e7d32;
        border: 2px solid #4caf50;
    }
    .calendar-day-appointment {
        background-color: #1565c0;
        border: 2px solid #1e88e5;
    }
    .calendar-day-empty {
        background-color: transparent;
        border: none;
    }
    .calendar-patient-name {
        font-size: 11px;
        margin-top: 5px;
        color: #fff;
    }
    .day-header {
        font-weight: bold;
        text-align: center;
        padding: 10px;
        background-color: #262730;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Check login
if 'doctor_logged_in' not in st.session_state or not st.session_state.doctor_logged_in:
    st.error("❌ Please login first from Doctor Dashboard page")
    st.info("👉 Go to 'Doctor Dashboard' page to login")
    st.stop()

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    return create_client(url, key)

supabase = init_supabase()

st.title("📅 My Appointments")
st.markdown(f"### Dr. {st.session_state.doctor_name}")

# Get current month and year
today = datetime.now()

# Month selector
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_date = st.date_input(
        "📆 Select Month",
        value=today,
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
    selected_month = selected_date.month
    selected_year = selected_date.year

try:
    phone = st.session_state.doctor_phone
    
    # Get appointments for selected month
    appointments_response = supabase.table("appointments").select("*").eq("doctor_phone", phone).eq("status", "scheduled").execute()
    
    all_appointments = appointments_response.data if appointments_response.data else []
    
    # Filter appointments for selected month
    month_appointments = []
    for apt in all_appointments:
        apt_date = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        if apt_date.month == selected_month and apt_date.year == selected_year:
            month_appointments.append(apt)
    
    st.markdown("---")
    st.markdown(f"## 📆 {calendar.month_name[selected_month]} {selected_year}")
    st.markdown("")
    
    # Get calendar matrix
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # Day headers
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f'<div class="day-header">{day[:3]}</div>', unsafe_allow_html=True)
    
    # Calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    # Empty cell
                    st.markdown('<div class="calendar-day calendar-day-empty" style="min-height: 80px;"></div>', unsafe_allow_html=True)
                else:
                    # Check if this day has appointment
                    day_date = datetime(selected_year, selected_month, day).strftime('%Y-%m-%d')
                    day_appointments = [apt for apt in month_appointments if apt['appointment_date'] == day_date]
                    
                    # Check if today
                    is_today = (day == today.day and selected_month == today.month and selected_year == today.year)
                    
                    if day_appointments:
                        # Day with appointment
                        apt = day_appointments[0]
                        patient_name = apt['patient_name']
                        if len(patient_name) > 10:
                            patient_name = patient_name[:10] + "..."
                        
                        st.markdown(f"""
                        <div class="calendar-day calendar-day-appointment">
                            <div class="calendar-day-number">{day}</div>
                            <div class="calendar-patient-name">👤 {patient_name}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    elif is_today:
                        # Today
                        st.markdown(f"""
                        <div class="calendar-day calendar-day-today">
                            <div class="calendar-day-number">{day}</div>
                            <div class="calendar-patient-name">Today</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Regular day
                        st.markdown(f"""
                        <div class="calendar-day">
                            <div class="calendar-day-number">{day}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Legend
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("🔵 **Blue** = Appointment")
    with col2:
        st.markdown("🟢 **Green** = Today")
    with col3:
        st.markdown("⚫ **Gray** = Regular Day")
    with col4:
        st.metric("📊 Total", len(month_appointments))
    
    st.markdown("---")
    
    # List all appointments
    st.markdown("### 📋 Appointment Details")
    
    if month_appointments:
        # Sort by date
        month_appointments.sort(key=lambda x: x['appointment_date'])
        
        for apt in month_appointments:
            date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
            display_date = date_obj.strftime('%d %B %Y')
            day_name = date_obj.strftime('%A')
            
            with st.expander(f"📅 {display_date} ({day_name}) - {apt['patient_name']}", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**👤 Patient:** {apt['patient_name']}")
                    if apt.get('patient_phone'):
                        st.markdown(f"**📱 Phone:** {apt['patient_phone']}")
                    if apt.get('patient_village'):
                        st.markdown(f"**📍 Village:** {apt['patient_village']}")
                with col2:
                    st.markdown(f"**📝 Reason:** {apt.get('reason', 'Not specified')}")
                    st.markdown(f"**🕐 Booked:** {apt.get('created_at', 'N/A')[:10]}")
                    st.markdown(f"**🆔 ID:** {apt['id']}")
    else:
        st.info(f"📭 No appointments scheduled for {calendar.month_name[selected_month]} {selected_year}")

except Exception as e:
    st.error(f"❌ Error loading appointments: {e}")
    st.exception(e)

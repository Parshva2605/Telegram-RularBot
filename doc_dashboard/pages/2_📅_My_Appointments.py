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
current_month = today.month
current_year = today.year

# Month selector
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    selected_date = st.date_input(
        "Select Month",
        value=today,
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
    selected_month = selected_date.month
    selected_year = selected_date.year

try:
    phone = st.session_state.doctor_phone
    
    # Get appointments for selected month
    first_day = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        last_day = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = datetime(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    appointments_response = supabase.table("appointments").select("*").eq("doctor_phone", phone).eq("status", "scheduled").execute()
    
    all_appointments = appointments_response.data if appointments_response.data else []
    
    # Filter appointments for selected month
    month_appointments = []
    for apt in all_appointments:
        apt_date = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        if apt_date.month == selected_month and apt_date.year == selected_year:
            month_appointments.append(apt)
    
    # Create calendar grid
    st.markdown(f"### 📆 {calendar.month_name[selected_month]} {selected_year}")
    
    # Get calendar matrix
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # Day headers
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    cols = st.columns(7)
    for i, day in enumerate(days):
        with cols[i]:
            st.markdown(f"**{day}**")
    
    # Calendar grid
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown("")
                else:
                    # Check if this day has appointment
                    day_date = datetime(selected_year, selected_month, day).strftime('%Y-%m-%d')
                    day_appointments = [apt for apt in month_appointments if apt['appointment_date'] == day_date]
                    
                    if day_appointments:
                        # Highlight day with appointment
                        apt = day_appointments[0]
                        st.markdown(f"""
                        <div style='background-color: #1e88e5; padding: 10px; border-radius: 5px; text-align: center;'>
                            <div style='font-size: 20px; font-weight: bold;'>{day}</div>
                            <div style='font-size: 12px;'>👤 {apt['patient_name']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Regular day
                        is_today = (day == today.day and selected_month == today.month and selected_year == today.year)
                        bg_color = '#2e7d32' if is_today else '#424242'
                        st.markdown(f"""
                        <div style='background-color: {bg_color}; padding: 10px; border-radius: 5px; text-align: center;'>
                            <div style='font-size: 20px;'>{day}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
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
            
            with st.expander(f"📅 {display_date} ({day_name}) - {apt['patient_name']}"):
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
    
    # Show total count
    st.markdown("---")
    st.metric("📊 Total Appointments This Month", len(month_appointments))

except Exception as e:
    st.error(f"❌ Error loading appointments: {e}")
    st.exception(e)

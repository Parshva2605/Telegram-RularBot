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
        padding: 20px;
        border-radius: 8px;
        text-align: center;
        height: 100px;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 1px solid #333;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .calendar-day:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .calendar-day-number {
        font-size: 28px;
        font-weight: bold;
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
        cursor: default;
    }
    .calendar-day-empty:hover {
        transform: none;
        box-shadow: none;
    }
    .day-header {
        font-weight: bold;
        text-align: center;
        padding: 12px;
        background-color: #262730;
        border-radius: 5px;
        margin-bottom: 15px;
        font-size: 16px;
    }
    /* Logout button at bottom */
    .sidebar-logout {
        position: fixed;
        bottom: 20px;
        left: 20px;
        width: calc(16rem - 40px);
        z-index: 999;
    }
</style>
""", unsafe_allow_html=True)

# Check login
if 'doctor_logged_in' not in st.session_state or not st.session_state.doctor_logged_in:
    st.error("❌ Please login first from Doctor Dashboard page")
    st.info("👉 Go to 'Doctor Dashboard' page to login")
    st.stop()

# Logout function
def logout():
    st.session_state.doctor_logged_in = False
    st.session_state.doctor_phone = None
    st.session_state.doctor_name = None
    st.session_state.doctor_data = None

# Sidebar - Logout button at bottom
with st.sidebar:
    st.markdown("<br>" * 25, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-logout">', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True, type="secondary", key="logout_btn"):
        logout()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
    appointments_by_date = {}
    for apt in all_appointments:
        apt_date = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        if apt_date.month == selected_month and apt_date.year == selected_year:
            month_appointments.append(apt)
            appointments_by_date[apt['appointment_date']] = apt
    
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
    
    # Calendar grid with clickable dates
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    # Empty cell
                    st.markdown('<div class="calendar-day calendar-day-empty" style="height: 100px;"></div>', unsafe_allow_html=True)
                else:
                    # Check if this day has appointment
                    day_date = datetime(selected_year, selected_month, day).strftime('%Y-%m-%d')
                    has_appointment = day_date in appointments_by_date
                    
                    # Check if today
                    is_today = (day == today.day and selected_month == today.month and selected_year == today.year)
                    
                    # Determine style
                    if has_appointment:
                        css_class = "calendar-day calendar-day-appointment"
                    elif is_today:
                        css_class = "calendar-day calendar-day-today"
                    else:
                        css_class = "calendar-day"
                    
                    # Create clickable button
                    if has_appointment:
                        if st.button(f"{day}", key=f"day_{day_date}", use_container_width=True):
                            st.session_state.selected_appointment_date = day_date
                        st.markdown(f"""
                        <div class="{css_class}">
                            <div class="calendar-day-number">{day}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="{css_class}">
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
    
    # Show selected appointment details
    if 'selected_appointment_date' in st.session_state and st.session_state.selected_appointment_date in appointments_by_date:
        apt = appointments_by_date[st.session_state.selected_appointment_date]
        date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        display_date = date_obj.strftime('%d %B %Y')
        day_name = date_obj.strftime('%A')
        
        st.markdown("### 📋 Selected Appointment Details")
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1565c0 0%, #1e88e5 100%); 
                    padding: 20px; border-radius: 10px; color: white; margin-bottom: 20px;'>
            <h3>📅 {display_date} ({day_name})</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**👤 Patient Name:** {apt['patient_name']}")
            st.markdown(f"**🎂 Age:** {apt.get('patient_age', 'N/A')}")
            if apt.get('patient_phone'):
                st.markdown(f"**📱 Phone:** {apt['patient_phone']}")
            if apt.get('patient_village'):
                st.markdown(f"**📍 Village:** {apt['patient_village']}")
        with col2:
            st.markdown(f"**📝 Reason:** {apt.get('reason', 'Not specified')}")
            st.markdown(f"**🕐 Booked On:** {apt.get('created_at', 'N/A')[:10]}")
            st.markdown(f"**🆔 Appointment ID:** {apt['id']}")
            st.markdown(f"**📊 Status:** {apt.get('status', 'scheduled').upper()}")
        
        if st.button("❌ Clear Selection"):
            del st.session_state.selected_appointment_date
            st.rerun()
    
    # List all appointments
    st.markdown("### 📋 All Appointments This Month")
    
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

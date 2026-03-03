# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client
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
    
    /* Remove default streamlit padding */
    .block-container {
        padding-top: 2rem;
    }
    
    /* Remove extra spacing between column groups */
    div[data-testid="column"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Calendar day button styling */
    div[data-testid="column"] > div > div > div > button {
        width: 100% !important;
        height: 80px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        margin: 3px 0 !important;
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
        max_value=datetime(2030, 12, 31),
        key="month_selector"
    )
    selected_month = selected_date.month
    selected_year = selected_date.year

# Clear selected appointment when month changes
if 'last_selected_month' not in st.session_state:
    st.session_state.last_selected_month = selected_month
    st.session_state.last_selected_year = selected_year
elif st.session_state.last_selected_month != selected_month or st.session_state.last_selected_year != selected_year:
    if 'selected_appointment_date' in st.session_state:
        del st.session_state.selected_appointment_date
    st.session_state.last_selected_month = selected_month
    st.session_state.last_selected_year = selected_year

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
    
    # Show today's date and selected month
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### 📅 Today: {today.strftime('%d %B %Y (%A)')}")
    with col2:
        st.markdown(f"### 📆 Viewing: {calendar.month_name[selected_month]} {selected_year}")
    
    st.markdown("")
    
    # Get calendar matrix
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # Create calendar container to control spacing
    calendar_container = st.container()
    
    with calendar_container:
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        cols = st.columns(7)
        for i, day in enumerate(days):
            with cols[i]:
                st.markdown(f"<div style='text-align: center; font-weight: bold; padding: 10px; background-color: #262730; border-radius: 5px; margin-bottom: 3px;'>{day}</div>", unsafe_allow_html=True)
        
        # Calendar grid
        for week_idx, week in enumerate(cal):
            cols = st.columns(7)
            for day_idx, day in enumerate(week):
                with cols[day_idx]:
                    if day == 0:
                        # Empty cell with same height as buttons
                        st.markdown("<div style='height: 86px; margin: 3px 0;'></div>", unsafe_allow_html=True)
                    else:
                        # Check if this day has appointment
                        day_date = datetime(selected_year, selected_month, day).strftime('%Y-%m-%d')
                        has_appointment = day_date in appointments_by_date
                        
                        # Check if today
                        is_today = (day == today.day and selected_month == today.month and selected_year == today.year)
                        
                        # Determine button type and color
                        if has_appointment:
                            button_type = "primary"
                            if st.button(str(day), key=f"day_{week_idx}_{day_idx}", use_container_width=True, type=button_type):
                                st.session_state.selected_appointment_date = day_date
                                st.rerun()
                        else:
                            # Regular day (including today) - no special highlight
                            st.button(str(day), key=f"day_{week_idx}_{day_idx}", use_container_width=True, disabled=True)
    
    st.markdown("---")
    
    # Legend
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("🔵 **Blue** = Appointment (Click to view)")
    with col2:
        st.metric("📊 Total Appointments", len(month_appointments))
    
    st.markdown("---")
    
    # Show selected appointment details
    if 'selected_appointment_date' in st.session_state and st.session_state.selected_appointment_date in appointments_by_date:
        apt = appointments_by_date[st.session_state.selected_appointment_date]
        date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        display_date = date_obj.strftime('%d %B %Y')
        day_name = date_obj.strftime('%A')
        
        st.markdown("### 📋 Appointment Details")
        
        # Appointment card
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #1565c0 0%, #1e88e5 100%); 
                    padding: 25px; border-radius: 12px; color: white; margin-bottom: 20px;'>
            <h2 style='margin: 0 0 10px 0;'>📅 {display_date}</h2>
            <h3 style='margin: 0; opacity: 0.9;'>{day_name}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 👤 Patient Information")
            st.markdown(f"**Name:** {apt['patient_name']}")
            if apt.get('patient_phone'):
                st.markdown(f"**Phone:** {apt['patient_phone']}")
            if apt.get('patient_village'):
                st.markdown(f"**Village:** {apt['patient_village']}")
        
        with col2:
            st.markdown("#### 📝 Appointment Information")
            st.markdown(f"**Reason:** {apt.get('reason', 'Not specified')}")
            st.markdown(f"**Booked On:** {apt.get('created_at', 'N/A')[:10]}")
            st.markdown(f"**Status:** {apt.get('status', 'scheduled').upper()}")
            st.markdown(f"**ID:** {apt['id']}")
        
        if st.button("❌ Close Details", type="secondary"):
            del st.session_state.selected_appointment_date
            st.rerun()
        
        st.markdown("---")
    
    # List all appointments
    if month_appointments:
        st.markdown("### 📋 All Appointments This Month")
        
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

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
    page_title="All Appointments - Admin",
    page_icon="📅",
    layout="wide"
)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    return create_client(url, key)

supabase = init_supabase()

st.title("📅 All Appointments (Admin View)")
st.markdown("### View appointments from all doctors")

# Filters
col1, col2, col3 = st.columns(3)

with col1:
    # Doctor filter
    doctors_response = supabase.table('doctors').select('phone, name').eq('active', True).execute()
    doctors = doctors_response.data if doctors_response.data else []
    doctor_options = ['All Doctors'] + [f"Dr. {d['name']} ({d['phone']})" for d in doctors]
    selected_doctor = st.selectbox("👨‍⚕️ Filter by Doctor", doctor_options)

with col2:
    # Status filter
    status_options = ['All Status', 'scheduled', 'completed', 'cancelled_by_patient', 'cancelled_by_doctor']
    selected_status = st.selectbox("📊 Filter by Status", status_options)

with col3:
    # Month filter
    selected_date = st.date_input(
        "📆 Select Month",
        value=datetime.now(),
        min_value=datetime(2024, 1, 1),
        max_value=datetime(2030, 12, 31)
    )
    selected_month = selected_date.month
    selected_year = selected_date.year

try:
    # Get all appointments
    appointments_response = supabase.table("appointments").select("*").execute()
    all_appointments = appointments_response.data if appointments_response.data else []
    
    # Apply filters
    filtered_appointments = all_appointments
    
    # Filter by doctor
    if selected_doctor != 'All Doctors':
        doctor_phone = selected_doctor.split('(')[1].split(')')[0]
        filtered_appointments = [apt for apt in filtered_appointments if apt['doctor_phone'] == doctor_phone]
    
    # Filter by status
    if selected_status != 'All Status':
        filtered_appointments = [apt for apt in filtered_appointments if apt['status'] == selected_status]
    
    # Filter by month
    month_appointments = []
    for apt in filtered_appointments:
        apt_date = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
        if apt_date.month == selected_month and apt_date.year == selected_year:
            month_appointments.append(apt)
    
    # Statistics
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_count = len(month_appointments)
    scheduled_count = len([a for a in month_appointments if a['status'] == 'scheduled'])
    completed_count = len([a for a in month_appointments if a['status'] == 'completed'])
    cancelled_count = len([a for a in month_appointments if a['status'] in ['cancelled_by_patient', 'cancelled_by_doctor']])
    
    with col1:
        st.metric("📅 Total", total_count)
    with col2:
        st.metric("🟢 Scheduled", scheduled_count)
    with col3:
        st.metric("✅ Completed", completed_count)
    with col4:
        st.metric("❌ Cancelled", cancelled_count)
    
    st.markdown("---")
    
    # Calendar view
    st.markdown(f"### 📆 {calendar.month_name[selected_month]} {selected_year} Calendar")
    
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
                    # Check if this day has appointments
                    day_date = datetime(selected_year, selected_month, day).strftime('%Y-%m-%d')
                    day_appointments = [apt for apt in month_appointments if apt['appointment_date'] == day_date]
                    
                    if day_appointments:
                        # Count appointments by status
                        scheduled = len([a for a in day_appointments if a['status'] == 'scheduled'])
                        
                        # Highlight day with appointments
                        st.markdown(f"""
                        <div style='background-color: #1e88e5; padding: 10px; border-radius: 5px; text-align: center;'>
                            <div style='font-size: 20px; font-weight: bold;'>{day}</div>
                            <div style='font-size: 12px;'>📅 {len(day_appointments)} apt(s)</div>
                            <div style='font-size: 10px;'>🟢 {scheduled}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Regular day
                        today = datetime.now()
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
        
        # Create DataFrame for better display
        df_data = []
        for apt in month_appointments:
            date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
            display_date = date_obj.strftime('%d %b %Y')
            day_name = date_obj.strftime('%A')
            
            status_emoji = {
                'scheduled': '🟢',
                'completed': '✅',
                'cancelled_by_patient': '❌',
                'cancelled_by_doctor': '🚫'
            }.get(apt['status'], '❓')
            
            df_data.append({
                'ID': apt['id'],
                'Date': f"{display_date} ({day_name})",
                'Patient': apt['patient_name'],
                'Phone': apt.get('patient_phone', 'N/A'),
                'Village': apt.get('patient_village', 'N/A'),
                'Doctor': f"Dr. {apt['doctor_name']}",
                'PHC': apt.get('doctor_phc', 'N/A'),
                'Reason': apt.get('reason', 'Not specified')[:50],
                'Status': f"{status_emoji} {apt['status']}",
                'Booked': apt.get('created_at', 'N/A')[:10]
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"appointments_{selected_month}_{selected_year}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"📭 No appointments found for the selected filters")

except Exception as e:
    st.error(f"❌ Error loading appointments: {e}")
    st.exception(e)

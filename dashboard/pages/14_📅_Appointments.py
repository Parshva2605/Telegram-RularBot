# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client
import pandas as pd
from datetime import datetime, timedelta

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
    doctor_options = ['All Doctors'] + [f"Dr. {d['name']}" for d in doctors]
    selected_doctor = st.selectbox("👨‍⚕️ Filter by Doctor", doctor_options)

with col2:
    # Status filter
    status_options = ['All Status', 'scheduled', 'completed', 'cancelled_by_patient', 'cancelled_by_doctor']
    selected_status = st.selectbox("📊 Filter by Status", status_options)

with col3:
    # Date range filter
    date_range = st.selectbox("📆 Date Range", ['All Time', 'Today', 'This Week', 'This Month', 'Next 7 Days', 'Next 30 Days'])

try:
    # Get all appointments
    appointments_response = supabase.table("appointments").select("*").order("appointment_date", desc=False).execute()
    all_appointments = appointments_response.data if appointments_response.data else []
    
    # Apply filters
    filtered_appointments = all_appointments
    
    # Filter by doctor
    if selected_doctor != 'All Doctors':
        doctor_name = selected_doctor.replace('Dr. ', '')
        filtered_appointments = [apt for apt in filtered_appointments if apt['doctor_name'] == doctor_name]
    
    # Filter by status
    if selected_status != 'All Status':
        filtered_appointments = [apt for apt in filtered_appointments if apt['status'] == selected_status]
    
    # Filter by date range
    today = datetime.now().date()
    if date_range == 'Today':
        filtered_appointments = [apt for apt in filtered_appointments if datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date() == today]
    elif date_range == 'This Week':
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        filtered_appointments = [apt for apt in filtered_appointments if week_start <= datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date() <= week_end]
    elif date_range == 'This Month':
        filtered_appointments = [apt for apt in filtered_appointments if datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date().month == today.month and datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date().year == today.year]
    elif date_range == 'Next 7 Days':
        next_week = today + timedelta(days=7)
        filtered_appointments = [apt for apt in filtered_appointments if today <= datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date() <= next_week]
    elif date_range == 'Next 30 Days':
        next_month = today + timedelta(days=30)
        filtered_appointments = [apt for apt in filtered_appointments if today <= datetime.strptime(apt['appointment_date'], '%Y-%m-%d').date() <= next_month]
    
    st.markdown("---")
    
    # Statistics
    st.markdown("### 📊 Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    total_count = len(filtered_appointments)
    scheduled_count = len([a for a in filtered_appointments if a['status'] == 'scheduled'])
    completed_count = len([a for a in filtered_appointments if a['status'] == 'completed'])
    cancelled_count = len([a for a in filtered_appointments if a['status'] in ['cancelled_by_patient', 'cancelled_by_doctor']])
    
    with col1:
        st.metric("📅 Total", total_count)
    with col2:
        st.metric("🟢 Scheduled", scheduled_count)
    with col3:
        st.metric("✅ Completed", completed_count)
    with col4:
        st.metric("❌ Cancelled", cancelled_count)
    
    st.markdown("---")
    
    # List all appointments
    st.markdown("### 📋 Appointment Details")
    
    if filtered_appointments:
        # Sort by date
        filtered_appointments.sort(key=lambda x: x['appointment_date'])
        
        for apt in filtered_appointments:
            date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
            display_date = date_obj.strftime('%d %B %Y')
            day_name = date_obj.strftime('%A')
            
            # Status emoji
            status_emoji = {
                'scheduled': '🟢',
                'completed': '✅',
                'cancelled_by_patient': '❌',
                'cancelled_by_doctor': '🚫'
            }.get(apt['status'], '❓')
            
            # Status color
            status_color = {
                'scheduled': '#1565c0',
                'completed': '#2e7d32',
                'cancelled_by_patient': '#c62828',
                'cancelled_by_doctor': '#f57c00'
            }.get(apt['status'], '#666')
            
            with st.expander(f"{status_emoji} {display_date} ({day_name}) - Dr. {apt['doctor_name']} - {apt['patient_name']}", expanded=False):
                # Appointment card
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, {status_color} 0%, {status_color}dd 100%); 
                            padding: 20px; border-radius: 10px; color: white; margin-bottom: 15px;'>
                    <h3 style='margin: 0 0 10px 0;'>📅 {display_date} ({day_name})</h3>
                    <p style='margin: 0; font-size: 18px;'>{status_emoji} Status: {apt['status'].upper().replace('_', ' ')}</p>
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
                    st.markdown(f"**Telegram ID:** {apt.get('patient_telegram_id', 'N/A')}")
                
                with col2:
                    st.markdown("#### 👨‍⚕️ Doctor & Appointment Info")
                    st.markdown(f"**Doctor:** Dr. {apt['doctor_name']}")
                    st.markdown(f"**PHC:** {apt.get('doctor_phc', 'N/A')}")
                    st.markdown(f"**Doctor Phone:** {apt['doctor_phone']}")
                    st.markdown(f"**Reason:** {apt.get('reason', 'Not specified')}")
                    st.markdown(f"**Booked On:** {apt.get('created_at', 'N/A')[:10]}")
                    st.markdown(f"**Appointment ID:** {apt['id']}")
                    st.markdown(f"**Reminder Sent:** {'Yes' if apt.get('reminder_sent') else 'No'}")
        
        st.markdown("---")
        
        # Download as CSV
        st.markdown("### 📥 Export Data")
        df_data = []
        for apt in filtered_appointments:
            date_obj = datetime.strptime(apt['appointment_date'], '%Y-%m-%d')
            display_date = date_obj.strftime('%d %b %Y')
            day_name = date_obj.strftime('%A')
            
            df_data.append({
                'ID': apt['id'],
                'Date': f"{display_date} ({day_name})",
                'Patient Name': apt['patient_name'],
                'Patient Phone': apt.get('patient_phone', 'N/A'),
                'Patient Village': apt.get('patient_village', 'N/A'),
                'Doctor': f"Dr. {apt['doctor_name']}",
                'Doctor Phone': apt['doctor_phone'],
                'PHC': apt.get('doctor_phc', 'N/A'),
                'Reason': apt.get('reason', 'Not specified'),
                'Status': apt['status'],
                'Booked On': apt.get('created_at', 'N/A')[:10],
                'Reminder Sent': 'Yes' if apt.get('reminder_sent') else 'No'
            })
        
        df = pd.DataFrame(df_data)
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Appointments as CSV",
            data=csv,
            file_name=f"appointments_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info(f"📭 No appointments found for the selected filters")

except Exception as e:
    st.error(f"❌ Error loading appointments: {e}")
    st.exception(e)

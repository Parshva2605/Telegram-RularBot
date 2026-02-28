# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

st.set_page_config(page_title="Appointments", page_icon="📅", layout="wide")

st.markdown("""
<style>
    .main {background-color: #f0f8ff;}
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 10px;
        padding: 8px 16px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

st.title("📅 Appointments Management")
st.markdown("### View and Manage Patient Appointments")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Appointments", "📆 Calendar View", "📊 Statistics"])

with tab1:
    st.markdown("#### All Scheduled Appointments")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("🔍 Search by username or hospital", "")
    with col2:
        filter_date = st.selectbox("Filter by", ["All", "Today", "This Week", "This Month"])
    with col3:
        sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Hospital"])
    
    try:
        response = supabase.table('appointments').select('*').execute()
        appointments = response.data
        
        if appointments:
            # Filter by search
            if search:
                appointments = [a for a in appointments if 
                              search.lower() in a.get('username', '').lower() or
                              search.lower() in a.get('hospital', '').lower()]
            
            # Filter by date
            today = datetime.now().strftime('%d-%m-%Y')
            if filter_date == "Today":
                appointments = [a for a in appointments if a.get('date') == today]
            elif filter_date == "This Week":
                # Simple week filter (next 7 days)
                appointments = [a for a in appointments if a.get('date', '') >= today]
            
            # Sort
            if sort_by == "Date (Newest)":
                appointments = sorted(appointments, key=lambda x: x.get('date', ''), reverse=True)
            elif sort_by == "Date (Oldest)":
                appointments = sorted(appointments, key=lambda x: x.get('date', ''))
            elif sort_by == "Hospital":
                appointments = sorted(appointments, key=lambda x: x.get('hospital', ''))
            
            st.info(f"📊 Showing {len(appointments)} appointments")
            
            # Display appointments
            for appointment in appointments:
                with st.expander(f"📅 {appointment.get('date')} - {appointment.get('username')} at {appointment.get('hospital')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Patient Details:**
                        - 👤 Username: {appointment.get('username', 'N/A')}
                        - 🆔 User ID: {appointment.get('user_id', 'N/A')}
                        - 📅 Date: {appointment.get('date', 'N/A')}
                        - ⏰ Time: {appointment.get('time', 'N/A')}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Appointment Details:**
                        - 🏥 Hospital: {appointment.get('hospital', 'N/A')}
                        - 📝 Notes: {appointment.get('notes', 'No notes')}
                        - 🔔 Reminder Sent: {'Yes' if appointment.get('reminder_sent') else 'No'}
                        - 🕐 Created: {appointment.get('created', 'N/A')}
                        """)
                    
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("❌ Cancel", key=f"cancel_{appointment['id']}", use_container_width=True):
                            supabase.table('appointments').delete().eq('id', appointment['id']).execute()
                            st.success("Appointment cancelled!")
                            st.rerun()
                    
                    with col2:
                        if not appointment.get('reminder_sent'):
                            if st.button("🔔 Send Reminder", key=f"remind_{appointment['id']}", use_container_width=True):
                                supabase.table('appointments').update({'reminder_sent': True}).eq('id', appointment['id']).execute()
                                st.success("Reminder sent!")
                                st.rerun()
        else:
            st.info("No appointments scheduled")
    
    except Exception as e:
        st.error(f"Error loading appointments: {e}")

with tab2:
    st.markdown("#### Calendar View")
    
    try:
        response = supabase.table('appointments').select('*').execute()
        appointments = response.data
        
        if appointments:
            # Group by date
            appointments_by_date = {}
            for appointment in appointments:
                date = appointment.get('date', 'Unknown')
                if date not in appointments_by_date:
                    appointments_by_date[date] = []
                appointments_by_date[date].append(appointment)
            
            # Sort dates
            sorted_dates = sorted(appointments_by_date.keys())
            
            # Display calendar
            for date in sorted_dates:
                date_appointments = appointments_by_date[date]
                
                # Check if today
                today = datetime.now().strftime('%d-%m-%Y')
                is_today = date == today
                
                header = f"📅 {date}" + (" - TODAY" if is_today else "")
                st.markdown(f"### {header}")
                
                for appointment in date_appointments:
                    col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                    
                    with col1:
                        st.markdown(f"⏰ **{appointment.get('time', 'N/A')}**")
                    
                    with col2:
                        st.markdown(f"👤 {appointment.get('username', 'Unknown')}")
                    
                    with col3:
                        st.markdown(f"🏥 {appointment.get('hospital', 'N/A')}")
                    
                    with col4:
                        if st.button("❌", key=f"cal_cancel_{appointment['id']}"):
                            supabase.table('appointments').delete().eq('id', appointment['id']).execute()
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("No appointments to display")
    
    except Exception as e:
        st.error(f"Error loading calendar: {e}")

with tab3:
    st.markdown("#### Appointment Statistics")
    
    try:
        response = supabase.table('appointments').select('*').execute()
        appointments = response.data
        
        if appointments:
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(appointments)
            today = datetime.now().strftime('%d-%m-%Y')
            today_appointments = len([a for a in appointments if a.get('date') == today])
            
            # Count by hospital
            hospitals = {}
            for appointment in appointments:
                hospital = appointment.get('hospital', 'Unknown')
                hospitals[hospital] = hospitals.get(hospital, 0) + 1
            
            most_popular = max(hospitals, key=hospitals.get) if hospitals else "N/A"
            
            # Reminder stats
            reminders_sent = len([a for a in appointments if a.get('reminder_sent')])
            
            with col1:
                st.metric("Total Appointments", total)
            with col2:
                st.metric("📅 Today", today_appointments)
            with col3:
                st.metric("🔔 Reminders Sent", reminders_sent)
            with col4:
                st.metric("Most Popular Hospital", most_popular, label_visibility="visible")
            
            # Hospital breakdown
            st.markdown("#### Appointments by Hospital")
            hospital_df = pd.DataFrame(list(hospitals.items()), columns=['Hospital', 'Count'])
            hospital_df = hospital_df.sort_values('Count', ascending=False)
            st.dataframe(hospital_df, use_container_width=True)
            
            # Upcoming appointments
            st.markdown("#### Upcoming This Week")
            upcoming = [a for a in appointments if a.get('date', '') >= today]
            upcoming = sorted(upcoming, key=lambda x: x.get('date', ''))[:10]
            
            for appointment in upcoming:
                st.markdown(f"📅 **{appointment.get('date')}** at {appointment.get('time')} - {appointment.get('username')} → {appointment.get('hospital')}")
        else:
            st.info("No appointment data available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

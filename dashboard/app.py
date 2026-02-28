# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="MediMind Admin Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1565c0;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-value {
        font-size: 48px;
        font-weight: bold;
        margin: 10px 0;
    }
    .metric-label {
        font-size: 18px;
        opacity: 0.9;
    }
    h1 {
        color: #1e88e5;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    if not url or not key:
        st.error("⚠️ Supabase credentials not found in .env file!")
        return None
    return create_client(url, key)

supabase = init_supabase()

# Main content
st.title("🏥 MediMind Rural - Admin Dashboard")
st.markdown("### Welcome to the Control Center")

if not supabase:
    st.error("❌ Cannot connect to Supabase. Please check your .env file.")
    st.stop()

# Metrics cards
col1, col2, col3, col4 = st.columns(4)

try:
    # Get data
    emergencies_data = supabase.table('emergencies').select('*').execute()
    workers_data = supabase.table('health_workers').select('*').execute()
    appointments_data = supabase.table('appointments').select('*').execute()
    reminders_data = supabase.table('reminders').select('*').eq('active', True).execute()
    
    total_emergencies = len(emergencies_data.data) if emergencies_data.data else 0
    pending_emergencies = len([e for e in emergencies_data.data if e.get('status') == 'pending']) if emergencies_data.data else 0
    total_workers = len(workers_data.data) if workers_data.data else 0
    approved_workers = len([w for w in workers_data.data if w.get('approved') == True]) if workers_data.data else 0
    total_appointments = len(appointments_data.data) if appointments_data.data else 0
    active_reminders = len(reminders_data.data) if reminders_data.data else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">🚨 Emergencies</div>
            <div class="metric-value">{pending_emergencies}</div>
            <div class="metric-label">Pending / {total_emergencies} Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">👥 Health Workers</div>
            <div class="metric-value">{approved_workers}</div>
            <div class="metric-label">Approved / {total_workers} Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">📅 Appointments</div>
            <div class="metric-value">{total_appointments}</div>
            <div class="metric-label">Scheduled</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <div class="metric-label">💊 Reminders</div>
            <div class="metric-value">{active_reminders}</div>
            <div class="metric-label">Active</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Live Emergency Map
    st.markdown("### 🗺️ Live Emergency Map")
    
    if emergencies_data.data:
        # Create map centered on Gujarat
        m = folium.Map(location=[22.5, 72.5], zoom_start=8)
        
        # Add emergency markers
        for emergency in emergencies_data.data:
            if emergency.get('lat') and emergency.get('lon'):
                status = emergency.get('status', 'pending')
                
                # Set icon based on status
                if status == 'pending':
                    # Red exclamation mark for pending
                    icon = folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')
                else:
                    # Green checkmark for resolved
                    icon = folium.Icon(color='green', icon='check', prefix='fa')
                
                # Create popup with status indicator
                status_emoji = "🔴 PENDING" if status == 'pending' else "✅ RESOLVED"
                
                folium.Marker(
                    location=[emergency['lat'], emergency['lon']],
                    popup=f"""
                    <b>Emergency #{emergency['id']}</b><br>
                    <b>{status_emoji}</b><br>
                    User: {emergency.get('username', 'Unknown')}<br>
                    Time: {emergency.get('timestamp', 'N/A')}
                    """,
                    icon=icon
                ).add_to(m)
        
        folium_static(m, width=1200, height=400)
    else:
        st.info("📍 No emergency locations to display")
    
    # Recent Activity
    st.markdown("### 📋 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Latest Emergencies")
        if emergencies_data.data:
            recent_emergencies = sorted(emergencies_data.data, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            for emergency in recent_emergencies:
                status_emoji = "🔴" if emergency.get('status') == 'pending' else "🟢"
                st.markdown(f"""
                {status_emoji} **{emergency.get('username', 'Unknown')}** - {emergency.get('status', 'pending')}  
                📍 Location: {emergency.get('lat', 'N/A')}, {emergency.get('lon', 'N/A')}  
                🕐 {emergency.get('timestamp', 'N/A')}
                """)
                st.markdown("---")
        else:
            st.info("No emergencies recorded")
    
    with col2:
        st.markdown("#### 📅 Upcoming Appointments")
        if appointments_data.data:
            today = datetime.now().strftime('%d-%m-%Y')
            upcoming = [a for a in appointments_data.data if a.get('date', '') >= today]
            upcoming = sorted(upcoming, key=lambda x: x.get('date', ''))[:5]
            
            for appointment in upcoming:
                st.markdown(f"""
                📅 **{appointment.get('date', 'N/A')}** at {appointment.get('time', 'N/A')}  
                👤 {appointment.get('username', 'Unknown')}  
                🏥 {appointment.get('hospital', 'N/A')}  
                📝 {appointment.get('notes', 'No notes')}
                """)
                st.markdown("---")
        else:
            st.info("No upcoming appointments")

except Exception as e:
    st.error(f"❌ Error loading dashboard data: {e}")
    st.exception(e)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🏥 MediMind Rural Admin Dashboard v1.0</p>
    <p>Made with ❤️ for Rural Gujarat Healthcare</p>
</div>
""", unsafe_allow_html=True)

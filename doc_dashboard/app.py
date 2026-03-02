# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="MediMind Doctor Dashboard",
    page_icon="👨‍⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'doctor_phone' not in st.session_state:
    st.session_state.doctor_phone = None
if 'doctor_name' not in st.session_state:
    st.session_state.doctor_name = None

# Login page
if not st.session_state.logged_in:
    st.title("👨‍⚕️ MediMind Doctor Dashboard")
    st.markdown("### Login to Access Your Dashboard")
    
    with st.form("login_form"):
        phone = st.text_input("📱 Phone Number", placeholder="+919876543210")
        access_code = st.text_input("🔐 Access Code", type="password", placeholder="Enter your 8-digit code")
        submit = st.form_submit_button("🔓 Login")
        
        if submit:
            if not phone or not access_code:
                st.error("❌ Please enter both phone and access code")
            else:
                try:
                    # Verify doctor credentials
                    doctor_response = supabase.table('doctors').select('*').eq('phone', phone).eq('access_code', access_code).execute()
                    
                    if doctor_response.data and len(doctor_response.data) > 0:
                        doctor = doctor_response.data[0]
                        
                        # Check if doctor is active
                        if doctor.get('active'):
                            st.session_state.logged_in = True
                            st.session_state.doctor_phone = phone
                            st.session_state.doctor_name = doctor.get('name')
                            st.session_state.doctor_data = doctor
                            st.success(f"✅ Welcome, Dr. {doctor.get('name')}!")
                            st.rerun()
                        else:
                            st.error("❌ Your account is inactive. Please contact admin.")
                    else:
                        st.error("❌ Invalid phone number or access code")
                except Exception as e:
                    st.error(f"❌ Login error: {e}")
    
    st.markdown("---")
    st.info("💡 Get your access code from the Doctor Bot (@MediMindDoctorBot)")
    st.stop()

# Logged in - Show dashboard
st.title(f"👨‍⚕️ Welcome, Dr. {st.session_state.doctor_name}")

# Logout button in sidebar
with st.sidebar:
    st.markdown(f"### 👤 Dr. {st.session_state.doctor_name}")
    st.markdown(f"📱 {st.session_state.doctor_phone}")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.doctor_phone = None
        st.session_state.doctor_name = None
        st.rerun()

# Dashboard metrics
col1, col2, col3 = st.columns(3)

try:
    phone = st.session_state.doctor_phone
    
    # Get doctor's statistics
    pending_requests = supabase.table("xray_requests").select("id").eq("doctor_phone", phone).eq("status", "pending").execute()
    reviewed_requests = supabase.table("xray_requests").select("id").eq("doctor_phone", phone).eq("status", "reviewed").execute()
    appointments = supabase.table("appointments").select("*").eq("doctor_phone", phone).eq("status", "scheduled").execute()
    
    pending_count = len(pending_requests.data) if pending_requests.data else 0
    reviewed_count = len(reviewed_requests.data) if reviewed_requests.data else 0
    total_cases = pending_count + reviewed_count
    appointments_count = len(appointments.data) if appointments.data else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-label">🔴 Pending</div>
            <div class="metric-value">{pending_count}</div>
            <div class="metric-label">X-Ray Requests</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
            <div class="metric-label">✅ Reviewed</div>
            <div class="metric-value">{reviewed_count}</div>
            <div class="metric-label">Total Cases</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
            <div class="metric-label">📅 Appointments</div>
            <div class="metric-value">{appointments_count}</div>
            <div class="metric-label">Scheduled</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Quick stats
    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📈 Total Cases", total_cases)
        st.metric("⭐ Rating", f"{st.session_state.doctor_data.get('rating', 0.0)}/5.0")
    
    with col2:
        st.metric("🏥 PHC", st.session_state.doctor_data.get('phc', 'N/A'))
        st.metric("🆔 MCI", st.session_state.doctor_data.get('mci_number', 'N/A'))

except Exception as e:
    st.error(f"❌ Error loading dashboard: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>👨‍⚕️ MediMind Doctor Dashboard v1.0</p>
    <p>Made with ❤️ for Rural Gujarat Healthcare</p>
</div>
""", unsafe_allow_html=True)

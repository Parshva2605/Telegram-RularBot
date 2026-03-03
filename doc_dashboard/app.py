# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="MediMind Doctor Portal",
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
    h1 {
        color: #1e88e5;
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #262730;
    }
    /* Make sidebar navigation always visible */
    [data-testid="stSidebarNav"] {
        max-height: none !important;
    }
    /* Hide the collapse arrow completely */
    [data-testid="stSidebarNavCollapseIcon"] {
        display: none !important;
    }
    /* Hide the collapse button */
    button[kind="header"] {
        display: none !important;
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

# Main page
st.title("👨‍⚕️ MediMind Doctor Portal")
st.markdown("### Welcome to the Doctor Dashboard")

st.markdown("""
## 📋 Available Features

Navigate using the sidebar to access:

1. **📅 My Appointments** - View your scheduled appointments in calendar format
2. **👨‍⚕️ Doctor Dashboard** - Login to access your X-ray queue and reports
3. **🩻 X-Ray Requests** - View and manage X-ray analysis requests
4. **📄 Reports** - Access all generated PDF reports

---

## 🔐 Getting Started

1. Click on **"👨‍⚕️ Doctor Dashboard"** in the sidebar
2. Login with your phone number and access code
3. Access your queue, reports, and statistics

💡 **Get your access code from @MediMindDoctorBot on Telegram**

---

## 📱 Quick Links

- **Telegram Bot**: @MediMindDoctorBot
- **Patient Bot**: @MediMindRuralBot
- **Support**: Contact admin for assistance

""")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>👨‍⚕️ MediMind Doctor Portal v1.0</p>
    <p>Made with ❤️ for Rural Gujarat Healthcare</p>
</div>
""", unsafe_allow_html=True)

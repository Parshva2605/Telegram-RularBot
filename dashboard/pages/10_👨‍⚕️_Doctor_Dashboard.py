# -*- coding: utf-8 -*-
"""
MediMind Doctor Dashboard
Login with phone + access code → View queue → Manage reports
"""

import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Doctor Dashboard", page_icon="👨‍⚕️", layout="wide")

st.markdown("""
<style>
    .main {background-color: #0e1117;}
    .stButton>button {
        background-color: #1e88e5;
        color: white;
        border-radius: 10px;
        padding: 8px 16px;
        border: none;
    }
    .doctor-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
    .queue-card {
        background: #1e1e1e;
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
    .reviewed-card {
        background: #1e1e1e;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
def get_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = get_supabase()

# Session state initialization
if 'doctor_logged_in' not in st.session_state:
    st.session_state.doctor_logged_in = False
if 'doctor_phone' not in st.session_state:
    st.session_state.doctor_phone = None
if 'doctor_name' not in st.session_state:
    st.session_state.doctor_name = None
if 'doctor_data' not in st.session_state:
    st.session_state.doctor_data = None

# Logout function
def logout():
    st.session_state.doctor_logged_in = False
    st.session_state.doctor_phone = None
    st.session_state.doctor_name = None
    st.session_state.doctor_data = None

# ============================================
# LOGIN PAGE
# ============================================
if not st.session_state.doctor_logged_in:
    st.title("🩻 MediMind Doctor Dashboard")
    st.markdown("### 🔐 Doctor Login")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        phone = st.text_input("📱 Phone Number", placeholder="+919876543210", help="Enter your registered phone number")
    
    with col2:
        code = st.text_input("🔐 Access Code", type="password", placeholder="X7K9P2M4", help="8-character code from Telegram bot")
    
    st.markdown("")
    
    if st.button("🔓 Login", type="primary", use_container_width=True):
        if phone and code:
            try:
                # Query doctor from database
                response = supabase.table("doctors").select("*").eq("phone", phone).eq("access_code", code).execute()
                
                if response.data and len(response.data) > 0:
                    doctor = response.data[0]
                    
                    # Update session state
                    st.session_state.doctor_logged_in = True
                    st.session_state.doctor_phone = phone
                    st.session_state.doctor_name = doctor.get('name', 'Doctor')
                    st.session_state.doctor_data = doctor
                    
                    # Update last login
                    supabase.table("doctors").update({
                        "last_login": datetime.now().isoformat()
                    }).eq("phone", phone).execute()
                    
                    st.success(f"✅ Welcome Dr. {doctor.get('name')}!")
                    st.rerun()
                else:
                    st.error("❌ Invalid phone number or access code")
            except Exception as e:
                st.error(f"❌ Login error: {str(e)}")
        else:
            st.warning("⚠️ Please enter both phone number and access code")
    
    st.markdown("---")
    st.info("💡 **Don't have an access code?** Register via Telegram bot @MediMindDoctorBot")

# ============================================
# DASHBOARD (After Login)
# ============================================
else:
    doctor = st.session_state.doctor_data
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="doctor-card">
            <h3>👨‍⚕️ {st.session_state.doctor_name}</h3>
            <p>📱 {st.session_state.doctor_phone}</p>
            <p>🏥 {doctor.get('phc', 'N/A')}</p>
            <p>🩺 MCI: {doctor.get('mci_reg', 'N/A')}</p>
            <p>⭐ Rating: {doctor.get('rating', 0):.1f}/5.0</p>
            <p>📊 Cases: {doctor.get('total_cases', 0)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Main content
    st.title("🩻 MediMind Doctor Dashboard")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Live Queue", "📊 My Reports", "📈 Statistics"])
    
    # ============================================
    # TAB 1: LIVE QUEUE
    # ============================================
    with tab1:
        st.header("📋 Live X-Ray Queue")
        st.markdown("Pending X-ray requests assigned to you")
        
        try:
            # Get pending requests
            queue_response = supabase.table("xray_requests").select("*").eq("doctor_phone", st.session_state.doctor_phone).eq("status", "pending").order("created_at", desc=True).execute()
            
            if queue_response.data and len(queue_response.data) > 0:
                st.success(f"📊 {len(queue_response.data)} pending request(s)")
                
                # Display as cards
                for req in queue_response.data:
                    with st.container():
                        st.markdown(f"""
                        <div class="queue-card">
                            <h4>👤 {req['patient_name']} ({req['age']}y)</h4>
                            <p>📍 Village: {req.get('village', 'N/A')}</p>
                            <p>🩺 Symptoms: {req.get('symptoms', 'N/A')}</p>
                            <p>📅 Requested: {req.get('created_at', 'N/A')}</p>
                            <p>🆔 Request ID: {req['id']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if req.get('image_url'):
                                st.markdown(f"[🖼️ View X-Ray Image]({req['image_url']})")
                            else:
                                st.info("📤 Image not uploaded yet")
                        
                        with col2:
                            if st.button(f"✅ Mark Reviewed", key=f"review_{req['id']}"):
                                try:
                                    supabase.table("xray_requests").update({
                                        "status": "reviewed",
                                        "reviewed_at": datetime.now().isoformat()
                                    }).eq("id", req['id']).execute()
                                    
                                    # Update doctor's total cases
                                    supabase.table("doctors").update({
                                        "total_cases": doctor.get('total_cases', 0) + 1
                                    }).eq("phone", st.session_state.doctor_phone).execute()
                                    
                                    st.success("✅ Marked as reviewed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        with col3:
                            if st.button(f"❌ Cancel", key=f"cancel_{req['id']}"):
                                try:
                                    supabase.table("xray_requests").update({
                                        "status": "cancelled"
                                    }).eq("id", req['id']).execute()
                                    st.warning("Request cancelled")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        st.markdown("---")
                
                # Bulk actions
                st.markdown("### 🔧 Bulk Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Mark All as Reviewed", type="primary"):
                        try:
                            for req in queue_response.data:
                                supabase.table("xray_requests").update({
                                    "status": "reviewed",
                                    "reviewed_at": datetime.now().isoformat()
                                }).eq("id", req['id']).execute()
                            
                            # Update total cases
                            supabase.table("doctors").update({
                                "total_cases": doctor.get('total_cases', 0) + len(queue_response.data)
                            }).eq("phone", st.session_state.doctor_phone).execute()
                            
                            st.success(f"✅ Marked {len(queue_response.data)} requests as reviewed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
            else:
                st.info("✅ No pending X-ray requests in your queue")
                st.balloons()
        
        except Exception as e:
            st.error(f"❌ Error loading queue: {str(e)}")
    
    # ============================================
    # TAB 2: MY REPORTS
    # ============================================
    with tab2:
        st.header("📊 My Generated Reports")
        st.markdown("PDF reports you've generated for patients")
        
        # Search filter
        search = st.text_input("🔍 Search patient name", placeholder="Enter patient name...")
        
        # Date filter
        date_filter = st.selectbox(
            "Date Range",
            ["All Time", "Today", "Last 7 Days", "Last 30 Days"],
            help="Filter by report generation date"
        )
        
        try:
            # Get only reports with PDF (generated reports)
            # Get all requests first, then filter client-side
            all_requests = supabase.table("xray_requests").select("*").eq("doctor_phone", st.session_state.doctor_phone).order("reviewed_at", desc=True).execute()
            
            # Filter for only requests with reports
            reports_data = [r for r in all_requests.data if r.get('report_pdf_url')] if all_requests.data else []
            
            # Apply date filter
            if date_filter == "Today":
                today = datetime.now().date().isoformat()
                reports_data = [r for r in reports_data if r.get('reviewed_at', '').startswith(today)]
            elif date_filter == "Last 7 Days":
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                reports_data = [r for r in reports_data if r.get('reviewed_at', '') >= week_ago]
            elif date_filter == "Last 30 Days":
                month_ago = (datetime.now() - timedelta(days=30)).isoformat()
                reports_data = [r for r in reports_data if r.get('reviewed_at', '') >= month_ago]
            
            if reports_data:
                # Filter by search
                filtered_reports = reports_data
                
                if search:
                    filtered_reports = [r for r in filtered_reports if search.lower() in r['patient_name'].lower()]
                
                if filtered_reports:
                    st.success(f"📊 {len(filtered_reports)} report(s) found")
                    
                    # Display as expandable cards
                    for report in filtered_reports:
                        with st.expander(
                            f"📄 {report['patient_name']} ({report['age']}y) - Generated: {report.get('reviewed_at', 'N/A')[:10]}",
                            expanded=False
                        ):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**👤 Patient:** {report['patient_name']}")
                                st.markdown(f"**🎂 Age:** {report['age']}")
                                st.markdown(f"**📍 Village:** {report.get('village', 'N/A')}")
                                st.markdown(f"**🩺 Symptoms:** {report.get('symptoms', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**📅 Request Created:** {report.get('created_at', 'N/A')[:19]}")
                                st.markdown(f"**✅ Report Generated:** {report.get('reviewed_at', 'N/A')[:19]}")
                                st.markdown(f"**📊 Status:** {report.get('status', 'N/A')}")
                                st.markdown(f"**🆔 Request ID:** {report['id']}")
                                
                                # Calculate turnaround time
                                if report.get('created_at') and report.get('reviewed_at'):
                                    try:
                                        created = datetime.fromisoformat(report['created_at'].replace('Z', '+00:00'))
                                        reviewed = datetime.fromisoformat(report['reviewed_at'].replace('Z', '+00:00'))
                                        turnaround = reviewed - created
                                        hours = int(turnaround.total_seconds() / 3600)
                                        st.info(f"⏱️ Turnaround: {hours} hours")
                                    except:
                                        pass
                            
                            st.markdown("---")
                            
                            if report.get('ai_report'):
                                st.markdown(f"**🤖 AI Analysis:**")
                                st.text_area("", report.get('ai_report', '')[:500] + "..." if len(report.get('ai_report', '')) > 500 else report.get('ai_report', ''), height=100, disabled=True, key=f"ai_{report['id']}")
                            
                            if report.get('doctor_notes'):
                                st.markdown(f"**📝 Your Notes:**")
                                st.text_area("", report.get('doctor_notes', ''), height=100, disabled=True, key=f"notes_{report['id']}")
                            
                            st.markdown("---")
                            
                            # Download PDF button
                            pdf_path = report.get('report_pdf_url')
                            if pdf_path:
                                # Normalize path separators (handle both / and \)
                                pdf_path = pdf_path.replace('\\', os.sep).replace('/', os.sep)
                                
                                # Convert to absolute path from project root
                                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                                absolute_pdf_path = os.path.join(project_root, pdf_path)
                                
                                if os.path.exists(absolute_pdf_path):
                                    with open(absolute_pdf_path, 'rb') as pdf_file:
                                        pdf_data = pdf_file.read()
                                        pdf_filename = os.path.basename(pdf_path)
                                        
                                        col1, col2 = st.columns([3, 1])
                                        
                                        with col1:
                                            st.download_button(
                                                label="📥 Download PDF Report",
                                                data=pdf_data,
                                                file_name=pdf_filename,
                                                mime="application/pdf",
                                                key=f"download_{report['id']}",
                                                use_container_width=True
                                            )
                                        
                                        with col2:
                                            file_size = len(pdf_data) / 1024  # KB
                                            st.info(f"💾 {file_size:.1f} KB")
                                else:
                                    st.warning("⚠️ PDF file not found")
                            
                            if report.get('image_url') and os.path.exists(report.get('image_url')):
                                st.markdown("**📸 X-Ray Image:**")
                                try:
                                    st.image(report['image_url'], width=300, caption=f"X-ray for {report['patient_name']}")
                                except:
                                    st.info("Could not load image")
                else:
                    st.info("No reports match your search criteria")
            else:
                st.info("📭 No reports generated yet. Complete X-ray requests to generate reports.")
        
        except Exception as e:
            st.error(f"❌ Error loading reports: {str(e)}")
    
    # ============================================
    # TAB 3: STATISTICS
    # ============================================
    with tab3:
        st.header("📈 Statistics")
        st.markdown("Your performance metrics")
        
        try:
            # Get all requests
            all_requests = supabase.table("xray_requests").select("*").eq("doctor_phone", st.session_state.doctor_phone).execute()
            
            if all_requests.data:
                total = len(all_requests.data)
                pending = len([r for r in all_requests.data if r.get('status') == 'pending'])
                reviewed = len([r for r in all_requests.data if r.get('status') == 'reviewed'])
                sent = len([r for r in all_requests.data if r.get('status') == 'sent'])
                cancelled = len([r for r in all_requests.data if r.get('status') == 'cancelled'])
                
                # Display metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("📊 Total Cases", total)
                
                with col2:
                    st.metric("⏳ Pending", pending)
                
                with col3:
                    st.metric("🔍 Reviewed", reviewed)
                
                with col4:
                    st.metric("✅ Sent", sent)
                
                with col5:
                    st.metric("❌ Cancelled", cancelled)
                
                st.markdown("---")
                
                # Create DataFrame for chart
                df = pd.DataFrame(all_requests.data)
                
                if not df.empty:
                    st.markdown("### 📊 Status Distribution")
                    status_counts = df['status'].value_counts()
                    st.bar_chart(status_counts)
                    
                    st.markdown("### 📅 Requests Over Time")
                    df['created_at'] = pd.to_datetime(df['created_at'])
                    df['date'] = df['created_at'].dt.date
                    daily_counts = df.groupby('date').size()
                    st.line_chart(daily_counts)
            else:
                st.info("📭 No data available yet")
        
        except Exception as e:
            st.error(f"❌ Error loading statistics: {str(e)}")

st.markdown("---")
st.markdown("💡 **Need help?** Contact admin or check Telegram bot @MediMindDoctorBot")

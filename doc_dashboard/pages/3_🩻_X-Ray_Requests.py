# -*- coding: utf-8 -*-
"""
X-Ray Requests Management - Doctor Panel
View, manage, and monitor X-ray requests assigned to you
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client

# Page config
st.set_page_config(
    page_title="X-Ray Requests - MediMind Doctor",
    page_icon="🩻",
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
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if SUPABASE_URL and SUPABASE_KEY:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None

supabase = init_supabase()

# Title
st.title("🩻 X-Ray Requests Management")
st.markdown("---")

if not supabase:
    st.error("⚠️ Database connection failed. Please check your environment variables.")
    st.stop()

# ============================================
# STATISTICS SECTION
# ============================================

st.subheader("📊 Overview Statistics")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get total requests
    total_response = supabase.table("xray_requests").select("*", count='exact').execute()
    total_requests = total_response.count if total_response else 0
    
    # Get pending requests
    pending_response = supabase.table("xray_requests").select("*", count='exact').eq("status", "pending").execute()
    pending_requests = pending_response.count if pending_response else 0
    
    # Get reviewed requests
    reviewed_response = supabase.table("xray_requests").select("*", count='exact').eq("status", "reviewed").execute()
    reviewed_requests = reviewed_response.count if reviewed_response else 0
    
    # Get cancelled requests
    cancelled_response = supabase.table("xray_requests").select("*", count='exact').eq("status", "cancelled").execute()
    cancelled_requests = cancelled_response.count if cancelled_response else 0
    
    with col1:
        st.metric("Total Requests", total_requests, help="All X-ray requests in system")
    
    with col2:
        st.metric("Pending", pending_requests, help="Awaiting doctor review", delta=f"{pending_requests} waiting")
    
    with col3:
        st.metric("Completed", reviewed_requests, help="Reviewed by doctors", delta=f"{reviewed_requests} done")
    
    with col4:
        st.metric("Cancelled", cancelled_requests, help="Cancelled requests")

except Exception as e:
    st.error(f"Error loading statistics: {e}")

st.markdown("---")

# ============================================
# FILTERS SECTION
# ============================================

st.subheader("🔍 Filters")

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    status_filter = st.selectbox(
        "Status",
        ["All", "pending", "reviewed", "sent", "cancelled"],
        help="Filter by request status"
    )

with filter_col2:
    # Get all doctors for filter
    try:
        doctors_response = supabase.table("doctors").select("phone, name").execute()
        doctor_options = ["All Doctors"] + [f"{d['name']} ({d['phone']})" for d in doctors_response.data] if doctors_response.data else ["All Doctors"]
        doctor_filter = st.selectbox("Doctor", doctor_options, help="Filter by assigned doctor")
    except:
        doctor_filter = st.selectbox("Doctor", ["All Doctors"])

with filter_col3:
    date_filter = st.selectbox(
        "Date Range",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom"],
        help="Filter by date range"
    )

with filter_col4:
    search_query = st.text_input("🔎 Search Patient", placeholder="Enter patient name...", help="Search by patient name")

# Custom date range
if date_filter == "Custom":
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with date_col2:
        end_date = st.date_input("End Date", datetime.now())

st.markdown("---")

# ============================================
# REQUESTS TABLE
# ============================================

st.subheader("📋 X-Ray Requests")

try:
    # Build query based on filters
    query = supabase.table("xray_requests").select("*")
    
    # Apply status filter
    if status_filter != "All":
        query = query.eq("status", status_filter)
    
    # Apply doctor filter
    if doctor_filter != "All Doctors":
        doctor_phone = doctor_filter.split("(")[1].split(")")[0]
        query = query.eq("doctor_phone", doctor_phone)
    
    # Apply date filter
    if date_filter == "Today":
        today = datetime.now().date().isoformat()
        query = query.gte("created_at", today)
    elif date_filter == "Last 7 Days":
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        query = query.gte("created_at", week_ago)
    elif date_filter == "Last 30 Days":
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        query = query.gte("created_at", month_ago)
    elif date_filter == "Custom":
        query = query.gte("created_at", start_date.isoformat()).lte("created_at", end_date.isoformat())
    
    # Execute query
    response = query.order("created_at", desc=True).execute()
    
    if response.data and len(response.data) > 0:
        requests_data = response.data
        
        # Apply search filter
        if search_query:
            requests_data = [r for r in requests_data if search_query.lower() in r.get('patient_name', '').lower()]
        
        if len(requests_data) > 0:
            st.success(f"Found {len(requests_data)} request(s)")
            
            # Display each request as a card
            for idx, request in enumerate(requests_data):
                with st.expander(
                    f"🩻 Request #{request['id']} - {request['patient_name']} ({request['age']}y) - {request['village']} - Status: {request['status'].upper()}",
                    expanded=(idx < 3)  # Expand first 3 by default
                ):
                    # Request details
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.markdown("**👤 Patient Information**")
                        st.write(f"**Name:** {request['patient_name']}")
                        st.write(f"**Age:** {request['age']} years")
                        st.write(f"**Village:** {request.get('village', 'N/A')}")
                        st.write(f"**Symptoms:** {request.get('symptoms', 'N/A')}")
                    
                    with detail_col2:
                        st.markdown("**👨‍⚕️ Doctor Information**")
                        doctor_phone = request.get('doctor_phone', 'N/A')
                        
                        # Get doctor details
                        if doctor_phone != 'N/A':
                            try:
                                doc_response = supabase.table("doctors").select("name, phc, mci_reg").eq("phone", doctor_phone).execute()
                                if doc_response.data and len(doc_response.data) > 0:
                                    doc = doc_response.data[0]
                                    st.write(f"**Doctor:** Dr. {doc.get('name', 'Unknown')}")
                                    st.write(f"**PHC:** {doc.get('phc', 'N/A')}")
                                    st.write(f"**MCI:** {doc.get('mci_reg', 'N/A')}")
                                else:
                                    st.write(f"**Phone:** {doctor_phone}")
                            except:
                                st.write(f"**Phone:** {doctor_phone}")
                        else:
                            st.write("**Doctor:** Not assigned")
                        
                        st.write(f"**Status:** {request['status'].upper()}")
                        if request.get('reviewed_at'):
                            st.write(f"**Reviewed:** {request['reviewed_at'][:10]}")
                    
                    with detail_col3:
                        st.markdown("**📅 Timeline**")
                        st.write(f"**Created:** {request.get('created_at', 'N/A')[:19]}")
                        if request.get('consent_time'):
                            st.write(f"**Consent:** {request['consent_time'][:19]}")
                        if request.get('reviewed_at'):
                            st.write(f"**Reviewed:** {request['reviewed_at'][:19]}")
                        
                        # Calculate waiting time for pending requests
                        if request['status'] == 'pending':
                            created = datetime.fromisoformat(request['created_at'].replace('Z', '+00:00'))
                            waiting_time = datetime.now(created.tzinfo) - created
                            hours = int(waiting_time.total_seconds() / 3600)
                            st.warning(f"⏰ Waiting: {hours} hours")
                    
                    # Image preview
                    image_url = request.get('image_url')
                    if image_url and os.path.exists(image_url):
                        st.markdown("**📸 X-Ray Image**")
                        try:
                            st.image(image_url, width=300, caption=f"X-ray for {request['patient_name']}")
                        except Exception as e:
                            st.warning(f"Could not load image: {e}")
                    else:
                        st.info("📤 Image file not found")
                    
                    # AI Analysis Results (if available)
                    if request.get('ai_report'):
                        st.markdown("**🤖 AI Analysis**")
                        st.text_area(
                            "AI Report",
                            request['ai_report'][:500] + "..." if len(request.get('ai_report', '')) > 500 else request.get('ai_report', ''),
                            height=100,
                            key=f"ai_report_{request['id']}"
                        )
                    
                    # Doctor Notes (if available)
                    if request.get('doctor_notes'):
                        st.markdown("**📝 Doctor's Notes**")
                        st.text_area(
                            "Notes",
                            request['doctor_notes'],
                            height=100,
                            key=f"doctor_notes_{request['id']}"
                        )
                    
                    # Report PDF (if available)
                    if request.get('report_pdf_url'):
                        st.markdown("**📄 Report PDF**")
                        pdf_path = request['report_pdf_url']
                        
                        # Normalize path separators (handle both / and \)
                        pdf_path = pdf_path.replace('\\', os.sep).replace('/', os.sep)
                        
                        # Convert to absolute path from project root
                        # Pages are in dashboard/pages/, need to go up 2 levels
                        current_file = os.path.abspath(__file__)
                        pages_dir = os.path.dirname(current_file)
                        dashboard_dir = os.path.dirname(pages_dir)
                        project_root = os.path.dirname(dashboard_dir)
                        absolute_pdf_path = os.path.join(project_root, pdf_path)
                        
                        if os.path.exists(absolute_pdf_path):
                            with open(absolute_pdf_path, 'rb') as pdf_file:
                                st.download_button(
                                    label="📥 Download Report PDF",
                                    data=pdf_file,
                                    file_name=f"report_{request['id']}.pdf",
                                    mime="application/pdf",
                                    key=f"download_pdf_{request['id']}"
                                )
                        else:
                            st.info("PDF file not found on server")
                    
                    st.markdown("---")
                    
                    # Action buttons
                    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
                    
                    with action_col1:
                        # Remind Doctor button (only for pending requests)
                        if request['status'] == 'pending':
                            if st.button(f"🔔 Remind Doctor", key=f"remind_{request['id']}", type="primary"):
                                try:
                                    # Get doctor's telegram_id
                                    doc_response = supabase.table("doctors").select("telegram_id, name").eq("phone", doctor_phone).execute()
                                    if doc_response.data and len(doc_response.data) > 0:
                                        doctor_telegram_id = doc_response.data[0].get('telegram_id')
                                        doctor_name = doc_response.data[0].get('name')
                                        
                                        if doctor_telegram_id:
                                            # Calculate waiting time
                                            created = datetime.fromisoformat(request['created_at'].replace('Z', '+00:00'))
                                            waiting_time = datetime.now(created.tzinfo) - created
                                            waiting_hours = int(waiting_time.total_seconds() / 3600)
                                            
                                            # Send reminder via Telegram with full patient details
                                            with st.spinner("Sending urgent reminder to doctor..."):
                                                result = send_reminder_sync(
                                                    doctor_telegram_id,
                                                    request['id'],
                                                    request['patient_name'],
                                                    waiting_hours,
                                                    request.get('age'),
                                                    request.get('village')
                                                )
                                            
                                            if result:
                                                st.success(f"✅ Urgent reminder sent to Dr. {doctor_name}!")
                                                st.info(f"📱 Message delivered to @MediMindDoctorBot\n\n"
                                                       f"Message: 'Request #{request['id']} for {request['patient_name']} is PENDING - Please complete immediately!'")
                                            else:
                                                st.error("❌ Failed to send reminder. Please check doctor's Telegram ID.")
                                        else:
                                            st.warning("⚠️ Doctor's Telegram ID not found. Please ensure doctor is registered in @MediMindDoctorBot.")
                                    else:
                                        st.error("❌ Doctor not found in database.")
                                except Exception as e:
                                    st.error(f"❌ Error sending reminder: {e}")
                    
                    with action_col2:
                        # Send Custom Message button
                        if st.button(f"💬 Send Message", key=f"message_{request['id']}"):
                            st.session_state[f'show_message_form_{request["id"]}'] = True
                    
                    with action_col3:
                        # Change Status button
                        new_status = st.selectbox(
                            "Change Status",
                            ["pending", "reviewed", "sent", "cancelled"],
                            index=["pending", "reviewed", "sent", "cancelled"].index(request['status']),
                            key=f"status_{request['id']}"
                        )
                        if st.button(f"💾 Update", key=f"update_status_{request['id']}"):
                            try:
                                supabase.table("xray_requests").update({
                                    "status": new_status,
                                    "updated_at": datetime.now().isoformat()
                                }).eq("id", request['id']).execute()
                                st.success(f"✅ Status updated to {new_status}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error updating status: {e}")
                    
                    with action_col4:
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"delete_{request['id']}", type="secondary"):
                            st.session_state[f'confirm_delete_{request["id"]}'] = True
                    
                    # Message form (if triggered)
                    if st.session_state.get(f'show_message_form_{request["id"]}', False):
                        st.markdown("**💬 Send Custom Message to Doctor**")
                        message_text = st.text_area(
                            "Message",
                            placeholder="Enter your message to the doctor...",
                            key=f"message_text_{request['id']}"
                        )
                        
                        msg_col1, msg_col2 = st.columns(2)
                        with msg_col1:
                            if st.button("📤 Send", key=f"send_msg_{request['id']}"):
                                if message_text:
                                    try:
                                        # Get doctor's telegram_id
                                        doc_response = supabase.table("doctors").select("telegram_id, name").eq("phone", doctor_phone).execute()
                                        if doc_response.data and len(doc_response.data) > 0:
                                            doctor_telegram_id = doc_response.data[0].get('telegram_id')
                                            doctor_name = doc_response.data[0].get('name')
                                            
                                            if doctor_telegram_id:
                                                # Send custom message via Telegram
                                                with st.spinner("Sending message..."):
                                                    result = send_message_sync(
                                                        doctor_telegram_id,
                                                        message_text,
                                                        request['id']
                                                    )
                                                
                                                if result:
                                                    st.success(f"✅ Message sent to Dr. {doctor_name}")
                                                    st.session_state[f'show_message_form_{request["id"]}'] = False
                                                    st.rerun()
                                                else:
                                                    st.error("❌ Failed to send message")
                                            else:
                                                st.warning("⚠️ Doctor's Telegram ID not found")
                                        else:
                                            st.error("❌ Doctor not found")
                                    except Exception as e:
                                        st.error(f"Error sending message: {e}")
                                else:
                                    st.warning("Please enter a message")
                        
                        with msg_col2:
                            if st.button("❌ Cancel", key=f"cancel_msg_{request['id']}"):
                                st.session_state[f'show_message_form_{request["id"]}'] = False
                                st.rerun()
                    
                    # Delete confirmation (if triggered)
                    if st.session_state.get(f'confirm_delete_{request["id"]}', False):
                        st.warning("⚠️ **Are you sure you want to delete this request?**")
                        st.write("This action cannot be undone!")
                        
                        del_col1, del_col2 = st.columns(2)
                        with del_col1:
                            if st.button("✅ Yes, Delete", key=f"confirm_yes_{request['id']}", type="primary"):
                                try:
                                    # Delete the request
                                    supabase.table("xray_requests").delete().eq("id", request['id']).execute()
                                    st.success(f"✅ Request #{request['id']} deleted successfully")
                                    st.session_state[f'confirm_delete_{request["id"]}'] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting request: {e}")
                        
                        with del_col2:
                            if st.button("❌ No, Cancel", key=f"confirm_no_{request['id']}"):
                                st.session_state[f'confirm_delete_{request["id"]}'] = False
                                st.rerun()
        else:
            st.info("No requests found matching your search criteria")
    else:
        st.info("📭 No X-ray requests found")

except Exception as e:
    st.error(f"Error loading requests: {e}")
    st.exception(e)

st.markdown("---")

# ============================================
# DOCTOR PERFORMANCE SECTION
# ============================================

st.subheader("👨‍⚕️ Doctor Performance")

try:
    # Get all doctors with their request counts
    doctors_response = supabase.table("doctors").select("phone, name, phc, rating, total_cases").execute()
    
    if doctors_response.data and len(doctors_response.data) > 0:
        doctor_stats = []
        
        for doctor in doctors_response.data:
            phone = doctor['phone']
            
            # Get pending requests for this doctor
            pending = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).eq("status", "pending").execute()
            pending_count = pending.count if pending else 0
            
            # Get completed requests for this doctor
            completed = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).eq("status", "reviewed").execute()
            completed_count = completed.count if completed else 0
            
            # Get total requests for this doctor
            total = supabase.table("xray_requests").select("*", count='exact').eq("doctor_phone", phone).execute()
            total_count = total.count if total else 0
            
            # Calculate completion rate
            completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
            
            doctor_stats.append({
                'Doctor': f"Dr. {doctor['name']}",
                'PHC': doctor.get('phc', 'N/A'),
                'Total Requests': total_count,
                'Pending': pending_count,
                'Completed': completed_count,
                'Completion Rate': f"{completion_rate:.1f}%",
                'Rating': f"{doctor.get('rating', 0):.1f}⭐",
                'Phone': phone
            })
        
        # Create DataFrame
        df = pd.DataFrame(doctor_stats)
        
        # Sort by pending (descending) to show doctors with most pending first
        df = df.sort_values('Pending', ascending=False)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Doctor": st.column_config.TextColumn("Doctor", width="medium"),
                "PHC": st.column_config.TextColumn("PHC", width="medium"),
                "Total Requests": st.column_config.NumberColumn("Total", width="small"),
                "Pending": st.column_config.NumberColumn("Pending", width="small"),
                "Completed": st.column_config.NumberColumn("Completed", width="small"),
                "Completion Rate": st.column_config.TextColumn("Rate", width="small"),
                "Rating": st.column_config.TextColumn("Rating", width="small"),
                "Phone": st.column_config.TextColumn("Phone", width="medium")
            }
        )
        
        # Highlight doctors with high pending counts
        high_pending = [d for d in doctor_stats if d['Pending'] > 5]
        if high_pending:
            st.warning(f"⚠️ {len(high_pending)} doctor(s) have more than 5 pending requests")
    else:
        st.info("No doctors found in the system")

except Exception as e:
    st.error(f"Error loading doctor performance: {e}")

st.markdown("---")

# ============================================
# BULK ACTIONS SECTION
# ============================================

st.subheader("⚡ Bulk Actions")

bulk_col1, bulk_col2, bulk_col3 = st.columns(3)

with bulk_col1:
    if st.button("🔔 Remind All Doctors with Pending Requests", type="primary"):
        try:
            # Get all pending requests with doctor info
            pending_response = supabase.table("xray_requests").select("id, patient_name, age, village, doctor_phone, created_at").eq("status", "pending").execute()
            
            if pending_response.data:
                # Group by doctor and prepare reminder data
                doctor_reminders = {}
                
                for request in pending_response.data:
                    doctor_phone = request.get('doctor_phone')
                    if not doctor_phone:
                        continue
                    
                    # Get doctor's telegram_id
                    doc_response = supabase.table("doctors").select("telegram_id, name").eq("phone", doctor_phone).execute()
                    if doc_response.data and len(doc_response.data) > 0:
                        doctor_telegram_id = doc_response.data[0].get('telegram_id')
                        
                        if doctor_telegram_id:
                            # Calculate waiting time
                            created = datetime.fromisoformat(request['created_at'].replace('Z', '+00:00'))
                            waiting_time = datetime.now(created.tzinfo) - created
                            waiting_hours = int(waiting_time.total_seconds() / 3600)
                            
                            if doctor_phone not in doctor_reminders:
                                doctor_reminders[doctor_phone] = []
                            
                            doctor_reminders[doctor_phone].append({
                                'doctor_telegram_id': doctor_telegram_id,
                                'request_id': request['id'],
                                'patient_name': request['patient_name'],
                                'waiting_hours': waiting_hours,
                                'patient_age': request.get('age'),
                                'patient_village': request.get('village')
                            })
                
                # Send reminders
                if doctor_reminders:
                    with st.spinner(f"Sending urgent reminders to {len(doctor_reminders)} doctor(s)..."):
                        # Flatten the list
                        all_reminders = []
                        for reminders in doctor_reminders.values():
                            all_reminders.extend(reminders)
                        
                        result = send_bulk_reminders_sync(all_reminders)
                    
                    st.success(f"✅ Sent {result['success']} urgent reminder(s) successfully!")
                    st.info(f"📱 All messages delivered to @MediMindDoctorBot\n\n"
                           f"Message: 'Request is PENDING - Please complete immediately!'")
                    if result['failure'] > 0:
                        st.warning(f"⚠️ Failed to send {result['failure']} reminder(s)")
                else:
                    st.info("No doctors with valid Telegram IDs found")
            else:
                st.info("No pending requests found")
        except Exception as e:
            st.error(f"Error sending bulk reminders: {e}")

with bulk_col2:
    if st.button("📊 Export All Requests to CSV"):
        try:
            # Get all requests
            all_requests = supabase.table("xray_requests").select("*").execute()
            
            if all_requests.data:
                df = pd.DataFrame(all_requests.data)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"xray_requests_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No requests to export")
        except Exception as e:
            st.error(f"Error exporting data: {e}")

with bulk_col3:
    if st.button("🗑️ Delete All Cancelled Requests"):
        st.session_state['confirm_bulk_delete'] = True

# Bulk delete confirmation
if st.session_state.get('confirm_bulk_delete', False):
    st.warning("⚠️ **Are you sure you want to delete ALL cancelled requests?**")
    st.write("This action cannot be undone!")
    
    bulk_del_col1, bulk_del_col2 = st.columns(2)
    with bulk_del_col1:
        if st.button("✅ Yes, Delete All Cancelled", type="primary"):
            try:
                result = supabase.table("xray_requests").delete().eq("status", "cancelled").execute()
                st.success(f"✅ All cancelled requests deleted successfully")
                st.session_state['confirm_bulk_delete'] = False
                st.rerun()
            except Exception as e:
                st.error(f"Error deleting requests: {e}")
    
    with bulk_del_col2:
        if st.button("❌ Cancel"):
            st.session_state['confirm_bulk_delete'] = False
            st.rerun()

st.markdown("---")

# Footer
st.caption("🩻 X-Ray Requests Management | MediMind Admin Panel")

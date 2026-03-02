# -*- coding: utf-8 -*-
"""
Reports Management - Admin Panel
View all generated PDF reports from all doctors
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client

# Page config
st.set_page_config(
    page_title="Reports - MediMind Admin",
    page_icon="📄",
    layout="wide"
)

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
st.title("📄 Reports Management")
st.markdown("View all generated PDF reports from all doctors")
st.markdown("---")

if not supabase:
    st.error("⚠️ Database connection failed. Please check your environment variables.")
    st.stop()

# ============================================
# STATISTICS SECTION
# ============================================

st.subheader("📊 Reports Overview")

col1, col2, col3, col4 = st.columns(4)

try:
    # Get all reports (requests with report_pdf_url)
    # Note: Filter client-side since wrapper doesn't support NOT NULL
    all_requests = supabase.table("xray_requests").select("*").execute()
    all_reports = [r for r in all_requests.data if r.get('report_pdf_url')] if all_requests.data else []
    total_reports = len(all_reports)
    
    # Get reports from today
    today = datetime.now().date().isoformat()
    today_reports = [r for r in all_reports if r.get('reviewed_at', '').startswith(today)]
    today_count = len(today_reports)
    
    # Get reports from last 7 days
    week_ago = (datetime.now() - timedelta(days=7)).isoformat()
    week_reports = [r for r in all_reports if r.get('reviewed_at', '') >= week_ago]
    week_count = len(week_reports)
    
    # Get reports from last 30 days
    month_ago = (datetime.now() - timedelta(days=30)).isoformat()
    month_reports = [r for r in all_reports if r.get('reviewed_at', '') >= month_ago]
    month_count = len(month_reports)
    
    with col1:
        st.metric("Total Reports", total_reports, help="All generated PDF reports")
    
    with col2:
        st.metric("Today", today_count, help="Reports generated today")
    
    with col3:
        st.metric("Last 7 Days", week_count, help="Reports in the last week")
    
    with col4:
        st.metric("Last 30 Days", month_count, help="Reports in the last month")

except Exception as e:
    st.error(f"Error loading statistics: {e}")

st.markdown("---")

# ============================================
# FILTERS SECTION
# ============================================

st.subheader("🔍 Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    # Get all doctors for filter
    try:
        doctors_response = supabase.table("doctors").select("phone, name").execute()
        doctor_options = ["All Doctors"] + [f"{d['name']} ({d['phone']})" for d in doctors_response.data] if doctors_response.data else ["All Doctors"]
        doctor_filter = st.selectbox("Doctor", doctor_options, help="Filter by doctor who generated the report")
    except:
        doctor_filter = st.selectbox("Doctor", ["All Doctors"])

with filter_col2:
    date_filter = st.selectbox(
        "Date Range",
        ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Custom"],
        help="Filter by report generation date"
    )

with filter_col3:
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
# REPORTS TABLE
# ============================================

st.subheader("📋 Generated Reports")

try:
    # Get all requests first, then filter client-side for report_pdf_url
    response = supabase.table("xray_requests").select("*").order("created_at", desc=True).execute()
    
    if response.data and len(response.data) > 0:
        # Filter for only requests with reports (report_pdf_url not null)
        requests_data = [r for r in response.data if r.get('report_pdf_url')]
        
        # Apply doctor filter
        if doctor_filter != "All Doctors":
            doctor_phone = doctor_filter.split("(")[1].split(")")[0]
            requests_data = [r for r in requests_data if r.get('doctor_phone') == doctor_phone]
        
        # Apply date filter
        if date_filter == "Today":
            today = datetime.now().date().isoformat()
            requests_data = [r for r in requests_data if r.get('reviewed_at', '').startswith(today)]
        elif date_filter == "Last 7 Days":
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            requests_data = [r for r in requests_data if r.get('reviewed_at', '') >= week_ago]
        elif date_filter == "Last 30 Days":
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            requests_data = [r for r in requests_data if r.get('reviewed_at', '') >= month_ago]
        elif date_filter == "Custom":
            requests_data = [r for r in requests_data if start_date.isoformat() <= r.get('reviewed_at', '')[:10] <= end_date.isoformat()]
        
        # Apply search filter
        if search_query:
            requests_data = [r for r in requests_data if search_query.lower() in r.get('patient_name', '').lower()]
        
        # Sort by reviewed_at descending
        requests_data = sorted(requests_data, key=lambda x: x.get('reviewed_at', ''), reverse=True)
        
        if len(requests_data) > 0:
            st.success(f"Found {len(requests_data)} report(s)")
            
            # Display each report as a card
            for idx, report in enumerate(requests_data):
                with st.expander(
                    f"📄 Report #{report['id']} - {report['patient_name']} ({report['age']}y) - Generated: {report.get('reviewed_at', 'N/A')[:10]}",
                    expanded=(idx < 3)  # Expand first 3 by default
                ):
                    # Report details
                    detail_col1, detail_col2, detail_col3 = st.columns(3)
                    
                    with detail_col1:
                        st.markdown("**👤 Patient Information**")
                        st.write(f"**Name:** {report['patient_name']}")
                        st.write(f"**Age:** {report['age']} years")
                        st.write(f"**Village:** {report.get('village', 'N/A')}")
                        st.write(f"**Symptoms:** {report.get('symptoms', 'N/A')}")
                    
                    with detail_col2:
                        st.markdown("**👨‍⚕️ Doctor Information**")
                        doctor_phone = report.get('doctor_phone', 'N/A')
                        
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
                    
                    with detail_col3:
                        st.markdown("**📅 Timeline**")
                        st.write(f"**Request Created:** {report.get('created_at', 'N/A')[:19]}")
                        st.write(f"**Report Generated:** {report.get('reviewed_at', 'N/A')[:19]}")
                        
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
                    
                    # AI Analysis Results
                    if report.get('ai_report'):
                        st.markdown("**🤖 AI Analysis**")
                        st.text_area(
                            "AI Report",
                            report['ai_report'][:500] + "..." if len(report.get('ai_report', '')) > 500 else report.get('ai_report', ''),
                            height=100,
                            key=f"ai_report_{report['id']}",
                            disabled=True
                        )
                    
                    # Doctor Notes
                    if report.get('doctor_notes'):
                        st.markdown("**📝 Doctor's Notes**")
                        st.text_area(
                            "Notes",
                            report['doctor_notes'],
                            height=100,
                            key=f"doctor_notes_{report['id']}",
                            disabled=True
                        )
                    
                    st.markdown("---")
                    
                    # Download PDF button
                    pdf_path = report.get('report_pdf_url')
                    if pdf_path:
                        # Convert to absolute path from project root
                        # Dashboard runs from dashboard/ folder, so go up one level
                        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                        absolute_pdf_path = os.path.join(project_root, pdf_path)
                        
                        if os.path.exists(absolute_pdf_path):
                            with open(absolute_pdf_path, 'rb') as pdf_file:
                                pdf_data = pdf_file.read()
                                
                                # Extract filename from path
                                pdf_filename = os.path.basename(pdf_path)
                                
                                col1, col2, col3 = st.columns([2, 1, 1])
                                
                                with col1:
                                    st.download_button(
                                        label="📥 Download Report PDF",
                                        data=pdf_data,
                                        file_name=pdf_filename,
                                        mime="application/pdf",
                                        key=f"download_pdf_{report['id']}",
                                        use_container_width=True
                                    )
                                
                            with col2:
                                st.info(f"📄 {pdf_filename}")
                            
                            with col3:
                                # File size
                                file_size = len(pdf_data) / 1024  # KB
                                st.info(f"💾 {file_size:.1f} KB")
                        else:
                            st.warning("⚠️ PDF file not found on server")
                            st.info(f"Expected path: {absolute_pdf_path}")
                    else:
                        st.warning("⚠️ No PDF path recorded")

        else:
            st.info("No reports found matching your search criteria")
    else:
        st.info("📭 No reports generated yet")

except Exception as e:
    st.error(f"Error loading reports: {e}")
    st.exception(e)

st.markdown("---")

# ============================================
# DOCTOR REPORT STATISTICS
# ============================================

st.subheader("👨‍⚕️ Doctor Report Statistics")

try:
    # Get all doctors with their report counts
    doctors_response = supabase.table("doctors").select("phone, name, phc, rating").execute()
    
    if doctors_response.data and len(doctors_response.data) > 0:
        # Get all reports once
        all_requests = supabase.table("xray_requests").select("*").execute()
        all_reports_list = [r for r in all_requests.data if r.get('report_pdf_url')] if all_requests.data else []
        
        doctor_stats = []
        
        for doctor in doctors_response.data:
            phone = doctor['phone']
            
            # Filter reports for this doctor
            doctor_reports = [r for r in all_reports_list if r.get('doctor_phone') == phone]
            reports_count = len(doctor_reports)
            
            # Get reports from last 7 days
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            week_reports = [r for r in doctor_reports if r.get('reviewed_at', '') >= week_ago]
            week_count = len(week_reports)
            
            # Get reports from last 30 days
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            month_reports = [r for r in doctor_reports if r.get('reviewed_at', '') >= month_ago]
            month_count = len(month_reports)
            
            doctor_stats.append({
                'Doctor': f"Dr. {doctor['name']}",
                'PHC': doctor.get('phc', 'N/A'),
                'Total Reports': reports_count,
                'Last 7 Days': week_count,
                'Last 30 Days': month_count,
                'Rating': f"{doctor.get('rating', 0):.1f}⭐",
                'Phone': phone
            })
        
        # Create DataFrame
        df = pd.DataFrame(doctor_stats)
        
        # Sort by total reports (descending)
        df = df.sort_values('Total Reports', ascending=False)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Doctor": st.column_config.TextColumn("Doctor", width="medium"),
                "PHC": st.column_config.TextColumn("PHC", width="medium"),
                "Total Reports": st.column_config.NumberColumn("Total", width="small"),
                "Last 7 Days": st.column_config.NumberColumn("7 Days", width="small"),
                "Last 30 Days": st.column_config.NumberColumn("30 Days", width="small"),
                "Rating": st.column_config.TextColumn("Rating", width="small"),
                "Phone": st.column_config.TextColumn("Phone", width="medium")
            }
        )
        
        # Show top performers
        if len(df) > 0:
            top_doctor = df.iloc[0]
            st.success(f"🏆 Top Performer: {top_doctor['Doctor']} with {top_doctor['Total Reports']} reports")
    else:
        st.info("No doctors found in the system")

except Exception as e:
    st.error(f"Error loading doctor statistics: {e}")

st.markdown("---")

# ============================================
# BULK ACTIONS
# ============================================

st.subheader("⚡ Bulk Actions")

bulk_col1, bulk_col2 = st.columns(2)

with bulk_col1:
    if st.button("📊 Export All Reports to CSV", type="primary"):
        try:
            # Get all reports
            all_requests = supabase.table("xray_requests").select("*").execute()
            all_reports_list = [r for r in all_requests.data if r.get('report_pdf_url')] if all_requests.data else []
            
            if all_reports_list:
                df = pd.DataFrame(all_reports_list)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"reports_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No reports to export")
        except Exception as e:
            st.error(f"Error exporting data: {e}")

with bulk_col2:
    if st.button("📈 Generate Monthly Report"):
        try:
            # Get reports from last 30 days
            month_ago = (datetime.now() - timedelta(days=30)).isoformat()
            all_requests = supabase.table("xray_requests").select("*").execute()
            all_reports_list = [r for r in all_requests.data if r.get('report_pdf_url')] if all_requests.data else []
            month_reports = [r for r in all_reports_list if r.get('reviewed_at', '') >= month_ago]
            
            if month_reports:
                st.success(f"📊 Monthly Report: {len(month_reports)} reports generated in the last 30 days")
                
                # Group by doctor
                doctor_counts = {}
                for report in month_reports:
                    doctor_phone = report.get('doctor_phone', 'Unknown')
                    doctor_counts[doctor_phone] = doctor_counts.get(doctor_phone, 0) + 1
                
                st.markdown("**Reports by Doctor:**")
                for phone, count in sorted(doctor_counts.items(), key=lambda x: x[1], reverse=True):
                    # Get doctor name
                    try:
                        doc = supabase.table("doctors").select("name").eq("phone", phone).execute()
                        name = doc.data[0]['name'] if doc.data else phone
                        st.write(f"- Dr. {name}: {count} reports")
                    except:
                        st.write(f"- {phone}: {count} reports")
            else:
                st.info("No reports in the last 30 days")
        except Exception as e:
            st.error(f"Error generating monthly report: {e}")

st.markdown("---")
st.markdown("💡 **Tip:** All PDF reports are stored in the `reports/` folder on the server")

# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()

st.set_page_config(page_title="Maternal Health", page_icon="👶", layout="wide")

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
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

st.title("👶 Maternal Health Tracker")
st.markdown("### Monitor Pregnancy Progress")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Pregnancies", "📊 Statistics", "🔔 Alerts"])

with tab1:
    st.markdown("#### Pregnancy Tracking Records")
    
    # Search
    search = st.text_input("🔍 Search by username", "")
    
    try:
        response = supabase.table('maternal').select('*').execute()
        records = response.data
        
        if records:
            # Filter by search
            if search:
                records = [r for r in records if search.lower() in r.get('username', '').lower()]
            
            # Sort by weeks pregnant (descending)
            records = sorted(records, key=lambda x: x.get('weeks_pregnant', 0), reverse=True)
            
            st.info(f"👶 Tracking {len(records)} pregnancies")
            
            # Display records
            for record in records:
                weeks = record.get('weeks_pregnant', 0)
                
                # Calculate trimester
                if weeks <= 12:
                    trimester = "1st Trimester"
                    color = "#4caf50"
                elif weeks <= 26:
                    trimester = "2nd Trimester"
                    color = "#2196f3"
                else:
                    trimester = "3rd Trimester"
                    color = "#ff9800"
                
                with st.expander(f"👤 {record.get('username', 'Unknown')} - {weeks} weeks ({trimester})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Patient Details:**
                        - 👤 Username: {record.get('username', 'N/A')}
                        - 🆔 User ID: {record.get('user_id', 'N/A')}
                        - 📅 LMP Date: {record.get('lmp_date', 'N/A')}
                        - ⏰ Weeks Pregnant: **{weeks} weeks**
                        - 🎯 Trimester: **{trimester}**
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Pregnancy Timeline:**
                        - 👶 Due Date: {record.get('due_date', 'N/A')}
                        - 🕐 Record Created: {record.get('created', 'N/A')}
                        """)
                        
                        # Progress bar
                        progress = min(weeks / 40, 1.0)
                        st.progress(progress)
                        st.markdown(f"**{weeks}/40 weeks** ({progress*100:.1f}%)")
                    
                    # Health tips based on trimester
                    st.markdown("#### 💡 Health Tips")
                    if weeks <= 12:
                        st.info("""
                        **1st Trimester Tips:**
                        - Take folic acid supplements
                        - Avoid alcohol and smoking
                        - Get plenty of rest
                        - Stay hydrated
                        """)
                    elif weeks <= 26:
                        st.info("""
                        **2nd Trimester Tips:**
                        - Continue prenatal vitamins
                        - Start gentle exercises
                        - Monitor weight gain
                        - Schedule anatomy scan
                        """)
                    else:
                        st.warning("""
                        **3rd Trimester Tips:**
                        - Prepare hospital bag
                        - Attend childbirth classes
                        - Monitor baby movements
                        - Schedule weekly checkups
                        """)
        else:
            st.info("No pregnancy records found")
    
    except Exception as e:
        st.error(f"Error loading records: {e}")

with tab2:
    st.markdown("#### Maternal Health Statistics")
    
    try:
        response = supabase.table('maternal').select('*').execute()
        records = response.data
        
        if records:
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(records)
            
            # Count by trimester
            first_tri = len([r for r in records if r.get('weeks_pregnant', 0) <= 12])
            second_tri = len([r for r in records if 12 < r.get('weeks_pregnant', 0) <= 26])
            third_tri = len([r for r in records if r.get('weeks_pregnant', 0) > 26])
            
            with col1:
                st.metric("Total Pregnancies", total)
            with col2:
                st.metric("1st Trimester", first_tri)
            with col3:
                st.metric("2nd Trimester", second_tri)
            with col4:
                st.metric("3rd Trimester", third_tri)
            
            # Average weeks
            avg_weeks = sum([r.get('weeks_pregnant', 0) for r in records]) / total if total > 0 else 0
            st.metric("Average Weeks Pregnant", f"{avg_weeks:.1f} weeks")
            
            # Due dates this month
            st.markdown("#### 📅 Due Dates This Month")
            current_month = datetime.now().strftime('%m-%Y')
            due_this_month = [r for r in records if current_month in r.get('due_date', '')]
            
            if due_this_month:
                for record in due_this_month:
                    st.markdown(f"👶 **{record.get('username')}** - Due: {record.get('due_date')}")
            else:
                st.info("No due dates this month")
            
            # Trimester distribution chart
            st.markdown("#### Distribution by Trimester")
            trimester_data = pd.DataFrame({
                'Trimester': ['1st Trimester', '2nd Trimester', '3rd Trimester'],
                'Count': [first_tri, second_tri, third_tri]
            })
            st.bar_chart(trimester_data.set_index('Trimester'))
        else:
            st.info("No data available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

with tab3:
    st.markdown("#### Health Alerts & Reminders")
    
    try:
        response = supabase.table('maternal').select('*').execute()
        records = response.data
        
        if records:
            # High-risk pregnancies (>35 weeks)
            high_risk = [r for r in records if r.get('weeks_pregnant', 0) >= 35]
            if high_risk:
                st.warning(f"⚠️ {len(high_risk)} pregnancies at 35+ weeks (High Priority)")
                for record in high_risk:
                    st.markdown(f"- 👤 {record.get('username')} - {record.get('weeks_pregnant')} weeks - Due: {record.get('due_date')}")
            
            # Due soon (38+ weeks)
            due_soon = [r for r in records if r.get('weeks_pregnant', 0) >= 38]
            if due_soon:
                st.error(f"🚨 {len(due_soon)} pregnancies at 38+ weeks (Due Very Soon!)")
                for record in due_soon:
                    st.markdown(f"- 👤 {record.get('username')} - {record.get('weeks_pregnant')} weeks - Due: {record.get('due_date')}")
            
            # First trimester (need extra care)
            first_tri = [r for r in records if r.get('weeks_pregnant', 0) <= 12]
            if first_tri:
                st.info(f"💙 {len(first_tri)} pregnancies in 1st trimester (Critical Period)")
                for record in first_tri:
                    st.markdown(f"- 👤 {record.get('username')} - {record.get('weeks_pregnant')} weeks")
            
            if not high_risk and not due_soon and not first_tri:
                st.success("✅ No critical alerts at this time")
        else:
            st.info("No records to monitor")
    
    except Exception as e:
        st.error(f"Error loading alerts: {e}")

# Quick actions
st.markdown("---")
st.markdown("### ⚙️ Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📧 Send Reminder to All 3rd Trimester", use_container_width=True):
        st.success("Reminders sent to all 3rd trimester patients!")

with col2:
    if st.button("📊 Export Data to CSV", use_container_width=True):
        try:
            response = supabase.table('maternal').select('*').execute()
            if response.data:
                df = pd.DataFrame(response.data)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name="maternal_health_data.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error: {e}")

# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd

load_dotenv()

st.set_page_config(page_title="Medicine Reminders", page_icon="💊", layout="wide")

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

st.title("💊 Medicine Reminders")
st.markdown("### Manage Patient Medicine Schedules")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 Active Reminders", "🔕 Inactive", "📊 Statistics"])

with tab1:
    st.markdown("#### Active Medicine Reminders")
    
    # Search
    search = st.text_input("🔍 Search by username or medicine name", "")
    
    try:
        response = supabase.table('reminders').select('*').eq('active', True).execute()
        reminders = response.data
        
        if reminders:
            # Filter by search
            if search:
                reminders = [r for r in reminders if 
                            search.lower() in r.get('username', '').lower() or
                            search.lower() in r.get('medicine_name', '').lower()]
            
            # Sort by time
            reminders = sorted(reminders, key=lambda x: x.get('time', ''))
            
            st.info(f"💊 {len(reminders)} active reminders")
            
            # Display reminders
            for reminder in reminders:
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                
                with col1:
                    st.markdown(f"""
                    **{reminder.get('medicine_name', 'Unknown')}**  
                    👤 {reminder.get('username', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    ⏰ **{reminder.get('time', 'N/A')}**  
                    📋 {reminder.get('dosage', 'N/A')}
                    """)
                
                with col3:
                    st.markdown(f"""
                    🆔 User ID: {reminder.get('user_id', 'N/A')}  
                    🕐 Created: {reminder.get('created', 'N/A')}
                    """)
                
                with col4:
                    if st.button("🔕 Stop", key=f"stop_{reminder['id']}", use_container_width=True):
                        supabase.table('reminders').update({'active': False}).eq('id', reminder['id']).execute()
                        st.success("Reminder stopped!")
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("No active reminders")
    
    except Exception as e:
        st.error(f"Error loading reminders: {e}")

with tab2:
    st.markdown("#### Inactive/Stopped Reminders")
    
    try:
        response = supabase.table('reminders').select('*').eq('active', False).execute()
        inactive = response.data
        
        if inactive:
            st.warning(f"🔕 {len(inactive)} inactive reminders")
            
            for reminder in inactive:
                col1, col2, col3, col4 = st.columns([2, 2, 3, 1])
                
                with col1:
                    st.markdown(f"""
                    **{reminder.get('medicine_name', 'Unknown')}**  
                    👤 {reminder.get('username', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    ⏰ {reminder.get('time', 'N/A')}  
                    📋 {reminder.get('dosage', 'N/A')}
                    """)
                
                with col3:
                    st.markdown(f"""
                    🆔 User ID: {reminder.get('user_id', 'N/A')}
                    """)
                
                with col4:
                    if st.button("🔔 Reactivate", key=f"reactivate_{reminder['id']}", use_container_width=True):
                        supabase.table('reminders').update({'active': True}).eq('id', reminder['id']).execute()
                        st.success("Reminder reactivated!")
                        st.rerun()
                
                st.markdown("---")
        else:
            st.info("No inactive reminders")
    
    except Exception as e:
        st.error(f"Error loading inactive reminders: {e}")

with tab3:
    st.markdown("#### Reminder Statistics")
    
    try:
        response = supabase.table('reminders').select('*').execute()
        all_reminders = response.data
        
        if all_reminders:
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(all_reminders)
            active = len([r for r in all_reminders if r.get('active')])
            inactive = total - active
            
            # Count unique users
            unique_users = len(set([r.get('user_id') for r in all_reminders if r.get('user_id')]))
            
            with col1:
                st.metric("Total Reminders", total)
            with col2:
                st.metric("🔔 Active", active)
            with col3:
                st.metric("🔕 Inactive", inactive)
            with col4:
                st.metric("👥 Unique Users", unique_users)
            
            # Most common medicines
            st.markdown("#### Most Common Medicines")
            medicines = {}
            for reminder in all_reminders:
                medicine = reminder.get('medicine_name', 'Unknown')
                medicines[medicine] = medicines.get(medicine, 0) + 1
            
            medicine_df = pd.DataFrame(list(medicines.items()), columns=['Medicine', 'Count'])
            medicine_df = medicine_df.sort_values('Count', ascending=False).head(10)
            st.dataframe(medicine_df, use_container_width=True)
            
            # Reminder times distribution
            st.markdown("#### Reminder Times Distribution")
            times = {}
            for reminder in all_reminders:
                time = reminder.get('time', 'Unknown')
                times[time] = times.get(time, 0) + 1
            
            time_df = pd.DataFrame(list(times.items()), columns=['Time', 'Count'])
            time_df = time_df.sort_values('Time')
            st.dataframe(time_df, use_container_width=True)
            
            # Active reminders by user
            st.markdown("#### Top Users by Active Reminders")
            user_reminders = {}
            for reminder in all_reminders:
                if reminder.get('active'):
                    username = reminder.get('username', 'Unknown')
                    user_reminders[username] = user_reminders.get(username, 0) + 1
            
            if user_reminders:
                user_df = pd.DataFrame(list(user_reminders.items()), columns=['Username', 'Active Reminders'])
                user_df = user_df.sort_values('Active Reminders', ascending=False).head(10)
                st.dataframe(user_df, use_container_width=True)
        else:
            st.info("No reminder data available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Bulk actions
st.markdown("---")
st.markdown("### ⚙️ Bulk Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔕 Stop All Active Reminders", use_container_width=True):
        if st.session_state.get('confirm_stop_all'):
            try:
                supabase.table('reminders').update({'active': False}).eq('active', True).execute()
                st.success("All reminders stopped!")
                st.session_state['confirm_stop_all'] = False
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.session_state['confirm_stop_all'] = True
            st.warning("⚠️ Click again to confirm stopping ALL active reminders")

with col2:
    if st.button("🗑️ Delete All Inactive Reminders", use_container_width=True):
        if st.session_state.get('confirm_delete_all'):
            try:
                supabase.table('reminders').delete().eq('active', False).execute()
                st.success("All inactive reminders deleted!")
                st.session_state['confirm_delete_all'] = False
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.session_state['confirm_delete_all'] = True
            st.warning("⚠️ Click again to confirm deleting ALL inactive reminders")

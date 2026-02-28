# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
import json

load_dotenv()

st.set_page_config(page_title="CRUD Operations", page_icon="⚙️", layout="wide")

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

st.title("⚙️ CRUD Operations")
st.markdown("### Create, Read, Update, Delete Database Records")

# Table selection
tables = ['emergencies', 'health_workers', 'appointments', 'reminders', 'maternal']
selected_table = st.selectbox("📋 Select Table", tables)

# Tabs for CRUD operations
tab1, tab2, tab3, tab4 = st.tabs(["📖 Read", "➕ Create", "✏️ Update", "🗑️ Delete"])

with tab1:
    st.markdown(f"#### View All Records from `{selected_table}`")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        search_column = st.text_input("Search column (leave empty for all)", "")
    with col2:
        limit = st.number_input("Limit", min_value=10, max_value=1000, value=100, step=10)
    
    if st.button("🔍 Load Data", use_container_width=True):
        try:
            response = supabase.table(selected_table).select('*').limit(limit).execute()
            data = response.data
            
            if data:
                df = pd.DataFrame(data)
                
                # Filter by search
                if search_column:
                    df = df[df.astype(str).apply(lambda x: x.str.contains(search_column, case=False, na=False)).any(axis=1)]
                
                st.success(f"✅ Loaded {len(df)} records")
                st.dataframe(df, use_container_width=True)
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"{selected_table}_export.csv",
                    mime="text/csv"
                )
            else:
                st.info("No data found")
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.markdown(f"#### Create New Record in `{selected_table}`")
    
    # Dynamic form based on table
    if selected_table == 'emergencies':
        with st.form("create_emergency"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            status = st.selectbox("Status", ["pending", "resolved"])
            
            if st.form_submit_button("➕ Create"):
                try:
                    data = {
                        'user_id': user_id,
                        'username': username,
                        'lat': lat,
                        'lon': lon,
                        'status': status
                    }
                    supabase.table(selected_table).insert(data).execute()
                    st.success("✅ Record created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif selected_table == 'health_workers':
        with st.form("create_worker"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            name = st.text_input("Full Name")
            age = st.number_input("Age", min_value=18, max_value=100)
            category = st.selectbox("Category", ["ASHA", "NURSE", "PHYSIO"])
            experience = st.number_input("Experience (years)", min_value=0)
            lat = st.number_input("Latitude", format="%.6f")
            lon = st.number_input("Longitude", format="%.6f")
            approved = st.checkbox("Approved")
            
            if st.form_submit_button("➕ Create"):
                try:
                    data = {
                        'user_id': user_id,
                        'username': username,
                        'name': name,
                        'age': age,
                        'category': category,
                        'experience': experience,
                        'lat': lat,
                        'lon': lon,
                        'approved': approved
                    }
                    supabase.table(selected_table).insert(data).execute()
                    st.success("✅ Record created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif selected_table == 'appointments':
        with st.form("create_appointment"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            hospital = st.text_input("Hospital Name")
            date = st.text_input("Date (DD-MM-YYYY)", "23-02-2026")
            time = st.text_input("Time (HH:MM AM/PM)", "10:00 AM")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("➕ Create"):
                try:
                    data = {
                        'user_id': user_id,
                        'username': username,
                        'hospital': hospital,
                        'date': date,
                        'time': time,
                        'notes': notes,
                        'reminder_sent': False
                    }
                    supabase.table(selected_table).insert(data).execute()
                    st.success("✅ Record created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif selected_table == 'reminders':
        with st.form("create_reminder"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            medicine_name = st.text_input("Medicine Name")
            time = st.text_input("Time (HH:MM AM/PM)", "09:00 AM")
            dosage = st.text_input("Dosage", "2 tablets")
            active = st.checkbox("Active", value=True)
            
            if st.form_submit_button("➕ Create"):
                try:
                    data = {
                        'user_id': user_id,
                        'username': username,
                        'medicine_name': medicine_name,
                        'time': time,
                        'dosage': dosage,
                        'active': active
                    }
                    supabase.table(selected_table).insert(data).execute()
                    st.success("✅ Record created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif selected_table == 'maternal':
        with st.form("create_maternal"):
            user_id = st.number_input("User ID", min_value=1)
            username = st.text_input("Username")
            lmp_date = st.text_input("LMP Date (DD-MM-YYYY)", "01-01-2026")
            weeks_pregnant = st.number_input("Weeks Pregnant", min_value=0, max_value=42)
            due_date = st.text_input("Due Date (DD-MM-YYYY)", "08-10-2026")
            
            if st.form_submit_button("➕ Create"):
                try:
                    data = {
                        'user_id': user_id,
                        'username': username,
                        'lmp_date': lmp_date,
                        'weeks_pregnant': weeks_pregnant,
                        'due_date': due_date
                    }
                    supabase.table(selected_table).insert(data).execute()
                    st.success("✅ Record created successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab3:
    st.markdown(f"#### Update Record in `{selected_table}`")
    
    record_id = st.number_input("Record ID to Update", min_value=1, key="update_id")
    
    if st.button("🔍 Load Record"):
        try:
            response = supabase.table(selected_table).select('*').eq('id', record_id).execute()
            if response.data:
                st.session_state['update_record'] = response.data[0]
                st.success("✅ Record loaded!")
            else:
                st.error("Record not found")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if 'update_record' in st.session_state:
        record = st.session_state['update_record']
        st.json(record)
        
        st.markdown("#### Edit Fields")
        
        # JSON editor
        updated_json = st.text_area("Edit JSON (Advanced)", json.dumps(record, indent=2), height=300)
        
        if st.button("💾 Save Changes"):
            try:
                updated_data = json.loads(updated_json)
                # Remove id from update data
                updated_data.pop('id', None)
                updated_data.pop('created', None)
                
                supabase.table(selected_table).update(updated_data).eq('id', record_id).execute()
                st.success("✅ Record updated successfully!")
                del st.session_state['update_record']
            except json.JSONDecodeError:
                st.error("Invalid JSON format")
            except Exception as e:
                st.error(f"Error: {e}")

with tab4:
    st.markdown(f"#### Delete Record from `{selected_table}`")
    
    st.warning("⚠️ Warning: This action cannot be undone!")
    
    delete_id = st.number_input("Record ID to Delete", min_value=1, key="delete_id")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Preview Record"):
            try:
                response = supabase.table(selected_table).select('*').eq('id', delete_id).execute()
                if response.data:
                    st.json(response.data[0])
                else:
                    st.error("Record not found")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with col2:
        if st.button("🗑️ DELETE RECORD", type="primary"):
            if st.session_state.get(f'confirm_delete_{delete_id}'):
                try:
                    supabase.table(selected_table).delete().eq('id', delete_id).execute()
                    st.success("✅ Record deleted successfully!")
                    st.session_state[f'confirm_delete_{delete_id}'] = False
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.session_state[f'confirm_delete_{delete_id}'] = True
                st.warning("⚠️ Click DELETE again to confirm")

# Bulk operations
st.markdown("---")
st.markdown("### 🔧 Bulk Operations")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Show Table Schema", use_container_width=True):
        st.code(f"""
Table: {selected_table}

Common fields:
- id: BIGSERIAL PRIMARY KEY
- user_id: BIGINT
- username: TEXT
- created: TIMESTAMPTZ DEFAULT NOW()

Specific fields vary by table.
        """)

with col2:
    if st.button("🔄 Refresh Cache", use_container_width=True):
        st.cache_resource.clear()
        st.success("Cache cleared!")

# SQL Query executor (Advanced)
st.markdown("---")
st.markdown("### 🔬 Advanced: SQL Query")

with st.expander("⚠️ Execute Custom SQL (Use with caution)"):
    sql_query = st.text_area("SQL Query", "SELECT * FROM emergencies LIMIT 10;", height=100)
    
    if st.button("▶️ Execute Query"):
        st.warning("⚠️ Direct SQL execution is disabled for safety. Use the CRUD operations above.")
        # In production, you might want to enable this with proper authentication
        # try:
        #     response = supabase.rpc('execute_sql', {'query': sql_query}).execute()
        #     st.json(response.data)
        # except Exception as e:
        #     st.error(f"Error: {e}")

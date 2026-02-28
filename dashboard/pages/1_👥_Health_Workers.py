# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
import folium
from streamlit_folium import folium_static

load_dotenv()

st.set_page_config(page_title="Health Workers", page_icon="👥", layout="wide")

# Custom CSS
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
    .approve-btn {background-color: #4caf50 !important;}
    .reject-btn {background-color: #f44336 !important;}
</style>
""", unsafe_allow_html=True)

# Initialize Supabase
@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

st.title("👥 Health Workers Management")
st.markdown("### Manage ASHA, Nurses, and Physiotherapists")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Workers", "⏳ Pending Approval", "🗺️ Worker Map"])

with tab1:
    st.markdown("#### All Registered Health Workers")
    
    # Search bar
    search = st.text_input("🔍 Search by name, category, or username", "")
    
    try:
        response = supabase.table('health_workers').select('*').execute()
        workers = response.data
        
        if workers:
            # Filter by search
            if search:
                workers = [w for w in workers if 
                          search.lower() in w.get('name', '').lower() or
                          search.lower() in w.get('category', '').lower() or
                          search.lower() in w.get('username', '').lower()]
            
            # Display as cards
            for worker in workers:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                
                with col1:
                    status = "✅ Approved" if worker.get('approved') else "⏳ Pending"
                    st.markdown(f"""
                    **{worker.get('name', 'Unknown')}**  
                    🏷️ {worker.get('category', 'N/A')} | {status}  
                    📱 @{worker.get('username', 'N/A')}
                    """)
                
                with col2:
                    st.markdown(f"""
                    🎂 Age: {worker.get('age', 'N/A')}  
                    📅 Exp: {worker.get('experience', 'N/A')} years
                    """)
                
                with col3:
                    if worker.get('lat') and worker.get('lon'):
                        st.markdown(f"""
                        📍 Location:  
                        {worker['lat']:.4f}, {worker['lon']:.4f}
                        """)
                    else:
                        st.markdown("📍 No location")
                
                with col4:
                    if not worker.get('approved'):
                        if st.button(f"✅ Approve", key=f"approve_{worker['id']}"):
                            supabase.table('health_workers').update({'approved': True}).eq('id', worker['id']).execute()
                            st.success("Worker approved!")
                            st.rerun()
                    else:
                        if st.button(f"❌ Revoke", key=f"revoke_{worker['id']}"):
                            supabase.table('health_workers').update({'approved': False}).eq('id', worker['id']).execute()
                            st.warning("Approval revoked!")
                            st.rerun()
                
                st.markdown("---")
            
            st.info(f"📊 Total Workers: {len(workers)}")
        else:
            st.info("No health workers registered yet")
    
    except Exception as e:
        st.error(f"Error loading workers: {e}")

with tab2:
    st.markdown("#### Pending Approval Requests")
    
    try:
        response = supabase.table('health_workers').select('*').eq('approved', False).execute()
        pending = response.data
        
        if pending:
            for worker in pending:
                with st.expander(f"👤 {worker.get('name', 'Unknown')} - {worker.get('category', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"""
                        **Personal Details:**
                        - 👤 Name: {worker.get('name', 'N/A')}
                        - 🎂 Age: {worker.get('age', 'N/A')}
                        - 🏷️ Category: {worker.get('category', 'N/A')}
                        - 📅 Experience: {worker.get('experience', 'N/A')} years
                        - 📱 Username: @{worker.get('username', 'N/A')}
                        - 🆔 User ID: {worker.get('user_id', 'N/A')}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        **Location:**
                        - 📍 Latitude: {worker.get('lat', 'N/A')}
                        - 📍 Longitude: {worker.get('lon', 'N/A')}
                        - 🕐 Registered: {worker.get('created', 'N/A')}
                        """)
                        
                        if worker.get('lat') and worker.get('lon'):
                            # Mini map
                            m = folium.Map(location=[worker['lat'], worker['lon']], zoom_start=13)
                            folium.Marker(
                                [worker['lat'], worker['lon']],
                                popup=worker.get('name', 'Worker'),
                                icon=folium.Icon(color='blue', icon='user-md', prefix='fa')
                            ).add_to(m)
                            folium_static(m, width=300, height=200)
                    
                    col1, col2, col3 = st.columns([1, 1, 3])
                    with col1:
                        if st.button("✅ Approve", key=f"approve_pending_{worker['id']}", use_container_width=True):
                            supabase.table('health_workers').update({'approved': True}).eq('id', worker['id']).execute()
                            st.success(f"✅ {worker.get('name')} approved!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Reject", key=f"reject_{worker['id']}", use_container_width=True):
                            supabase.table('health_workers').delete().eq('id', worker['id']).execute()
                            st.warning(f"❌ {worker.get('name')} rejected and removed")
                            st.rerun()
            
            st.warning(f"⏳ {len(pending)} workers awaiting approval")
        else:
            st.success("✅ No pending approvals!")
    
    except Exception as e:
        st.error(f"Error loading pending workers: {e}")

with tab3:
    st.markdown("#### Health Workers Location Map")
    
    try:
        response = supabase.table('health_workers').select('*').execute()
        workers = response.data
        
        if workers:
            # Create map
            m = folium.Map(location=[22.5, 72.5], zoom_start=8)
            
            # Add markers
            for worker in workers:
                if worker.get('lat') and worker.get('lon'):
                    color = 'green' if worker.get('approved') else 'orange'
                    icon = 'user-md'
                    
                    folium.Marker(
                        location=[worker['lat'], worker['lon']],
                        popup=f"""
                        <b>{worker.get('name', 'Unknown')}</b><br>
                        Category: {worker.get('category', 'N/A')}<br>
                        Experience: {worker.get('experience', 'N/A')} years<br>
                        Status: {'Approved' if worker.get('approved') else 'Pending'}<br>
                        Contact: @{worker.get('username', 'N/A')}
                        """,
                        icon=folium.Icon(color=color, icon=icon, prefix='fa')
                    ).add_to(m)
            
            folium_static(m, width=1200, height=600)
            
            # Legend
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🟢 **Green** = Approved Workers")
            with col2:
                st.markdown("🟠 **Orange** = Pending Approval")
        else:
            st.info("No workers to display on map")
    
    except Exception as e:
        st.error(f"Error loading map: {e}")

# Statistics
st.markdown("---")
st.markdown("### 📊 Statistics")

try:
    response = supabase.table('health_workers').select('*').execute()
    workers = response.data
    
    if workers:
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(workers)
        approved = len([w for w in workers if w.get('approved')])
        pending = total - approved
        
        # Count by category
        asha = len([w for w in workers if w.get('category', '').upper() == 'ASHA'])
        nurse = len([w for w in workers if w.get('category', '').upper() == 'NURSE'])
        physio = len([w for w in workers if w.get('category', '').upper() == 'PHYSIO'])
        
        with col1:
            st.metric("Total Workers", total)
        with col2:
            st.metric("✅ Approved", approved)
        with col3:
            st.metric("⏳ Pending", pending)
        with col4:
            avg_exp = sum([w.get('experience', 0) for w in workers]) / total if total > 0 else 0
            st.metric("Avg Experience", f"{avg_exp:.1f} years")
        
        st.markdown("#### By Category")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("ASHA Workers", asha)
        with col2:
            st.metric("Nurses", nurse)
        with col3:
            st.metric("Physiotherapists", physio)

except Exception as e:
    st.error(f"Error loading statistics: {e}")

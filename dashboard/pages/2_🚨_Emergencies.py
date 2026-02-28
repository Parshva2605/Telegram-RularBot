# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import pandas as pd
import folium
from streamlit_folium import folium_static
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Emergencies", page_icon="🚨", layout="wide")

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
    .emergency-card {
        background: #fff3cd;
        border-left: 5px solid #ff5722;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .resolved-card {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Supabase without caching to avoid stale data
def get_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = get_supabase()

st.title("🚨 Emergency Management")
st.markdown("### Monitor and Respond to SOS Alerts")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔴 Active Emergencies", "✅ Resolved", "🗺️ Emergency Map"])

with tab1:
    st.markdown("#### Active Emergency Alerts")
    
    # Filter
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search by username or ID", "")
    with col2:
        show_resolved = st.checkbox("Show Resolved", value=False)
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
    
    try:
        if show_resolved:
            response = supabase.table('emergencies').select('*').execute()
        else:
            response = supabase.table('emergencies').select('*').eq('status', 'pending').execute()
        emergencies = response.data
        
        if emergencies:
            # Sort by timestamp (newest first)
            emergencies = sorted(emergencies, key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Filter by search
            if search:
                emergencies = [e for e in emergencies if 
                              search.lower() in str(e.get('username', '')).lower() or
                              search.lower() in str(e.get('id', '')).lower()]
            
            st.warning(f"🚨 {len(emergencies)} ACTIVE EMERGENCIES")
            
            for emergency in emergencies:
                card_class = "emergency-card"
                
                with st.container():
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Emergency #{emergency.get('id')}**  
                        👤 User: {emergency.get('username', 'Unknown')}  
                        🆔 ID: {emergency.get('user_id', 'N/A')}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        📍 **Location:**  
                        Lat: {emergency.get('lat', 'N/A')}  
                        Lon: {emergency.get('lon', 'N/A')}
                        """)
                        if emergency.get('lat') and emergency.get('lon'):
                            maps_link = f"https://maps.google.com/?q={emergency['lat']},{emergency['lon']}"
                            st.markdown(f"[🗺️ Open in Google Maps]({maps_link})")
                    
                    with col3:
                        timestamp = emergency.get('timestamp', 'N/A')
                        st.markdown(f"""
                        🕐 **Time:**  
                        {timestamp}
                        """)
                        
                        # Calculate time elapsed
                        try:
                            if timestamp != 'N/A':
                                alert_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                elapsed = datetime.now(alert_time.tzinfo) - alert_time
                                minutes = int(elapsed.total_seconds() / 60)
                                st.markdown(f"⏱️ {minutes} minutes ago")
                        except:
                            pass
                    
                    with col4:
                        status = emergency.get('status', 'pending')
                        emergency_id = emergency.get('id')
                        
                        if status == 'pending':
                            if st.button("✅ Resolve", key=f"resolve_{emergency_id}", use_container_width=True):
                                try:
                                    # Debug: Show what we're updating
                                    st.info(f"Updating emergency ID: {emergency_id}")
                                    
                                    # Update the emergency status
                                    result = supabase.table('emergencies').update({'status': 'resolved'}).eq('id', emergency_id).execute()
                                    
                                    # Debug: Show result
                                    st.write(f"Update result: {result}")
                                    
                                    st.success(f"✅ Emergency #{emergency_id} resolved!")
                                    
                                    # Wait a moment before reloading
                                    import time
                                    time.sleep(0.5)
                                    
                                    # Force page reload
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Error resolving emergency: {str(e)}")
                                    import traceback
                                    st.code(traceback.format_exc())
                        else:
                            st.success("✅ Resolved")
                        
                        if st.button("📞 Call 108", key=f"call_{emergency_id}", use_container_width=True):
                            st.info("Ambulance dispatched!")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.success("✅ No active emergencies!")
            st.balloons()
    
    except Exception as e:
        st.error(f"Error loading emergencies: {e}")

with tab2:
    st.markdown("#### Resolved Emergencies")
    
    try:
        response = supabase.table('emergencies').select('*').eq('status', 'resolved').execute()
        resolved = response.data
        
        if resolved:
            # Sort by timestamp (newest first)
            resolved = sorted(resolved, key=lambda x: x.get('timestamp', ''), reverse=True)[:20]
            
            st.info(f"✅ Showing last 20 resolved emergencies")
            
            for emergency in resolved:
                with st.container():
                    st.markdown('<div class="resolved-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        st.markdown(f"""
                        **Emergency #{emergency.get('id')}** ✅  
                        👤 {emergency.get('username', 'Unknown')}
                        """)
                    
                    with col2:
                        st.markdown(f"""
                        📍 {emergency.get('lat', 'N/A')}, {emergency.get('lon', 'N/A')}
                        """)
                    
                    with col3:
                        st.markdown(f"""
                        🕐 {emergency.get('timestamp', 'N/A')}
                        """)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No resolved emergencies yet")
    
    except Exception as e:
        st.error(f"Error loading resolved emergencies: {e}")

with tab3:
    st.markdown("#### Emergency Locations Map")
    
    # Map controls
    col1, col2 = st.columns(2)
    with col1:
        show_pending = st.checkbox("🔴 Show Pending", value=True)
    with col2:
        show_resolved = st.checkbox("🟢 Show Resolved", value=False)
    
    try:
        # Get emergencies
        all_emergencies = []
        
        if show_pending:
            response = supabase.table('emergencies').select('*').eq('status', 'pending').execute()
            all_emergencies.extend(response.data or [])
        
        if show_resolved:
            response = supabase.table('emergencies').select('*').eq('status', 'resolved').execute()
            all_emergencies.extend(response.data or [])
        
        if all_emergencies:
            # Create map
            m = folium.Map(location=[22.5, 72.5], zoom_start=8)
            
            # Add markers
            for emergency in all_emergencies:
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
                        Time: {emergency.get('timestamp', 'N/A')}<br>
                        <a href="https://maps.google.com/?q={emergency['lat']},{emergency['lon']}" target="_blank">Open in Google Maps</a>
                        """,
                        icon=icon
                    ).add_to(m)
            
            folium_static(m, width=1200, height=600)
            
            # Legend
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🔴 **Red ⚠️** = Pending Emergencies (Exclamation)")
            with col2:
                st.markdown("🟢 **Green ✓** = Resolved Emergencies (Checkmark)")
        else:
            st.info("No emergencies to display on map")
    
    except Exception as e:
        st.error(f"Error loading map: {e}")

# Statistics
st.markdown("---")
st.markdown("### 📊 Emergency Statistics")

try:
    response = supabase.table('emergencies').select('*').execute()
    all_emergencies = response.data
    
    if all_emergencies:
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(all_emergencies)
        pending = len([e for e in all_emergencies if e.get('status') == 'pending'])
        resolved = len([e for e in all_emergencies if e.get('status') == 'resolved'])
        
        with col1:
            st.metric("Total Emergencies", total)
        with col2:
            st.metric("🔴 Pending", pending)
        with col3:
            st.metric("✅ Resolved", resolved)
        with col4:
            resolution_rate = (resolved / total * 100) if total > 0 else 0
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        # Today's emergencies
        today = datetime.now().strftime('%Y-%m-%d')
        today_emergencies = [e for e in all_emergencies if today in e.get('timestamp', '')]
        st.metric("📅 Today's Emergencies", len(today_emergencies))

except Exception as e:
    st.error(f"Error loading statistics: {e}")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

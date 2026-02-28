# -*- coding: utf-8 -*-
"""
MediMind Admin - Manage Doctors
View, add, edit, and delete doctors
"""

import streamlit as st
import os
from dotenv import load_dotenv
import sys
import secrets

# Add parent directory to path to import supabase_wrapper
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from supabase_wrapper import create_client

load_dotenv()

st.set_page_config(page_title="Manage Doctors", page_icon="👨‍⚕️", layout="wide")

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
        background: #1e1e1e;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        color: white;
    }
    .inactive-card {
        background: #1e1e1e;
        border-left: 5px solid #f44336;
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

# Check admin access
ADMIN_ID = os.getenv('ADMIN_ID', '1155518443')

st.title("👨‍⚕️ Manage Doctors")
st.markdown("Admin panel to manage doctor accounts")
st.markdown("---")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Doctors", "➕ Add Doctor", "📊 Statistics"])

# ============================================
# TAB 1: ALL DOCTORS
# ============================================
with tab1:
    st.header("📋 All Doctors")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("🔍 Search by name", placeholder="Dr. Shah")
    
    with col2:
        filter_status = st.selectbox("Filter by status", ["All", "Active", "Inactive"])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Total Cases", "Rating", "Created Date"])
    
    st.markdown("---")
    
    try:
        # Get all doctors
        doctors_response = supabase.table("doctors").select("*").execute()
        
        if doctors_response.data:
            doctors = doctors_response.data
            
            # Apply filters
            if search_name:
                doctors = [d for d in doctors if search_name.lower() in d.get('name', '').lower()]
            
            if filter_status == "Active":
                doctors = [d for d in doctors if d.get('active', False)]
            elif filter_status == "Inactive":
                doctors = [d for d in doctors if not d.get('active', False)]
            
            # Sort
            if sort_by == "Name":
                doctors = sorted(doctors, key=lambda x: x.get('name', ''))
            elif sort_by == "Total Cases":
                doctors = sorted(doctors, key=lambda x: x.get('total_cases', 0), reverse=True)
            elif sort_by == "Rating":
                doctors = sorted(doctors, key=lambda x: x.get('rating', 0), reverse=True)
            elif sort_by == "Created Date":
                doctors = sorted(doctors, key=lambda x: x.get('created', ''), reverse=True)
            
            st.success(f"📊 {len(doctors)} doctor(s) found")
            
            # Display doctors
            for doctor in doctors:
                card_class = "doctor-card" if doctor.get('active', False) else "inactive-card"
                status_emoji = "✅" if doctor.get('active', False) else "❌"
                
                with st.container():
                    st.markdown(f"""
                    <div class="{card_class}">
                        <h4>{status_emoji} {doctor.get('name', 'Unknown')}</h4>
                        <p>📱 Phone: {doctor.get('phone', 'N/A')}</p>
                        <p>🩺 MCI: {doctor.get('mci_reg', 'N/A')}</p>
                        <p>🏥 PHC: {doctor.get('phc', 'N/A')}</p>
                        <p>⭐ Rating: {doctor.get('rating', 0):.1f}/5.0 | 📊 Cases: {doctor.get('total_cases', 0)}</p>
                        <p>🔐 Access Code: {doctor.get('access_code', 'N/A')}</p>
                        <p>🆔 ID: {doctor.get('id')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button(f"✏️ Edit", key=f"edit_{doctor['id']}"):
                            st.session_state[f'editing_{doctor["id"]}'] = True
                            st.rerun()
                    
                    with col2:
                        if doctor.get('active', False):
                            if st.button(f"🚫 Deactivate", key=f"deactivate_{doctor['id']}"):
                                try:
                                    supabase.table("doctors").update({"active": False}).eq("id", doctor['id']).execute()
                                    st.success("Doctor deactivated")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            if st.button(f"✅ Activate", key=f"activate_{doctor['id']}"):
                                try:
                                    supabase.table("doctors").update({"active": True}).eq("id", doctor['id']).execute()
                                    st.success("Doctor activated")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                    
                    with col3:
                        if st.button(f"🔄 Reset Code", key=f"reset_{doctor['id']}"):
                            try:
                                new_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
                                supabase.table("doctors").update({"access_code": new_code}).eq("id", doctor['id']).execute()
                                st.success(f"New code: {new_code}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col4:
                        if st.button(f"🗑️ Delete", key=f"delete_{doctor['id']}"):
                            st.session_state[f'confirm_delete_{doctor["id"]}'] = True
                    
                    # Edit form
                    if st.session_state.get(f'editing_{doctor["id"]}', False):
                        with st.expander("✏️ Edit Doctor", expanded=True):
                            with st.form(key=f'edit_form_{doctor["id"]}'):
                                edit_name = st.text_input("Name", value=doctor.get('name', ''))
                                edit_phone = st.text_input("Phone", value=doctor.get('phone', ''))
                                edit_mci = st.text_input("MCI Registration", value=doctor.get('mci_reg', ''))
                                edit_phc = st.text_input("PHC", value=doctor.get('phc', ''))
                                edit_rating = st.slider("Rating", 0.0, 5.0, float(doctor.get('rating', 0)), 0.1)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("💾 Save"):
                                        try:
                                            supabase.table("doctors").update({
                                                "name": edit_name,
                                                "phone": edit_phone,
                                                "mci_reg": edit_mci,
                                                "phc": edit_phc,
                                                "rating": edit_rating
                                            }).eq("id", doctor['id']).execute()
                                            
                                            st.success("Doctor updated!")
                                            st.session_state[f'editing_{doctor["id"]}'] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error: {e}")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancel"):
                                        st.session_state[f'editing_{doctor["id"]}'] = False
                                        st.rerun()
                    
                    # Delete confirmation
                    if st.session_state.get(f'confirm_delete_{doctor["id"]}', False):
                        st.warning(f"⚠️ Are you sure you want to delete Dr. {doctor.get('name')}?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"✅ Yes, Delete", key=f"confirm_yes_{doctor['id']}"):
                                try:
                                    supabase.table("doctors").delete().eq("id", doctor['id']).execute()
                                    st.success("Doctor deleted")
                                    st.session_state[f'confirm_delete_{doctor["id"]}'] = False
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        with col2:
                            if st.button(f"❌ Cancel", key=f"confirm_no_{doctor['id']}"):
                                st.session_state[f'confirm_delete_{doctor["id"]}'] = False
                                st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("📭 No doctors found")
    
    except Exception as e:
        st.error(f"❌ Error loading doctors: {e}")

# ============================================
# TAB 2: ADD DOCTOR
# ============================================
with tab2:
    st.header("➕ Add New Doctor")
    
    with st.form("add_doctor_form"):
        st.markdown("### Doctor Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("👨‍⚕️ Full Name *", placeholder="Dr. Rajesh Shah")
            new_phone = st.text_input("📱 Phone Number *", placeholder="+919876543210")
            new_mci = st.text_input("🩺 MCI Registration *", placeholder="GJMC12345")
        
        with col2:
            new_phc = st.text_input("🏥 PHC Name *", placeholder="Anklav PHC")
            new_telegram_id = st.number_input("📱 Telegram ID (optional)", min_value=0, value=0, step=1)
            new_rating = st.slider("⭐ Initial Rating", 0.0, 5.0, 5.0, 0.1)
        
        st.markdown("### Access Code")
        col1, col2 = st.columns(2)
        
        with col1:
            auto_generate = st.checkbox("🔐 Auto-generate access code", value=True)
        
        with col2:
            if not auto_generate:
                custom_code = st.text_input("Custom Access Code", placeholder="ABC12345")
        
        st.markdown("---")
        
        submitted = st.form_submit_button("➕ Add Doctor", type="primary", use_container_width=True)
        
        if submitted:
            if not new_name or not new_phone or not new_mci or not new_phc:
                st.error("❌ Please fill all required fields (*)")
            else:
                try:
                    # Generate or use custom access code
                    if auto_generate:
                        access_code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
                    else:
                        access_code = custom_code if custom_code else ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
                    
                    # Insert doctor
                    result = supabase.table("doctors").insert({
                        "name": new_name,
                        "phone": new_phone,
                        "telegram_id": new_telegram_id if new_telegram_id > 0 else None,
                        "access_code": access_code,
                        "mci_reg": new_mci,
                        "phc": new_phc,
                        "rating": new_rating,
                        "total_cases": 0,
                        "active": True
                    }).execute()
                    
                    st.success("✅ Doctor added successfully!")
                    st.info(f"🔐 Access Code: **{access_code}**")
                    st.info(f"📱 Phone: **{new_phone}**")
                    st.markdown("---")
                    st.markdown("**Share these credentials with the doctor:**")
                    st.code(f"""
Phone: {new_phone}
Access Code: {access_code}

Login at: [Dashboard URL]
Or register via Telegram: @MediMindDoctorBot
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Error adding doctor: {e}")

# ============================================
# TAB 3: STATISTICS
# ============================================
with tab3:
    st.header("📊 Doctor Statistics")
    
    try:
        doctors_response = supabase.table("doctors").select("*").execute()
        
        if doctors_response.data:
            doctors = doctors_response.data
            
            # Calculate statistics
            total_doctors = len(doctors)
            active_doctors = len([d for d in doctors if d.get('active', False)])
            inactive_doctors = total_doctors - active_doctors
            total_cases = sum(d.get('total_cases', 0) for d in doctors)
            avg_rating = sum(d.get('rating', 0) for d in doctors) / total_doctors if total_doctors > 0 else 0
            
            # Display metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("👨‍⚕️ Total Doctors", total_doctors)
            
            with col2:
                st.metric("✅ Active", active_doctors)
            
            with col3:
                st.metric("❌ Inactive", inactive_doctors)
            
            with col4:
                st.metric("📊 Total Cases", total_cases)
            
            with col5:
                st.metric("⭐ Avg Rating", f"{avg_rating:.1f}")
            
            st.markdown("---")
            
            # Top doctors
            st.markdown("### 🏆 Top Doctors by Cases")
            top_doctors = sorted(doctors, key=lambda x: x.get('total_cases', 0), reverse=True)[:5]
            
            for i, doctor in enumerate(top_doctors, 1):
                st.markdown(f"""
                **{i}. {doctor.get('name', 'Unknown')}**
                - Cases: {doctor.get('total_cases', 0)}
                - Rating: {doctor.get('rating', 0):.1f}/5.0
                - PHC: {doctor.get('phc', 'N/A')}
                """)
            
            st.markdown("---")
            
            # PHC distribution
            st.markdown("### 🏥 Doctors by PHC")
            phc_counts = {}
            for doctor in doctors:
                phc = doctor.get('phc', 'Unknown')
                phc_counts[phc] = phc_counts.get(phc, 0) + 1
            
            for phc, count in sorted(phc_counts.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"- **{phc}**: {count} doctor(s)")
        
        else:
            st.info("📭 No data available")
    
    except Exception as e:
        st.error(f"❌ Error loading statistics: {e}")

st.markdown("---")
st.markdown("💡 **Admin Panel** - Manage all doctor accounts from here")

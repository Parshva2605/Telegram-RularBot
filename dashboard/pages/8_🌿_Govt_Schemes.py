# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Government Schemes", page_icon="🌿", layout="wide")

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
    .scheme-card {
        background: white;
        border-left: 5px solid #4caf50;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

# Auto-populate default schemes if table is empty
def init_default_schemes():
    try:
        response = supabase.table('govt_schemes').select('*', count='exact').execute()
        if response.count == 0:
            default_schemes = [
                {
                    "title_en": "PMMVY - Pradhan Mantri Matru Vandana Yojana",
                    "title_hi": "प्रधानमंत्री मातृ वंदना योजना",
                    "title_gu": "પ્રધાનમંત્રી માતૃ વંદના યોજના",
                    "desc_en": "₹6,000 in 3 installments for first living child. Apply at Anganwadi Center.",
                    "desc_hi": "पहले जीवित बच्चे के लिए 3 किस्तों में ₹6,000। आंगनवाड़ी केंद्र पर आवेदन करें।",
                    "desc_gu": "પ્રથમ જીવંત બાળક માટે 3 હપ્તામાં ₹6,000। આંગણવાડી કેન્દ્ર પર અરજી કરો।",
                    "phone": "104",
                    "link": "https://wcd.nic.in/schemes/pradhan-mantri-matru-vandana-yojana",
                    "active": True
                },
                {
                    "title_en": "JSSK - Janani Shishu Suraksha Karyakram",
                    "title_hi": "जननी शिशु सुरक्षा कार्यक्रम",
                    "title_gu": "જનની શિશુ સુરક્ષા કાર્યક્રમ",
                    "desc_en": "100% FREE delivery in govt hospitals. Free medicines, tests, ambulance (108), food during stay.",
                    "desc_hi": "सरकारी अस्पतालों में 100% मुफ्त प्रसव। मुफ्त दवाएं, जांच, एम्बुलेंस (108), रहने के दौरान भोजन।",
                    "desc_gu": "સરકારી હોસ્પિટલોમાં 100% મફત પ્રસૂતિ। મફત દવાઓ, પરીક્ષણો, એમ્બ્યુલન્સ (108), રહેવા દરમિયાન ભોજન।",
                    "phone": "108",
                    "link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=841&lid=309",
                    "active": True
                },
                {
                    "title_en": "Maa Amrutam Yojana (Gujarat)",
                    "title_hi": "माँ अमृतम योजना (गुजरात)",
                    "title_gu": "માં અમૃતમ યોજના (ગુજરાત)",
                    "desc_en": "FREE treatment up to ₹5 Lakh for BPL families. Covers surgeries, cancer, heart, kidney, maternity care.",
                    "desc_hi": "BPL परिवारों के लिए ₹5 लाख तक मुफ्त इलाज। सर्जरी, कैंसर, हृदय, किडनी, मातृत्व देखभाल शामिल।",
                    "desc_gu": "BPL પરિવારો માટે ₹5 લાખ સુધી મફત સારવાર। સર્જરી, કેન્સર, હૃદય, કિડની, માતૃત્વ સંભાળ સમાવેશ।",
                    "phone": "1800-233-1022",
                    "link": "https://mmcg.gujarat.gov.in/",
                    "active": True
                },
                {
                    "title_en": "Gujarat Matru Voucher Scheme",
                    "title_hi": "गुजरात मातृ वाउचर योजना",
                    "title_gu": "ગુજરાત માતૃ વાઉચર યોજના",
                    "desc_en": "₹4,000 voucher for nutrition support. Available at local PHC and Anganwadi centers.",
                    "desc_hi": "पोषण सहायता के लिए ₹4,000 वाउचर। स्थानीय PHC और आंगनवाड़ी केंद्रों पर उपलब्ध।",
                    "desc_gu": "પોષણ સહાય માટે ₹4,000 વાઉચર। સ્થાનિક PHC અને આંગણવાડી કેન્દ્રો પર ઉપલબ્ધ।",
                    "phone": "104",
                    "link": "https://gujhealth.gujarat.gov.in/",
                    "active": True
                },
                {
                    "title_en": "JSY - Janani Suraksha Yojana",
                    "title_hi": "जननी सुरक्षा योजना",
                    "title_gu": "જનની સુરક્ષા યોજના",
                    "desc_en": "Cash incentive for safe institutional delivery. Contact ASHA worker for registration.",
                    "desc_hi": "सुरक्षित संस्थागत प्रसव के लिए नकद प्रोत्साहन। पंजीकरण के लिए ASHA कार्यकर्ता से संपर्क करें।",
                    "desc_gu": "સુરક્ષિત સંસ્થાકીય પ્રસૂતિ માટે રોકડ પ્રોત્સાહન। નોંધણી માટે ASHA કાર્યકર સાથે સંપર્ક કરો।",
                    "phone": "ASHA Worker",
                    "link": "https://nhm.gov.in/index1.php?lang=1&level=3&sublinkid=841&lid=309",
                    "active": True
                }
            ]
            
            for scheme in default_schemes:
                supabase.table('govt_schemes').insert(scheme).execute()
            
            st.success("✅ Initialized 5 default Gujarat schemes!")
            return True
    except Exception as e:
        st.error(f"Error initializing schemes: {e}")
    return False

# Initialize schemes on first load
if 'schemes_initialized' not in st.session_state:
    init_default_schemes()
    st.session_state.schemes_initialized = True

st.title("🌿 Government Schemes Management")
st.markdown("### Manage Healthcare Schemes (CRUD)")

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Schemes", "➕ Add New Scheme", "📊 Statistics"])

with tab1:
    st.markdown("#### All Government Schemes")
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search schemes", "")
    with col2:
        language = st.selectbox("🌍 Language", ["English", "Hindi", "Gujarati"])
    with col3:
        show_inactive = st.checkbox("Show Inactive", value=False)
    
    try:
        if show_inactive:
            response = supabase.table('govt_schemes').select('*').execute()
        else:
            response = supabase.table('govt_schemes').select('*').eq('active', True).execute()
        
        schemes = response.data
        
        if schemes:
            # Filter by search
            if search:
                schemes = [s for s in schemes if 
                          search.lower() in str(s.get('title_en', '')).lower() or
                          search.lower() in str(s.get('title_hi', '')).lower() or
                          search.lower() in str(s.get('title_gu', '')).lower()]
            
            st.info(f"📊 Total Schemes: {len(schemes)}")
            
            for scheme in schemes:
                with st.container():
                    st.markdown('<div class="scheme-card">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        # Display based on selected language
                        if language == "Hindi":
                            title = scheme.get('title_hi') or scheme.get('title_en')
                            desc = scheme.get('desc_hi') or scheme.get('desc_en')
                        elif language == "Gujarati":
                            title = scheme.get('title_gu') or scheme.get('title_en')
                            desc = scheme.get('desc_gu') or scheme.get('desc_en')
                        else:
                            title = scheme.get('title_en')
                            desc = scheme.get('desc_en')
                        
                        st.markdown(f"**{title}**")
                        st.markdown(f"{desc[:200]}..." if len(desc) > 200 else desc)
                    
                    with col2:
                        if scheme.get('phone'):
                            st.markdown(f"📞 {scheme['phone']}")
                        if scheme.get('link'):
                            st.markdown(f"[🔗 More Info]({scheme['link']})")
                        
                        status = "🟢 Active" if scheme.get('active') else "🔴 Inactive"
                        st.markdown(f"Status: {status}")
                    
                    with col3:
                        if st.button("✏️ Edit", key=f"edit_{scheme['id']}", use_container_width=True):
                            st.session_state.edit_scheme = scheme
                            st.session_state.show_edit_form = True
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_{scheme['id']}", use_container_width=True):
                            try:
                                supabase.table('govt_schemes').delete().eq('id', scheme['id']).execute()
                                st.success("Scheme deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                        
                        # Toggle active status
                        new_status = not scheme.get('active', True)
                        status_text = "Deactivate" if scheme.get('active') else "Activate"
                        if st.button(f"🔄 {status_text}", key=f"toggle_{scheme['id']}", use_container_width=True):
                            try:
                                supabase.table('govt_schemes').update({'active': new_status}).eq('id', scheme['id']).execute()
                                st.success(f"Scheme {status_text}d!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No schemes found. Add your first scheme!")
    
    except Exception as e:
        st.error(f"Error loading schemes: {e}")

# Edit form (shown when edit button clicked)
if st.session_state.get('show_edit_form'):
    st.markdown("---")
    st.markdown("### ✏️ Edit Scheme")
    
    scheme = st.session_state.edit_scheme
    
    with st.form("edit_scheme_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title_en = st.text_input("Title (English)", value=scheme.get('title_en', ''))
            desc_en = st.text_area("Description (English)", value=scheme.get('desc_en', ''), height=150)
        
        with col2:
            title_hi = st.text_input("Title (Hindi)", value=scheme.get('title_hi', ''))
            desc_hi = st.text_area("Description (Hindi)", value=scheme.get('desc_hi', ''), height=150)
        
        with col3:
            title_gu = st.text_input("Title (Gujarati)", value=scheme.get('title_gu', ''))
            desc_gu = st.text_area("Description (Gujarati)", value=scheme.get('desc_gu', ''), height=150)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            phone = st.text_input("Helpline Phone", value=scheme.get('phone', ''))
        with col2:
            link = st.text_input("Website Link", value=scheme.get('link', ''))
        with col3:
            active = st.checkbox("Active", value=scheme.get('active', True))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Update Scheme", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submit:
            try:
                update_data = {
                    'title_en': title_en,
                    'title_hi': title_hi,
                    'title_gu': title_gu,
                    'desc_en': desc_en,
                    'desc_hi': desc_hi,
                    'desc_gu': desc_gu,
                    'phone': phone,
                    'link': link,
                    'active': active
                }
                supabase.table('govt_schemes').update(update_data).eq('id', scheme['id']).execute()
                st.success("✅ Scheme updated successfully!")
                st.session_state.show_edit_form = False
                st.session_state.edit_scheme = None
                st.rerun()
            except Exception as e:
                st.error(f"Error updating scheme: {e}")
        
        if cancel:
            st.session_state.show_edit_form = False
            st.session_state.edit_scheme = None
            st.rerun()

with tab2:
    st.markdown("#### Add New Government Scheme")
    
    with st.form("add_scheme_form"):
        st.markdown("##### English")
        title_en = st.text_input("Title (English) *", placeholder="e.g., Pradhan Mantri Matru Vandana Yojana")
        desc_en = st.text_area("Description (English) *", placeholder="Enter detailed description...", height=150)
        
        st.markdown("##### Hindi (Optional)")
        title_hi = st.text_input("Title (Hindi)", placeholder="e.g., प्रधानमंत्री मातृ वंदना योजना")
        desc_hi = st.text_area("Description (Hindi)", placeholder="विवरण दर्ज करें...", height=150)
        
        st.markdown("##### Gujarati (Optional)")
        title_gu = st.text_input("Title (Gujarati)", placeholder="e.g., પ્રધાનમંત્રી માતૃ વંદના યોજના")
        desc_gu = st.text_area("Description (Gujarati)", placeholder="વિગતો દાખલ કરો...", height=150)
        
        st.markdown("##### Additional Information")
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Helpline Phone", placeholder="e.g., 104, 1800-XXX-XXXX")
        with col2:
            link = st.text_input("Website Link", placeholder="https://...")
        
        active = st.checkbox("Active", value=True)
        
        submit = st.form_submit_button("➕ Add Scheme", use_container_width=True)
        
        if submit:
            if not title_en or not desc_en:
                st.error("❌ English title and description are required!")
            else:
                try:
                    scheme_data = {
                        'title_en': title_en,
                        'title_hi': title_hi,
                        'title_gu': title_gu,
                        'desc_en': desc_en,
                        'desc_hi': desc_hi,
                        'desc_gu': desc_gu,
                        'phone': phone,
                        'link': link,
                        'active': active
                    }
                    supabase.table('govt_schemes').insert(scheme_data).execute()
                    st.success("✅ Scheme added successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding scheme: {e}")

with tab3:
    st.markdown("#### Scheme Statistics")
    
    try:
        response = supabase.table('govt_schemes').select('*').execute()
        all_schemes = response.data
        
        if all_schemes:
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(all_schemes)
            active = len([s for s in all_schemes if s.get('active')])
            inactive = total - active
            with_phone = len([s for s in all_schemes if s.get('phone')])
            
            with col1:
                st.metric("Total Schemes", total)
            with col2:
                st.metric("🟢 Active", active)
            with col3:
                st.metric("🔴 Inactive", inactive)
            with col4:
                st.metric("📞 With Helpline", with_phone)
            
            # Language coverage
            st.markdown("---")
            st.markdown("#### Language Coverage")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                english = len([s for s in all_schemes if s.get('title_en')])
                st.metric("🇬🇧 English", f"{english}/{total}")
            
            with col2:
                hindi = len([s for s in all_schemes if s.get('title_hi')])
                st.metric("🇮🇳 Hindi", f"{hindi}/{total}")
            
            with col3:
                gujarati = len([s for s in all_schemes if s.get('title_gu')])
                st.metric("🇮🇳 Gujarati", f"{gujarati}/{total}")
            
            # Recent schemes
            st.markdown("---")
            st.markdown("#### Recently Added")
            
            recent = sorted(all_schemes, key=lambda x: x.get('created', ''), reverse=True)[:5]
            for scheme in recent:
                st.markdown(f"- **{scheme.get('title_en')}** - {scheme.get('created', 'N/A')}")
        
        else:
            st.info("No schemes data available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🌿 Government Schemes Management System</p>
    <p>Add, Edit, Delete schemes visible in Telegram bot</p>
</div>
""", unsafe_allow_html=True)

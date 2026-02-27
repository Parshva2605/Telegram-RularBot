# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Issues", page_icon="🆘", layout="wide")

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
    .issue-card-open {
        background: #fff3cd;
        border-left: 5px solid #ff9800;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .issue-card-closed {
        background: #d4edda;
        border-left: 5px solid #28a745;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

st.title("🆘 Issues & Problems")
st.markdown("### User-Reported Issues Management")

# Tabs
tab1, tab2, tab3 = st.tabs(["🔴 Open Issues", "✅ Closed Issues", "📊 Statistics"])

with tab1:
    st.markdown("#### Open Issues")
    
    # Filters
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search = st.text_input("🔍 Search by name or description", "")
    with col2:
        category_filter = st.selectbox("Category", ["All", "User", "Worker"])
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
    
    try:
        response = supabase.table('issues').select('*').eq('status', 'open').execute()
        issues = response.data
        
        if issues:
            # Sort by created (newest first)
            issues = sorted(issues, key=lambda x: x.get('created', ''), reverse=True)
            
            # Filter by search
            if search:
                issues = [i for i in issues if 
                         search.lower() in str(i.get('name', '')).lower() or
                         search.lower() in str(i.get('description', '')).lower()]
            
            # Filter by category
            if category_filter != "All":
                issues = [i for i in issues if i.get('category', '').lower() == category_filter.lower()]
            
            st.warning(f"🔴 {len(issues)} OPEN ISSUES")
            
            for issue in issues:
                with st.container():
                    st.markdown('<div class="issue-card-open">', unsafe_allow_html=True)
                    
                    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                    
                    with col1:
                        st.markdown(f"""
                        **Issue #{issue.get('id')}**  
                        👤 Name: {issue.get('name', 'Unknown')}  
                        🆔 User ID: {issue.get('user_id', 'N/A')}  
                        📱 Username: {issue.get('username', 'N/A')}
                        """)
                    
                    with col2:
                        category = issue.get('category', 'N/A')
                        category_emoji = "👤" if category.lower() == "user" else "👩‍⚕️" if category.lower() == "worker" else "❓"
                        st.markdown(f"""
                        🏷️ **Category:** {category_emoji} {category}  
                        🎂 **Age:** {issue.get('age', 'N/A')}
                        """)
                    
                    with col3:
                        timestamp = issue.get('created', 'N/A')
                        st.markdown(f"""
                        🕐 **Reported:**  
                        {timestamp}
                        """)
                        
                        # Calculate time elapsed
                        try:
                            if timestamp != 'N/A':
                                issue_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                elapsed = datetime.now(issue_time.tzinfo) - issue_time
                                hours = int(elapsed.total_seconds() / 3600)
                                if hours < 24:
                                    st.markdown(f"⏱️ {hours} hours ago")
                                else:
                                    days = hours // 24
                                    st.markdown(f"⏱️ {days} days ago")
                        except:
                            pass
                    
                    with col4:
                        if st.button("✅ Resolve", key=f"resolve_{issue['id']}", use_container_width=True):
                            try:
                                supabase.table('issues').update({'status': 'closed'}).eq('id', issue['id']).execute()
                                st.success("Issue resolved!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    # Description in expandable section
                    with st.expander("📝 View Description"):
                        st.markdown(f"**Problem Description:**")
                        st.write(issue.get('description', 'No description provided'))
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.success("✅ No open issues!")
            st.balloons()
    
    except Exception as e:
        st.error(f"Error loading issues: {e}")

with tab2:
    st.markdown("#### Closed Issues")
    
    try:
        response = supabase.table('issues').select('*').eq('status', 'closed').execute()
        closed = response.data
        
        if closed:
            # Sort by created (newest first)
            closed = sorted(closed, key=lambda x: x.get('created', ''), reverse=True)[:20]
            
            st.info(f"✅ Showing last 20 closed issues")
            
            for issue in closed:
                with st.container():
                    st.markdown('<div class="issue-card-closed">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([2, 2, 2])
                    
                    with col1:
                        st.markdown(f"""
                        **Issue #{issue.get('id')}** ✅  
                        👤 {issue.get('name', 'Unknown')}
                        """)
                    
                    with col2:
                        category = issue.get('category', 'N/A')
                        category_emoji = "👤" if category.lower() == "user" else "👩‍⚕️"
                        st.markdown(f"""
                        🏷️ {category_emoji} {category}  
                        🎂 Age: {issue.get('age', 'N/A')}
                        """)
                    
                    with col3:
                        st.markdown(f"""
                        🕐 {issue.get('created', 'N/A')}
                        """)
                    
                    with st.expander("📝 View Description"):
                        st.write(issue.get('description', 'No description'))
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
        else:
            st.info("No closed issues yet")
    
    except Exception as e:
        st.error(f"Error loading closed issues: {e}")

with tab3:
    st.markdown("#### Issue Statistics")
    
    try:
        response = supabase.table('issues').select('*').execute()
        all_issues = response.data
        
        if all_issues:
            col1, col2, col3, col4 = st.columns(4)
            
            total = len(all_issues)
            open_count = len([i for i in all_issues if i.get('status') == 'open'])
            closed_count = len([i for i in all_issues if i.get('status') == 'closed'])
            
            with col1:
                st.metric("Total Issues", total)
            with col2:
                st.metric("🔴 Open", open_count)
            with col3:
                st.metric("✅ Closed", closed_count)
            with col4:
                resolution_rate = (closed_count / total * 100) if total > 0 else 0
                st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
            
            # Category breakdown
            st.markdown("---")
            st.markdown("#### Issues by Category")
            
            col1, col2 = st.columns(2)
            
            user_issues = len([i for i in all_issues if i.get('category', '').lower() == 'user'])
            worker_issues = len([i for i in all_issues if i.get('category', '').lower() == 'worker'])
            
            with col1:
                st.metric("👤 User Issues", user_issues)
            with col2:
                st.metric("👩‍⚕️ Worker Issues", worker_issues)
            
            # Today's issues
            st.markdown("---")
            today = datetime.now().strftime('%Y-%m-%d')
            today_issues = [i for i in all_issues if today in i.get('created', '')]
            st.metric("📅 Today's Issues", len(today_issues))
            
            # Recent issues
            st.markdown("---")
            st.markdown("#### Recent Issues")
            
            recent = sorted(all_issues, key=lambda x: x.get('created', ''), reverse=True)[:5]
            for issue in recent:
                status_emoji = "🔴" if issue.get('status') == 'open' else "✅"
                category_emoji = "👤" if issue.get('category', '').lower() == 'user' else "👩‍⚕️"
                st.markdown(f"{status_emoji} {category_emoji} **{issue.get('name')}** - {issue.get('created', 'N/A')}")
        
        else:
            st.info("No issues data available")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Auto-refresh
if auto_refresh:
    import time
    time.sleep(30)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🆘 Issues Management System</p>
    <p>Track and resolve user-reported problems</p>
</div>
""", unsafe_allow_html=True)

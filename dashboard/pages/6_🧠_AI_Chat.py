# -*- coding: utf-8 -*-
import streamlit as st
import os
from dotenv import load_dotenv
from supabase_wrapper import create_client
import requests
import json

load_dotenv()

st.set_page_config(page_title="AI Chat", page_icon="🤖", layout="wide")

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
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background-color: #1e40af;
        color: white;
        border-left: 5px solid #1e3a8a;
    }
    .ai-message {
        background-color: #374151;
        color: white;
        border-left: 5px solid #1f2937;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_supabase():
    return create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

supabase = init_supabase()

st.title("🤖 AI Assistant - Sarvam-1")
st.markdown("### Ask Questions About Your Data")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Ollama API configuration
OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "mashriram/sarvam-1"

def query_ollama(prompt, context=""):
    """Query Ollama API with Sarvam-1 model"""
    try:
        full_prompt = f"""You are a helpful AI assistant for MediMind Rural healthcare dashboard.
        
Context: {context}

User Question: {prompt}

Please provide a helpful, accurate answer based on the context provided."""

        payload = {
            "model": MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API, json=payload, timeout=30)
        
        if response.status_code == 200:
            return response.json().get('response', 'No response from AI')
        else:
            return f"Error: API returned status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Cannot connect to Ollama. Please ensure Ollama is running with: `ollama run sarvam-1`"
    except Exception as e:
        return f"Error: {str(e)}"

def get_database_context():
    """Get summary of database for AI context"""
    try:
        context = "MediMind Rural Database Summary:\n\n"
        
        # Emergencies
        emergencies = supabase.table('emergencies').select('*', count='exact').execute()
        context += f"- Total Emergencies: {emergencies.count}\n"
        pending = supabase.table('emergencies').select('*', count='exact').eq('status', 'pending').execute()
        context += f"- Pending Emergencies: {pending.count}\n\n"
        
        # Health Workers
        workers = supabase.table('health_workers').select('*', count='exact').execute()
        context += f"- Total Health Workers: {workers.count}\n"
        approved = supabase.table('health_workers').select('*', count='exact').eq('approved', True).execute()
        context += f"- Approved Workers: {approved.count}\n\n"
        
        # Appointments
        appointments = supabase.table('appointments').select('*', count='exact').execute()
        context += f"- Total Appointments: {appointments.count}\n\n"
        
        # Reminders
        reminders = supabase.table('reminders').select('*', count='exact').eq('active', True).execute()
        context += f"- Active Medicine Reminders: {reminders.count}\n\n"
        
        # Maternal
        maternal = supabase.table('maternal').select('*', count='exact').execute()
        context += f"- Pregnancy Records: {maternal.count}\n"
        
        return context
    except Exception as e:
        return f"Error getting database context: {e}"

# Sidebar with example questions
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    st.markdown("""
    - How many emergencies are pending?
    - What's the status of health workers?
    - How many appointments today?
    - Show me maternal health stats
    - Which medicines are most common?
    - How many ASHA workers approved?
    """)
    
    st.markdown("---")
    st.markdown("### ⚙️ AI Settings")
    
    use_context = st.checkbox("Use Database Context", value=True)
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📊 Database Stats")
    try:
        emergencies = supabase.table('emergencies').select('*', count='exact').execute()
        workers = supabase.table('health_workers').select('*', count='exact').execute()
        appointments = supabase.table('appointments').select('*', count='exact').execute()
        
        st.metric("Emergencies", emergencies.count)
        st.metric("Health Workers", workers.count)
        st.metric("Appointments", appointments.count)
    except:
        pass

# Main chat interface
st.markdown("### 💬 Chat with AI")

# Display chat history
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f'<div class="chat-message user-message">👤 <b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message ai-message">🤖 <b>AI:</b> {message["content"]}</div>', unsafe_allow_html=True)

# Chat input
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input("Ask a question...", key="user_input", label_visibility="collapsed", placeholder="Type your question here...")

with col2:
    send_button = st.button("Send", use_container_width=True)

if send_button and user_input:
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    # Get database context if enabled
    context = get_database_context() if use_context else ""
    
    # Query AI
    with st.spinner("🤖 AI is thinking..."):
        ai_response = query_ollama(user_input, context)
    
    # Add AI response to history
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': ai_response
    })
    
    st.rerun()

# Quick action buttons
st.markdown("---")
st.markdown("### 🚀 Quick Questions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Overall Summary", use_container_width=True):
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "Give me an overall summary of the MediMind Rural system"
        })
        context = get_database_context()
        ai_response = query_ollama("Give me an overall summary of the MediMind Rural system", context)
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        st.rerun()

with col2:
    if st.button("🚨 Emergency Status", use_container_width=True):
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "What's the current emergency situation?"
        })
        context = get_database_context()
        ai_response = query_ollama("What's the current emergency situation?", context)
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        st.rerun()

with col3:
    if st.button("👥 Worker Stats", use_container_width=True):
        st.session_state.chat_history.append({
            'role': 'user',
            'content': "Tell me about health worker statistics"
        })
        context = get_database_context()
        ai_response = query_ollama("Tell me about health worker statistics", context)
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response
        })
        st.rerun()

# Info box
st.markdown("---")
st.info("""
**💡 How to use AI Chat:**
1. Type your question in the input box
2. Click "Send" or press Enter
3. AI will analyze your data and respond
4. Use "Database Context" for data-aware answers

**Note:** Make sure Ollama is running with Sarvam-1 model:
```bash
ollama run sarvam-1
```
""")

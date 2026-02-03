import streamlit as st
import requests
import os

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Book Gen Pipeline", layout="wide")

st.title("📚 Book Generation Pipeline")
st.markdown("Upload content, consolidate it into a Knowledge Base, and chat with your data.")

# --- Sidebar: Upload & Consolidation ---
with st.sidebar:
    st.header("1. Upload Files")
    uploaded_files = st.file_uploader(
        "Upload PDF or other documents", 
        accept_multiple_files=True,
        type=["pdf", "docx", "txt", "md"]
    )
    
    if uploaded_files:
        if st.button("Process Uploaded Files"):
            progress_bar = st.progress(0)
            total_files = len(uploaded_files)
            
            for index, uploaded_file in enumerate(uploaded_files):
                st.write(f"Processing: *{uploaded_file.name}*...")
                
                # Prepare file for upload
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                try:
                    response = requests.post(f"{API_BASE_URL}/extract/", files=files)
                    if response.status_code == 200:
                        st.success(f"✅ Extracted: {uploaded_file.name}")
                    else:
                        st.error(f"❌ Failed: {uploaded_file.name} - {response.text}")
                except Exception as e:
                    st.error(f"❌ Error connecting to server: {e}")
                
                progress_bar.progress((index + 1) / total_files)

    st.divider()
    
    st.header("2. Consolidate Context")
    st.info("Merge all extracted files into a single Base Context.")
    
    if st.button("Generate Base Context"):
        with st.spinner("Consolidating with Gemini... This may take a minute."):
            try:
                response = requests.post(f"{API_BASE_URL}/consolidate/")
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ Consolidation Complete!")
                    st.markdown(f"**Output:** `{data['file']}`")
                else:
                    st.error(f"❌ Failed: {response.text}")
            except Exception as e:
                st.error(f"❌ Connection Error: {e}")

# --- Main Area: Chat ---
st.divider()
st.header("3. Chat with Data")

# --- Session Management (Sidebar) ---
with st.sidebar:
    st.divider()
    st.header("Chat Settings")
    temperature = st.slider("Model Temperature", 0.0, 1.0, 0.7, help="Higher = Creative, Lower = Precise")
    
    st.divider()
    st.header("Chat Sessions")
    
    if st.button("➕ New Chat"):
        try:
            res = requests.post(f"{API_BASE_URL}/sessions/")
            if res.status_code == 200:
                new_id = res.json()["session_id"]
                st.session_state["current_session_id"] = new_id
                st.session_state.messages = [] # Clear local view
                st.rerun()
        except Exception as e:
            st.error(f"Failed to create session: {e}")

    # List recent sessions
    try:
        res = requests.get(f"{API_BASE_URL}/sessions/")
        if res.status_code == 200:
            sessions = res.json()
            for sess in sessions:
                label = f"Session {sess['id'][:8]}... ({sess['message_count']} msgs)"
                if st.button(label, key=sess["id"]):
                    st.session_state["current_session_id"] = sess["id"]
                    st.rerun()
    except Exception:
        st.warning("Could not fetch sessions.")

# --- Chat Interface ---

import json

# Initialize or Load Session
if "current_session_id" not in st.session_state:
    # Try to create one if none exists
    try:
        res = requests.post(f"{API_BASE_URL}/sessions/")
        if res.status_code == 200:
            st.session_state["current_session_id"] = res.json()["session_id"]
    except:
        st.error("Backend not reachable.")

current_id = st.session_state.get("current_session_id")

if current_id:
    st.subheader(f"Current Session: `{current_id}`")
    
    # Load history from backend
    try:
        res = requests.get(f"{API_BASE_URL}/sessions/{current_id}")
        if res.status_code == 200:
            server_messages = res.json().get("messages", [])
            # Sync local state with server state
            st.session_state.messages = server_messages
        else:
            st.error("Failed to load session history.")
    except Exception as e:
        st.error(f"Error loading history: {e}")

    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        # Map 'user'/'assistant' to streamlit roles if needed, usually they match
        with st.chat_message(role):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question about your uploaded documents..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        # Optimistically append to local state (though we re-fetch on rerun usually)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    payload = {"prompt": prompt, "temperature": temperature}
                    response = requests.post(f"{API_BASE_URL}/chat/{current_id}", json=payload)
                    
                    if response.status_code == 200:
                        answer = response.json().get("response", "No response received.")
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        error_msg = f"Error {response.status_code}: {response.text}"
                        st.error(error_msg)
                
                except Exception as e:
                    error_msg = f"Connection Error: {e}"
                    st.error(error_msg)
else:
    st.info("Please create a new chat session to start.")

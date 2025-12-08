import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Flagged Activities')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Admin')}.")

API_URL = "http://web-api:4000/admin/flagged-activities"

@st.cache_data(ttl=60)
def fetch_flagged_activities():
    """Fetch flagged activities from the API"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('flagged_activities', [])
        else:
            st.error(f"Failed to fetch flagged activities. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        return []

def update_flag_status(flag_id, status, resolution_notes=None):
    """Update flag status via API"""
    try:
        update_url = f"{API_URL}/{flag_id}"
        payload = {"status": status}
        if resolution_notes:
            payload["resolution_notes"] = resolution_notes
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Flag {flag_id} updated successfully!")
            st.cache_data.clear()
            return True
        else:
            st.error(f"Failed to update flag. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating flag: {str(e)}")
        return False

def delete_flag(flag_id):
    """Delete a flag via API"""
    try:
        delete_url = f"{API_URL}/{flag_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Flag {flag_id} deleted successfully!")
            st.cache_data.clear()
            return True
        else:
            st.error(f"Failed to delete flag. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting flag: {str(e)}")
        return False

def create_flag(related_type, related_id, reason, status="open"):
    """Create a new flag via API"""
    try:
        payload = {
            "related_type": related_type,
            "related_id": related_id,
            "reason": reason,
            "status": status
        }
        response = requests.post(API_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Flag created successfully!")
            st.cache_data.clear()
            return True
        else:
            st.error(f"Failed to create flag. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error creating flag: {str(e)}")
        return False

flagged = fetch_flagged_activities()

if flagged:
    df = pd.DataFrame(flagged)
    
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    if 'resolved_at' in df.columns:
        df['resolved_at'] = pd.to_datetime(df['resolved_at'], errors='coerce')
    
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_flags = len(df)
        st.metric("Total Flags", total_flags)
    
    with col2:
        open_flags = len(df[df['status'] == 'open']) if 'status' in df.columns else 0
        st.metric("Open", open_flags)
    
    with col3:
        in_review = len(df[df['status'] == 'in-review']) if 'status' in df.columns else 0
        st.metric("In Review", in_review)
    
    with col4:
        resolved = len(df[df['status'] == 'resolved']) if 'status' in df.columns else 0
        st.metric("Resolved", resolved)
    
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if 'related_type' in df.columns:
            types = ['All'] + sorted(df['related_type'].dropna().unique().tolist())
            selected_type = st.selectbox("Filter by Type", types)
        else:
            selected_type = 'All'
    
    with col2:
        if 'status' in df.columns:
            statuses = ['All'] + sorted(df['status'].dropna().unique().tolist())
            selected_status = st.selectbox("Filter by Status", statuses)
        else:
            selected_status = 'All'
    
    filtered_df = df.copy()
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['related_type'] == selected_type]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    st.subheader("Flagged Activities")
    
    for idx, flag in filtered_df.iterrows():
        flag_id = flag.get('flag_id', 'N/A')
        related_type = flag.get('related_type', 'N/A')
        related_id = flag.get('related_id', 'N/A')
        reason = flag.get('reason', 'No reason provided')
        status = flag.get('status', 'N/A')
        created_at = flag.get('created_at', 'N/A')
        if pd.notna(created_at) and isinstance(created_at, pd.Timestamp):
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        status_icon = {'open': '🔴', 'in-review': '🟡', 'resolved': '🟢'}.get(status, '⚪')
        
        with st.expander(f"{status_icon} Flag #{flag_id} - {related_type} #{related_id} ({status})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Reason:** {reason}")
                st.write(f"**Created:** {created_at}")
                if flag.get('resolution_notes'):
                    st.write(f"**Resolution Notes:** {flag.get('resolution_notes')}")
            
            with col2:
                if status != 'resolved':
                    if st.button("Mark In Review", key=f"review_{flag_id}"):
                        update_flag_status(flag_id, 'in-review')
                        st.rerun()
                    
                    if st.button("Resolve", key=f"resolve_{flag_id}"):
                        resolution_notes = st.text_input("Resolution Notes", key=f"notes_{flag_id}")
                        if resolution_notes:
                            update_flag_status(flag_id, 'resolved', resolution_notes)
                            st.rerun()
                    
                    if st.button("Delete", key=f"delete_{flag_id}"):
                        delete_flag(flag_id)
                        st.rerun()
                else:
                    st.info("Flag is resolved")
    
    st.write("---")
    st.subheader("Create New Flag")
    with st.form("create_flag"):
        col1, col2 = st.columns(2)
        with col1:
            flag_type = st.selectbox("Related Type", ["post", "portfolio", "project", "message", "user"])
            flag_id_input = st.number_input("Related ID", min_value=1)
        with col2:
            flag_reason = st.text_area("Reason", height=100)
            flag_status = st.selectbox("Status", ["open", "in-review"])
        
        if st.form_submit_button("Create Flag"):
            if flag_reason:
                create_flag(flag_type, flag_id_input, flag_reason, flag_status)
                st.rerun()
            else:
                st.error("Please provide a reason for the flag")

else:
    st.info("No flagged activities found.")


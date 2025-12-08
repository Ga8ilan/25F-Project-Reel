import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('My Collaborations')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Mike')}.")

COLLABORATIONS_URL = "http://web-api:4000/creator/collaborations"

@st.cache_data(ttl=60)
def fetch_collaborations(user_id=None):
    """Fetch collaborations from the API"""
    try:
        params = {}
        if user_id:
            params['user_id'] = user_id
        response = requests.get(COLLABORATIONS_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('collaborations', [])
        return []
    except:
        return []

def create_collaboration(project_id, user_id, role, verified=False):
    """Create a new collaboration"""
    try:
        payload = {
            "project_id": project_id,
            "user_id": user_id,
            "role": role,
            "verified": verified
        }
        response = requests.post(COLLABORATIONS_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Collaboration added successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_collaboration(credit_id, role=None, verified=None):
    """Update a collaboration"""
    try:
        update_url = f"{COLLABORATIONS_URL}/{credit_id}"
        payload = {}
        if role:
            payload['role'] = role
        if verified is not None:
            payload['verified'] = verified
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Collaboration {credit_id} updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_collaboration(credit_id):
    """Delete a collaboration"""
    try:
        delete_url = f"{COLLABORATIONS_URL}/{credit_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Collaboration {credit_id} deleted successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

user_id = 1  # Demo user ID
collaborations = fetch_collaborations(user_id)

st.write("---")

if collaborations:
    st.subheader("My Collaborations")
    df = pd.DataFrame(collaborations)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        total = len(collaborations)
        st.metric("Total Collaborations", total)
    with col2:
        verified = len([c for c in collaborations if c.get('verified')])
        st.metric("Verified", verified)
    with col3:
        projects = len(set([c.get('project_id') for c in collaborations]))
        st.metric("Projects", projects)
    
    st.write("---")
    
    for collab in collaborations:
        credit_id = collab.get('credit_id', 'N/A')
        project_id = collab.get('project_id', 'N/A')
        role = collab.get('role', 'N/A')
        verified = collab.get('verified', False)
        
        verified_icon = "✅" if verified else "⏳"
        
        with st.expander(f"{verified_icon} Project #{project_id} - Role: {role}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Project ID:** {project_id}")
                st.write(f"**Role:** {role}")
                st.write(f"**Verified:** {verified}")
            with col2:
                if st.button("Edit", key=f"edit_{credit_id}"):
                    st.session_state[f"editing_{credit_id}"] = True
                if st.button("Delete", key=f"delete_{credit_id}"):
                    delete_collaboration(credit_id)
                    st.rerun()
            
            if st.session_state.get(f"editing_{credit_id}", False):
                with st.form(f"edit_form_{credit_id}"):
                    new_role = st.text_input("Role", value=role)
                    new_verified = st.checkbox("Verified", value=verified)
                    
                    if st.form_submit_button("Update Collaboration"):
                        update_collaboration(credit_id, new_role, new_verified)
                        st.session_state[f"editing_{credit_id}"] = False
                        st.rerun()
else:
    st.info("You don't have any collaborations yet. Add one below!")

st.write("---")
st.subheader("Add New Collaboration")
with st.form("create_collaboration_form"):
    collab_project_id = st.number_input("Project ID *", min_value=1)
    collab_user_id = st.number_input("User ID *", min_value=1)
    collab_role = st.text_input("Role *")
    collab_verified = st.checkbox("Verified")
    
    if st.form_submit_button("Add Collaboration", type="primary"):
        if collab_project_id and collab_user_id and collab_role:
            create_collaboration(collab_project_id, collab_user_id, collab_role, collab_verified)
            st.rerun()
        else:
            st.error("Please fill in all required fields")


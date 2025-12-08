import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Manage Projects & Credits')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Mike')}.")

PROJECTS_URL = "http://web-api:4000/creator/projects"
CREDITS_URL = "http://web-api:4000/creator/projects"

@st.cache_data(ttl=60)
def fetch_projects():
    """Fetch projects from the API"""
    try:
        response = requests.get(PROJECTS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('projects', [])
        return []
    except:
        return []

def create_project(portfolio_id, title, description, tags, visibility="public"):
    """Create a new project"""
    try:
        payload = {
            "portfolio_id": portfolio_id,
            "title": title,
            "description": description,
            "tags": tags,
            "visibility": visibility
        }
        response = requests.post(PROJECTS_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success(f"Project '{title}' created successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_project(project_id, title=None, description=None, tags=None, visibility=None):
    """Update a project"""
    try:
        update_url = f"{PROJECTS_URL}/{project_id}"
        payload = {}
        if title:
            payload['title'] = title
        if description:
            payload['description'] = description
        if tags:
            payload['tags'] = tags
        if visibility:
            payload['visibility'] = visibility
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Project {project_id} updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_project(project_id):
    """Archive a project"""
    try:
        delete_url = f"{PROJECTS_URL}/{project_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Project {project_id} archived successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def add_project_credit(project_id, user_id, role, verified=False):
    """Add a credit to a project"""
    try:
        credit_url = f"{PROJECTS_URL}/{project_id}/credits"
        payload = {
            "user_id": user_id,
            "role": role,
            "verified": verified
        }
        response = requests.post(credit_url, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Credit added successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

projects = fetch_projects()

st.write("---")

if projects:
    st.subheader("My Projects")
    for project in projects[:10]:  # Show first 10
        project_id = project.get('project_id', 'N/A')
        title = project.get('title', 'No title')
        description = project.get('description', 'No description')
        tags = project.get('tags', 'No tags')
        
        with st.expander(f"Project #{project_id}: {title}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Description:** {description}")
                st.write(f"**Tags:** {tags}")
            with col2:
                if st.button("Edit", key=f"edit_{project_id}"):
                    st.session_state[f"editing_{project_id}"] = True
                if st.button("Archive", key=f"archive_{project_id}"):
                    delete_project(project_id)
                    st.rerun()
            
            if st.session_state.get(f"editing_{project_id}", False):
                with st.form(f"edit_form_{project_id}"):
                    new_title = st.text_input("Title", value=title)
                    new_desc = st.text_area("Description", value=description, height=100)
                    new_tags = st.text_input("Tags", value=tags)
                    new_visibility = st.selectbox("Visibility", ["public", "private"],
                                                index=0 if project.get('visibility') == 'public' else 1)
                    
                    if st.form_submit_button("Update Project"):
                        update_project(project_id, new_title, new_desc, new_tags, new_visibility)
                        st.session_state[f"editing_{project_id}"] = False
                        st.rerun()
            
            st.write("---")
            st.write("**Add Collaborator Credit:**")
            with st.form(f"add_credit_{project_id}"):
                credit_user_id = st.number_input("User ID", min_value=1, key=f"user_{project_id}")
                credit_role = st.text_input("Role", key=f"role_{project_id}")
                credit_verified = st.checkbox("Verified", key=f"verified_{project_id}")
                
                if st.form_submit_button("Add Credit"):
                    add_project_credit(project_id, credit_user_id, credit_role, credit_verified)
                    st.rerun()
else:
    st.info("You don't have any projects yet. Create one below!")

st.write("---")
st.subheader("Create New Project")
with st.form("create_project_form"):
    portfolio_id = st.number_input("Portfolio ID *", min_value=1, value=1)
    project_title = st.text_input("Project Title *")
    project_description = st.text_area("Description", height=150)
    project_tags = st.text_input("Tags (comma-separated)")
    project_visibility = st.selectbox("Visibility", ["public", "private"])
    
    if st.form_submit_button("Create Project", type="primary"):
        if project_title and portfolio_id:
            create_project(portfolio_id, project_title, project_description, project_tags, project_visibility)
            st.rerun()
        else:
            st.error("Please fill in all required fields")


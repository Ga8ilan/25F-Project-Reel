import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('KPI & Trend Configuration Panel')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Chris')}.")

KPIS_URL = "http://web-api:4000/analytics/kpis"
TREND_TAGS_URL = "http://web-api:4000/analytics/trend-tags"

@st.cache_data(ttl=300)
def fetch_kpis():
    """Fetch KPIs from the API"""
    try:
        response = requests.get(KPIS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('kpis', [])
        return []
    except:
        return []

@st.cache_data(ttl=300)
def fetch_trend_tags():
    """Fetch trend tags from the API"""
    try:
        response = requests.get(TREND_TAGS_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('trend_tags', [])
        return []
    except:
        return []

def create_kpi(kpi_name, formula):
    """Create a new KPI"""
    try:
        response = requests.post(KPIS_URL, json={"kpi_name": kpi_name, "formula": formula}, timeout=5)
        if response.status_code == 201:
            st.success(f"KPI '{kpi_name}' created successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_kpi(kpi_id, kpi_name=None, formula=None, status=None):
    """Update a KPI"""
    try:
        update_url = f"{KPIS_URL}/{kpi_id}"
        payload = {}
        if kpi_name:
            payload['kpi_name'] = kpi_name
        if formula:
            payload['formula'] = formula
        if status:
            payload['status'] = status
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"KPI {kpi_id} updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_kpi(kpi_id):
    """Archive a KPI"""
    try:
        delete_url = f"{KPIS_URL}/{kpi_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"KPI {kpi_id} archived successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def create_trend_tag(tag_name, description):
    """Create a new trend tag"""
    try:
        response = requests.post(TREND_TAGS_URL, json={"tag_name": tag_name, "description": description}, timeout=5)
        if response.status_code == 201:
            st.success(f"Trend tag '{tag_name}' created successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_trend_tag(tag_id, tag_name=None, description=None, status=None):
    """Update a trend tag"""
    try:
        update_url = f"{TREND_TAGS_URL}/{tag_id}"
        payload = {}
        if tag_name:
            payload['tag_name'] = tag_name
        if description is not None:
            payload['description'] = description
        if status:
            payload['status'] = status
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Trend tag {tag_id} updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_trend_tag(tag_id):
    """Archive a trend tag"""
    try:
        delete_url = f"{TREND_TAGS_URL}/{tag_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Trend tag {tag_id} archived successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

tab1, tab2 = st.tabs(["KPI Management", "Trend Tag Management"])

with tab1:
    st.subheader("📊 KPI Management")
    
    kpis = fetch_kpis()
    if kpis:
        st.write("**Existing KPIs:**")
        kpi_df = pd.DataFrame(kpis)
        if not kpi_df.empty:
            display_kpis = kpi_df[['kpi_id', 'kpi_name', 'formula', 'status']]
            display_kpis.columns = ['ID', 'KPI Name', 'Formula', 'Status']
            st.dataframe(display_kpis, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.write("**Edit KPI:**")
            selected_kpi = st.selectbox("Select KPI to Edit", [f"{k['kpi_id']}: {k['kpi_name']}" for k in kpis])
            if selected_kpi:
                kpi_id = int(selected_kpi.split(':')[0])
                selected_kpi_data = next((k for k in kpis if k['kpi_id'] == kpi_id), None)
                
                if selected_kpi_data:
                    with st.form(f"edit_kpi_{kpi_id}"):
                        new_name = st.text_input("KPI Name", value=selected_kpi_data.get('kpi_name', ''))
                        new_formula = st.text_area("Formula", value=selected_kpi_data.get('formula', ''))
                        new_status = st.selectbox("Status", ["active", "archived"], 
                                                 index=0 if selected_kpi_data.get('status') == 'active' else 1)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update KPI"):
                                update_kpi(kpi_id, new_name, new_formula, new_status)
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Archive KPI"):
                                delete_kpi(kpi_id)
                                st.rerun()
        else:
            st.info("No KPIs found")
    else:
        st.info("Unable to fetch KPIs. Please check API connection.")
    
    st.write("---")
    st.write("**Create New KPI:**")
    with st.form("create_kpi_form"):
        kpi_name = st.text_input("KPI Name *")
        kpi_formula = st.text_area("Formula *", placeholder="e.g., total_users / active_users")
        
        if st.form_submit_button("Create KPI", type="primary"):
            if kpi_name and kpi_formula:
                create_kpi(kpi_name, kpi_formula)
                st.rerun()
            else:
                st.error("Please fill in all required fields")

with tab2:
    st.subheader("🏷️ Trend Tag Management")
    
    trend_tags = fetch_trend_tags()
    if trend_tags:
        st.write("**Existing Trend Tags:**")
        sorted_tags = sorted(trend_tags, key=lambda x: x.get('usage_count', 0), reverse=True)
        tag_df = pd.DataFrame(sorted_tags)
        if not tag_df.empty:
            display_tags = tag_df[['tag_id', 'tag_name', 'usage_count', 'status']]
            display_tags.columns = ['ID', 'Tag Name', 'Usage Count', 'Status']
            st.dataframe(display_tags, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.write("**Edit Trend Tag:**")
            selected_tag = st.selectbox("Select Tag to Edit", [f"{t['tag_id']}: {t['tag_name']}" for t in trend_tags])
            if selected_tag:
                tag_id = int(selected_tag.split(':')[0])
                selected_tag_data = next((t for t in trend_tags if t['tag_id'] == tag_id), None)
                
                if selected_tag_data:
                    with st.form(f"edit_tag_{tag_id}"):
                        new_name = st.text_input("Tag Name", value=selected_tag_data.get('tag_name', ''))
                        new_desc = st.text_area("Description", value=selected_tag_data.get('description', ''))
                        new_status = st.selectbox("Status", ["active", "archived"],
                                                  index=0 if selected_tag_data.get('status') == 'active' else 1)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button("Update Tag"):
                                update_trend_tag(tag_id, new_name, new_desc, new_status)
                                st.rerun()
                        with col2:
                            if st.form_submit_button("Archive Tag"):
                                delete_trend_tag(tag_id)
                                st.rerun()
        else:
            st.info("No trend tags found")
    else:
        st.info("Unable to fetch trend tags. Please check API connection.")
    
    st.write("---")
    st.write("**Create New Trend Tag:**")
    with st.form("create_trend_tag_form"):
        tag_name = st.text_input("Tag Name *")
        tag_description = st.text_area("Description", placeholder="Optional description of the trend")
        
        if st.form_submit_button("Create Trend Tag", type="primary"):
            if tag_name:
                create_trend_tag(tag_name, tag_description)
                st.rerun()
            else:
                st.error("Please provide a tag name")


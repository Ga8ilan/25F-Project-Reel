import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests
import pandas as pd

st.set_page_config(layout="wide")

# Display the appropriate sidebar links for the role of the logged in user
SideBarLinks()

st.title("Prediction with Regression")

# API endpoints
KPIS_URL = "http://web-api:4000/analytics/kpis"
TREND_TAGS_URL = "http://web-api:4000/analytics/trend-tags"

# Fetch KPIs and Trend Tags
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
        else:
            error_data = response.json() if response.content else {}
            st.error(f"Failed to create KPI: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error creating KPI: {str(e)}")
        return False

def create_trend_tag(tag_name, description):
    """Create a new trend tag"""
    try:
        response = requests.post(TREND_TAGS_URL, json={"tag_name": tag_name, "description": description}, timeout=5)
        if response.status_code == 201:
            st.success(f"Trend tag '{tag_name}' created successfully!")
            st.cache_data.clear()
            return True
        else:
            error_data = response.json() if response.content else {}
            st.error(f"Failed to create trend tag: {error_data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        st.error(f"Error creating trend tag: {str(e)}")
        return False

# Main content area with tabs
tab1, tab2 = st.tabs(["Prediction", "KPI & Trend Configuration"])

with tab1:
    # create a 2 column layout
    col1, col2 = st.columns(2)

    # add one number input for variable 1 into column 1
    with col1:
        var_01 = st.number_input("Variable 01:", step=1)

    # add another number input for variable 2 into column 2
    with col2:
        var_02 = st.number_input("Variable 02:", step=1)

    logger.info(f"var_01 = {var_01}")
    logger.info(f"var_02 = {var_02}")

    # add a button to use the values entered into the number field to send to the
    # prediction function via the REST API
    if st.button("Calculate Prediction", type="primary", use_container_width=True):
        results = requests.get(f"http://web-api:4000/prediction/{var_01}/{var_02}")
        json_results = results.json()
        st.dataframe(json_results)

with tab2:
    st.subheader("KPI & Trend Configuration Panel")
    
    # Two columns for KPI and Trend Tag configuration
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### 📊 KPI Management")
        
        # Display existing KPIs
        kpis = fetch_kpis()
        if kpis:
            st.write("**Existing KPIs:**")
            kpi_df = pd.DataFrame(kpis)
            if not kpi_df.empty:
                display_kpis = kpi_df[['kpi_id', 'kpi_name', 'formula', 'status']]
                display_kpis.columns = ['ID', 'KPI Name', 'Formula', 'Status']
                st.dataframe(display_kpis, use_container_width=True, hide_index=True)
            else:
                st.info("No KPIs found")
        else:
            st.info("Unable to fetch KPIs. Please check API connection.")
        
        # Create new KPI form
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
    
    with col2:
        st.write("### 🏷️ Trend Tag Management")
        
        # Display existing trend tags
        trend_tags = fetch_trend_tags()
        if trend_tags:
            st.write("**Existing Trend Tags:**")
            # Sort by usage count
            sorted_tags = sorted(trend_tags, key=lambda x: x.get('usage_count', 0), reverse=True)
            tag_df = pd.DataFrame(sorted_tags)
            if not tag_df.empty:
                display_tags = tag_df[['tag_id', 'tag_name', 'usage_count', 'status']].head(10)
                display_tags.columns = ['ID', 'Tag Name', 'Usage Count', 'Status']
                st.dataframe(display_tags, use_container_width=True, hide_index=True)
            else:
                st.info("No trend tags found")
        else:
            st.info("Unable to fetch trend tags. Please check API connection.")
        
        # Create new trend tag form
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

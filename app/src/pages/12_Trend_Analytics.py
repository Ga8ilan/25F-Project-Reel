import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Trend Analytics')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Chris')}.")

TREND_TAGS_URL = "http://web-api:4000/analytics/trend-tags"

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

def update_trend_tag(tag_id, tag_name=None, description=None, status=None):
    """Update a trend tag via API"""
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
    """Archive a trend tag via API"""
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

trend_tags = fetch_trend_tags()

if trend_tags:
    df = pd.DataFrame(trend_tags)
    
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_tags = len(df)
        st.metric("Total Trend Tags", total_tags)
    
    with col2:
        if 'usage_count' in df.columns:
            total_usage = df['usage_count'].sum()
            st.metric("Total Usage Count", total_usage)
    
    with col3:
        active_tags = len(df[df['status'] == 'active']) if 'status' in df.columns else 0
        st.metric("Active Tags", active_tags)
    
    st.write("---")
    
    # Sort by usage count
    sorted_tags = sorted(trend_tags, key=lambda x: x.get('usage_count', 0), reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Trending Tags by Usage")
        top_10 = sorted_tags[:10]
        if top_10:
            tag_df = pd.DataFrame(top_10)
            fig = px.bar(tag_df, x='tag_name', y='usage_count',
                        title="Top 10 Trending Tags",
                        labels={'tag_name': 'Tag Name', 'usage_count': 'Usage Count'},
                        color='usage_count',
                        color_continuous_scale='Blues')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Trend Tag Status Distribution")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            fig = px.pie(values=status_counts.values, names=status_counts.index,
                        title="Tag Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    st.subheader("All Trend Tags")
    
    for tag in sorted_tags:
        tag_id = tag.get('tag_id', 'N/A')
        tag_name = tag.get('tag_name', 'N/A')
        usage_count = tag.get('usage_count', 0)
        description = tag.get('description', 'No description')
        status = tag.get('status', 'N/A')
        
        with st.expander(f"{tag_name} (Usage: {usage_count}, Status: {status})"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Description:** {description}")
                st.write(f"**Usage Count:** {usage_count}")
            with col2:
                if status != 'archived':
                    if st.button("Archive", key=f"archive_{tag_id}"):
                        update_trend_tag(tag_id, status='archived')
                        st.rerun()
                
                with st.form(key=f"edit_{tag_id}"):
                    new_name = st.text_input("Tag Name", value=tag_name)
                    new_desc = st.text_area("Description", value=description)
                    if st.form_submit_button("Update"):
                        update_trend_tag(tag_id, new_name, new_desc)
                        st.rerun()

else:
    st.info("No trend tags found. Please check the API connection.")


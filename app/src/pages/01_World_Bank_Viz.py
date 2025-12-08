import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import requests
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# Set the header of the page
st.title('User Onboarding Statistics')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Admin')}.")

# API endpoint for users
API_URL = "http://web-api:4000/creator/users"

# Fetch user data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_users():
    """Fetch user data from the API"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('users', [])
        else:
            st.error(f"Failed to fetch user data. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")
        return []

users = fetch_users()

if users:
    # Convert to DataFrame
    df = pd.DataFrame(users)
    
    # Convert created_at to datetime if it exists
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
        df['signup_date'] = df['created_at'].dt.date
        df['signup_month'] = df['created_at'].dt.to_period('M')
    
    # Key Metrics Row
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(df)
        st.metric("Total Users", total_users)
    
    with col2:
        active_users = df['is_active'].sum() if 'is_active' in df.columns else 0
        st.metric("Active Users", active_users)
    
    with col3:
        creators = df['is_creator'].sum() if 'is_creator' in df.columns else 0
        st.metric("Creators", creators)
    
    with col4:
        if 'created_at' in df.columns and df['created_at'].notna().any():
            new_users_30d = len(df[df['created_at'] >= datetime.now() - timedelta(days=30)])
            st.metric("New Users (30 days)", new_users_30d)
        else:
            st.metric("New Users (30 days)", "N/A")
    
    st.write("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Users by Role")
        if 'role' in df.columns:
            role_counts = df['role'].value_counts()
            fig_role = px.pie(
                values=role_counts.values,
                names=role_counts.index,
                title="User Distribution by Role"
            )
            st.plotly_chart(fig_role, use_container_width=True)
        else:
            st.info("Role data not available")
    
    with col2:
        st.subheader("Active vs Inactive Users")
        if 'is_active' in df.columns:
            active_counts = df['is_active'].value_counts()
            labels = ['Active' if idx else 'Inactive' for idx in active_counts.index]
            fig_active = px.pie(
                values=active_counts.values,
                names=labels,
                title="User Status Distribution"
            )
            st.plotly_chart(fig_active, use_container_width=True)
        else:
            st.info("Active status data not available")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("New Users Over Time")
        if 'created_at' in df.columns and df['created_at'].notna().any():
            # Group by month
            monthly_signups = df.groupby('signup_month').size().reset_index(name='count')
            monthly_signups['signup_month'] = monthly_signups['signup_month'].astype(str)
            
            fig_timeline = px.line(
                monthly_signups,
                x='signup_month',
                y='count',
                title="Monthly User Signups",
                labels={'signup_month': 'Month', 'count': 'Number of Users'}
            )
            fig_timeline.update_xaxes(tickangle=45)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Signup date data not available")
    
    with col2:
        st.subheader("Users by Market")
        if 'market' in df.columns:
            market_counts = df['market'].value_counts().head(10)
            fig_market = px.bar(
                x=market_counts.index,
                y=market_counts.values,
                title="Top 10 Markets by User Count",
                labels={'x': 'Market', 'y': 'Number of Users'}
            )
            fig_market.update_xaxes(tickangle=45)
            st.plotly_chart(fig_market, use_container_width=True)
        else:
            st.info("Market data not available")
    
    # Charts Row 3
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Creators vs Non-Creators")
        if 'is_creator' in df.columns:
            creator_counts = df['is_creator'].value_counts()
            labels = ['Creator' if idx else 'Non-Creator' for idx in creator_counts.index]
            fig_creator = px.pie(
                values=creator_counts.values,
                names=labels,
                title="Creator Status Distribution"
            )
            st.plotly_chart(fig_creator, use_container_width=True)
        else:
            st.info("Creator data not available")
    
    with col2:
        st.subheader("Users by Location")
        if 'location' in df.columns:
            location_counts = df['location'].value_counts().head(10)
            fig_location = px.bar(
                x=location_counts.index,
                y=location_counts.values,
                title="Top 10 Locations by User Count",
                labels={'x': 'Location', 'y': 'Number of Users'}
            )
            fig_location.update_xaxes(tickangle=45)
            st.plotly_chart(fig_location, use_container_width=True)
        else:
            st.info("Location data not available")
    
    st.write("---")
    
    # Recent Signups Table
    st.subheader("Recent User Signups")
    if 'created_at' in df.columns and df['created_at'].notna().any():
        recent_users = df.nlargest(20, 'created_at')[['name', 'email', 'role', 'location', 'is_creator', 'is_active', 'created_at']]
        recent_users['created_at'] = recent_users['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        recent_users.columns = ['Name', 'Email', 'Role', 'Location', 'Is Creator', 'Is Active', 'Signup Date']
        st.dataframe(recent_users, use_container_width=True, hide_index=True)
    else:
        st.info("Signup date data not available for recent signups table")
    
    # Full User Data (Expandable)
    with st.expander("View All User Data"):
        display_df = df[['user_id', 'name', 'email', 'role', 'location', 'market', 'is_creator', 'is_active', 'created_at']].copy()
        if 'created_at' in display_df.columns:
            display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['User ID', 'Name', 'Email', 'Role', 'Location', 'Market', 'Is Creator', 'Is Active', 'Signup Date']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("No user data available. Please check the API connection.")

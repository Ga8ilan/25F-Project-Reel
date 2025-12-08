import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

# Set up the page
st.title('System Alerts')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Admin')}.")

# API endpoint for alerts
API_URL = "http://web-api:4000/admin/alerts"

# Fetch alerts data
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_alerts():
    """Fetch alerts data from the API"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('alerts', [])
        else:
            st.error(f"Failed to fetch alerts. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")
        return []

def update_alert_status(alert_id, status, admin_notes=None):
    """Update alert status via API"""
    try:
        update_url = f"{API_URL}/{alert_id}"
        payload = {"status": status}
        if admin_notes:
            payload["admin_notes"] = admin_notes
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Alert {alert_id} updated successfully!")
            st.cache_data.clear()  # Clear cache to refresh data
            return True
        else:
            st.error(f"Failed to update alert. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating alert: {str(e)}")
        return False

alerts = fetch_alerts()

if alerts:
    # Convert to DataFrame
    df = pd.DataFrame(alerts)
    
    # Convert created_at and resolved_at to datetime if they exist
    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    if 'resolved_at' in df.columns:
        df['resolved_at'] = pd.to_datetime(df['resolved_at'], errors='coerce')
    
    # Key Metrics Row
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alerts = len(df)
        st.metric("Total Alerts", total_alerts)
    
    with col2:
        open_alerts = len(df[df['status'] == 'open']) if 'status' in df.columns else 0
        st.metric("Open Alerts", open_alerts, delta=None)
    
    with col3:
        acknowledged_alerts = len(df[df['status'] == 'acknowledged']) if 'status' in df.columns else 0
        st.metric("Acknowledged", acknowledged_alerts)
    
    with col4:
        resolved_alerts = len(df[df['status'] == 'resolved']) if 'status' in df.columns else 0
        st.metric("Resolved", resolved_alerts)
    
    st.write("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'alert_type' in df.columns:
            alert_types = ['All'] + sorted(df['alert_type'].dropna().unique().tolist())
            selected_type = st.selectbox("Filter by Alert Type", alert_types)
        else:
            selected_type = 'All'
    
    with col2:
        if 'status' in df.columns:
            statuses = ['All'] + sorted(df['status'].dropna().unique().tolist())
            selected_status = st.selectbox("Filter by Status", statuses)
        else:
            selected_status = 'All'
    
    with col3:
        show_resolved = st.checkbox("Include Resolved Alerts", value=True)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['alert_type'] == selected_type]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if not show_resolved:
        filtered_df = filtered_df[filtered_df['status'] != 'resolved']
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Alerts by Type")
        if 'alert_type' in filtered_df.columns:
            type_counts = filtered_df['alert_type'].value_counts()
            fig_type = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Alert Distribution by Type"
            )
            st.plotly_chart(fig_type, use_container_width=True)
        else:
            st.info("Alert type data not available")
    
    with col2:
        st.subheader("Alerts by Status")
        if 'status' in filtered_df.columns:
            status_counts = filtered_df['status'].value_counts()
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title="Alert Distribution by Status",
                labels={'x': 'Status', 'y': 'Number of Alerts'},
                color=status_counts.index,
                color_discrete_map={
                    'open': '#FF6B6B',
                    'acknowledged': '#FFD93D',
                    'resolved': '#6BCF7F'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Status data not available")
    
    # Timeline chart
    if 'created_at' in filtered_df.columns and filtered_df['created_at'].notna().any():
        st.subheader("Alerts Over Time")
        filtered_df['date'] = filtered_df['created_at'].dt.date
        daily_alerts = filtered_df.groupby('date').size().reset_index(name='count')
        daily_alerts = daily_alerts.sort_values('date')
        
        fig_timeline = px.line(
            daily_alerts,
            x='date',
            y='count',
            title="Daily Alert Count",
            labels={'date': 'Date', 'count': 'Number of Alerts'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    st.write("---")
    
    # Alerts Table
    st.subheader("Alert Details")
    
    # Display alerts in expandable sections
    for idx, alert in filtered_df.iterrows():
        alert_id = alert.get('alert_id', 'N/A')
        alert_type = alert.get('alert_type', 'N/A')
        status = alert.get('status', 'N/A')
        message = alert.get('message', 'No message')
        created_at = alert.get('created_at', 'N/A')
        if pd.notna(created_at) and isinstance(created_at, pd.Timestamp):
            created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Color code by status
        status_color = {
            'open': '🔴',
            'acknowledged': '🟡',
            'resolved': '🟢'
        }
        status_icon = status_color.get(status, '⚪')
        
        with st.expander(f"{status_icon} Alert #{alert_id} - {alert_type} ({status})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Message:** {message}")
                st.write(f"**Created:** {created_at}")
                
                if pd.notna(alert.get('resolved_at')):
                    resolved_at = alert['resolved_at']
                    if isinstance(resolved_at, pd.Timestamp):
                        resolved_at = resolved_at.strftime('%Y-%m-%d %H:%M:%S')
                    st.write(f"**Resolved:** {resolved_at}")
                
                if alert.get('related_type'):
                    st.write(f"**Related Type:** {alert.get('related_type')}")
                    if alert.get('related_id'):
                        st.write(f"**Related ID:** {alert.get('related_id')}")
                
                if alert.get('admin_notes'):
                    st.write(f"**Admin Notes:** {alert.get('admin_notes')}")
            
            with col2:
                if status != 'resolved':
                    st.write("**Update Status:**")
                    
                    if status == 'open':
                        if st.button("Acknowledge", key=f"ack_{alert_id}"):
                            update_alert_status(alert_id, 'acknowledged')
                            st.rerun()
                    
                    if status in ['open', 'acknowledged']:
                        if st.button("Resolve", key=f"resolve_{alert_id}"):
                            update_alert_status(alert_id, 'resolved')
                            st.rerun()
                    
                    # Add notes
                    with st.form(key=f"notes_{alert_id}"):
                        notes = st.text_area("Admin Notes", value=alert.get('admin_notes', ''))
                        if st.form_submit_button("Update Notes"):
                            update_alert_status(alert_id, status, notes)
                            st.rerun()
                else:
                    st.info("Alert is resolved")
    
    # Summary table
    with st.expander("View All Alerts (Table Format)"):
        display_df = filtered_df[['alert_id', 'alert_type', 'status', 'message', 'created_at', 'resolved_at']].copy()
        if 'created_at' in display_df.columns:
            display_df['created_at'] = display_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'resolved_at' in display_df.columns:
            display_df['resolved_at'] = display_df['resolved_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['Alert ID', 'Type', 'Status', 'Message', 'Created At', 'Resolved At']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("No alerts available. The system is running smoothly!")
    st.info("If you expected to see alerts, please check the API connection.")

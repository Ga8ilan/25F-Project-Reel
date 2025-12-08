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

# Set up the page
st.title('Pending Approvals')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Admin')}.")

# API endpoint for applications
API_URL = "http://web-api:4000/admin/applications"

# Fetch applications data
@st.cache_data(ttl=60)  # Cache for 1 minute
def fetch_applications(status_filter=None):
    """Fetch applications data from the API"""
    try:
        params = {}
        if status_filter:
            params['status'] = status_filter
        
        response = requests.get(API_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('applications', [])
        else:
            st.error(f"Failed to fetch applications. Status code: {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")
        st.info("Please ensure the API server is running on http://web-api:4000")
        return []

def update_application_status(application_id, status, admin_notes=None):
    """Update application status via API"""
    try:
        update_url = f"{API_URL}/{application_id}"
        payload = {"status": status}
        if admin_notes:
            payload["admin_notes"] = admin_notes
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Application {application_id} updated successfully!")
            st.cache_data.clear()  # Clear cache to refresh data
            return True
        else:
            error_data = response.json() if response.content else {}
            error_msg = error_data.get('error', f"Status code: {response.status_code}")
            st.error(f"Failed to update application: {error_msg}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error updating application: {str(e)}")
        return False

# Fetch all applications for metrics
all_applications = fetch_applications()

if all_applications:
    # Convert to DataFrame
    df = pd.DataFrame(all_applications)
    
    # Convert timestamps to datetime if they exist
    if 'submitted_at' in df.columns:
        df['submitted_at'] = pd.to_datetime(df['submitted_at'], errors='coerce')
    if 'last_updated_at' in df.columns:
        df['last_updated_at'] = pd.to_datetime(df['last_updated_at'], errors='coerce')
    
    # Key Metrics Row
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_apps = len(df)
        st.metric("Total Applications", total_apps)
    
    with col2:
        pending_count = len(df[df['status'] == 'pending']) if 'status' in df.columns else 0
        st.metric("Pending", pending_count, delta=None)
    
    with col3:
        approved_count = len(df[df['status'] == 'approved']) if 'status' in df.columns else 0
        st.metric("Approved", approved_count)
    
    with col4:
        rejected_count = len(df[df['status'] == 'rejected']) if 'status' in df.columns else 0
        needs_info_count = len(df[df['status'] == 'needs-info']) if 'status' in df.columns else 0
        other_count = rejected_count + needs_info_count
        st.metric("Other", other_count)
    
    st.write("---")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        if 'status' in df.columns:
            statuses = ['All', 'pending', 'approved', 'rejected', 'needs-info']
            selected_status = st.selectbox("Filter by Status", statuses)
        else:
            selected_status = 'All'
    
    with col2:
        show_pending_only = st.checkbox("Show Pending Only", value=True)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if show_pending_only and selected_status == 'All':
        filtered_df = filtered_df[filtered_df['status'] == 'pending']
    
    # Sort by submitted date (newest first)
    if 'submitted_at' in filtered_df.columns:
        filtered_df = filtered_df.sort_values('submitted_at', ascending=False)
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Applications by Status")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            fig_status = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Application Status Distribution",
                color_discrete_map={
                    'pending': '#FFD93D',
                    'approved': '#6BCF7F',
                    'rejected': '#FF6B6B',
                    'needs-info': '#4D96FF'
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("Status data not available")
    
    with col2:
        st.subheader("Applications Over Time")
        if 'submitted_at' in df.columns and df['submitted_at'].notna().any():
            df['date'] = df['submitted_at'].dt.date
            daily_apps = df.groupby('date').size().reset_index(name='count')
            daily_apps = daily_apps.sort_values('date')
            
            fig_timeline = px.line(
                daily_apps,
                x='date',
                y='count',
                title="Daily Application Submissions",
                labels={'date': 'Date', 'count': 'Number of Applications'}
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Submission date data not available")
    
    st.write("---")
    
    # Pending Applications Section (highlighted)
    if show_pending_only or selected_status == 'pending' or (selected_status == 'All' and len(filtered_df[filtered_df['status'] == 'pending']) > 0):
        pending_df = filtered_df[filtered_df['status'] == 'pending'] if selected_status == 'All' else filtered_df
        if len(pending_df) > 0:
            st.subheader(f"🔴 Pending Applications ({len(pending_df)})")
            
            for idx, app in pending_df.iterrows():
                app_id = app.get('application_id', 'N/A')
                applicant_name = app.get('applicant_name', 'N/A')
                email = app.get('email', 'N/A')
                portfolio_url = app.get('portfolio_url', '')
                submitted_at = app.get('submitted_at', 'N/A')
                if pd.notna(submitted_at) and isinstance(submitted_at, pd.Timestamp):
                    submitted_at = submitted_at.strftime('%Y-%m-%d %H:%M:%S')
                admin_notes = app.get('admin_notes', '')
                
                with st.expander(f"Application #{app_id} - {applicant_name}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Applicant Name:** {applicant_name}")
                        st.write(f"**Email:** {email}")
                        st.write(f"**Submitted:** {submitted_at}")
                        
                        if portfolio_url:
                            st.write(f"**Portfolio URL:** [{portfolio_url}]({portfolio_url})")
                        else:
                            st.write("**Portfolio URL:** Not provided")
                        
                        if admin_notes:
                            st.write(f"**Admin Notes:** {admin_notes}")
                    
                    with col2:
                        st.write("**Actions:**")
                        
                        # Approve button
                        if st.button("✅ Approve", key=f"approve_{app_id}", type="primary"):
                            if update_application_status(app_id, 'approved'):
                                st.rerun()
                        
                        # Reject button
                        if st.button("❌ Reject", key=f"reject_{app_id}"):
                            if update_application_status(app_id, 'rejected'):
                                st.rerun()
                        
                        # Needs Info button
                        if st.button("ℹ️ Needs Info", key=f"needs_info_{app_id}"):
                            if update_application_status(app_id, 'needs-info'):
                                st.rerun()
                        
                        # Add/Update Notes
                        with st.form(key=f"notes_{app_id}"):
                            notes = st.text_area("Admin Notes", value=admin_notes, height=100)
                            if st.form_submit_button("Update Notes"):
                                update_application_status(app_id, 'pending', notes)
                                st.rerun()
    
    st.write("---")
    
    # All Applications Section
    st.subheader("All Applications")
    
    # Display all filtered applications
    for idx, app in filtered_df.iterrows():
        app_id = app.get('application_id', 'N/A')
        applicant_name = app.get('applicant_name', 'N/A')
        email = app.get('email', 'N/A')
        status = app.get('status', 'N/A')
        portfolio_url = app.get('portfolio_url', '')
        submitted_at = app.get('submitted_at', 'N/A')
        if pd.notna(submitted_at) and isinstance(submitted_at, pd.Timestamp):
            submitted_at = submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        last_updated = app.get('last_updated_at', 'N/A')
        if pd.notna(last_updated) and isinstance(last_updated, pd.Timestamp):
            last_updated = last_updated.strftime('%Y-%m-%d %H:%M:%S')
        admin_notes = app.get('admin_notes', '')
        
        # Status color coding
        status_colors = {
            'pending': '🟡',
            'approved': '🟢',
            'rejected': '🔴',
            'needs-info': '🔵'
        }
        status_icon = status_colors.get(status, '⚪')
        
        with st.expander(f"{status_icon} Application #{app_id} - {applicant_name} ({status})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Applicant Name:** {applicant_name}")
                st.write(f"**Email:** {email}")
                st.write(f"**Status:** {status}")
                st.write(f"**Submitted:** {submitted_at}")
                st.write(f"**Last Updated:** {last_updated}")
                
                if portfolio_url:
                    st.write(f"**Portfolio URL:** [{portfolio_url}]({portfolio_url})")
                else:
                    st.write("**Portfolio URL:** Not provided")
                
                if admin_notes:
                    st.write(f"**Admin Notes:** {admin_notes}")
            
            with col2:
                st.write("**Update Status:**")
                
                status_options = ['pending', 'approved', 'rejected', 'needs-info']
                current_status_idx = status_options.index(status) if status in status_options else 0
                new_status = st.selectbox(
                    "Change Status",
                    status_options,
                    index=current_status_idx,
                    key=f"status_{app_id}"
                )
                
                if st.button("Update Status", key=f"update_{app_id}"):
                    if update_application_status(app_id, new_status):
                        st.rerun()
                
                # Add/Update Notes
                with st.form(key=f"notes_all_{app_id}"):
                    notes = st.text_area("Admin Notes", value=admin_notes, height=100, key=f"notes_text_{app_id}")
                    if st.form_submit_button("Update Notes"):
                        update_application_status(app_id, status, notes)
                        st.rerun()
    
    # Summary table
    with st.expander("View All Applications (Table Format)"):
        display_df = filtered_df[['application_id', 'applicant_name', 'email', 'status', 'submitted_at', 'last_updated_at']].copy()
        if 'submitted_at' in display_df.columns:
            display_df['submitted_at'] = display_df['submitted_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        if 'last_updated_at' in display_df.columns:
            display_df['last_updated_at'] = display_df['last_updated_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['Application ID', 'Applicant Name', 'Email', 'Status', 'Submitted At', 'Last Updated']
        st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    st.warning("No applications available.")
    st.info("If you expected to see applications, please check the API connection.")
    
    # Option to create a test application
    with st.expander("Create Test Application"):
        with st.form("create_test_app"):
            name = st.text_input("Applicant Name")
            email = st.text_input("Email")
            portfolio = st.text_input("Portfolio URL (optional)")
            
            if st.form_submit_button("Create Test Application"):
                st.info("Note: This would require a POST endpoint to /admin/applications. Check API documentation for implementation.")


import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

# Initialize sidebar
SideBarLinks()

st.title("NGO Directory")

# API endpoints
API_URL = "http://web-api:4000/ngo/ngos"
TREND_TAGS_URL = "http://web-api:4000/analytics/trend-tags"

# Fetch trend tags
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

# Create filter columns
col1, col2, col3 = st.columns(3)

# Get unique values for filters from the API
try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        ngos = response.json()

        # Extract unique values for filters
        countries = sorted(list(set(ngo["Country"] for ngo in ngos)))
        focus_areas = sorted(list(set(ngo["Focus_Area"] for ngo in ngos)))
        founding_years = sorted(list(set(ngo["Founding_Year"] for ngo in ngos)))

        # Create filters
        with col1:
            selected_country = st.selectbox("Filter by Country", ["All"] + countries)

        with col2:
            selected_focus = st.selectbox("Filter by Focus Area", ["All"] + focus_areas)

        with col3:
            selected_year = st.selectbox(
                "Filter by Founding Year",
                ["All"] + [str(year) for year in founding_years],
            )

        # Build query parameters
        params = {}
        if selected_country != "All":
            params["country"] = selected_country
        if selected_focus != "All":
            params["focus_area"] = selected_focus
        if selected_year != "All":
            params["founding_year"] = selected_year

        # Get filtered data
        filtered_response = requests.get(API_URL, params=params)
        if filtered_response.status_code == 200:
            filtered_ngos = filtered_response.json()

            # Display results count
            st.write(f"Found {len(filtered_ngos)} NGOs")
            
            # Trend Analytics Section
            st.write("---")
            st.subheader("📊 Trend Analytics")
            
            trend_tags = fetch_trend_tags()
            if trend_tags:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Top Trending Tags**")
                    # Sort by usage count and get top 10
                    sorted_tags = sorted(trend_tags, key=lambda x: x.get('usage_count', 0), reverse=True)[:10]
                    tag_df = pd.DataFrame(sorted_tags)
                    
                    if not tag_df.empty and 'usage_count' in tag_df.columns:
                        fig_tags = px.bar(
                            tag_df,
                            x='tag_name',
                            y='usage_count',
                            title="Top 10 Trending Tags by Usage",
                            labels={'tag_name': 'Tag Name', 'usage_count': 'Usage Count'},
                            color='usage_count',
                            color_continuous_scale='Blues'
                        )
                        fig_tags.update_xaxes(tickangle=45)
                        st.plotly_chart(fig_tags, use_container_width=True)
                    else:
                        st.info("No trend tag data available")
                
                with col2:
                    st.write("**Trend Tag Details**")
                    # Display trend tags in a table
                    if not tag_df.empty:
                        display_tags = tag_df[['tag_name', 'usage_count', 'description']].head(10)
                        display_tags.columns = ['Tag Name', 'Usage Count', 'Description']
                        st.dataframe(display_tags, use_container_width=True, hide_index=True)
                    else:
                        st.info("No trend tags available")
            else:
                st.info("Trend analytics data is currently unavailable. Please check API connection.")
            
            st.write("---")

            # Create expandable rows for each NGO
            for ngo in filtered_ngos:
                with st.expander(f"{ngo['Name']} ({ngo['Country']})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write("**Basic Information**")
                        st.write(f"**Country:** {ngo['Country']}")
                        st.write(f"**Founded:** {ngo['Founding_Year']}")
                        st.write(f"**Focus Area:** {ngo['Focus_Area']}")

                    with col2:
                        st.write("**Contact Information**")
                        st.write(f"**Website:** [{ngo['Website']}]({ngo['Website']})")

                    # Add a button to view full profile
                    if st.button(f"View Full Profile", key=f"view_{ngo['NGO_ID']}"):
                        st.session_state["selected_ngo_id"] = ngo["NGO_ID"]
                        st.switch_page("pages/16_NGO_Profile.py")

    else:
        st.error("Failed to fetch NGO data from the API")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running on http://web-api:4000")

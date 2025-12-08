import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Rising Creators Dashboard')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Chris')}.")

API_URL = "http://web-api:4000/creator/creators"

@st.cache_data(ttl=300)
def fetch_creators():
    """Fetch creators from the API"""
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('creators', [])
        return []
    except:
        return []

creators = fetch_creators()

if creators:
    df = pd.DataFrame(creators)
    
    st.write("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_creators = len(df)
        st.metric("Total Creators", total_creators)
    
    with col2:
        if 'credit_momentum' in df.columns:
            avg_momentum = df['credit_momentum'].mean()
            st.metric("Avg Credit Momentum", f"{avg_momentum:.1f}")
    
    with col3:
        if 'market' in df.columns:
            top_market = df['market'].mode()[0] if not df['market'].empty else 'N/A'
            st.metric("Top Market", top_market)
    
    st.write("---")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'market' in df.columns:
            markets = ['All'] + sorted(df['market'].dropna().unique().tolist())
            selected_market = st.selectbox("Filter by Market", markets)
        else:
            selected_market = 'All'
    
    with col2:
        if 'primary_styles' in df.columns:
            all_styles = set()
            for styles in df['primary_styles'].dropna():
                if styles:
                    all_styles.update([s.strip() for s in str(styles).split(',')])
            styles_list = ['All'] + sorted(list(all_styles))
            selected_style = st.selectbox("Filter by Style", styles_list)
        else:
            selected_style = 'All'
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Credit Momentum (High to Low)", "Credit Momentum (Low to High)", "Name"])
    
    # Apply filters
    filtered_df = df.copy()
    if selected_market != 'All':
        filtered_df = filtered_df[filtered_df['market'] == selected_market]
    if selected_style != 'All':
        filtered_df = filtered_df[filtered_df['primary_styles'].str.contains(selected_style, na=False)]
    
    # Sort
    if sort_by == "Credit Momentum (High to Low)":
        filtered_df = filtered_df.sort_values('credit_momentum', ascending=False)
    elif sort_by == "Credit Momentum (Low to High)":
        filtered_df = filtered_df.sort_values('credit_momentum', ascending=True)
    else:
        filtered_df = filtered_df.sort_values('name', ascending=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Creators by Credit Momentum")
        top_10 = filtered_df.head(10)
        if not top_10.empty and 'credit_momentum' in top_10.columns:
            fig = px.bar(top_10, x='name', y='credit_momentum',
                        title="Top 10 Creators by Momentum",
                        labels={'name': 'Creator', 'credit_momentum': 'Credit Momentum'},
                        color='credit_momentum',
                        color_continuous_scale='Viridis')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Creators by Market")
        if 'market' in filtered_df.columns:
            market_counts = filtered_df['market'].value_counts()
            fig = px.pie(values=market_counts.values, names=market_counts.index,
                        title="Distribution by Market")
            st.plotly_chart(fig, use_container_width=True)
    
    st.write("---")
    st.subheader("Rising Creators List")
    
    for idx, creator in filtered_df.head(20).iterrows():
        with st.expander(f"{creator.get('name', 'N/A')} - Momentum: {creator.get('credit_momentum', 0)}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Email:** {creator.get('email', 'N/A')}")
                st.write(f"**Location:** {creator.get('location', 'N/A')}")
                st.write(f"**Market:** {creator.get('market', 'N/A')}")
            with col2:
                st.write(f"**Styles:** {creator.get('primary_styles', 'N/A')}")
                st.write(f"**Tools:** {creator.get('tools', 'N/A')}")
                st.write(f"**Headline:** {creator.get('headline', 'N/A')}")

else:
    st.info("No creators found. Please check the API connection.")


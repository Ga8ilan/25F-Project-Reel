import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Manage My Portfolio')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Mike')}.")

PORTFOLIOS_URL = "http://web-api:4000/creator/portfolios"
USERS_URL = "http://web-api:4000/creator/users"

@st.cache_data(ttl=60)
def fetch_portfolios(user_id=None):
    """Fetch portfolios from the API"""
    try:
        params = {}
        if user_id:
            params['user_id'] = user_id
        response = requests.get(PORTFOLIOS_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('portfolios', [])
        return []
    except:
        return []

def create_portfolio(user_id, headline, bio):
    """Create a new portfolio"""
    try:
        payload = {
            "user_id": user_id,
            "headline": headline,
            "bio": bio
        }
        response = requests.post(PORTFOLIOS_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Portfolio created successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_portfolio(portfolio_id, headline=None, bio=None, featured_projects=None):
    """Update a portfolio"""
    try:
        update_url = f"{PORTFOLIOS_URL}/{portfolio_id}"
        payload = {}
        if headline:
            payload['headline'] = headline
        if bio:
            payload['bio'] = bio
        if featured_projects:
            payload['featured_projects'] = featured_projects
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success(f"Portfolio {portfolio_id} updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_portfolio(portfolio_id):
    """Archive a portfolio"""
    try:
        delete_url = f"{PORTFOLIOS_URL}/{portfolio_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success(f"Portfolio {portfolio_id} archived successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

# For demo, use user_id = 1 (you can make this dynamic)
user_id = 1
portfolios = fetch_portfolios(user_id)

st.write("---")

if portfolios:
    st.subheader("My Portfolios")
    for portfolio in portfolios:
        portfolio_id = portfolio.get('portfolio_id', 'N/A')
        headline = portfolio.get('headline', 'No headline')
        bio = portfolio.get('bio', 'No bio')
        
        with st.expander(f"Portfolio #{portfolio_id}: {headline}"):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Headline:** {headline}")
                st.write(f"**Bio:** {bio}")
            with col2:
                if st.button("Edit", key=f"edit_{portfolio_id}"):
                    st.session_state[f"editing_{portfolio_id}"] = True
                if st.button("Archive", key=f"archive_{portfolio_id}"):
                    delete_portfolio(portfolio_id)
                    st.rerun()
            
            if st.session_state.get(f"editing_{portfolio_id}", False):
                with st.form(f"edit_form_{portfolio_id}"):
                    new_headline = st.text_input("Headline", value=headline)
                    new_bio = st.text_area("Bio", value=bio, height=150)
                    if st.form_submit_button("Update Portfolio"):
                        update_portfolio(portfolio_id, new_headline, new_bio)
                        st.session_state[f"editing_{portfolio_id}"] = False
                        st.rerun()
else:
    st.info("You don't have any portfolios yet. Create one below!")

st.write("---")
st.subheader("Create New Portfolio")
with st.form("create_portfolio_form"):
    portfolio_headline = st.text_input("Portfolio Headline *")
    portfolio_bio = st.text_area("Bio *", height=150, placeholder="Tell us about yourself and your work...")
    
    if st.form_submit_button("Create Portfolio", type="primary"):
        if portfolio_headline and portfolio_bio:
            create_portfolio(user_id, portfolio_headline, portfolio_bio)
            st.rerun()
        else:
            st.error("Please fill in all required fields")


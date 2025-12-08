import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome to the Analytics Dashboard, {st.session_state.get('first_name', 'Chris')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Rising Creators Dashboard', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Rising_Creators.py')

if st.button('View Trend Analytics', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/12_Trend_Analytics.py')

if st.button('KPI & Trend Configuration', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/13_KPI_Config.py')


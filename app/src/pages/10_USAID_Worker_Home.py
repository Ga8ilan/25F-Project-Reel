import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome to the Data Analyst dashboard, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Trend Analytics', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/14_NGO_Directory.py')

if st.button('View Top Creators', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/15_Add_NGO.py')

if st.button('View KPI & Trend Configuration Panel', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/11_Prediction.py')

import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

# Show appropriate sidebar links for the role of the currently logged in user
SideBarLinks()

st.title(f"Welcome to the Admin Dashboard, {st.session_state['first_name']}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View User Onboarding', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/01_World_Bank_Viz.py')

if st.button('View System Alerts', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/02_Map_Demo.py')

if st.button('View Pending Approvals', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/03_Pending_Approvals.py')
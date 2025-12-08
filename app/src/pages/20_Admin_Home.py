import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome to the Admin Dashboard, {st.session_state.get('first_name', 'William')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Pending Approvals', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/21_Pending_Approvals.py')

if st.button('View System Alerts', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/22_System_Alerts.py')

if st.button('View Flagged Activities', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/23_Flagged_Activities.py')
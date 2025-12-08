import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome to Your Creator Dashboard, {st.session_state.get('first_name', 'Mike')}.")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('Manage My Portfolio', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/31_Manage_Portfolio.py')

if st.button('Manage Projects & Credits', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/32_Manage_Projects.py')

if st.button('View Collaborations', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/33_Collaborations.py')


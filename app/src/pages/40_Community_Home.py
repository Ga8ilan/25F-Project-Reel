import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')

SideBarLinks()

st.title(f"Welcome to Reel, {st.session_state.get('first_name', 'Veronica')}!")
st.write('')
st.write('')
st.write('### What would you like to do today?')

if st.button('View Social Feed', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/41_Social_Feed.py')

if st.button('My Messages', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/42_Messages.py')

if st.button('Create Post', 
             type='primary',
             use_container_width=True):
  st.switch_page('pages/43_Create_Post.py')


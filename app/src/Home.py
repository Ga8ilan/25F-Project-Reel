##################################################
# This is the main/entry-point file for the 
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports reguarl and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout = 'wide')

# If a user is at this page, we assume they are not 
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false. 
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel. 
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

# set the title of the page and provide a simple prompt. 
logger.info("Loading the Home page of the app")
st.title('WELCOME TO REEL 📸')
st.write('\n\n')
# st.write('### Overview:')
# st.write('\n')
st.write('#### HI! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user 
# can click to MIMIC logging in as that mock user. 

if st.button("Act as William, a platform administrator", 
            type = 'primary', 
            use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'admin'
    st.session_state['first_name'] = 'William'
    logger.info("Logging in as Admin William")
    st.switch_page('pages/20_Admin_Home.py')

if st.button('Act as Chris Parker, a data analyst', 
            type = 'primary', 
            use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'analytics'
    st.session_state['first_name'] = 'Chris'
    logger.info("Logging in as Data Analyst Chris")
    st.switch_page('pages/10_Analytics_Home.py')

if st.button('Act as Mike Walston, a creator', 
            type = 'primary', 
            use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'creator'
    st.session_state['first_name'] = 'Mike'
    logger.info("Logging in as Creator Mike")
    st.switch_page('pages/30_Creator_Home.py')

if st.button('Act as Veronica Fuller, a community user',
                type = 'primary',
                use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'community'
    st.session_state['first_name'] = 'Veronica'
    logger.info("Logging in as Community User Veronica")
    st.switch_page('pages/40_Community_Home.py')





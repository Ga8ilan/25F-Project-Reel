import streamlit as st
from streamlit_extras.app_logo import add_logo
from modules.nav import SideBarLinks

SideBarLinks()

st.write("# REEL 📸")

st.markdown(
    """
    WELCOME TO REEL. 

    Reel is an invite-only, portfolio-first professional network built for creatives and the brands that hire them. Where LinkedIn overwhelms with noise and generic resumes, Reel elevates proven creative work by showcasing reels, credits, and verified collaborators. The app curates a high-quality ecosystem of filmmakers, designers, animators, photographers, editors, musicians, and creative directors, alongside vetted companies and agencies seeking talent. By collecting structured portfolio data, analyzing collaboration networks, and tracking availability and project metadata, Reel helps both sides make faster, better-informed decisions. 

    Stay tuned for more information and features to come!
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")

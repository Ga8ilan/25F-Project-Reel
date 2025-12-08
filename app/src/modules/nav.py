# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has function to add certain functionality to the left side bar of the app

import streamlit as st


#### ------------------------ General ------------------------
def HomeNav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def AboutPageNav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


#### ------------------------ Admin Role (William) ------------------------
def AdminHomeNav():
    st.sidebar.page_link("pages/20_Admin_Home.py", label="Admin Dashboard", icon="🖥️")

def PendingApprovalsNav():
    st.sidebar.page_link("pages/21_Pending_Approvals.py", label="Pending Approvals", icon="📋")

def SystemAlertsNav():
    st.sidebar.page_link("pages/22_System_Alerts.py", label="System Alerts", icon="🚨")

def FlaggedActivitiesNav():
    st.sidebar.page_link("pages/23_Flagged_Activities.py", label="Flagged Activities", icon="🚩")


#### ------------------------ Analytics Role (Chris) ------------------------
def AnalyticsHomeNav():
    st.sidebar.page_link("pages/10_Analytics_Home.py", label="Analytics Dashboard", icon="📈")

def RisingCreatorsNav():
    st.sidebar.page_link("pages/11_Rising_Creators.py", label="Rising Creators", icon="⭐")

def TrendAnalyticsNav():
    st.sidebar.page_link("pages/12_Trend_Analytics.py", label="Trend Analytics", icon="📊")

def KPIConfigNav():
    st.sidebar.page_link("pages/13_KPI_Config.py", label="KPI & Trend Config", icon="⚙️")


#### ------------------------ Creator Role (Mike) ------------------------
def CreatorHomeNav():
    st.sidebar.page_link("pages/30_Creator_Home.py", label="Creator Dashboard", icon="🎬")

def ManagePortfolioNav():
    st.sidebar.page_link("pages/31_Manage_Portfolio.py", label="Manage Portfolio", icon="📁")

def ManageProjectsNav():
    st.sidebar.page_link("pages/32_Manage_Projects.py", label="Manage Projects", icon="🎥")

def CollaborationsNav():
    st.sidebar.page_link("pages/33_Collaborations.py", label="Collaborations", icon="🤝")


#### ------------------------ Community/Social Role (Veronica) ------------------------
def CommunityHomeNav():
    st.sidebar.page_link("pages/40_Community_Home.py", label="Community Home", icon="🏠")

def SocialFeedNav():
    st.sidebar.page_link("pages/41_Social_Feed.py", label="Social Feed", icon="📱")

def MessagesNav():
    st.sidebar.page_link("pages/42_Messages.py", label="Messages", icon="💬")

def CreatePostNav():
    st.sidebar.page_link("pages/43_Create_Post.py", label="Create Post", icon="➕")


# --------------------------------Links Function -----------------------------------------------
def SideBarLinks(show_home=False):
    """
    This function handles adding links to the sidebar of the app based upon the logged-in user's role, which was put in the streamlit session_state object when logging in.
    """

    # add a logo to the sidebar always
    st.sidebar.image("assets/reellogo2.png", width=150)

    # If there is no logged in user, redirect to the Home (Landing) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        # Show the Home page link (the landing page)
        HomeNav()

    # Show the other page navigators depending on the users' role.
    if st.session_state["authenticated"]:

        # Admin role (William)
        if st.session_state["role"] == "admin":
            AdminHomeNav()
            PendingApprovalsNav()
            SystemAlertsNav()
            FlaggedActivitiesNav()

        # Analytics role (Chris)
        if st.session_state["role"] == "analytics":
            AnalyticsHomeNav()
            RisingCreatorsNav()
            TrendAnalyticsNav()
            KPIConfigNav()

        # Creator role (Mike)
        if st.session_state["role"] == "creator":
            CreatorHomeNav()
            ManagePortfolioNav()
            ManageProjectsNav()
            CollaborationsNav()

        # Community/Social role (Veronica)
        if st.session_state["role"] == "community":
            CommunityHomeNav()
            SocialFeedNav()
            MessagesNav()
            CreatePostNav()

    # Always show the About page at the bottom of the list of links
    AboutPageNav()

    if st.session_state["authenticated"]:
        # Always show a logout button if there is a logged in user
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            if "first_name" in st.session_state:
                del st.session_state["first_name"]
            st.switch_page("Home.py")

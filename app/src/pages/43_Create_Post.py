import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Create New Post')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Veronica')}.")

POSTS_URL = "http://web-api:4000/social/posts"

def create_post(user_id, caption, media_url=None, tags=None, visibility="public"):
    """Create a new post"""
    try:
        payload = {
            "user_id": user_id,
            "caption": caption,
            "visibility": visibility
        }
        if media_url:
            payload['media_url'] = media_url
        if tags:
            payload['tags'] = tags
        
        response = requests.post(POSTS_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Post created successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_post(post_id, caption=None, tags=None, visibility=None):
    """Update a post"""
    try:
        update_url = f"{POSTS_URL}/{post_id}"
        payload = {}
        if caption:
            payload['caption'] = caption
        if tags:
            payload['tags'] = tags
        if visibility:
            payload['visibility'] = visibility
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success("Post updated successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

st.write("---")

user_id = 1  # Demo user ID

st.subheader("Create a New Post")
with st.form("create_post_form"):
    post_caption = st.text_area("Caption *", height=200, placeholder="What's on your mind?")
    post_media_url = st.text_input("Media URL (optional)", placeholder="https://example.com/image.jpg")
    post_tags = st.text_input("Tags (comma-separated, optional)", placeholder="cinematic, drama, indie")
    post_visibility = st.selectbox("Visibility", ["public", "private"])
    
    if st.form_submit_button("Create Post", type="primary"):
        if post_caption:
            create_post(user_id, post_caption, post_media_url, post_tags, post_visibility)
            st.rerun()
        else:
            st.error("Please provide a caption")

st.write("---")
st.subheader("Recent Posts")
st.info("💡 After creating a post, you can view it in the Social Feed!")


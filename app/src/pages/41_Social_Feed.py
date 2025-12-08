import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Social Feed')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Veronica')}.")

POSTS_URL = "http://web-api:4000/social/posts"
INTERACTIONS_URL = "http://web-api:4000/social/post-interactions"

@st.cache_data(ttl=60)
def fetch_posts(user_id=None, visibility=None):
    """Fetch posts from the API"""
    try:
        params = {}
        if user_id:
            params['userID'] = user_id
        if visibility:
            params['visibility'] = visibility
        response = requests.get(POSTS_URL, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('posts', [])
        return []
    except:
        return []

def fetch_interactions(post_id):
    """Fetch interactions for a post"""
    try:
        response = requests.get(INTERACTIONS_URL, params={"postID": post_id}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('interactions', [])
        return []
    except:
        return []

def create_interaction(post_id, user_id, interaction_type, comment_text=None):
    """Create a post interaction"""
    try:
        payload = {
            "post_id": post_id,
            "user_id": user_id,
            "interaction_type": interaction_type
        }
        if comment_text:
            payload["comment_text"] = comment_text
        
        response = requests.post(INTERACTIONS_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Interaction recorded!")
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

def delete_post(post_id):
    """Delete a post"""
    try:
        delete_url = f"{POSTS_URL}/{post_id}"
        response = requests.delete(delete_url, timeout=5)
        if response.status_code == 200:
            st.success("Post deleted successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

posts = fetch_posts()

st.write("---")

if posts:
    st.subheader("Recent Posts")
    
    for post in posts[:20]:  # Show first 20
        post_id = post.get('post_id', 'N/A')
        user_id = post.get('user_id', 'N/A')
        caption = post.get('caption', 'No caption')
        media_url = post.get('media_url', '')
        tags = post.get('tags', '')
        created_at = post.get('created_at', 'N/A')
        
        with st.container():
            st.write(f"**Post #{post_id}** by User #{user_id}")
            if media_url:
                st.image(media_url, width=400)
            st.write(caption)
            if tags:
                st.write(f"Tags: {tags}")
            st.write(f"Posted: {created_at}")
            
            # Interactions
            interactions = fetch_interactions(post_id)
            likes = len([i for i in interactions if i.get('interaction_type') == 'like'])
            comments = len([i for i in interactions if i.get('interaction_type') == 'comment'])
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(f"❤️ Like ({likes})", key=f"like_{post_id}"):
                    create_interaction(post_id, 1, 'like')  # Demo user_id = 1
                    st.rerun()
            with col2:
                if st.button(f"💬 Comment ({comments})", key=f"comment_{post_id}"):
                    st.session_state[f"commenting_{post_id}"] = True
            
            if st.session_state.get(f"commenting_{post_id}", False):
                comment_text = st.text_input("Add a comment", key=f"comment_input_{post_id}")
                if st.button("Post Comment", key=f"post_comment_{post_id}"):
                    if comment_text:
                        create_interaction(post_id, 1, 'comment', comment_text)
                        st.session_state[f"commenting_{post_id}"] = False
                        st.rerun()
            
            # Show comments
            if comments > 0:
                with st.expander(f"View Comments ({comments})"):
                    for interaction in interactions:
                        if interaction.get('interaction_type') == 'comment':
                            st.write(f"**User {interaction.get('user_id', 'N/A')}:** {interaction.get('comment_text', '')}")
            
            st.write("---")
else:
    st.info("No posts found. Be the first to create a post!")


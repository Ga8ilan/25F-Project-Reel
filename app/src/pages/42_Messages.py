import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('My Messages')
st.write(f"### Welcome, {st.session_state.get('first_name', 'Veronica')}.")

MESSAGES_URL = "http://web-api:4000/social/messages"

@st.cache_data(ttl=60)
def fetch_messages(user_id):
    """Fetch messages for a user"""
    try:
        response = requests.get(MESSAGES_URL, params={"userID": user_id}, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('messages', [])
        return []
    except:
        return []

def create_message(sender_id, receiver_id, content):
    """Send a new message"""
    try:
        payload = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content
        }
        response = requests.post(MESSAGES_URL, json=payload, timeout=5)
        if response.status_code == 201:
            st.success("Message sent successfully!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def update_message(message_id, is_read=None, is_starred=None, is_archived=None):
    """Update message metadata"""
    try:
        update_url = f"{MESSAGES_URL}/{message_id}"
        payload = {}
        if is_read is not None:
            payload['is_read'] = is_read
        if is_starred is not None:
            payload['is_starred'] = is_starred
        if is_archived is not None:
            payload['is_archived'] = is_archived
        
        response = requests.put(update_url, json=payload, timeout=5)
        if response.status_code == 200:
            st.success("Message updated!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

def delete_message(message_id, user_id):
    """Delete a message"""
    try:
        delete_url = f"{MESSAGES_URL}/{message_id}"
        response = requests.delete(delete_url, params={"userID": user_id}, timeout=5)
        if response.status_code == 200:
            st.success("Message deleted!")
            st.cache_data.clear()
            return True
        return False
    except:
        return False

user_id = 1  # Demo user ID
messages = fetch_messages(user_id)

st.write("---")

col1, col2 = st.columns([2, 1])

with col1:
    if messages:
        st.subheader("My Messages")
        
        # Filter options
        filter_option = st.selectbox("Filter", ["All", "Unread", "Starred", "Archived"])
        
        filtered_messages = messages.copy()
        if filter_option == "Unread":
            filtered_messages = [m for m in messages if not m.get('is_read', False)]
        elif filter_option == "Starred":
            filtered_messages = [m for m in messages if m.get('is_starred', False)]
        elif filter_option == "Archived":
            filtered_messages = [m for m in messages if m.get('is_archived', False)]
        
        for msg in filtered_messages:
            message_id = msg.get('message_id', 'N/A')
            sender_id = msg.get('sender_id', 'N/A')
            receiver_id = msg.get('receiver_id', 'N/A')
            content = msg.get('content', 'No content')
            is_read = msg.get('is_read', False)
            is_starred = msg.get('is_starred', False)
            created_at = msg.get('created_at', 'N/A')
            
            # Determine if user is sender or receiver
            is_sender = str(sender_id) == str(user_id)
            other_user = receiver_id if is_sender else sender_id
            
            read_icon = "✅" if is_read else "📬"
            star_icon = "⭐" if is_starred else "☆"
            
            with st.expander(f"{read_icon} {star_icon} Message #{message_id} - {'To' if is_sender else 'From'} User #{other_user}"):
                st.write(f"**Content:** {content}")
                st.write(f"**Sent:** {created_at}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if not is_read:
                        if st.button("Mark as Read", key=f"read_{message_id}"):
                            update_message(message_id, is_read=True)
                            st.rerun()
                    else:
                        if st.button("Mark as Unread", key=f"unread_{message_id}"):
                            update_message(message_id, is_read=False)
                            st.rerun()
                
                with col2:
                    if not is_starred:
                        if st.button("⭐ Star", key=f"star_{message_id}"):
                            update_message(message_id, is_starred=True)
                            st.rerun()
                    else:
                        if st.button("☆ Unstar", key=f"unstar_{message_id}"):
                            update_message(message_id, is_starred=False)
                            st.rerun()
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{message_id}"):
                        delete_message(message_id, user_id)
                        st.rerun()
    else:
        st.info("No messages found. Send a message to get started!")

with col2:
    st.subheader("Send New Message")
    with st.form("send_message_form"):
        receiver_id = st.number_input("To User ID *", min_value=1)
        message_content = st.text_area("Message *", height=150)
        
        if st.form_submit_button("Send Message", type="primary"):
            if message_content and receiver_id:
                create_message(user_id, receiver_id, message_content)
                st.rerun()
            else:
                st.error("Please fill in all required fields")


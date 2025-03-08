"""
Custom CSS styles for the EduGenius Streamlit application.
"""

import streamlit as st

def apply_custom_styles():
    """Apply custom CSS styles to the Streamlit application."""
    st.markdown("""
    <style>
        /* Main application styling */
        .main {
            background-color: #f8f9fa;
        }
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        /* Header styling */
        .edu-header {
            color: #4257b2;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }
        .edu-subheader {
            color: #5a6275;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Card styling for features and content */
        .feature-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 10px;
            color: #4257b2;
        }
        .feature-title {
            font-weight: bold;
            color: #4257b2;
            margin-bottom: 10px;
        }
        
        /* Button styling */
        .submit-btn {
            background-color: #4257b2;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            font-weight: bold;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 5px 5px 0 0;
            padding: 10px 16px;
            font-weight: bold;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4257b2 !important;
            color: white !important;
        }
        
        /* Chat message styling */
        .user-message {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .assistant-message {
            background-color: #e6f3ff;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
        .stTextArea > div > div > textarea {
            border-radius: 10px;
        }
        
        /* File uploader styling */
        .stFileUploader > div > button {
            background-color: #4257b2;
            color: white;
        }
        
        /* Card container for settings */
        .settings-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* Section dividers */
        .section-divider {
            margin: 30px 0 20px 0;
            border-bottom: 1px solid #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)


def user_message_html(content):
    """
    Format user message with custom styling.
    
    Args:
        content (str): Message content
        
    Returns:
        str: HTML formatted user message
    """
    return f'<div class="user-message"><strong>You:</strong> {content}</div>'


def assistant_message_html(content):
    """
    Format assistant message with custom styling.
    
    Args:
        content (str): Message content
        
    Returns:
        str: HTML formatted assistant message
    """
    return f'<div class="assistant-message"><strong>EduGenius:</strong> {content}</div>'


def render_chat_message(message):
    """
    Render a chat message with appropriate styling based on role.
    
    Args:
        message (dict): Message dictionary with 'role' and 'content' keys
    """
    if message["role"] == "user":
        st.markdown(user_message_html(message["content"]), unsafe_allow_html=True)
    else:
        st.markdown(assistant_message_html(message["content"]), unsafe_allow_html=True)


def render_chat_history(messages):
    """
    Render a list of chat messages.
    
    Args:
        messages (list): List of message dictionaries
    """
    for message in messages:
        render_chat_message(message)

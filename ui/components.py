"""
Reusable UI components for the EduGenius application.
"""

import streamlit as st

def welcome_screen():
    """
    Display the welcome screen for first-time visitors.
    
    Returns:
        bool: True if user clicked "Get Started", False otherwise
    """
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f7ff; border-radius: 10px; margin-bottom: 25px;">
        <h2 style="color: #4257b2; text-align: center;">Welcome to EduGenius!</h2>
        <p style="text-align: center; font-size: 1.1rem;">The next-generation AI-powered educational platform that transforms how students learn and teachers teach.</p>
        
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 25px;">
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">🤖 AI Tutor</h3>
                <p>Engage in natural conversations with your AI learning companion that adapts to your learning style.</p>
            </div>
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">📷 Visual Learning</h3>
                <p>Upload images of diagrams, problems, or visual concepts for AI explanation and analysis.</p>
            </div>
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">🎧 Audio Understanding</h3>
                <p>Process lectures, podcasts, and audio content for transcription and concept extraction.</p>
            </div>
        </div>
        
        <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; margin-top: 20px;">
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">🎬 Video Analysis</h3>
                <p>Extract key moments, concepts, and generate quizzes from educational videos.</p>
            </div>
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">📝 Quiz Generator</h3>
                <p>Create personalized assessments with adaptive difficulty and instant feedback.</p>
            </div>
            <div style="flex: 1; min-width: 250px; background-color: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #4257b2;">🧠 Concept Mapper</h3>
                <p>Visualize connections between ideas to enhance understanding and retention.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    return st.button("Get Started", key="welcome_dismiss", use_container_width=True)


def chat_input_area(key_prefix="chat", placeholder="Type your question here...", height=80):
    """
    Create a standardized chat input area with text area and send button.
    
    Args:
        key_prefix (str): Prefix for session state keys
        placeholder (str): Placeholder text for input area
        height (int): Height of the input area
    
    Returns:
        tuple: (user_input, submit_button)
    """
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area(
            "Your question:",
            height=height,
            key=f"{key_prefix}_input",
            placeholder=placeholder
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button(
            "Send",
            use_container_width=True,
            key=f"{key_prefix}_submit"
        )
    
    return user_input, submit_button


def media_upload_area(key_prefix="upload"):
    """
    Create a standardized media upload area with selector and uploader.
    
    Args:
        key_prefix (str): Prefix for session state keys
        
    Returns:
        tuple: (upload_option, uploaded_file)
    """
    from config.settings import ALLOWED_EXTENSIONS
    
    # Create a dropdown for selecting media type
    upload_option = st.selectbox(
        "",
        ["Add Media", "Image", "Audio", "Video", "Document"],
        key=f"{key_prefix}_selector"
    )
    
    # Initialize uploaded_file to None
    uploaded_file = None
    
    # Show the appropriate file uploader based on selection
    if upload_option != "Add Media":
        if upload_option == "Image":
            uploaded_file = st.file_uploader(
                "Upload an image:",
                type=ALLOWED_EXTENSIONS['image'],
                key=f"{key_prefix}_image"
            )
        elif upload_option == "Audio":
            uploaded_file = st.file_uploader(
                "Upload audio:",
                type=ALLOWED_EXTENSIONS['audio'],
                key=f"{key_prefix}_audio"
            )
        elif upload_option == "Video":
            uploaded_file = st.file_uploader(
                "Upload video:",
                type=ALLOWED_EXTENSIONS['video'],
                key=f"{key_prefix}_video"
            )
        elif upload_option == "Document":
            uploaded_file = st.file_uploader(
                "Upload document:",
                type=ALLOWED_EXTENSIONS['document'],
                key=f"{key_prefix}_document"
            )
        
        # Display success message if file is uploaded
        if uploaded_file is not None:
            st.success(f"File '{uploaded_file.name}' uploaded successfully! ({uploaded_file.type})")
            
            # Store the file reference in session state
            st.session_state[f"{key_prefix}_current"] = {
                "file": uploaded_file,
                "type": upload_option,
                "name": uploaded_file.name
            }
    
    return upload_option, uploaded_file


def learning_settings_expander():
    """
    Create a standardized learning settings expander section.
    
    Returns:
        dict: Selected learning settings
    """
    with st.expander("Learning Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            learning_level = st.selectbox(
                "Learning Level:", 
                ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"]
            )
            
            learning_style = st.selectbox(
                "Learning Style:", 
                ["Visual", "Textual", "Interactive", "Example-based", "Socratic"]
            )
        
        with col2:
            memory_option = st.checkbox(
                "Enable Chat Memory",
                value=True, 
                help="When enabled, the AI will remember previous exchanges in this conversation"
            )
            
            multimedia_examples = st.checkbox(
                "Include Multimedia Examples",
                value=True,
                help="When possible, include diagrams, charts, or other visual aids in explanations"
            )
    
    return {
        "learning_level": learning_level,
        "learning_style": learning_style,
        "memory_option": memory_option,
        "multimedia_examples": multimedia_examples
    }


def spinner_with_status(text="Processing..."):
    """
    Create a spinner with status text displayed underneath.
    
    Args:
        text (str): Status text to display
        
    Returns:
        tuple: (spinner, status_placeholder)
    """
    spinner = st.spinner(text)
    status_placeholder = st.empty()
    
    return spinner, status_placeholder

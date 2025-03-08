import streamlit as st
from ui.styles import apply_custom_styles
from ui.pages import (
    learning_assistant,
    document_analysis,
    visual_learning,
    audio_analysis,
    video_learning,
    quiz_generator,
    concept_mapper
)
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT

# Initialize application
def init_app():
    """Initialize the Streamlit application settings and state."""
    # Configure page settings
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Apply custom styles
    apply_custom_styles()
    
    # Initialize session state variables
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "Learning Assistant"
        
    if "first_visit" not in st.session_state:
        st.session_state.first_visit = True
        
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

# Display welcome screen on first visit
def show_welcome_screen():
    """Display welcome screen for first-time visitors."""
    if st.session_state.first_visit:
        from ui.components import welcome_screen
        
        if welcome_screen():  # Returns True if user clicks "Get Started"
            st.session_state.first_visit = False
            st.experimental_rerun()

def main():
    """Main application entry point."""
    # Initialize app settings and state
    init_app()
    
    # Display header
    st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
    st.markdown('<div class="edu-subheader">Powered by Google Gemini | Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)
    
    # Show welcome screen for first-time visitors
    show_welcome_screen()
    
    # If not showing welcome screen, display the main application
    if not st.session_state.first_visit:
        # Define available modes/tabs
        modes = [
            "Learning Assistant", 
            "Document Analysis", 
            "Visual Learning", 
            "Audio Analysis", 
            "Video Learning", 
            "Quiz Generator", 
            "Concept Mapper"
        ]
        
        # Create tabs for each mode
        tabs = st.tabs(modes)
        
        # Handle each tab's content
        with tabs[0]:
            learning_assistant.render()
        
        with tabs[1]:
            document_analysis.render()
            
        with tabs[2]:
            visual_learning.render()
            
        with tabs[3]:
            audio_analysis.render()
            
        with tabs[4]:
            video_learning.render()
            
        with tabs[5]:
            quiz_generator.render()
            
        with tabs[6]:
            concept_mapper.render()

if __name__ == "__main__":
    main()

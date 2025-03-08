"""
Audio Analysis page module for the EduGenius application.
This provides functionality for analyzing educational audio content.
"""

import streamlit as st
from services.gemini_service import generate_text_content
from services.audio_service import process_audio_file
from utils.prompt_utils import create_audio_analysis_prompt
from utils.file_utils import save_uploaded_file, TempFileManager
from config.settings import ALLOWED_EXTENSIONS

def render():
    """Render the Audio Analysis page."""
    # Reset chat history if switching to this mode
    if st.session_state.current_mode != "Audio Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Audio Analysis"
        # Reset audio chat history
        if "audio_chat_history" in st.session_state:
            st.session_state.audio_chat_history = []
    
    # Initialize audio chat history if not exists
    if "audio_chat_history" not in st.session_state:
        st.session_state.audio_chat_history = []
    
    # Page header
    st.markdown("### Audio Learning Assistant")
    st.markdown("Upload audio files for transcription, analysis, and educational insights")
    
    # Audio upload section
    uploaded_audio = st.file_uploader("Upload an audio file:", type=ALLOWED_EXTENSIONS['audio'])
    
    if uploaded_audio is not None:
        # Display audio player
        st.audio(uploaded_audio, format="audio/mp3")
        
        # Analysis options
        analysis_options = st.multiselect(
            "Select analysis types:", 
            [
                "Transcription", 
                "Content Summary", 
                "Key Concepts Extraction", 
                "Generate Quiz from Audio",
                "Language Analysis", 
                "Vocabulary Extraction"
            ]
        )
        
        # Language selection
        language = st.selectbox(
            "Audio Language (if known):", 
            [
                "Auto-detect", 
                "English", 
                "Spanish", 
                "French", 
                "German", 
                "Chinese", 
                "Japanese", 
                "Arabic", 
                "Hindi", 
                "Russian"
            ]
        )
        
        # Process audio when button is clicked
        if st.button("Analyze Audio", use_container_width=True):
            with st.spinner("Processing audio..."):
                try:
                    # Use context manager for temporary file handling
                    with TempFileManager() as temp_manager:
                        # Save uploaded file
                        temp_file_path = temp_manager.save_uploaded_file(uploaded_audio)
                        
                        # Process audio file
                        audio_info = process_audio_file(temp_file_path, uploaded_audio.name)
                        
                        # Create prompt for audio analysis
                        analysis_prompt = create_audio_analysis_prompt(
                            audio_name=uploaded_audio.name,
                            analysis_types=analysis_options,
                            language=language
                        )
                        
                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "user", 
                            "content": f"[Audio uploaded] Please analyze with: {', '.join(analysis_options)}"
                        })
                        
                        # Generate content analysis
                        response_text = generate_text_content(
                            prompt=analysis_prompt,
                            temperature=0.2  # Lower temperature for more factual responses
                        )
                        
                        # Add response to chat history
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": response_text
                        })
                        
                        # Show audio chat interface
                        display_audio_chat(uploaded_audio.name)
                
                except Exception as e:
                    st.error(f"Error analyzing audio: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I apologize, but I encountered an error: {str(e)}"
                    })
    
    # Display audio analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")


def display_audio_chat(audio_name):
    """
    Display the audio chat interface.
    
    Args:
        audio_name (str): Name of the uploaded audio file
    """
    st.markdown("### Audio Chat")
    st.info("You can ask questions about this audio by typing below")
    
    # Display audio chat history
    for message in st.session_state.audio_chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**EduGenius:** {message['content']}")
        st.markdown("---")
    
    # Chat input
    audio_chat_input = st.text_input(
        "Ask about this audio:", 
        placeholder="e.g., Can you summarize the main points from this lecture?"
    )
    
    # Process chat input
    if st.button("Send", key="audio_chat_button"):
        if audio_chat_input:
            # Add to audio chat history
            st.session_state.audio_chat_history.append({
                "role": "user", 
                "content": audio_chat_input
            })
            
            # Generate audio chat response
            prompt = f"Regarding the audio file '{audio_name}', the user asks: {audio_chat_input}"
            
            try:
                # Generate content
                response_text = generate_text_content(
                    prompt=prompt,
                    temperature=0.7
                )
                
                # Add to chat history
                st.session_state.audio_chat_history.append({
                    "role": "assistant", 
                    "content": response_text
                })
                
                # Rerun to update the chat display
                st.experimental_rerun()
                
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.audio_chat_history.append({
                    "role": "assistant", 
                    "content": error_message
                })
                st.experimental_rerun()

"""
Video Learning page module for the EduGenius application.
This provides functionality for analyzing educational video content.
"""

import streamlit as st
from services.gemini_service import generate_text_content
from services.video_service import process_video_file, identify_key_video_moments, generate_video_timestamps
from utils.prompt_utils import create_video_analysis_prompt
from utils.file_utils import save_uploaded_file, TempFileManager
from config.settings import ALLOWED_EXTENSIONS

def render():
    """Render the Video Learning page."""
    # Reset chat history if switching to this mode
    if st.session_state.current_mode != "Video Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Video Learning"
        # Reset video chat history
        if "video_chat_history" in st.session_state:
            st.session_state.video_chat_history = []
    
    # Initialize video chat history if not exists
    if "video_chat_history" not in st.session_state:
        st.session_state.video_chat_history = []
    
    # Page header
    st.markdown("### Video Learning Assistant")
    st.markdown("Upload educational videos for AI analysis, summaries, and interactive learning")
    
    # Video upload section
    uploaded_video = st.file_uploader("Upload a video file:", type=ALLOWED_EXTENSIONS['video'])
    
    if uploaded_video is not None:
        # Display video player
        video_bytes = uploaded_video.getvalue()
        st.video(video_bytes)
        
        # Analysis options
        video_analysis_options = st.multiselect(
            "Select analysis types:", 
            [
                "Video Transcription", 
                "Content Summary", 
                "Visual Concept Detection", 
                "Key Moments Identification",
                "Generate Quiz from Video", 
                "Educational Value Assessment"
            ]
        )
        
        # Focus selection
        video_focus = st.selectbox(
            "Educational Focus:", 
            [
                "General Analysis", 
                "STEM Concepts", 
                "Humanities Focus", 
                "Language Learning", 
                "Procedural Skills", 
                "Critical Thinking"
            ]
        )
        
        # Process video when button is clicked
        if st.button("Analyze Video", use_container_width=True):
            with st.spinner("Processing video..."):
                try:
                    # Use context manager for temporary file handling
                    with TempFileManager() as temp_manager:
                        # Save uploaded file
                        temp_file_path = temp_manager.save_uploaded_file(uploaded_video)
                        
                        # Process video file
                        video_info = process_video_file(temp_file_path, uploaded_video.name)
                        
                        # Create prompt for video analysis
                        analysis_prompt = create_video_analysis_prompt(
                            video_name=uploaded_video.name,
                            analysis_types=video_analysis_options,
                            focus=video_focus
                        )
                        
                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "user", 
                            "content": f"[Video uploaded] Please analyze with: {', '.join(video_analysis_options)}"
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
                        
                        # Add key moments for video (simulated in this implementation)
                        key_moments = identify_key_video_moments(video_info, "Placeholder transcription")
                        st.session_state.video_key_moments = key_moments
                        
                        # Show interactive features
                        display_video_interactive_features(uploaded_video.name)
                
                except Exception as e:
                    st.error(f"Error analyzing video: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I apologize, but I encountered an error: {str(e)}"
                    })
    
    # Display video analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")


def display_video_interactive_features(video_name):
    """
    Display interactive features for video learning.
    
    Args:
        video_name (str): Name of the uploaded video file
    """
    st.markdown("### Video Interactive Learning")
    
    # Create tabs for different interactive features
    interactive_tabs = st.tabs(["Chat About Video", "Generate Timestamps", "Create Quiz"])
    
    with interactive_tabs[0]:
        display_video_chat(video_name)
        
    with interactive_tabs[1]:
        display_video_timestamps()
        
    with interactive_tabs[2]:
        display_video_quiz_generator(video_name)


def display_video_chat(video_name):
    """
    Display the video chat interface.
    
    Args:
        video_name (str): Name of the uploaded video file
    """
    st.markdown("#### Ask questions about this video")
    
    # Display video chat history
    for message in st.session_state.video_chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**EduGenius:** {message['content']}")
        st.markdown("---")
    
    # Chat input
    video_chat_input = st.text_input(
        "Ask about this video:", 
        placeholder="e.g., What are the main points covered in this video?"
    )
    
    # Process chat input
    if st.button("Send", key="video_chat_button"):
        if video_chat_input:
            # Add to video chat history
            st.session_state.video_chat_history.append({
                "role": "user", 
                "content": video_chat_input
            })
            
            # Generate video chat response
            prompt = f"Regarding the video file '{video_name}', the user asks: {video_chat_input}"
            
            try:
                # Generate content
                response_text = generate_text_content(
                    prompt=prompt,
                    temperature=0.7
                )
                
                # Add to chat history
                st.session_state.video_chat_history.append({
                    "role": "assistant", 
                    "content": response_text
                })
                
                # Rerun to update the chat display
                st.experimental_rerun()
                
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.video_chat_history.append({
                    "role": "assistant", 
                    "content": error_message
                })
                st.experimental_rerun()


def display_video_timestamps():
    """Display the video timestamps interface."""
    st.markdown("#### Generate Educational Timestamps")
    st.info("This identifies key moments in the video for educational purposes")
    
    # Timestamp purpose selection
    timestamp_purpose = st.selectbox(
        "Timestamp Purpose:", 
        [
            "Key Concepts", 
            "Quiz Questions", 
            "Discussion Points", 
            "Practice Exercises"
        ]
    )
    
    # Generate timestamps button
    if st.button("Generate Timestamps", key="timestamp_button"):
        if hasattr(st.session_state, "video_key_moments"):
            # Format the timestamps
            formatted_timestamps = generate_video_timestamps(st.session_state.video_key_moments)
            
            # Display table of timestamps
            st.markdown("## Generated Educational Timestamps")
            
            # Create markdown table
            timestamp_table = "| Time | Content | Educational Value |\n|------|---------|-------------------|\n"
            for ts in formatted_timestamps:
                timestamp_table += f"| {ts['time']} | {ts['description']} | {ts['educational_value']} |\n"
            
            st.markdown(timestamp_table)
        else:
            st.warning("Please analyze the video first to generate timestamps.")


def display_video_quiz_generator(video_name):
    """
    Display the video quiz generator interface.
    
    Args:
        video_name (str): Name of the uploaded video file
    """
    st.markdown("#### Generate Quiz Based on Video")
    
    # Quiz settings
    quiz_question_count = st.slider("Number of Questions:", min_value=3, max_value=15, value=5)
    quiz_format = st.selectbox(
        "Quiz Format:", 
        [
            "Multiple Choice", 
            "True/False", 
            "Mixed Formats", 
            "Short Answer"
        ]
    )
    
    # Generate quiz button
    if st.button("Create Video Quiz", key="video_quiz_button"):
        with st.spinner("Creating quiz..."):
            try:
                # Generate video quiz prompt
                prompt = f"""Create a {quiz_question_count}-question educational quiz based on the video '{video_name}'. 
Use {quiz_format} format. Include questions that assess understanding of key concepts, 
visual elements, and important points from the video. Include answers and explanations."""
                
                # Generate quiz content
                quiz_content = generate_text_content(
                    prompt=prompt,
                    temperature=0.3  # Lower temperature for more consistent quiz generation
                )
                
                # Display generated quiz
                st.markdown("## Generated Video Quiz")
                st.markdown(quiz_content)
                
            except Exception as e:
                st.error(f"Error creating quiz: {str(e)}")

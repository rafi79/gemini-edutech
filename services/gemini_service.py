"""
Gemini API service for handling interactions with Google's Generative AI models.
"""

import os
import streamlit as st
import google.generativeai as genai
from google.genai import types

# Initialize the Gemini API client
def initialize_genai():
    """Initialize the Gemini API client with the API key."""
    # Get API key from environment or use the provided one
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCagQKSSGGM-VcoOwIVEFp2l8dX-FIvTcA")
    genai.configure(api_key=api_key)
    return True

# Generate content with text prompt
def generate_text_content(prompt, temperature=0.7, model_name=None):
    """
    Generate content from a text prompt.
    
    Args:
        prompt (str): The text prompt for generation
        temperature (float, optional): Temperature for generation. Defaults to 0.7.
        model_name (str, optional): Name of the model to use. Defaults to None.
        
    Returns:
        str: Generated content
    """
    # Initialize API
    initialize_genai()
    
    # Set default model if not provided
    if not model_name:
        model_name = "gemini-2.0-flash"
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Generate content with multimodal input (text + media)
def generate_multimodal_content(prompt, media_data, media_type="image/jpeg", temperature=0.7):
    """
    Generate content from a text prompt and media data.
    
    Args:
        prompt (str): The text prompt for generation
        media_data (bytes): Binary data of the media file
        media_type (str, optional): MIME type of the media. Defaults to "image/jpeg".
        temperature (float, optional): Temperature for generation. Defaults to 0.7.
        
    Returns:
        str: Generated content
    """
    # Initialize API
    initialize_genai()
    
    # Use gemini-1.5-flash for multimedia content
    model_name = "gemini-1.5-flash"
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Generate content with media
        response = model.generate_content([
            prompt,
            {"mime_type": media_type, "data": media_data}
        ])
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content from {media_type}: {str(e)}")
        return f"I apologize, but I encountered an error processing your media: {str(e)}"

# Create a chat session
def create_chat_session(history=None, model_name="gemini-2.0-flash"):
    """
    Create a Gemini chat session.
    
    Args:
        history (list, optional): Initial chat history. Defaults to None.
        model_name (str, optional): Name of the model to use. Defaults to "gemini-2.0-flash".
        
    Returns:
        ChatSession: A Gemini chat session
    """
    # Initialize API
    initialize_genai()
    
    # Create generation config
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Start chat session
        return model.start_chat(history=history or [])
        
    except Exception as e:
        st.error(f"Error creating chat session: {str(e)}")
        return None

# Send message to chat session
def send_chat_message(chat_session, message):
    """
    Send a message to a Gemini chat session.
    
    Args:
        chat_session: The chat session
        message (str): Message to send
        
    Returns:
        str: Response text
    """
    try:
        response = chat_session.send_message(message)
        return response.text
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Function to handle video analysis specifically
def analyze_video(video_data, analysis_types, focus="General Analysis"):
    """
    Analyze video content.
    
    Args:
        video_data (bytes): Binary data of the video file
        analysis_types (list): Types of analysis to perform
        focus (str, optional): Educational focus. Defaults to "General Analysis".
        
    Returns:
        str: Analysis results
    """
    # Initialize API
    initialize_genai()
    
    # Create prompt for video analysis
    analysis_prompt = f"""
    You are EduGenius, an AI video learning assistant.
    
    Please analyze this educational video and provide insights on the following aspects:
    {', '.join(analysis_types)}
    
    Focus on {focus} educational aspects.
    
    Provide a detailed analysis organized with markdown headings, including:
    1. Content summary
    2. Key educational moments with timestamps
    3. Educational value assessment
    4. Suggested learning activities
    
    Format your response in clear, organized markdown.
    """
    
    # Use multimodal content generation for video
    return generate_multimodal_content(
        prompt=analysis_prompt,
        media_data=video_data,
        media_type="video/mp4",
        temperature=0.2  # Lower temperature for more factual analysis
    )

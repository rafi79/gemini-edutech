"""
Gemini API service for handling interactions with Google's Generative AI models.
Provides both synchronous and streaming interfaces for text and multimodal content.
"""

import google.generativeai as genai
from google.genai import types
from config.settings import get_gemini_api_key, GEMINI_MODELS, DEFAULT_GENERATION_CONFIG, SAFETY_SETTINGS
import streamlit as st

# Initialize the Gemini API client
@st.cache_resource
def initialize_genai():
    """Initialize the Gemini API client with the API key."""
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("Gemini API key not found. Please set the GEMINI_API_KEY in Streamlit secrets or environment variables.")
        st.stop()
        
    genai.configure(api_key=api_key)
    return True

# Get appropriate model based on content type
def get_model_for_content(content_type="text"):
    """
    Get the appropriate Gemini model based on content type.
    
    Args:
        content_type (str): Type of content ('text', 'image', 'audio', 'video')
        
    Returns:
        str: Name of the appropriate Gemini model
    """
    if content_type in ['image', 'audio', 'video']:
        return GEMINI_MODELS.get("multimedia")
    return GEMINI_MODELS.get("default")

# Create a generative model client
def create_generative_model(model_name=None, temperature=None):
    """
    Create a Gemini generative model instance.
    
    Args:
        model_name (str, optional): Name of the model to use. Defaults to None.
        temperature (float, optional): Temperature for generation. Defaults to None.
        
    Returns:
        GenerativeModel: A configured Gemini generative model
    """
    # Ensure API is initialized
    initialize_genai()
    
    # Set defaults if not provided
    if not model_name:
        model_name = GEMINI_MODELS.get("default")
        
    # Create generation config
    config = DEFAULT_GENERATION_CONFIG.copy()
    if temperature is not None:
        config["temperature"] = temperature
        
    # Create and return the model
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=config,
        safety_settings=SAFETY_SETTINGS
    )

# Function to generate content with text prompt
def generate_text_content(prompt, temperature=0.7, model_name=None, stream=False):
    """
    Generate content from a text prompt.
    
    Args:
        prompt (str): The text prompt for generation
        temperature (float, optional): Temperature for generation. Defaults to 0.7.
        model_name (str, optional): Name of the model to use. Defaults to None.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        
    Returns:
        Union[str, Iterator]: Generated content as string or stream iterator
    """
    model = create_generative_model(
        model_name=model_name or get_model_for_content("text"),
        temperature=temperature
    )
    
    try:
        if stream:
            return model.generate_content(prompt, stream=True)
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

# Function to generate content with multimodal input (text + media)
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
    model = create_generative_model(
        model_name=get_model_for_content(media_type.split('/')[0]),
        temperature=temperature
    )
    
    try:
        response = model.generate_content([
            prompt,
            {"mime_type": media_type, "data": media_data}
        ])
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content from {media_type}: {str(e)}")
        return f"I apologize, but I encountered an error processing your {media_type.split('/')[0]}: {str(e)}"

# Function to create a chat session
def create_chat_session(history=None, model_name=None):
    """
    Create a Gemini chat session.
    
    Args:
        history (list, optional): Initial chat history. Defaults to None.
        model_name (str, optional): Name of the model to use. Defaults to None.
        
    Returns:
        ChatSession: A Gemini chat session
    """
    model = create_generative_model(model_name=model_name or get_model_for_content("text"))
    
    try:
        return model.start_chat(history=history or [])
        
    except Exception as e:
        st.error(f"Error creating chat session: {str(e)}")
        return None

# Alternative implementation using the newer Google AI client (for streaming)
def generate_streaming_content(prompt, model_name=None, temperature=0.7):
    """
    Generate content with streaming response using Google AI client.
    
    Args:
        prompt (str): The text prompt for generation
        model_name (str, optional): Name of the model to use. Defaults to None.
        temperature (float, optional): Temperature for generation. Defaults to 0.7.
        
    Returns:
        Iterator: A stream of generated content
    """
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("Gemini API key not found. Please set the GEMINI_API_KEY in Streamlit secrets or environment variables.")
        st.stop()
    
    client = genai.Client(api_key=api_key)
    
    # Use specified model or default
    model = model_name or get_model_for_content("text")
    
    # Create content structure
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=prompt)]
        )
    ]
    
    # Configure generation parameters
    config = types.GenerateContentConfig(
        temperature=temperature,
        top_p=DEFAULT_GENERATION_CONFIG["top_p"],
        top_k=DEFAULT_GENERATION_CONFIG["top_k"],
        max_output_tokens=DEFAULT_GENERATION_CONFIG["max_output_tokens"],
        response_mime_type="text/plain",
    )
    
    try:
        return client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )
        
    except Exception as e:
        st.error(f"Error in streaming content generation: {str(e)}")
        return None

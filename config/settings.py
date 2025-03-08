import os
import streamlit as st

# Application settings
APP_TITLE = "EduGenius - AI Learning Assistant"
APP_ICON = "🧠"
APP_LAYOUT = "wide"

# Gemini API settings
def get_gemini_api_key():
    """
    Get the Gemini API key from Streamlit secrets or environment variables.
    Returns the API key as a string.
    """
    # Try to get from Streamlit secrets (preferred for production)
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    
    # Fall back to environment variable
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key
    
    # For development only - hardcoded key with warning
    # In production, this should be removed
    if os.environ.get("ENVIRONMENT") == "development":
        # This is just a placeholder - the actual key from the original code
        # Replace with proper secrets management in production
        return "AIzaSyCl9IcFv0Qv72XvrrKyN2inQ8RG_12Xr6s"
    
    # If no key is found, return None (the application will handle this case)
    return None

# Gemini model settings
GEMINI_MODELS = {
    "default": "gemini-2.0-flash",
    "chat": "gemini-2.0-flash",  # For general text interactions
    "multimedia": "gemini-1.5-flash",  # For image, audio, video processing
}

# Default generation config
DEFAULT_GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
}

# Safety settings to prevent harmful content
SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# File upload settings
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png'],
    'document': ['pdf', 'docx', 'txt'],
    'audio': ['mp3', 'wav', 'm4a', 'ogg'],
    'video': ['mp4', 'mov', 'avi', 'mkv']
}

# Maximum file size (in MB)
MAX_FILE_SIZE_MB = 25

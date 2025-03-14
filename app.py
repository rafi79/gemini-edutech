#!/usr/bin/env python3
# EduGenius - AI Learning Assistant with Multimedia Analysis

import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import warnings
import json
from datetime import datetime
import logging
import time

# Try to import PyPDF2 for PDF processing
try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not available. PDF processing will be limited.")

# Optional imports for API integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("Google Generative AI module not available.")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("Groq API module not available.")

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="EduGenius - AI Learning Assistant", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
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
    .submit-btn {
        background-color: #4257b2;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
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
    .analysis-card {
        background: linear-gradient(45deg, #f5f7ff, #e8eeff);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .analysis-title {
        color: #4257b2;
        margin-bottom: 1rem;
    }
    .analysis-content {
        background: rgba(255,255,255,0.7);
        padding: 1rem;
        border-radius: 8px;
    }
    .reasoning-card {
        background: linear-gradient(45deg, #fff5f0, #fff0e8);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .reasoning-title {
        color: #d85b31;
        margin-bottom: 1rem;
    }
    .reasoning-content {
        background: rgba(255,255,255,0.7);
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDLPkZIKqjPzdawHnWjEFnX3h-pkML0vm0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# Initialize API clients conditionally
use_groq = False
use_gemini = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if HAS_GEMINI:
    try:
        # Check if API key is valid format (at least non-empty)
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            # Verify API connectivity
            try:
                test_models = genai.list_models()
                if any("gemini" in model.name.lower() for model in test_models):
                    use_gemini = True
                    logger.info("Successfully connected to Google Gemini API")
                else:
                    logger.warning("No Gemini models found in available models")
            except Exception as e:
                logger.error(f"Error verifying Gemini models: {str(e)}")
        else:
            logger.warning("Gemini API key not provided")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {str(e)}")

if HAS_GROQ:
    try:
        # Check if API key is valid format
        if GROQ_API_KEY and len(GROQ_API_KEY) > 10:
            groq_client = Groq(api_key=GROQ_API_KEY)
            # Verify API connectivity (lightweight check)
            use_groq = True
            logger.info("Successfully initialized Groq API client")
        else:
            logger.warning("Groq API key not provided or invalid format")
    except Exception as e:
        logger.error(f"Failed to initialize Groq API: {str(e)}")

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    """
    Return the appropriate Gemini model name based on the task type
    
    Parameters:
    task_type: One of 'chat', 'image', 'audio', 'video', 'document'
    
    Returns:
    String with the model name to use
    """
    # For multimedia tasks, use Gemini 2.0 flash which has multimodal capabilities
    if task_type in ["image", "audio", "video"]:
        return "gemini-2.0-flash"
    # For document analysis requiring more reasoning
    elif task_type == "document":
        return "gemini-2.0-flash"
    # Default chat model
    else:
        return "gemini-2.0-flash"

# Function to check if Gemini API is properly set up for multimedia
def check_gemini_multimodal_support():
    """Verify if the current Gemini setup supports multimodal inputs"""
    if not use_gemini:
        return False
        
    try:
        available_models = genai.list_models()
        for model in available_models:
            if "gemini-2.0" in model.name and "generateContent" in str(model.supported_generation_methods):
                # Check if model supports multimodal inputs
                if any(input_type for input_type in ["image", "video", "audio"] if input_type in str(model)):
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking multimodal support: {str(e)}")
        return False

# Function to generate content with Gemini API
def generate_content(prompt, model_name="gemini-2.0-flash", image_data=None, audio_data=None, video_data=None, temperature=0.7):
    """Generate content with error handling for multimedia inputs"""
    if not use_gemini:
        return "Gemini API is not available. Please install the google-generativeai package and set your API key."
    
    try:
        # Generation config
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        
        # Create model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Prepare content parts list
        content_parts = [{"text": prompt}]
        
        # Add multimedia if provided
        if image_data:
            # Encode image
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg", 
                    "data": encoded_image
                }
            })
        
        if audio_data:
            # Determine MIME type based on file extension
            mime_type = "audio/mpeg"  # Default
            if hasattr(audio_data, 'name'):
                if audio_data.name.lower().endswith('.wav'):
                    mime_type = "audio/wav"
                elif audio_data.name.lower().endswith('.mp3'):
                    mime_type = "audio/mpeg"
                elif audio_data.name.lower().endswith('.m4a'):
                    mime_type = "audio/mp4"
            
            # Encode audio
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": mime_type, 
                    "data": encoded_audio
                }
            })
        
        if video_data:
            # Determine MIME type based on file extension
            mime_type = "video/mp4"  # Default
            if hasattr(video_data, 'name'):
                if video_data.name.lower().endswith('.mp4'):
                    mime_type = "video/mp4"
                elif video_data.name.lower().endswith('.webm'):
                    mime_type = "video/webm"
                elif video_data.name.lower().endswith('.mov'):
                    mime_type = "video/quicktime"
            
            # Encode video
            encoded_video = base64.b64encode(video_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": mime_type, 
                    "data": encoded_video
                }
            })
        
        # Generate content with all parts
        response = model.generate_content(content_parts)
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return f"Sorry, I encountered an error with Gemini API: {str(e)}"

# Function to generate content with DeepSeek model via Groq API for enhanced reasoning
def generate_content_with_deepseek(prompt, temperature=0.6, max_tokens=4096):
    """Generate content using DeepSeek R1 Distill Qwen 32B model through Groq API with streaming"""
    if not use_groq:
        return "Groq API is not available. Please install the groq package and set your API key."
    
    try:
        # Validate API key format first
        if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
            return "Invalid Groq API key. Please provide a valid API key."
            
        full_response = ""
        
        # Create completion with streaming using DeepSeek model
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-qwen-32b",  # Using DeepSeek model with strong reasoning
            messages=[
                {"role": "system", "content": "You are an expert educational content creator with advanced reasoning abilities. You provide detailed, thoughtful responses that show your step-by-step thinking process."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            stream=True,
            stop=None,
        )
        
        # Process streaming response
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                full_response += chunk_content
                
        return full_response
    
    except Exception as e:
        logger.error(f"DeepSeek API error: {str(e)}")
        return f"Sorry, I encountered an error with the DeepSeek model: {str(e)}"

# Fallback text generation for when APIs are not available
def generate_text_fallback(prompt):
    """Provide a basic response when APIs are not available"""
    return f"I would respond to: '{prompt}' but API access is currently unavailable. Please ensure you have installed the required packages and provided API keys."

# Class for Educational Content Analysis
class EducationalContentAnalyzer:
    def __init__(self):
        if use_gemini:
            # Using the already configured Gemini client
            self.model_available = True
        else:
            self.model_available = False
            logger.warning("Gemini API not available for Content Analysis")
    
    def analyze_video_content(self, video_file, context_info=None):
        """
        Analyze video for educational content insights
        
        Parameters:
        video_file: Streamlit UploadedFile object
        context_info: Dictionary with analysis context information
        
        Returns:
        List of string analysis results
        """
        if not self.model_available:
            return ["Gemini API not available. Cannot perform video analysis."]
        
        try:
            # Prepare context string based on provided info
            context_str = ""
            focus_str = ""
            thoroughness = "standard"
            
            if context_info:
                if "contexts" in context_info and context_info["contexts"]:
                    context_str = ", ".join(context_info["contexts"])
                if "focus_areas" in context_info and context_info["focus_areas"]:
                    focus_str = ", ".join(context_info["focus_areas"])
                if "thoroughness" in context_info:
                    thoroughness = context_info["thoroughness"].lower()
            
            # Get video metadata
            video_name = video_file.name
            video_type = video_file.type
            video_size = len(video_file.getvalue()) / (1024 * 1024)  # Size in MB
            
            # Adjust detail level based on thoroughness
            detail_level = {
                "basic": "Provide a brief overview of the key educational concepts.",
                "standard": "Provide a balanced analysis with moderate detail on educational content.",
                "detailed": "Provide an in-depth, comprehensive analysis with detailed explanations of all educational concepts observed in the video."
            }.get(thoroughness, "Provide a balanced analysis with moderate detail.")
            
            # Create a detailed prompt for video analysis
            video_prompt = f"""
            Analyze this educational video file ({video_name}, {video_type}, {video_size:.2f} MB) for educational content and teaching strategies.
            
            Educational Context: {context_str or "General educational setting"}
            Analysis Focus Areas: {focus_str or "General educational content and pedagogy"}
            
            Focus your analysis on:
            • Key educational concepts presented
            • Teaching methodologies demonstrated
            • Learning objectives covered
            • Student engagement strategies
            • Visual and auditory teaching techniques
            • Sequencing and pacing of content
            • Examples and illustrations used
            • Instructional clarity and effectiveness
            
            {detail_level}
            
            Provide a comprehensive educational assessment including:
            1. Main educational concepts identified
            2. Teaching strategies observed
            3. Suggestions for enhancing the educational content
            4. How the content connects to broader learning objectives
            5. Summary of key educational takeaways
            
            Format your response using markdown for readability.
            """
            
            # Generate response using Gemini with appropriate model for video
            response = generate_content(
                prompt=video_prompt,
                model_name="gemini-2.0-flash",
                video_data=video_file.getvalue(),
                temperature=0.3
            )
            
            return [response]
            
        except Exception as e:
            logger.error(f"Error in video analysis: {e}")
            return [f"Error in video analysis: {str(e)}"]

    def analyze_audio_content(self, audio_file, context_info=None):
        """
        Analyze audio for educational content insights
        
        Parameters:
        audio_file: Streamlit UploadedFile object
        context_info: Dictionary with analysis context information
        
        Returns:
        List of string analysis results
        """
        if not self.model_available:
            return ["Gemini API not available. Cannot perform audio analysis."]
        
        try:
            # Prepare context string based on provided info
            context_str = ""
            focus_str = ""
            thoroughness = "standard"
            
            if context_info:
                if "contexts" in context_info and context_info["contexts"]:
                    context_str = ", ".join(context_info["contexts"])
                if "focus_areas" in context_info and context_info["focus_areas"]:
                    focus_str = ", ".join(context_info["focus_areas"])
                if "thoroughness" in context_info:
                    thoroughness = context_info["thoroughness"].lower()
            
            # Get audio metadata
            audio_name = audio_file.name
            audio_type = audio_file.type
            audio_size = len(audio_file.getvalue()) / (1024 * 1024)  # Size in MB
            
            # Adjust detail level based on thoroughness
            detail_level = {
                "basic": "Provide a brief overview of the key educational concepts.",
                "standard": "Provide a balanced analysis with moderate detail on educational content.",
                "detailed": "Provide an in-depth, comprehensive analysis with detailed explanations of all educational concepts in the audio."
            }.get(thoroughness, "Provide a balanced analysis with moderate detail.")
            
            # Create a detailed prompt for audio analysis
            audio_prompt = f"""
            Analyze this educational audio file ({audio_name}, {audio_type}, {audio_size:.2f} MB) for educational content and teaching strategies.
            
            Educational Context: {context_str or "General educational setting"}
            Analysis Focus Areas: {focus_str or "General educational content and pedagogy"}
            
            Focus your analysis on:
            • Key educational concepts presented
            • Verbal teaching techniques
            • Clarity of explanations
            • Questioning strategies used
            • Pacing and structure of the lesson
            • Verbal engagement techniques
            • Use of examples and analogies
            • Content organization and flow
            
            {detail_level}
            
            Provide a detailed educational analysis of:
            1. Main educational concepts identified
            2. Verbal teaching strategies observed
            3. Suggestions for enhancing the audio instruction
            4. How the content connects to broader learning objectives
            5. Summary of key educational takeaways
            
            Format your response using markdown for readability.
            """
            
            # Generate response using Gemini with appropriate model for audio
            response = generate_content(
                prompt=audio_prompt,
                model_name="gemini-2.0-flash",
                audio_data=audio_file.getvalue(),
                temperature=0.3
            )
            
            return [response]
        
        except Exception as e:
            logger.error(f"Error in audio analysis: {e}")
            return [f"Error in audio analysis: {str(e)}"]

    def analyze_content(self, video_file, audio_file, context_info=None):
        """
        Process both video and audio files with contextual information and return analysis results
        
        Parameters:
        video_file: Streamlit UploadedFile object for video or None
        audio_file: Streamlit UploadedFile object for audio or None
        context_info: Dictionary with keys 'contexts', 'focus_areas', and 'thoroughness'
        
        Returns:
        Dictionary with analysis results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "video_analysis": None,
            "audio_analysis": None
        }

        if video_file:
            results["video_analysis"] = self.analyze_video_content(video_file, context_info)

        if audio_file:
            results["audio_analysis"] = self.analyze_audio_content(audio_file, context_info)

        return results

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Learning Assistant"

if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm your AI learning companion. What would you like to learn about today?"}
    ]

if "reasoning_messages" not in st.session_state:
    st.session_state.reasoning_messages = [
        {"role": "assistant", "content": "👋 Welcome to the DeepSeek Reasoning Assistant! I use advanced reasoning to create educational content. What topic would you like me to explore with in-depth reasoning?"}
    ]

# Header
st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
st.markdown('<div class="edu-subheader">Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)

# Display welcome screen on first visit
if st.session_state.first_visit:
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
                <h3 style="color: #d85b31;">🧠 Reasoning Assistant</h3>
                <p>Create educational content with deep reasoning capabilities using advanced DeepSeek AI model.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.rerun()

# Display API status
with st.sidebar:
    st.header("API Status")
    
    if use_gemini:
        st.success("✅ Google Gemini API: Connected")
    else:
        st.error("❌ Google Gemini API: Not Available")
        st.info("To use Gemini features, install the google-generativeai package and set your API key.")
        
    if use_groq:
        st.success("✅ Groq API: Connected")
        st.success("✅ DeepSeek R1 Model: Available")
    else:
        st.error("❌ Groq API: Not Available")
        st.info("To use Groq and DeepSeek features, install the groq package and set your API key.")
    
    # Add setup instructions
    with st.expander("Setup Instructions"):
        st.markdown("""
        ### Setting Up API Access
        
        1. **Install Required Packages**:
           ```
           pip install streamlit Pillow PyPDF2 google-generativeai groq
           ```
           
        2. **Set API Keys as Environment Variables**:
           - For Gemini: `GEMINI_API_KEY`
           - For Groq: `GROQ_API_KEY`
        """)

# Define tab names and create tabs
tab_names = ["Learning Assistant", "Document Analysis", "Visual Learning", "DeepSeek Reasoning", "Quiz Generator", "Educational Content Analysis"]
selected_tab = st.tabs(tab_names)

# Learning Assistant tab
with selected_tab[0]:
    if st.session_state.current_mode != "Learning Assistant":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Learning Assistant"
    
    st.markdown("### Your AI Learning Companion")
    st.markdown("Ask any question about any subject, request explanations, or get help with homework")
    
    # Configure learning settings in an expandable section
    with st.expander("Learning Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            learning_level = st.selectbox("Learning Level:", 
                                        ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"])
            learning_style = st.selectbox("Learning Style:", 
                                        ["Visual", "Textual", "Interactive", "Example-based", "Socratic"])
        
        with col2:
            memory_option = st.checkbox("Enable Chat Memory", value=True, 
                                     help="When enabled, the AI will remember previous exchanges in this conversation")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.tutor_messages:
            if message["role"] == "user":
                st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #e6f3ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>EduGenius:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input area with a more modern design
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area("Your question:", height=80, key="tutor_input",
                                placeholder="Type your question here... (e.g., Explain quantum entanglement in simple terms)")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button("Send", use_container_width=True, key="tutor_submit")
        
        # Add multimedia upload option
        upload_option = st.selectbox("", ["Add Media", "Image"], key="upload_selector")
    
    # Handle file uploads
    uploaded_file = None
    if upload_option != "Add Media":
        if upload_option == "Image":
            uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"], key="chat_image_upload")
        
        if uploaded_file is not None:
            # Display information about the uploaded file
            st.success(f"File '{uploaded_file.name}' uploaded successfully! ({uploaded_file.type})")
            # Store the file reference in the session state for later use
            st.session_state.current_upload = {
                "file": uploaded_file,
                "type": upload_option,
                "name": uploaded_file.name
            }
            
    # Processing user input
    # Processing user input
        if submit_button and user_input:
    #   Add user message to chat
           st.session_state.tutor_messages.append({"role": "user", "content": user_input})
    
    # Create system context based on selected options
            system_context = f"You are EduGenius, an educational AI tutor. Adapt your explanation for {learning_level} level students. Use a {learning_style} learning style in your response."
    
    # Create conversation history for context
    conversation_history = ""
      if memory_option and len(st.session_state.tutor_messages) > 1:
        for msg in st.session_state.tutor_messages[:-1]:  # Exclude the current message
            role = "User" if msg["role"] == "user" else "EduGenius"
            conversation_history += f"{role}: {msg['content']}\n\n"
    
    # Try to generate response
          with st.spinner("Thinking..."):
          try:
            # Determine if we have multimedia
            has_multimedia = False
            media_bytes = None
            
            # Rest of your code here...
        # Code to execute while showing spinner
        # Rest of the code
        if analyze_button and (video_file or audio_file):
        with st.spinner("Analyzing educational content..."):
            try:
                # Create content analyzer
                content_analyzer = EducationalContentAnalyzer()
                
                # Prepare context information dictionary
                context_info = {
                    "contexts": context_options,
                    "focus_areas": focus_areas,
                    "thoroughness": thoroughness
                }
                
                # Display progress information
                analysis_progress = st.progress(0)
                status_text = st.empty()
                
                # Update status
                status_text.text("Initializing analysis...")
                analysis_progress.progress(10)
                
                # Process content with context awareness
                if video_file and audio_file:
                    status_text.text("Analyzing video and audio content...")
                    analysis_progress.progress(25)
                elif video_file:
                    status_text.text("Analyzing video content...")
                    analysis_progress.progress(25)
                else:
                    status_text.text("Analyzing audio content...")
                    analysis_progress.progress(25)
                
                # Perform the analysis with context information
                results = content_analyzer.analyze_content(video_file, audio_file, context_info)
                
                # Update progress
                status_text.text("Processing results...")
                analysis_progress.progress(75)
                
                # Store results in session state for persistence
                st.session_state.edu_results = results
                
                # Complete progress
                analysis_progress.progress(100)
                status_text.text("Analysis complete!")
                
                # Clear progress indicators after a moment
                time.sleep(1)
                status_text.empty()
                analysis_progress.empty()
                
                # Display results in a styled container
                st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                st.markdown('<h2 class="analysis-title">Educational Content Analysis Results</h2>', unsafe_allow_html=True)
                
                # Add timestamp and context
                st.markdown(f"**Analysis time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Educational contexts:** {', '.join(context_options)}")
                st.markdown(f"**Focus areas:** {', '.join(focus_areas)}")
                st.markdown(f"**Analysis level:** {thoroughness}")
                
                # Video results
                if video_file and results.get("video_analysis"):
                    st.subheader("📹 Video Analysis")
                    st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                    for analysis in results["video_analysis"]:
                        st.markdown(analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Audio results
                if audio_file and results.get("audio_analysis"):
                    st.subheader("🔊 Audio Analysis")
                    st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                    for analysis in results["audio_analysis"]:
                        st.markdown(analysis)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Prepare download report with enhanced formatting
                report_content = f"""
                # Educational Content Analysis Report
                
                ## Analysis Overview
                - **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                - **Educational Contexts:** {', '.join(context_options)}
                - **Focus Areas:** {', '.join(focus_areas)}
                - **Analysis Level:** {thoroughness}
                
                ## Files Analyzed
                {f"- **Video:** {video_file

# Quiz Generator tab
with selected_tab[4]:
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.current_mode = "Quiz Generator"
        
    st.markdown("### AI Quiz Generator")
    st.markdown("Create custom quizzes for any subject and learning level")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quiz_subject = st.text_input("Subject or topic:", placeholder="E.g., World War II, Photosynthesis, Calculus")
        quiz_level = st.select_slider(
            "Difficulty level:",
            options=["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"],
            value="High School"
        )
    
    with col2:
        quiz_type = st.selectbox(
            "Question type:",
            ["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank", "Mixed"]
        )
        question_count = st.slider("Number of questions:", min_value=3, max_value=20, value=5)
    
    # Additional options
    with st.expander("Advanced Options"):
        include_answers = st.checkbox("Include answers", value=True)
        include_explanations = st.checkbox("Include explanations", value=True)
        specific_topics = st.text_area("Focus on specific subtopics (optional):", 
                                      placeholder="E.g., 'Focus on European theater' or 'Only cover derivatives'")
    
    # Generate quiz button
    if st.button("Generate Quiz", use_container_width=True):
        if not quiz_subject:
            st.warning("Please enter a subject or topic for the quiz.")
        else:
            with st.spinner("Creating your custom quiz..."):
                try:
                    # Build prompt
                    prompt = f"Create a {quiz_level} level quiz about {quiz_subject} with {question_count} {quiz_type} questions. "
                    
                    if specific_topics:
                        prompt += f"Focus on these specific subtopics: {specific_topics}. "
                    
                    prompt += "Format the quiz nicely with markdown. "
                    
                    if include_answers:
                        prompt += "Include the correct answers. "
                    
                    if include_explanations:
                        prompt += "Provide brief explanations for each answer. "
                    
                    # Get response
                    if use_gemini:
                        response = generate_content(
                            prompt=prompt,
                            model_name=get_model_name("chat"),
                            temperature=0.7
                        )
                    else:
                        response = generate_text_fallback(prompt)
                    
                    # Display quiz
                    st.markdown("## Your Custom Quiz")
                    st.markdown(response)
                    
                    # Add download option
                    quiz_filename = f"{quiz_subject.replace(' ', '_').lower()}_quiz.md"
                    st.download_button(
                        label="Download Quiz",
                        data=response,
                        file_name=quiz_filename,
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")

# Educational Content Analysis tab
with selected_tab[5]:
    if st.session_state.current_mode != "Educational Content Analysis":
        st.session_state.edu_results = {}  # Initialize results storage
        st.session_state.current_mode = "Educational Content Analysis"
    
    st.markdown("### Educational Content Analysis")
    st.markdown("Upload educational videos or audio for AI-powered analysis of teaching content and strategies")
    
    # Check for Gemini API suitability
    if not use_gemini:
        st.warning("⚠️ Gemini API is not available. Please install the google-generativeai package and set your API key to use this feature.")
    elif not check_gemini_multimodal_support():
        st.warning("⚠️ Your current Gemini API setup may not fully support multimodal analysis. Results may be limited.")
    
    # Create columns for video and audio uploads
    col1, col2 = st.columns(2)
    
    video_file = None
    audio_file = None
    
    with col1:
        st.subheader("Video Analysis")
        video_file = st.file_uploader("Upload educational video:", 
                                    type=["mp4", "mov", "webm"], 
                                    key="edu_video",
                                    help="Upload a video of educational content for AI analysis")
        
        # Video settings
        if video_file:
            # Display video preview with proper handling
            try:
                # Create a temp file to properly display the video
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{video_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(video_file.getvalue())
                    video_path = tmp_file.name
                
                # Display the video
                st.video(video_path)
                
                # Remove temp file after displaying
                try:
                    os.unlink(video_path)
                except:
                    pass  # Ignore errors in cleanup
                
            except Exception as e:
                st.error(f"Error displaying video preview: {str(e)}")
                st.info("Video preview not available, but analysis can still be performed.")
            
            # Show video details
            video_size_mb = len(video_file.getvalue()) / (1024 * 1024)
            st.info(f"Video: {video_file.name} ({video_file.type}, {video_size_mb:.2f} MB)")
            
            # Warning for large files
            if video_size_mb > 20:
                st.warning("⚠️ Large video file detected. Analysis may take longer and could be less accurate. Consider using a shorter clip for better results.")
    
    with col2:
        st.subheader("Audio Analysis") 
        audio_file = st.file_uploader("Upload educational audio:", 
                                    type=["mp3", "wav", "m4a"], 
                                    key="edu_audio",
                                    help="Upload educational audio for content and teaching analysis")
        
        if audio_file:
            # Display audio player with proper handling
            try:
                # Create a temp file to properly display the audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{audio_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    audio_path = tmp_file.name
                
                # Display the audio
                st.audio(audio_path)
                
                # Remove temp file after displaying
                try:
                    os.unlink(audio_path)
                except:
                    pass  # Ignore errors in cleanup
                
            except Exception as e:
                st.error(f"Error displaying audio preview: {str(e)}")
                st.info("Audio preview not available, but analysis can still be performed.")
            
            # Show audio details
            audio_size_mb = len(audio_file.getvalue()) / (1024 * 1024)
            st.info(f"Audio: {audio_file.name} ({audio_file.type}, {audio_size_mb:.2f} MB)")
            
            # Warning for large files
            if audio_size_mb > 10:
                st.warning("⚠️ Large audio file detected. Analysis may take longer. Consider using a shorter clip for better results.")
    
    # Add a context selection with improved descriptions
    st.subheader("Analysis Context")
    context_options = st.multiselect(
        "Select educational contexts to consider:",
        [
            "Elementary Education (K-5)", 
            "Middle School (6-8)",
            "High School (9-12)",
            "Higher Education", 
            "Professional Development", 
            "Special Education",
            "Online Learning", 
            "STEM Education"
        ],
        default=["Elementary Education (K-5)"]
    )
    
    # Additional analysis parameters
    col1, col2 = st.columns(2)
    
    with col1:
        focus_areas = st.multiselect(
            "Focus areas for analysis:",
            [
                "Teaching Methods", 
                "Content Accuracy", 
                "Learning Objectives",
                "Engagement Strategies",
                "Instructional Clarity",
                "Pedagogical Approach",
                "Content Organization"
            ],
            default=["Teaching Methods", "Content Accuracy"]
        )
    
    with col2:
        thoroughness = st.select_slider(
            "Analysis thoroughness:",
            options=["Basic", "Standard", "Detailed"],
            value="Standard",
            help="More thorough analysis will take longer but provide more detailed insights"
        )
    
    # Analysis button
    analyze_button = st.button("Analyze Educational Content", 
                              use_container_width=True,
                              disabled=not (video_file or audio_file) or not use_gemini)

# Visual Learning tab
with selected_tab[2]:
    if st.session_state.current_mode != "Visual Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Visual Learning"
        
    st.markdown("### Visual Learning Analysis")
    st.markdown("Upload images, diagrams, or visual problems for AI explanation and tutoring")
    
    # Image upload section
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png", "gif"], key="visual_learning_image")
    
    if uploaded_image:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption=f"Uploaded: {uploaded_image.name}", use_column_width=True)
        
        # Analysis type selection
        analysis_types = st.multiselect(
            "What would you like me to do with this image?",
            [
                "Explain the concept shown", 
                "Identify key elements",
                "Provide step-by-step solution", 
                "Relate to curriculum topics",
                "Generate practice questions", 
                "Explain in simpler terms"
            ],
            default=["Explain the concept shown"]
        )
        
        # Add subject context
        subject_area = st.selectbox(
            "Subject area:",
            ["General", "Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", 
             "History", "Geography", "Literature", "Art", "Music", "Economics"]
        )
        
        # Education level
        education_level = st.select_slider(
            "Education level:",
            options=["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Professional"],
            value="High School"
        )
        
        # Custom query
        custom_prompt = st.text_area(
            "Additional instructions (optional):",
            placeholder="E.g., 'Focus on how this relates to Newton's Laws' or 'Explain how to solve this equation'"
        )
        
        # Process the image
        if st.button("Analyze Image", use_container_width=True):
            if not use_gemini:
                st.error("Gemini API is required for image analysis. Please set up the API key.")
            else:
                with st.spinner("Analyzing your image..."):
                    try:
                        # Prepare the image data
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                        img_data = img_byte_arr.getvalue()
                        
                        # Create prompt based on selections
                        prompt = f"I'm a student at the {education_level} level studying {subject_area}. "
                        prompt += f"Please analyze this image and {', '.join(analysis_types).lower()}. "
                        
                        if custom_prompt:
                            prompt += f"Additional instructions: {custom_prompt}"
                        
                        # Generate response
                        response = generate_content(
                            prompt=prompt,
                            model_name=get_model_name("image"),
                            image_data=img_data,
                            temperature=0.2
                        )
                        
                        # Display the response
                        st.markdown("### Analysis Results")
                        st.markdown(response)
                        
                        # Add to history
                        st.session_state.chat_history.append({
                            "role": "user", 
                            "content": f"Analyze image {uploaded_image.name}: {prompt}"
                        })
                        st.session_state.chat_history.append({
                            "role": "assistant", 
                            "content": response
                        })
                        
                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
    else:
        st.info("Please upload an image to begin analysis")
        
        # Example showcase
        with st.expander("Examples of what you can analyze"):
            st.markdown("""
            - **Math problems** - Get step-by-step solutions
            - **Science diagrams** - Get detailed explanations of processes
            - **Charts and graphs** - Understand data visualizations
            - **Historical artifacts** - Learn about historical context
            - **Technical illustrations** - Understand complex systems
            - **Biological diagrams** - Explore anatomy and processes
            - **Chemistry structures** - Understand molecular compositions
            """)

# DeepSeek Reasoning Assistant tab
with selected_tab[3]:
    if st.session_state.current_mode != "DeepSeek Reasoning":
        st.session_state.current_mode = "DeepSeek Reasoning"

    st.markdown("### 🧠 DeepSeek Reasoning Assistant")
    st.markdown("The DeepSeek Reasoning Assistant uses advanced AI reasoning to create high-quality educational content with step-by-step thinking.")
    
    if not use_groq:
        st.error("⚠️ The DeepSeek model requires the Groq API. Please install the groq package and set your API key.")
    else:
        # Display chat messages
        reasoning_container = st.container()
        with reasoning_container:
            for message in st.session_state.reasoning_messages:
                if message["role"] == "user":
                    st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='background-color: #fff0e8; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>DeepSeek:</strong> {message['content']}</div>", unsafe_allow_html=True)
        
        # Configuration options
        with st.expander("Content Generation Settings"):
            col1, col2 = st.columns(2)
            
            with col1:
                content_type = st.selectbox(
                    "Content Type:",
                    ["Lesson Plan", "Educational Essay", "Concept Explanation", 
                     "Problem-Solution Walkthrough", "Debate Analysis", 
                     "Research Summary", "Step-by-Step Tutorial"]
                )
                
                audience_level = st.select_slider(
                    "Target Audience:",
                    options=["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"],
                    value="High School"
                )
            
            with col2:
                reasoning_depth = st.select_slider(
                    "Reasoning Depth:",
                    options=["Basic", "Standard", "In-depth", "Comprehensive"],
                    value="Standard",
                    help="Higher reasoning depth produces more detailed step-by-step thinking"
                )
                
                temperature_value = st.slider(
                    "Creativity Level:",
                    min_value=0.1,
                    max_value=1.0,
                    value=0.7,
                    step=0.1,
                    help="Lower values produce more deterministic output, higher values more creative"
                )
        
        # Input area
        st.markdown("<br>", unsafe_allow_html=True)
        user_prompt = st.text_area(
            "What educational content would you like me to create?",
            height=100,
            key="deepseek_input",
            placeholder="Describe the educational content you'd like me to create using advanced reasoning (e.g., Explain the concept of quantum superposition for high school students, or Create a lesson plan on photosynthesis)"
        )
        
        # Process button
        generate_button = st.button(
            "Generate Educational Content with Reasoning",
            key="deepseek_generate",
            use_container_width=True,
            disabled=not use_groq
        )
        
        if generate_button and user_prompt:
            # Add user message to history
            st.session_state.reasoning_messages.append({"role": "user", "content": user_prompt})
            
            # Create detailed instruction prompt
            system_instruction = f"""
            Create high-quality educational content on: {user_prompt}
            
            Content type: {content_type}
            Target audience: {audience_level} level
            Reasoning depth: {reasoning_depth}
            
            Please follow these guidelines:
            1. Start by analyzing what the core concepts and learning objectives should be.
            2. Use clear and explicit step-by-step reasoning throughout your explanation.
            3. Break down complex ideas into understandable components.
            4. Provide examples, analogies, and illustrations where helpful.
            5. Show your thought process as you develop this educational content.
            6. Format your response with markdown for readability.
            7. Maintain educational accuracy while making the content engaging.
            
            For {audience_level} level students, tailor your language, examples, and depth appropriately.
            """
            
            # Process with DeepSeek model
            with st.spinner(f"Generating {content_type.lower()} with DeepSeek reasoning..."):
                try:
                    response = generate_content_with_deepseek(
                        prompt=system_instruction,
                        temperature=temperature_value,
                        max_tokens=4096
                    )
                    
                    # Add response to chat history
                    st.session_state.reasoning_messages.append({"role": "assistant", "content": response})
                    
                    # Clear input
                    st.session_state["deepseek_input"] = ""
                    
                    # Refresh the display
                    st.rerun()
                    
                except Exception as e:
                    error_message = f"I apologize, but I encountered an error when using the DeepSeek model: {str(e)}"
                    st.session_state.reasoning_messages.append({"role": "assistant", "content": error_message})
                    st.rerun()
                    
        # Display helpful information for first-time users
        if len(st.session_state.reasoning_messages) <= 1:
            st.markdown("""
            <div style="background-color: #f9f2ee; padding: 15px; border-radius: 10px; margin-top: 20px;">
                <h4 style="color: #d85b31;">💡 How to use the DeepSeek Reasoning Assistant</h4>
                <p>The DeepSeek R1 Distill Qwen 32B model is specially designed for strong reasoning capabilities to create high-quality educational content. Try asking for:</p>
                <ul>
                    <li>In-depth concept explanations with step-by-step reasoning</li>
                    <li>Complex problem solutions that show all thinking steps</li>
                    <li>Educational content that breaks down difficult topics</li>
                    <li>Step-by-step tutorials that reveal the reasoning process</li>
                    <li>Detailed lesson plans with pedagogical reasoning</li>
                </ul>
                <p>The assistant will reveal its reasoning process as it creates educational content.</p>
            </div>
            """, unsafe_allow_html=True)#!/usr/bin/env python3
# EduGenius - AI Learning Assistant with Multimedia Analysis

import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import warnings
import json
from datetime import datetime
import logging
import time

# Try to import PyPDF2 for PDF processing
try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not available. PDF processing will be limited.")

# Optional imports for API integration
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("Google Generative AI module not available.")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False
    print("Groq API module not available.")

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="EduGenius - AI Learning Assistant", 
    page_icon="🧠", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
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
    .submit-btn {
        background-color: #4257b2;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
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
    .analysis-card {
        background: linear-gradient(45deg, #f5f7ff, #e8eeff);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .analysis-title {
        color: #4257b2;
        margin-bottom: 1rem;
    }
    .analysis-content {
        background: rgba(255,255,255,0.7);
        padding: 1rem;
        border-radius: 8px;
    }
    .reasoning-card {
        background: linear-gradient(45deg, #fff5f0, #fff0e8);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .reasoning-title {
        color: #d85b31;
        margin-bottom: 1rem;
    }
    .reasoning-content {
        background: rgba(255,255,255,0.7);
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDLPkZIKqjPzdawHnWjEFnX3h-pkML0vm0")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# Initialize API clients conditionally
use_groq = False
use_gemini = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if HAS_GEMINI:
    try:
        # Check if API key is valid format (at least non-empty)
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            # Verify API connectivity
            try:
                test_models = genai.list_models()
                if any("gemini" in model.name.lower() for model in test_models):
                    use_gemini = True
                    logger.info("Successfully connected to Google Gemini API")
                else:
                    logger.warning("No Gemini models found in available models")
            except Exception as e:
                logger.error(f"Error verifying Gemini models: {str(e)}")
        else:
            logger.warning("Gemini API key not provided")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini API: {str(e)}")

if HAS_GROQ:
    try:
        # Check if API key is valid format
        if GROQ_API_KEY and len(GROQ_API_KEY) > 10:
            groq_client = Groq(api_key=GROQ_API_KEY)
            # Verify API connectivity (lightweight check)
            use_groq = True
            logger.info("Successfully initialized Groq API client")
        else:
            logger.warning("Groq API key not provided or invalid format")
    except Exception as e:
        logger.error(f"Failed to initialize Groq API: {str(e)}")

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    """
    Return the appropriate Gemini model name based on the task type
    
    Parameters:
    task_type: One of 'chat', 'image', 'audio', 'video', 'document'
    
    Returns:
    String with the model name to use
    """
    # For multimedia tasks, use Gemini 2.0 flash which has multimodal capabilities
    if task_type in ["image", "audio", "video"]:
        return "gemini-2.0-flash"
    # For document analysis requiring more reasoning
    elif task_type == "document":
        return "gemini-2.0-flash"
    # Default chat model
    else:
        return "gemini-2.0-flash"

# Function to check if Gemini API is properly set up for multimedia
def check_gemini_multimodal_support():
    """Verify if the current Gemini setup supports multimodal inputs"""
    if not use_gemini:
        return False
        
    try:
        available_models = genai.list_models()
        for model in available_models:
            if "gemini-2.0" in model.name and "generateContent" in str(model.supported_generation_methods):
                # Check if model supports multimodal inputs
                if any(input_type for input_type in ["image", "video", "audio"] if input_type in str(model)):
                    return True
        return False
    except Exception as e:
        logger.error(f"Error checking multimodal support: {str(e)}")
        return False

# Function to generate content with Gemini API
def generate_content(prompt, model_name="gemini-2.0-flash", image_data=None, audio_data=None, video_data=None, temperature=0.7):
    """Generate content with error handling for multimedia inputs"""
    if not use_gemini:
        return "Gemini API is not available. Please install the google-generativeai package and set your API key."
    
    try:
        # Generation config
        generation_config = {
            "temperature": temperature,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
        
        # Safety settings
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        
        # Create model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Prepare content parts list
        content_parts = [{"text": prompt}]
        
        # Add multimedia if provided
        if image_data:
            # Encode image
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg", 
                    "data": encoded_image
                }
            })
        
        if audio_data:
            # Determine MIME type based on file extension
            mime_type = "audio/mpeg"  # Default
            if hasattr(audio_data, 'name'):
                if audio_data.name.lower().endswith('.wav'):
                    mime_type = "audio/wav"
                elif audio_data.name.lower().endswith('.mp3'):
                    mime_type = "audio/mpeg"
                elif audio_data.name.lower().endswith('.m4a'):
                    mime_type = "audio/mp4"
            
            # Encode audio
            encoded_audio = base64.b64encode(audio_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": mime_type, 
                    "data": encoded_audio
                }
            })
        
        if video_data:
            # Determine MIME type based on file extension
            mime_type = "video/mp4"  # Default
            if hasattr(video_data, 'name'):
                if video_data.name.lower().endswith('.mp4'):
                    mime_type = "video/mp4"
                elif video_data.name.lower().endswith('.webm'):
                    mime_type = "video/webm"
                elif video_data.name.lower().endswith('.mov'):
                    mime_type = "video/quicktime"
            
            # Encode video
            encoded_video = base64.b64encode(video_data).decode('utf-8')
            content_parts.append({
                "inline_data": {
                    "mime_type": mime_type, 
                    "data": encoded_video
                }
            })
        
        # Generate content with all parts
        response = model.generate_content(content_parts)
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return f"Sorry, I encountered an error with Gemini API: {str(e)}"

# Function to generate content with DeepSeek model via Groq API for enhanced reasoning
def generate_content_with_deepseek(prompt, temperature=0.6, max_tokens=4096):
    """Generate content using DeepSeek R1 Distill Qwen 32B model through Groq API with streaming"""
    if not use_groq:
        return "Groq API is not available. Please install the groq package and set your API key."
    
    try:
        # Validate API key format first
        if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
            return "Invalid Groq API key. Please provide a valid API key."
            
        full_response = ""
        
        # Create completion with streaming using DeepSeek model
        completion = groq_client.chat.completions.create(
            model="deepseek-r1-distill-qwen-32b",  # Using DeepSeek model with strong reasoning
            messages=[
                {"role": "system", "content": "You are an expert educational content creator with advanced reasoning abilities. You provide detailed, thoughtful responses that show your step-by-step thinking process."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            stream=True,
            stop=None,
        )
        
        # Process streaming response
        for chunk in completion:
            if chunk.choices and chunk.choices[0].delta.content:
                chunk_content = chunk.choices[0].delta.content
                full_response += chunk_content
                
        return full_response
    
    except Exception as e:
        logger.error(f"DeepSeek API error: {str(e)}")
        return f"Sorry, I encountered an error with the DeepSeek model: {str(e)}"

# Fallback text generation for when APIs are not available
def generate_text_fallback(prompt):
    """Provide a basic response when APIs are not available"""
    return f"I would respond to: '{prompt}' but API access is currently unavailable. Please ensure you have installed the required packages and provided API keys."

# Class for Educational Content Analysis
class EducationalContentAnalyzer:
    def __init__(self):
        if use_gemini:
            # Using the already configured Gemini client
            self.model_available = True
        else:
            self.model_available = False
            logger.warning("Gemini API not available for Content Analysis")
    
    def analyze_video_content(self, video_file, context_info=None):
        """
        Analyze video for educational content insights
        
        Parameters:
        video_file: Streamlit UploadedFile object
        context_info: Dictionary with analysis context information
        
        Returns:
        List of string analysis results
        """
        if not self.model_available:
            return ["Gemini API not available. Cannot perform video analysis."]
        
        try:
            # Prepare context string based on provided info
            context_str = ""
            focus_str = ""
            thoroughness = "standard"
            
            if context_info:
                if "contexts" in context_info and context_info["contexts"]:
                    context_str = ", ".join(context_info["contexts"])
                if "focus_areas" in context_info and context_info["focus_areas"]:
                    focus_str = ", ".join(context_info["focus_areas"])
                if "thoroughness" in context_info:
                    thoroughness = context_info["thoroughness"].lower()
            
            # Get video metadata
            video_name = video_file.name
            video_type = video_file.type
            video_size = len(video_file.getvalue()) / (1024 * 1024)  # Size in MB
            
            # Adjust detail level based on thoroughness
            detail_level = {
                "basic": "Provide a brief overview of the key educational concepts.",
                "standard": "Provide a balanced analysis with moderate detail on educational content.",
                "detailed": "Provide an in-depth, comprehensive analysis with detailed explanations of all educational concepts observed in the video."
            }.get(thoroughness, "Provide a balanced analysis with moderate detail.")
            
            # Create a detailed prompt for video analysis
            video_prompt = f"""
            Analyze this educational video file ({video_name}, {video_type}, {video_size:.2f} MB) for educational content and teaching strategies.
            
            Educational Context: {context_str or "General educational setting"}
            Analysis Focus Areas: {focus_str or "General educational content and pedagogy"}
            
            Focus your analysis on:
            • Key educational concepts presented
            • Teaching methodologies demonstrated
            • Learning objectives covered
            • Student engagement strategies
            • Visual and auditory teaching techniques
            • Sequencing and pacing of content
            • Examples and illustrations used
            • Instructional clarity and effectiveness
            
            {detail_level}
            
            Provide a comprehensive educational assessment including:
            1. Main educational concepts identified
            2. Teaching strategies observed
            3. Suggestions for enhancing the educational content
            4. How the content connects to broader learning objectives
            5. Summary of key educational takeaways
            
            Format your response using markdown for readability.
            """
            
            # Generate response using Gemini with appropriate model for video
            response = generate_content(
                prompt=video_prompt,
                model_name="gemini-2.0-flash",
                video_data=video_file.getvalue(),
                temperature=0.3
            )
            
            return [response]
            
        except Exception as e:
            logger.error(f"Error in video analysis: {e}")
            return [f"Error in video analysis: {str(e)}"]

    def analyze_audio_content(self, audio_file, context_info=None):
        """
        Analyze audio for educational content insights
        
        Parameters:
        audio_file: Streamlit UploadedFile object
        context_info: Dictionary with analysis context information
        
        Returns:
        List of string analysis results
        """
        if not self.model_available:
            return ["Gemini API not available. Cannot perform audio analysis."]
        
        try:
            # Prepare context string based on provided info
            context_str = ""
            focus_str = ""
            thoroughness = "standard"
            
            if context_info:
                if "contexts" in context_info and context_info["contexts"]:
                    context_str = ", ".join(context_info["contexts"])
                if "focus_areas" in context_info and context_info["focus_areas"]:
                    focus_str = ", ".join(context_info["focus_areas"])
                if "thoroughness" in context_info:
                    thoroughness = context_info["thoroughness"].lower()
            
            # Get audio metadata
            audio_name = audio_file.name
            audio_type = audio_file.type
            audio_size = len(audio_file.getvalue()) / (1024 * 1024)  # Size in MB
            
            # Adjust detail level based on thoroughness
            detail_level = {
                "basic": "Provide a brief overview of the key educational concepts.",
                "standard": "Provide a balanced analysis with moderate detail on educational content.",
                "detailed": "Provide an in-depth, comprehensive analysis with detailed explanations of all educational concepts in the audio."
            }.get(thoroughness, "Provide a balanced analysis with moderate detail.")
            
            # Create a detailed prompt for audio analysis
            audio_prompt = f"""
            Analyze this educational audio file ({audio_name}, {audio_type}, {audio_size:.2f} MB) for educational content and teaching strategies.
            
            Educational Context: {context_str or "General educational setting"}
            Analysis Focus Areas: {focus_str or "General educational content and pedagogy"}
            
            Focus your analysis on:
            • Key educational concepts presented
            • Verbal teaching techniques
            • Clarity of explanations
            • Questioning strategies used
            • Pacing and structure of the lesson
            • Verbal engagement techniques
            • Use of examples and analogies
            • Content organization and flow
            
            {detail_level}
            
            Provide a detailed educational analysis of:
            1. Main educational concepts identified
            2. Verbal teaching strategies observed
            3. Suggestions for enhancing the audio instruction
            4. How the content connects to broader learning objectives
            5. Summary of key educational takeaways
            
            Format your response using markdown for readability.
            """
            
            # Generate response using Gemini with appropriate model for audio
            response = generate_content(
                prompt=audio_prompt,
                model_name="gemini-2.0-flash",
                audio_data=audio_file.getvalue(),
                temperature=0.3
            )
            
            return [response]
        
        except Exception as e:
            logger.error(f"Error in audio analysis: {e}")
            return [f"Error in audio analysis: {str(e)}"]

    def analyze_content(self, video_file, audio_file, context_info=None):
        """
        Process both video and audio files with contextual information and return analysis results
        
        Parameters:
        video_file: Streamlit UploadedFile object for video or None
        audio_file: Streamlit UploadedFile object for audio or None
        context_info: Dictionary with keys 'contexts', 'focus_areas', and 'thoroughness'
        
        Returns:
        Dictionary with analysis results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "video_analysis": None,
            "audio_analysis": None
        }

        if video_file:
            results["video_analysis"] = self.analyze_video_content(video_file, context_info)

        if audio_file:
            results["audio_analysis"] = self.analyze_audio_content(audio_file, context_info)

        return results

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Learning Assistant"

if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm your AI learning companion. What would you like to learn about today?"}
    ]

if "reasoning_messages" not in st.session_state:
    st.session_state.reasoning_messages = [
        {"role": "assistant", "content": "👋 Welcome to the DeepSeek Reasoning Assistant! I use advanced reasoning to create educational content. What topic would you like me to explore with in-depth reasoning?"}
    ]

# Header
st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
st.markdown('<div class="edu-subheader">Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)

# Display welcome screen on first visit
if st.session_state.first_visit:
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
                <h3 style="color: #d85b31;">🧠 Reasoning Assistant</h3>
                <p>Create educational content with deep reasoning capabilities using advanced DeepSeek AI model.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.rerun()

# Display API status
with st.sidebar:
    st.header("API Status")
    
    if use_gemini:
        st.success("✅ Google Gemini API: Connected")
    else:
        st.error("❌ Google Gemini API: Not Available")
        st.info("To use Gemini features, install the google-generativeai package and set your API key.")
        
    if use_groq:
        st.success("✅ Groq API: Connected")
        st.success("✅ DeepSeek R1 Model: Available")
    else:
        st.error("❌ Groq API: Not Available")
        st.info("To use Groq and DeepSeek features, install the groq package and set your API key.")
    
    # Add setup instructions
    with st.expander("Setup Instructions"):
        st.markdown("""
        ### Setting Up API Access
        
        1. **Install Required Packages**:
           ```
           pip install streamlit Pillow PyPDF2 google-generativeai groq
           ```
           
        2. **Set API Keys as Environment Variables**:
           - For Gemini: `GEMINI_API_KEY`
           - For Groq: `GROQ_API_KEY`
        """)

# Define tab names and create tabs
tab_names = ["Learning Assistant", "Document Analysis", "Visual Learning", "DeepSeek Reasoning", "Quiz Generator", "Educational Content Analysis"]
selected_tab = st.tabs(tab_names)

# Learning Assistant tab
with selected_tab[0]:
    if st.session_state.current_mode != "Learning Assistant":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Learning Assistant"
    
    st.markdown("### Your AI Learning Companion")
    st.markdown("Ask any question about any subject, request explanations, or get help with homework")
    
    # Configure learning settings in an expandable section
    with st.expander("Learning Settings", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            learning_level = st.selectbox("Learning Level:", 
                                        ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"])
            learning_style = st.selectbox("Learning Style:", 
                                        ["Visual", "Textual", "Interactive", "Example-based", "Socratic"])
        
        with col2:
            memory_option = st.checkbox("Enable Chat Memory", value=True, 
                                     help="When enabled, the AI will remember previous exchanges in this conversation")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.tutor_messages:
            if message["role"] == "user":
                st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background-color: #e6f3ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>EduGenius:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    # Chat input area with a more modern design
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area("Your question:", height=80, key="tutor_input",
                                placeholder="Type your question here... (e.g., Explain quantum entanglement in simple terms)")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button("Send", use_container_width=True, key="tutor_submit")
        
        # Add multimedia upload option
        upload_option = st.selectbox("", ["Add Media", "Image"], key="upload_selector")
    
    # Handle file uploads
    uploaded_file = None
    if upload_option != "Add Media":
        if upload_option == "Image":
            uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"], key="chat_image_upload")
        
        if uploaded_file is not None:
            # Display information about the uploaded file
            st.success(f"File '{uploaded_file.name}' uploaded successfully! ({uploaded_file.type})")
            # Store the file reference in the session state for later use
            st.session_state.current_upload = {
                "file": uploaded_file,
                "type": upload_option,
                "name": uploaded_file.name
            }
            
    # Processing user input
    if submit_button and user_input:
        # Add user message to chat
        st.session_state.tutor_messages.append({"role": "user", "content": user_input})
        
        # Create system context based on selected options
        system_context = f"You are EduGenius, an educational AI tutor. Adapt your explanation for {learning_level} level students. Use a {learning_style} learning style in your response."
        
        # Create conversation history for context
        conversation_history = ""
        if memory_option and len(st.session_state.tutor_messages) > 1:
            for msg in st.session_state.tutor_messages[:-1]:  # Exclude the current message
                role = "User" if msg["role"] == "user" else "EduGenius"
                conversation_history += f"{role}: {msg['content']}\n\n"
        
            try:
                # Determine if we have multimedia
                has_multimedia = False
                media_bytes = None
                
                if hasattr(st.session_state, 'current_upload') and st.session_state.current_upload is not None:
                    has_multimedia = True
                    media_bytes = st.session_state.current_upload["file"].getvalue()
                
                # Create prompt with system context and conversation history
                prompt = f"{system_context}\n\nConversation history:\n{conversation_history}\n\nCurrent question: {user_input}"
                
                if has_multimedia:
                    media_type = st.session_state.current_upload["type"].lower()
                    prompt += f"\n\nNote: The student has also uploaded a {media_type} file named '{st.session_state.current_upload['name']}'. Please incorporate this into your response if relevant."
                
                if use_gemini:
                    # Select appropriate model
                    model_name = get_model_name("image" if has_multimedia else "chat")
                    
                    # Generate response
                    response_text = generate_content(
                        prompt=prompt,
                        model_name=model_name,
                        image_data=media_bytes if has_multimedia else None,
                        temperature=0.7
                    )
                else:
                    # Use fallback
                    response_text = generate_text_fallback(prompt)
                
                # Add AI response to chat
                st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                
                # Clear the input area (using proper Streamlit session state method)
                st.session_state["tutor_input"] = ""
                
                # Update display
                st.rerun()
            
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.tutor_messages.append({"role": "assistant", "content": error_message})
                st.rerun()

# Document Analysis tab
with selected_tab[1]:
    if st.session_state.current_mode != "Document Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Document Analysis"
    
    st.markdown("### AI-Powered Document Analysis")
    st.markdown("Upload study materials, textbooks, or notes for AI analysis and insights")
    
    # Use Gemini for document analysis
    if not use_gemini:
        st.warning("Gemini API is not available. Please install the google-generativeai package and provide your API key.")
    
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"])
    
    # Add manual text input option as a fallback
    manual_text_input = st.text_area(
        "Or paste document content here:",
        height=200, 
        placeholder="Paste the content of your document here if file upload doesn't work properly..."
    )
    
    if uploaded_file is not None or manual_text_input:
        analysis_type = st.multiselect("Select analysis types:", 
                                      ["Key Concepts Extraction", "Summary Generation", 
                                       "Difficulty Assessment", "Concept Relations", 
                                       "Generate Study Questions"])
        
        if st.button("Analyze Document", use_container_width=True):
            with st.spinner("Analyzing document..."):
                try:
                    file_content = ""
                    file_name = "pasted text"
                    
                    if uploaded_file is not None:
                        file_name = uploaded_file.name
                        # Get file content as bytes
                        file_bytes = uploaded_file.getvalue()
                        
                        # Process based on file type
                        if uploaded_file.type == "text/plain":
                            # For text files
                            file_content = file_bytes.decode('utf-8')
                        elif uploaded_file.name.lower().endswith('.pdf'):
                            # For PDF files
                            try:
                                pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
                                for page in pdf_reader.pages:
                                    extracted_text = page.extract_text()
                                    if extracted_text:  # Only add if text was actually extracted
                                        file_content += extracted_text + "\n"
                                
                                if not file_content.strip():
                                    st.warning("The PDF appears to be image-based or has no extractable text.")
                                    file_content = f"[Image-based PDF: {uploaded_file.name}]"
                            except Exception as pdf_error:
                                st.error(f"Error extracting PDF content: {str(pdf_error)}")
                                file_content = f"[Unable to extract content from {uploaded_file.name}]"
                        else:
                            # For other file types
                            file_content = f"[Content of {uploaded_file.name} - {uploaded_file.type}]"
                    elif manual_text_input:
                        # Use the pasted text instead
                        file_content = manual_text_input
                    
                    # If the file content is large, trim it
                    if len(file_content) > 10000:
                        file_content = file_content[:10000] + "... [content truncated due to size]"
                    
                    # Create prompt for document analysis
                    analysis_prompt = f"I'm analyzing document: '{file_name}'. "
                    analysis_prompt += f"Please perform the following analyses: {', '.join(analysis_type)}. "
                    analysis_prompt += "Here's the document content: " + file_content
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Please analyze my document '{file_name}' for: {', '.join(analysis_type)}"})
                    
                    # Generate response using Gemini for document analysis
                    if use_gemini:
                        with st.status("Processing with Gemini..."):
                            response_text = generate_content(
                                prompt=analysis_prompt,
                                model_name=get_model_name("document"),
                                temperature=0.3
                            )
                    else:
                        # Use fallback
                        response_text = generate_text_fallback(analysis_prompt)
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    st.error(f"Error analyzing document: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

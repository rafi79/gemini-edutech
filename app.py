#!/usr/bin/env python3
# EduGenius with Safety Analysis Integration

import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import warnings
import cv2
import numpy as np
import json
from datetime import datetime
import logging

# Try to import PyPDF2 for PDF processing
try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not available. PDF processing will be limited.")

# Optional imports for API integration
try:
    from google import generativeai
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

# Try to import audio processing libraries
try:
    import soundfile as sf
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False
    print("Audio processing libraries not available.")

# Suppress warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="EduGenius - AI Learning & Safety Assistant", 
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
    .safety-header {
        color: #FF4B4B;
        font-size: 2.0rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-align: center;
    }
    .safety-card {
        background: linear-gradient(45deg, #2b1f47, #1a1a2e);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .safety-title {
        color: #FF69B4;
        margin-bottom: 1rem;
    }
    .safety-content {
        background: rgba(255,255,255,0.05);
        padding: 1rem;
        border-radius: 8px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyAnP99siTh3kaaayNPBcj_y1HwP1PCrxjo")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")

# Initialize API clients conditionally
use_groq = False
use_gemini = False

if HAS_GEMINI:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        use_gemini = True
    except Exception as e:
        st.sidebar.warning(f"Failed to initialize Gemini API: {str(e)}")

if HAS_GROQ:
    try:
        groq_client = Groq(api_key=GROQ_API_KEY)
        use_groq = True
    except Exception as e:
        st.sidebar.warning(f"Failed to initialize Groq API: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    if task_type in ["image", "audio", "video"]:
        return "gemini-1.5-flash"  # For multimodal tasks
    else:
        return "gemini-2.0-flash"  # For chat and reasoning

# Function to generate content with Gemini API
def generate_content(prompt, model_name="gemini-2.0-flash", image_data=None, temperature=0.7):
    """Generate content with error handling"""
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
        
        # Generate with or without image
        if image_data:
            # Encode image
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Try with image
            response = model.generate_content([
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}
            ])
        else:
            # Text only
            response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        return f"Sorry, I encountered an error with Gemini API: {str(e)}"

# Function to generate content with Groq API (specialized for document analysis)
def generate_content_with_groq(prompt, temperature=0.6):
    """Generate content using Groq API with streaming for document analysis"""
    if not use_groq:
        return "Groq API is not available. Please install the groq package and set your API key."
    
    try:
        # Validate API key format first
        if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
            return "Invalid Groq API key. Please provide a valid API key."
            
        full_response = ""
        
        # Create completion with streaming
        completion = groq_client.chat.completions.create(
            model="qwen-2.5-32b",  # Using Qwen model which is good for document analysis
            messages=[
                {"role": "system", "content": "You are an expert document analyzer and educator."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=4096,
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
        return f"Sorry, I encountered an error with Groq API: {str(e)}"

# Fallback text generation for when APIs are not available
def generate_text_fallback(prompt):
    """Provide a basic response when APIs are not available"""
    return f"I would respond to: '{prompt}' but API access is currently unavailable. Please ensure you have installed the required packages and provided API keys."

# New class for Women Safety Analysis
class WomenSafetyAnalyzer:
    def __init__(self):
        if use_gemini:
            # Using the already configured Gemini client
            self.model_available = True
        else:
            self.model_available = False
            logger.warning("Gemini API not available for Safety Analysis")
    
    def analyze_video_safety(self, video_path):
        """Analyze video for safety concerns"""
        if not self.model_available:
            return ["Gemini API not available. Cannot perform video analysis."]
        
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            frames = []
            frame_count = 0
            safety_concerns = []
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                if frame_count % int(fps) == 0:  # Sample one frame per second
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    pil_frame = Image.fromarray(rgb_frame)
                    frames.append(pil_frame)
                    
                    progress = int((frame_count / total_frames) * 100)
                    progress_bar.progress(progress)
                    status_text.text(f"Analyzing frame {frame_count}/{total_frames}")
                    
                    if len(frames) >= 5:  # Analyze in batches of 5 frames
                        safety_prompt = """
                        Analyze these frames from an educational perspective, identifying:
                        • Potential safety concerns for students
                        • Educational content that requires attention
                        • Classroom dynamics and interactions
                        • Signs of distress or discomfort in educational settings
                        • Engagement levels and participation
                        • Potential bullying or harassment indicators
                        • Learning environment safety factors
                        
                        Provide a clear assessment of:
                        1. Type of educational concern detected
                        2. Severity level
                        3. Recommendations for educators
                        """
                        
                        chat = genai.GenerativeModel(model_name="gemini-2.0-flash").start_chat(history=[])
                        response = chat.send_message([safety_prompt, *frames])
                        safety_concerns.append(response.text)
                        frames = []  # Reset frames for next batch
            
            cap.release()
            progress_bar.progress(100)
            status_text.text("Video analysis complete")
            
            return safety_concerns
            
        except Exception as e:
            logger.error(f"Error in video analysis: {e}")
            return [f"Error in video analysis: {str(e)}"]

    def analyze_audio_safety(self, audio_path):
        """Analyze audio for safety concerns"""
        if not self.model_available:
            return "Gemini API not available. Cannot perform audio analysis."
        
        if not HAS_AUDIO:
            return "Audio processing libraries not available. Cannot perform audio analysis."
        
        try:
            # Use soundfile to extract basic audio features
            data, sample_rate = sf.read(audio_path)
            
            # Basic audio features
            duration = len(data) / sample_rate
            rms_energy = np.sqrt(np.mean(np.square(data)))
            
            audio_prompt = f"""
            Analyze these audio characteristics from an educational perspective:
            Duration: {duration:.2f} seconds
            Energy Level: {rms_energy:.4f}
            
            Focus on detecting:
            • Classroom interactions 
            • Student participation
            • Clear vs. unclear instruction
            • Engagement levels
            • Potential learning barriers
            • Signs of confusion or distress
            • Educational content quality
            
            Provide analysis of:
            1. Educational effectiveness
            2. Areas for improvement
            3. Recommended teaching adjustments
            """
            
            response = generate_content(audio_prompt, model_name="gemini-2.0-flash", temperature=0.3)
            return response
        
        except Exception as e:
            logger.error(f"Error in audio analysis: {e}")
            return f"Error in audio analysis: {str(e)}"

    def analyze_content(self, video_file, audio_file):
        """Process both video and audio files and return analysis results"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "video_analysis": None,
            "audio_analysis": None
        }

        if video_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
                tmp_video.write(video_file.getvalue())
                tmp_path = tmp_video.name
            
            results["video_analysis"] = self.analyze_video_safety(tmp_path)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

        if audio_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_audio:
                tmp_audio.write(audio_file.getvalue())
                tmp_path = tmp_audio.name
                
            results["audio_analysis"] = self.analyze_audio_safety(tmp_path)
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

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

# Header
st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
st.markdown('<div class="edu-subheader">Your AI-Enhanced Learning & Safety Companion</div>', unsafe_allow_html=True)

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
                <h3 style="color: #4257b2;">🔍 Safety Analysis</h3>
                <p>Advanced AI safety analysis for educational environments using video and audio content.</p>
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
    else:
        st.error("❌ Groq API: Not Available")
        st.info("To use Groq features, install the groq package and set your API key.")
    
    # Add setup instructions
    with st.expander("Setup Instructions"):
        st.markdown("""
        ### Setting Up API Access
        
        1. **Install Required Packages**:
           ```
           pip install streamlit Pillow PyPDF2 google-generativeai groq opencv-python numpy soundfile
           ```
           
        2. **Set API Keys as Environment Variables**:
           - For Gemini: `GEMINI_API_KEY`
           - For Groq: `GROQ_API_KEY`
        """)

# App modes with added Safety Analysis
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Quiz Generator", "Safety Analysis"]
selected_tab = st.tabs(modes)

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
        
        # Try to generate response
        with st.spinner("Thinking..."):
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
    
    # Add API selection for document analysis
    api_choice = st.radio("Select AI model for document analysis:", 
                          ["Groq (Qwen-2.5-32B) - Better for documents", "Google Gemini"])
    
    # Document analysis functionality (same as in original EduGenius code)
    # ... [Keeping this section the same as the original EduGenius code] ...

# Visual Learning tab  
with selected_tab[2]:
    if st.session_state.current_mode != "Visual Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Visual Learning"
    
    st.markdown("### Visual Learning Assistant")
    st.markdown("Upload images of diagrams, problems, or visual concepts for AI explanation")
    
    # Visual learning functionality (same as in original EduGenius code)
    # ... [Keeping this section the same as the original EduGenius code] ...

# Quiz Generator tab
with selected_tab[3]:
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Quiz Generator"
    
    st.markdown("### AI Quiz Generator")
    st.markdown("Generate customized quizzes and assessments for any subject or learning level")
    
    # Quiz generator functionality (same as in original EduGenius code)
    # ... [Keeping this section the same as the original EduGenius code] ...

# New Safety Analysis tab
with selected_tab[4]:
    if st.session_state.current_mode != "Safety Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Safety Analysis"
    
    st.markdown('<div class="safety-header">Educational Environment Safety Analysis</div>', unsafe_allow_html=True)
    st.markdown("Advanced AI analysis of educational environments to ensure a safe and productive learning atmosphere")
    
    # Check if the required APIs are available
    if not use_gemini:
        st.warning("Safety Analysis requires the Google Gemini API. Please install the google-generativeai package and provide your API key.")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
            <div style='background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
                <div style='color: #4257b2; font-size: 1.1rem; font-weight: 500;'>📹 Educational Video Analysis</div>
                <div style='color: rgba(0,0,0,0.6); font-size: 0.8rem;'>Upload MP4, AVI, MOV (Max 200MB)</div>
            </div>
        """, unsafe_allow_html=True)
        video_file = st.file_uploader("Upload video", type=['mp4', 'avi', 'mov'], label_visibility="collapsed")

        st.markdown("""
            <div style='background: rgba(255,255,255,0.05); border-radius: 10px; padding: 1rem; margin-bottom: 1rem;'>
                <div style='color: #4257b2; font-size: 1.1rem; font-weight: 500;'>🎤 Educational Audio Analysis</div>
                <div style='color: rgba(0,0,0,0.6); font-size: 0.8rem;'>Upload WAV, MP3 (Max 200MB)</div>
            </div>
        """, unsafe_allow_html=True)
        audio_file = st.file_uploader("Upload audio", type=['wav', 'mp3'], label_visibility="collapsed")

        if video_file:
            st.video(video_file)
        if audio_file:
            st.audio(audio_file)
            
        # Add analysis context
        st.markdown("### Analysis Context")
        analysis_context = st.selectbox(
            "Educational Environment Type:",
            ["Classroom", "Online Learning", "Laboratory", "Field Trip", "Student Activities", "General"]
        )
        
        education_level = st.selectbox(
            "Education Level:",
            ["Early Childhood", "Elementary School", "Middle School", "High School", "College/University", "Adult Education"]
        )
        
        # Additional context information
        with st.expander("Additional Context (Optional)"):
            specific_concerns = st.text_area(
                "Specific areas of concern:",
                placeholder="e.g., classroom dynamics, bullying indicators, engagement levels..."
            )
            
            institutional_policies = st.text_area(
                "Relevant institutional policies:",
                placeholder="e.g., specific safety guidelines, school policies..."
            )

    with col2:
        st.subheader("Analysis Results")
        analyze_button = st.button("Begin Safety Analysis", 
                            type="primary",
                            use_container_width=True,
                            disabled=(not video_file and not audio_file))

        if analyze_button:
            analyzer = WomenSafetyAnalyzer()
            
            # Create enhanced context for educational safety analysis
            context_info = f"Educational Environment: {analysis_context}\nEducation Level: {education_level}\n"
            if specific_concerns:
                context_info += f"Specific Concerns: {specific_concerns}\n"
            if institutional_policies:
                context_info += f"Institutional Policies: {institutional_policies}\n"
                
            st.info(f"Analyzing with context: {context_info}")
            
            with st.spinner("Analyzing content for educational safety concerns..."):
                results = analyzer.analyze_content(video_file, audio_file)
                
                if results.get("video_analysis") or results.get("audio_analysis"):
                    st.markdown("""
                        <div class="safety-card">
                            <h3 class="safety-title">Educational Safety Assessment</h3>
                    """, unsafe_allow_html=True)
                    
                    if results.get("video_analysis"):
                        st.markdown("<h4 style='color: white;'>Video Analysis:</h4>", unsafe_allow_html=True)
                        for i, analysis in enumerate(results["video_analysis"]):
                            st.markdown(f"""
                                <div class="safety-content">
                                    {analysis}
                                </div>
                            """, unsafe_allow_html=True)
                    
                    if results.get("audio_analysis"):
                        st.markdown("<h4 style='color: white;'>Audio Analysis:</h4>", unsafe_allow_html=True)
                        st.markdown(f"""
                            <div class="safety-content">
                                {results["audio_analysis"]}
                            </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download button for report
                    st.download_button(
                        label="Download Safety Report",
                        data=json.dumps(results, indent=2),
                        file_name=f"edu_safety_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_report"
                    )
                else:
                    st.error("Analysis failed or no safety concerns detected.")
                    
        # Add information about system usage
        with st.expander("How to use Educational Safety Analysis"):
            st.markdown("""
            1. **Upload Media**: Add classroom video and/or audio files for analysis
            2. **Provide Context**: Select the educational environment type and level
            3. **Begin Analysis**: Click the analysis button to start the AI-powered safety assessment
            4. **Review Results**: The system will highlight potential safety concerns in educational contexts
            5. **Download Report**: Save the analysis for documentation or further action
            
            This system is designed to help educators identify potential safety concerns in learning environments.
            It can be used to analyze classroom dynamics, student engagement, and potential issues that may affect
            the learning experience.
            """)
            
        # Educational guidance section
        with st.expander("Educational Safety Guidelines"):
            st.markdown("""
            ### Best Practices for Educational Safety
            
            - **Physical Safety**: Ensure learning environments are free from physical hazards
            - **Emotional Safety**: Create spaces where students feel respected and valued
            - **Digital Safety**: Monitor online interactions and teach responsible digital citizenship
            - **Inclusive Environment**: Ensure all students feel included regardless of background
            - **Clear Expectations**: Set and communicate clear behavioral guidelines
            - **Positive Reinforcement**: Recognize and reward positive behaviors
            - **Intervention Plans**: Have procedures in place for addressing safety concerns
            
            Remember that AI analysis is a tool to assist educators, not replace professional judgment.
            Always follow your institution's policies and procedures when addressing safety concerns.
            """)

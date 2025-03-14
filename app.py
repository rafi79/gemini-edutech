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
    .content-card {
        background: linear-gradient(45deg, #f0fff5, #e8ffee);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .content-title {
        color: #2a9d8f;
        margin-bottom: 1rem;
    }
    .content-preview {
        background: rgba(255,255,255,0.7);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDLPkZIKqjPzdawHnWjEFnX3h-pkML0vm0")

# Initialize API clients conditionally
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

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    """
    Return the appropriate Gemini model name based on the task type
    
    Parameters:
    task_type: One of 'chat', 'image', 'audio', 'video', 'document'
    
    Returns:
    String with the model name to use
    """
    # For all tasks, use Gemini 2.0 flash which has multimodal capabilities
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

# Class for Educational Content Creation
class EducationalContentCreator:
    def __init__(self):
        if use_gemini:
            self.model_available = True
        else:
            self.model_available = False
            logger.warning("Gemini API not available for Content Creation")
    
    def create_lesson_plan(self, topic, grade_level, duration, learning_objectives=None, teaching_strategies=None):
        """
        Create a comprehensive lesson plan for the given topic and parameters
        
        Parameters:
        topic: String with the main topic for the lesson
        grade_level: String with the target grade level
        duration: String with lesson duration (e.g., "45 minutes", "1 hour")
        learning_objectives: List of specific learning objectives
        teaching_strategies: List of preferred teaching strategies
        
        Returns:
        String with the generated lesson plan
        """
        if not self.model_available:
            return "Gemini API not available. Cannot create lesson plan."
        
        try:
            # Format learning objectives and teaching strategies
            objectives_str = "\n- " + "\n- ".join(learning_objectives) if learning_objectives else "Not specified"
            strategies_str = "\n- " + "\n- ".join(teaching_strategies) if teaching_strategies else "Not specified"
            
            # Create prompt for lesson plan generation
            prompt = f"""
            Create a detailed, professional lesson plan for educators on the topic of '{topic}'.
            
            Lesson Parameters:
            - Grade Level: {grade_level}
            - Duration: {duration}
            - Learning Objectives: {objectives_str}
            - Preferred Teaching Strategies: {strategies_str}
            
            Please include the following components in your lesson plan:
            
            1. Lesson Overview
               - Brief description of the lesson
               - Key concepts to be covered
               - How this lesson connects to broader curriculum
            
            2. Learning Objectives
               - Clear, measurable learning outcomes
               - Skills students will develop
            
            3. Required Materials
               - List all materials needed
               - Include any technology requirements
               - Note any preparation needed before class
            
            4. Lesson Structure
               - Introduction/Hook (5-10 minutes)
               - Main Activities (detailed step-by-step)
               - Guided Practice
               - Independent Practice
               - Closure/Conclusion
            
            5. Differentiation Strategies
               - Accommodations for different learning needs
               - Extension activities for advanced students
               - Support strategies for struggling students
            
            6. Assessment Methods
               - Formative assessment techniques
               - Summative assessment if applicable
               - Success criteria
            
            7. Additional Resources
               - Supplementary materials
               - References and links
            
            Format the lesson plan using markdown for clear organization and readability. Make it comprehensive, practical, and classroom-ready.
            """
            
            # Generate lesson plan content
            response = generate_content(
                prompt=prompt,
                model_name="gemini-2.0-flash",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in lesson plan creation: {e}")
            return f"Error creating lesson plan: {str(e)}"
    
    def create_assessment(self, topic, grade_level, assessment_type, num_questions=10, difficulty_level="medium"):
        """
        Create educational assessments including quizzes, tests, and rubrics
        
        Parameters:
        topic: String with the main topic for assessment
        grade_level: String with the target grade level
        assessment_type: String indicating type (quiz, test, rubric, etc.)
        num_questions: Integer number of questions to generate
        difficulty_level: String indicating difficulty (easy, medium, hard)
        
        Returns:
        String with the generated assessment
        """
        if not self.model_available:
            return "Gemini API not available. Cannot create assessment."
        
        try:
            # Determine question types based on assessment type
            question_types = []
            if assessment_type.lower() in ["quiz", "test", "exam"]:
                question_types = ["Multiple choice", "True/False", "Short answer", "Fill in the blank"]
            elif assessment_type.lower() == "worksheet":
                question_types = ["Short answer", "Problem solving", "Matching", "Calculation"]
            elif assessment_type.lower() == "project":
                question_types = ["Open-ended", "Creative", "Research-based"]
            
            question_types_str = ", ".join(question_types) if question_types else "Various types"
            
            # Create prompt for assessment generation
            prompt = f"""
            Create a {assessment_type} on the topic of '{topic}' for {grade_level} students.
            
            Assessment Parameters:
            - Topic: {topic}
            - Grade Level: {grade_level}
            - Assessment Type: {assessment_type}
            - Number of Questions/Items: {num_questions}
            - Difficulty Level: {difficulty_level}
            - Question Types: {question_types_str}
            
            Please include:
            
            1. Clear instructions for students
            2. Point values for each question/section
            3. A mix of {question_types_str} questions
            4. An answer key or scoring guidelines
            
            The assessment should align with grade-level standards and thoroughly assess understanding of {topic}.
            Format the assessment using markdown for clear organization and readability.
            Include appropriate headers, sections, and formatting to make it classroom-ready.
            """
            
            # Generate assessment content
            response = generate_content(
                prompt=prompt,
                model_name="gemini-2.0-flash",
                temperature=0.3
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in assessment creation: {e}")
            return f"Error creating assessment: {str(e)}"
    
    def create_instructional_materials(self, topic, grade_level, material_type, specific_requirements=None):
        """
        Create supplementary instructional materials like handouts, slide decks, or activity guides
        
        Parameters:
        topic: String with the main topic
        grade_level: String with the target grade level
        material_type: String indicating type (handout, slides, activity)
        specific_requirements: Optional list of specific requirements or elements to include
        
        Returns:
        String with the generated instructional materials
        """
        if not self.model_available:
            return "Gemini API not available. Cannot create instructional materials."
        
        try:
            # Format specific requirements if provided
            requirements_str = "\n- " + "\n- ".join(specific_requirements) if specific_requirements else "Not specified"
            
            # Customize prompt based on material type
            material_specific_guidance = ""
            if material_type.lower() == "handout":
                material_specific_guidance = """
                This educational handout should include:
                - Clear title and sections
                - Key concepts and definitions
                - Visual elements (described in detail for illustration purposes)
                - Practice problems or activities
                - Key takeaways or summary
                """
            elif material_type.lower() in ["slides", "presentation", "slide deck"]:
                material_specific_guidance = """
                This educational slide presentation should include:
                - Title slide
                - Learning objectives slide
                - 7-12 content slides with key points (not paragraphs)
                - Visual elements (described in detail)
                - Interactive elements or discussion questions
                - Summary/conclusion slide
                """
            elif material_type.lower() in ["activity", "activity guide"]:
                material_specific_guidance = """
                This educational activity guide should include:
                - Activity title and overview
                - Learning objectives
                - Materials needed
                - Step-by-step instructions
                - Discussion questions
                - Extension ideas
                - Assessment options
                """
            
            # Create prompt for instructional material generation
            prompt = f"""
            Create a {material_type} on the topic of '{topic}' for {grade_level} students.
            
            Material Parameters:
            - Topic: {topic}
            - Grade Level: {grade_level}
            - Material Type: {material_type}
            - Specific Requirements: {requirements_str}
            
            {material_specific_guidance}
            
            The material should be:
            - Age-appropriate for {grade_level} students
            - Engaging and visually interesting
            - Aligned with educational standards
            - Formatted for easy classroom use
            
            Format your response using markdown for clear organization and readability.
            """
            
            # Generate instructional material content
            response = generate_content(
                prompt=prompt,
                model_name="gemini-2.0-flash",
                temperature=0.4
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in instructional material creation: {e}")
            return f"Error creating instructional material: {str(e)}"

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

if "content_creator_messages" not in st.session_state:
    st.session_state.content_creator_messages = [
        {"role": "assistant", "content": "👋 Welcome to the Educational Content Creator! I can help you create lesson plans, assessments, and other educational materials. What would you like to create today?"}
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
                <h3 style="color: #2a9d8f;">📚 Content Creator</h3>
                <p>Generate lesson plans, assessments, and educational materials using AI to streamline your teaching workflow.</p>
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
    
    # Add setup instructions
    with st.expander("Setup Instructions"):
        st.markdown("""
        ### Setting Up API Access
        
        1. **Install Required Packages**:
           ```
           pip install streamlit Pillow PyPDF2 google-generativeai
           ```
           
        2. **Set API Keys as Environment Variables**:
           - For Gemini: `GEMINI_API_KEY`
        """)

# Define tab names and create tabs
tab_names = ["Learning Assistant", "Document Analysis", "Visual Learning", "Educational Content Creator", "Quiz Generator", "Educational Content Analysis"]
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
        upload_option = st.selectbox("", ["Add Media", "Image", "Audio", "Video"], key="upload_selector")
    
    # Handle file uploads
    uploaded_file = None
    if upload_option != "Add Media":
        if upload_option == "Image":
            uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"], key="chat_image_upload")
        elif upload_option == "Audio":
            uploaded_file = st.file_uploader("Upload audio:", type=["mp3", "wav", "m4a"], key="chat_audio_upload")
        elif upload_option == "Video":
            uploaded_file = st.file_uploader("Upload video:", type=["mp4", "mov", "webm"], key="chat_video_upload")
        
        if uploaded_file is not None:
            # Display information about the uploaded file
            st.success(f"File '{uploaded_file.name}' uploaded successfully! ({uploaded_file.type})")
            
            # Display preview when possible
            if upload_option == "Image":
                st.image(uploaded_file, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)
            elif upload_option == "Audio":
                st.audio(uploaded_file)
            elif upload_option == "Video":
                st.video(uploaded_file)
            
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
                media_type = None
                
                if hasattr(st.session_state, 'current_upload') and st.session_state.current_upload is not None:
                    has_multimedia = True
                    media_bytes = st.session_state.current_upload["file"].getvalue()
                    media_type = st.session_state.current_upload["type"].lower()
                
                # Create prompt with system context and conversation history
                prompt = f"{system_context}\n\nConversation history:\n{conversation_history}\n\nCurrent question: {user_input}"
                
                if has_multimedia:
                    prompt += f"\n\nNote: The student has also uploaded a {media_type} file named '{st.session_state.current_upload['name']}'. Please incorporate this into your response if relevant."
                
                if use_gemini:
                    # Use Gemini 2.0 Flash for all types of content
                    model_name = "gemini-2.0-flash"
                    
                    # Generate response with appropriate multimedia data
                    if has_multimedia:
                        if media_type == "image":
                            response_text = generate_content(
                                prompt=prompt,
                                model_name=model_name,
                                image_data=media_bytes,
                                temperature=0.7
                            )
                        elif media_type == "audio":
                            response_text = generate_content(
                                prompt=prompt,
                                model_name=model_name,
                                audio_data=media_bytes,
                                temperature=0.7
                            )
                        elif media_type == "video":
                            response_text = generate_content(
                                prompt=prompt,
                                model_name=model_name,
                                video_data=media_bytes,
                                temperature=0.7
                            )
                    else:
                        # Text-only response
                        response_text = generate_content(
                            prompt=prompt,
                            model_name=model_name,
                            temperature=0.7
                        )
                else:
                    # Use fallback
                    response_text = generate_text_fallback(prompt)
                
                # Add AI response to chat
                st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                
                # Clear the input area and reset uploaded file (using proper Streamlit session state method)
                st.session_state["tutor_input"] = ""
                if has_multimedia:
                    st.session_state.current_upload = None
                
                # Update display
                st.rerun()
            
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.tutor_messages.append({"role": "assistant", "content": error_message})
                st.rerun()

# Educational Content Creator tab (new tab)
with selected_tab[3]:  # Index 3 corresponds to "Educational Content Creator" in the tab list
    st.markdown("### Educational Content Creator")
    st.markdown("Generate professional-quality lesson plans, assessments, and teaching materials")
    
    # Initialize content creator if needed
    if "content_creator" not in st.session_state:
        st.session_state.content_creator = EducationalContentCreator()
    
    # Create tabs for different content types
    content_tabs = st.tabs(["Lesson Plans", "Assessments", "Instructional Materials"])
    
    # Lesson Plans tab
    with content_tabs[0]:
        st.markdown("#### Create Comprehensive Lesson Plans")
        st.markdown("Generate detailed, standards-aligned lesson plans for any subject and grade level")
        
        col1, col2 = st.columns(2)
        
        with col1:
            lesson_topic = st.text_input("Lesson Topic:", placeholder="e.g., Photosynthesis", key="lesson_topic")
            lesson_grade = st.selectbox("Grade Level:", 
                                     ["K-2", "3-5", "6-8", "9-10", "11-12", "Higher Education"], key="lesson_grade")
            lesson_duration = st.selectbox("Lesson Duration:", 
                                        ["30 minutes", "45 minutes", "60 minutes", "90 minutes", "2 hours"], key="lesson_duration")
        
        with col2:
            lesson_objectives = st.text_area("Learning Objectives (one per line):", 
                                          placeholder="e.g., \nStudents will explain the process of photosynthesis\nStudents will identify key components...", 
                                          height=120, key="lesson_objectives")
            lesson_strategies = st.multiselect("Teaching Strategies:", 
                                           ["Direct Instruction", "Inquiry-based Learning", "Cooperative Learning", 
                                            "Project-based Learning", "Discussion-based", "Visual Learning", 
                                            "Hands-on Activities", "Technology Integration"], key="lesson_strategies")
        
        generate_lesson_plan = st.button("Generate Lesson Plan", key="generate_lesson", use_container_width=True)
        
        if generate_lesson_plan and lesson_topic:
            with st.spinner("Creating your lesson plan..."):
                # Parse objectives into a list
                objectives_list = [obj.strip() for obj in lesson_objectives.split('\n') if obj.strip()]
                
                # Generate lesson plan
                lesson_plan = st.session_state.content_creator.create_lesson_plan(
                    topic=lesson_topic,
                    grade_level=lesson_grade,
                    duration=lesson_duration,
                    learning_objectives=objectives_list,
                    teaching_strategies=lesson_strategies
                )
                
                # Display the lesson plan in a formatted container
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="content-title"><h3>Lesson Plan: {lesson_topic}</h3></div>', unsafe_allow_html=True)
                st.markdown('<div class="content-preview">', unsafe_allow_html=True)
                st.markdown(lesson_plan)
                st.markdown('</div></div>', unsafe_allow_html=True)
                
                # Add download button for the lesson plan
                st.download_button(
                    label="Download Lesson Plan",
                    data=lesson_plan,
                    file_name=f"lesson_plan_{lesson_topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
    
    # Assessments tab
    with content_tabs[1]:
        st.markdown("#### Create Educational Assessments")
        st.markdown("Generate quizzes, tests, worksheets, and other assessment materials")
        
        col1, col2 = st.columns(2)
        
        with col1:
            assessment_topic = st.text_input("Assessment Topic:", placeholder="e.g., Cell Division", key="assessment_topic")
            assessment_grade = st.selectbox("Grade Level:", 
                                         ["K-2", "3-5", "6-8", "9-10", "11-12", "Higher Education"], key="assessment_grade")
            assessment_type = st.selectbox("Assessment Type:", 
                                         ["Quiz", "Test", "Exam", "Worksheet", "Project Rubric", "Lab Assessment"], 
                                         key="assessment_type")
        
        with col2:
            num_questions = st.slider("Number of Questions/Items:", 5, 30, 10, key="num_questions")
            difficulty = st.select_slider("Difficulty Level:", 
                                        options=["Easy", "Medium", "Hard", "Mixed"], value="Medium", key="difficulty")
            include_answers = st.checkbox("Include Answer Key", value=True, key="include_answers")
        
        generate_assessment = st.button("Generate Assessment", key="generate_assessment", use_container_width=True)
        
        if generate_assessment and assessment_topic:
            with st.spinner("Creating your assessment..."):
                # Generate assessment
                assessment = st.session_state.content_creator.create_assessment(
                    topic=assessment_topic,
                    grade_level=assessment_grade,
                    assessment_type=assessment_type,
                    num_questions=num_questions,
                    difficulty_level=difficulty.lower()
                )
                
                # Display the assessment in a formatted container
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="content-title"><h3>{assessment_type}: {assessment_topic}</h3></div>', unsafe_allow_html=True)
                st.markdown('<div class="content-preview">', unsafe_allow_html=True)
                st.markdown(assessment)
                st.markdown('</div></div>', unsafe_allow_html=True)
                
                # Add download button for the assessment
                st.download_button(
                    label=f"Download {assessment_type}",
                    data=assessment,
                    file_name=f"{assessment_type.lower()}_{assessment_topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )
    
    # Instructional Materials tab
    with content_tabs[2]:
        st.markdown("#### Create Instructional Materials")
        st.markdown("Generate handouts, slide decks, activity guides, and other teaching resources")
        
        col1, col2 = st.columns(2)
        
        with col1:
            material_topic = st.text_input("Topic:", placeholder="e.g., The Water Cycle", key="material_topic")
            material_grade = st.selectbox("Grade Level:", 
                                       ["K-2", "3-5", "6-8", "9-10", "11-12", "Higher Education"], key="material_grade")
            material_type = st.selectbox("Material Type:", 
                                       ["Handout", "Slide Deck", "Activity Guide", "Study Guide", "Reference Sheet", "Graphic Organizer"], 
                                       key="material_type")
        
        with col2:
            specific_reqs = st.text_area("Specific Requirements (one per line):", 
                                       placeholder="e.g., \nInclude diagrams\nAdd practice problems\nMake it interactive", 
                                       height=120, key="specific_reqs")
            visual_elements = st.checkbox("Include descriptions of visual elements", value=True, key="visual_elements")
        
        generate_material = st.button("Generate Instructional Material", key="generate_material", use_container_width=True)
        
        if generate_material and material_topic:
            with st.spinner("Creating your instructional material..."):
                # Parse requirements into a list
                requirements_list = [req.strip() for req in specific_reqs.split('\n') if req.strip()]
                if visual_elements:
                    requirements_list.append("Include detailed descriptions of visual elements and diagrams")
                
                # Generate instructional material
                material = st.session_state.content_creator.create_instructional_materials(
                    topic=material_topic,
                    grade_level=material_grade,
                    material_type=material_type,
                    specific_requirements=requirements_list
                )
                
                # Display the material in a formatted container
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="content-title"><h3>{material_type}: {material_topic}</h3></div>', unsafe_allow_html=True)
                st.markdown('<div class="content-preview">', unsafe_allow_html=True)
                st.markdown(material)
                st.markdown('</div></div>', unsafe_allow_html=True)
                
                # Add download button for the material
                st.download_button(
                    label=f"Download {material_type}",
                    data=material,
                    file_name=f"{material_type.lower()}_{material_topic.replace(' ', '_')}.md",
                    mime="text/markdown"
                )

# Add placeholder content for other tabs to maintain compatibility
with selected_tab[1]:  # Document Analysis
    st.markdown("### Document Analysis")
    st.markdown("Upload and analyze educational documents, papers, and text materials")
    # Placeholder for document analysis functionality

with selected_tab[2]:  # Visual Learning
    st.markdown("### Visual Learning")
    st.markdown("Learn through visual explanations and upload images for analysis")
    # Placeholder for visual learning functionality

with selected_tab[4]:  # Quiz Generator
    st.markdown("### Quiz Generator")
    st.markdown("Generate customized quizzes and assessments for any subject")
    # Placeholder for quiz generator functionality

with selected_tab[5]:  # Educational Content Analysis
    st.markdown("### Educational Content Analysis")
    st.markdown("Analyze educational videos and audio for insights and improvement")
    
    st.write("Upload educational content to analyze its educational value and effectiveness")
    
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_video = st.file_uploader("Upload Educational Video:", type=["mp4", "mov", "avi"], key="analysis_video")
    with col2:
        analysis_audio = st.file_uploader("Upload Educational Audio:", type=["mp3", "wav", "m4a"], key="analysis_audio")
    
    # Analysis settings
    with st.expander("Analysis Settings", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            educational_contexts = st.multiselect(
                "Educational Context:",
                ["K-12 Classroom", "Higher Education", "Professional Development", "Special Education", 
                 "Online Learning", "Self-Directed Learning", "Homeschool"],
                key="contexts"
            )
            
        with col2:
            analysis_focus = st.multiselect(
                "Analysis Focus Areas:",
                ["Content Accuracy", "Pedagogical Approaches", "Engagement Techniques", 
                 "Accessibility", "Assessment Strategies", "Visual Design", "Audio Quality"],
                key="focus_areas"
            )
            
        analysis_thoroughness = st.select_slider(
            "Analysis Thoroughness:",
            options=["Basic", "Standard", "Detailed"],
            value="Standard",
            key="thoroughness"
        )
    
    # Analyze button
    analyze_button = st.button("Analyze Educational Content", key="analyze_content", use_container_width=True)
    
    if analyze_button and (analysis_video is not None or analysis_audio is not None):
        with st.spinner("Analyzing content..."):
            # Create context info dictionary
            context_info = {
                "contexts": educational_contexts,
                "focus_areas": analysis_focus,
                "thoroughness": analysis_thoroughness
            }
            
            # Initialize analyzer
            analyzer = EducationalContentAnalyzer()
            
            # Perform analysis
            analysis_results = analyzer.analyze_content(
                video_file=analysis_video,
                audio_file=analysis_audio,
                context_info=context_info
            )
            
            # Display video analysis if available
            if analysis_results["video_analysis"]:
                st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title"><h3>Video Analysis Results</h3></div>', unsafe_allow_html=True)
                st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                st.markdown(analysis_results["video_analysis"][0])
                st.markdown('</div></div>', unsafe_allow_html=True)
            
            # Display audio analysis if available
            if analysis_results["audio_analysis"]:
                st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                st.markdown('<div class="analysis-title"><h3>Audio Analysis Results</h3></div>', unsafe_allow_html=True)
                st.markdown('<div class="analysis-content">', unsafe_allow_html=True)
                st.markdown(analysis_results["audio_analysis"][0])
                st.markdown('</div></div>', unsafe_allow_html=True)

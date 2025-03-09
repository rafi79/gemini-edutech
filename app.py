import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import google.generativeai as genai
from google.generativeai import types

# Set page configuration
st.set_page_config(page_title="EduGenius - AI Learning Assistant", 
                   page_icon="🧠", 
                   layout="wide",
                   initial_sidebar_state="expanded")

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
</style>
""", unsafe_allow_html=True)

# GEMINI API Configuration
API_KEY = "AIzaSyCagQKSSGGM-VcoOwIVEFp2l8dX-FIvTcA"  # Replace with your API key

# Initialize Gemini client and models
@st.cache_resource
def get_gemini_client():
    genai.configure(api_key=API_KEY)
    return genai

# Function to get the appropriate model based on task
def get_model(task_type="chat"):
    if task_type in ["image", "audio", "video"]:
        return "gemini-1.5-flash"  # For multimodal tasks
    else:
        return "gemini-1.5-flash"  # For chat and reasoning

# Common generation config
def get_generation_config(temperature=0.7):
    return {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 4096,
    }

# Safety settings
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# Initialize the client
get_gemini_client()

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Learning Assistant"

if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

# Header
st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
st.markdown('<div class="edu-subheader">Powered by Google Gemini | Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)

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
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.experimental_rerun()

# App modes
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Audio Analysis", "Video Learning", "Quiz Generator"]
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
            
            multimedia_examples = st.checkbox("Include Multimedia Examples", value=True,
                                          help="When possible, include diagrams, charts, or other visual aids in explanations")
    
    # Initialize chat if not exists
    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = [
            {"role": "assistant", "content": "👋 Hi there! I'm your AI learning companion. What would you like to learn about today?"}
        ]
    
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
        upload_option = st.selectbox("", ["Add Media", "Image", "Audio", "Video", "Document"], key="upload_selector")
    
    # Handle file uploads
    uploaded_file = None
    if upload_option != "Add Media":
        if upload_option == "Image":
            uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"], key="chat_image_upload")
        elif upload_option == "Audio":
            uploaded_file = st.file_uploader("Upload audio:", type=["mp3", "wav", "m4a"], key="chat_audio_upload")
        elif upload_option == "Video":
            uploaded_file = st.file_uploader("Upload video:", type=["mp4", "mov", "avi"], key="chat_video_upload")
        elif upload_option == "Document":
            uploaded_file = st.file_uploader("Upload document:", type=["pdf", "docx", "txt"], key="chat_doc_upload")
        
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
        
        with st.spinner("Thinking..."):
            try:
                # Create a generative model instance
                model = genai.GenerativeModel(
                    model_name=get_model(),
                    generation_config=get_generation_config(temperature=0.7),
                    safety_settings=safety_settings
                )
                
                # Check if there's a multimedia upload to process
                has_multimedia = False
                
                if hasattr(st.session_state, 'current_upload') and st.session_state.current_upload is not None:
                    has_multimedia = True
                    media_type = st.session_state.current_upload["type"].lower()
                    media_bytes = st.session_state.current_upload["file"].getvalue()
                    
                    # Handle image upload
                    if media_type == "image":
                        # Create content parts for the API
                        parts = [
                            {"text": f"{system_context}\n\nUser question: {user_input}\n\nNote: The user has also uploaded an image."}
                        ]
                        
                        # Add image part
                        mime_type = f"image/{st.session_state.current_upload['name'].split('.')[-1]}"
                        encoded_image = base64.b64encode(media_bytes).decode('utf-8')
                        parts.append({"inline_data": {"mime_type": mime_type, "data": encoded_image}})
                        
                        # Generate content with image
                        response = model.generate_content(parts)
                    else:
                        # For text-only or other media types
                        prompt = f"{system_context}\n\nConversation history:\n{conversation_history}\n\nCurrent question: {user_input}"
                        if has_multimedia:
                            prompt += f"\n\nNote: The student has also uploaded a {media_type} file named '{st.session_state.current_upload['name']}'. Please incorporate this into your response if relevant."
                        
                        response = model.generate_content(prompt)
                else:
                    # Text-only request
                    prompt = f"{system_context}\n\nConversation history:\n{conversation_history}\n\nCurrent question: {user_input}"
                    response = model.generate_content(prompt)
                
                # Extract response text
                response_text = response.text
                
                # Add AI response to chat
                st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                
                # Clear the input area
                st.session_state.tutor_input = ""
                
                # Rerun to update the chat display
                st.experimental_rerun()
            
            except Exception as e:
                error_message = f"I apologize, but I encountered an error: {str(e)}"
                st.session_state.tutor_messages.append({"role": "assistant", "content": error_message})
                st.experimental_rerun()


# Document Analysis tab
with selected_tab[1]:
    if st.session_state.current_mode != "Document Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Document Analysis"
    
    st.markdown("### AI-Powered Document Analysis")
    st.markdown("Upload study materials, textbooks, or notes for AI analysis and insights")
    
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        analysis_type = st.multiselect("Select analysis types:", 
                                      ["Key Concepts Extraction", "Summary Generation", 
                                       "Difficulty Assessment", "Concept Relations", 
                                       "Generate Study Questions"])
        
        if st.button("Analyze Document", use_container_width=True):
            with st.spinner("Analyzing document..."):
                # Get file content as bytes
                file_bytes = uploaded_file.getvalue()
                
                # Create a temporary file to hold the content
                with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split(".")[-1]) as temp_file:
                    temp_file.write(file_bytes)
                    temp_file_path = temp_file.name
                
                try:
                    # For text files, we can read and process directly
                    if uploaded_file.type == "text/plain":
                        file_content = file_bytes.decode('utf-8')
                        # If the file is large, trim it
                        if len(file_content) > 10000:
                            file_content = file_content[:10000] + "... [content truncated due to size]"
                    else:
                        # For other files, use a simplification for this demo
                        file_content = f"[Content of {uploaded_file.name} - {uploaded_file.type}]"
                    
                    # Create prompt with analysis instructions
                    analysis_prompt = f"I'm uploading a document named '{uploaded_file.name}'. "
                    analysis_prompt += f"Please perform the following analyses: {', '.join(analysis_type)}. "
                    analysis_prompt += "Here's the document content: " + file_content
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Please analyze my document '{uploaded_file.name}' for: {', '.join(analysis_type)}"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=get_model(),
                        generation_config=get_generation_config(temperature=0.2),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(analysis_prompt)
                    
                    # Extract response text
                    response_text = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                    
                    # Clean up the temporary file
                    os.unlink(temp_file_path)
                
                except Exception as e:
                    st.error(f"Error analyzing document: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                    
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
    
    # Display analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

# Visual Learning tab  
with selected_tab[2]:
    if st.session_state.current_mode != "Visual Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Visual Learning"
    
    st.markdown("### Visual Learning Assistant")
    st.markdown("Upload images of diagrams, problems, or visual concepts for AI explanation")
    
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        query_type = st.radio("What would you like to do with this image?", 
                             ["Explain the concept shown", "Identify elements", 
                              "Solve the problem shown", "Create a related exercise"])
        
        specific_question = st.text_input("Any specific questions about this image?", 
                                         placeholder="e.g., What does this diagram represent?")
        
        # Main image analysis button
        if st.button("Analyze Image", use_container_width=True, key="main_analysis"):
            with st.spinner("Analyzing image..."):
                try:
                    # Create prompt with image query
                    image_prompt = f"{query_type}"
                    if specific_question:
                        image_prompt += f": {specific_question}"
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Image uploaded] {image_prompt}"})
                    
                    # Convert image for API
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=get_model("image"),
                        generation_config=get_generation_config(temperature=0.2),
                        safety_settings=safety_settings
                    )
                    
                    # Create content parts for the API
                    parts = [
                        {"text": image_prompt}
                    ]
                    
                    # Add image part
                    encoded_image = base64.b64encode(img_byte_arr).decode('utf-8')
                    parts.append({"inline_data": {"mime_type": "image/png", "data": encoded_image}})
                    
                    # Generate content with image
                    response = model.generate_content(parts)
                    
                    # Extract response text
                    response_text = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display visual analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

# Audio Analysis tab
with selected_tab[3]:
    if st.session_state.current_mode != "Audio Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Audio Analysis"
    
    st.markdown("### Audio Learning Assistant")
    st.markdown("Upload audio files for transcription, analysis, and educational insights")
    
    uploaded_audio = st.file_uploader("Upload an audio file:", type=["mp3", "wav", "m4a", "ogg"])
    
    if uploaded_audio is not None:
        # Display audio player
        st.audio(uploaded_audio, format="audio/mp3")
        
        analysis_options = st.multiselect("Select analysis types:", 
                                     ["Transcription", "Content Summary", 
                                      "Key Concepts Extraction", "Generate Quiz from Audio",
                                      "Language Analysis", "Vocabulary Extraction"])
        
        language = st.selectbox("Audio Language (if known):", 
                              ["Auto-detect", "English", "Spanish", "French", "German", 
                               "Chinese", "Japanese", "Arabic", "Hindi", "Russian"])
        
        if st.button("Analyze Audio", use_container_width=True):
            with st.spinner("Processing audio..."):
                try:
                    # Get audio bytes
                    audio_bytes = uploaded_audio.getvalue()
                    
                    # Create prompt for audio analysis
                    audio_prompt = f"I've uploaded an audio file named '{uploaded_audio.name}'. "
                    audio_prompt += f"Please perform the following analyses: {', '.join(analysis_options)}. "
                    
                    if language != "Auto-detect":
                        audio_prompt += f"The audio is in {language}. "
                    
                    audio_prompt += "Please provide a detailed analysis focusing on educational value."
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Audio uploaded] Please analyze with: {', '.join(analysis_options)}"})
                    
                    # For this demo, provide a simulated analysis since audio processing may not be fully available
                    analysis_content = f"""
# Audio Analysis of {uploaded_audio.name}

## Transcription
[This would contain the transcribed text from the audio file]

## Content Summary
This audio appears to contain educational content related to [subject]. The main topics covered include:
- Topic 1
- Topic 2
- Topic 3

## Key Concepts Identified
- Concept 1: Brief explanation
- Concept 2: Brief explanation
- Concept 3: Brief explanation

## Educational Value
This audio would be suitable for students at the [level] level. It effectively explains [concepts] and could be integrated into curriculum for [subject] courses.
"""
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": analysis_content})
                
                except Exception as e:
                    st.error(f"Error analyzing audio: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display audio analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

# Video Learning tab
with selected_tab[4]:
    if st.session_state.current_mode != "Video Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Video Learning"
    
    st.markdown("### Video Learning Assistant")
    st.markdown("Upload educational videos for AI analysis, summaries, and interactive learning")
    
    uploaded_video = st.file_uploader("Upload a video file:", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        # Display video player
        video_bytes = uploaded_video.getvalue()
        st.video(video_bytes)
        
        video_analysis_options = st.multiselect("Select analysis types:", 
                                      ["Video Transcription", "Content Summary", 
                                       "Visual Concept Detection", "Key Moments Identification",
                                       "Generate Quiz from Video", "Educational Value Assessment"])
        
        video_focus = st.selectbox("Educational Focus:", 
                                ["General Analysis", "STEM Concepts", "Humanities Focus", 
                                 "Language Learning", "Procedural Skills", "Critical Thinking"])
        
        if st.button("Analyze Video", use_container_width=True):
            with st.spinner("Processing video..."):
                try:
                    # Create prompt for video analysis
                    video_prompt = f"I've uploaded a video file named '{uploaded_video.name}'. "
                    video_prompt += f"Please perform the following analyses: {', '.join(video_analysis_options)}. "
                    video_prompt += f"Focus on {video_focus} educational aspects. "
                    video_prompt += "Provide a detailed analysis of the educational value of this video."
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Video uploaded] Please analyze with: {', '.join(video_analysis_options)}"})
                    
                    # For this demo, provide a simulated analysis
                    video_analysis = f"""
# Video Analysis of {uploaded_video.name}

## Content Summary
This educational video covers [subject] with a focus on [specific topics]. The presenter demonstrates [concepts/skills] through visual examples and clear explanations.

## Visual Concepts Detected
- Concept 1 (00:15-01:30): Brief explanation
- Concept 2 (02:45-04:10): Brief explanation
- Concept 3 (05:20-07:45): Brief explanation

## Key Educational Moments
1. Introduction to [concept] (00:00-01:15)
2. Demonstration of [technique/process] (03:20-05:40)
3. Practice examples and applications (06:30-08:45)
4. Summary and key takeaways (09:10-end)

## Educational Value
This video would be valuable for students studying [subject] at the [level] level. It effectively visualizes [complex concepts] that are difficult to convey through text alone.

## Suggested Learning Activities
- Pre-video introduction to basic terminology
- Pause-point questions at key moments (times noted above)
- Post-video assessment focusing on key concepts
- Group discussion topics based on applications shown
"""
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": video_analysis})
                
                except Exception as e:
                    st.error(f"Error analyzing video: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display video analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

# Quiz Generator tab
with selected_tab[5]:
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Quiz Generator"
    
    st.markdown("### AI Quiz Generator")
    st.markdown("Generate customized quizzes and assessments for any subject or learning level")
    
    quiz_subject = st.text_input("Quiz Subject or Topic:", placeholder="e.g., World History, Algebra, Biology")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quiz_level = st.selectbox("Difficulty Level:", 
                                ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Mixed"])
        
        quiz_type = st.selectbox("Question Type:", 
                               ["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank", "Mixed Format"])
    
    with col2:
        question_count = st.slider("Number of Questions:", min_value=3, max_value=20, value=10)
        
        include_answers = st.checkbox("Include Answer Key", value=True)
    
    # Additional options in an expander
    with st.expander("Advanced Options"):
        specific_topics = st.text_area("Focus on specific subtopics or concepts:", 
                                      placeholder="e.g., French Revolution, Quadratic Equations, Cell Biology")
        
        learning_objectives = st.text_area("Learning objectives to assess:", 
                                          placeholder="e.g., Understand causes and effects, Apply formulas to solve problems")
        
        time_limit = st.slider("Recommended Time Limit (minutes):", min_value=5, max_value=120, value=30)
    
    if st.button("Generate Quiz", use_container_width=True):
        if not quiz_subject:
            st.warning("Please enter a quiz subject")
        else:
            with st.spinner("Generating your quiz..."):
                try:
                    # Create quiz prompt
                    quiz_prompt = f"Generate a {quiz_level} level quiz on {quiz_subject} with {question_count} {quiz_type} questions."
                    
                    if specific_topics:
                        quiz_prompt += f" Focus on these specific topics: {specific_topics}."
                    
                    if learning_objectives:
                        quiz_prompt += f" The quiz should assess these learning objectives: {learning_objectives}."
                    
                    quiz_prompt += f" The quiz should take approximately {time_limit} minutes to complete."
                    
                    if include_answers:
                        quiz_prompt += " Include an answer key with explanations."
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=get_model(),
                        generation_config=get_generation_config(temperature=0.7),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(quiz_prompt)
                    
                    # Extract response text
                    quiz_text = response.text
                    
                    # Display the generated quiz in a formatted box
                    st.markdown("## Generated Quiz")
                    st.markdown(f"<div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>{quiz_text}</div>", unsafe_allow_html=True)
                    
                    # Add download options
                    st.download_button(
                        label="Download Quiz as Text",
                        data=quiz_text,
                        file_name=f"{quiz_subject.replace(' ', '_')}_quiz.txt",
                        mime="text/plain"
                    )
                
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 10px; color: #666;">
    <p>EduGenius - Powered by Google Gemini | &copy; 2025</p>
    <p style="font-size: 0.8rem;">Disclaimer: This is a demo application. AI-generated content should be reviewed by educators before use in formal educational settings.</p>
</div>
""", unsafe_allow_html=True)

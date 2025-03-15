import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import google.generativeai as genai

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

# Initialize Gemini client
@st.cache_resource
def get_gemini_client():
    # In production, use a more secure way to store API keys
    api_key = "AIzaSyCl9IcFv0Qv72XvrrKyN2inQ8RG_12Xr6s"  # Replace with st.secrets["GEMINI_API_KEY"] in production
    genai.configure(api_key=api_key)
    return genai

# Initialize the client
get_gemini_client()
model_name = "gemini-1.5-flash"  # Using Gemini 1.5 Flash model

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
        
        <div style="text-align: center; margin-top: 30px;">
            <button style="background-color: #4257b2; color: white; border: none; padding: 10px 20px; border-radius: 5px; font-weight: bold; cursor: pointer;" id="get-started-btn">Get Started</button>
        </div>
    </div>
    
    <script>
        document.getElementById("get-started-btn").addEventListener("click", function() {
            window.parent.postMessage({type: "streamlit:setComponentValue", value: false}, "*");
        });
    </script>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.experimental_rerun()

# App modes
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Audio Analysis", "Video Learning", "Quiz Generator", "Concept Mapper"]
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
        
        # Create complete prompt
        if conversation_history:
            prompt = f"{system_context}\n\nConversation history:\n{conversation_history}\n\nCurrent question: {user_input}"
        else:
            prompt = f"{system_context}\n\nStudent question: {user_input}"
        
        # Check if there's a multimedia upload to process
        has_multimedia = False
        media_type = None
        media_bytes = None
        
        if hasattr(st.session_state, 'current_upload') and st.session_state.current_upload is not None:
            has_multimedia = True
            media_type = st.session_state.current_upload["type"].lower()
            media_bytes = st.session_state.current_upload["file"].getvalue()
            
            # Add multimedia context to prompt
            prompt += f"\n\nNote: The student has also uploaded a {media_type} file named '{st.session_state.current_upload['name']}'. Please incorporate this into your response if relevant."
        
        with st.spinner("Thinking..."):
            try:
                # Create a generative model instance
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=get_generation_config(temperature=0.7),
                    safety_settings=safety_settings
                )
                
                # Generate response based on whether there's multimedia
                if has_multimedia and media_type == "image":
                    response = model.generate_content([
                        prompt,
                        {"mime_type": "image/jpeg", "data": media_bytes}
                    ])
                else:
                    # For text-only or other media types (which we're simulating for now)
                    response = model.generate_content(prompt)
                
                # Extract response text
                response_text = response.text
                
                # Add AI response to chat
                st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                
                # Clear the input area
                st.session_state.tutor_input = ""
                
                # Rerun to update the chat display
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
                
                # In a real implementation, you would process the document content here
                # For now, just use a placeholder for the demo
                file_content_preview = file_bytes[:1000]  # Just use first 1000 bytes as a preview
                
                try:
                    # Create prompt with analysis instructions
                    analysis_prompt = f"I'm uploading a document named '{uploaded_file.name}'. "
                    analysis_prompt += f"Please perform the following analyses: {', '.join(analysis_type)}. "
                    analysis_prompt += "Here's a preview of the document content: " + str(file_content_preview)
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Please analyze my document '{uploaded_file.name}' for: {', '.join(analysis_type)}"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
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
        
        # Add chat-like interaction
        st.markdown("### Image Chat")
        st.info("You can have a conversation about this image by entering questions below.")
        
        # Initialize image chat history if not exists
        if "image_chat_history" not in st.session_state:
            st.session_state.image_chat_history = []
        
        # Display image chat history
        for message in st.session_state.image_chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**EduGenius:** {message['content']}")
            st.markdown("---")
        
        image_chat_input = st.text_input("Ask about this image:", 
                               placeholder="e.g., Can you explain what's happening in this diagram?")
        
        if st.button("Send", key="image_chat_button"):
            if image_chat_input:
                # Add to image chat history
                st.session_state.image_chat_history.append({"role": "user", "content": image_chat_input})
                
                with st.spinner("Analyzing..."):
                    try:
                        # Convert image for API
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        # Create a generative model instance
                        model = genai.GenerativeModel(
                            model_name=model_name,
                            generation_config=get_generation_config(temperature=0.2),
                            safety_settings=safety_settings
                        )
                        
                        # Prepare multipart content
                        response = model.generate_content([
                            image_chat_input,
                            {"mime_type": "image/png", "data": img_byte_arr}
                        ])
                        
                        # Extract response text
                        response_text = response.text
                        st.session_state.image_chat_history.append({"role": "assistant", "content": response_text})
                        
                        # Rerun to update the chat display
                        st.experimental_rerun()
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.image_chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                        st.experimental_rerun()
        
        # Main image analysis button
        if st.button("Analyze Image", use_container_width=True, key="main_analysis"):
            with st.spinner("Analyzing image..."):
                try:
                    # Create prompt with image query
                    image_prompt = f"{query_type}: {specific_question}" if specific_question else query_type
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Image uploaded] {image_prompt}"})
                    
                    # Convert image for API
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.2),
                        safety_settings=safety_settings
                    )
                    
                    # Prepare multipart content
                    response = model.generate_content([
                        image_prompt,
                        {"mime_type": "image/png", "data": img_byte_arr}
                    ])
                    
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
                    
                    # Create a generative model instance for audio
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.2),
                        safety_settings=safety_settings
                    )
                    
                    # In production, you would process the audio file here
                    # For demo purposes, simulate the audio analysis
                    
                    # Simulate an analysis response
                    analysis_content = f"""
# Audio Analysis of {uploaded_audio.name}

## Transcription
[This would normally contain the transcribed text from the audio file]

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
                    
                    # Add chat functionality for audio
                    st.markdown("### Audio Chat")
                    st.info("You can ask questions about this audio by typing below")
                    
                    # Initialize audio chat if not exists
                    if "audio_chat_history" not in st.session_state:
                        st.session_state.audio_chat_history = []
                    
                    # Display audio chat history
                    for message in st.session_state.audio_chat_history:
                        if message["role"] == "user":
                            st.markdown(f"**You:** {message['content']}")
                        else:
                            st.markdown(f"**EduGenius:** {message['content']}")
                    
                    audio_chat_input = st.text_input("Ask about this audio:", 
                                              placeholder="e.g., Can you summarize the main points from this lecture?")
                    
                    if st.button("Send", key="audio_chat_button"):
                        if audio_chat_input:
                            # Add to audio chat history
                            st.session_state.audio_chat_history.append({"role": "user", "content": audio_chat_input})
                            
                            # In a real implementation, you would process the audio file here
                            # For demo purposes, simulate the chat response
                            chat_response = "I'd be happy to answer questions about the audio content once the audio processing capability is fully implemented. This would typically include details about the content, concepts, and educational aspects of the audio you uploaded."
                            
                            st.session_state.audio_chat_history.append({"role": "assistant", "content": chat_response})
                
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
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.2),
                        safety_settings=safety_settings
                    )
                    
                    # In production, you would process the video file here
                    # For demo purposes, simulate the video analysis
                    
                    # Simulate an analysis response
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
                    
                    # Add interactive features
                    st.markdown("### Video Interactive Learning")
                    
                    # Create tabs for different interactive features
                    interactive_tabs = st.tabs(["Chat About Video", "Generate Timestamps", "Create Quiz"])
                    
                    with interactive_tabs[0]:
                        st.markdown("#### Ask questions about this video")
                        
                        # Initialize video chat if not exists
                        if "video_chat_history" not in st.session_state:
                            st.session_state.video_chat_history = []
                        
                        # Display video chat history
                        for message in st.session_state.video_chat_history:
                            if message["role"] == "user":
                                st.markdown(f"**You:** {message['content']}")
                            else:
                                st.markdown(f"**EduGenius:** {message['content']}")
                            st.markdown("---")
                        
                        video_chat_input = st.text_input("Ask about this video:", 
                                                placeholder="e.g., What are the main points covered in this video?")
                        
                        if st.button("Send", key="video_chat_button"):
                            if video_chat_input:
                                # Add to video chat history
                                st.session_state.video_chat_history.append({"role": "user", "content": video_chat_input})
                                
                                # In a real implementation, you would process the video query here
                                # For demo purposes, simulate a response
                                chat_response = "I'd be happy to answer questions about the video content once the video processing capability is fully implemented. This would typically include information about the visual concepts, explanations, demonstrations, and educational value of the video you uploaded."
                                
                                st.session_state.video_chat_history.append({"role": "assistant", "content": chat_response})
                    
                    with interactive_tabs[1]:
                        st.markdown("#### Generate Educational Timestamps")
                        st.info("This would identify key moments in the video for educational purposes")
                        
                        timestamp_purpose = st.selectbox("Timestamp Purpose:", 
                                                      ["Key Concepts", "Quiz Questions", "Discussion Points", "Practice Exercises"])
                        
                        if st.button("Generate Timestamps", key="timestamp_button"):
                            # In a real implementation, you would analyze the video for timestamps
                            # For demo purposes, display sample timestamps
                            st.markdown("""
                            ## Generated Educational Timestamps
                            
                            | Time | Content | Educational Value |
                            |------|---------|-------------------|
                            | 00:15 | Introduction to concept X | Establishes foundational knowledge |
                            | 01:30 | First example demonstration | Visual application of theory |
                            | 03:45 | Key insight explanation | Critical understanding point |
                            | 05:20 | Common misconception addressed | Prevents learning errors |
                            | 07:10 | Advanced application | Shows real-world relevance |
                            | 09:30 | Summary of key points | Reinforces learning |
                            """)
                    
                    with interactive_tabs[2]:
                        st.markdown("#### Generate Quiz Based on Video")
                        
                        quiz_question_count = st.slider("Number of Questions:", min_value=3, max_value=15, value=5)
                        quiz_format = st.selectbox("Quiz Format:", 
                                                ["Multiple Choice", "True/False", "Mixed Formats", "Short Answer"])
                        
                        if st.button("Create Video Quiz", key="video_quiz_button"):
                            # In a real implementation, you would generate questions based on video content
                            # For demo purposes, display a sample quiz
                            st.markdown(f"""
                            ## Video Content Quiz ({quiz_question_count} Questions)
                            
                            1. **Question**: What is the main concept introduced at the beginning of the video?
                               - A) Concept X
                               - B) Concept Y
                               - C) Concept Z
                               - D) None of the above
                               
                            2. **Question**: According to the video, which of the following statements is true?
                               - A) Statement 1
                               - B) Statement 2
                               - C) Statement 3
                               - D) Statement 4
                            
                            3. **Question**: What technique was demonstrated at approximately 03:45 in the video?
                               - A) Technique A
                               - B) Technique B
                               - C) Technique C
                               - D) Technique D
                            
                            4. **Question**: The video suggests that the best application of this concept is in which field?
                               - A) Field 1
                               - B) Field 2
                               - C) Field 3
                               - D) All of the above
                            
                            5. **Question**: What was the concluding point made in the video?
                               - A) Point A
                               - B) Point B
                               - C) Point C
                               - D) Point D
                            """)
                
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
    st.markdown("Create customized quizzes and assessments for any subject or learning level")
    
    # Quiz generation form
    with st.form("quiz_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.text_input("Subject or Topic:", placeholder="e.g., World History, Algebra, Biology")
            subtopic = st.text_input("Specific Subtopic (optional):", placeholder="e.g., World War II, Quadratic Equations")
            education_level = st.selectbox("Education Level:", 
                                         ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
        
        with col2:
            question_count = st.slider("Number of Questions:", 5, 25, 10)
            quiz_type = st.selectbox("Quiz Type:", 
                                    ["Multiple Choice", "True/False", "Fill in the Blank", "Mixed Format", "Short Answer"])
            difficulty = st.select_slider("Difficulty Level:", 
                                        options=["Easy", "Medium", "Hard", "Challenging"])
        
        # Additional options
        include_answers = st.checkbox("Include Answer Key", value=True)
        include_explanations = st.checkbox("Include Explanations", value=True)
        auto_grade = st.checkbox("Enable Auto-grading Features", value=True)
        
        # Content focus
        content_focus = st.multiselect("Content Focus:", 
                                     ["Factual Recall", "Conceptual Understanding", "Application", 
                                      "Analysis", "Critical Thinking", "Problem Solving"],
                                     default=["Factual Recall", "Conceptual Understanding"])
        
        # Special instructions
        special_instructions = st.text_area("Special Instructions (optional):", 
                                          placeholder="Any specific requirements or focus areas for the quiz...")
        
        # Generate quiz button
        generate_button = st.form_submit_button("Generate Quiz", use_container_width=True)
    
    if generate_button:
        with st.spinner("Creating quiz..."):
            try:
                # Create prompt for quiz generation
                quiz_prompt = f"Create a quiz on {subject}"
                if subtopic:
                    quiz_prompt += f" focusing on {subtopic}"
                
                quiz_prompt += f". The quiz should be for {education_level} level students and contain {question_count} {quiz_type} questions at a {difficulty} difficulty level."
                
                if content_focus:
                    quiz_prompt += f" Focus on {', '.join(content_focus)}."
                
                if include_answers:
                    quiz_prompt += " Include an answer key."
                
                if include_explanations:
                    quiz_prompt += " Include explanations for each answer."
                
                if special_instructions:
                    quiz_prompt += f" Additional instructions: {special_instructions}"
                
                # Add to history
                st.session_state.chat_history.append({"role": "user", "content": quiz_prompt})
                
                # Create a generative model instance
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=get_generation_config(temperature=0.3),
                    safety_settings=safety_settings
                )
                
                # Generate content
                response = model.generate_content(quiz_prompt)
                
                # Extract response text
                response_text = response.text
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                # Display the quiz
                st.markdown("## Generated Quiz")
                st.markdown(response_text)
                
                # Add export options
                st.download_button(
                    label="Export Quiz as Text",
                    data=response_text,
                    file_name=f"Quiz_{subject.replace(' ', '_')}.txt",
                    mime="text/plain",
                )
                
                # Quiz usage options
                st.markdown("### Quiz Usage Options")
                
                usage_cols = st.columns(4)
                with usage_cols[0]:
                    if st.button("Print Version", use_container_width=True):
                        st.info("In a full implementation, this would format the quiz for printing")
                
                with usage_cols[1]:
                    if st.button("Student Version", use_container_width=True):
                        st.info("This would create a version without answers for students")
                
                with usage_cols[2]:
                    if st.button("Teacher Version", use_container_width=True):
                        st.info("This would create a version with answers and grading tips")
                
                with usage_cols[3]:
                    if st.button("Interactive Version", use_container_width=True):
                        st.info("This would create an interactive quiz students could take online")
            
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display previously generated quizzes
    st.markdown("### Your Generated Quizzes")
    if len(st.session_state.chat_history) > 0:
        for i in range(0, len(st.session_state.chat_history), 2):
            if i+1 < len(st.session_state.chat_history):
                with st.expander(f"Quiz on {subject}", expanded=False):
                    st.markdown(st.session_state.chat_history[i+1]["content"])
    else:
        st.info("No quizzes generated yet. Create your first quiz above!")

# Concept Mapper tab
with selected_tab[6]:
    if st.session_state.current_mode != "Concept Mapper":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Concept Mapper"
    
    st.markdown("### AI Concept Mapper")
    st.markdown("Visualize connections between concepts to enhance understanding and retention")
    
    # Concept mapping form
    with st.form("concept_map_form"):
        main_topic = st.text_input("Main Topic:", placeholder="e.g., Photosynthesis, Democracy, Machine Learning")
        
        col1, col2 = st.columns(2)
        with col1:
            complexity = st.select_slider("Map Complexity:", 
                                        options=["Simple", "Moderate", "Detailed", "Comprehensive"])
            focus_area = st.selectbox("Focus Area:", 
                                    ["Hierarchical Structure", "Process Flow", "Cause and Effect", 
                                     "Compare and Contrast", "Theoretical Framework"])
        
        with col2:
            education_level = st.selectbox("Education Level:", 
                                         ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"],
                                         key="concept_edu_level")
            visual_style = st.selectbox("Visual Style:", 
                                      ["Academic", "Educational", "Mind Map", "Network Diagram", "Infographic"])
        
        # Additional options
        include_definitions = st.checkbox("Include Concept Definitions", value=True)
        include_examples = st.checkbox("Include Examples", value=True)
        include_resources = st.checkbox("Include Additional Resources", value=False)
        
        # Custom content
        custom_content = st.text_area("Custom Content or Specific Concepts to Include (optional):", 
                                    placeholder="List specific concepts or content you want included in the map...")
        
        # Generate map button
        map_button = st.form_submit_button("Generate Concept Map", use_container_width=True)
    
    if map_button:
        with st.spinner("Creating concept map..."):
            try:
                # Create prompt for concept map generation
                map_prompt = f"Create a {complexity} concept map about {main_topic} for {education_level} level students. "
                map_prompt += f"The concept map should focus on {focus_area} and use a {visual_style} style. "
                
                if include_definitions:
                    map_prompt += "Include brief definitions for key concepts. "
                
                if include_examples:
                    map_prompt += "Include examples where appropriate. "
                
                if include_resources:
                    map_prompt += "Suggest additional resources for further learning. "
                
                if custom_content:
                    map_prompt += f"Be sure to include these specific concepts or content: {custom_content}. "
                
                map_prompt += "Provide the concept map in a format that clearly shows relationships between concepts."
                
                # Add to history
                st.session_state.chat_history.append({"role": "user", "content": map_prompt})
                
                # Create a generative model instance
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config=get_generation_config(temperature=0.3),
                    safety_settings=safety_settings
                )
                
                # Generate content
                response = model.generate_content(map_prompt)
                
                # Extract response text
                response_text = response.text
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                # Display the concept map description
                st.markdown("## Generated Concept Map")
                st.markdown(response_text)
                
                # Add export and visualization options
                st.download_button(
                    label="Export Concept Map Description",
                    data=response_text,
                    file_name=f"ConceptMap_{main_topic.replace(' ', '_')}.txt",
                    mime="text/plain",
                )
                
                # Visual representation (in a real implementation, this would create a graphical concept map)
                st.markdown("### Visual Representation")
                st.info("In a full implementation, this would generate an interactive visual concept map based on the description above.")
                
                # Sample visualization (placeholder)
                st.markdown("""
                This is a placeholder for the visual concept map. In a complete implementation, 
                this would be an interactive visualization showing concepts and their relationships.
                """)
                
                # Study tools based on the concept map
                st.markdown("### Study Tools")
                
                tool_cols = st.columns(3)
                with tool_cols[0]:
                    if st.button("Generate Flashcards", use_container_width=True):
                        st.info("This would create flashcards based on the concept map")
                
                with tool_cols[1]:
                    if st.button("Create Study Guide", use_container_width=True):
                        st.info("This would create a study guide based on the concept map")
                
                with tool_cols[2]:
                    if st.button("Generate Quiz", use_container_width=True):
                        st.info("This would create a quiz based on the concept map")
            
            except Exception as e:
                st.error(f"Error generating concept map: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display previously generated concept maps
    st.markdown("### Your Concept Maps")
    if len(st.session_state.chat_history) > 0:
        for i in range(0, len(st.session_state.chat_history), 2):
            if i+1 < len(st.session_state.chat_history):
                with st.expander(f"Concept Map on {main_topic}", expanded=False):
                    st.markdown(st.session_state.chat_history[i+1]["content"])
    else:
        st.info("No concept maps generated yet. Create your first concept map above!")

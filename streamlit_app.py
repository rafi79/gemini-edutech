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
model_name = "gemini-2.0-flash"  # Using a model that actually exists in the API

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
        st.rerun()

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
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
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
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.image_chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                        st.rerun()
        
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
            st.markdown(f"**Analysis:** {message['

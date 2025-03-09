import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
import google.generativeai as genai
from google.generativeai import types
from google import generativeai

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
API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyCagQKSSGGM-VcoOwIVEFp2l8dX-FIvTcA")

# Initialize both legacy and new Gemini clients
@st.cache_resource
def initialize_gemini_clients():
    # Initialize legacy client (google.generativeai)
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize legacy Gemini API: {str(e)}")
    
    # Initialize newer client (google.generativeai.generativeai)
    try:
        client = generativeai.Client(api_key=API_KEY)
        return client
    except Exception as e:
        st.error(f"Failed to initialize new Gemini client: {str(e)}")
        return None

# Get newer client
gemini_client = initialize_gemini_clients()

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    if task_type in ["image", "audio", "video"]:
        return "gemini-1.5-flash"  # For multimodal tasks
    else:
        return "gemini-2.0-flash"  # For chat and reasoning

# Streamlined function to generate content with fallbacks
def generate_content(prompt, model_name="gemini-2.0-flash", image_data=None, temperature=0.7):
    """
    Generate content using multiple fallback approaches.
    
    Args:
        prompt: Text prompt
        model_name: Which Gemini model to use
        image_data: Optional image data as bytes
        temperature: Temperature for generation
    
    Returns:
        Response text or error message
    """
    # Try multiple approaches with robust fallbacks
    errors = []
    
    # 1. Try newest client API first (streaming)
    if gemini_client:
        try:
            # Prepare content
            if image_data:
                # With image
                content = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(prompt),
                            types.Part.from_data(mime_type="image/jpeg", data=image_data)
                        ]
                    )
                ]
            else:
                # Text only
                content = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(prompt)]
                    )
                ]
            
            # Configure generation
            generate_config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain"
            )
            
            # For streaming, collect chunks
            response_chunks = []
            for chunk in gemini_client.models.generate_content_stream(
                model=model_name,
                contents=content,
                config=generate_config
            ):
                response_chunks.append(chunk.text)
            
            # Combine all chunks
            return "".join(response_chunks)
        
        except Exception as e:
            errors.append(f"New client streaming API error: {str(e)}")
    
    # 2. Try the legacy client API
    try:
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
        errors.append(f"Legacy client API error: {str(e)}")
    
    # 3. Try newer client non-streaming as last resort
    if gemini_client:
        try:
            # Same content setup as in streaming
            if image_data:
                content = [
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(prompt),
                            types.Part.from_data(mime_type="image/jpeg", data=image_data)
                        ]
                    )
                ]
            else:
                content = [
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(prompt)]
                    )
                ]
            
            # Configure generation
            generate_config = types.GenerateContentConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="text/plain"
            )
            
            # Non-streaming request
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=content,
                config=generate_config
            )
            
            return response.text
            
        except Exception as e:
            errors.append(f"New client non-streaming API error: {str(e)}")
    
    # If all methods fail, return error details
    return f"Sorry, I encountered errors while generating a response. Technical details: {'; '.join(errors)}"

# Function to start a chat session
def start_chat_session(model_name="gemini-2.0-flash", history=None):
    """Start a chat session with the specified model"""
    if history is None:
        history = []
    
    try:
        # Try legacy API first
        return genai.GenerativeModel(model_name=model_name).start_chat(history=history)
    except Exception as e:
        st.error(f"Error starting chat session with legacy API: {str(e)}")
        # Could implement fallback to newer API here if needed
        return None

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
        st.rerun()

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
        
        # Try to use the new generate_content function with fallbacks
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
                
                # Select appropriate model
                model_name = get_model_name("image" if has_multimedia else "chat")
                
                # Generate response using our robust function
                response_text = generate_content(
                    prompt=prompt,
                    model_name=model_name,
                    image_data=media_bytes if has_multimedia else None,
                    temperature=0.7
                )
                
                # Add AI response to chat
                st.session_state.tutor_messages.append({"role": "assistant", "content": response_text})
                
                # Clear the input area
                st.session_state.tutor_input = ""
                
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
                    
                    # Create prompt for document analysis
                    analysis_prompt = f"I'm uploading a document named '{uploaded_file.name}'. "
                    analysis_prompt += f"Please perform the following analyses: {', '.join(analysis_type)}. "
                    analysis_prompt += "Here's the document content: " + file_content
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Please analyze my document '{uploaded_file.name}' for: {', '.join(analysis_type)}"})
                    
                    # Generate with our robust function
                    response_text = generate_content(
                        prompt=analysis_prompt,
                        model_name=get_model_name("chat"),
                        temperature=0.3
                    )
                    
                    # Add to history
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
                        
                        # Use our robust generate_content function
                        response_text = generate_content(
                            prompt=image_chat_input,
                            model_name=get_model_name("image"),
                            image_data=img_byte_arr,
                            temperature=0.7
                        )
                        
                        # Add to chat history and update display
                        st.session_state.image_chat_history.append({"role": "assistant", "content": response_text})
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        st.session_state.image_chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
                        st.rerun()
        
        # Main image analysis button
        if st.button("Analyze Image", use_container_width=True, key="main_analysis"):
            with st.spinner("Analyzing image..."):
                try:
                    # Create prompt for image analysis
                    image_prompt = f"{query_type}"
                    if specific_question:
                        image_prompt += f": {specific_question}"
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Image uploaded] {image_prompt}"})
                    
                    # Convert image for API
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_byte_arr = img_byte_arr.getvalue()
                    
                    # Use our robust image processing function
                    response_text = generate_content(
                        prompt=image_prompt,
                        model_name=get_model_name("image"),
                        image_data=img_byte_arr,
                        temperature=0.3
                    )
                    
                    # Add to history
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
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"[Audio uploaded] Please analyze with: {', '.join(analysis_options)}"})
                    
                    # For this demo, we'll use the text prompt only since direct audio processing
                    # may not be fully supported yet
                    response_text = generate_content(
                        prompt=audio_prompt,
                        model_name=get_model_name("chat"),
                        temperature=0.3
                    )
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
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
                    
                    # Use our robust generate function (text only for now)
                    response_text = generate_content(
                        prompt=video_prompt,
                        model_name=get_model_name("chat"),
                        temperature=0.3
                    )
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
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
                    # Create prompt for quiz
                    quiz_prompt = f"Generate a {quiz_level} level quiz on {quiz_subject} with {question_count} {quiz_type} questions."
                    
                    if specific_topics:
                        quiz_prompt += f" Focus on these specific topics: {specific_topics}."
                    
                    if learning_objectives:
                        quiz_prompt += f" The quiz should assess these learning objectives: {learning_objectives}."
                    
                    quiz_prompt += f" The quiz should take approximately {time_limit} minutes to complete."
                    
                    if include_answers:
                        quiz_prompt += " Include an answer key with explanations."
                    
                    # Generate with our robust function
                    quiz_text = generate_content(
                        prompt=quiz_prompt,
                        model_name=get_model_name("chat"),
                        temperature=0.7
                    )
                    
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

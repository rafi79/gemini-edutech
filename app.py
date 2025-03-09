import streamlit as st
import base64
from PIL import Image
import io
import os
import tempfile
from google import generativeai
import google.generativeai as genai
import PyPDF2


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

# Initialize Gemini client
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Gemini API: {str(e)}")

# Function to get the appropriate model based on task
def get_model_name(task_type="chat"):
    if task_type in ["image", "audio", "video"]:
        return "gemini-1.5-flash"  # For multimodal tasks
    else:
        return "gemini-2.0-flash"  # For chat and reasoning

# Function to generate content with robust error handling
def generate_content(prompt, model_name="gemini-2.0-flash", image_data=None, temperature=0.7):
    """Generate content with error handling"""
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
        return f"Sorry, I encountered an error: {str(e)}"

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
                <h3 style="color: #4257b2;">📝 Quiz Generator</h3>
                <p>Create personalized assessments with adaptive difficulty and instant feedback.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.rerun()

# App modes - Simplified for compatibility
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Quiz Generator"]
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
                
                # Select appropriate model
                model_name = get_model_name("image" if has_multimedia else "chat")
                
                # Generate response
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
                                    file_content += page.extract_text() + "\n"
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
                    
                    # Generate response
                    response_text = generate_content(
                        prompt=analysis_prompt,
                        model_name=get_model_name("chat"),
                        temperature=0.3
                    )
                    
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
                    
                    # Generate response
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

# Quiz Generator tab
with selected_tab[3]:
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
                    
                    # Generate quiz
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

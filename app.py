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
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Audio Analysis", "Video Learning", "Quiz Generator", "Content Creation", "Concept Mapper"]
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
                    st.session_state.chat_history.append({"role": "user", "content": f"Generate a {detail_level} {map_style} concept map for {main_concept} at {education_level} level"})"Please analyze my document '{uploaded_file.name}' for: {', '.join(analysis_type)}"})
                    
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

# Quiz Generator tab
with selected_tab[5]:
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Quiz Generator"
    
    st.markdown("### AI Quiz Generator")
    st.markdown("Create customized quizzes, tests, and assessments for any subject or topic")
    
    # Quiz configuration section
    st.subheader("Quiz Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject or Topic:", placeholder="e.g., World War II, Photosynthesis, Python Programming")
        education_level = st.selectbox("Educational Level:", 
                                      ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Professional"])
        question_count = st.slider("Number of Questions:", min_value=3, max_value=20, value=5)
    
    with col2:
        question_types = st.multiselect("Question Types:", 
                                       ["Multiple Choice", "True/False", "Short Answer", "Fill in the Blank", "Matching"], 
                                       default=["Multiple Choice"])
        
        difficulty = st.select_slider("Difficulty Level:", 
                                     options=["Very Easy", "Easy", "Medium", "Hard", "Very Hard"], 
                                     value="Medium")
        
        include_answers = st.checkbox("Include Answer Key", value=True)
    
    # Advanced options in expander
    with st.expander("Advanced Options", expanded=False):
        specific_topics = st.text_area("Focus on Specific Subtopics (optional):", 
                                      placeholder="Enter specific topics to focus on, separated by commas")
        
        specific_concepts = st.text_area("Specific Concepts to Test (optional):", 
                                        placeholder="Enter specific concepts to test, separated by commas")
        
        time_limit = st.number_input("Suggested Time Limit (minutes):", min_value=5, max_value=180, value=30, step=5)
        
        col1, col2 = st.columns(2)
        with col1:
            include_images = st.checkbox("Include Image-Based Questions", value=False)
        
        with col2:
            randomize_options = st.checkbox("Randomize Answer Options", value=True)
        
        instruction_notes = st.text_area("Additional Instructions or Notes:", 
                                        placeholder="Add any specific instructions or notes for the AI when generating the quiz")
    
    # Generate quiz button
    if st.button("Generate Quiz", use_container_width=True):
        if not subject:
            st.warning("Please enter a subject or topic to generate a quiz.")
        else:
            with st.spinner("Generating quiz..."):
                try:
                    # Create prompt for quiz generation
                    quiz_prompt = f"Create a {difficulty} difficulty quiz on {subject} for {education_level} level students. "
                    quiz_prompt += f"Include {question_count} questions of the following types: {', '.join(question_types)}. "
                    
                    if specific_topics:
                        quiz_prompt += f"Focus on these specific subtopics: {specific_topics}. "
                    
                    if specific_concepts:
                        quiz_prompt += f"Test these specific concepts: {specific_concepts}. "
                    
                    if include_answers:
                        quiz_prompt += "Include an answer key. "
                    
                    quiz_prompt += f"The quiz should take approximately {time_limit} minutes to complete. "
                    
                    if include_images:
                        quiz_prompt += "Include descriptions for image-based questions where appropriate. "
                    
                    if randomize_options:
                        quiz_prompt += "The answer options should be randomized. "
                    
                    if instruction_notes:
                        quiz_prompt += f"Additional instructions: {instruction_notes}"
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Generate a {question_count}-question {difficulty} quiz on {subject} for {education_level} level"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.7),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(quiz_prompt)
                    
                    # Extract response text
                    quiz_content = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": quiz_content})
                    
                    # Display the generated quiz with download option
                    st.markdown("### Generated Quiz")
                    st.markdown(quiz_content)
                    
                    # Create a download option for the quiz
                    quiz_download = quiz_content.encode()
                    st.download_button(
                        label="Download Quiz",
                        data=quiz_download,
                        file_name=f"{subject.replace(' ', '_')}_quiz.md",
                        mime="text/markdown"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display quiz history
    st.markdown("### Previously Generated Quizzes")
    quiz_history_count = 0
    
    for i in range(0, len(st.session_state.chat_history), 2):
        if i + 1 < len(st.session_state.chat_history):
            if "Generate a" in st.session_state.chat_history[i]["content"] and "quiz" in st.session_state.chat_history[i]["content"]:
                quiz_history_count += 1
                with st.expander(f"Quiz {quiz_history_count}: {st.session_state.chat_history[i]['content']}", expanded=False):
                    st.markdown(st.session_state.chat_history[i+1]["content"])
                    
                    # Add download button for each historical quiz
                    quiz_download = st.session_state.chat_history[i+1]["content"].encode()
                    st.download_button(
                        label="Download This Quiz",
                        data=quiz_download,
                        file_name=f"quiz_{quiz_history_count}.md",
                        mime="text/markdown",
                        key=f"download_quiz_{quiz_history_count}"
                    )

# Content Creation tab (NEW)
with selected_tab[6]:
    if st.session_state.current_mode != "Content Creation":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Content Creation"
    
    st.markdown("### Educational Content Creator")
    st.markdown("Generate customized educational materials powered by Gemini 1.5 Flash")
    
    # Content type selection
    content_type = st.selectbox("Content Type:", 
                              ["Lesson Plan", "Student Handout", "Lecture Notes", 
                               "Educational Presentation", "Study Guide", 
                               "Educational Infographic", "Interactive Worksheet"])
    
    # Content configuration
    col1, col2 = st.columns(2)
    
    with col1:
        content_subject = st.text_input("Subject:", placeholder="e.g., Biology, Literature, Mathematics")
        content_level = st.selectbox("Educational Level:", 
                                   ["Elementary", "Middle School", "High School", 
                                    "Undergraduate", "Graduate", "Professional Development"])
        
        learning_objectives = st.text_area("Learning Objectives:", 
                                         placeholder="Enter the learning objectives, separated by new lines")
    
    with col2:
        content_duration = st.slider("Estimated Duration (minutes):", 
                                   min_value=15, max_value=120, value=45, step=15)
        
        teaching_style = st.selectbox("Teaching Style:", 
                                    ["Traditional", "Inquiry-Based", "Project-Based", 
                                     "Flipped Classroom", "Collaborative Learning", "Gamified"])
        
        accessibility_needs = st.multiselect("Accessibility Considerations:", 
                                          ["Visual Impairments", "Hearing Impairments", 
                                           "Attention Difficulties", "Language Barriers", 
                                           "Physical Disabilities", "None"],
                                          default=["None"])
    
    # Advanced content options
    with st.expander("Advanced Content Options", expanded=False):
        specific_content_topics = st.text_area("Specific Topics to Cover:", 
                                            placeholder="Enter specific topics to include, separated by new lines")
        
        include_examples = st.checkbox("Include Real-World Examples", value=True)
        include_assessments = st.checkbox("Include Assessment Activities", value=True)
        include_resources = st.checkbox("Include Additional Resources", value=True)
        
        content_format = st.selectbox("Output Format:", 
                                    ["Markdown", "Structured Text", "Rich Text", "Printable Layout"])
        
        additional_notes = st.text_area("Additional Instructions:", 
                                      placeholder="Any specific requirements or preferences for the content")
    
    # Generate content button
    if st.button("Generate Educational Content", use_container_width=True):
        if not content_subject:
            st.warning("Please enter a subject to generate content.")
        else:
            with st.spinner("Creating educational content..."):
                try:
                    # Create detailed prompt for content generation
                    content_prompt = f"Create a {content_type} for teaching {content_subject} at the {content_level} level. "
                    content_prompt += f"This should be designed for approximately {content_duration} minutes of educational time. "
                    content_prompt += f"Use a {teaching_style} teaching style. "
                    
                    if learning_objectives:
                        content_prompt += f"\n\nLearning Objectives:\n{learning_objectives}\n"
                    
                    if accessibility_needs and "None" not in accessibility_needs:
                        content_prompt += f"\nInclude accommodations for: {', '.join(accessibility_needs)}. "
                    
                    if specific_content_topics:
                        content_prompt += f"\n\nSpecific Topics to Cover:\n{specific_content_topics}\n"
                    
                    if include_examples:
                        content_prompt += "\nInclude relevant real-world examples and applications. "
                    
                    if include_assessments:
                        content_prompt += "\nInclude formative and summative assessment activities. "
                    
                    if include_resources:
                        content_prompt += "\nSuggest additional resources and materials. "
                    
                    content_prompt += f"\nFormat the content as {content_format}. "
                    
                    if additional_notes:
                        content_prompt += f"\nAdditional requirements: {additional_notes}"
                    
                    # Specify that this is for educational purposes
                    content_prompt += "\n\nThis content will be used for educational purposes, so ensure it is accurate, engaging, and pedagogically sound."
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Create a {content_type} on {content_subject} for {content_level} level using {teaching_style} approach"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.7),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(content_prompt)
                    
                    # Extract response text
                    generated_content = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": generated_content})
                    
                    # Display the generated content with download option
                    st.markdown("### Generated Educational Content")
                    st.markdown(generated_content)
                    
                    # Create a download option for the content
                    content_download = generated_content.encode()
                    st.download_button(
                        label="Download Content",
                        data=content_download,
                        file_name=f"{content_subject.replace(' ', '_')}_{content_type.replace(' ', '_')}.md",
                        mime="text/markdown"
                    )
                    
                    # Additional educator resources
                    st.markdown("### Teacher Resources")
                    
                    # Create tabs for different resources
                    resource_tabs = st.tabs(["Implementation Tips", "Extension Activities", "Modification Suggestions"])
                    
                    with resource_tabs[0]:
                        st.markdown("#### Tips for Implementation")
                        
                        # Generate implementation tips
                        implementation_prompt = f"Provide 5-7 practical tips for effectively implementing this {content_type} on {content_subject} for {content_level} students. Focus on classroom management, time optimization, and maximizing student engagement."
                        
                        # Create a generative model instance
                        implementation_response = model.generate_content(implementation_prompt)
                        st.markdown(implementation_response.text)
                    
                    with resource_tabs[1]:
                        st.markdown("#### Extension Activities")
                        
                        # Generate extension activities
                        extension_prompt = f"Suggest 3-5 extension activities for this {content_type} on {content_subject} for {content_level} students who finish early or need additional challenges. Include activities for different learning styles."
                        
                        # Create a generative model instance
                        extension_response = model.generate_content(extension_prompt)
                        st.markdown(extension_response.text)
                    
                    with resource_tabs[2]:
                        st.markdown("#### Modification Suggestions")
                        
                        # Generate modification suggestions
                        modification_prompt = f"Provide suggestions for modifying this {content_type} on {content_subject} for different learner needs, including struggling students, advanced students, and students with specific learning disabilities."
                        
                        # Create a generative model instance
                        modification_response = model.generate_content(modification_prompt)
                        st.markdown(modification_response.text)
                    
                except Exception as e:
                    st.error(f"Error generating content: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display content history
    st.markdown("### Previously Generated Content")
    content_history_count = 0
    
    for i in range(0, len(st.session_state.chat_history), 2):
        if i + 1 < len(st.session_state.chat_history):
            if "Create" in st.session_state.chat_history[i]["content"] and any(content_type in st.session_state.chat_history[i]["content"] for content_type in ["Lesson Plan", "Student Handout", "Lecture Notes", "Presentation", "Study Guide", "Infographic", "Worksheet"]):
                content_history_count += 1
                with st.expander(f"Content {content_history_count}: {st.session_state.chat_history[i]['content']}", expanded=False):
                    st.markdown(st.session_state.chat_history[i+1]["content"])
                    
                    # Add download button for each historical content
                    content_download = st.session_state.chat_history[i+1]["content"].encode()
                    st.download_button(
                        label="Download This Content",
                        data=content_download,
                        file_name=f"educational_content_{content_history_count}.md",
                        mime="text/markdown",
                        key=f"download_content_{content_history_count}"
                    )

# Concept Mapper tab
with selected_tab[7]:
    if st.session_state.current_mode != "Concept Mapper":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Concept Mapper"
    
    st.markdown("### AI Concept Mapper")
    st.markdown("Visualize connections between concepts and ideas to enhance understanding")
    
    # Concept map input
    main_concept = st.text_input("Main Concept/Topic:", placeholder="e.g., Photosynthesis, American Revolution, Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        detail_level = st.select_slider("Level of Detail:", 
                                      options=["Basic", "Moderate", "Detailed", "Comprehensive"], 
                                      value="Moderate")
        
        map_style = st.selectbox("Concept Map Style:", 
                               ["Hierarchical", "Spider/Radial", "Flowchart", "Mind Map", "Network Diagram"])
    
    with col2:
        relation_types = st.multiselect("Relationship Types to Include:", 
                                      ["Cause-Effect", "Part-Whole", "Sequential", "Comparative", 
                                       "Categorical", "Process-Based", "Functional"], 
                                      default=["Cause-Effect", "Part-Whole"])
        
        education_level = st.selectbox("Target Education Level:", 
                                     ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
    
    # Advanced mapping options
    with st.expander("Advanced Mapping Options", expanded=False):
        specific_subtopics = st.text_area("Include Specific Subtopics (optional):", 
                                        placeholder="Enter specific subtopics to include, separated by commas")
        
        excluded_subtopics = st.text_area("Exclude Subtopics (optional):", 
                                        placeholder="Enter subtopics to exclude, separated by commas")
        
        color_coding = st.checkbox("Use Color Coding for Different Concept Types", value=True)
        include_definitions = st.checkbox("Include Brief Definitions for Key Terms", value=True)
        include_examples = st.checkbox("Include Examples for Key Concepts", value=True)
        
        additional_instructions = st.text_area("Additional Instructions:", 
                                             placeholder="Any specific requirements or preferences for the concept map")
    
    # Generate concept map button
    if st.button("Generate Concept Map", use_container_width=True):
        if not main_concept:
            st.warning("Please enter a main concept to generate a map.")
        else:
            with st.spinner("Generating concept map..."):
                try:
                    # Create prompt for concept map generation
                    map_prompt = f"Create a detailed {map_style} concept map for '{main_concept}' at a {detail_level} level of detail. "
                    map_prompt += f"Target this for {education_level} level students. "
                    map_prompt += f"Include these relationship types: {', '.join(relation_types)}. "
                    
                    if specific_subtopics:
                        map_prompt += f"Include these specific subtopics: {specific_subtopics}. "
                    
                    if excluded_subtopics:
                        map_prompt += f"Exclude these subtopics: {excluded_subtopics}. "
                    
                    if color_coding:
                        map_prompt += "Use color coding to distinguish different types of concepts. "
                    
                    if include_definitions:
                        map_prompt += "Include brief definitions for key terms. "
                    
                    if include_examples:
                        map_prompt += "Include examples for key concepts. "
                    
                    if additional_instructions:
                        map_prompt += f"Additional instructions: {additional_instructions} "
                    
                    # Specify format for the response
                    map_prompt += """
                    Format your response as a Mermaid diagram using the flowchart syntax. For example:

                    ```mermaid
                    flowchart TD
                        A[Main Concept] --> B[Subtopic 1]
                        A --> C[Subtopic 2]
                        B --> D[Detail 1.1]
                        B --> E[Detail 1.2]
                        C --> F[Detail 2.1]
                        C --> G[Detail 2.2]
                    ```

                    Use appropriate Mermaid syntax for your chosen map style, and include clear relationships between concepts.
                    """
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Generate a {detail_level} {map_style} concept map for {main_concept} at {education_level} level"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.3),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(map_prompt)
                    
                    # Extract response text
                    map_content = response.text
                    
                    # Extract the Mermaid diagram code
                    mermaid_code = ""
                    if "```mermaid" in map_content and "```" in map_content.split("```mermaid", 1)[1]:
                        mermaid_code = map_content.split("```mermaid", 1)[1].split("```", 1)[0].strip()
                    else:
                        # If not properly formatted, attempt to extract anything that looks like a flowchart
                        import re
                        mermaid_match = re.search(r'flowchart [A-Z]{1,2}[\s\S]*?(?=```|$)', map_content)
                        if mermaid_match:
                            mermaid_code = mermaid_match.group(0)
                        else:
                            mermaid_code = "flowchart TD\n    A[Error: Could not generate proper concept map]"
                    
                    # Add the mermaid code to history
                    full_response = map_content.replace("```mermaid", "").replace("```", "")
                    st.session_state.chat_history.append({"role": "assistant", "content": full_response})
                    
                    # Display the concept map using Streamlit's mermaid component
                    st.markdown("### Generated Concept Map")
                    st.markdown(f"**{main_concept}** - {detail_level} Detail Level")
                    
                    # Display the mermaid diagram
                    st.markdown(f"```mermaid\n{mermaid_code}\n```")
                    
                    # Provide text explanation
                    st.markdown("### Map Explanation")
                    
                    # Generate explanation prompt
                    explanation_prompt = f"Given this concept map about {main_concept}, provide a brief explanation of the key relationships and concepts shown in the map. Make this explanation appropriate for {education_level} level students."
                    
                    # Generate explanation
                    explanation_response = model.generate_content(explanation_prompt + "\n\n" + mermaid_code)
                    st.markdown(explanation_response.text)
                    
                    # Educational activities based on the concept map
                    st.markdown("### Learning Activities")
                    
                    # Generate activities prompt
                    activities_prompt = f"Suggest 3-5 educational activities that teachers or students can do with this concept map on {main_concept}. Target these for {education_level} level students."
                    
                    # Generate activities
                    activities_response = model.generate_content(activities_prompt)
                    st.markdown(activities_response.text)
                    
                    # Provide download options
                    st.markdown("### Download Options")
                    
                    # Download as Mermaid code
                    mermaid_download = mermaid_code.encode()
                    st.download_button(
                        label="Download Mermaid Code",
                        data=mermaid_download,
                        file_name=f"{main_concept.replace(' ', '_')}_concept_map.mmd",
                        mime="text/plain",
                        key="download_mermaid"
                    )
                    
                    # Download as markdown with explanation
                    markdown_content = f"""# Concept Map: {main_concept}

## Map Diagram

```mermaid
{mermaid_code}
```

## Explanation

{explanation_response.text}

## Learning Activities

{activities_response.text}
"""
                    markdown_download = markdown_content.encode()
                    st.download_button(
                        label="Download Complete Package (Markdown)",
                        data=markdown_download,
                        file_name=f"{main_concept.replace(' ', '_')}_concept_map_package.md",
                        mime="text/markdown",
                        key="download_package"
                    )
                
                except Exception as e:
                    st.error(f"Error generating concept map: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display concept map history
    st.markdown("### Previously Generated Concept Maps")
    map_history_count = 0
    
    for i in range(0, len(st.session_state.chat_history), 2):
        if i + 1 < len(st.session_state.chat_history):
            if "Generate" in st.session_state.chat_history[i]["content"] and "concept map" in st.session_state.chat_history[i]["content"]:
                map_history_count += 1
                with st.expander(f"Map {map_history_count}: {st.session_state.chat_history[i]['content']}", expanded=False):
                    st.markdown(st.session_state.chat_history[i+1]["content"])

    
    st.markdown("### AI Concept Mapper")
    st.markdown("Visualize connections between concepts and ideas to enhance understanding")
    
    # Concept map input
    main_concept = st.text_input("Main Concept/Topic:", placeholder="e.g., Photosynthesis, American Revolution, Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        detail_level = st.select_slider("Level of Detail:", 
                                      options=["Basic", "Moderate", "Detailed", "Comprehensive"], 
                                      value="Moderate")
        
        map_style = st.selectbox("Concept Map Style:", 
                               ["Hierarchical", "Spider/Radial", "Flowchart", "Mind Map", "Network Diagram"])
    
    with col2:
        relation_types = st.multiselect("Relationship Types to Include:", 
                                      ["Cause-Effect", "Part-Whole", "Sequential", "Comparative", 
                                       "Categorical", "Process-Based", "Functional"], 
                                      default=["Cause-Effect", "Part-Whole"])
        
        education_level = st.selectbox("Target Education Level:", 
                                     ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"])
    
    # Advanced mapping options
    with st.expander("Advanced Mapping Options", expanded=False):
        specific_subtopics = st.text_area("Include Specific Subtopics (optional):", 
                                        placeholder="Enter specific subtopics to include, separated by commas")
        
        excluded_subtopics = st.text_area("Exclude Subtopics (optional):", 
                                        placeholder="Enter subtopics to exclude, separated by commas")
        
        color_coding = st.checkbox("Use Color Coding for Different Concept Types", value=True)
        include_definitions = st.checkbox("Include Brief Definitions for Key Terms", value=True)
        include_examples = st.checkbox("Include Examples for Key Concepts", value=True)
        
        additional_instructions = st.text_area("Additional Instructions:", 
                                             placeholder="Any specific requirements or preferences for the concept map")
    
    # Generate concept map button
    if st.button("Generate Concept Map", use_container_width=True):
        if not main_concept:
            st.warning("Please enter a main concept to generate a map.")
        else:
            with st.spinner("Generating concept map..."):
                try:
                    # Create prompt for concept map generation
                    map_prompt = f"Create a detailed {map_style} concept map for '{main_concept}' at a {detail_level} level of detail. "
                    map_prompt += f"Target this for {education_level} level students. "
                    map_prompt += f"Include these relationship types: {', '.join(relation_types)}. "
                    
                    if specific_subtopics:
                        map_prompt += f"Include these specific subtopics: {specific_subtopics}. "
                    
                    if excluded_subtopics:
                        map_prompt += f"Exclude these subtopics: {excluded_subtopics}. "
                    
                    if color_coding:
                        map_prompt += "Use color coding to distinguish different types of concepts. "
                    
                    if include_definitions:
                        map_prompt += "Include brief definitions for key terms. "
                    
                    if include_examples:
                        map_prompt += "Include examples for key concepts. "
                    
                    if additional_instructions:
                        map_prompt += f"Additional instructions: {additional_instructions} "
                    
                    # Specify format for the response
                    map_prompt += """
                    Format your response as a Mermaid diagram using the flowchart syntax. For example:

                    ```mermaid
                    flowchart TD
                        A[Main Concept] --> B[Subtopic 1]
                        A --> C[Subtopic 2]
                        B --> D[Detail 1.1]
                        B --> E[Detail 1.2]
                        C --> F[Detail 2.1]
                        C --> G[Detail 2.2]
                    ```

                    Use appropriate Mermaid syntax for your chosen map style, and include clear relationships between concepts.
                    """
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f['content']}")
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

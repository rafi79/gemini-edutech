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
model_name = "gemini-1.5-flash"  # Using a model that actually exists in the API

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

# History management
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Learning Assistant"

# Header
st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
st.markdown('<div class="edu-subheader">Powered by Google Gemini | Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)

# App modes
modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Quiz Generator", "Concept Mapper"]
selected_tab = st.tabs(modes)

# Learning Assistant tab
with selected_tab[0]:
    if st.session_state.current_mode != "Learning Assistant":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Learning Assistant"
    
    st.markdown("### Your AI Learning Companion")
    st.markdown("Ask any question about any subject, request explanations, or get help with homework")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_area("Enter your question:", height=100, 
                                  placeholder="e.g., Explain quantum entanglement in simple terms" if not st.session_state.chat_history else "")
    with col2:
        learning_level = st.selectbox("Learning Level:", 
                                     ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"])
        learning_style = st.selectbox("Learning Style:", 
                                     ["Visual", "Textual", "Interactive", "Example-based", "Socratic"])
    
    if st.button("Submit", use_container_width=True):
        if user_input:
            # Add system context based on selected options
            system_context = f"You are EduGenius, an educational AI tutor. Adapt your explanation for {learning_level} level students. Use a {learning_style} learning style in your response."
            
            # Create prompt with the system context
            prompt = f"{system_context}\n\nStudent question: {user_input}"
            
            # Add to history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            with st.spinner("Generating response..."):
                try:
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(prompt)
                    
                    # Extract response text
                    response_text = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
    
    # Display chat history
    st.markdown("### Conversation")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**EduGenius:** {message['content']}")
        st.markdown("---")

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
        
        if st.button("Analyze Image", use_container_width=True):
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

# Quiz Generator tab
with selected_tab[3]:
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Quiz Generator"
    
    st.markdown("### AI Quiz Generator")
    st.markdown("Generate personalized quizzes on any subject with adaptive difficulty")
    
    col1, col2 = st.columns(2)
    
    with col1:
        subject = st.text_input("Subject:", placeholder="e.g., World History, Calculus, Chemistry")
        topic = st.text_input("Specific Topic:", placeholder="e.g., French Revolution, Derivatives, Periodic Table")
        
    with col2:
        difficulty = st.select_slider("Difficulty Level:", options=["Beginner", "Elementary", "Intermediate", "Advanced", "Expert"])
        question_types = st.multiselect("Question Types:", 
                                       ["Multiple Choice", "True/False", "Short Answer", "Essay", "Matching"], 
                                       default=["Multiple Choice"])
    
    num_questions = st.slider("Number of Questions:", min_value=5, max_value=30, value=10, step=5)
    
    include_answers = st.checkbox("Include Answers and Explanations", value=True)
    adaptive_feedback = st.checkbox("Generate Adaptive Feedback", value=True)
    
    if st.button("Generate Quiz", use_container_width=True):
        if subject and topic:
            with st.spinner("Generating quiz..."):
                try:
                    # Create quiz generation prompt
                    quiz_prompt = f"Generate a {difficulty} level quiz on {subject}: {topic}. "
                    quiz_prompt += f"Include {num_questions} questions of the following types: {', '.join(question_types)}. "
                    
                    if include_answers:
                        quiz_prompt += "Include correct answers and detailed explanations. "
                    
                    if adaptive_feedback:
                        quiz_prompt += "For each question, provide adaptive feedback for both correct and incorrect responses. "
                    
                    quiz_prompt += "Format the quiz in a clean, organized way that's easy to read and implement in an educational setting."
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Generate a {difficulty} level quiz with {num_questions} questions on {subject}: {topic}"})
                    
                    # Create a generative model instance
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        generation_config=get_generation_config(temperature=0.7),
                        safety_settings=safety_settings
                    )
                    
                    # Generate content
                    response = model.generate_content(quiz_prompt)
                    
                    # Extract response text
                    response_text = response.text
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
        else:
            st.warning("Please enter both a subject and a specific topic.")
    
    # Display generated quiz
    if st.session_state.chat_history:
        st.markdown("### Generated Quiz")
        # Show only the most recent quiz
        for i in range(len(st.session_state.chat_history)-1, -1, -1):
            if st.session_state.chat_history[i]["role"] == "assistant":
                st.markdown(st.session_state.chat_history[i]["content"])
                break

# Concept Mapper tab
with selected_tab[4]:
    if st.session_state.current_mode != "Concept Mapper":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Concept Mapper"
    
    st.markdown("### AI Concept Mapper")
    st.markdown("Create visual concept maps to understand relationships between ideas and topics")
    
    main_concept = st.text_input("Main Concept/Topic:", placeholder="e.g., Photosynthesis, Democracy, Machine Learning")
    
    col1, col2 = st.columns(2)
    with col1:
        depth = st.slider("Map Depth:", min_value=1, max_value=5, value=3, 
                         help="How many levels of related concepts to include")
    with col2:
        breadth = st.slider("Map Breadth:", min_value=2, max_value=8, value=4, 
                           help="How many related concepts per level")
    
    map_style = st.radio("Map Style:", ["Hierarchical", "Network", "Mind Map", "Process Flow"])
    
    additional_context = st.text_area("Additional Context:", 
                                     placeholder="Add any specific focus areas or context for the concept map")
    
    if st.button("Generate Concept Map", use_container_width=True):
        if main_concept:
            with st.spinner("Generating concept map..."):
                try:
                    # Create concept map generation prompt
                    map_prompt = f"Generate a {map_style} concept map for '{main_concept}' with a depth of {depth} levels and {breadth} concepts per level. "
                    
                    if additional_context:
                        map_prompt += f"Additional context: {additional_context}. "
                    
                    map_prompt += "Include key relationships, definitions, and connections between concepts. "
                    map_prompt += "Format the output as a text-based concept map structure with clear indentation and relationship indicators."
                    
                    # Add to history
                    st.session_state.chat_history.append({"role": "user", "content": f"Generate a {map_style} concept map for '{main_concept}'"})
                    
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
                
                except Exception as e:
                    st.error(f"Error generating concept map: {str(e)}")
                    st.session_state.chat_history.append({"role": "assistant", "content": f"I apologize, but I encountered an error: {str(e)}"})
        else:
            st.warning("Please enter a main concept or topic.")
    
    # Display generated concept map
    if st.session_state.chat_history:
        st.markdown("### Generated Concept Map")
        # Show only the most recent concept map
        for i in range(len(st.session_state.chat_history)-1, -1, -1):
            if st.session_state.chat_history[i]["role"] == "assistant":
                st.markdown(st.session_state.chat_history[i]["content"])
                break

# Add features and benefits showcase in the sidebar
with st.sidebar:
    st.markdown("## EduGenius Features")
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">Multimodal Learning</div>
        <p>Process text, images, documents, and more for comprehensive understanding</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-title">Adaptive Learning</div>
        <p>Personalized responses based on learning level, style, and needs</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">Visual Concept Mapping</div>
        <p>Transform complex topics into visual knowledge structures</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">Dynamic Assessments</div>
        <p>Generate tailored quizzes with adaptive feedback</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📚</div>
        <div class="feature-title">Document Intelligence</div>
        <p>Extract insights, summaries, and key concepts from study materials</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### Powered by Google Gemini")
    st.markdown("* 1M token input context")
    st.markdown("* Multimodal capabilities")
    st.markdown("* Latest knowledge (June 2024)")
    st.markdown("* Advanced reasoning")

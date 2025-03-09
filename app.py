import streamlit as st
import os
import google.generativeai as genai

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

# Initialize session state
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "Learning Assistant"

if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm your AI learning companion. What would you like to learn about today?"}
    ]

# Gemini API functions integrated directly into app.py
def initialize_genai():
    """Initialize the Gemini API client with the API key."""
    # Get API key from environment or use the provided one
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyCagQKSSGGM-VcoOwIVEFp2l8dX-FIvTcA")
    genai.configure(api_key=api_key)
    return True

def generate_text_content(prompt, temperature=0.7, model_name=None):
    """Generate content from a text prompt."""
    # Initialize API
    initialize_genai()
    
    # Set default model if not provided
    if not model_name:
        model_name = "gemini-2.0-flash"
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Generate content
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

def generate_multimodal_content(prompt, media_data, media_type="image/jpeg", temperature=0.7):
    """Generate content from a text prompt and media data."""
    # Initialize API
    initialize_genai()
    
    # Use gemini-1.5-flash for multimedia content
    model_name = "gemini-1.5-flash"
    
    # Create generation config
    generation_config = {
        "temperature": temperature,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    
    try:
        # Create the model
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        # Generate content with media
        response = model.generate_content([
            prompt,
            {"mime_type": media_type, "data": media_data}
        ])
        return response.text
        
    except Exception as e:
        st.error(f"Error generating content from {media_type}: {str(e)}")
        return f"I apologize, but I encountered an error processing your media: {str(e)}"

def analyze_video(video_data, analysis_types, focus="General Analysis"):
    """Analyze video content."""
    # Initialize API
    initialize_genai()
    
    # Create prompt for video analysis
    analysis_prompt = f"""
    You are EduGenius, an AI video learning assistant.
    
    Please analyze this educational video and provide insights on the following aspects:
    {', '.join(analysis_types)}
    
    Focus on {focus} educational aspects.
    
    Provide a detailed analysis organized with markdown headings, including:
    1. Content summary
    2. Key educational moments with timestamps
    3. Educational value assessment
    4. Suggested learning activities
    
    Format your response in clear, organized markdown.
    """
    
    # Use multimodal content generation for video
    return generate_multimodal_content(
        prompt=analysis_prompt,
        media_data=video_data,
        media_type="video/mp4",
        temperature=0.2  # Lower temperature for more factual analysis
    )

# Functions for displaying welcome screen
def show_welcome_screen():
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
    </div>
    """, unsafe_allow_html=True)
    
    # Button to dismiss welcome screen
    if st.button("Get Started", key="welcome_dismiss"):
        st.session_state.first_visit = False
        st.rerun()  # Changed from experimental_rerun() to rerun()

# Function to render chat messages
def render_chat_message(message):
    if message["role"] == "user":
        st.markdown(f"<div style='background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color: #e6f3ff; padding: 10px; border-radius: 10px; margin-bottom: 10px;'><strong>EduGenius:</strong> {message['content']}</div>", unsafe_allow_html=True)

# Functions for different pages
def render_learning_assistant():
    st.markdown("### Your AI Learning Companion")
    st.markdown("Ask any question about any subject, request explanations, or get help with homework")
    
    # Learning settings in an expandable section
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
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.tutor_messages:
            render_chat_message(message)
    
    # Chat input area
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_area("Your question:", height=80, key="tutor_input",
                                placeholder="Type your question here... (e.g., Explain quantum entanglement in simple terms)")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        submit_button = st.button("Send", use_container_width=True, key="tutor_submit")
    
    # Process user input
    if submit_button and user_input:
        # Add user message to chat
        st.session_state.tutor_messages.append({"role": "user", "content": user_input})
        
        # Create AI prompt
        prompt = f"""You are EduGenius, an educational AI tutor.
Adapt your explanation for {learning_level} level students.
Use a {learning_style} learning style in your response.

Student question: {user_input}

Provide a clear, helpful, and engaging educational response."""
        
        with st.spinner("Generating response..."):
            # Generate AI response using Gemini
            ai_response = generate_text_content(prompt)
            
            # Add AI response to chat
            st.session_state.tutor_messages.append({"role": "assistant", "content": ai_response})
            
            # Clear the input area
            st.session_state.tutor_input = ""
            
            # Rerun to update the chat display
            st.rerun()

def render_document_analysis():
    st.markdown("### AI-Powered Document Analysis")
    st.markdown("Upload study materials, textbooks, or notes for AI analysis and insights")
    
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, or TXT):", type=["pdf", "docx", "txt"])
    
    if uploaded_file is not None:
        analysis_type = st.multiselect("Select analysis types:", 
                                      ["Key Concepts Extraction", "Summary Generation", 
                                       "Difficulty Assessment", "Concept Relations", 
                                       "Generate Study Questions"])
        
        if st.button("Analyze Document", use_container_width=True):
            # Simulate document analysis
            st.success(f"Document '{uploaded_file.name}' uploaded successfully!")
            st.info("This is a simplified demo. In a real implementation, this would analyze your document using the Gemini API.")
            
            # Display simulated analysis
            st.markdown(f"""
            ## Document Analysis Results
            
            ### Summary
            This is a simulated summary of your document. In a real implementation, this would provide an actual summary of the content.
            
            ### Key Concepts
            - Simulated Key Concept 1
            - Simulated Key Concept 2
            - Simulated Key Concept 3
            
            ### Difficulty Assessment
            This document appears to be at an intermediate level, suitable for high school to undergraduate students.
            
            ### Study Questions
            1. Simulated study question 1?
            2. Simulated study question 2?
            3. Simulated study question 3?
            """)

def render_visual_learning():
    st.markdown("### Visual Learning Assistant")
    st.markdown("Upload images of diagrams, problems, or visual concepts for AI explanation")
    
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        
        query_type = st.radio("What would you like to do with this image?", 
                             ["Explain the concept shown", "Identify elements", 
                              "Solve the problem shown", "Create a related exercise"])
        
        specific_question = st.text_input("Any specific questions about this image?", 
                                         placeholder="e.g., What does this diagram represent?")
        
        if st.button("Analyze Image", use_container_width=True, key="main_analysis"):
            with st.spinner("Analyzing image with AI..."):
                try:
                    # Get image data
                    image_bytes = uploaded_image.getvalue()
                    
                    # Create prompt based on query type
                    if query_type == "Explain the concept shown":
                        prompt = "Please explain the educational concept shown in this image. Identify key elements and their relationships."
                    elif query_type == "Identify elements":
                        prompt = "Please identify and label all significant elements in this image. Explain their educational relevance."
                    elif query_type == "Solve the problem shown":
                        prompt = "Please solve the problem shown in this image. Explain your solution step by step."
                    elif query_type == "Create a related exercise":
                        prompt = "Based on this image, please create a related educational exercise that would reinforce the concepts shown."
                    
                    # Add specific question if provided
                    if specific_question:
                        prompt += f"\n\nSpecific question: {specific_question}"
                    
                    # Call Gemini API to analyze image
                    analysis_result = generate_multimodal_content(
                        prompt=prompt,
                        media_data=image_bytes,
                        media_type="image/jpeg",
                        temperature=0.2
                    )
                    
                    # Display analysis results
                    st.markdown("## Image Analysis Results")
                    st.markdown(analysis_result)
                    
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")

def render_audio_analysis():
    st.markdown("### Audio Learning Assistant")
    st.markdown("Upload audio files for transcription, analysis, and educational insights")
    
    uploaded_audio = st.file_uploader("Upload an audio file:", type=["mp3", "wav", "m4a", "ogg"])
    
    if uploaded_audio is not None:
        st.audio(uploaded_audio, format="audio/mp3")
        
        analysis_options = st.multiselect("Select analysis types:", 
                                     ["Transcription", "Content Summary", 
                                      "Key Concepts Extraction", "Generate Quiz from Audio",
                                      "Language Analysis", "Vocabulary Extraction"])
        
        if st.button("Analyze Audio", use_container_width=True):
            # Simulate audio analysis
            st.success(f"Audio file '{uploaded_audio.name}' uploaded successfully!")
            st.info("This is a simplified demo. In a real implementation, this would analyze your audio using the Gemini API.")
            
            # Display simulated analysis
            st.markdown(f"""
            ## Audio Analysis Results
            
            ### Transcription
            This is a simulated transcription of your audio file. In a real implementation, this would provide an actual transcription of the spoken content.
            
            ### Content Summary
            This audio appears to contain educational content related to [simulated subject]. The main topics covered include several key areas relevant to learners.
            
            ### Key Concepts Identified
            - Simulated Concept 1: Brief explanation
            - Simulated Concept 2: Brief explanation
            - Simulated Concept 3: Brief explanation
            
            ### Educational Value
            This audio would be suitable for students at the [level] level. It effectively explains concepts and could be integrated into curriculum for courses.
            """)

def render_video_learning():
    """Render the Video Learning page with Gemini API integration."""
    st.markdown("### Video Learning Assistant")
    st.markdown("Upload educational videos for AI analysis, summaries, and interactive learning")
    
    uploaded_video = st.file_uploader("Upload a video file:", type=["mp4", "mov", "avi", "mkv"])
    
    if uploaded_video is not None:
        st.video(uploaded_video)
        
        video_analysis_options = st.multiselect("Select analysis types:", 
                                    ["Video Transcription", "Content Summary", 
                                     "Visual Concept Detection", "Key Moments Identification",
                                     "Generate Quiz from Video", "Educational Value Assessment"])
        
        video_focus = st.selectbox("Educational Focus:", 
                                ["General Analysis", "STEM Concepts", "Humanities Focus", 
                                 "Language Learning", "Procedural Skills", "Critical Thinking"])
        
        if st.button("Analyze Video", use_container_width=True):
            with st.spinner("Processing video with AI..."):
                try:
                    # Get video data
                    video_bytes = uploaded_video.getvalue()
                    
                    # Call analyze_video function to analyze video
                    analysis_result = analyze_video(
                        video_data=video_bytes,
                        analysis_types=video_analysis_options,
                        focus=video_focus
                    )
                    
                    # Success message
                    st.success(f"Video file '{uploaded_video.name}' analyzed successfully!")
                    
                    # Display analysis results
                    st.markdown(analysis_result)
                    
                    # Store analysis for later reference
                    if "video_analysis" not in st.session_state:
                        st.session_state.video_analysis = {}
                    
                    st.session_state.video_analysis[uploaded_video.name] = {
                        "result": analysis_result,
                        "analysis_types": video_analysis_options,
                        "focus": video_focus
                    }
                    
                    # Show interactive video chat option
                    st.markdown("### Ask Questions About This Video")
                    video_question = st.text_input(
                        "What would you like to know about this video?",
                        placeholder="e.g., Can you explain the main concept in more detail?"
                    )
                    
                    if st.button("Ask", key="video_question_button"):
                        if video_question:
                            with st.spinner("Generating response..."):
                                try:
                                    # Create prompt using the analysis and the question
                                    prompt = f"""
                                    Based on this video analysis:
                                    
                                    {analysis_result}
                                    
                                    Answer the following question about the video:
                                    {video_question}
                                    
                                    Provide a helpful, educational response.
                                    """
                                    
                                    # Generate response
                                    response = generate_text_content(prompt)
                                    
                                    # Display response
                                    st.markdown("### Response")
                                    st.markdown(response)
                                    
                                except Exception as e:
                                    st.error(f"Error generating response: {str(e)}")
                
                except Exception as e:
                    st.error(f"Error analyzing video: {str(e)}")
                    st.markdown(f"""
                    ## Analysis Error
                    
                    I'm sorry, but I encountered an error analyzing your video:
                    
                    {str(e)}
                    
                    This might be due to:
                    - Video format incompatibility
                    - Video file size limitations
                    - Temporary API issues
                    
                    Please try again with a different video file or try later.
                    """)

def render_quiz_generator():
    st.markdown("### Educational Quiz Generator")
    st.markdown("Create customized quizzes for any subject or topic")
    
    quiz_topic = st.text_input("Quiz Topic:", placeholder="e.g., Photosynthesis, World War II, Linear Algebra")
    
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.select_slider("Difficulty Level:", 
                                   options=["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"],
                                   value="High School")
        
    with col2:
        question_count = st.slider("Number of Questions:", min_value=3, max_value=20, value=10)
        question_format = st.selectbox("Question Format:", ["Multiple Choice", "True/False", "Short Answer", "Mixed Formats"])
    
    if st.button("Generate Quiz", use_container_width=True):
        if not quiz_topic:
            st.warning("Please enter a quiz topic.")
        else:
            with st.spinner(f"Generating {difficulty} level quiz on {quiz_topic}..."):
                try:
                    # Create prompt for quiz generation
                    prompt = f"""
                    Generate a {difficulty} level educational quiz on {quiz_topic}.
                    
                    Create {question_count} questions in {question_format} format.
                    Include answers and brief explanations for each question.
                    Ensure questions assess different cognitive levels, from recall to application and analysis.
                    Format your response in clear, organized markdown.
                    """
                    
                    # Generate quiz content
                    quiz_content = generate_text_content(prompt, temperature=0.3)
                    
                    # Display quiz
                    st.markdown(quiz_content)
                    
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")

def render_concept_mapper():
    st.markdown("### Educational Concept Mapper")
    st.markdown("Visualize connections between ideas to enhance understanding and retention")
    
    main_concept = st.text_input("Main Concept/Topic:", placeholder="e.g., Photosynthesis, Democracy, Machine Learning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        complexity = st.select_slider("Complexity Level:", 
                                   options=["Basic", "Intermediate", "Advanced", "Comprehensive"],
                                   value="Intermediate")
        
    with col2:
        educational_level = st.selectbox("Educational Level:", 
                                      ["Elementary", "Middle School", "High School", "Undergraduate", "Graduate"],
                                      index=2)
    
    if st.button("Generate Concept Map", use_container_width=True):
        if not main_concept:
            st.warning("Please enter a main concept.")
        else:
            # Simulate concept map generation
            st.success(f"Generating {complexity} concept map for {main_concept}!")
            st.info("This is a simplified demo. In a real implementation, this would generate a concept map using the Gemini API.")
            
            # Display simulated concept map
            st.markdown(f"""
            ## {main_concept} Concept Map ({complexity} Level)
            
            ### Core Concept
            - **{main_concept}**
              - Subconcept 1
                - Related idea 1.1
                - Related idea 1.2
              - Subconcept 2
                - Related idea 2.1
                - Related idea 2.2
              - Subconcept 3
                - Related idea 3.1
                - Related idea 3.2
            
            ### Relationships
            - {main_concept} → Subconcept 1: [simulated relationship]
            - {main_concept} → Subconcept 2: [simulated relationship]
            - {main_concept} → Subconcept 3: [simulated relationship]
            - Subconcept 1 ↔ Subconcept 2: [simulated cross-relationship]
            
            *Note: In a real implementation, this would generate a visual concept map with proper relationships and hierarchies.*
            """)

# Main application
def main():
    # Display header
    st.markdown('<div class="edu-header">EduGenius</div>', unsafe_allow_html=True)
    st.markdown('<div class="edu-subheader">Powered by Google Gemini | Your AI-Enhanced Learning Companion</div>', unsafe_allow_html=True)
    
    # Display welcome screen on first visit
    if st.session_state.first_visit:
        show_welcome_screen()
    else:
        # App modes
        modes = ["Learning Assistant", "Document Analysis", "Visual Learning", "Audio Analysis", "Video Learning", "Quiz Generator", "Concept Mapper"]
        selected_tab = st.tabs(modes)
        
        # Learning Assistant tab
        with selected_tab[0]:
            render_learning_assistant()
        
        # Document Analysis tab
        with selected_tab[1]:
            render_document_analysis()
        
        # Visual Learning tab
        with selected_tab[2]:
            render_visual_learning()
        
        # Audio Analysis tab
        with selected_tab[3]:
            render_audio_analysis()
        
        # Video Learning tab
        with selected_tab[4]:
            render_video_learning()
        
        # Quiz Generator tab
        with selected_tab[5]:
            render_quiz_generator()
        
        # Concept Mapper tab
        with selected_tab[6]:
            render_concept_mapper()

if __name__ == "__main__":
    main()

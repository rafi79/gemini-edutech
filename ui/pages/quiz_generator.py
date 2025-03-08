"""
Quiz Generator page module for the EduGenius application.
This provides functionality for generating educational quizzes.
"""

import streamlit as st
import json
from services.gemini_service import generate_text_content
from utils.prompt_utils import create_quiz_generation_prompt

def render():
    """Render the Quiz Generator page."""
    # Reset state if switching to this mode
    if st.session_state.current_mode != "Quiz Generator":
        st.session_state.current_mode = "Quiz Generator"
        # Clear any existing quiz data
        if "generated_quiz" in st.session_state:
            del st.session_state.generated_quiz
    
    # Page header
    st.markdown("### Educational Quiz Generator")
    st.markdown("Create customized quizzes for any subject or topic")
    
    # Quiz settings
    with st.container():
        st.markdown("#### Quiz Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Topic and difficulty
            quiz_topic = st.text_input(
                "Quiz Topic:", 
                placeholder="e.g., Photosynthesis, World War II, Linear Algebra"
            )
            
            difficulty = st.select_slider(
                "Difficulty Level:", 
                options=["Elementary", "Middle School", "High School", "Undergraduate", "Graduate", "Expert"],
                value="High School"
            )
        
        with col2:
            # Question count and format
            question_count = st.slider("Number of Questions:", min_value=3, max_value=20, value=10)
            
            format_type = st.selectbox(
                "Question Format:", 
                [
                    "Multiple Choice", 
                    "True/False", 
                    "Short Answer", 
                    "Fill in the Blank", 
                    "Mixed Formats"
                ]
            )
    
    # Advanced options
    with st.expander("Advanced Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Specific focus and alignment
            specific_focus = st.text_input(
                "Specific Focus (Optional):", 
                placeholder="e.g., Causes and effects, Practical applications"
            )
            
            educational_standards = st.text_input(
                "Educational Standards Alignment (Optional):", 
                placeholder="e.g., Common Core, NGSS"
            )
        
        with col2:
            # Time limit and additional instructions
            time_limit = st.slider("Suggested Time Limit (minutes):", min_value=5, max_value=60, value=15)
            
            additional_instructions = st.text_area(
                "Additional Instructions (Optional):", 
                placeholder="e.g., Include diagrams, Focus on critical thinking"
            )
    
    # Generate quiz button
    if st.button("Generate Quiz", use_container_width=True, key="generate_quiz_button"):
        if not quiz_topic:
            st.warning("Please enter a quiz topic.")
        else:
            with st.spinner(f"Creating {difficulty} level quiz on {quiz_topic}..."):
                try:
                    # Create additional context from advanced options
                    additional_context = ""
                    if specific_focus:
                        additional_context += f"\nFocus specifically on: {specific_focus}"
                    if educational_standards:
                        additional_context += f"\nAlign with these educational standards: {educational_standards}"
                    if additional_instructions:
                        additional_context += f"\nAdditional instructions: {additional_instructions}"
                    
                    # Create prompt for quiz generation
                    prompt = create_quiz_generation_prompt(
                        topic=quiz_topic,
                        difficulty=difficulty,
                        question_count=question_count,
                        format_type=format_type
                    )
                    
                    # Add additional context if any
                    if additional_context:
                        prompt += additional_context
                    
                    # Generate quiz content
                    quiz_content = generate_text_content(
                        prompt=prompt,
                        temperature=0.3  # Lower temperature for more consistent quiz generation
                    )
                    
                    # Store generated quiz in session state
                    st.session_state.generated_quiz = {
                        "content": quiz_content,
                        "metadata": {
                            "topic": quiz_topic,
                            "difficulty": difficulty,
                            "question_count": question_count,
                            "format": format_type,
                            "time_limit": time_limit
                        }
                    }
                
                except Exception as e:
                    st.error(f"Error generating quiz: {str(e)}")
    
    # Display generated quiz if available
    if "generated_quiz" in st.session_state:
        display_generated_quiz(st.session_state.generated_quiz)


def display_generated_quiz(quiz_data):
    """
    Display a generated quiz with options for export and customization.
    
    Args:
        quiz_data (dict): Dictionary containing quiz content and metadata
    """
    st.markdown("### Generated Quiz")
    
    # Quiz metadata
    metadata = quiz_data["metadata"]
    st.markdown(f"""
    **Topic:** {metadata['topic']}  
    **Difficulty:** {metadata['difficulty']}  
    **Format:** {metadata['format']}  
    **Suggested Time:** {metadata['time_limit']} minutes  
    """)
    
    # Display quiz content in a container with scrolling
    with st.container():
        st.markdown(quiz_data["content"])
    
    # Export options
    st.markdown("### Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Copy to Clipboard", use_container_width=True):
            # Use JavaScript to copy to clipboard
            st.markdown(
                f"""
                <script>
                    navigator.clipboard.writeText({json.dumps(quiz_data['content'])});
                </script>
                """,
                unsafe_allow_html=True
            )
            st.success("Quiz copied to clipboard!")
    
    with col2:
        st.download_button(
            label="Download as Text",
            data=quiz_data["content"],
            file_name=f"quiz_{metadata['topic'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        if st.button("Generate New Version", use_container_width=True):
            # Clear current quiz and rerun
            del st.session_state.generated_quiz
            st.experimental_rerun()
    
    # Quiz customization
    st.markdown("### Customize Quiz")
    
    customization_option = st.selectbox(
        "Select customization option:",
        [
            "Make it easier",
            "Make it harder",
            "Add more questions",
            "Reduce number of questions",
            "Focus more on practical applications",
            "Focus more on theoretical concepts",
            "Add explanations to answers",
            "Custom modification"
        ]
    )
    
    custom_instruction = ""
    if customization_option == "Custom modification":
        custom_instruction = st.text_area(
            "Enter custom modification instructions:",
            placeholder="e.g., Add more visual questions, Focus on historical context"
        )
    
    if st.button("Apply Customization", use_container_width=True):
        with st.spinner("Customizing quiz..."):
            try:
                # Prepare customization prompt
                instruction = customization_option if customization_option != "Custom modification" else custom_instruction
                
                customization_prompt = f"""
                I have a quiz on {metadata['topic']} with the following specifications:
                - Difficulty level: {metadata['difficulty']}
                - Question format: {metadata['format']}
                - Question count: {metadata['question_count']}
                
                Here is the current quiz:
                {quiz_data['content']}
                
                Please modify this quiz to {instruction}. Maintain the same overall structure and format.
                """
                
                # Generate customized quiz
                customized_content = generate_text_content(
                    prompt=customization_prompt,
                    temperature=0.3
                )
                
                # Update quiz in session state
                st.session_state.generated_quiz["content"] = customized_content
                
                # Add customization to metadata
                st.session_state.generated_quiz["metadata"]["customizations"] = st.session_state.generated_quiz["metadata"].get("customizations", []) + [instruction]
                
                # Show success message
                st.success("Quiz customized successfully!")
                st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Error customizing quiz: {str(e)}")

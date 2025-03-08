"""
Learning Assistant page module for the EduGenius application.
This provides a chat-based interface for asking educational questions.
"""

import streamlit as st
from services.gemini_service import generate_text_content, generate_multimodal_content
from ui.styles import render_chat_history
from ui.components import chat_input_area, media_upload_area, learning_settings_expander

def render():
    """Render the Learning Assistant page."""
    # Reset chat history if switching to this mode
    if st.session_state.current_mode != "Learning Assistant":
        st.session_state.tutor_messages = []
        st.session_state.current_mode = "Learning Assistant"
    
    # Initialize tutor messages if not exists
    if "tutor_messages" not in st.session_state:
        st.session_state.tutor_messages = [
            {"role": "assistant", "content": "👋 Hi there! I'm your AI learning companion. What would you like to learn about today?"}
        ]
    
    # Page header
    st.markdown("### Your AI Learning Companion")
    st.markdown("Ask any question about any subject, request explanations, or get help with homework")
    
    # Learning settings section
    settings = learning_settings_expander()
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        render_chat_history(st.session_state.tutor_messages)
    
    # Chat input area
    st.markdown("<br>", unsafe_allow_html=True)
    user_input, submit_button = chat_input_area(
        key_prefix="tutor", 
        placeholder="Type your question here... (e.g., Explain quantum entanglement in simple terms)"
    )
    
    # Media upload section
    upload_option, uploaded_file = media_upload_area(key_prefix="tutor")
    
    # Process user input when submit button is clicked
    if submit_button and user_input:
        # Add user message to chat
        st.session_state.tutor_messages.append({"role": "user", "content": user_input})
        
        # Create system context based on selected options
        system_context = f"You are EduGenius, an educational AI tutor. Adapt your explanation for {settings['learning_level']} level students. Use a {settings['learning_style']} learning style in your response."
        
        # Create conversation history for context
        conversation_history = ""
        if settings['memory_option'] and len(st.session_state.tutor_messages) > 1:
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
        
        if hasattr(st.session_state, 'tutor_current') and st.session_state.tutor_current is not None:
            has_multimedia = True
            media_type = st.session_state.tutor_current["type"].lower()
            media_bytes = st.session_state.tutor_current["file"].getvalue()
            
            # Add multimedia context to prompt
            prompt += f"\n\nNote: The student has also uploaded a {media_type} file named '{st.session_state.tutor_current['name']}'. Please incorporate this into your response if relevant."
        
        with st.spinner("Thinking..."):
            try:
                # Generate response based on whether there's multimedia
                if has_multimedia and media_type == "image":
                    response_text = generate_multimodal_content(
                        prompt=prompt,
                        media_data=media_bytes,
                        media_type="image/jpeg",  # Adjust based on actual file type
                        temperature=0.7
                    )
                else:
                    # For text-only or other media types (which we're simulating for now)
                    response_text = generate_text_content(
                        prompt=prompt,
                        temperature=0.7
                    )
                
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

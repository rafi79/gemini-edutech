"""
Visual Learning page module for the EduGenius application.
This provides functionality for analyzing images and visual content.
"""

import streamlit as st
from PIL import Image
from services.gemini_service import generate_multimodal_content
from ui.styles import render_chat_history
from ui.components import chat_input_area

def render():
    """Render the Visual Learning page."""
    # Reset chat history if switching to this mode
    if st.session_state.current_mode != "Visual Learning":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Visual Learning"
        # Reset image chat history
        if "image_chat_history" in st.session_state:
            st.session_state.image_chat_history = []
    
    # Initialize image chat history if not exists
    if "image_chat_history" not in st.session_state:
        st.session_state.image_chat_history = []
    
    # Page header
    st.markdown("### Visual Learning Assistant")
    st.markdown("Upload images of diagrams, problems, or visual concepts for AI explanation")
    
    # Image upload section
    uploaded_image = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        # Query type selection
        query_type = st.radio(
            "What would you like to do with this image?", 
            [
                "Explain the concept shown", 
                "Identify elements",
                "Solve the problem shown", 
                "Create a related exercise"
            ]
        )
        
        # Option for specific questions
        specific_question = st.text_input(
            "Any specific questions about this image?", 
            placeholder="e.g., What does this diagram represent?"
        )
        
        # Image chat section
        st.markdown("### Image Chat")
        st.info("You can have a conversation about this image by entering questions below.")
        
        # Display image chat history
        chat_container = st.container()
        with chat_container:
            render_chat_history(st.session_state.image_chat_history)
        
        # Chat input for image
        image_chat_input, image_chat_button = chat_input_area(
            key_prefix="image_chat",
            placeholder="e.g., Can you explain what's happening in this diagram?"
        )
        
        # Process image chat input
        if image_chat_button and image_chat_input:
            # Add to image chat history
            st.session_state.image_chat_history.append({"role": "user", "content": image_chat_input})
            
            with st.spinner("Analyzing..."):
                try:
                    # Convert image for API
                    img_byte_arr = uploaded_image.getvalue()
                    
                    # Generate multimodal content
                    response_text = generate_multimodal_content(
                        prompt=image_chat_input,
                        media_data=img_byte_arr,
                        media_type="image/jpeg",  # Adjust based on actual file type
                        temperature=0.2
                    )
                    
                    # Add response to chat history
                    st.session_state.image_chat_history.append({"role": "assistant", "content": response_text})
                    
                    # Rerun to update the chat display
                    st.experimental_rerun()
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.image_chat_history.append({
                        "role": "assistant", 
                        "content": f"I apologize, but I encountered an error: {str(e)}"
                    })
                    st.experimental_rerun()
        
        # Main image analysis button
        if st.button("Analyze Image", use_container_width=True, key="main_analysis"):
            with st.spinner("Analyzing image..."):
                try:
                    # Create prompt with image query
                    image_prompt = f"{query_type}: {specific_question}" if specific_question else query_type
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "content": f"[Image uploaded] {image_prompt}"
                    })
                    
                    # Get image data
                    img_byte_arr = uploaded_image.getvalue()
                    
                    # Generate multimodal content
                    response_text = generate_multimodal_content(
                        prompt=image_prompt,
                        media_data=img_byte_arr,
                        media_type="image/jpeg",  # Adjust based on actual file type
                        temperature=0.2
                    )
                    
                    # Add response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
                except Exception as e:
                    st.error(f"Error analyzing image: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I apologize, but I encountered an error: {str(e)}"
                    })
    
    # Display visual analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

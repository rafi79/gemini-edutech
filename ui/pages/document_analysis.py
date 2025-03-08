"""
Document Analysis page module for the EduGenius application.
This provides functionality for analyzing educational documents.
"""

import streamlit as st
import tempfile
import os
from services.gemini_service import generate_text_content
from services.document_service import process_document
from utils.file_utils import save_uploaded_file, get_file_preview
from config.settings import ALLOWED_EXTENSIONS

def render():
    """Render the Document Analysis page."""
    # Reset chat history if switching to this mode
    if st.session_state.current_mode != "Document Analysis":
        st.session_state.chat_history = []
        st.session_state.current_mode = "Document Analysis"
    
    # Page header
    st.markdown("### AI-Powered Document Analysis")
    st.markdown("Upload study materials, textbooks, or notes for AI analysis and insights")
    
    # Document upload section
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, DOCX, or TXT):", 
        type=ALLOWED_EXTENSIONS['document']
    )
    
    if uploaded_file is not None:
        # Analysis options
        analysis_type = st.multiselect(
            "Select analysis types:", 
            [
                "Key Concepts Extraction", 
                "Summary Generation",
                "Difficulty Assessment", 
                "Concept Relations",
                "Generate Study Questions"
            ]
        )
        
        # Process document when button is clicked
        if st.button("Analyze Document", use_container_width=True):
            with st.spinner("Analyzing document..."):
                try:
                    # Save uploaded file to a temporary location
                    temp_file_path = save_uploaded_file(uploaded_file)
                    
                    # Get a preview of the document content
                    file_content_preview = get_file_preview(temp_file_path, max_length=1000)
                    
                    # Create prompt with analysis instructions
                    analysis_prompt = f"I'm uploading a document named '{uploaded_file.name}'. "
                    analysis_prompt += f"Please perform the following analyses: {', '.join(analysis_type)}. "
                    analysis_prompt += "Here's a preview of the document content: " + file_content_preview
                    
                    # Add to history
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "content": f"Please analyze my document '{uploaded_file.name}' for: {', '.join(analysis_type)}"
                    })
                    
                    # Process document and generate content
                    document_info = process_document(temp_file_path, uploaded_file.name)
                    analysis_prompt += f"\n\nDocument metadata: {document_info}"
                    
                    # Generate content analysis
                    response_text = generate_text_content(
                        prompt=analysis_prompt,
                        temperature=0.2  # Lower temperature for more factual responses
                    )
                    
                    # Add response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": response_text
                    })
                    
                    # Clean up the temporary file
                    os.unlink(temp_file_path)
                
                except Exception as e:
                    st.error(f"Error analyzing document: {str(e)}")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I apologize, but I encountered an error: {str(e)}"
                    })
                    
                    # Ensure temporary file is cleaned up even if error occurs
                    if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
    
    # Display analysis history
    st.markdown("### Analysis Results")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**Request:** {message['content']}")
        else:
            st.markdown(f"**Analysis:** {message['content']}")
        st.markdown("---")

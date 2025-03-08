"""
File utilities for handling uploads, processing different file types, and managing temporary files.
"""

import os
import tempfile
import mimetypes
from pathlib import Path
import streamlit as st
from config.settings import MAX_FILE_SIZE_MB, ALLOWED_EXTENSIONS

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Path to the saved temporary file
    
    Raises:
        ValueError: If file size exceeds limit or file type is not allowed
    """
    # Check file size
    file_size_mb = uploaded_file.size / (1024 * 1024)  # Convert bytes to MB
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB}MB")
    
    # Get file extension
    file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
    
    # Check if extension is allowed (in any category)
    allowed_extensions_list = []
    for _, extensions in ALLOWED_EXTENSIONS.items():
        allowed_extensions_list.extend(extensions)
    
    if file_extension not in allowed_extensions_list:
        raise ValueError(f"File type .{file_extension} is not supported")
    
    # Create a temporary file with the correct extension
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp_file:
        temp_file.write(uploaded_file.getvalue())
        return temp_file.name


def get_file_mime_type(file_path):
    """
    Get the MIME type of a file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: MIME type of the file
    """
    # Initialize mimetypes
    mimetypes.init()
    
    # Get mime type based on file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Default to application/octet-stream if mime type couldn't be determined
    if mime_type is None:
        return 'application/octet-stream'
        
    return mime_type


def get_file_type_category(file_path):
    """
    Determine the category of a file (image, document, audio, video).
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        str: Category of the file (image, document, audio, video, or unknown)
    """
    # Get mime type
    mime_type = get_file_mime_type(file_path)
    
    # Determine category based on mime type
    mime_prefix = mime_type.split('/')[0] if mime_type else ''
    
    if mime_prefix == 'image':
        return 'image'
    elif mime_prefix == 'audio':
        return 'audio'
    elif mime_prefix == 'video':
        return 'video'
    elif mime_type in ['application/pdf', 'application/msword', 
                      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                      'text/plain']:
        return 'document'
    else:
        return 'unknown'


def get_file_preview(file_path, max_length=1000):
    """
    Get a preview of a file's content.
    
    Args:
        file_path (str): Path to the file
        max_length (int): Maximum length of the preview
        
    Returns:
        str: Preview of the file content
    """
    try:
        # Determine file type to handle appropriately
        file_category = get_file_type_category(file_path)
        
        # Get file extension
        file_extension = Path(file_path).suffix.lower()
        
        # Handle different file types
        if file_category == 'document':
            if file_extension == '.txt':
                # Simple text file
                with open(file_path, 'r', errors='replace') as f:
                    content = f.read(max_length)
                    return content + ("..." if len(content) >= max_length else "")
                    
            elif file_extension == '.pdf':
                # For PDF files, return a placeholder - in a real app, use PyPDF2 or similar
                return "[PDF content preview - In a production app, extract text from PDF here]"
                
            elif file_extension in ['.docx', '.doc']:
                # For Word files, return a placeholder - in a real app, use python-docx
                return "[Word document content preview - In a production app, extract text from DOCX here]"
                
        elif file_category == 'image':
            # For images, return metadata instead of content
            import PIL.Image
            try:
                with PIL.Image.open(file_path) as img:
                    return f"[Image: {img.format}, {img.size[0]}x{img.size[1]} pixels, {img.mode} mode]"
            except Exception as e:
                return f"[Image metadata unavailable: {str(e)}]"
                
        elif file_category == 'audio':
            # For audio files, return a simple placeholder
            return "[Audio file - In a production app, extract metadata or transcribe audio here]"
            
        elif file_category == 'video':
            # For video files, return a simple placeholder
            return "[Video file - In a production app, extract metadata or transcribe video here]"
            
        # Default response for unknown file types
        return f"[Preview not available for this file type: {file_extension}]"
        
    except Exception as e:
        return f"[Error previewing file: {str(e)}]"


def clean_temp_files(file_paths):
    """
    Clean up temporary files.
    
    Args:
        file_paths (list): List of file paths to remove
    """
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            st.warning(f"Failed to remove temporary file {file_path}: {str(e)}")


class TempFileManager:
    """
    Context manager for handling temporary files.
    Ensures all temporary files are cleaned up.
    
    Example:
        with TempFileManager() as manager:
            file_path = manager.save_uploaded_file(uploaded_file)
            # Do something with file_path
        # All temporary files are cleaned up automatically
    """
    
    def __init__(self):
        self.temp_files = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def save_uploaded_file(self, uploaded_file):
        """
        Save an uploaded file and track it for cleanup.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            str: Path to the saved temporary file
        """
        temp_file_path = save_uploaded_file(uploaded_file)
        self.temp_files.append(temp_file_path)
        return temp_file_path
    
    def cleanup(self):
        """Clean up all tracked temporary files."""
        clean_temp_files(self.temp_files)
        self.temp_files = []

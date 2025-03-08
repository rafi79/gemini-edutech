"""
Utilities for generating and formatting prompts for the Gemini API.
These utilities create consistent, well-structured prompts for different use cases.
"""

def create_learning_assistant_prompt(question, learning_level, learning_style, chat_history=None):
    """
    Create a prompt for the Learning Assistant mode.
    
    Args:
        question (str): User's question
        learning_level (str): Learning level (Elementary, Middle School, etc.)
        learning_style (str): Learning style (Visual, Interactive, etc.)
        chat_history (list, optional): Previous chat messages. Defaults to None.
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = f"""You are EduGenius, an educational AI tutor. 
Adapt your explanation for {learning_level} level students.
Use a {learning_style} learning style in your response.
Provide clear, accurate, and engaging educational content.
Include examples and analogies where helpful."""

    # Add chat history if provided
    conversation_context = ""
    if chat_history and len(chat_history) > 0:
        conversation_context = "\n\nConversation history:\n"
        for msg in chat_history:
            role = "User" if msg["role"] == "user" else "EduGenius"
            conversation_context += f"{role}: {msg['content']}\n\n"
    
    # Combine all parts
    prompt = f"{system_context}\n{conversation_context}\nStudent question: {question}"
    
    return prompt


def create_document_analysis_prompt(document_name, analysis_types, document_preview, document_metadata=None):
    """
    Create a prompt for document analysis.
    
    Args:
        document_name (str): Name of the document
        analysis_types (list): Types of analysis to perform
        document_preview (str): Preview of document content
        document_metadata (dict, optional): Document metadata. Defaults to None.
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI educational document analyst.
Your task is to analyze educational documents and provide insights.
Focus on educational value, key concepts, and learning opportunities."""

    # Analysis instructions
    analysis_instructions = f"Please analyze the document '{document_name}' and perform the following analyses: {', '.join(analysis_types)}."
    
    # Add metadata if provided
    metadata_text = ""
    if document_metadata:
        metadata_text = "\n\nDocument metadata:\n"
        for key, value in document_metadata.items():
            metadata_text += f"- {key}: {value}\n"
    
    # Document preview
    preview_text = f"\n\nHere's a preview of the document content:\n\n{document_preview}"
    
    # Combine all parts
    prompt = f"{system_context}\n\n{analysis_instructions}{metadata_text}{preview_text}"
    
    return prompt


def create_image_analysis_prompt(query_type, specific_question=None):
    """
    Create a prompt for image analysis.
    
    Args:
        query_type (str): Type of analysis to perform
        specific_question (str, optional): Specific question about the image. Defaults to None.
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI visual learning assistant.
Your task is to analyze educational images and provide insights.
Focus on educational value, key concepts, and visual explanations."""

    # Query instructions based on type
    if query_type == "Explain the concept shown":
        instructions = "Please explain the educational concept shown in this image. Identify key elements and their relationships."
    elif query_type == "Identify elements":
        instructions = "Please identify and label all significant elements in this image. Explain their educational relevance."
    elif query_type == "Solve the problem shown":
        instructions = "Please solve the problem shown in this image. Explain your solution step by step."
    elif query_type == "Create a related exercise":
        instructions = "Based on this image, please create a related educational exercise or problem that would reinforce the concepts shown."
    else:
        instructions = "Please analyze this image from an educational perspective."
    
    # Add specific question if provided
    if specific_question:
        instructions += f"\n\nPlease also address this specific question: {specific_question}"
    
    # Combine all parts
    prompt = f"{system_context}\n\n{instructions}"
    
    return prompt


def create_audio_analysis_prompt(audio_name, analysis_types, language="Auto-detect"):
    """
    Create a prompt for audio analysis.
    
    Args:
        audio_name (str): Name of the audio file
        analysis_types (list): Types of analysis to perform
        language (str, optional): Language of the audio. Defaults to "Auto-detect".
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI audio learning assistant.
Your task is to analyze educational audio content and provide insights.
Focus on educational value, key concepts, and learning opportunities."""

    # Analysis instructions
    analysis_instructions = f"Please analyze the audio file '{audio_name}' and perform the following analyses: {', '.join(analysis_types)}."
    
    # Add language context if specified
    language_text = ""
    if language and language != "Auto-detect":
        language_text = f"\n\nThe audio is in {language}."
    
    # Combine all parts
    prompt = f"{system_context}\n\n{analysis_instructions}{language_text}\n\nPlease provide a detailed analysis focusing on educational value."
    
    return prompt


def create_video_analysis_prompt(video_name, analysis_types, focus="General Analysis"):
    """
    Create a prompt for video analysis.
    
    Args:
        video_name (str): Name of the video file
        analysis_types (list): Types of analysis to perform
        focus (str, optional): Educational focus. Defaults to "General Analysis".
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI video learning assistant.
Your task is to analyze educational video content and provide insights.
Focus on educational value, key moments, and learning opportunities."""

    # Analysis instructions
    analysis_instructions = f"Please analyze the video file '{video_name}' and perform the following analyses: {', '.join(analysis_types)}."
    
    # Add focus context
    focus_text = f"\n\nFocus on {focus} educational aspects."
    
    # Combine all parts
    prompt = f"{system_context}\n\n{analysis_instructions}{focus_text}\n\nProvide a detailed analysis of the educational value of this video."
    
    return prompt


def create_quiz_generation_prompt(topic, difficulty, question_count, format_type):
    """
    Create a prompt for quiz generation.
    
    Args:
        topic (str): Quiz topic
        difficulty (str): Difficulty level
        question_count (int): Number of questions
        format_type (str): Question format
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI educational quiz generator.
Your task is to create effective educational assessment questions.
Focus on clear, engaging questions that assess understanding."""

    # Generation instructions
    generation_instructions = f"""Please create a quiz on the topic of '{topic}' with the following specifications:
- Difficulty level: {difficulty}
- Number of questions: {question_count}
- Question format: {format_type}

Ensure questions assess different cognitive levels, from recall to application and analysis.
Include correct answers and brief explanations for each question."""
    
    # Combine all parts
    prompt = f"{system_context}\n\n{generation_instructions}"
    
    return prompt


def create_concept_mapping_prompt(topic, complexity, related_concepts=None):
    """
    Create a prompt for concept mapping.
    
    Args:
        topic (str): Main concept topic
        complexity (str): Complexity level
        related_concepts (list, optional): List of related concepts. Defaults to None.
        
    Returns:
        str: Formatted prompt
    """
    # System context
    system_context = """You are EduGenius, an AI educational concept mapper.
Your task is to map concepts and their relationships for educational purposes.
Focus on clear hierarchies, connections, and educational relevance."""

    # Mapping instructions
    mapping_instructions = f"""Please create a concept map for '{topic}' with {complexity} complexity level.
Identify key concepts, sub-concepts, and their relationships.
Organize information in a hierarchical structure and show cross-relationships."""
    
    # Add related concepts if provided
    related_text = ""
    if related_concepts and len(related_concepts) > 0:
        related_text = "\n\nPlease include these related concepts in the map: " + ", ".join(related_concepts)
    
    # Combine all parts
    prompt = f"{system_context}\n\n{mapping_instructions}{related_text}"
    
    return prompt

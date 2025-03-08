"""
Concept Mapper page module for the EduGenius application.
This provides functionality for creating concept maps for educational topics.
"""

import streamlit as st
from services.gemini_service import generate_text_content
from utils.prompt_utils import create_concept_mapping_prompt

def render():
    """Render the Concept Mapper page."""
    # Reset state if switching to this mode
    if st.session_state.current_mode != "Concept Mapper":
        st.session_state.current_mode = "Concept Mapper"
        # Clear any existing concept map data
        if "concept_map" in st.session_state:
            del st.session_state.concept_map
    
    # Page header
    st.markdown("### Educational Concept Mapper")
    st.markdown("Visualize connections between ideas to enhance understanding and retention")
    
    # Concept mapping settings
    with st.container():
        st.markdown("#### Concept Map Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Main concept and complexity
            main_concept = st.text_input(
                "Main Concept/Topic:", 
                placeholder="e.g., Photosynthesis, Democracy, Machine Learning"
            )
            
            complexity = st.select_slider(
                "Complexity Level:", 
                options=["Basic", "Intermediate", "Advanced", "Comprehensive"],
                value="Intermediate"
            )
        
        with col2:
            # Related concepts and educational level
            related_concepts = st.text_area(
                "Related Concepts (Optional, one per line):", 
                placeholder="e.g.,\nEnergy transfer\nChlorophyll\nCarbon dioxide"
            )
            
            educational_level = st.selectbox(
                "Educational Level:", 
                [
                    "Elementary", 
                    "Middle School", 
                    "High School", 
                    "Undergraduate", 
                    "Graduate"
                ],
                index=2  # Default to High School
            )
    
    # Advanced options
    with st.expander("Advanced Options", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # Map format and focus
            map_format = st.selectbox(
                "Map Format:", 
                [
                    "Hierarchical", 
                    "Web/Network", 
                    "Flowchart", 
                    "Comparison Map"
                ]
            )
            
            specific_focus = st.text_input(
                "Specific Focus (Optional):", 
                placeholder="e.g., Historical development, Practical applications"
            )
        
        with col2:
            # Include examples and additional instructions
            include_examples = st.checkbox("Include Examples", value=True)
            
            include_definitions = st.checkbox("Include Definitions", value=True)
            
            additional_instructions = st.text_area(
                "Additional Instructions (Optional):", 
                placeholder="e.g., Emphasize connections to real-world scenarios"
            )
    
    # Generate concept map button
    if st.button("Generate Concept Map", use_container_width=True, key="generate_map_button"):
        if not main_concept:
            st.warning("Please enter a main concept.")
        else:
            with st.spinner(f"Creating concept map for {main_concept}..."):
                try:
                    # Process related concepts
                    related_concepts_list = None
                    if related_concepts:
                        related_concepts_list = [concept.strip() for concept in related_concepts.split('\n') if concept.strip()]
                    
                    # Create additional context from advanced options
                    additional_context = f"\nTarget educational level: {educational_level}"
                    
                    if map_format:
                        additional_context += f"\nUse a {map_format.lower()} map format."
                    
                    if specific_focus:
                        additional_context += f"\nFocus specifically on: {specific_focus}"
                    
                    if include_examples:
                        additional_context += "\nInclude relevant examples for key concepts."
                    
                    if include_definitions:
                        additional_context += "\nInclude concise definitions for each concept."
                    
                    if additional_instructions:
                        additional_context += f"\nAdditional instructions: {additional_instructions}"
                    
                    # Create prompt for concept mapping
                    prompt = create_concept_mapping_prompt(
                        topic=main_concept,
                        complexity=complexity,
                        related_concepts=related_concepts_list
                    )
                    
                    # Add additional context
                    prompt += additional_context
                    
                    # Add request for Mermaid diagram
                    prompt += "\n\nYour response should include:\n1. A brief explanation of the concept map\n2. A textual representation of the relationships\n3. A Mermaid.js diagram code for visualizing the concept map (use flowchart or graph syntax)"
                    
                    # Generate concept map content
                    map_content = generate_text_content(
                        prompt=prompt,
                        temperature=0.3  # Lower temperature for more consistent output
                    )
                    
                    # Store generated concept map in session state
                    st.session_state.concept_map = {
                        "content": map_content,
                        "metadata": {
                            "main_concept": main_concept,
                            "complexity": complexity,
                            "educational_level": educational_level,
                            "map_format": map_format
                        }
                    }
                
                except Exception as e:
                    st.error(f"Error generating concept map: {str(e)}")
    
    # Display generated concept map if available
    if "concept_map" in st.session_state:
        display_concept_map(st.session_state.concept_map)


def display_concept_map(map_data):
    """
    Display a generated concept map with visualization options.
    
    Args:
        map_data (dict): Dictionary containing concept map content and metadata
    """
    st.markdown("### Generated Concept Map")
    
    # Map metadata
    metadata = map_data["metadata"]
    st.markdown(f"""
    **Main Concept:** {metadata['main_concept']}  
    **Complexity:** {metadata['complexity']}  
    **Educational Level:** {metadata['educational_level']}  
    **Format:** {metadata['map_format']}  
    """)
    
    # Extract Mermaid diagram if available
    content = map_data["content"]
    
    # Try to find Mermaid code block
    mermaid_code = None
    if "```mermaid" in content:
        try:
            start_idx = content.find("```mermaid")
            end_idx = content.find("```", start_idx + 10)
            if end_idx > start_idx:
                mermaid_code = content[start_idx + 10:end_idx].strip()
        except:
            pass
    
    # Display content in tabs - one for text, one for visualization
    text_tab, visual_tab = st.tabs(["Text Explanation", "Visual Concept Map"])
    
    with text_tab:
        st.markdown(content)
    
    with visual_tab:
        if mermaid_code:
            st.markdown(f"```mermaid\n{mermaid_code}\n```")
        else:
            # If no Mermaid code was found, generate one
            st.warning("No diagram code found in the generated content. Generating visualization...")
            
            # Request specifically a Mermaid diagram
            visualization_prompt = f"""
            Create a Mermaid.js diagram code (using flowchart or graph syntax) to visualize the following concept map about {metadata['main_concept']}:
            
            {content}
            
            Return ONLY the Mermaid code (no explanations), starting with the word 'graph' or 'flowchart'.
            """
            
            try:
                mermaid_code = generate_text_content(visualization_prompt, temperature=0.1)
                
                # Clean up the response to get just the Mermaid code
                if "```mermaid" in mermaid_code:
                    mermaid_code = mermaid_code.split("```mermaid")[1].split("```")[0].strip()
                elif "```" in mermaid_code:
                    mermaid_code = mermaid_code.split("```")[1].strip()
                
                # Display the generated diagram
                st.markdown(f"```mermaid\n{mermaid_code}\n```")
                
            except Exception as e:
                st.error(f"Error generating visualization: {str(e)}")
    
    # Export options
    st.markdown("### Export Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download as Text",
            data=map_data["content"],
            file_name=f"concept_map_{metadata['main_concept'].replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col2:
        if st.button("Generate New Version", use_container_width=True):
            # Clear current concept map and rerun
            del st.session_state.concept_map
            st.experimental_rerun()
    
    # Customization options
    st.markdown("### Customize Concept Map")
    
    customization_option = st.selectbox(
        "Select customization option:",
        [
            "Add more details",
            "Simplify the map",
            "Add educational standards alignment",
            "Add more examples",
            "Focus on prerequisites",
            "Focus on applications",
            "Custom modification"
        ]
    )
    
    custom_instruction = ""
    if customization_option == "Custom modification":
        custom_instruction = st.text_area(
            "Enter custom modification instructions:",
            placeholder="e.g., Add connections to another field, Include historical context"
        )
    
    if st.button("Apply Customization", use_container_width=True):
        with st.spinner("Customizing concept map..."):
            try:
                # Prepare customization prompt
                instruction = customization_option if customization_option != "Custom modification" else custom_instruction
                
                customization_prompt = f"""
                I have a concept map for '{metadata['main_concept']}' with the following specifications:
                - Complexity level: {metadata['complexity']}
                - Educational level: {metadata['educational_level']}
                - Format: {metadata['map_format']}
                
                Here is the current concept map:
                {map_data['content']}
                
                Please modify this concept map to {instruction}. Maintain the same overall structure and include a Mermaid.js diagram code.
                """
                
                # Generate customized concept map
                customized_content = generate_text_content(
                    prompt=customization_prompt,
                    temperature=0.3
                )
                
                # Update concept map in session state
                st.session_state.concept_map["content"] = customized_content
                
                # Add customization to metadata
                st.session_state.concept_map["metadata"]["customizations"] = st.session_state.concept_map["metadata"].get("customizations", []) + [instruction]
                
                # Show success message
                st.success("Concept map customized successfully!")
                st.experimental_rerun()
            
            except Exception as e:
                st.error(f"Error customizing concept map: {str(e)}")

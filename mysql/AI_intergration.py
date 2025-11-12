import google.generativeai as genai
import os
from typing import List, Dict

# Configure your API key (set as environment variable or replace with your key)
GOOGLE_API_KEY = "AIzaSyABadNBsgtYqWOydHvZJ43JzcxfgqTGRWI"
genai.configure(api_key=GOOGLE_API_KEY)

def generate_summary(search_query: str, verses: List[Dict[str, str]]) -> str:
    """
    Generate an AI summary based on the search query and found verses.
    
    Args:
        search_query: The user's original search term/phrase
        verses: List of verse dictionaries with keys: text, book, chapter, verse
    
    Returns:
        Generated summary string
    """
    if not verses:
        return "No verses found to summarize."
    
    # Create context from verses
    context_parts = []
    for v in verses[:10]:  # Limit to first 10 verses to avoid token limits
        book = v.get("book", "")
        chapter = v.get("chapter", "")
        verse_num = v.get("verse", "")
        text = v.get("text", "")
        context_parts.append(f"{book} {chapter}:{verse_num} - {text}")
    
    context = "\n".join(context_parts)
    
    # Create prompt for the AI - CUSTOMIZE THIS SECTION
    prompt = f"""
    The user searched for: "{search_query}"
    
    Here are the verses that matched their search:
    
    {context}
    
    Please provide a thoughtful summary of what these verses teach about "{search_query}".
    
    INSTRUCTIONS FOR YOUR RESPONSE:
    - Focus on the key themes, doctrines, and insights that emerge from these scriptures
    - Keep the summary concise but meaningful (1 paragraphs)
    - Write in a warm, Uplifting, simple inspirational tone that helps people understand spiritual concepts
    - Include specific references to the verses from the scripture database when making points
    - Connect the teachings to practical daily life applications and how it could be applied
    - If there are different perspectives across scriptures, acknowledge them
    - End with an encouraging thought about how these teachings can help someone
    
    Format your response as:
    1. Make a though provoking question related to the search topic. phrase it simply as if to a teenager
    2. Main Theme: [one sentence summary] make it simple for a 11th grader to understand
    3. Personal Application: [how to apply these teachings in daily life in simple language as ifif talking to a teenager]
    4. World Application: [how to apply these teachings to the events happening in the world and how the teachings relate to current news events to daily life.]
    5. Key Insights: [detailed paragraph in simple lanaguage with fun facts about the scriptures, 4 sentences at most ]
    """
    
    try:
        # Use the available models from your API key
        model_names = ['models/gemini-2.5-flash', 'models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-pro-preview-03-25']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception as model_error:
                continue  # Try next model
        
        # If all models fail, return error with available models
        try:
            available_models = genai.list_models()
            model_list = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
            return f"Error: No working model found. Available models: {model_list[:3]}..."
        except:
            return "Error: Could not access any models. Please check your API key."
            
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_simple_summary(search_query: str, verse_count: int) -> str:
    """
    Generate a simple summary when detailed verse analysis isn't needed.
    """
    try:
        # Use the available models from your API key
        model_names = ['models/gemini-2.5-flash', 'models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-pro-preview-03-25']
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                prompt = f"""Provide a brief, uplifting explanation of what the scriptures teach about '{search_query}'. 
                Keep it to 1-2 sentences and focus on practical application for daily life. and how the things going on in the news world today relate to this topic. Also, mention that {verse_count} verses were found on this topic."""
                response = model.generate_content(prompt)
                return response.text
            except Exception as model_error:
                continue  # Try next model
        
        return "Error: Could not find a model for simple summary."
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"

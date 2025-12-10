"""
Gemini API processor for video summarization.

This module provides functions to:
1. Create authenticated Gemini API client
2. Process YouTube video descriptions using Gemini to generate Telugu news summaries
"""

import json
import google.generativeai as genai
from typing import List


def create_gemini_client(api_key: str):
    """
    Create and configure Gemini API client.
    
    Args:
        api_key (str): Google Gemini API key
    
    Returns:
        GenerativeModel: Configured Gemini model instance
    
    Raises:
        ValueError: If API key is invalid or authentication fails
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        return model
    except Exception as e:
        raise ValueError(f"Failed to authenticate with Gemini API: {str(e)}")


def get_gemini_summary(video_title: str, video_description: str, api_key: str) -> List[str]:
    """
    Generate Telugu news summaries using Gemini API based on video title and description.
    
    Args:
        video_title (str): YouTube video title
        video_description (str): YouTube video description
        api_key (str): Google Gemini API key
    
    Returns:
        List[str]: List of 5-8 Telugu news bullet points
    
    Raises:
        ValueError: If API call fails or response is invalid
    """
    try:
        model = create_gemini_client(api_key)
        
        # Telugu prompt for news extraction
        prompt = f"""
        ఈ ETV తెలుగు వార్తల వీడియో గురించి సమాచారం:
        
        శీర్షిక: {video_title}
        వివరణ: {video_description}
        
        దయచేసి ఈ వార్తల వీడియో నుండి 5-8 ముఖ్య వార్తా శీర్షికలను JSON array రూపంలో అందించండి:
        
        ["వార్త శీర్షిక 1", "వార్త శీర్షిక 2", "వార్త శీర్షిక 3", ...]
        
        ప్రతి వార్త శీర్షిక:
        - తెలుగులో ఉండాలి
        - స్పష్టంగా మరియు సంక్షిప్తంగా ఉండాలి (10-15 పదాలు)
        - ముఖ్యమైన వార్తలకు ప్రాధాన్యత ఇవ్వండి
        - JSON array format మాత్రమే తిరిగి పంపండి, ఇతర వచనం వద్దు
        
        ఉదాహరణ: ["తెలంగాణలో భారీ వర్షాలు", "కేంద్ర మంత్రి హైదరాబాద్ పర్యటన", "రైతులకు ప్రభుత్వం సహాయం"]
        """
        
        # Generate content with text prompt only
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise ValueError("Gemini API returned empty response")
        
        # Parse JSON response
        try:
            summaries = json.loads(response.text)
            
            if not isinstance(summaries, list):
                raise ValueError("Gemini response is not a JSON array")
            
            if len(summaries) < 5 or len(summaries) > 8:
                raise ValueError(f"Expected 5-8 summaries, got {len(summaries)}")
            
            # Validate each summary is a string
            for item in summaries:
                if not isinstance(item, str):
                    raise ValueError("All summaries must be strings")
            
            return summaries
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
    
    except Exception as e:
        if isinstance(e, ValueError):
            raise
        raise ValueError(f"Gemini API error: {str(e)}")

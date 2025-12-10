"""
Gemini API processor for video summarization.

This module provides functions to:
1. Create authenticated Gemini API client
2. Process YouTube videos using Gemini to generate Telugu news summaries
"""

import json
import time
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from typing import List


def get_gemini_summary(video_url: str, api_key: str, max_retries: int = 3) -> List[str]:
    """
    Process YouTube video and generate Telugu news summaries using Gemini API.
    
    Args:
        video_url (str): YouTube video URL
        api_key (str): Google Gemini API key
        max_retries (int): Maximum number of retry attempts for rate limits
    
    Returns:
        List[str]: List of 5-8 Telugu news bullet points
    
    Raises:
        ValueError: If API call fails or response is invalid
    """
    # Create Gemini client
    client = genai.Client(api_key=api_key)
    
    # Telugu prompt for news extraction
    prompt = """
    ఈ వీడియోలో ఉన్న ETV తెలుగు వార్తలను విశ్లేషించండి.
    
    దయచేసి క్రింది ఫార్మాట్‌లో JSON array రూపంలో 5-8 ముఖ్య వార్తా శీర్షికలను అందించండి:
    
    ["వార్త శీర్షిక 1", "వార్త శీర్షిక 2", "వార్త శీర్షిక 3", ...]
    
    ప్రతి వార్త శీర్షిక:
    - తెలుగులో ఉండాలి
    - స్పష్టంగా మరియు సంక్షిప్తంగా ఉండాలి (10-15 పదాలు)
    - ముఖ్యమైన వార్తలకు ప్రాధాన్యత ఇవ్వండి
    - JSON array format మాత్రమే తిరిగి పంపండి, ఇతర వచనం వద్దు
    
    ఉదాహరణ: ["తెలంగాణలో భారీ వర్షాలు", "కేంద్ర మంత్రి హైదరాబాద్ పర్యటన", "రైతులకు ప్రభుత్వం సహాయం"]
    """
    
    # Retry logic for rate limits
    for attempt in range(max_retries):
        try:
            # Generate content with video URL using gemini-1.5-flash (better rate limits)
            response = client.models.generate_content(
                model='models/gemini-1.5-flash',
                contents=types.Content(
                    parts=[
                        types.Part(
                            file_data=types.FileData(file_uri=video_url)
                        ),
                        types.Part(text=prompt)
                    ]
                )
            )
            
            if not response or not response.text:
                raise ValueError("Gemini API returned empty response")
            
            # Parse JSON response
            try:
                # Extract text from response
                response_text = response.text.strip()
                
                # Remove markdown code blocks if present
                if response_text.startswith('```'):
                    response_text = response_text.split('\n', 1)[1]
                    response_text = response_text.rsplit('\n```', 1)[0]
                
                summaries = json.loads(response_text)
                
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
        
        except ClientError as e:
            # Handle rate limit errors with retry
            if e.status_code == 429 and attempt < max_retries - 1:
                # Extract wait time from error message if available
                wait_time = 30 * (attempt + 1)  # Exponential backoff: 30s, 60s, 90s
                print(f"Rate limit hit. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise ValueError(f"Gemini API rate limit exceeded: {str(e)}")
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Gemini API error: {str(e)}")
    
    # If all retries exhausted
    raise ValueError("Gemini API: Maximum retry attempts exceeded due to rate limits")

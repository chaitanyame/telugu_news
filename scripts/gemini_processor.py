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
from requests.exceptions import ConnectionError, Timeout
from typing import List


def get_gemini_summary(video_url: str, api_key: str, max_retries: int = 3) -> List[str]:
    """
    Process YouTube video and generate comprehensive Telugu news summaries using Gemini API.
    
    Args:
        video_url (str): YouTube video URL
        api_key (str): Google Gemini API key
        max_retries (int): Maximum number of retry attempts for rate limits
    
    Returns:
        List[str]: List of 8-12 comprehensive Telugu news summaries with category prefixes
    
    Raises:
        ValueError: If API call fails or response is invalid
    """
    # Create Gemini client
    client = genai.Client(api_key=api_key)
    
    # Telugu prompt for comprehensive news extraction with categories
    prompt = """
    ఈ వీడియోలో ఉన్న తెలుగు వార్తలను విశ్లేషించి, సమగ్రమైన సారాంశాలను అందించండి.
    
    దయచేసి క్రింది ఫార్మాట్‌లో JSON array రూపంలో 8-12 ముఖ్యమైన వార్తల సారాంశాలను అందించండి:
    
    ["వర్గం: వివరణాత్మక వార్త సారాంశం", ...]
    
    ప్రతి వార్త సారాంశం:
    - తెలుగులో ఉండాలి
    - వర్గం ప్రిఫిక్స్ తో ప్రారంభం (రాజకీయాలు, క్రీడలు, వ్యాపారం, నేరం, వాతావరణం, సినిమా, విద్య, ఆరోగ్యం, అంతర్జాతీయం, రవాణా, వ్యవసాయం, ఇతరం)
    - సమగ్రంగా ఉండాలి (25-40 పదాలు)
    - ఏమి జరిగింది, ఎవరు పాల్గొన్నారు, ఎక్కడ జరిగింది, ఎందుకు ముఖ్యమైనది అనే వివరాలు చేర్చండి
    - ముఖ్యమైన సంఖ్యలు, పేర్లు, ప్రదేశాలు చేర్చండి
    - ప్రాముఖ్యత క్రమంలో అమర్చండి
    - JSON array format మాత్రమే తిరిగి పంపండి, ఇతర వచనం వద్దు
    
    ఉదాహరణ: [
        "రాజకీయాలు: తెలంగాణ పంచాయతీ ఎన్నికలు: తొలి విడతలో కాంగ్రెస్ హవా, 2303 స్థానాలు కైవసం. బీఆర్ఎస్ 1850 స్థానాలతో రెండో స్థానంలో నిలిచింది",
        "వ్యాపారం: తెలంగాణలో అమెజాన్ భారీ పెట్టుబడి: 50 వేల కోట్లతో వెబ్ సర్వీసెస్ విస్తరణ. 10,000 మందికి ఉద్యోగ అవకాశాలు కల్పించనున్నట్లు ప్రకటన",
        "నేరం: అల్లూరి సీతారామరాజు జిల్లాలో ఘోర రోడ్డు ప్రమాదం: 8 మంది మృతి, 15 మంది గాయాలు. స్పీడ్ వల్ల ప్రమాదం జరిగినట్లు పోలీసుల నిర్ధారణ"
    ]
    """
    
    # Retry logic for rate limits
    for attempt in range(max_retries):
        try:
            # Generate content with video URL using gemini-2.5-flash
            response = client.models.generate_content(
                model='models/gemini-2.5-flash',
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
                
                if len(summaries) < 8 or len(summaries) > 12:
                    raise ValueError(f"Expected 8-12 summaries, got {len(summaries)}")
                
                # Validate each summary is a string with minimum length
                for item in summaries:
                    if not isinstance(item, str):
                        raise ValueError("All summaries must be strings")
                    if len(item) < 30:
                        raise ValueError(f"Summary too short (min 30 chars): {item[:50]}")
                
                return summaries
            
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse Gemini response as JSON: {str(e)}")
        
        except ClientError as e:
            # Handle rate limit errors with retry
            if e.code == 429 and attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)  # Exponential backoff: 30s, 60s, 90s
                print(f"Rate limit hit. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise ValueError(f"Gemini API rate limit exceeded: {str(e)}")
        
        except (ConnectionError, Timeout) as e:
            # Handle connection errors and timeouts with retry
            if attempt < max_retries - 1:
                wait_time = 20 * (attempt + 1)  # Backoff: 20s, 40s, 60s
                print(f"Connection error. Retrying in {wait_time} seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                raise ValueError(f"Gemini API connection failed after {max_retries} attempts. The video may be too long to process: {str(e)}")
        
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            # Don't retry for other exceptions
            raise ValueError(f"Gemini API error: {str(e)}")
    
    # If all retries exhausted
    raise ValueError("Gemini API: Maximum retry attempts exceeded")

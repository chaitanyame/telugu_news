"""
JSON Schema Validators for ETV Telugu News Aggregator
Validates news file structure, date formats, and video IDs.
"""
import re
from datetime import datetime
from typing import Any, Dict


def validate_news_file(data: Dict[str, Any]) -> bool:
    """
    Validate news file structure.
    
    Args:
        data: Dictionary containing news data
        
    Returns:
        True if valid, False otherwise
        
    Expected structure:
        {
            "date": "YYYY-MM-DD",
            "slots": {
                "9pm": {
                    "video_id": str,
                    "title": str,
                    "summary": list[str],
                    "published_at": str
                } or None,
                "7am": {...} or None
            }
        }
    """
    if not isinstance(data, dict):
        return False
    
    # Check required top-level keys
    if "date" not in data or "slots" not in data:
        return False
    
    # Validate date format
    if not validate_date_format(data["date"]):
        return False
    
    # Validate slots structure
    slots = data["slots"]
    if not isinstance(slots, dict):
        return False
    
    # Check that at least 9pm and 7am keys exist
    if "9pm" not in slots or "7am" not in slots:
        return False
    
    # Validate each slot if not None
    for slot_name in ["9pm", "7am"]:
        slot_data = slots[slot_name]
        if slot_data is not None:
            if not isinstance(slot_data, dict):
                return False
            
            # Check required fields in slot
            required_fields = ["video_id", "title", "summary", "published_at"]
            for field in required_fields:
                if field not in slot_data:
                    return False
            
            # Validate video_id
            if not validate_video_id(slot_data["video_id"]):
                return False
            
            # Validate summary is a list
            if not isinstance(slot_data["summary"], list):
                return False
    
    return True


def validate_date_format(date_str: str) -> bool:
    """
    Validate date string is in YYYY-MM-DD format and represents a valid date.
    
    Args:
        date_str: Date string to validate
        
    Returns:
        True if valid YYYY-MM-DD format, False otherwise
    """
    if not isinstance(date_str, str):
        return False
    
    # Check format with regex
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_str):
        return False
    
    # Check if it's a valid date
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_video_id(video_id: str) -> bool:
    """
    Validate YouTube video ID format.
    
    YouTube video IDs are 11 characters long and contain:
    - Letters (a-z, A-Z)
    - Numbers (0-9)
    - Underscores (_)
    - Hyphens (-)
    
    Args:
        video_id: Video ID string to validate
        
    Returns:
        True if valid YouTube video ID format, False otherwise
    """
    if not isinstance(video_id, str):
        return False
    
    # Check length (YouTube video IDs are 11 characters)
    if len(video_id) != 11:
        return False
    
    # Check allowed characters
    pattern = r'^[a-zA-Z0-9_-]{11}$'
    return bool(re.match(pattern, video_id))

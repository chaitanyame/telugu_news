"""
Configuration Manager for Telugu News Aggregator
Contains all configuration constants and environment variable loading.
"""
import os
import re


# Telugu News Channel ID (ETV Telugu)
ETV_CHANNEL_ID = "UCJi8M0hRKjz8SLPvJKEVTOg"

# Video title patterns for searching - flexible regex to match various formats
# Matches patterns like "9 PM | ETV Telugu News | Date" or "9 PM Telugu News"
VIDEO_PATTERN_9PM = r"9 PM.*Telugu.*News"
VIDEO_PATTERN_7AM = r"7 AM.*Telugu.*News"

# Data retention period (days)
DATA_RETENTION_DAYS = 30


def get_youtube_api_key() -> str:
    """
    Get YouTube Data API key from environment variables.
    
    Returns:
        str: YouTube API key
        
    Raises:
        ValueError: If YOUTUBE_API_KEY environment variable is not set or empty
    """
    api_key = os.environ.get('YOUTUBE_API_KEY', '').strip()
    
    if not api_key:
        raise ValueError(
            "YOUTUBE_API_KEY environment variable not set. "
            "Please set it in GitHub Secrets or your local environment."
        )
    
    return api_key


def get_gemini_api_key() -> str:
    """
    Get Google Gemini API key from environment variables.
    
    Returns:
        str: Gemini API key
        
    Raises:
        ValueError: If GEMINI_API_KEY environment variable is not set or empty
    """
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable not set. "
            "Please set it in GitHub Secrets or your local environment."
        )
    
    return api_key

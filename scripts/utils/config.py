"""
Configuration Manager for Telugu News Aggregator
Contains all configuration constants and environment variable loading.
"""
import os
import re


# Telugu News Channel IDs
# ETV Andhra Pradesh uploads 9 PM news
ETV_AP_CHANNEL_ID = "UCJi8M0hRKjz8SLPvJKEVTOg"
# ETV Telugu India uploads 7 AM news  
ETV_TELUGU_CHANNEL_ID = "UCSs9H1cyB3OHdy8wkit8ZKg"

# Mapping of time slots to channel IDs
CHANNEL_IDS = {
    "9pm": ETV_AP_CHANNEL_ID,
    "7am": ETV_TELUGU_CHANNEL_ID
}

# Video title patterns for searching
# Format: "9 PM | ETV Telugu News | 9th December "2025"
# Format: "7 AM | ETV Telugu News | 9th December "2025"
VIDEO_PATTERN_9PM = r"^9 PM \| ETV Telugu News \|"
VIDEO_PATTERN_7AM = r"^7 AM \| ETV Telugu News \|"

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

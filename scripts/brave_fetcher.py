"""
Brave Search-based video fetcher for Telugu News.

This module uses Brave Search API to find YouTube videos by date and keywords,
eliminating the need for YouTube Data API or RSS feeds.
"""

import os
import re
import html
import requests
from typing import Dict, Optional, List
from datetime import datetime


# Search keywords for each time slot
SEARCH_KEYWORDS = {
    "9pm": "ETV Telugu News 9 PM",
    "7am": "ETV Telugu News 7 AM"
}

# Month name mapping for date parsing
MONTH_MAP = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12'
}


def get_brave_api_key() -> str:
    """
    Get Brave Search API key from environment variables.
    
    Returns:
        str: Brave Search API key
        
    Raises:
        ValueError: If BRAVE_API_KEY environment variable is not set or empty
    """
    api_key = os.environ.get('BRAVE_API_KEY', '').strip()
    
    if not api_key:
        raise ValueError(
            "BRAVE_API_KEY environment variable not set. "
            "Please set it in GitHub Secrets or your local environment."
        )
    
    return api_key


def extract_date_from_title(title: str) -> Optional[str]:
    """
    Extract date from video title.
    
    Expected formats:
    - "9 PM | ETV Telugu News | 9th December 2025"
    - "7 AM | ETV Telugu News | 10th December "2025""
    
    Args:
        title: Video title string
        
    Returns:
        Date in YYYY-MM-DD format or None if not found
    """
    # Decode HTML entities first
    title = html.unescape(title)
    
    # Pattern: day + suffix + month + year
    # Handles: 9th December 2025, 10th December "2025", etc.
    pattern = r'(\d{1,2})(?:st|nd|rd|th)\s+([A-Za-z]+)\s+["\']?(\d{4})["\']?'
    match = re.search(pattern, title, re.IGNORECASE)
    
    if match:
        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = match.group(3)
        
        if month_name in MONTH_MAP:
            month = MONTH_MAP[month_name]
            return f"{year}-{month}-{day:02d}"
    
    return None


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from URL.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video ID or None if not found
    """
    # Match various YouTube URL formats
    patterns = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def search_youtube_via_brave(time_slot: str, date: str) -> Optional[Dict]:
    """
    Search for YouTube video using Brave Search API.
    
    Args:
        time_slot: '9pm' or '7am'
        date: Date in YYYY-MM-DD format
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
    """
    try:
        api_key = get_brave_api_key()
    except ValueError:
        return None
    
    # Parse the date to get components for search
    date_obj = datetime.strptime(date, '%Y-%m-%d')
    day = date_obj.day
    month_name = date_obj.strftime('%B')  # Full month name
    year = date_obj.year
    
    # Build search query with date
    base_keywords = SEARCH_KEYWORDS.get(time_slot, "ETV Telugu News")
    search_query = f'site:youtube.com {base_keywords} {day} {month_name} {year}'
    
    # Brave Search API endpoint
    url = "https://api.search.brave.com/res/v1/web/search"
    
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }
    
    params = {
        "q": search_query,
        "count": 10,  # Get top 10 results
        "search_lang": "en",
        "country": "IN",
        "freshness": "pw"  # Past week for recent videos
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Parse web results
        web_results = data.get("web", {}).get("results", [])
        
        for result in web_results:
            result_url = result.get("url", "")
            title = result.get("title", "")
            
            # Check if it's a YouTube video
            if "youtube.com/watch" not in result_url and "youtu.be/" not in result_url:
                continue
            
            video_id = extract_video_id_from_url(result_url)
            if not video_id:
                continue
            
            # Verify date in title matches requested date
            title_date = extract_date_from_title(title)
            if title_date != date:
                continue
            
            # Verify time slot in title
            slot_pattern = "9 PM" if time_slot == "9pm" else "7 AM"
            if slot_pattern not in title:
                continue
            
            # Found matching video
            return {
                "video_id": video_id,
                "title": title,
                "published_at": f"{date}T{'21:00:00' if time_slot == '9pm' else '07:00:00'}Z",
                "source": "brave_search"
            }
        
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Brave Search API error: {e}")
        return None
    except Exception as e:
        print(f"Error searching via Brave: {e}")
        return None


def search_video(time_slot: str, date: str) -> Optional[Dict]:
    """
    Main entry point to search for a video.
    
    Args:
        time_slot: '9pm' or '7am'
        date: Date in YYYY-MM-DD format
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
    """
    return search_youtube_via_brave(time_slot, date)

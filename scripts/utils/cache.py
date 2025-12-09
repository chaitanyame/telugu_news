"""
Video ID Caching System
Prevents reprocessing of videos and reduces API calls.
"""
import json
import os
from typing import Dict


# Cache file path
CACHE_FILE = "data/cache/video-ids.json"


def load_video_cache() -> Dict[str, str]:
    """
    Load video ID cache from disk.
    
    Returns:
        Dictionary mapping video_id -> date processed
    """
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_video_cache(cache: Dict[str, str]) -> None:
    """
    Save video ID cache to disk.
    
    Args:
        cache: Dictionary mapping video_id -> date processed
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)


def is_video_processed(video_id: str) -> bool:
    """
    Check if video has already been processed.
    
    Args:
        video_id: YouTube video ID
        
    Returns:
        True if video is in cache, False otherwise
    """
    cache = load_video_cache()
    return video_id in cache


def mark_video_processed(video_id: str, date: str) -> None:
    """
    Mark video as processed in cache.
    
    Args:
        video_id: YouTube video ID
        date: Date processed (YYYY-MM-DD)
    """
    cache = load_video_cache()
    cache[video_id] = date
    save_video_cache(cache)

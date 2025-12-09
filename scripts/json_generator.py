"""
JSON file generator and manager for news data.

This module provides functions to:
1. Load or create news JSON files
2. Save news data to archive
3. Update news slots with video summaries
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from scripts.utils.validators import validate_news_file, validate_date_format


def load_or_create_news_file(date: str) -> Dict:
    """
    Load existing news file or create new one.
    
    Args:
        date (str): Date in YYYY-MM-DD format
    
    Returns:
        Dict: News data structure with date and slots
    
    Raises:
        ValueError: If date format is invalid
    """
    # Validate date format
    if not validate_date_format(date):
        raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
    
    # Parse date components
    year, month, _ = date.split('-')
    file_path = f"data/archive/{year}-{month}/{date}.json"
    
    # Load existing file if it exists
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    
    # Create new file structure
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    return {
        "date": date,
        "slots": {
            "9pm": None,
            "7am": None
        }
    }


def save_news_file(date: str, data: Dict) -> None:
    """
    Save news data to archive.
    
    Args:
        date (str): Date in YYYY-MM-DD format
        data (Dict): News data structure to save
    
    Raises:
        ValueError: If data structure is invalid
    """
    # Validate data structure
    if not validate_news_file(data):
        raise ValueError("Invalid news file structure")
    
    # Parse date components
    year, month, _ = date.split('-')
    file_path = f"data/archive/{year}-{month}/{date}.json"
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_news_slot(
    data: Dict,
    slot: str,
    summaries: List[str],
    video_data: Dict
) -> Dict:
    """
    Update a news slot with video summaries.
    
    Args:
        data (Dict): News data structure
        slot (str): Slot name ('9pm' or '7am')
        summaries (List[str]): List of Telugu news summaries
        video_data (Dict): Video metadata (video_id, video_title, published_at)
    
    Returns:
        Dict: Updated news data structure
    
    Raises:
        ValueError: If slot name is invalid
    """
    if slot not in ["9pm", "7am"]:
        raise ValueError(f"Invalid slot: {slot}. Must be '9pm' or '7am'")
    
    # Update slot with new data
    data["slots"][slot] = {
        "video_id": video_data["video_id"],
        "title": video_data["title"],
        "published_at": video_data["published_at"],
        "summary": summaries
    }
    
    return data

"""
YouTube RSS Feed Client
Fetches videos from YouTube channels using RSS feeds (no API key required).
"""
import re
import html
import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional
from scripts.utils.config import ALL_CHANNEL_IDS, VIDEO_PATTERN_9PM, VIDEO_PATTERN_7AM

logger = logging.getLogger(__name__)

# Atom namespace
ATOM_NS = '{http://www.w3.org/2005/Atom}'
MEDIA_NS = '{http://search.yahoo.com/mrss/}'
YT_NS = '{http://www.youtube.com/xml/schemas/2015}'

# Pattern to extract date from video title
TITLE_DATE_PATTERN = re.compile(
    r'(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+["\']?(\d{4})',
    re.IGNORECASE
)

# Month name to number mapping
MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}


def extract_date_from_title(title: str) -> Optional[str]:
    """
    Extract the news date from video title.
    
    Args:
        title: Video title like "9 PM | ETV Telugu News | 8th December "2025"
        
    Returns:
        Date string in YYYY-MM-DD format, or None if not found
    """
    # Decode HTML entities
    decoded_title = html.unescape(title)
    
    match = TITLE_DATE_PATTERN.search(decoded_title)
    if match:
        day = int(match.group(1))
        month_name = match.group(2).lower()
        year = int(match.group(3))
        month = MONTH_MAP.get(month_name)
        if month:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return None


def extract_video_id_from_url(url: str) -> Optional[str]:
    """Extract video ID from YouTube URL."""
    match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    return None


def get_channel_videos_rss(channel_id: str) -> list[dict]:
    """
    Get recent videos from a channel's RSS feed.
    
    Args:
        channel_id: YouTube channel ID
        
    Returns:
        List of video dictionaries with video_id, title, published_at, url
    """
    rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    videos = []
    
    try:
        response = requests.get(rss_url, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        for entry in root.findall(f'{ATOM_NS}entry'):
            title_elem = entry.find(f'{ATOM_NS}title')
            link_elem = entry.find(f'{ATOM_NS}link')
            published_elem = entry.find(f'{ATOM_NS}published')
            video_id_elem = entry.find(f'{YT_NS}videoId')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ''
                url = link_elem.get('href', '')
                published_at = published_elem.text if published_elem is not None else ''
                
                # Get video ID from yt:videoId element or from URL
                if video_id_elem is not None:
                    video_id = video_id_elem.text
                else:
                    video_id = extract_video_id_from_url(url)
                
                if video_id:
                    videos.append({
                        'video_id': video_id,
                        'title': title,
                        'published_at': published_at,
                        'url': url
                    })
        
        logger.info(f"Found {len(videos)} videos in RSS feed for channel {channel_id}")
        return videos
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching RSS feed for channel {channel_id}: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"Error parsing RSS XML for channel {channel_id}: {e}")
        return []


def search_video_rss(channel_id: Optional[str], time_slot: str, target_date: str) -> Optional[dict]:
    """
    Search for a specific news video using RSS feed.
    
    Args:
        channel_id: YouTube channel ID (or None to search all channels)
        time_slot: "9pm" or "7am"
        target_date: Date string in YYYY-MM-DD format
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
    """
    # Select title pattern based on time slot
    if time_slot == "9pm":
        pattern = re.compile(VIDEO_PATTERN_9PM)
    elif time_slot == "7am":
        pattern = re.compile(VIDEO_PATTERN_7AM)
    else:
        raise ValueError(f"Invalid time slot: {time_slot}")
    
    # Search all channels if none specified
    channels_to_search = [channel_id] if channel_id else ALL_CHANNEL_IDS
    
    for search_channel_id in channels_to_search:
        logger.info(f"Searching RSS feed for channel {search_channel_id}, slot {time_slot}, date {target_date}")
        
        videos = get_channel_videos_rss(search_channel_id)
        
        for video in videos:
            title = video['title']
            
            # Check if title matches the time slot pattern (7 AM or 9 PM news)
            if pattern.match(title):
                # Extract date from title
                title_date = extract_date_from_title(title)
                
                if title_date:
                    logger.info(f"Video '{title}' has date {title_date}, looking for {target_date}")
                    
                    if title_date == target_date:
                        logger.info(f"✅ MATCHED! Video ID: {video['video_id']}, Title: {title}")
                        return {
                            'video_id': video['video_id'],
                            'title': title,
                            'published_at': video['published_at']
                        }
                else:
                    logger.warning(f"Could not extract date from title: {title}")
        
        logger.info(f"No matching video found in channel {search_channel_id}")
    
    logger.info(f"Video not found in any channel for {time_slot} on {target_date}")
    return None


def get_videos_for_date_rss(target_date: str) -> list[dict]:
    """
    Get all ETV Telugu News videos for a specific date.
    
    Args:
        target_date: Date string in YYYY-MM-DD format
        
    Returns:
        List of matching videos with slot info
    """
    results = []
    
    for slot in ["7am", "9pm"]:
        video = search_video_rss(None, slot, target_date)
        if video:
            video['slot'] = slot
            results.append(video)
    
    return results

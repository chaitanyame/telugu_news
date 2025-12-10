"""
YouTube Data API v3 Client Wrapper
Handles YouTube API authentication and video searching.
"""
import re
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scripts.utils.config import VIDEO_PATTERN_9PM, VIDEO_PATTERN_7AM, ALL_CHANNEL_IDS


# Date ordinal suffixes
ORDINAL_MAP = {
    1: '1st', 2: '2nd', 3: '3rd', 4: '4th', 5: '5th',
    6: '6th', 7: '7th', 8: '8th', 9: '9th', 10: '10th',
    11: '11th', 12: '12th', 13: '13th', 14: '14th', 15: '15th',
    16: '16th', 17: '17th', 18: '18th', 19: '19th', 20: '20th',
    21: '21st', 22: '22nd', 23: '23rd', 24: '24th', 25: '25th',
    26: '26th', 27: '27th', 28: '28th', 29: '29th', 30: '30th', 31: '31st'
}

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def get_expected_date_string(date_str: str) -> str:
    """
    Convert YYYY-MM-DD to expected title format like "10th December"
    
    Args:
        date_str: Date in YYYY-MM-DD format
    
    Returns:
        str: Date string like "10th December"
    """
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    day_ordinal = ORDINAL_MAP.get(dt.day, f"{dt.day}th")
    month_name = MONTH_NAMES.get(dt.month, '')
    return f"{day_ordinal} {month_name}"

logger = logging.getLogger(__name__)


def get_youtube_api_client(api_key: str):
    """
    Create YouTube Data API v3 client.
    
    Args:
        api_key: YouTube Data API key
        
    Returns:
        YouTube API client object
        
    Raises:
        Exception: If authentication fails
    """
    try:
        client = build('youtube', 'v3', developerKey=api_key)
        return client
    except Exception as e:
        raise Exception(f"Failed to create YouTube API client: {str(e)}")


def search_channel_videos(client, channel_id: str, time_slot: str, date: str):
    """
    Search for video on channel by time slot and date.
    Searches multiple channels if channel_id is None.
    
    Args:
        client: YouTube API client
        channel_id: YouTube channel ID (or None to search all channels)
        time_slot: "9pm" or "7am"
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
        
    Raises:
        Exception: If API request fails
    """
    # If no specific channel, search all channels
    channels_to_search = [channel_id] if channel_id else ALL_CHANNEL_IDS
    
    for search_channel_id in channels_to_search:
        result = _search_single_channel(client, search_channel_id, time_slot, date)
        if result:
            return result
    
    return None


def _search_single_channel(client, channel_id: str, time_slot: str, date: str):
    """
    Search a single channel for video by time slot and date.
    """
    try:
        # Get the appropriate title pattern
        if time_slot == "9pm":
            pattern = VIDEO_PATTERN_9PM
        elif time_slot == "7am":
            pattern = VIDEO_PATTERN_7AM
        else:
            raise ValueError(f"Invalid time slot: {time_slot}")
        
        # Parse date and create search window (2 days before to 1 day after)
        target_date = datetime.strptime(date, '%Y-%m-%d')
        published_after = target_date - timedelta(days=2)
        published_before = target_date + timedelta(days=1)
        
        # Format for API (RFC 3339)
        published_after_str = published_after.strftime('%Y-%m-%dT00:00:00Z')
        published_before_str = published_before.strftime('%Y-%m-%dT23:59:59Z')
        
        logger.info(f"Searching channel {channel_id} for {time_slot} videos between {published_after_str} and {published_before_str}")
        
        # Search request
        request = client.search().list(
            part='snippet',
            channelId=channel_id,
            type='video',
            order='date',
            publishedAfter=published_after_str,
            publishedBefore=published_before_str,
            maxResults=50
        )
        
        response = request.execute()
        
        items = response.get('items', [])
        logger.info(f"Found {len(items)} videos in channel {channel_id}")
        
        # Get expected date string to match in title (e.g., "10th December")
        expected_date_str = get_expected_date_string(date)
        logger.info(f"Looking for videos with date: {expected_date_str}")
        
        # Filter by title pattern AND date
        compiled_pattern = re.compile(pattern)
        for item in items:
            title = item['snippet']['title']
            if compiled_pattern.match(title):
                # Check if the date in the title matches the requested date
                # Title format: "7 AM | ETV Telugu News | 10th December "2025"
                if expected_date_str in title:
                    logger.info(f"Matched video: {title} on channel {channel_id}")
                    return {
                        'video_id': item['id']['videoId'],
                        'title': title,
                        'published_at': item['snippet']['publishedAt']
                    }
                else:
                    logger.info(f"Pattern match but wrong date - Title: {title}, Expected: {expected_date_str}")
        
        # Log titles for debugging if no match
        if items:
            logger.info(f"No pattern match on {channel_id}. First 5 titles: {[item['snippet']['title'] for item in items[:5]]}")
        
        return None
        
    except HttpError as e:
        logger.error(f"YouTube API error for channel {channel_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Search failed for channel {channel_id}: {str(e)}")
        return None

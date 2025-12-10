"""
YouTube Data API v3 Client Wrapper
Handles YouTube API authentication and video searching.
"""
import re
import html
import logging
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scripts.utils.config import VIDEO_PATTERN_9PM, VIDEO_PATTERN_7AM, ALL_CHANNEL_IDS

logger = logging.getLogger(__name__)

# Pattern to extract date from video title
# Matches: "8th December", "1st December", "22nd December", "3rd December"
# The year may be preceded by a quote or &quot; (HTML entity)
TITLE_DATE_PATTERN = re.compile(r'(\d{1,2})(?:st|nd|rd|th)\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+["\']?(\d{4})', re.IGNORECASE)

# Month name to number mapping
MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}


def extract_date_from_title(title: str) -> str | None:
    """
    Extract the news date from video title.
    
    Args:
        title: Video title like "9 PM | ETV Telugu News | 8th December "2025"
               May contain HTML entities like &quot; which will be decoded.
        
    Returns:
        Date string in YYYY-MM-DD format, or None if not found
    """
    # Decode HTML entities (e.g., &quot; -> ")
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
    Matches video by parsing the date from the video title, not the published date.
    """
    try:
        # Get the appropriate title pattern
        if time_slot == "9pm":
            pattern = VIDEO_PATTERN_9PM
        elif time_slot == "7am":
            pattern = VIDEO_PATTERN_7AM
        else:
            raise ValueError(f"Invalid time slot: {time_slot}")
        
        # Parse date and create search window (3 days before to 2 days after)
        # Videos may be uploaded days after the actual news date
        target_date = datetime.strptime(date, '%Y-%m-%d')
        published_after = target_date - timedelta(days=3)
        published_before = target_date + timedelta(days=2)
        
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
        
        # Filter by title pattern AND extract date from title
        compiled_pattern = re.compile(pattern)
        matched_pattern_count = 0
        
        for item in items:
            title = item['snippet']['title']
            published_at = item['snippet']['publishedAt']
            video_id = item['id']['videoId']
            
            if compiled_pattern.match(title):
                matched_pattern_count += 1
                
                # Extract the actual news date from the video title
                title_date = extract_date_from_title(title)
                
                if title_date:
                    logger.info(f"Video '{title}' - Title date: {title_date}, Looking for: {date}")
                    
                    # Check if the date in title matches the target date
                    if title_date == date:
                        logger.info(f"✅ MATCHED! Title: {title}, Title Date: {title_date}, Published: {published_at}, Video ID: {video_id}")
                        return {
                            'video_id': video_id,
                            'title': title,
                            'published_at': published_at
                        }
                    else:
                        logger.info(f"❌ Date mismatch - Title has {title_date}, looking for {date}")
                else:
                    logger.warning(f"Could not extract date from title: {title}")
        
        logger.info(f"Summary for channel {channel_id}: {matched_pattern_count} videos matched pattern, 0 matched target date {date}")
        
        return None
        
    except HttpError as e:
        logger.error(f"YouTube API error for channel {channel_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Search failed for channel {channel_id}: {str(e)}")
        return None

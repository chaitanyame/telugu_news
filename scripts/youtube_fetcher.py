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
        
        # Filter by title pattern AND published date
        compiled_pattern = re.compile(pattern)
        matched_pattern_count = 0
        
        for item in items:
            title = item['snippet']['title']
            published_at = item['snippet']['publishedAt']
            
            # Parse published date (format: 2025-12-09T16:28:16Z)
            published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ').date()
            published_date_str = published_date.strftime('%Y-%m-%d')
            
            if compiled_pattern.match(title):
                matched_pattern_count += 1
                
                # Compare published date with requested date
                # For 9 PM news: video published on the same date (evening)
                # For 7 AM news: video published on the same date (morning)
                if published_date_str == date:
                    logger.info(f"✅ MATCHED! Title: {title}, Published: {published_at}, Video ID: {item['id']['videoId']}")
                    return {
                        'video_id': item['id']['videoId'],
                        'title': title,
                        'published_at': published_at
                    }
                else:
                    logger.info(f"❌ Pattern match but wrong date - Title: {title}, Published: {published_date_str}, Expected: {date}")
        
        logger.info(f"Summary for channel {channel_id}: {matched_pattern_count} videos matched pattern, 0 matched date")
        
        return None
        
    except HttpError as e:
        logger.error(f"YouTube API error for channel {channel_id}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Search failed for channel {channel_id}: {str(e)}")
        return None

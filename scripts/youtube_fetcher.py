"""
YouTube Data API v3 Client Wrapper
Handles YouTube API authentication and video searching.
"""
import re
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from scripts.utils.config import VIDEO_PATTERN_9PM, VIDEO_PATTERN_7AM


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
    
    Args:
        client: YouTube API client
        channel_id: YouTube channel ID
        time_slot: "9pm" or "7am"
        date: Date string in YYYY-MM-DD format
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
        
    Raises:
        Exception: If API request fails
    """
    try:
        # Get the appropriate title pattern
        if time_slot == "9pm":
            pattern = VIDEO_PATTERN_9PM
        elif time_slot == "7am":
            pattern = VIDEO_PATTERN_7AM
        else:
            raise ValueError(f"Invalid time slot: {time_slot}")
        
        # Parse date and create 24-hour search window
        target_date = datetime.strptime(date, '%Y-%m-%d')
        published_after = target_date - timedelta(days=1)
        published_before = target_date + timedelta(days=1)
        
        # Format for API (RFC 3339)
        published_after_str = published_after.strftime('%Y-%m-%dT00:00:00Z')
        published_before_str = published_before.strftime('%Y-%m-%dT23:59:59Z')
        
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
        
        # Filter by title pattern
        compiled_pattern = re.compile(pattern)
        for item in response.get('items', []):
            title = item['snippet']['title']
            if compiled_pattern.match(title):
                video_id = item['id']['videoId']
                
                # Get full video details including description
                video_request = client.videos().list(
                    part='snippet',
                    id=video_id
                )
                video_response = video_request.execute()
                
                description = ""
                if video_response.get('items'):
                    description = video_response['items'][0]['snippet'].get('description', '')
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'published_at': item['snippet']['publishedAt']
                }
        
        # No matching video found
        return None
        
    except HttpError as e:
        raise Exception(f"YouTube API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Search failed: {str(e)}")

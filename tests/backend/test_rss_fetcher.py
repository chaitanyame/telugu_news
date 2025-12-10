"""
Tests for RSS Feed Client
Tests video fetching via YouTube RSS feeds.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.rss_fetcher import (
    extract_date_from_title,
    extract_video_id_from_url,
    get_channel_videos_rss,
    search_video_rss
)


class TestExtractDateFromTitle:
    """Test extract_date_from_title function"""
    
    def test_extract_date_standard_format(self):
        """Test date extraction from standard video title format"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 8th December 2025') == '2025-12-08'
        assert extract_date_from_title('7 AM | ETV Telugu News | 9th December 2025') == '2025-12-09'
    
    def test_extract_date_with_html_entities(self):
        """Test date extraction when title contains HTML entities"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 9th December &quot;2025') == '2025-12-09'
        assert extract_date_from_title('7 AM | ETV Telugu News | 10th December &quot;2025') == '2025-12-10'
    
    def test_extract_date_different_suffixes(self):
        """Test date extraction with different day suffixes"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 1st January 2025') == '2025-01-01'
        assert extract_date_from_title('9 PM | ETV Telugu News | 2nd February 2025') == '2025-02-02'
        assert extract_date_from_title('9 PM | ETV Telugu News | 3rd March 2025') == '2025-03-03'
        assert extract_date_from_title('9 PM | ETV Telugu News | 11th April 2025') == '2025-04-11'
    
    def test_extract_date_no_match(self):
        """Test returns None when no date found"""
        assert extract_date_from_title('Some random video title') is None
        assert extract_date_from_title('') is None


class TestExtractVideoIdFromUrl:
    """Test extract_video_id_from_url function"""
    
    def test_extract_video_id_standard_url(self):
        """Test extracting video ID from standard YouTube URL"""
        assert extract_video_id_from_url('https://www.youtube.com/watch?v=dQw4w9WgXcQ') == 'dQw4w9WgXcQ'
    
    def test_extract_video_id_with_params(self):
        """Test extracting video ID with additional parameters"""
        assert extract_video_id_from_url('https://www.youtube.com/watch?v=abc123def45&t=120') == 'abc123def45'
    
    def test_extract_video_id_no_match(self):
        """Test returns None when no video ID found"""
        assert extract_video_id_from_url('https://www.youtube.com/channel/UCxxx') is None
        assert extract_video_id_from_url('not a url') is None


class TestGetChannelVideosRss:
    """Test get_channel_videos_rss function"""
    
    @patch('scripts.rss_fetcher.requests.get')
    def test_get_channel_videos_success(self, mock_get):
        """Test successful RSS feed fetch"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
            <entry>
                <yt:videoId>test123video</yt:videoId>
                <title>9 PM | ETV Telugu News | 8th December 2025</title>
                <link href="https://www.youtube.com/watch?v=test123video"/>
                <published>2025-12-08T15:30:00+00:00</published>
            </entry>
        </feed>'''
        mock_get.return_value = mock_response
        
        videos = get_channel_videos_rss('UCtest123')
        
        assert len(videos) == 1
        assert videos[0]['video_id'] == 'test123video'
        assert videos[0]['title'] == '9 PM | ETV Telugu News | 8th December 2025'
    
    @patch('scripts.rss_fetcher.requests.get')
    def test_get_channel_videos_request_error(self, mock_get):
        """Test handling of request errors"""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        videos = get_channel_videos_rss('UCtest123')
        
        assert videos == []


class TestSearchVideoRss:
    """Test search_video_rss function"""
    
    @patch('scripts.rss_fetcher.get_channel_videos_rss')
    def test_search_video_found(self, mock_get_videos):
        """Test finding a matching video"""
        mock_get_videos.return_value = [
            {
                'video_id': 'match123',
                'title': '9 PM | ETV Telugu News | 8th December 2025',
                'published_at': '2025-12-08T15:30:00+00:00',
                'url': 'https://www.youtube.com/watch?v=match123'
            },
            {
                'video_id': 'other456',
                'title': 'Some other video',
                'published_at': '2025-12-08T10:00:00+00:00',
                'url': 'https://www.youtube.com/watch?v=other456'
            }
        ]
        
        result = search_video_rss('UCtest', '9pm', '2025-12-08')
        
        assert result is not None
        assert result['video_id'] == 'match123'
    
    @patch('scripts.rss_fetcher.get_channel_videos_rss')
    def test_search_video_not_found(self, mock_get_videos):
        """Test when no matching video found"""
        mock_get_videos.return_value = [
            {
                'video_id': 'other456',
                'title': 'Some other video',
                'published_at': '2025-12-08T10:00:00+00:00',
                'url': 'https://www.youtube.com/watch?v=other456'
            }
        ]
        
        result = search_video_rss('UCtest', '9pm', '2025-12-08')
        
        assert result is None
    
    @patch('scripts.rss_fetcher.get_channel_videos_rss')
    def test_search_video_date_mismatch(self, mock_get_videos):
        """Test when video title date doesn't match target date"""
        mock_get_videos.return_value = [
            {
                'video_id': 'match123',
                'title': '9 PM | ETV Telugu News | 9th December 2025',  # Dec 9, not Dec 8
                'published_at': '2025-12-09T15:30:00+00:00',
                'url': 'https://www.youtube.com/watch?v=match123'
            }
        ]
        
        result = search_video_rss('UCtest', '9pm', '2025-12-08')  # Looking for Dec 8
        
        assert result is None

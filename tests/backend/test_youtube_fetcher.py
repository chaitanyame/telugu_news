"""
Tests for YouTube API client wrapper
Tests the YouTube Data API v3 client initialization and video search.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from scripts.youtube_fetcher import get_youtube_api_client, search_channel_videos, extract_date_from_title


class TestExtractDateFromTitle:
    """Test extract_date_from_title function"""
    
    def test_extract_date_standard_format(self):
        """Test date extraction from standard video title format"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 8th December 2025') == '2025-12-08'
        assert extract_date_from_title('7 AM | ETV Telugu News | 9th December 2025') == '2025-12-09'
    
    def test_extract_date_with_quotes(self):
        """Test date extraction when year has quotes"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 8th December "2025') == '2025-12-08'
    
    def test_extract_date_different_day_suffixes(self):
        """Test date extraction with different day suffixes (st, nd, rd, th)"""
        assert extract_date_from_title('9 PM | ETV Telugu News | 1st January 2025') == '2025-01-01'
        assert extract_date_from_title('9 PM | ETV Telugu News | 2nd February 2025') == '2025-02-02'
        assert extract_date_from_title('9 PM | ETV Telugu News | 3rd March 2025') == '2025-03-03'
        assert extract_date_from_title('9 PM | ETV Telugu News | 22nd April 2025') == '2025-04-22'
        assert extract_date_from_title('9 PM | ETV Telugu News | 11th May 2025') == '2025-05-11'
    
    def test_extract_date_all_months(self):
        """Test date extraction works for all months"""
        months = [
            ('January', '01'), ('February', '02'), ('March', '03'),
            ('April', '04'), ('May', '05'), ('June', '06'),
            ('July', '07'), ('August', '08'), ('September', '09'),
            ('October', '10'), ('November', '11'), ('December', '12')
        ]
        for month_name, month_num in months:
            title = f'9 PM | ETV Telugu News | 15th {month_name} 2025'
            expected = f'2025-{month_num}-15'
            assert extract_date_from_title(title) == expected
    
    def test_extract_date_no_match(self):
        """Test returns None when no date found"""
        assert extract_date_from_title('Some random video title') is None
        assert extract_date_from_title('9 PM | ETV Telugu News') is None
        assert extract_date_from_title('') is None


class TestGetYoutubeApiClient:
    """Test get_youtube_api_client function"""
    
    @patch('scripts.youtube_fetcher.build')
    def test_get_youtube_api_client_success(self, mock_build):
        """Test successful YouTube API client creation"""
        mock_client = Mock()
        mock_build.return_value = mock_client
        
        api_key = "test_api_key_123"
        client = get_youtube_api_client(api_key)
        
        assert client == mock_client
        mock_build.assert_called_once_with('youtube', 'v3', developerKey=api_key)
    
    @patch('scripts.youtube_fetcher.build')
    def test_get_youtube_api_client_auth_error(self, mock_build):
        """Test authentication error handling"""
        mock_build.side_effect = Exception("Invalid API key")
        
        api_key = "invalid_key"
        with pytest.raises(Exception, match="Invalid API key"):
            get_youtube_api_client(api_key)


class TestSearchChannelVideos:
    """Test search_channel_videos function"""
    
    @patch('scripts.youtube_fetcher.datetime')
    def test_search_channel_videos_found(self, mock_datetime):
        """Test successful video search"""
        # Mock datetime for date filtering
        from datetime import datetime
        mock_datetime.fromisoformat.return_value = datetime(2025, 12, 8, 0, 0, 0)
        mock_datetime.strptime = datetime.strptime
        
        # Mock API client
        mock_client = Mock()
        mock_search = Mock()
        mock_client.search.return_value = mock_search
        mock_list = Mock()
        mock_search.list.return_value = mock_list
        
        # Mock API response
        mock_list.execute.return_value = {
            'items': [
                {
                    'id': {'videoId': 'test_video_123'},
                    'snippet': {
                        'title': '9 PM | ETV Telugu News | 8th December 2025',
                        'publishedAt': '2025-12-07T15:30:00Z'
                    }
                }
            ]
        }
        
        result = search_channel_videos(
            mock_client,
            "UCJi8M0hRKjz8SLPvJKEVTOg",
            "9pm",
            "2025-12-08"
        )
        
        assert result is not None
        assert result['video_id'] == 'test_video_123'
        assert result['title'] == '9 PM | ETV Telugu News | 8th December 2025'
        assert result['published_at'] == '2025-12-07T15:30:00Z'
    
    def test_search_channel_videos_not_found(self):
        """Test video not found scenario"""
        # Mock API client
        mock_client = Mock()
        mock_search = Mock()
        mock_client.search.return_value = mock_search
        mock_list = Mock()
        mock_search.list.return_value = mock_list
        
        # Mock empty API response
        mock_list.execute.return_value = {'items': []}
        
        result = search_channel_videos(
            mock_client,
            "UCJi8M0hRKjz8SLPvJKEVTOg",
            "9pm",
            "2025-12-08"
        )
        
        assert result is None
    
    def test_search_channel_videos_api_error(self):
        """Test API error handling - should return None and not raise"""
        # Mock API client that raises error
        mock_client = Mock()
        mock_search = Mock()
        mock_client.search.return_value = mock_search
        mock_list = Mock()
        mock_search.list.return_value = mock_list
        mock_list.execute.side_effect = Exception("API quota exceeded")
        
        # Function should catch exception and return None (graceful error handling)
        result = search_channel_videos(
            mock_client,
            "UCJi8M0hRKjz8SLPvJKEVTOg",
            "9pm",
            "2025-12-08"
        )
        
        assert result is None

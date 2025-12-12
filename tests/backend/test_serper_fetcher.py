"""
Tests for SerperDev-based YouTube video fetcher.
Tests the SerperDev API integration and video searching functionality.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from scripts.serper_fetcher import (
    get_serper_api_key,
    extract_date_from_title,
    extract_video_id_from_url,
    search_youtube_via_serper,
    search_video
)


class TestGetSerperApiKey:
    """Test get_serper_api_key function"""
    
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_api_key_123'})
    def test_get_api_key_success(self):
        """Test successful API key retrieval"""
        key = get_serper_api_key()
        assert key == 'test_api_key_123'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_api_key_missing(self):
        """Test error when API key is missing"""
        with pytest.raises(ValueError, match="SERPER_API_KEY environment variable not set"):
            get_serper_api_key()
    
    @patch.dict(os.environ, {'SERPER_API_KEY': ''})
    def test_get_api_key_empty(self):
        """Test error when API key is empty"""
        with pytest.raises(ValueError, match="SERPER_API_KEY environment variable not set"):
            get_serper_api_key()
    
    @patch.dict(os.environ, {'SERPER_API_KEY': '  whitespace_key  '})
    def test_get_api_key_strips_whitespace(self):
        """Test that whitespace is stripped from API key"""
        key = get_serper_api_key()
        assert key == 'whitespace_key'


class TestExtractDateFromTitle:
    """Test extract_date_from_title function"""
    
    def test_extract_date_standard_format(self):
        """Test extraction from standard title format"""
        title = '9 PM | ETV Telugu News | 8th December "2025"'
        result = extract_date_from_title(title)
        assert result == "2025-12-08"
    
    def test_extract_date_7am_format(self):
        """Test extraction from 7 AM title format"""
        title = '7 AM | ETV Telugu News | 15th January "2025"'
        result = extract_date_from_title(title)
        assert result == "2025-01-15"
    
    def test_extract_date_different_ordinals(self):
        """Test extraction with different ordinal suffixes"""
        # 1st
        assert extract_date_from_title('9 PM | ETV Telugu News | 1st March "2025"') == "2025-03-01"
        # 2nd
        assert extract_date_from_title('9 PM | ETV Telugu News | 2nd April "2025"') == "2025-04-02"
        # 3rd
        assert extract_date_from_title('9 PM | ETV Telugu News | 3rd May "2025"') == "2025-05-03"
        # 21st
        assert extract_date_from_title('9 PM | ETV Telugu News | 21st June "2025"') == "2025-06-21"
        # 22nd
        assert extract_date_from_title('9 PM | ETV Telugu News | 22nd July "2025"') == "2025-07-22"
        # 23rd
        assert extract_date_from_title('9 PM | ETV Telugu News | 23rd August "2025"') == "2025-08-23"
    
    def test_extract_date_all_months(self):
        """Test extraction for all months"""
        months = [
            ("January", "01"), ("February", "02"), ("March", "03"),
            ("April", "04"), ("May", "05"), ("June", "06"),
            ("July", "07"), ("August", "08"), ("September", "09"),
            ("October", "10"), ("November", "11"), ("December", "12")
        ]
        for month_name, month_num in months:
            title = f'9 PM | ETV Telugu News | 5th {month_name} "2025"'
            result = extract_date_from_title(title)
            assert result == f"2025-{month_num}-05"
    
    def test_extract_date_single_digit_day(self):
        """Test extraction with single digit day"""
        title = '9 PM | ETV Telugu News | 5th December "2025"'
        result = extract_date_from_title(title)
        assert result == "2025-12-05"
    
    def test_extract_date_double_digit_day(self):
        """Test extraction with double digit day"""
        title = '9 PM | ETV Telugu News | 25th December "2025"'
        result = extract_date_from_title(title)
        assert result == "2025-12-25"
    
    def test_extract_date_no_match(self):
        """Test when title doesn't contain date"""
        title = "Random video title without date"
        result = extract_date_from_title(title)
        assert result is None
    
    def test_extract_date_html_entities(self):
        """Test extraction with HTML entities in title"""
        title = '9 PM | ETV Telugu News | 8th December &quot;2025&quot;'
        result = extract_date_from_title(title)
        assert result == "2025-12-08"
    
    def test_extract_date_single_quotes(self):
        """Test extraction with single quotes around year"""
        title = "9 PM | ETV Telugu News | 8th December '2025'"
        result = extract_date_from_title(title)
        assert result == "2025-12-08"


class TestExtractVideoIdFromUrl:
    """Test extract_video_id_from_url function"""
    
    def test_extract_from_watch_url(self):
        """Test extraction from standard watch URL"""
        # YouTube video IDs are exactly 11 characters
        url = "https://www.youtube.com/watch?v=abc123XYZ12"
        result = extract_video_id_from_url(url)
        assert result == "abc123XYZ12"
    
    def test_extract_from_watch_url_with_params(self):
        """Test extraction from watch URL with extra parameters"""
        url = "https://www.youtube.com/watch?v=abc123XYZ12&list=PLxyz"
        result = extract_video_id_from_url(url)
        assert result == "abc123XYZ12"
    
    def test_extract_from_short_url(self):
        """Test extraction from short youtu.be URL"""
        url = "https://youtu.be/abc123XYZ12"
        result = extract_video_id_from_url(url)
        assert result == "abc123XYZ12"
    
    def test_extract_from_short_url_with_params(self):
        """Test extraction from short URL with parameters"""
        url = "https://youtu.be/abc123XYZ12?t=120"
        result = extract_video_id_from_url(url)
        assert result == "abc123XYZ12"
    
    def test_extract_from_embed_url(self):
        """Test extraction from embed URL"""
        url = "https://www.youtube.com/embed/abc123XYZ12"
        result = extract_video_id_from_url(url)
        assert result == "abc123XYZ12"
    
    def test_extract_invalid_url(self):
        """Test extraction from invalid URL"""
        url = "https://example.com/video"
        result = extract_video_id_from_url(url)
        assert result is None
    
    def test_extract_empty_url(self):
        """Test extraction from empty URL"""
        result = extract_video_id_from_url("")
        assert result is None


class TestSearchYoutubeViaSerper:
    """Test search_youtube_via_serper function"""
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_successful_search(self, mock_post):
        """Test successful video search"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '9 PM | ETV Telugu News | 8th December "2025"',
                    "link": "https://www.youtube.com/watch?v=test123abcd"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_youtube_via_serper("9pm", "2025-12-08")
        
        assert result is not None
        assert result["video_id"] == "test123abcd"
        assert "9 PM" in result["title"]
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_no_results(self, mock_post):
        """Test search with no results"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"organic": []}
        mock_post.return_value = mock_response
        
        result = search_youtube_via_serper("9pm", "2025-12-08")
        
        assert result is None
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_api_error(self, mock_post):
        """Test handling of API error"""
        import requests as req
        mock_post.side_effect = req.exceptions.RequestException("API Error")
        
        result = search_youtube_via_serper("9pm", "2025-12-08")
        
        assert result is None
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_request_exception(self, mock_post):
        """Test handling of request exception"""
        mock_post.side_effect = Exception("Connection error")
        
        result = search_youtube_via_serper("9pm", "2025-12-08")
        
        assert result is None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_api_key(self):
        """Test handling of missing API key"""
        result = search_youtube_via_serper("9pm", "2025-12-08")
        
        assert result is None


class TestSearchVideo:
    """Test search_video function"""
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_9pm_success(self, mock_post):
        """Test successful 9 PM video search"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '9 PM | ETV Telugu News | 8th December "2025"',
                    "link": "https://www.youtube.com/watch?v=test9pm12ab"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_video("9pm", "2025-12-08")
        
        assert result is not None
        assert result["video_id"] == "test9pm12ab"
        assert "9 PM" in result["title"]
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_7am_success(self, mock_post):
        """Test successful 7 AM video search"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '7 AM | ETV Telugu News | 8th December "2025"',
                    "link": "https://www.youtube.com/watch?v=test7am45cd"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_video("7am", "2025-12-08")
        
        assert result is not None
        assert result["video_id"] == "test7am45cd"
        assert "7 AM" in result["title"]
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_date_mismatch(self, mock_post):
        """Test that videos with wrong date are rejected"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '9 PM | ETV Telugu News | 7th December "2025"',  # Different date
                    "link": "https://www.youtube.com/watch?v=wrong123abc"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_video("9pm", "2025-12-08")  # Looking for 8th
        
        assert result is None
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_no_results(self, mock_post):
        """Test when no videos found"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"organic": []}
        mock_post.return_value = mock_response
        
        result = search_video("9pm", "2025-12-08")
        
        assert result is None
    
    @patch.dict(os.environ, {}, clear=True)
    def test_search_video_api_failure(self):
        """Test when API key is missing"""
        result = search_video("9pm", "2025-12-08")
        
        assert result is None
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_selects_correct_match(self, mock_post):
        """Test that correct video is selected from multiple results"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '9 PM | ETV Telugu News | 7th December "2025"',  # Wrong date
                    "link": "https://www.youtube.com/watch?v=wrong123abc"
                },
                {
                    "title": '9 PM | ETV Telugu News | 8th December "2025"',  # Correct date
                    "link": "https://www.youtube.com/watch?v=correct456d"
                },
                {
                    "title": '9 PM | ETV Telugu News | 9th December "2025"',  # Wrong date
                    "link": "https://www.youtube.com/watch?v=wrong789efg"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_video("9pm", "2025-12-08")
        
        assert result is not None
        assert result["video_id"] == "correct456d"
    
    @patch('scripts.serper_fetcher.requests.post')
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_key'})
    def test_search_video_invalid_video_id(self, mock_post):
        """Test handling of invalid video URL"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "organic": [
                {
                    "title": '9 PM | ETV Telugu News | 8th December "2025"',
                    "link": "https://invalid-url.com/not-youtube"
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = search_video("9pm", "2025-12-08")
        
        assert result is None

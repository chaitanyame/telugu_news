"""
Tests for Brave Search-based video fetcher.
Tests the Brave Search API integration for finding YouTube videos.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.brave_fetcher import (
    extract_date_from_title,
    extract_video_id_from_url,
    search_youtube_via_brave,
    search_video,
    get_brave_api_key
)


class TestExtractDateFromTitle:
    """Test extract_date_from_title function"""
    
    def test_extract_date_standard_format(self):
        """Test standard date format extraction"""
        title = "9 PM | ETV Telugu News | 9th December 2025"
        result = extract_date_from_title(title)
        assert result == "2025-12-09"
    
    def test_extract_date_with_quotes(self):
        """Test date with quoted year"""
        title = '9 PM | ETV Telugu News | 10th December "2025"'
        result = extract_date_from_title(title)
        assert result == "2025-12-10"
    
    def test_extract_date_with_html_entities(self):
        """Test date with HTML entities in title"""
        title = '9 PM | ETV Telugu News | 9th December &quot;2025&quot;'
        result = extract_date_from_title(title)
        assert result == "2025-12-09"
    
    def test_extract_date_different_day_suffixes(self):
        """Test different day suffixes (st, nd, rd, th)"""
        assert extract_date_from_title("7 AM | ETV Telugu News | 1st January 2025") == "2025-01-01"
        assert extract_date_from_title("7 AM | ETV Telugu News | 2nd February 2025") == "2025-02-02"
        assert extract_date_from_title("7 AM | ETV Telugu News | 3rd March 2025") == "2025-03-03"
        assert extract_date_from_title("7 AM | ETV Telugu News | 4th April 2025") == "2025-04-04"
    
    def test_extract_date_all_months(self):
        """Test all month names"""
        months = [
            ("January", "01"), ("February", "02"), ("March", "03"),
            ("April", "04"), ("May", "05"), ("June", "06"),
            ("July", "07"), ("August", "08"), ("September", "09"),
            ("October", "10"), ("November", "11"), ("December", "12")
        ]
        for month_name, month_num in months:
            title = f"9 PM | ETV Telugu News | 15th {month_name} 2025"
            result = extract_date_from_title(title)
            assert result == f"2025-{month_num}-15", f"Failed for {month_name}"
    
    def test_extract_date_no_match(self):
        """Test title without date"""
        title = "Some random video title"
        result = extract_date_from_title(title)
        assert result is None


class TestExtractVideoIdFromUrl:
    """Test extract_video_id_from_url function"""
    
    def test_extract_video_id_standard_url(self):
        """Test standard YouTube URL"""
        url = "https://www.youtube.com/watch?v=abc123_-XYZ"
        result = extract_video_id_from_url(url)
        assert result == "abc123_-XYZ"
    
    def test_extract_video_id_short_url(self):
        """Test short youtu.be URL"""
        url = "https://youtu.be/abc123_-XYZ"
        result = extract_video_id_from_url(url)
        assert result == "abc123_-XYZ"
    
    def test_extract_video_id_embed_url(self):
        """Test embed URL"""
        url = "https://www.youtube.com/embed/abc123_-XYZ"
        result = extract_video_id_from_url(url)
        assert result == "abc123_-XYZ"
    
    def test_extract_video_id_with_params(self):
        """Test URL with additional parameters"""
        url = "https://www.youtube.com/watch?v=abc123_-XYZ&list=PLxyz&index=1"
        result = extract_video_id_from_url(url)
        assert result == "abc123_-XYZ"
    
    def test_extract_video_id_no_match(self):
        """Test non-YouTube URL"""
        url = "https://example.com/video"
        result = extract_video_id_from_url(url)
        assert result is None


class TestGetBraveApiKey:
    """Test get_brave_api_key function"""
    
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key_123'})
    def test_get_brave_api_key_success(self):
        """Test successful API key retrieval"""
        result = get_brave_api_key()
        assert result == "test_key_123"
    
    @patch.dict('os.environ', {}, clear=True)
    def test_get_brave_api_key_missing(self):
        """Test missing API key raises ValueError"""
        # Remove the key if it exists
        import os
        os.environ.pop('BRAVE_API_KEY', None)
        with pytest.raises(ValueError, match="BRAVE_API_KEY"):
            get_brave_api_key()
    
    @patch.dict('os.environ', {'BRAVE_API_KEY': '  '})
    def test_get_brave_api_key_empty(self):
        """Test empty API key raises ValueError"""
        with pytest.raises(ValueError, match="BRAVE_API_KEY"):
            get_brave_api_key()


class TestSearchYoutubeViaBrave:
    """Test search_youtube_via_brave function"""
    
    @patch('scripts.brave_fetcher.requests.get')
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'})
    def test_search_youtube_via_brave_found(self, mock_get):
        """Test successful video search"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()  # Mock the raise_for_status call
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "url": "https://www.youtube.com/watch?v=test123abcX",
                        "title": "9 PM | ETV Telugu News | 10th December 2025"
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = search_youtube_via_brave("9pm", "2025-12-10")
        
        assert result is not None
        assert result["video_id"] == "test123abcX"
        assert result["source"] == "brave_search"
    
    @patch('scripts.brave_fetcher.requests.get')
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'})
    def test_search_youtube_via_brave_not_found(self, mock_get):
        """Test video not found"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "web": {
                "results": []
            }
        }
        mock_get.return_value = mock_response
        
        result = search_youtube_via_brave("9pm", "2025-12-10")
        
        assert result is None
    
    @patch('scripts.brave_fetcher.requests.get')
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'})
    def test_search_youtube_via_brave_date_mismatch(self, mock_get):
        """Test video found but date doesn't match"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "url": "https://www.youtube.com/watch?v=test123abcX",
                        "title": "9 PM | ETV Telugu News | 9th December 2025"  # Different date
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = search_youtube_via_brave("9pm", "2025-12-10")
        
        assert result is None
    
    @patch('scripts.brave_fetcher.requests.get')
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'})
    def test_search_youtube_via_brave_slot_mismatch(self, mock_get):
        """Test video found but time slot doesn't match"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {
                        "url": "https://www.youtube.com/watch?v=test123abcX",
                        "title": "7 AM | ETV Telugu News | 10th December 2025"  # 7 AM not 9 PM
                    }
                ]
            }
        }
        mock_get.return_value = mock_response
        
        result = search_youtube_via_brave("9pm", "2025-12-10")
        
        assert result is None
    
    @patch.dict('os.environ', {}, clear=True)
    def test_search_youtube_via_brave_no_api_key(self):
        """Test search without API key returns None"""
        import os
        os.environ.pop('BRAVE_API_KEY', None)
        result = search_youtube_via_brave("9pm", "2025-12-10")
        assert result is None
    
    @patch('scripts.brave_fetcher.requests.get')
    @patch.dict('os.environ', {'BRAVE_API_KEY': 'test_key'})
    def test_search_youtube_via_brave_api_error(self, mock_get):
        """Test API error handling"""
        mock_get.side_effect = Exception("API error")
        
        result = search_youtube_via_brave("9pm", "2025-12-10")
        
        assert result is None


class TestSearchVideo:
    """Test search_video main entry point"""
    
    @patch('scripts.brave_fetcher.search_youtube_via_brave')
    def test_search_video_calls_brave(self, mock_brave):
        """Test search_video calls brave search"""
        mock_brave.return_value = {"video_id": "test123", "title": "Test", "source": "brave_search"}
        
        result = search_video("9pm", "2025-12-10")
        
        mock_brave.assert_called_once_with("9pm", "2025-12-10")
        assert result["video_id"] == "test123"

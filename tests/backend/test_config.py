"""
Tests for configuration manager
Tests the configuration constants and environment variable loading.
"""
import pytest
import os
from unittest.mock import patch
from scripts.utils.config import (
    ETV_AP_CHANNEL_ID,
    ETV_TELUGU_CHANNEL_ID,
    ALL_CHANNEL_IDS,
    VIDEO_PATTERN_9PM,
    VIDEO_PATTERN_7AM,
    DATA_RETENTION_DAYS,
    get_youtube_api_key,
    get_gemini_api_key
)


class TestConfigConstants:
    """Test configuration constants"""
    
    def test_etv_channel_ids(self):
        """Test ETV channel ID constants"""
        assert ETV_AP_CHANNEL_ID == "UCJi8M0hRKjz8SLPvJKEVTOg"
        assert ETV_TELUGU_CHANNEL_ID == "UCSs9H1cyB3OHdy8wkit8ZKg"
        assert isinstance(ETV_AP_CHANNEL_ID, str)
        assert isinstance(ETV_TELUGU_CHANNEL_ID, str)
    
    def test_all_channel_ids(self):
        """Test ALL_CHANNEL_IDS contains both channels"""
        assert ETV_TELUGU_CHANNEL_ID in ALL_CHANNEL_IDS
        assert ETV_AP_CHANNEL_ID in ALL_CHANNEL_IDS
        assert len(ALL_CHANNEL_IDS) == 2
    
    def test_video_pattern_9pm(self):
        """Test 9 PM video pattern regex"""
        import re
        pattern = re.compile(VIDEO_PATTERN_9PM)
        
        # Should match
        assert pattern.match("9 PM | ETV Telugu News | 8th December 2025")
        assert pattern.match("9 PM | ETV Telugu News | Latest")
        
        # Should not match
        assert not pattern.match("7 AM | ETV Telugu News | 8th December 2025")
        assert not pattern.match("Evening News")
    
    def test_video_pattern_7am(self):
        """Test 7 AM video pattern regex"""
        import re
        pattern = re.compile(VIDEO_PATTERN_7AM)
        
        # Should match
        assert pattern.match("7 AM | ETV Telugu News | 8th December 2025")
        assert pattern.match("7 AM | ETV Telugu News | Latest")
        
        # Should not match
        assert not pattern.match("9 PM | ETV Telugu News | 8th December 2025")
        assert not pattern.match("Morning News")
    
    def test_data_retention_days(self):
        """Test data retention days constant"""
        assert DATA_RETENTION_DAYS == 30
        assert isinstance(DATA_RETENTION_DAYS, int)


class TestGetYoutubeApiKey:
    """Test get_youtube_api_key function"""
    
    @patch.dict(os.environ, {'YOUTUBE_API_KEY': 'test_youtube_key_123'})
    def test_get_youtube_api_key_success(self):
        """Test successful retrieval of YouTube API key"""
        key = get_youtube_api_key()
        assert key == 'test_youtube_key_123'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_youtube_api_key_missing(self):
        """Test error when YouTube API key is missing"""
        with pytest.raises(ValueError, match="YOUTUBE_API_KEY environment variable not set"):
            get_youtube_api_key()
    
    @patch.dict(os.environ, {'YOUTUBE_API_KEY': ''})
    def test_get_youtube_api_key_empty(self):
        """Test error when YouTube API key is empty"""
        with pytest.raises(ValueError, match="YOUTUBE_API_KEY environment variable not set"):
            get_youtube_api_key()


class TestGetGeminiApiKey:
    """Test get_gemini_api_key function"""
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': 'test_gemini_key_456'})
    def test_get_gemini_api_key_success(self):
        """Test successful retrieval of Gemini API key"""
        key = get_gemini_api_key()
        assert key == 'test_gemini_key_456'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_gemini_api_key_missing(self):
        """Test error when Gemini API key is missing"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            get_gemini_api_key()
    
    @patch.dict(os.environ, {'GEMINI_API_KEY': ''})
    def test_get_gemini_api_key_empty(self):
        """Test error when Gemini API key is empty"""
        with pytest.raises(ValueError, match="GEMINI_API_KEY environment variable not set"):
            get_gemini_api_key()


class TestGetBraveApiKey:
    """Test get_brave_api_key function"""
    
    @patch.dict(os.environ, {'BRAVE_API_KEY': 'test_brave_key_789'})
    def test_get_brave_api_key_success(self):
        """Test successful retrieval of Brave Search API key"""
        from scripts.utils.config import get_brave_api_key
        key = get_brave_api_key()
        assert key == 'test_brave_key_789'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_brave_api_key_missing(self):
        """Test error when Brave Search API key is missing"""
        from scripts.utils.config import get_brave_api_key
        with pytest.raises(ValueError, match="BRAVE_API_KEY environment variable not set"):
            get_brave_api_key()
    
    @patch.dict(os.environ, {'BRAVE_API_KEY': ''})
    def test_get_brave_api_key_empty(self):
        """Test error when Brave Search API key is empty"""
        from scripts.utils.config import get_brave_api_key
        with pytest.raises(ValueError, match="BRAVE_API_KEY environment variable not set"):
            get_brave_api_key()


class TestGetSerperApiKey:
    """Test get_serper_api_key function"""
    
    @patch.dict(os.environ, {'SERPER_API_KEY': 'test_serper_key_abc'})
    def test_get_serper_api_key_success(self):
        """Test successful retrieval of SerperDev API key"""
        from scripts.utils.config import get_serper_api_key
        key = get_serper_api_key()
        assert key == 'test_serper_key_abc'
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_serper_api_key_missing(self):
        """Test error when SerperDev API key is missing"""
        from scripts.utils.config import get_serper_api_key
        with pytest.raises(ValueError, match="SERPER_API_KEY environment variable not set"):
            get_serper_api_key()
    
    @patch.dict(os.environ, {'SERPER_API_KEY': ''})
    def test_get_serper_api_key_empty(self):
        """Test error when SerperDev API key is empty"""
        from scripts.utils.config import get_serper_api_key
        with pytest.raises(ValueError, match="SERPER_API_KEY environment variable not set"):
            get_serper_api_key()

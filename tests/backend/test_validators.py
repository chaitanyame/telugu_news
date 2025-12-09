"""
Tests for JSON validators
Tests the validation functions for news files, dates, and video IDs.
"""
import pytest
from scripts.utils.validators import validate_news_file, validate_date_format, validate_video_id


class TestValidateNewsFile:
    """Test validate_news_file function"""
    
    def test_valid_news_file(self):
        """Test validation of correctly structured news file"""
        valid_data = {
            "date": "2025-12-08",
            "slots": {
                "9pm": {
                    "video_id": "dQw4w9WgXcQ",
                    "title": "9 PM | ETV Telugu News | 8th December 2025",
                    "summary": ["న్యూస్ 1", "న్యూస్ 2"],
                    "published_at": "2025-12-07T15:30:00Z"
                },
                "7am": None
            }
        }
        assert validate_news_file(valid_data) is True
    
    def test_invalid_news_file_missing_date(self):
        """Test validation fails when date is missing"""
        invalid_data = {
            "slots": {
                "9pm": None,
                "7am": None
            }
        }
        assert validate_news_file(invalid_data) is False
    
    def test_invalid_news_file_missing_slots(self):
        """Test validation fails when slots key is missing"""
        invalid_data = {
            "date": "2025-12-08"
        }
        assert validate_news_file(invalid_data) is False
    
    def test_invalid_news_file_bad_slot_structure(self):
        """Test validation fails when slot structure is incorrect"""
        invalid_data = {
            "date": "2025-12-08",
            "slots": {
                "9pm": {
                    "video_id": "test123"
                    # Missing required fields
                }
            }
        }
        assert validate_news_file(invalid_data) is False


class TestValidateDateFormat:
    """Test validate_date_format function"""
    
    def test_valid_date_format(self):
        """Test validation of correct YYYY-MM-DD format"""
        assert validate_date_format("2025-12-08") is True
        assert validate_date_format("2025-01-01") is True
        assert validate_date_format("2025-12-31") is True
    
    def test_invalid_date_format(self):
        """Test validation fails for incorrect formats"""
        assert validate_date_format("08-12-2025") is False
        assert validate_date_format("2025/12/08") is False
        assert validate_date_format("12-08-2025") is False
        assert validate_date_format("2025-13-01") is False  # Invalid month
        assert validate_date_format("2025-12-32") is False  # Invalid day
    
    def test_invalid_date_type(self):
        """Test validation fails for non-string input"""
        assert validate_date_format(None) is False
        assert validate_date_format(20251208) is False


class TestValidateVideoId:
    """Test validate_video_id function"""
    
    def test_valid_video_id(self):
        """Test validation of correct YouTube video ID format"""
        assert validate_video_id("dQw4w9WgXcQ") is True
        assert validate_video_id("oHg5SJYRHA0") is True
        assert validate_video_id("_ZTYgq4EoRo") is True  # With underscore
        assert validate_video_id("9bZkp7q19f0") is True  # With numbers
    
    def test_invalid_video_id(self):
        """Test validation fails for incorrect video IDs"""
        assert validate_video_id("") is False
        assert validate_video_id("short") is False  # Too short
        assert validate_video_id("this-is-way-too-long-to-be-valid") is False
        assert validate_video_id("invalid#chars!") is False
        assert validate_video_id(None) is False

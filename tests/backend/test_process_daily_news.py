"""
Tests for main processing script
Tests end-to-end orchestration of the news processing pipeline.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from scripts.process_daily_news import main, process_time_slot


class TestProcessTimeSlot:
    """Test process_time_slot orchestration function"""
    
    @patch('scripts.process_daily_news.get_gemini_api_key')
    @patch('scripts.process_daily_news.is_video_processed')
    @patch('scripts.process_daily_news.search_video')
    @patch('scripts.process_daily_news.get_gemini_summary')
    @patch('scripts.process_daily_news.load_or_create_news_file')
    @patch('scripts.process_daily_news.update_news_slot')
    @patch('scripts.process_daily_news.save_news_file')
    @patch('scripts.process_daily_news.generate_index')
    @patch('scripts.process_daily_news.mark_video_processed')
    def test_successful_processing(
        self, mock_mark, mock_gen_index, mock_save, mock_update,
        mock_load, mock_gemini, mock_search, mock_is_processed, mock_gemini_key
    ):
        """Test successful end-to-end processing"""
        # Mock API key
        mock_gemini_key.return_value = "test_gemini_key"
        
        # Mock video not processed
        mock_is_processed.return_value = False
        
        # Mock video search result (RSS or API)
        mock_search.return_value = {
            "video_id": "abc12345678",
            "title": "9 PM | ETV Telugu News | 9th December 2025",
            "published_at": "2025-12-09T21:00:00Z"
        }
        
        # Mock Gemini summary
        mock_gemini.return_value = [
            "వార్త 1", "వార్త 2", "వార్త 3", 
            "వార్త 4", "వార్త 5"
        ]
        
        # Mock news file operations
        mock_load.return_value = {
            "date": "2025-12-09",
            "slots": {"9pm": None, "7am": None}
        }
        mock_update.return_value = {
            "date": "2025-12-09",
            "slots": {
                "9pm": {
                    "video_id": "abc12345678",
                    "title": "9 PM | ETV Telugu News | 9th December 2025",
                    "published_at": "2025-12-09T21:00:00Z",
                    "summary": ["వార్త 1", "వార్త 2", "వార్త 3", "వార్త 4", "వార్త 5"]
                },
                "7am": None
            }
        }
        
        # Execute
        result = process_time_slot("9pm", "2025-12-09")
        
        # Verify success
        assert result["success"] is True
        assert result["video_id"] == "abc12345678"
        assert result["summaries_count"] == 5
        
        # Verify all steps called
        mock_is_processed.assert_called_once()
        mock_search.assert_called_once()
        mock_gemini.assert_called_once()
        mock_save.assert_called_once()
        mock_gen_index.assert_called_once()
        mock_mark.assert_called_once()
    
    @patch('scripts.process_daily_news.get_gemini_api_key')
    @patch('scripts.process_daily_news.search_video')
    @patch('scripts.process_daily_news.is_video_processed')
    def test_video_already_processed(
        self, mock_is_processed, mock_search, mock_gemini_key
    ):
        """Test skipping already processed video"""
        mock_gemini_key.return_value = "test_key"
        
        # Mock video found
        mock_search.return_value = {
            "video_id": "abc12345678",
            "title": "9 PM | ETV Telugu News | 9th December 2025",
            "published_at": "2025-12-09T21:00:00Z"
        }
        
        # Video already processed
        mock_is_processed.return_value = True
        
        result = process_time_slot("9pm", "2025-12-09")
        
        assert result["success"] is True
        assert result["skipped"] is True
        assert "already processed" in result["message"]
    
    @patch('scripts.process_daily_news.get_gemini_api_key')
    @patch('scripts.process_daily_news.search_video')
    def test_video_not_found(self, mock_search, mock_gemini_key):
        """Test handling when video not found"""
        mock_gemini_key.return_value = "test_key"
        mock_search.return_value = None
        
        result = process_time_slot("9pm", "2025-12-09")
        
        assert result["success"] is True
        assert result["video_found"] is False
        assert "not found" in result["message"]
    
    @patch('scripts.process_daily_news.get_gemini_api_key')
    def test_missing_api_key(self, mock_gemini_key):
        """Test error handling for missing API key"""
        mock_gemini_key.side_effect = ValueError("Missing API key")
        
        result = process_time_slot("9pm", "2025-12-09")
        
        assert result["success"] is False
        assert "error" in result


class TestMain:
    """Test main entry point"""
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_main_success(self, mock_process):
        """Test main function successful execution"""
        mock_process.return_value = {
            "success": True,
            "video_id": "test123",
            "summaries_count": 5
        }
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--date', '2025-12-09']):
            result = main()
        
        assert result == 0
        mock_process.assert_called_once_with("9pm", "2025-12-09", force=False, dry_run=False)
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_main_failure(self, mock_process):
        """Test main function handles errors"""
        mock_process.return_value = {
            "success": False,
            "error": "API error"
        }
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--date', '2025-12-09']):
            result = main()
        
        assert result == 1

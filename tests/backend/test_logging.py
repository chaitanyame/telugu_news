"""
Tests for logging functionality in process_daily_news.py

Feature #16: Add Logging and Error Reporting
TDD Workflow:
1. RED: Create tests that expect structured JSON logging (will fail)
2. GREEN: Implement Python logging with JSON format
3. REFACTOR: Verify all tests pass
"""

import pytest
import json
import logging
from unittest.mock import patch, MagicMock
from io import StringIO


class TestLoggingConfiguration:
    """Test logging setup and configuration"""
    
    def test_logger_configured_with_json_format(self):
        """Test that logger uses JSON formatter"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        
        # Check logger is configured
        assert logger is not None
        assert logger.name == 'process_daily_news'
        assert logger.level == logging.INFO
        
        # Check handler exists
        assert len(logger.handlers) > 0
        handler = logger.handlers[0]
        
        # Check formatter is JSON-capable
        formatter = handler.formatter
        assert formatter is not None
    
    def test_logger_outputs_to_stdout(self):
        """Test that logs are written to stdout"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        handler = logger.handlers[0]
        
        # Handler should be StreamHandler writing to stdout
        assert isinstance(handler, logging.StreamHandler)
    
    def test_log_levels_configured(self):
        """Test that INFO, WARNING, ERROR levels are available"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        
        # Logger should accept INFO level and above
        assert logger.isEnabledFor(logging.INFO)
        assert logger.isEnabledFor(logging.WARNING)
        assert logger.isEnabledFor(logging.ERROR)


class TestJSONLogging:
    """Test JSON log output format"""
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_info_log_json_format(self, mock_stdout):
        """Test INFO log outputs valid JSON"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        logger.info("Test message", extra={"video_id": "abc123", "slot": "9pm"})
        
        output = mock_stdout.getvalue().strip()
        
        # Output should be valid JSON
        log_data = json.loads(output)
        
        assert log_data["level"] == "INFO"
        assert log_data["message"] == "Test message"
        assert "timestamp" in log_data
        assert log_data.get("video_id") == "abc123"
        assert log_data.get("slot") == "9pm"
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_error_log_json_format(self, mock_stdout):
        """Test ERROR log outputs valid JSON with error details"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        logger.error("API error", extra={"error_type": "ConnectionError", "retry_count": 3})
        
        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)
        
        assert log_data["level"] == "ERROR"
        assert log_data["message"] == "API error"
        assert log_data.get("error_type") == "ConnectionError"
        assert log_data.get("retry_count") == 3
    
    @patch('sys.stdout', new_callable=StringIO)
    def test_warning_log_json_format(self, mock_stdout):
        """Test WARNING log outputs valid JSON"""
        from scripts.process_daily_news import setup_logging
        
        logger = setup_logging()
        logger.warning("Cache miss", extra={"video_id": "xyz789"})
        
        output = mock_stdout.getvalue().strip()
        log_data = json.loads(output)
        
        assert log_data["level"] == "WARNING"
        assert log_data["message"] == "Cache miss"


class TestLoggingIntegration:
    """Test logging integration in process_time_slot"""
    
    @patch('scripts.process_daily_news.get_youtube_api_key')
    @patch('scripts.process_daily_news.get_gemini_api_key')
    @patch('scripts.process_daily_news.get_youtube_api_client')
    @patch('scripts.process_daily_news.search_channel_videos')
    @patch('scripts.process_daily_news.is_video_processed')
    @patch('scripts.process_daily_news.get_gemini_summary')
    @patch('scripts.process_daily_news.load_or_create_news_file')
    @patch('scripts.process_daily_news.update_news_slot')
    @patch('scripts.process_daily_news.save_news_file')
    @patch('scripts.process_daily_news.generate_index')
    @patch('scripts.process_daily_news.mark_video_processed')
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_logs_structured_events(
        self, mock_stdout, mock_mark, mock_gen_index, mock_save, mock_update,
        mock_load, mock_summary, mock_is_processed, mock_search, mock_youtube_client,
        mock_gemini_key, mock_youtube_key
    ):
        """Test that process_time_slot logs structured events"""
        # Setup mocks
        mock_youtube_key.return_value = "test_yt_key"
        mock_gemini_key.return_value = "test_gemini_key"
        mock_youtube_client.return_value = MagicMock()
        mock_search.return_value = {
            "video_id": "test123",
            "title": "Test Video",
            "published_at": "2025-12-09T21:00:00Z"
        }
        mock_is_processed.return_value = False
        mock_summary.return_value = ["Summary 1", "Summary 2", "Summary 3", "Summary 4", "Summary 5"]
        mock_load.return_value = {"date": "2025-12-09", "news": {"9pm": None, "7am": None}}
        mock_update.return_value = {"date": "2025-12-09", "news": {"9pm": {"video_id": "test123"}}}
        
        from scripts.process_daily_news import process_time_slot
        
        result = process_time_slot("9pm", "2025-12-09")
        
        # Capture all log output
        output = mock_stdout.getvalue()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        
        # Should have multiple JSON log entries
        assert len(lines) > 0
        
        # Verify at least one log is valid JSON
        first_log = json.loads(lines[0])
        assert "level" in first_log
        assert "message" in first_log
        assert "timestamp" in first_log
    
    @patch('scripts.process_daily_news.get_youtube_api_key')
    @patch('sys.stdout', new_callable=StringIO)
    def test_process_logs_error_on_failure(self, mock_stdout, mock_youtube_key):
        """Test that errors are logged with ERROR level"""
        mock_youtube_key.side_effect = Exception("API key not found")
        
        from scripts.process_daily_news import process_time_slot
        
        result = process_time_slot("9pm", "2025-12-09")
        
        output = mock_stdout.getvalue()
        
        # Should contain ERROR level log
        assert "ERROR" in output or "error" in output.lower()

"""
Tests for retry logic with exponential backoff
Tests the tenacity-based retry decorator.
"""
import pytest
from unittest.mock import Mock, patch
from tenacity import RetryError
from scripts.utils.error_handler import retry_with_backoff


class TestRetryWithBackoff:
    """Test retry_with_backoff decorator"""
    
    def test_retry_success_first_attempt(self):
        """Test successful execution on first attempt"""
        mock_func = Mock(return_value="success")
        decorated_func = retry_with_backoff(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test successful execution after retries"""
        mock_func = Mock()
        mock_func.side_effect = [
            Exception("Temporary error"),
            Exception("Temporary error"),
            "success"
        ]
        decorated_func = retry_with_backoff(mock_func)
        
        result = decorated_func()
        
        assert result == "success"
        assert mock_func.call_count == 3
    
    def test_retry_exhausted(self):
        """Test all retries exhausted"""
        mock_func = Mock()
        mock_func.side_effect = Exception("Permanent error")
        decorated_func = retry_with_backoff(mock_func)
        
        with pytest.raises(RetryError):
            decorated_func()
        
        # Should try 4 times total (initial + 3 retries)
        assert mock_func.call_count == 4
    
    @patch('time.sleep')
    def test_retry_backoff_delays(self, mock_sleep):
        """Test exponential backoff delays"""
        mock_func = Mock()
        mock_func.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            Exception("Error 3"),
            Exception("Error 4")
        ]
        decorated_func = retry_with_backoff(mock_func)
        
        with pytest.raises(Exception):
            decorated_func()
        
        # Verify sleep was called with increasing delays
        assert mock_sleep.call_count == 3
        # Delays should be approximately 1s, 2s, 4s (exponential)
        delays = [call.args[0] for call in mock_sleep.call_args_list]
        assert len(delays) == 3
        # Check delays are increasing
        assert delays[1] > delays[0]
        assert delays[2] > delays[1]

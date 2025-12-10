"""
Tests for Gemini API client and video summarization
Tests the Google Gemini API integration for Telugu news summarization.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.gemini_processor import get_gemini_summary


class TestGetGeminiSummary:
    """Test get_gemini_summary function"""
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_success(self, mock_client_class):
        """Test successful video summarization"""
        # Mock client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '''[
            "న్యూస్ 1: తెలంగాణ రాష్ట్రంలో కొత్త పథకం ప్రారంభం",
            "న్యూస్ 2: హైదరాబాద్ మెట్రో కొత్త రూట్లు",
            "న్యూస్ 3: ఐటీ రంగంలో వృద్ధి",
            "న్యూస్ 4: వ్యవసాయ రంగంలో కొత్త ఆవిష్కరణలు",
            "న్యూస్ 5: విద్యారంగంలో మార్పులు"
        ]'''
        mock_client.models.generate_content.return_value = mock_response
        
        result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 5
        assert "తెలంగాణ" in result[0]
        mock_client_class.assert_called_once_with(api_key="test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_with_code_block(self, mock_client_class):
        """Test handling of markdown code block wrapper"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '''```json
["వార్త 1", "వార్త 2", "వార్త 3", "వార్త 4", "వార్త 5"]
```'''
        mock_client.models.generate_content.return_value = mock_response
        
        result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 5
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_empty_response(self, mock_client_class):
        """Test handling of empty API response"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = ""
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="empty response"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_invalid_json(self, mock_client_class):
        """Test invalid JSON response handling"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = "Not valid JSON"
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Failed to parse"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_not_array(self, mock_client_class):
        """Test handling when response is not an array"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '{"summaries": ["item1", "item2"]}'
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="not a JSON array"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_too_few_items(self, mock_client_class):
        """Test handling when response has too few items"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '["item1", "item2", "item3"]'
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Expected 5-8 summaries"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_too_many_items(self, mock_client_class):
        """Test handling when response has too many items"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        items = '["item1", "item2", "item3", "item4", "item5", "item6", "item7", "item8", "item9", "item10"]'
        mock_response.text = items
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Expected 5-8 summaries"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_non_string_items(self, mock_client_class):
        """Test handling when array items are not strings"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '[1, 2, 3, 4, 5]'
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="must be strings"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_rate_limit_retry(self, mock_client_class):
        """Test rate limit retry logic"""
        from google.genai.errors import ClientError
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # First call raises rate limit error, second succeeds
        # response_json must have proper format for ClientError
        error = ClientError(code=429, response_json={"error": {"message": "rate limited"}})
        mock_response = Mock()
        mock_response.text = '["వార్త 1", "వార్త 2", "వార్త 3", "వార్త 4", "వార్త 5"]'
        
        mock_client.models.generate_content.side_effect = [error, mock_response]
        
        # Patch sleep to avoid waiting
        with patch('scripts.gemini_processor.time.sleep'):
            result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 5
        assert mock_client.models.generate_content.call_count == 2
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_max_retries_exceeded(self, mock_client_class):
        """Test behavior when all retries are exhausted"""
        from google.genai.errors import ClientError
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # All calls raise rate limit error
        error = ClientError(code=429, response_json={"error": {"message": "rate limited"}})
        mock_client.models.generate_content.side_effect = error
        
        # Patch sleep to avoid waiting
        with patch('scripts.gemini_processor.time.sleep'):
            with pytest.raises(ValueError, match="rate limit"):
                get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_connection_error_retry(self, mock_client_class):
        """Test connection error retry logic"""
        from requests.exceptions import ConnectionError
        
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        # First call raises connection error, second succeeds
        mock_response = Mock()
        mock_response.text = '["వార్త 1", "వార్త 2", "వార్త 3", "వార్త 4", "వార్త 5"]'
        
        mock_client.models.generate_content.side_effect = [
            ConnectionError("Network error"),
            mock_response
        ]
        
        # Patch sleep to avoid waiting
        with patch('scripts.gemini_processor.time.sleep'):
            result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 5

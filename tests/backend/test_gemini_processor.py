"""
Tests for Gemini API client and video summarization
Tests the Google Gemini API integration for Telugu news summarization.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from scripts.gemini_processor import create_gemini_client, get_gemini_summary


class TestCreateGeminiClient:
    """Test create_gemini_client function"""
    
    @patch('scripts.gemini_processor.genai.configure')
    @patch('scripts.gemini_processor.genai.GenerativeModel')
    def test_create_gemini_client_success(self, mock_model, mock_configure):
        """Test successful Gemini API client creation"""
        mock_client = Mock()
        mock_model.return_value = mock_client
        
        api_key = "test_gemini_key_123"
        client = create_gemini_client(api_key)
        
        mock_configure.assert_called_once_with(api_key=api_key)
        mock_model.assert_called_once_with("gemini-2.0-flash-exp")
        assert client == mock_client
    
    @patch('scripts.gemini_processor.genai.configure')
    def test_create_gemini_client_auth_error(self, mock_configure):
        """Test authentication error handling"""
        mock_configure.side_effect = Exception("Invalid API key")
        
        api_key = "invalid_key"
        with pytest.raises(Exception, match="Invalid API key"):
            create_gemini_client(api_key)


class TestGetGeminiSummary:
    """Test get_gemini_summary function"""
    
    @patch('scripts.gemini_processor.create_gemini_client')
    def test_get_gemini_summary_success(self, mock_create_client):
        """Test successful video summarization"""
        # Mock client and response
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '''[
            "న్యూస్ 1: తెలంగాణ రాష్ట్రంలో కొత్త పథకం ప్రారంభం",
            "న్యూస్ 2: హైదరాబాద్ మెట్రో కొత్త రూట్లు",
            "న్యూస్ 3: ఐటీ రంగంలో వృద్ధి",
            "న్యూస్ 4: వ్యవసాయ రంగంలో కొత్త ఆవిష్కరణలు",
            "న్యూస్ 5: విద్యారంగంలో మార్పులు"
        ]'''
        mock_client.generate_content.return_value = mock_response
        
        result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 5
        assert "తెలంగాణ" in result[0]
    
    @patch('scripts.gemini_processor.create_gemini_client')
    def test_get_gemini_summary_api_error(self, mock_create_client):
        """Test API error handling"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        mock_client.generate_content.side_effect = Exception("API rate limit")
        
        with pytest.raises(Exception, match="API rate limit"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.create_gemini_client')
    def test_get_gemini_summary_invalid_response(self, mock_create_client):
        """Test invalid JSON response handling"""
        mock_client = Mock()
        mock_create_client.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = "Not valid JSON"
        mock_client.generate_content.return_value = mock_response
        
        with pytest.raises(Exception):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")

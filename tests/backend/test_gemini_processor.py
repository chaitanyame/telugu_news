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
        """Test successful video summarization with comprehensive summaries"""
        # Mock client and response
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '''[
            "రాజకీయాలు: తెలంగాణ రాష్ట్రంలో కొత్త పథకం ప్రారంభం. ముఖ్యమంత్రి రేవంత్ రెడ్డి ప్రకటించిన పథకం 50 లక్షల మందికి లబ్ధి చేకూర్చనుంది",
            "రవాణా: హైదరాబాద్ మెట్రో కొత్త రూట్లు ప్రారంభం. ఎల్బీనగర్ నుండి మియాపూర్ వరకు కొత్త లైన్ పనులు షురూ",
            "వ్యాపారం: ఐటీ రంగంలో వృద్ధి కొనసాగుతోంది. హైదరాబాద్‌లో 10 కొత్త కంపెనీలు ప్రారంభం, 5000 ఉద్యోగాలు",
            "వ్యవసాయం: వ్యవసాయ రంగంలో కొత్త ఆవిష్కరణలు. ప్రభుత్వం రైతులకు 50% సబ్సిడీతో డ్రోన్లు అందజేయనుంది",
            "విద్య: విద్యారంగంలో మార్పులు. ప్రభుత్వ పాఠశాలల్లో ఇంగ్లీష్ మీడియం ప్రారంభం, 10 లక్షల విద్యార్థులకు లబ్ధి",
            "క్రీడలు: హైదరాబాద్‌లో క్రికెట్ మ్యాచ్. భారత్ vs ఆస్ట్రేలియా టెస్ట్ మ్యాచ్ రేపటి నుండి ప్రారంభం",
            "ఆరోగ్యం: ప్రభుత్వ ఆసుపత్రుల్లో కొత్త సౌకర్యాలు. 100 కొత్త ఐసీయూ బెడ్లు అందుబాటులోకి వచ్చాయి",
            "వాతావరణం: తెలంగాణలో వర్షాలు. హైదరాబాద్, రంగారెడ్డి జిల్లాల్లో భారీ వర్షాలు కురిసే అవకాశం ఉందని వాతావరణ శాఖ హెచ్చరిక"
        ]'''
        mock_client.models.generate_content.return_value = mock_response
        
        result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 8
        assert "తెలంగాణ" in result[0]
        assert "రాజకీయాలు:" in result[0]
        mock_client_class.assert_called_once_with(api_key="test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_with_code_block(self, mock_client_class):
        """Test handling of markdown code block wrapper"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '''```json
["రాజకీయాలు: వార్త 1 - ముఖ్యమైన రాజకీయ పరిణామాలు జరిగాయి", "క్రీడలు: వార్త 2 - క్రికెట్ మ్యాచ్‌లో భారత్ విజయం సాధించింది", "వ్యాపారం: వార్త 3 - స్టాక్ మార్కెట్‌లో పెరుగుదల కనిపించింది", "విద్య: వార్త 4 - పాఠశాలల్లో కొత్త విధానాలు అమలు అవుతున్నాయి", "ఆరోగ్యం: వార్త 5 - ప్రభుత్వ ఆసుపత్రుల్లో మెరుగుదల జరిగింది", "వాతావరణం: వార్త 6 - రాష్ట్రంలో వర్షాలు కురిసే అవకాశం ఉంది", "రవాణా: వార్త 7 - మెట్రో రైలు సేవలు విస్తరించబడ్డాయి", "వ్యవసాయం: వార్త 8 - రైతులకు కొత్త పథకాలు ప్రకటించారు"]
```'''
        mock_client.models.generate_content.return_value = mock_response
        
        result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 8
    
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
        """Test handling when response has too few items (less than 8)"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '["రాజకీయాలు: వార్త 1 - ముఖ్యమైన పరిణామాలు జరిగాయి", "క్రీడలు: వార్త 2 - మ్యాచ్‌లో విజయం సాధించారు", "వ్యాపారం: వార్త 3 - మార్కెట్‌లో మార్పులు వచ్చాయి"]'
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Expected 8-12 summaries"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_too_many_items(self, mock_client_class):
        """Test handling when response has too many items (more than 12)"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        items = '["రాజకీయాలు: వార్త 1 - పరిణామాలు జరిగాయి", "క్రీడలు: వార్త 2 - విజయం సాధించారు", "వ్యాపారం: వార్త 3 - మార్పులు వచ్చాయి", "విద్య: వార్త 4 - విధానాలు అమలయ్యాయి", "ఆరోగ్యం: వార్త 5 - మెరుగుదల జరిగింది", "వాతావరణం: వార్త 6 - వర్షాలు కురిశాయి", "రవాణా: వార్త 7 - సేవలు విస్తరించాయి", "వ్యవసాయం: వార్త 8 - పథకాలు ప్రకటించారు", "నేరం: వార్త 9 - కేసు నమోదైంది", "సినిమా: వార్త 10 - చిత్రం విడుదలైంది", "అంతర్జాతీయం: వార్త 11 - సమావేశం జరిగింది", "టెక్నాలజీ: వార్త 12 - ఆవిష్కరణ జరిగింది", "ఇతరం: వార్త 13 - అదనపు వార్త", "మరో: వార్త 14 - ఇంకో వార్త", "చివరి: వార్త 15 - చివరి వార్త"]'
        mock_response.text = items
        mock_client.models.generate_content.return_value = mock_response
        
        with pytest.raises(ValueError, match="Expected 8-12 summaries"):
            get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
    
    @patch('scripts.gemini_processor.genai.Client')
    def test_get_gemini_summary_non_string_items(self, mock_client_class):
        """Test handling when array items are not strings"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_response = Mock()
        mock_response.text = '[1, 2, 3, 4, 5, 6, 7, 8]'
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
        mock_response.text = '["రాజకీయాలు: వార్త 1 - ముఖ్యమైన రాజకీయ పరిణామాలు జరిగాయి", "క్రీడలు: వార్త 2 - క్రికెట్ మ్యాచ్‌లో విజయం సాధించారు", "వ్యాపారం: వార్త 3 - స్టాక్ మార్కెట్‌లో మార్పులు వచ్చాయి", "విద్య: వార్త 4 - పాఠశాలల్లో కొత్త విధానాలు అమలయ్యాయి", "ఆరోగ్యం: వార్త 5 - ప్రభుత్వ ఆసుపత్రుల్లో మెరుగుదల జరిగింది", "వాతావరణం: వార్త 6 - రాష్ట్రంలో వర్షాలు కురిసే అవకాశం", "రవాణా: వార్త 7 - మెట్రో రైలు సేవలు విస్తరించబడ్డాయి", "వ్యవసాయం: వార్త 8 - రైతులకు కొత్త పథకాలు ప్రకటించారు"]'
        
        mock_client.models.generate_content.side_effect = [error, mock_response]
        
        # Patch sleep to avoid waiting
        with patch('scripts.gemini_processor.time.sleep'):
            result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 8
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
        mock_response.text = '["రాజకీయాలు: వార్త 1 - ముఖ్యమైన రాజకీయ పరిణామాలు జరిగాయి", "క్రీడలు: వార్త 2 - క్రికెట్ మ్యాచ్‌లో విజయం సాధించారు", "వ్యాపారం: వార్త 3 - స్టాక్ మార్కెట్‌లో మార్పులు వచ్చాయి", "విద్య: వార్త 4 - పాఠశాలల్లో కొత్త విధానాలు అమలయ్యాయి", "ఆరోగ్యం: వార్త 5 - ప్రభుత్వ ఆసుపత్రుల్లో మెరుగుదల జరిగింది", "వాతావరణం: వార్త 6 - రాష్ట్రంలో వర్షాలు కురిసే అవకాశం ఉంది", "రవాణా: వార్త 7 - మెట్రో రైలు సేవలు విస్తరించబడ్డాయి", "వ్యవసాయం: వార్త 8 - రైతులకు కొత్త పథకాలు ప్రకటించారు"]'
        
        mock_client.models.generate_content.side_effect = [
            ConnectionError("Network error"),
            mock_response
        ]
        
        # Patch sleep to avoid waiting
        with patch('scripts.gemini_processor.time.sleep'):
            result = get_gemini_summary("https://youtube.com/watch?v=test123", "test_key")
        
        assert result is not None
        assert len(result) == 8

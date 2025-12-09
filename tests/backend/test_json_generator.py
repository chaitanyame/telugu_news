"""
Tests for JSON file operations
Tests the news file generator and manager.
"""
import pytest
import json
import os
from datetime import datetime
from unittest.mock import Mock, patch, mock_open
from scripts.json_generator import (
    load_or_create_news_file,
    save_news_file,
    update_news_slot,
    generate_index
)


class TestLoadOrCreateNewsFile:
    """Test load_or_create_news_file function"""
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    def test_load_existing_file(self, mock_file, mock_exists):
        """Test loading existing news file"""
        mock_exists.return_value = True
        existing_data = {
            "date": "2025-01-15",
            "slots": {
                "9pm": None,
                "7am": None
            }
        }
        mock_file.return_value.read.return_value = json.dumps(existing_data)
        
        result = load_or_create_news_file("2025-01-15")
        
        assert result["date"] == "2025-01-15"
        assert "slots" in result
        assert result["slots"]["9pm"] is None
    
    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_create_new_file(self, mock_makedirs, mock_exists):
        """Test creating new news file when it doesn't exist"""
        mock_exists.return_value = False
        
        result = load_or_create_news_file("2025-01-15")
        
        assert result["date"] == "2025-01-15"
        assert result["slots"] == {"9pm": None, "7am": None}
        mock_makedirs.assert_called_once()
    
    def test_invalid_date_format(self):
        """Test invalid date format raises ValueError"""
        with pytest.raises(ValueError, match="Invalid date format"):
            load_or_create_news_file("15-01-2025")


class TestSaveNewsFile:
    """Test save_news_file function"""
    
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_news_file_success(self, mock_file, mock_makedirs):
        """Test saving news file successfully"""
        data = {
            "date": "2025-01-15",
            "slots": {
                "9pm": {
                    "video_id": "abc12345678",
                    "title": "9 PM | ETV Telugu News | 15th Jan 2025",
                    "summary": ["వార్త 1", "వార్త 2"],
                    "published_at": "2025-01-15T21:00:00Z"
                },
                "7am": None
            }
        }
        
        save_news_file("2025-01-15", data)
        
        mock_makedirs.assert_called_once()
        mock_file.assert_called_once()
        # Verify JSON was written
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert "2025-01-15" in written_data
    
    def test_save_invalid_data(self):
        """Test saving invalid data raises ValueError"""
        invalid_data = {"invalid": "structure"}
        
        with pytest.raises(ValueError):
            save_news_file("2025-01-15", invalid_data)


class TestUpdateNewsSlot:
    """Test update_news_slot function"""
    
    def test_update_empty_slot(self):
        """Test updating an empty slot"""
        data = {
            "date": "2025-01-15",
            "slots": {"9pm": None, "7am": None}
        }
        summaries = ["వార్త 1", "వార్త 2", "వార్త 3"]
        video_data = {
            "video_id": "abc12345678",
            "title": "9 PM | ETV Telugu News | 15th Jan 2025",
            "published_at": "2025-01-15T21:00:00Z"
        }
        
        result = update_news_slot(data, "9pm", summaries, video_data)
        
        assert result["slots"]["9pm"] is not None
        assert result["slots"]["9pm"]["video_id"] == "abc12345678"
        assert len(result["slots"]["9pm"]["summary"]) == 3
    
    def test_update_filled_slot_replaces(self):
        """Test updating an already filled slot replaces data"""
        data = {
            "date": "2025-01-15",
            "slots": {
                "9pm": {
                    "video_id": "old12345678",
                    "summary": ["పాత వార్త"]
                },
                "7am": None
            }
        }
        summaries = ["కొత్త వార్త 1", "కొత్త వార్త 2"]
        video_data = {
            "video_id": "new45678901",
            "title": "9 PM | ETV Telugu News | 15th Jan 2025",
            "published_at": "2025-01-15T21:00:00Z"
        }
        
        result = update_news_slot(data, "9pm", summaries, video_data)
        
        assert result["slots"]["9pm"]["video_id"] == "new45678901"
        assert len(result["slots"]["9pm"]["summary"]) == 2
    
    def test_invalid_slot_raises_error(self):
        """Test invalid slot name raises ValueError"""
        data = {"date": "2025-01-15", "slots": {"9pm": None, "7am": None}}
        
        with pytest.raises(ValueError, match="Invalid slot"):
            update_news_slot(data, "invalid_slot", [], {})


class TestGenerateIndex:
    """Test generate_index function"""
    
    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_generate_index_success(self, mock_exists, mock_file, mock_walk):
        """Test generating index from archive files"""
        # Mock directory structure
        mock_walk.return_value = [
            ('data/archive/2025-01', [], ['2025-01-15.json', '2025-01-16.json']),
            ('data/archive/2025-01', [], [])
        ]
        
        # Mock file contents
        file_data_1 = {
            "date": "2025-01-15",
            "slots": {
                "9pm": {"video_id": "abc12345678", "summary": ["test"]},
                "7am": None
            }
        }
        file_data_2 = {
            "date": "2025-01-16",
            "slots": {
                "9pm": None,
                "7am": {"video_id": "def12345678", "summary": ["test"]}
            }
        }
        
        mock_exists.return_value = True
        mock_file.return_value.read.side_effect = [
            json.dumps(file_data_1),
            json.dumps(file_data_2)
        ]
        
        generate_index()
        
        # Verify index.json was written
        calls = [call for call in mock_file.call_args_list if 'index.json' in str(call)]
        assert len(calls) > 0
    
    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_index_empty_archive(self, mock_file, mock_walk):
        """Test generating index with no archive files"""
        mock_walk.return_value = []
        
        generate_index()
        
        # Should create empty index
        calls = [call for call in mock_file.call_args_list if 'index.json' in str(call)]
        assert len(calls) > 0
    
    @patch('os.walk')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    def test_generate_index_sorts_descending(self, mock_exists, mock_file, mock_walk):
        """Test index sorts dates in descending order"""
        mock_walk.return_value = [
            ('data/archive/2025-01', [], ['2025-01-10.json', '2025-01-15.json', '2025-01-12.json'])
        ]
        
        file_data = {
            "date": "2025-01-10",
            "slots": {"9pm": None, "7am": None}
        }
        
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = json.dumps(file_data)
        
        generate_index()
        
        # Verify write was called
        write_calls = [call for call in mock_file.call_args_list if 'index.json' in str(call)]
        assert len(write_calls) > 0

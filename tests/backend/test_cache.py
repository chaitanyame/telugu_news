"""
Tests for video ID caching system
Tests the cache operations for preventing video reprocessing.
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open
from scripts.utils.cache import (
    load_video_cache,
    save_video_cache,
    is_video_processed,
    mark_video_processed
)


class TestLoadVideoCache:
    """Test load_video_cache function"""
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"video123": "2025-12-07"}')
    @patch('os.path.exists')
    def test_load_video_cache_success(self, mock_exists, mock_file):
        """Test successful cache loading"""
        mock_exists.return_value = True
        
        cache = load_video_cache()
        
        assert cache == {"video123": "2025-12-07"}
    
    @patch('os.path.exists')
    def test_load_video_cache_missing_file(self, mock_exists):
        """Test loading when cache file doesn't exist"""
        mock_exists.return_value = False
        
        cache = load_video_cache()
        
        assert cache == {}


class TestSaveVideoCache:
    """Test save_video_cache function"""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.makedirs')
    def test_save_video_cache_success(self, mock_makedirs, mock_file):
        """Test successful cache saving"""
        cache_data = {"video123": "2025-12-07", "video456": "2025-12-08"}
        
        save_video_cache(cache_data)
        
        mock_file.assert_called_once()
        # Verify JSON was written
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        assert 'video123' in written_data


class TestIsVideoProcessed:
    """Test is_video_processed function"""
    
    @patch('scripts.utils.cache.load_video_cache')
    def test_is_video_processed_true(self, mock_load):
        """Test video already processed"""
        mock_load.return_value = {"video123": "2025-12-07"}
        
        result = is_video_processed("video123")
        
        assert result is True
    
    @patch('scripts.utils.cache.load_video_cache')
    def test_is_video_processed_false(self, mock_load):
        """Test video not processed"""
        mock_load.return_value = {"video123": "2025-12-07"}
        
        result = is_video_processed("video999")
        
        assert result is False


class TestMarkVideoProcessed:
    """Test mark_video_processed function"""
    
    @patch('scripts.utils.cache.save_video_cache')
    @patch('scripts.utils.cache.load_video_cache')
    def test_mark_video_processed(self, mock_load, mock_save):
        """Test marking video as processed"""
        mock_load.return_value = {"video123": "2025-12-07"}
        
        mark_video_processed("video456", "2025-12-08")
        
        # Verify save was called with updated cache
        mock_save.assert_called_once()
        saved_cache = mock_save.call_args[0][0]
        assert "video456" in saved_cache
        assert saved_cache["video456"] == "2025-12-08"

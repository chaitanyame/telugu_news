"""
Tests for data cleanup script
Tests the cleanup function for old archive files.
"""
import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from scripts.cleanup import cleanup_old_files


class TestCleanupOldFiles:
    """Test cleanup_old_files function"""
    
    @patch('os.walk')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_removes_old_files(self, mock_remove, mock_getmtime, mock_walk):
        """Test cleanup removes files older than threshold"""
        # Mock current time and file modification times
        now = datetime.now().timestamp()
        old_file_time = (datetime.now() - timedelta(days=35)).timestamp()
        recent_file_time = (datetime.now() - timedelta(days=10)).timestamp()
        
        mock_walk.return_value = [
            ('data/archive/2024-12', [], ['2024-12-01.json', '2024-12-15.json'])
        ]
        
        # First file is old, second is recent
        mock_getmtime.side_effect = [old_file_time, recent_file_time]
        
        result = cleanup_old_files(days_to_keep=30)
        
        assert result["deleted"] == 1
        assert result["kept"] == 1
        mock_remove.assert_called_once()
    
    @patch('os.walk')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_dry_run_mode(self, mock_remove, mock_getmtime, mock_walk):
        """Test dry run mode doesn't delete files"""
        now = datetime.now().timestamp()
        old_file_time = (datetime.now() - timedelta(days=35)).timestamp()
        
        mock_walk.return_value = [
            ('data/archive/2024-12', [], ['2024-12-01.json'])
        ]
        mock_getmtime.return_value = old_file_time
        
        result = cleanup_old_files(days_to_keep=30, dry_run=True)
        
        assert result["would_delete"] == 1
        mock_remove.assert_not_called()
    
    @patch('os.walk')
    def test_cleanup_preserves_index_and_cache(self, mock_walk):
        """Test cleanup skips index.json and cache files"""
        mock_walk.return_value = [
            ('data', [], ['index.json']),
            ('data/cache', [], ['video-ids.json'])
        ]
        
        result = cleanup_old_files(days_to_keep=30)
        
        # These files should be skipped
        assert result["deleted"] == 0
    
    @patch('os.walk')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_handles_errors(self, mock_remove, mock_getmtime, mock_walk):
        """Test cleanup handles file deletion errors gracefully"""
        old_file_time = (datetime.now() - timedelta(days=35)).timestamp()
        
        mock_walk.return_value = [
            ('data/archive/2024-12', [], ['2024-12-01.json'])
        ]
        mock_getmtime.return_value = old_file_time
        mock_remove.side_effect = OSError("Permission denied")
        
        result = cleanup_old_files(days_to_keep=30)
        
        assert result["errors"] == 1
        assert result["deleted"] == 0
    
    @patch('os.walk')
    @patch('os.path.getmtime')
    @patch('os.remove')
    def test_cleanup_custom_threshold(self, mock_remove, mock_getmtime, mock_walk):
        """Test cleanup with custom days threshold"""
        # File is 15 days old
        file_time = (datetime.now() - timedelta(days=15)).timestamp()
        
        mock_walk.return_value = [
            ('data/archive/2025-01', [], ['2025-01-01.json'])
        ]
        mock_getmtime.return_value = file_time
        
        # Should NOT delete with 30 day threshold
        result1 = cleanup_old_files(days_to_keep=30)
        assert result1["deleted"] == 0
        
        # SHOULD delete with 10 day threshold
        result2 = cleanup_old_files(days_to_keep=10)
        assert result2["deleted"] == 1

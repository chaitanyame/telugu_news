"""
Tests for CLI argument parsing in process_daily_news.py

Feature #15: Add Command-Line Interface
TDD Workflow:
1. RED: Create tests that expect argparse CLI (will fail)
2. GREEN: Implement argparse with --slot, --date, --force, --dry-run
3. REFACTOR: Verify all tests pass
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
from datetime import datetime


class TestCLIArgumentParsing:
    """Test CLI argument parsing with argparse"""
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_slot_argument_required(self, mock_process):
        """Test that --slot argument is required"""
        # Missing --slot should show error
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['process_daily_news.py']):
                from scripts.process_daily_news import parse_args
                parse_args()
        
        assert exc_info.value.code == 2  # argparse error code
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_slot_argument_valid_values(self, mock_process):
        """Test that --slot only accepts 9pm or 7am"""
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.slot == '9pm'
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '7am']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.slot == '7am'
        
        # Invalid slot should raise error
        with pytest.raises(SystemExit) as exc_info:
            with patch('sys.argv', ['process_daily_news.py', '--slot', 'invalid']):
                from scripts.process_daily_news import parse_args
                parse_args()
        
        assert exc_info.value.code == 2
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_date_argument_optional_with_default(self, mock_process):
        """Test that --date is optional and defaults to today"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.date == today
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_date_argument_custom_value(self, mock_process):
        """Test that --date accepts custom date in YYYY-MM-DD format"""
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--date', '2025-12-01']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.date == '2025-12-01'
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_force_flag(self, mock_process):
        """Test that --force flag bypasses cache"""
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--force']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.force is True
        
        # Without --force
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.force is False
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_dry_run_flag(self, mock_process):
        """Test that --dry-run flag prevents saving files"""
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--dry-run']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.dry_run is True
        
        # Without --dry-run
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm']):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.dry_run is False
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_combined_flags(self, mock_process):
        """Test combining multiple flags"""
        with patch('sys.argv', [
            'process_daily_news.py',
            '--slot', '7am',
            '--date', '2025-11-15',
            '--force',
            '--dry-run'
        ]):
            from scripts.process_daily_news import parse_args
            args = parse_args()
            assert args.slot == '7am'
            assert args.date == '2025-11-15'
            assert args.force is True
            assert args.dry_run is True


class TestCLIIntegration:
    """Test CLI integration with process_time_slot"""
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_main_with_cli_args(self, mock_process):
        """Test main function uses CLI args correctly"""
        mock_process.return_value = {"success": True}
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--date', '2025-12-09']):
            from scripts.process_daily_news import main
            exit_code = main()
            
            mock_process.assert_called_once_with('9pm', '2025-12-09', force=False, dry_run=False)
            assert exit_code == 0
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_force_flag_passed_to_process(self, mock_process):
        """Test --force flag is passed to process_time_slot"""
        mock_process.return_value = {"success": True}
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--force']):
            from scripts.process_daily_news import main
            main()
            
            # Check that force=True was passed
            call_args = mock_process.call_args
            assert call_args[1]['force'] is True
    
    @patch('scripts.process_daily_news.process_time_slot')
    def test_dry_run_flag_passed_to_process(self, mock_process):
        """Test --dry-run flag is passed to process_time_slot"""
        mock_process.return_value = {"success": True}
        
        with patch('sys.argv', ['process_daily_news.py', '--slot', '9pm', '--dry-run']):
            from scripts.process_daily_news import main
            main()
            
            # Check that dry_run=True was passed
            call_args = mock_process.call_args
            assert call_args[1]['dry_run'] is True

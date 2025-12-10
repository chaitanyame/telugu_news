"""
Main processing script for ETV Telugu News Aggregator.

This script orchestrates the entire pipeline:
1. Load configuration and API keys
2. Check if video already processed
3. Search YouTube for video (RSS first, then API fallback)
4. Get Gemini summary if video found
5. Load or create news file
6. Update news slot
7. Save news file
8. Update index.json
9. Mark video as processed in cache
"""

import sys
import os
import argparse
import logging
import json
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from scripts.utils.config import get_gemini_api_key
from scripts.utils.cache import is_video_processed, mark_video_processed
from scripts.rss_fetcher import search_video_rss
from scripts.gemini_processor import get_gemini_summary
from scripts.json_generator import (
    load_or_create_news_file,
    update_news_slot,
    save_news_file,
    generate_index
)


def get_ist_date() -> str:
    """
    Get current date in IST timezone.
    
    Returns:
        str: Date in YYYY-MM-DD format (IST)
    """
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime('%Y-%m-%d')


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Outputs logs in JSON format for easy parsing by GitHub Actions.
    """
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields if provided
        if hasattr(record, 'video_id'):
            log_data['video_id'] = record.video_id
        if hasattr(record, 'slot'):
            log_data['slot'] = record.slot
        if hasattr(record, 'date'):
            log_data['date'] = record.date
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'retry_count'):
            log_data['retry_count'] = record.retry_count
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging():
    """
    Configure structured JSON logging for GitHub Actions.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger('process_daily_news')
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create console handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Set JSON formatter
    formatter = JSONFormatter()
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


def parse_args():
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Process ETV Telugu News for a specific time slot'
    )
    
    parser.add_argument(
        '--slot',
        required=True,
        choices=['9pm', '7am'],
        help='Time slot to process (9pm or 7am)'
    )
    
    parser.add_argument(
        '--date',
        default=get_ist_date(),
        help='Date to process in YYYY-MM-DD format (default: today in IST)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force processing even if video already in cache'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without saving files (testing mode)'
    )
    
    return parser.parse_args()


def search_video(time_slot: str, date: str, logger) -> Optional[Dict]:
    """
    Search for video using RSS first, then YouTube API as fallback.
    
    Args:
        time_slot: '9pm' or '7am'
        date: Date in YYYY-MM-DD format
        logger: Logger instance
        
    Returns:
        Dict with video_id, title, published_at if found, None otherwise
    """
    # Try RSS first (no API key required)
    logger.info("Trying RSS feed search", extra={"slot": time_slot, "date": date})
    video_data = search_video_rss(None, time_slot, date)
    
    if video_data:
        logger.info("Found video via RSS", extra={"video_id": video_data["video_id"]})
        return video_data
    
    # Fallback to YouTube API if RSS didn't find it
    logger.info("RSS search failed, trying YouTube API", extra={"slot": time_slot, "date": date})
    
    try:
        # Only import YouTube API modules if needed
        from scripts.utils.config import get_youtube_api_key
        from scripts.youtube_fetcher import get_youtube_api_client, search_channel_videos
        
        youtube_api_key = os.environ.get('YOUTUBE_API_KEY', '').strip()
        if not youtube_api_key:
            logger.warning("YOUTUBE_API_KEY not set, skipping API fallback")
            return None
        
        youtube_client = get_youtube_api_client(youtube_api_key)
        video_data = search_channel_videos(youtube_client, None, time_slot, date)
        
        if video_data:
            logger.info("Found video via YouTube API", extra={"video_id": video_data["video_id"]})
            return video_data
            
    except Exception as e:
        logger.warning(f"YouTube API fallback failed: {e}")
    
    return None


def process_time_slot(time_slot: str, date: str, force: bool = False, dry_run: bool = False) -> Dict:
    """
    Process a single time slot for a specific date.
    
    Args:
        time_slot (str): Time slot ('9pm' or '7am')
        date (str): Date in YYYY-MM-DD format
        force (bool): Force processing even if video already in cache
        dry_run (bool): Run without saving files (testing mode)
    
    Returns:
        Dict: Processing result with status and details
    """
    logger = setup_logging()
    
    result = {
        "success": False,
        "time_slot": time_slot,
        "date": date,
        "force": force,
        "dry_run": dry_run
    }
    
    try:
        # Step 1: Load Gemini API key
        logger.info("Processing time slot", extra={"slot": time_slot, "date": date})
        if dry_run:
            logger.info("Running in DRY-RUN mode", extra={"slot": time_slot})
        if force:
            logger.info("FORCE mode enabled", extra={"slot": time_slot})
        
        gemini_api_key = get_gemini_api_key()
        
        # Step 2: Search for video (RSS first, then YouTube API fallback)
        logger.info("Searching for video", extra={"slot": time_slot, "date": date})
        video_data = search_video(time_slot, date, logger)
        
        if video_data is None:
            logger.info("Video not found in any channel", extra={"slot": time_slot, "date": date})
            result["success"] = True
            result["video_found"] = False
            result["message"] = f"Video not found for {time_slot} on {date}"
            return result
        
        # Check if video already processed (skip if force=True)
        video_id = video_data["video_id"]
        if not force and is_video_processed(video_id):
            logger.info("Video already processed, skipping", extra={"video_id": video_id, "slot": time_slot})
            result["success"] = True
            result["skipped"] = True
            result["video_id"] = video_id
            result["message"] = f"Video {video_id} already processed"
            return result
        
        logger.info("Found video", extra={"video_id": video_id, "slot": time_slot})
        
        # Step 4: Get Gemini summary
        logger.info("Generating summary with Gemini", extra={"video_id": video_id})
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        summaries = get_gemini_summary(video_url, gemini_api_key)
        logger.info("Generated summaries", extra={"video_id": video_id, "count": len(summaries)})
        
        # Step 5: Load or create news file
        logger.info("Loading news file", extra={"date": date})
        news_data = load_or_create_news_file(date)
        
        # Step 6: Update news slot
        logger.info("Updating news slot", extra={"slot": time_slot})
        news_data = update_news_slot(news_data, time_slot, summaries, video_data)
        
        # Step 7: Save news file (skip if dry_run)
        if not dry_run:
            logger.info("Saving news file", extra={"date": date})
            save_news_file(date, news_data)
        else:
            logger.info("Skipping save (dry-run mode)")
        
        # Step 8: Update index.json (skip if dry_run)
        if not dry_run:
            logger.info("Updating index")
            generate_index()
        else:
            logger.info("Skipping index update (dry-run mode)")
        
        # Step 9: Mark video as processed (skip if dry_run)
        if not dry_run:
            logger.info("Marking video as processed", extra={"video_id": video_id})
            mark_video_processed(video_id, date)
        else:
            logger.info("Skipping cache update (dry-run mode)")
        
        logger.info("Processing complete", extra={"slot": time_slot, "date": date, "video_id": video_id})
        result["success"] = True
        result["video_id"] = video_id
        result["summaries_count"] = len(summaries)
        result["message"] = f"Successfully processed {time_slot} on {date}"
        
    except Exception as e:
        logger.error("Processing failed", extra={"slot": time_slot, "date": date, "error": str(e)}, exc_info=True)
        result["success"] = False
        result["error"] = str(e)
    
    return result


def main() -> int:
    """
    Main entry point for processing script.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    args = parse_args()
    result = process_time_slot(args.slot, args.date, force=args.force, dry_run=args.dry_run)
    
    if result["success"]:
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

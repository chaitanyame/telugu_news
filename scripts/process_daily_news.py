"""
Main processing script for ETV Telugu News Aggregator.

This script orchestrates the entire pipeline:
1. Load configuration and API keys
2. Check if video already processed
3. Search YouTube for video
4. Get Gemini summary if video found
5. Load or create news file
6. Update news slot
7. Save news file
8. Update index.json
9. Mark video as processed in cache
"""

import sys
import argparse
from typing import Dict
from datetime import datetime
from scripts.utils.config import get_youtube_api_key, get_gemini_api_key, ETV_CHANNEL_ID
from scripts.utils.cache import is_video_processed, mark_video_processed
from scripts.youtube_fetcher import get_youtube_api_client, search_channel_videos
from scripts.gemini_processor import get_gemini_summary
from scripts.json_generator import (
    load_or_create_news_file,
    update_news_slot,
    save_news_file,
    generate_index
)


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
        default=datetime.now().strftime('%Y-%m-%d'),
        help='Date to process in YYYY-MM-DD format (default: today)'
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
    result = {
        "success": False,
        "time_slot": time_slot,
        "date": date,
        "force": force,
        "dry_run": dry_run
    }
    
    try:
        # Step 1: Load API keys
        print(f"[INFO] Processing {time_slot} slot for {date}")
        if dry_run:
            print("[INFO] Running in DRY-RUN mode (no files will be saved)")
        if force:
            print("[INFO] FORCE mode enabled (bypassing cache)")
        
        youtube_api_key = get_youtube_api_key()
        gemini_api_key = get_gemini_api_key()
        
        # Step 2: Check if already processed (we'll check this after finding the video)
        print(f"[INFO] Searching for video...")
        
        # Step 3: Search YouTube for video
        youtube_client = get_youtube_api_client(youtube_api_key)
        video_data = search_channel_videos(youtube_client, ETV_CHANNEL_ID, time_slot, date)
        
        if video_data is None:
            print(f"[INFO] No video found for {time_slot} on {date}")
            result["success"] = True
            result["video_found"] = False
            result["message"] = f"Video not found for {time_slot} on {date}"
            return result
        
        # Check if video already processed (skip if force=True)
        video_id = video_data["video_id"]
        if not force and is_video_processed(video_id):
            print(f"[INFO] Video {video_id} already processed, skipping")
            result["success"] = True
            result["skipped"] = True
            result["video_id"] = video_id
            result["message"] = f"Video {video_id} already processed"
            return result
        
        print(f"[INFO] Found video: {video_id}")
        
        # Step 4: Get Gemini summary
        print(f"[INFO] Generating summary with Gemini...")
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        summaries = get_gemini_summary(video_url, gemini_api_key)
        print(f"[INFO] Generated {len(summaries)} summaries")
        
        # Step 5: Load or create news file
        print(f"[INFO] Loading news file for {date}")
        news_data = load_or_create_news_file(date)
        
        # Step 6: Update news slot
        print(f"[INFO] Updating {time_slot} slot")
        news_data = update_news_slot(news_data, time_slot, summaries, video_data)
        
        # Step 7: Save news file (skip if dry_run)
        if not dry_run:
            print(f"[INFO] Saving news file")
            save_news_file(date, news_data)
        else:
            print(f"[INFO] Skipping save (dry-run mode)")
        
        # Step 8: Update index.json (skip if dry_run)
        if not dry_run:
            print(f"[INFO] Updating index")
            generate_index()
        else:
            print(f"[INFO] Skipping index update (dry-run mode)")
        
        # Step 9: Mark video as processed (skip if dry_run)
        if not dry_run:
            print(f"[INFO] Marking video as processed")
            mark_video_processed(video_id, date)
        else:
            print(f"[INFO] Skipping cache update (dry-run mode)")
        
        print(f"[SUCCESS] Processing complete for {time_slot} on {date}")
        result["success"] = True
        result["video_id"] = video_id
        result["summaries_count"] = len(summaries)
        result["message"] = f"Successfully processed {time_slot} on {date}"
        
    except Exception as e:
        print(f"[ERROR] Processing failed: {str(e)}")
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

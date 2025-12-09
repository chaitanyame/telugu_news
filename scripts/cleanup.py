"""
Data cleanup script for archive files.

This module provides functions to:
1. Delete archive files older than specified threshold
2. Preserve index.json and cache files
3. Support dry-run mode for testing

Usage:
    python -m scripts.cleanup
    python -m scripts.cleanup --days 60
    python -m scripts.cleanup --dry-run
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from typing import Dict


def cleanup_old_files(days_to_keep: int = 30, dry_run: bool = False) -> Dict:
    """
    Clean up archive files older than specified days.
    
    Args:
        days_to_keep (int): Number of days to keep files (default: 30)
        dry_run (bool): If True, don't actually delete files
    
    Returns:
        Dict: Statistics about cleanup operation
            - deleted: Number of files deleted
            - kept: Number of files kept
            - errors: Number of errors encountered
            - would_delete: Number of files that would be deleted (dry_run only)
    """
    stats = {
        "deleted": 0,
        "kept": 0,
        "errors": 0
    }
    
    if dry_run:
        stats["would_delete"] = 0
    
    # Calculate threshold timestamp
    threshold = datetime.now() - timedelta(days=days_to_keep)
    threshold_timestamp = threshold.timestamp()
    
    # Scan data directory
    data_path = "data"
    if not os.path.exists(data_path):
        return stats
    
    # Files to preserve
    preserve_files = ["index.json", "video-ids.json"]
    
    for root, dirs, files in os.walk(data_path):
        for file in files:
            # Skip preserved files
            if file in preserve_files:
                continue
            
            # Skip cache directory
            if "cache" in root:
                continue
            
            file_path = os.path.join(root, file)
            
            try:
                # Check file age
                file_mtime = os.path.getmtime(file_path)
                
                if file_mtime < threshold_timestamp:
                    # File is older than threshold
                    if dry_run:
                        stats["would_delete"] += 1
                    else:
                        try:
                            os.remove(file_path)
                            stats["deleted"] += 1
                        except OSError:
                            stats["errors"] += 1
                else:
                    # File is within threshold
                    stats["kept"] += 1
            
            except OSError:
                stats["errors"] += 1
    
    return stats


def main():
    """
    Main entry point for cleanup script.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        description='Clean up old archive files from data directory'
    )
    
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to keep files (default: 30)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without deleting files (testing mode)'
    )
    
    args = parser.parse_args()
    
    print(f"Starting cleanup: days_to_keep={args.days}, dry_run={args.dry_run}")
    
    try:
        stats = cleanup_old_files(days_to_keep=args.days, dry_run=args.dry_run)
        
        print("\n=== Cleanup Statistics ===")
        if args.dry_run:
            print(f"Would delete: {stats.get('would_delete', 0)} files")
        else:
            print(f"Deleted: {stats['deleted']} files")
        print(f"Kept: {stats['kept']} files")
        print(f"Errors: {stats['errors']}")
        
        if stats['errors'] > 0:
            print("\nWARNING: Some files could not be processed")
            return 1
        
        return 0
    
    except Exception as e:
        print(f"ERROR: Cleanup failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

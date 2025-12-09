"""
Error handling utilities with retry logic and exponential backoff.

This module provides decorators for robust API error handling:
- Retry with exponential backoff for transient failures
- Configurable retry attempts and delays
"""

from tenacity import retry, stop_after_attempt, wait_exponential


# Retry decorator with exponential backoff
# 4 total attempts: initial + 3 retries
# Delays: 1s, 2s, 4s (exponential with multiplier=1, min=1, max=4)
retry_with_backoff = retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=1, max=4)
)

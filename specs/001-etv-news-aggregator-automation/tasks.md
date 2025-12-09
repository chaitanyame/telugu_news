# Task List

**Feature Branch**: 001-etv-news-aggregator-automation  
**Generated from**: [plan.md](plan.md)  
**Date**: 2025-12-08

## Overview
- **Total Tasks**: 45 tasks
- **Estimated Sessions**: 15-20 sessions
- **Critical Path**: Tasks 1-20 (Backend + Automation)
- **TDD Required**: 40 tasks (excluding documentation/config tasks)

---

## Task Categories

### Category 1: Project Foundation (Tasks 1-4)

#### Task 1: Create Directory Structure
- **ID**: T001
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: None
- **Estimated Effort**: 0.25 sessions

**Description**:
Create the complete directory structure for the project, including data storage, Python scripts, tests, and GitHub Actions workflows.

**Acceptance Criteria**:
- [ ] `data/` directory exists
- [ ] `data/cache/` directory exists
- [ ] `data/archive/` directory exists with `.gitkeep`
- [ ] `scripts/` directory exists
- [ ] `scripts/utils/` directory exists
- [ ] `tests/backend/` directory exists
- [ ] `tests/frontend/` directory exists
- [ ] `.github/workflows/` directory exists
- [ ] `css/` directory exists
- [ ] `js/utils/` directory exists
- [ ] `js/components/` directory exists

**Files to Create**:
- `data/.gitkeep`
- `data/cache/.gitkeep`
- `data/archive/.gitkeep`
- `scripts/__init__.py`
- `scripts/utils/__init__.py`
- `tests/backend/__init__.py`
- `tests/frontend/.gitkeep`

**Testing Notes**:
Run `ls -R` and verify all directories exist. Check that Python directories have `__init__.py` files.

**Command**:
```bash
mkdir -p data/cache data/archive scripts/utils tests/backend tests/frontend .github/workflows css js/utils js/components
touch data/.gitkeep data/cache/.gitkeep data/archive/.gitkeep
touch scripts/__init__.py scripts/utils/__init__.py tests/backend/__init__.py tests/frontend/.gitkeep
```

---

#### Task 2: Setup Python Environment
- **ID**: T002
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: T001
- **Estimated Effort**: 0.25 sessions

**Description**:
Create Python requirements file with all necessary dependencies for backend processing.

**Acceptance Criteria**:
- [ ] `scripts/requirements.txt` exists
- [ ] Contains `google-api-python-client==2.100.0`
- [ ] Contains `google-generativeai==0.3.0`
- [ ] Contains `requests==2.31.0`
- [ ] Contains `tenacity==8.2.3`
- [ ] Contains `pytest==7.4.0`
- [ ] `pip install -r scripts/requirements.txt` succeeds

**Files to Create**:
- `scripts/requirements.txt`

**Testing Notes**:
Create a virtual environment, install dependencies, and verify no errors:
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r scripts/requirements.txt
pip list | grep -E "google|requests|tenacity|pytest"
```

---

#### Task 3: Define JSON Schema and Validator
- **ID**: T003
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: T002
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create validator functions to ensure JSON files have correct structure and valid data formats.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_validators.py`
- [ ] Test runs and FAILS initially
- [ ] `scripts/utils/validators.py` created
- [ ] Function `validate_news_file(data: dict) -> bool` implemented
- [ ] Function `validate_date_format(date_str: str) -> bool` implemented
- [ ] Function `validate_video_id(video_id: str) -> bool` implemented
- [ ] All validators check required fields
- [ ] Test runs and PASSES after implementation
- [ ] Code coverage > 80%

**Files to Create**:
- `scripts/utils/validators.py`
- `tests/backend/test_validators.py`

**Testing Notes**:
```bash
# RED: Run test first (should fail)
pytest tests/backend/test_validators.py -v
# Implement validators
# GREEN: Run test again (should pass)
pytest tests/backend/test_validators.py -v
```

**Expected JSON Schema**:
```json
{
  "date": "YYYY-MM-DD",
  "slots": {
    "9pm": {
      "video_id": "string",
      "title": "string",
      "summary": ["string", "string", ...],
      "published_at": "ISO8601 timestamp",
      "processed_at": "ISO8601 timestamp"
    },
    "7am": { /* same structure */ }
  }
}
```

---

#### Task 4: Create Configuration Manager
- **ID**: T004
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: T002
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Create configuration module with all constants and environment variable loading.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_config.py`
- [ ] Test runs and FAILS initially
- [ ] `scripts/utils/config.py` created
- [ ] Constant `ETV_CHANNEL_ID = "UCJi8M0hRKjz8SLPvJKEVTOg"`
- [ ] Constant `VIDEO_PATTERN_9PM = r"^9 PM \| ETV Telugu News \|"`
- [ ] Constant `VIDEO_PATTERN_7AM = r"^7 AM \| ETV Telugu News \|"`
- [ ] Constant `DATA_RETENTION_DAYS = 30`
- [ ] Function `get_youtube_api_key() -> str` loads from env
- [ ] Function `get_gemini_api_key() -> str` loads from env
- [ ] Raises error if secrets missing
- [ ] Test runs and PASSES after implementation

**Files to Create**:
- `scripts/utils/config.py`
- `tests/backend/test_config.py`

**Testing Notes**:
```bash
# RED: Run test first
pytest tests/backend/test_config.py -v
# Implement config manager
# GREEN: Run test again
export YOUTUBE_API_KEY="test_key"
export GEMINI_API_KEY="test_key"
pytest tests/backend/test_config.py -v
```

---

### Category 2: YouTube API Integration (Tasks 5-7)

#### Task 5: Create YouTube API Client Wrapper
- **ID**: T005
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T004
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create wrapper for YouTube Data API v3 with authentication and error handling.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_youtube_fetcher.py`
- [ ] Test runs and FAILS initially (mocked API)
- [ ] `scripts/youtube_fetcher.py` created
- [ ] Function `get_youtube_api_client(api_key: str) -> Resource` implemented
- [ ] Handles authentication errors gracefully
- [ ] Returns authenticated YouTube client
- [ ] Test uses `unittest.mock` for API responses
- [ ] Test runs and PASSES after implementation

**Files to Create**:
- `scripts/youtube_fetcher.py`
- `tests/backend/test_youtube_fetcher.py`

**Testing Notes**:
```bash
# RED: Write failing test with mocked API
pytest tests/backend/test_youtube_fetcher.py::test_get_youtube_api_client -v
# GREEN: Implement wrapper
pytest tests/backend/test_youtube_fetcher.py::test_get_youtube_api_client -v
```

**Implementation Hint**:
```python
from googleapiclient.discovery import build

def get_youtube_api_client(api_key: str):
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to create YouTube client: {e}")
```

---

#### Task 6: Implement Video Search Function
- **ID**: T006
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T005
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Implement YouTube video search with channel filter, title pattern matching, and date filtering.

**Acceptance Criteria**:
- [ ] Test file updated with search scenarios
- [ ] Tests run and FAIL initially
- [ ] Function `search_channel_videos(client, channel_id, time_slot, date) -> dict` implemented
- [ ] Searches by `channelId` parameter
- [ ] Filters by title pattern using regex
- [ ] Filters by publishedAfter/publishedBefore (24-hour window)
- [ ] Returns `{"video_id": str, "title": str, "published_at": str}`
- [ ] Returns `None` if no results found
- [ ] Handles API errors gracefully
- [ ] Tests cover: found, not found, API error scenarios
- [ ] All tests PASS after implementation

**Files to Modify**:
- `scripts/youtube_fetcher.py` (add function)
- `tests/backend/test_youtube_fetcher.py` (add tests)

**Testing Notes**:
```bash
# RED: Write tests for multiple scenarios
pytest tests/backend/test_youtube_fetcher.py::test_search_channel_videos -v
# GREEN: Implement search function
pytest tests/backend/test_youtube_fetcher.py::test_search_channel_videos -v
```

**Implementation Hint**:
```python
import re
from datetime import datetime, timedelta

def search_channel_videos(client, channel_id, time_slot, date):
    pattern = VIDEO_PATTERN_9PM if time_slot == "9pm" else VIDEO_PATTERN_7AM
    date_obj = datetime.fromisoformat(date)
    
    request = client.search().list(
        part="snippet",
        channelId=channel_id,
        q=f"ETV Telugu News {time_slot}",
        type="video",
        publishedAfter=(date_obj - timedelta(hours=12)).isoformat() + "Z",
        publishedBefore=(date_obj + timedelta(hours=36)).isoformat() + "Z",
        maxResults=10
    )
    
    response = request.execute()
    
    for item in response.get('items', []):
        title = item['snippet']['title']
        if re.match(pattern, title):
            return {
                "video_id": item['id']['videoId'],
                "title": title,
                "published_at": item['snippet']['publishedAt']
            }
    
    return None
```

---

#### Task 7: Implement Video ID Caching
- **ID**: T007
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T001
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create caching system to prevent reprocessing same videos and reduce API calls.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_cache.py`
- [ ] Tests run and FAIL initially
- [ ] `scripts/utils/cache.py` created
- [ ] Function `load_video_cache() -> dict` implemented
- [ ] Function `save_video_cache(cache: dict) -> None` implemented
- [ ] Function `is_video_processed(video_id: str) -> bool` implemented
- [ ] Function `mark_video_processed(video_id: str, date: str) -> None` implemented
- [ ] Cache file: `data/cache/video-ids.json`
- [ ] Handles missing cache file gracefully
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/utils/cache.py`
- `tests/backend/test_cache.py`

**Testing Notes**:
```bash
# RED: Write failing tests
pytest tests/backend/test_cache.py -v
# GREEN: Implement cache functions
pytest tests/backend/test_cache.py -v
# REFACTOR: Check edge cases
pytest tests/backend/test_cache.py -v --cov=scripts/utils/cache
```

**Cache Structure**:
```json
{
  "video123": {
    "date": "2025-12-08",
    "processed_at": "2025-12-08T09:15:00Z",
    "slot": "9pm"
  }
}
```

---

### Category 3: Gemini API Integration (Tasks 8-10)

#### Task 8: Create Gemini API Client Wrapper
- **ID**: T008
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T004
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create wrapper for Google Gemini API with authentication.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_gemini_processor.py`
- [ ] Tests run and FAIL initially
- [ ] `scripts/gemini_processor.py` created
- [ ] Function `create_gemini_client(api_key: str) -> Client` implemented
- [ ] Handles authentication errors
- [ ] Returns authenticated Gemini client
- [ ] Tests use mocked API
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/gemini_processor.py`
- `tests/backend/test_gemini_processor.py`

**Testing Notes**:
```bash
pytest tests/backend/test_gemini_processor.py::test_create_gemini_client -v
```

---

#### Task 9: Implement Video Summarization Function
- **ID**: T009
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T008
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Implement Gemini API call to process YouTube videos and generate Telugu news summaries.

**Acceptance Criteria**:
- [ ] Tests added for summarization scenarios
- [ ] Tests run and FAIL initially
- [ ] Function `get_gemini_summary(video_url: str, api_key: str) -> list[str]` implemented
- [ ] Uses `gemini-2.5-flash` model
- [ ] Uses `file_data` parameter with YouTube URL
- [ ] Sends Telugu prompt for 5-8 news summaries
- [ ] Parses JSON array response
- [ ] Validates response structure
- [ ] Handles API errors (rate limit, invalid response)
- [ ] Tests cover: success, API error, parse error
- [ ] All tests PASS after implementation

**Files to Modify**:
- `scripts/gemini_processor.py` (add function)
- `tests/backend/test_gemini_processor.py` (add tests)

**Testing Notes**:
```bash
pytest tests/backend/test_gemini_processor.py::test_get_gemini_summary -v
```

**Telugu Prompt**:
```
విశ్లేషించి తెలుగులో 5-8 ముఖ్య వార్తా శీర్షికలు సంక్షిప్త వివరణతో తయారు చేయండి.

Format as JSON array:
[
  "వార్త శీర్షిక 1 - సంక్షిప్త వివరణ",
  "వార్త శీర్షిక 2 - సంక్షిప్త వివరణ"
]
```

**Implementation Hint**:
```python
import google.generativeai as genai
from google.ai import types

def get_gemini_summary(video_url: str, api_key: str) -> list[str]:
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = """విశ్లేషించి తెలుగులో 5-8 ముఖ్య వార్తా శీర్షికలు సంక్షిప్త వివరణతో తయారు చేయండి.
    
    Format as JSON array: ["వార్త 1", "వార్త 2"]"""
    
    response = client.generate_content([
        types.Part(file_data=types.FileData(file_uri=video_url)),
        types.Part(text=prompt)
    ])
    
    # Parse JSON response
    import json
    return json.loads(response.text)
```

---

#### Task 10: Implement Retry Logic with Exponential Backoff
- **ID**: T010
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T005, T008
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Add retry decorator using tenacity library for API resilience.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_error_handler.py`
- [ ] Tests run and FAIL initially
- [ ] `scripts/utils/error_handler.py` created
- [ ] Decorator `@retry_with_backoff` implemented
- [ ] Configuration: 3 retries, delays [1s, 2s, 4s]
- [ ] Applied to YouTube search function
- [ ] Applied to Gemini summary function
- [ ] Tests verify retry behavior
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/utils/error_handler.py`
- `tests/backend/test_error_handler.py`

**Files to Modify**:
- `scripts/youtube_fetcher.py` (add decorator)
- `scripts/gemini_processor.py` (add decorator)

**Testing Notes**:
```bash
pytest tests/backend/test_error_handler.py -v
```

**Implementation Hint**:
```python
from tenacity import retry, wait_exponential, stop_after_attempt

def retry_with_backoff(func):
    return retry(
        wait=wait_exponential(multiplier=1, min=1, max=4),
        stop=stop_after_attempt(3),
        reraise=True
    )(func)
```

---

### Category 4: JSON File Management (Tasks 11-13)

#### Task 11: Implement JSON File Operations
- **ID**: T011
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T003
- **Estimated Effort**: 1.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Create functions to load, create, update, and save news JSON files.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_json_generator.py`
- [ ] Tests run and FAIL initially
- [ ] `scripts/json_generator.py` created
- [ ] Function `load_or_create_news_file(date: str) -> dict` implemented
- [ ] Function `save_news_file(date: str, data: dict) -> None` implemented
- [ ] Function `update_news_slot(data: dict, slot: str, summary: list[str], video_data: dict) -> dict` implemented
- [ ] Files saved to `data/archive/YYYY-MM/YYYY-MM-DD.json`
- [ ] Validates data before saving
- [ ] Handles concurrent writes (file locking)
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/json_generator.py`
- `tests/backend/test_json_generator.py`

**Testing Notes**:
```bash
pytest tests/backend/test_json_generator.py -v
```

---

#### Task 12: Implement Index.json Generator
- **ID**: T012
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T011
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create function to scan archive and build index of all available dates.

**Acceptance Criteria**:
- [ ] Tests added to `test_json_generator.py`
- [ ] Tests run and FAIL initially
- [ ] Function `generate_index() -> None` implemented
- [ ] Scans `data/archive/YYYY-MM/*.json` files
- [ ] Builds structure with dates and available slots
- [ ] Sorts by date descending (newest first)
- [ ] Saves to `data/index.json`
- [ ] All tests PASS after implementation

**Files to Modify**:
- `scripts/json_generator.py` (add function)
- `tests/backend/test_json_generator.py` (add tests)

**Testing Notes**:
```bash
pytest tests/backend/test_json_generator.py::test_generate_index -v
```

**Index Structure**:
```json
{
  "dates": [
    {"date": "2025-12-08", "slots": ["9pm", "7am"]},
    {"date": "2025-12-07", "slots": ["9pm"]},
    {"date": "2025-12-06", "slots": ["9pm", "7am"]}
  ],
  "last_updated": "2025-12-08T15:30:00Z"
}
```

---

#### Task 13: Implement Data Cleanup Script
- **ID**: T013
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T011
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create script to delete files older than 30 days.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_cleanup.py`
- [ ] Tests run and FAIL initially
- [ ] `scripts/cleanup.py` created
- [ ] Function `cleanup_old_files(days_to_keep: int = 30) -> None` implemented
- [ ] Deletes files older than threshold
- [ ] Preserves `index.json` and cache files
- [ ] Logs deleted files
- [ ] Has `--dry-run` mode
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/cleanup.py`
- `tests/backend/test_cleanup.py`

**Testing Notes**:
```bash
# Test with temporary files
pytest tests/backend/test_cleanup.py -v
# Manual dry-run test
python scripts/cleanup.py --dry-run
```

---

### Category 5: Main Orchestrator (Tasks 14-16)

#### Task 14: Create Main Processing Script
- **ID**: T014
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T006, T009, T011
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Integrate all components into main orchestration pipeline.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_process_daily_news.py`
- [ ] Tests run and FAIL initially (end-to-end mocking)
- [ ] `scripts/process_daily_news.py` created
- [ ] Function `main(time_slot: str, date: str) -> None` implemented
- [ ] Orchestrates: config → cache → YouTube → Gemini → save → index
- [ ] Handles all error cases gracefully
- [ ] Logs progress at each step
- [ ] All tests PASS after implementation

**Files to Create**:
- `scripts/process_daily_news.py`
- `tests/backend/test_process_daily_news.py`

**Testing Notes**:
```bash
pytest tests/backend/test_process_daily_news.py -v
```

**Orchestration Flow**:
1. Load config and secrets
2. Check if video already processed (cache)
3. Search YouTube for video
4. If found, get Gemini summary
5. Load or create news file
6. Update news slot
7. Save news file
8. Update index.json
9. Mark video as processed in cache

---

#### Task 15: Add Command-Line Interface
- **ID**: T015
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: T014
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Add argparse CLI for script execution from GitHub Actions.

**Acceptance Criteria**:
- [ ] Tests added for CLI parsing
- [ ] Tests run and FAIL initially
- [ ] Uses `argparse` module
- [ ] Argument `--slot` (required): "9pm" or "7am"
- [ ] Argument `--date` (optional): YYYY-MM-DD
- [ ] Argument `--force` (flag): Bypass cache
- [ ] Argument `--dry-run` (flag): Don't save files
- [ ] All tests PASS after implementation

**Files to Modify**:
- `scripts/process_daily_news.py` (add CLI)
- `tests/backend/test_process_daily_news.py` (add tests)

**Testing Notes**:
```bash
python scripts/process_daily_news.py --slot 9pm --date 2025-12-08 --dry-run
```

---

#### Task 16: Add Logging and Error Reporting
- **ID**: T016
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T014
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Add structured logging for GitHub Actions monitoring.

**Acceptance Criteria**:
- [ ] Tests added for log output
- [ ] Tests run and FAIL initially
- [ ] Uses Python `logging` module
- [ ] Log levels: INFO, WARNING, ERROR
- [ ] JSON format for GitHub Actions parsing
- [ ] Logs to stdout
- [ ] All tests PASS after implementation

**Files to Modify**:
- `scripts/process_daily_news.py` (add logging)
- `tests/backend/test_process_daily_news.py` (add tests)

**Testing Notes**:
```bash
python scripts/process_daily_news.py --slot 9pm 2>&1 | jq .
```

---

### Category 6: GitHub Actions Workflows (Tasks 17-20)

#### Task 17: Create 9 PM News Workflow
- **ID**: T017
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T014, T015
- **Estimated Effort**: 1 session
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Create GitHub Actions workflow for daily 9 PM news processing at 9 AM IST.

**Acceptance Criteria**:
- [ ] File created: `.github/workflows/process-9pm-news.yml`
- [ ] Trigger: `cron: '30 3 * * *'` (9:00 AM IST = 3:30 UTC)
- [ ] Step: Checkout repository
- [ ] Step: Setup Python 3.11
- [ ] Step: Install dependencies from `scripts/requirements.txt`
- [ ] Step: Run `python scripts/process_daily_news.py --slot 9pm`
- [ ] Step: Commit changes if files modified
- [ ] Step: Push to dev branch
- [ ] Uses secrets: `YOUTUBE_API_KEY`, `GEMINI_API_KEY`
- [ ] Manual trigger works via GitHub UI

**Files to Create**:
- `.github/workflows/process-9pm-news.yml`

**Testing Notes**:
```bash
# Test locally with act (GitHub Actions runner)
act schedule -j process-9pm-news --secret-file .env

# Or trigger manually via GitHub UI
# Go to Actions tab → Select workflow → Run workflow
```

**Workflow Template**:
```yaml
name: Process 9 PM News

on:
  schedule:
    - cron: '30 3 * * *'  # 9:00 AM IST
  workflow_dispatch:
    inputs:
      date:
        description: 'Date to process (YYYY-MM-DD)'
        required: false
      force:
        description: 'Force reprocessing'
        type: boolean
        default: false

jobs:
  process-news:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r scripts/requirements.txt
      - name: Process 9 PM news
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python scripts/process_daily_news.py --slot 9pm
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: Update 9 PM news for $(date +%Y-%m-%d)"
          git push
```

---

#### Task 18: Create 7 AM News Workflow
- **ID**: T018
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T014, T015
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Create GitHub Actions workflow for daily 7 AM news processing at 11 PM IST.

**Acceptance Criteria**:
- [ ] File created: `.github/workflows/process-7am-news.yml`
- [ ] Trigger: `cron: '30 17 * * *'` (11:00 PM IST = 17:30 UTC)
- [ ] Same steps as 9 PM workflow with `--slot 7am`
- [ ] Uses same secrets
- [ ] Manual trigger works via GitHub UI

**Files to Create**:
- `.github/workflows/process-7am-news.yml`

**Testing Notes**:
```bash
act schedule -j process-7am-news --secret-file .env
```

---

#### Task 19: Create Weekly Cleanup Workflow
- **ID**: T019
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T013
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Create weekly cleanup workflow to remove old data files.

**Acceptance Criteria**:
- [ ] File created: `.github/workflows/cleanup-old-data.yml`
- [ ] Trigger: `cron: '0 0 * * 0'` (Sunday midnight UTC)
- [ ] Runs cleanup script
- [ ] Regenerates index.json
- [ ] Commits and pushes changes
- [ ] Manual trigger works

**Files to Create**:
- `.github/workflows/cleanup-old-data.yml`

**Testing Notes**:
```bash
act schedule -j cleanup-old-data
```

---

#### Task 20: Add Manual Workflow Dispatch
- **ID**: T020
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T017, T018, T019
- **Estimated Effort**: 0.25 sessions
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Add workflow_dispatch inputs to all workflows for manual testing.

**Acceptance Criteria**:
- [ ] All workflows have `workflow_dispatch` trigger
- [ ] Input: `date` (optional) - Process specific date
- [ ] Input: `force` (boolean) - Force reprocessing
- [ ] Manual triggers work from GitHub UI

**Files to Modify**:
- `.github/workflows/process-9pm-news.yml`
- `.github/workflows/process-7am-news.yml`
- `.github/workflows/cleanup-old-data.yml`

**Testing Notes**:
Go to GitHub Actions tab → Select workflow → Click "Run workflow"

---

### Category 7: Frontend HTML (Tasks 21-22)

#### Task 21: Create index.html with Semantic Structure
- **ID**: T021
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: None
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create HTML foundation with semantic structure and Telugu content.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_html_structure.spec.ts`
- [ ] Test runs and FAILS initially
- [ ] `index.html` created
- [ ] `<header>` with site title in Telugu
- [ ] `<main>` with `<aside>` (sidebar) and `<article>` (content)
- [ ] `<footer>` with last updated timestamp
- [ ] Meta tag: `charset="UTF-8"`
- [ ] Meta tag: `viewport` for mobile
- [ ] Link to Google Fonts (Noto Sans Telugu)
- [ ] Test runs and PASSES after implementation

**Files to Create**:
- `index.html`
- `tests/frontend/test_html_structure.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_html_structure.spec.ts
```

---

#### Task 22: Add Accessibility Attributes
- **ID**: T022
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T021
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Add ARIA labels and accessibility features.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_accessibility.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `lang="te"` on HTML tag
- [ ] ARIA labels in Telugu
- [ ] Skip-to-content link
- [ ] Keyboard navigation works
- [ ] All tests PASS after implementation

**Files to Modify**:
- `index.html`

**Files to Create**:
- `tests/frontend/test_accessibility.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_accessibility.spec.ts
```

---

### Category 8: Frontend CSS (Tasks 23-27)

#### Task 23: Create Base CSS Styles
- **ID**: T023
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: T021
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Create base CSS with custom properties and typography.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_styles.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `css/main.css` created
- [ ] CSS custom properties defined
- [ ] Reset default styles
- [ ] Noto Sans Telugu typography
- [ ] All tests PASS after implementation

**Files to Create**:
- `css/main.css`
- `tests/frontend/test_styles.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_styles.spec.ts
```

---

#### Task 24: Implement Mobile-First Layout
- **ID**: T024
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T023
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Implement responsive layout with CSS Grid/Flexbox.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_responsive_layout.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `css/layout.css` created
- [ ] Mobile (360px): Single column
- [ ] Tablet (768px): Sidebar slides in
- [ ] Desktop (1024px): Sidebar fixed left (25%)
- [ ] All tests PASS after implementation

**Files to Create**:
- `css/layout.css`
- `tests/frontend/test_responsive_layout.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_responsive_layout.spec.ts
```

---

#### Task 25: Style Sidebar Component
- **ID**: T025
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T024
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Style sidebar date list with hover effects and selected state.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_sidebar.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `css/sidebar.css` created
- [ ] Date list item styles
- [ ] Hover effects
- [ ] Selected state
- [ ] Checkmark icons
- [ ] All tests PASS after implementation

**Files to Create**:
- `css/sidebar.css`
- `tests/frontend/test_sidebar.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_sidebar.spec.ts
```

---

#### Task 26: Style News Content Area
- **ID**: T026
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T024
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Style news display cards and content.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_news_display.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `css/news-display.css` created
- [ ] News card styling
- [ ] Summary bullet points
- [ ] YouTube button styling
- [ ] All tests PASS after implementation

**Files to Create**:
- `css/news-display.css`
- `tests/frontend/test_news_display.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_news_display.spec.ts
```

---

#### Task 27: Add Dark Mode Support
- **ID**: T027
- **Priority**: P3 (Low)
- **Complexity**: Low
- **Depends On**: T023, T024, T025, T026
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Add dark mode using prefers-color-scheme.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_dark_mode.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] Dark mode variables in `css/main.css`
- [ ] Uses `prefers-color-scheme` media query
- [ ] Colors inverted for dark mode
- [ ] All tests PASS after implementation

**Files to Modify**:
- `css/main.css`

**Files to Create**:
- `tests/frontend/test_dark_mode.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_dark_mode.spec.ts --color-scheme=dark
```

---

### Category 9: Frontend JavaScript Data Loading (Tasks 28-29)

#### Task 28: Create Data Loader Utility
- **ID**: T028
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T021
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Create data loading functions with error handling.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_data_loader.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `js/utils/data-loader.js` created
- [ ] Function `async fetchIndex() -> object`
- [ ] Function `async fetchNewsForDate(date) -> object`
- [ ] Cache busting with timestamp
- [ ] Graceful error handling
- [ ] All tests PASS after implementation

**Files to Create**:
- `js/utils/data-loader.js`
- `tests/frontend/test_data_loader.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_data_loader.spec.ts
```

---

#### Task 29: Implement localStorage Caching
- **ID**: T029
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T028
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Add localStorage caching for performance.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_caching.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] Cache index.json in localStorage
- [ ] Cache recent news files (7 days)
- [ ] 24-hour TTL
- [ ] Prefer cache over network
- [ ] All tests PASS after implementation

**Files to Modify**:
- `js/utils/data-loader.js`

**Files to Create**:
- `tests/frontend/test_caching.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_caching.spec.ts
```

---

### Category 10: Frontend UI Components (Tasks 30-35)

#### Task 30: Create Sidebar Date List Component
- **ID**: T030
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T028
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Create interactive sidebar with date navigation.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_sidebar_component.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `js/components/sidebar.js` created
- [ ] Function `generateDateList(dates) -> HTMLElement`
- [ ] Render list items
- [ ] Click handlers
- [ ] Highlight today
- [ ] Show slot checkmarks
- [ ] All tests PASS after implementation

**Files to Create**:
- `js/components/sidebar.js`
- `tests/frontend/test_sidebar_component.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_sidebar_component.spec.ts
```

---

#### Task 31: Create News Display Component
- **ID**: T031
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T021
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Create news rendering component with Telugu messages.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_news_display_component.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `js/components/news-display.js` created
- [ ] Function `renderNewsSection(sectionId, newsData, timeSlot) -> void`
- [ ] Display video title
- [ ] Render 5-8 bullet points
- [ ] YouTube link button
- [ ] Handle missing data
- [ ] All tests PASS after implementation

**Files to Create**:
- `js/components/news-display.js`
- `tests/frontend/test_news_display_component.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_news_display_component.spec.ts
```

---

#### Task 32: Create Date Formatter Utility
- **ID**: T032
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: None
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Format dates in Telugu.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_date_formatter.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `js/utils/date-formatter.js` created
- [ ] Function `formatDateDisplay(date) -> string`
- [ ] Converts "2025-12-08" to "8 డిసెంబర్ 2025"
- [ ] Telugu month names
- [ ] All tests PASS after implementation

**Files to Create**:
- `js/utils/date-formatter.js`
- `tests/frontend/test_date_formatter.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_date_formatter.spec.ts
```

---

#### Task 33: Implement Page Initialization
- **ID**: T033
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T028, T030, T031
- **Estimated Effort**: 1.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Initialize page with data loading and event setup.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_app_initialization.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `js/app.js` created
- [ ] Function `initializePage() -> void`
- [ ] Load index.json
- [ ] Generate sidebar
- [ ] Load today's news
- [ ] Setup event listeners
- [ ] All tests PASS after implementation

**Files to Create**:
- `js/app.js`
- `tests/frontend/test_app_initialization.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_app_initialization.spec.ts
```

---

#### Task 34: Implement Date Navigation
- **ID**: T034
- **Priority**: P1 (Blocking)
- **Complexity**: Medium
- **Depends On**: T033
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Handle date selection and content updates.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_date_navigation.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] Function `handleDateClick(date) -> void` in `js/app.js`
- [ ] Clear previous content
- [ ] Show loading indicator
- [ ] Fetch and render news
- [ ] Update URL (pushState)
- [ ] All tests PASS after implementation

**Files to Modify**:
- `js/app.js`

**Files to Create**:
- `tests/frontend/test_date_navigation.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_date_navigation.spec.ts
```

---

#### Task 35: Add Loading and Error States
- **ID**: T035
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T031
- **Estimated Effort**: 1 session
- **TDD Required**: ✅ YES

**Description**:
Add loading spinners and Telugu error messages.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_loading_states.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] Show spinner during fetch
- [ ] Telugu error messages:
  - "సమాచారం లేదు"
  - "వార్తలు ప్రాసెస్ అవుతున్నాయి..."
  - "ఆ రోజు వార్తలు లేవు"
  - "వార్తలు ప్రాసెస్ చేయలేకపోయాం"
- [ ] All tests PASS after implementation

**Files to Modify**:
- `js/app.js`
- `js/components/news-display.js`

**Files to Create**:
- `tests/frontend/test_loading_states.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_loading_states.spec.ts
```

---

### Category 11: Integration Testing (Tasks 36-38)

#### Task 36: Create End-to-End Backend Test
- **ID**: T036
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T014
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Test complete backend pipeline with mocked APIs.

**Acceptance Criteria**:
- [ ] Test file created: `tests/backend/test_e2e_backend.py`
- [ ] Tests run and FAIL initially
- [ ] Mock YouTube API
- [ ] Mock Gemini API
- [ ] Run full pipeline
- [ ] Verify JSON files created
- [ ] Verify index.json updated
- [ ] Verify cache updated
- [ ] All tests PASS after implementation

**Files to Create**:
- `tests/backend/test_e2e_backend.py`

**Testing Notes**:
```bash
pytest tests/backend/test_e2e_backend.py -v
```

---

#### Task 37: Create End-to-End Frontend Test
- **ID**: T037
- **Priority**: P1 (Blocking)
- **Complexity**: High
- **Depends On**: T033, T034
- **Estimated Effort**: 2 sessions
- **TDD Required**: ✅ YES

**Description**:
Test complete user journey from page load to navigation.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_e2e_frontend.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] Test user journey:
  1. Load page
  2. Verify today's news
  3. Click different date
  4. Verify news updates
  5. Test responsive breakpoints
  6. Test dark mode
- [ ] All tests PASS after implementation

**Files to Create**:
- `tests/frontend/test_e2e_frontend.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_e2e_frontend.spec.ts
```

---

#### Task 38: Test GitHub Actions Workflows Locally
- **ID**: T038
- **Priority**: P2 (High)
- **Complexity**: Medium
- **Depends On**: T017, T018, T019
- **Estimated Effort**: 1 session
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Use `act` to test workflows locally before deployment.

**Acceptance Criteria**:
- [ ] Install `act` (GitHub Actions local runner)
- [ ] Test 9 PM workflow locally
- [ ] Test 7 AM workflow locally
- [ ] Test cleanup workflow locally
- [ ] Verify commits work
- [ ] Check error handling

**Testing Notes**:
```bash
# Install act
# On macOS: brew install act
# On Windows: choco install act-cli

# Test workflows
act schedule -j process-9pm-news --secret-file .env
act schedule -j process-7am-news --secret-file .env
act schedule -j cleanup-old-data
```

---

### Category 12: Documentation & Deployment (Tasks 39-42)

#### Task 39: Write README.md
- **ID**: T039
- **Priority**: P2 (High)
- **Complexity**: Low
- **Depends On**: None
- **Estimated Effort**: 1 session
- **TDD Required**: ❌ NO (Manual review)

**Description**:
Create comprehensive project documentation.

**Acceptance Criteria**:
- [ ] `README.md` created
- [ ] Project overview
- [ ] Architecture diagram
- [ ] Setup instructions
- [ ] API key configuration
- [ ] Deployment guide
- [ ] Contributing guidelines

**Files to Create**:
- `README.md`

**Testing Notes**:
Manual review for completeness and clarity.

---

#### Task 40: Configure GitHub Secrets
- **ID**: T040
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: None
- **Estimated Effort**: 0.25 sessions
- **TDD Required**: ❌ NO (Manual setup)

**Description**:
Add API keys to GitHub repository secrets.

**Acceptance Criteria**:
- [ ] `YOUTUBE_API_KEY` added to repository secrets
- [ ] `GEMINI_API_KEY` added to repository secrets
- [ ] Secret rotation process documented
- [ ] Workflow can access secrets (test run)

**Testing Notes**:
Trigger manual workflow and verify secrets are accessible.

---

#### Task 41: Configure GitHub Pages
- **ID**: T041
- **Priority**: P1 (Blocking)
- **Complexity**: Low
- **Depends On**: T021, T033
- **Estimated Effort**: 0.25 sessions
- **TDD Required**: ❌ NO (Manual setup)

**Description**:
Enable GitHub Pages for static site hosting.

**Acceptance Criteria**:
- [ ] GitHub Pages enabled on dev branch
- [ ] Source set to root directory
- [ ] Custom domain configured (if applicable)
- [ ] Site accessible via GitHub Pages URL
- [ ] Deployment works automatically

**Testing Notes**:
Visit `https://<username>.github.io/<repo>/` and verify site loads.

---

#### Task 42: Create Monitoring Dashboard
- **ID**: T042
- **Priority**: P3 (Low)
- **Complexity**: Low
- **Depends On**: T041
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ❌ NO (Manual setup)

**Description**:
Document monitoring strategy and setup alerts.

**Acceptance Criteria**:
- [ ] Document how to monitor:
  - Workflow success rate
  - API quota usage
  - Page performance (Lighthouse)
- [ ] Setup email alerts for workflow failures
- [ ] Create monitoring checklist

**Testing Notes**:
Manual verification of alert setup.

---

### Category 13: Performance Optimization (Tasks 43-45)

#### Task 43: Optimize Frontend Performance
- **ID**: T043
- **Priority**: P3 (Low)
- **Complexity**: Low
- **Depends On**: T033
- **Estimated Effort**: 1 session
- **TDD Required**: ❌ NO (Performance testing)

**Description**:
Optimize frontend for best performance scores.

**Acceptance Criteria**:
- [ ] Minify CSS and JavaScript
- [ ] Add preconnect to Google Fonts
- [ ] Use font-display: swap
- [ ] Implement lazy loading (if thumbnails)
- [ ] Lighthouse score > 90

**Testing Notes**:
```bash
npx lighthouse https://<username>.github.io/<repo>/ --view
```

---

#### Task 44: Add Service Worker for Offline Support
- **ID**: T044
- **Priority**: P3 (Low)
- **Complexity**: Medium
- **Depends On**: T033
- **Estimated Effort**: 1.5 sessions
- **TDD Required**: ✅ YES

**Description**:
Add service worker for offline functionality.

**Acceptance Criteria**:
- [ ] Test file created: `tests/frontend/test_service_worker.spec.ts`
- [ ] Tests run and FAIL initially
- [ ] `sw.js` created
- [ ] Cache static assets
- [ ] Cache recent JSON files
- [ ] Show offline indicator
- [ ] All tests PASS after implementation

**Files to Create**:
- `sw.js`
- `tests/frontend/test_service_worker.spec.ts`

**Testing Notes**:
```bash
npx playwright test tests/frontend/test_service_worker.spec.ts
```

---

#### Task 45: Add Analytics (Privacy-Respecting)
- **ID**: T045
- **Priority**: P3 (Low)
- **Complexity**: Low
- **Depends On**: T041
- **Estimated Effort**: 0.5 sessions
- **TDD Required**: ❌ NO (Manual testing)

**Description**:
Add simple privacy-respecting analytics.

**Acceptance Criteria**:
- [ ] Track page views per date
- [ ] Track most viewed news days
- [ ] No cookies used
- [ ] Privacy-respecting solution
- [ ] Manual verification works

**Testing Notes**:
Manual verification of analytics data.

---

## Dependency Graph

```
Foundation
T001 ─┬─> T002 ─┬─> T003 ─> T011 ─┬─> T012
      │         └─> T004 ─┬─> T005 ─> T006 ─┐
      │                   └─> T008 ─> T009 ─┤
      └─> T007                               │
                                             ├─> T010 ─> T014 ─┬─> T015
                                             │                  └─> T016
                                             └─> T013                 │
                                                                      ├─> T017
                                                                      ├─> T018
                                                                      └─> T019 ─> T020

Frontend HTML/CSS
T021 ─┬─> T022
      └─> T023 ─> T024 ─┬─> T025
                        └─> T026
                        └─> T027

Frontend JS
T021 ─> T028 ─┬─> T029
              └─> T030 ─┐
T021 ─────────> T031 ──┼─> T033 ─> T034 ─> T035
                       │
T032 ──────────────────┘

Integration & Deploy
T014 ────> T036
T033, T034 ─> T037
T017, T018, T019 ─> T038
T021, T033 ─> T041 ─> T042
           └─> T043
           └─> T044
           └─> T045
```

---

## Suggested Implementation Order

**Phase 1: Backend Foundation (6-8 sessions)**
1. T001 - Directory structure
2. T002 - Python environment
3. T003 - JSON validators (TDD)
4. T004 - Configuration (TDD)
5. T007 - Video caching (TDD)
6. T005 - YouTube client (TDD)
7. T006 - YouTube search (TDD)
8. T008 - Gemini client (TDD)
9. T009 - Gemini summarization (TDD)
10. T010 - Retry logic (TDD)

**Phase 2: Data Management & Orchestration (3-4 sessions)**
11. T011 - JSON operations (TDD)
12. T012 - Index generator (TDD)
13. T013 - Cleanup script (TDD)
14. T014 - Main orchestrator (TDD)
15. T015 - CLI interface (TDD)
16. T016 - Logging (TDD)

**Phase 3: Automation (1-2 sessions)**
17. T017 - 9 PM workflow
18. T018 - 7 AM workflow
19. T019 - Cleanup workflow
20. T020 - Manual dispatch

**Phase 4: Frontend Foundation (2-3 sessions)**
21. T021 - HTML structure (TDD)
22. T022 - Accessibility (TDD)
23. T023 - Base CSS (TDD)
24. T024 - Responsive layout (TDD)
25. T025 - Sidebar CSS (TDD)
26. T026 - News display CSS (TDD)
27. T027 - Dark mode (TDD)

**Phase 5: Frontend JavaScript (4-5 sessions)**
28. T028 - Data loader (TDD)
29. T029 - Caching (TDD)
32. T032 - Date formatter (TDD)
30. T030 - Sidebar component (TDD)
31. T031 - News display component (TDD)
33. T033 - Page initialization (TDD)
34. T034 - Date navigation (TDD)
35. T035 - Loading states (TDD)

**Phase 6: Integration & Deploy (2-3 sessions)**
36. T036 - Backend E2E test (TDD)
37. T037 - Frontend E2E test (TDD)
38. T038 - Local workflow testing
40. T040 - GitHub Secrets
41. T041 - GitHub Pages
39. T039 - README

**Phase 7: Optimization (Optional, 1-2 sessions)**
42. T042 - Monitoring
43. T043 - Performance
44. T044 - Service worker (TDD)
45. T045 - Analytics

---

## TDD Task Summary

**Total TDD Tasks**: 40 out of 45 tasks
**Non-TDD Tasks**: 5 (workflows, docs, config)

**Backend TDD**: 16 tasks (T003-T016, T036)
**Frontend TDD**: 24 tasks (T021-T035, T037, T044)

---

## Next Steps

1. **Run `/harness.generate`** to convert tasks to `memory/feature_list.json`
2. **Use `@Coder`** to implement tasks one at a time
3. **Follow TDD strictly**: RED → GREEN → REFACTOR
4. **Update `memory/claude-progress.md`** after each session
5. **Commit frequently** after each passing task

---

## Notes

- **One task at a time** - Complete fully before moving to next
- **TDD is mandatory** - Test must fail before implementation
- **Verify end-to-end** - Browser checks for frontend, pytest for backend
- **Update feature_list.json** - Only change `passes` field
- **Document blockers** - Update progress notes if stuck
- **Leave clean state** - Commit all passing work before session end

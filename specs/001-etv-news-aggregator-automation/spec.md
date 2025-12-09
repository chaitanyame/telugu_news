# ETV Telugu News Aggregator - Fully Automated Specification

## Overview

Build a **fully automated** ETV Telugu News aggregation website that operates as a two-tier system:

1. **Backend (GitHub Actions)**: Automatically discovers, processes, and caches daily 9 PM and 7 AM news videos from ETV Telugu News YouTube channel using Gemini API's video intelligence
2. **Frontend (GitHub Pages)**: Static website that displays pre-processed news summaries with instant, zero-latency navigation

**Key Innovation**: The UI never calls APIs or waits for processing. All heavy computation happens in scheduled background automation, making the user experience instant and the system infinitely scalable.

## User Stories

### End User Stories
- As a Telugu news reader, I want to see today's 9 PM and 7 AM news summaries instantly without waiting, so that I can quickly stay informed
- As a mobile user, I want a fast, responsive website that works on slow networks, so that I can read news on my phone anywhere in India
- As a history browser, I want to view news from the past 30 days, so that I can catch up on stories I missed
- As a visual learner, I want to click through to the original YouTube video, so that I can watch the full broadcast if interested

### Developer/Maintainer Stories
- As a project maintainer, I want the system to run automatically without my intervention, so that I don't need to manually trigger processing daily
- As a system admin, I want to be notified only when automation fails, so that I can fix issues without constant monitoring
- As a cost-conscious developer, I want the entire system to run on GitHub's free tier, so that there are zero hosting costs

## Requirements

### Functional Requirements

#### Backend Automation (GitHub Actions)
1. **Scheduled Execution**
   - FR-001: System MUST run automatically at 10:00 PM IST daily (process 9 PM video)
   - FR-002: System MUST run automatically at 8:00 AM IST daily (process 7 AM video)
   - FR-003: System MUST support manual trigger via `workflow_dispatch` for testing/recovery

2. **Video Discovery (YouTube Data API)**
   - FR-004: System MUST search ONLY ETV Telugu News YouTube channel (ID: `UCJi8M0hRKjz8SLPvJKEVTOg`)
   - FR-005: System MUST filter videos by exact title pattern:
     - `9 PM | ETV Telugu News | {Date}` (e.g., "9 PM | ETV Telugu News | 8th December 2025")
     - `7 AM | ETV Telugu News | {Date}` (e.g., "7 AM | ETV Telugu News | 8th December 2025")
   - FR-006: System MUST validate channel ID matches ETV official before processing
   - FR-007: System MUST handle "no videos found" gracefully (log warning, no error)
   - FR-008: System MUST extract: video_id, title, thumbnail URL, published_at timestamp

3. **Video Processing (Gemini API)**
   - FR-009: System MUST send video to Gemini API using `file_data` parameter for video analysis
   - FR-010: System MUST use prompt: "Analyze this ETV Telugu News broadcast and extract 5-8 key news headlines with brief summaries in Telugu. Format as bullet points."
   - FR-011: System MUST parse Gemini response into structured JSON format
   - FR-012: System MUST retry failed API calls 3 times with exponential backoff (1s, 2s, 4s)
   - FR-013: System MUST handle Gemini API rate limits gracefully

4. **Data Storage**
   - FR-014: System MUST generate JSON file: `data/news-YYYY-MM-DD.json` for each day
   - FR-015: System MUST store both 9 PM and 7 AM news in single daily file
   - FR-016: System MUST include metadata: video_id, video_url, title, summary array, processed_at timestamp, status
   - FR-017: System MUST commit generated JSON to repository with descriptive commit message
   - FR-018: System MUST maintain 30 days of historical data (auto-delete older files)

5. **Error Handling & Notifications**
   - FR-019: System MUST log all errors to GitHub Actions console
   - FR-020: System MUST send email notification on workflow failure (optional, configurable)
   - FR-021: System MUST continue processing if one video fails (don't fail entire workflow)
   - FR-022: System MUST mark failed video with `"status": "error"` in JSON

#### Frontend UI (GitHub Pages)
6. **Page Layout**
   - FR-023: UI MUST display header: "ETV తెలుగు న్యూస్ సారాంశం" (ETV Telugu News Summary)
   - FR-024: UI MUST show left sidebar (30% width) with date/time navigation
   - FR-025: UI MUST show main content area (70% width) with news display
   - FR-026: UI MUST be responsive: collapse sidebar to hamburger menu on mobile (< 768px)
   - FR-027: UI MUST use mobile-first design (360px base viewport)

7. **Date/Time Sidebar Navigation**
   - FR-028: Sidebar MUST show list of available news dates (latest first)
   - FR-029: Sidebar MUST display Telugu date format: "8 డిసెంబర్ 2025"
   - FR-030: Sidebar MUST show time slots available (✓ 9 PM, ✓ 7 AM) for each date
   - FR-031: Sidebar MUST highlight today's date with visual indicator
   - FR-032: Sidebar MUST be scrollable if dates exceed viewport height
   - FR-033: Sidebar MUST update selected date highlighting on click
   - FR-034: Sidebar MUST show last 30 days of news

8. **News Display Area**
   - FR-035: Main area MUST display date header: "8 డిసెంబర్ 2025 వార్తలు"
   - FR-036: Main area MUST show two sections: "రాత్రి 9 గంటల వార్తలు" (9 PM News) and "ఉదయం 7 గంటల వార్తలు" (7 AM News)
   - FR-037: Each section MUST display:
     - Original video title
     - 5-8 bullet points in Telugu (news summary)
     - "YouTube లో చూడండి" (Watch on YouTube) link
     - Processed timestamp (Telugu format)
   - FR-038: UI MUST show "సమాచారం లేదు" (No news available) if data missing
   - FR-039: YouTube links MUST open in new tab (`target="_blank"`)

9. **Data Loading (Frontend)**
   - FR-040: UI MUST load news data by fetching `data/news-YYYY-MM-DD.json` files
   - FR-041: UI MUST load data on page load (fetch today's date by default)
   - FR-042: UI MUST load data on sidebar date click (< 100ms response time)
   - FR-043: UI MUST cache loaded JSON in browser memory (avoid redundant fetches)
   - FR-044: UI MUST NOT call YouTube API or Gemini API
   - FR-045: UI MUST work offline after first load (optional enhancement)

### Non-Functional Requirements

#### Performance
- NFR-001: **First Contentful Paint (FCP)**: < 1.5 seconds on 3G network
- NFR-002: **Date Click Response**: < 100ms from click to news display
- NFR-003: **Total Page Weight**: < 150 KB (HTML + CSS + JS + initial JSON)
- NFR-004: **Backend Processing Time**: < 5 minutes per video (YouTube + Gemini)
- NFR-005: **GitHub Actions Execution**: < 15 minutes total per workflow run

#### Security
- NFR-006: API keys MUST be stored as GitHub Secrets (never in code)
- NFR-007: YouTube API key MUST be `YOUTUBE_API_KEY` secret
- NFR-008: Gemini API key MUST be `GEMINI_API_KEY` secret
- NFR-009: Frontend MUST NOT expose any API keys
- NFR-010: Repository MUST use `.gitignore` to prevent accidental key commits

#### Accessibility
- NFR-011: All UI text MUST be in Telugu with proper UTF-8 encoding
- NFR-012: All interactive elements MUST have minimum 44px touch target (mobile)
- NFR-013: UI MUST support keyboard navigation (Tab, Enter, Arrow keys)
- NFR-014: UI MUST have proper ARIA labels for screen readers
- NFR-015: Color contrast MUST meet WCAG AA standards (4.5:1 for text)

#### Reliability
- NFR-016: Backend MUST retry failed API calls 3 times before marking as error
- NFR-017: System MUST handle missing videos gracefully (no crash)
- NFR-018: Frontend MUST show last available data if current day processing failed
- NFR-019: System uptime target: 99.5% (accounting for GitHub Actions availability)

#### Scalability
- NFR-020: System MUST handle 30 days × 2 videos = 60 JSON files without performance degradation
- NFR-021: Frontend MUST load JSON files on-demand (not all 60 at once)
- NFR-022: System MUST auto-delete files older than 30 days to prevent repository bloat

#### Maintainability
- NFR-023: All code MUST follow project constitution coding standards
- NFR-024: Python scripts MUST have unit tests (pytest)
- NFR-025: Frontend MUST have UI tests (Playwright)
- NFR-026: All functions MUST have descriptive docstrings/comments

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  USER (Browser)                                                     │
│  • Opens https://{username}.github.io/telugu_news                   │
│  • Sees instant UI (no waiting)                                     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓ (HTTP GET)
┌─────────────────────────────────────────────────────────────────────┐
│  GITHUB PAGES (Static Hosting)                                      │
│  • Serves: index.html, CSS, JS files                                │
│  • Serves: data/news-*.json files (pre-generated)                   │
└─────────────────────────────────────────────────────────────────────┘
                              ↑ (Git Push)
┌─────────────────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS (Scheduled Automation)                              │
│  • Trigger: cron schedule (10 PM IST, 8 AM IST)                     │
│  • Runs: Python scripts in Ubuntu runner                            │
│  • Commits: Generated JSON files                                    │
└─────────────────────────────────────────────────────────────────────┘
       ↓ (API Call)              ↓ (API Call)
┌─────────────────┐      ┌─────────────────┐
│  YOUTUBE API    │      │  GEMINI API     │
│  • Video Search │      │  • Video Analysis│
│  • Metadata     │      │  • Telugu Summary│
└─────────────────┘      └─────────────────┘
```

### Data Model

#### Daily News JSON Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["date", "generated_at", "news"],
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Date in YYYY-MM-DD format"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of when this file was generated"
    },
    "news": {
      "type": "object",
      "properties": {
        "9pm": {
          "$ref": "#/definitions/newsItem"
        },
        "7am": {
          "$ref": "#/definitions/newsItem"
        }
      }
    }
  },
  "definitions": {
    "newsItem": {
      "type": "object",
      "required": ["video_id", "video_url", "title", "summary", "processed_at", "status"],
      "properties": {
        "video_id": {
          "type": "string",
          "description": "YouTube video ID (11 characters)"
        },
        "video_url": {
          "type": "string",
          "format": "uri",
          "description": "Full YouTube video URL"
        },
        "title": {
          "type": "string",
          "description": "Original video title from YouTube"
        },
        "thumbnail_url": {
          "type": "string",
          "format": "uri",
          "description": "YouTube thumbnail URL (maxresdefault)"
        },
        "summary": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 5,
          "maxItems": 8,
          "description": "Array of Telugu news bullet points"
        },
        "processed_at": {
          "type": "string",
          "format": "date-time",
          "description": "When this video was processed"
        },
        "status": {
          "type": "string",
          "enum": ["success", "error", "not_found"],
          "description": "Processing status"
        },
        "error_message": {
          "type": "string",
          "description": "Error details if status is 'error'"
        }
      }
    }
  }
}
```

#### Example JSON File
```json
{
  "date": "2025-12-08",
  "generated_at": "2025-12-08T14:30:00Z",
  "news": {
    "9pm": {
      "video_id": "dQw4w9WgXcQ",
      "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "title": "9 PM | ETV Telugu News | 8th December 2025",
      "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "summary": [
        "తెలంగాణలో కొత్త విధానం ప్రకటన",
        "ఆంధ్రప్రదేశ్‌లో వరదల పరిస్థితి",
        "కేంద్ర బడ్జెట్ ముసాయిదా చర్చలు",
        "క్రీడలలో భారత విజయాలు",
        "అంతర్జాతీయ వార్తలు - ముఖ్యాంశాలు"
      ],
      "processed_at": "2025-12-08T14:25:00Z",
      "status": "success"
    },
    "7am": {
      "video_id": "abc123xyz",
      "video_url": "https://www.youtube.com/watch?v=abc123xyz",
      "title": "7 AM | ETV Telugu News | 8th December 2025",
      "thumbnail_url": "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg",
      "summary": [
        "ఉదయం ముఖ్య వార్తలు",
        "రాజకీయ పరిణామాలు",
        "వాతావరణ సమాచారం",
        "స్థానిక వార్తలు",
        "ఆర్థిక సమీక్ష"
      ],
      "processed_at": "2025-12-08T02:25:00Z",
      "status": "success"
    }
  }
}
```

### API/Interface

#### GitHub Actions Workflow Interface
```yaml
# .github/workflows/process-news.yml
name: Process ETV Telugu News
on:
  schedule:
    - cron: '30 16 * * *'  # 10:00 PM IST
    - cron: '30 2 * * *'   # 8:00 AM IST
  workflow_dispatch:
    inputs:
      date:
        description: 'Process specific date (YYYY-MM-DD)'
        required: false
        default: 'today'
      slot:
        description: 'Time slot (9pm, 7am, or both)'
        required: false
        default: 'both'
```

#### Python Script Interface
```python
# scripts/process_daily_news.py
def main(target_date: str, slot: str = 'both') -> None:
    """
    Main orchestrator for daily news processing.
    
    Args:
        target_date: Date to process (YYYY-MM-DD or 'today')
        slot: Which time slot to process ('9pm', '7am', or 'both')
    
    Returns:
        None (writes JSON files to data/ directory)
    
    Raises:
        YouTubeAPIError: If video discovery fails
        GeminiAPIError: If video processing fails
    """
    pass

# scripts/youtube_fetcher.py
def fetch_etv_videos(date: datetime.date, slot: str) -> List[Dict]:
    """
    Fetch ETV Telugu News videos for specific date and slot.
    
    Args:
        date: Target date for video search
        slot: Time slot ('9pm' or '7am')
    
    Returns:
        List of video metadata dictionaries
    """
    pass

# scripts/gemini_processor.py
def process_video_content(video: Dict) -> Dict:
    """
    Process video with Gemini API to extract Telugu news summaries.
    
    Args:
        video: Video metadata from YouTube
    
    Returns:
        Processed news data with summary array
    """
    pass
```

#### Frontend JavaScript Interface
```javascript
// js/utils/data-loader.js
async function loadNewsForDate(date) {
  /**
   * Load news data for specific date.
   * @param {string} date - Date in YYYY-MM-DD format
   * @returns {Promise<Object>} News data object
   */
}

async function getAvailableDates() {
  /**
   * Get list of dates with available news data.
   * @returns {Promise<Array<string>>} Array of dates (YYYY-MM-DD)
   */
}

// js/components/sidebar.js
function renderSidebar(dates) {
  /**
   * Render date/time navigation sidebar.
   * @param {Array<string>} dates - Available news dates
   */
}

// js/components/news-display.js
function renderNewsDisplay(newsData) {
  /**
   * Render news content for selected date.
   * @param {Object} newsData - Daily news object
   */
}
```

### Dependencies

#### Backend Dependencies (Python)
```
google-api-python-client==2.100.0  # YouTube Data API
google-generativeai==0.3.0         # Gemini API
requests==2.31.0                   # HTTP client
python-dotenv==1.0.0               # Environment variables (local dev)
pytest==7.4.0                      # Testing
```

#### Frontend Dependencies
- **None** - Pure vanilla JavaScript, no npm packages
- Uses native browser APIs: `fetch()`, `localStorage`, `DOM`

#### External Services
- **GitHub Actions**: Free tier (2000 minutes/month for public repos)
- **GitHub Pages**: Free static hosting
- **YouTube Data API**: 10,000 quota units/day (free tier sufficient)
- **Google Gemini API**: Varies by tier (need to verify quota)

## Acceptance Criteria

### Backend Automation
- [ ] AC-001: GitHub Actions workflow runs automatically at scheduled times
- [ ] AC-002: Workflow successfully searches ETV YouTube channel
- [ ] AC-003: Workflow correctly identifies 9 PM and 7 AM videos by title pattern
- [ ] AC-004: Workflow validates ETV channel ID before processing
- [ ] AC-005: Workflow sends videos to Gemini API with correct prompt
- [ ] AC-006: Workflow parses Gemini response into 5-8 Telugu bullet points
- [ ] AC-007: Workflow generates valid JSON file in `data/` directory
- [ ] AC-008: Workflow commits JSON file to repository with descriptive message
- [ ] AC-009: Workflow handles "video not found" gracefully (no crash)
- [ ] AC-010: Workflow retries failed API calls 3 times before marking error
- [ ] AC-011: Workflow sends notification email on failure (optional)
- [ ] AC-012: Workflow completes within 15 minutes

### Frontend UI
- [ ] AC-013: Page loads in < 1.5 seconds on 3G network
- [ ] AC-014: Sidebar displays last 30 days of news dates
- [ ] AC-015: Sidebar shows Telugu date format correctly
- [ ] AC-016: Sidebar shows checkmarks for available time slots (9 PM, 7 AM)
- [ ] AC-017: Sidebar highlights today's date with visual indicator
- [ ] AC-018: Clicking sidebar date loads news in < 100ms
- [ ] AC-019: Main area displays date header in Telugu
- [ ] AC-020: Main area shows two sections (9 PM and 7 AM news)
- [ ] AC-021: Each section displays 5-8 Telugu bullet points
- [ ] AC-022: Each section shows "YouTube లో చూడండి" link that opens new tab
- [ ] AC-023: UI shows "సమాచారం లేదు" if data missing
- [ ] AC-024: UI is responsive on mobile (360px viewport)
- [ ] AC-025: Sidebar collapses to hamburger menu on mobile (< 768px)
- [ ] AC-026: All Telugu text renders correctly (no garbled characters)
- [ ] AC-027: Touch targets are minimum 44px on mobile
- [ ] AC-028: UI works offline after first load (optional)

### Integration
- [ ] AC-029: End-to-end test: Workflow runs → JSON generated → UI displays data
- [ ] AC-030: Historical data accessible for past 30 days
- [ ] AC-031: Old data (> 30 days) automatically deleted
- [ ] AC-032: GitHub Pages auto-deploys after workflow commits
- [ ] AC-033: No manual intervention required for daily operation

## Edge Cases

### Backend Edge Cases
1. **Video not yet published**: YouTube search returns empty
   - **Handling**: Log warning, create JSON with `"status": "not_found"`, retry on next run
   
2. **Video title format changed**: Title doesn't match regex pattern
   - **Handling**: Log error, notify admin, fallback to manual processing instructions
   
3. **Multiple videos match pattern**: More than one 9 PM or 7 AM video found
   - **Handling**: Take most recent by `published_at`, log warning about duplicates
   
4. **Gemini API rate limit**: Quota exceeded
   - **Handling**: Retry with exponential backoff, mark as error if all retries fail, send notification
   
5. **Gemini returns non-Telugu summary**: API returns English or gibberish
   - **Handling**: Validate language, retry with modified prompt emphasizing Telugu, mark error if fails
   
6. **Git push conflict**: Another workflow committed simultaneously
   - **Handling**: Pull latest, merge, retry push
   
7. **GitHub Actions quota exceeded**: Free tier limit reached
   - **Handling**: Workflow fails gracefully, send notification to upgrade or reduce schedule

### Frontend Edge Cases
1. **Today's JSON file missing**: Current date data not processed yet
   - **Handling**: Show last available date's data with banner: "తాజా వార్తలు ప్రాసెస్ అవుతున్నాయి" (Latest news processing)
   
2. **JSON file corrupted**: Invalid JSON syntax
   - **Handling**: Catch parse error, show error message in Telugu, log to console
   
3. **Network offline**: User has no internet connection
   - **Handling**: Show cached data from browser memory, display offline indicator
   
4. **Only one time slot available**: 9 PM processed but 7 AM failed
   - **Handling**: Show available slot, display "సమాచారం లేదు" for missing slot
   
5. **User clicks date in future**: Sidebar somehow shows future date
   - **Handling**: Prevent future dates from appearing, validate date is <= today
   
6. **Empty summary array**: Gemini returned no bullet points
   - **Handling**: Show fallback message: "ఈ వార్తలు అందుబాటులో లేవు" (News not available)
   
7. **Unicode rendering failure**: Telugu characters show as boxes
   - **Handling**: Include fallback fonts in CSS, detect font loading failure, show error

## Testing Strategy

### Backend Testing (pytest)

#### Unit Tests
```python
# tests/backend/test_youtube_fetcher.py
def test_fetch_etv_videos_returns_list()
def test_is_valid_title_accepts_9pm_format()
def test_is_valid_title_rejects_invalid_format()
def test_validate_channel_id_accepts_etv()
def test_validate_channel_id_rejects_others()

# tests/backend/test_gemini_processor.py
def test_process_video_returns_json_structure()
def test_process_video_validates_telugu_summary()
def test_process_video_retries_on_failure()

# tests/backend/test_json_generator.py
def test_generate_daily_json_creates_valid_file()
def test_generate_daily_json_handles_missing_slot()
```

#### Integration Tests
```python
# tests/backend/test_integration.py
def test_full_workflow_end_to_end()  # Mock APIs
def test_workflow_handles_video_not_found()
def test_workflow_handles_api_failure()
```

### Frontend Testing (Playwright)

#### UI Tests
```typescript
// tests/frontend/sidebar-navigation.spec.ts
test('should display last 30 days in sidebar')
test('should highlight today\'s date')
test('should load news on date click within 100ms')

// tests/frontend/news-display.spec.ts
test('should display 9 PM and 7 AM sections')
test('should render Telugu bullet points correctly')
test('should open YouTube links in new tab')

// tests/frontend/responsive.spec.ts
test('should collapse sidebar on mobile viewport')
test('should have 44px touch targets on mobile')

// tests/frontend/data-loading.spec.ts
test('should fetch JSON files from data/ directory')
test('should handle missing JSON file gracefully')
test('should cache loaded data in memory')
```

#### Visual Regression Tests
```typescript
// tests/frontend/visual.spec.ts
test('should match sidebar screenshot')
test('should match news display screenshot')
test('should match mobile layout screenshot')
```

### Manual Testing Checklist
- [ ] Test on actual mobile device (Android/iOS)
- [ ] Test with slow 3G throttling in Chrome DevTools
- [ ] Verify Telugu text rendering in Chrome, Firefox, Safari
- [ ] Test with GitHub Actions rate limits by simulating failures
- [ ] Verify email notifications work on workflow failure
- [ ] Test with missing videos (simulate by changing title pattern)
- [ ] Verify 30-day cleanup deletes old files correctly

## Technical Decisions & Implementation Details

### 1. GitHub Actions Workflow Timing

**Decision**: Workflow runs at **9:00 AM IST** and **11:00 PM IST**

**IST to UTC Conversion**:
- **9:00 AM IST** = **3:30 AM UTC** → cron: `'30 3 * * *'`
- **11:00 PM IST** = **5:30 PM UTC** → cron: `'30 17 * * *'`

**Branch Strategy**: Commit directly to **`dev` branch**
- Rationale: Automated commits don't need PR review
- GitHub Pages serves from `dev` branch
- Manual code changes go through PR to `dev`

```yaml
on:
  schedule:
    - cron: '30 3 * * *'   # 9:00 AM IST (process 7 AM video)
    - cron: '30 17 * * *'  # 11:00 PM IST (process 9 PM video)
```

### 2. YouTube Data API Integration

**Decision**: Use YouTube Data API v3 in Python with caching

**API Quota Analysis**:
- Daily quota: 10,000 units
- Search query: ~100 units per request
- Video metadata: ~1 unit per video
- Daily usage: 2 searches × 100 = 200 units + 2 videos × 1 = 2 units = **202 units/day**
- **Verdict**: ✅ Well within quota (only 2% usage)

**Caching Strategy**:
```python
# Cache video IDs in data/cache/video-ids.json to prevent duplicate processing
{
  "2025-12-08": {
    "9pm": "dQw4w9WgXcQ",
    "7am": "abc123xyz"
  }
}
```
- Check cache before calling YouTube API
- Skip processing if video ID already processed
- Prevents redundant Gemini API calls on workflow re-runs

### 3. Gemini API Video Processing

**Decision**: Use Gemini 2.5 Flash model with `file_data` (YouTube URL support)

**Python SDK Implementation**:
```python
import google.generativeai as genai
from google.generativeai import types

# Configure API
genai.configure(api_key=os.environ['GEMINI_API_KEY'])
client = genai.Client()

# Process YouTube video directly
response = client.models.generate_content(
    model='models/gemini-2.5-flash',
    contents=types.Content(
        parts=[
            types.Part(
                file_data=types.FileData(
                    file_uri=f'https://www.youtube.com/watch?v={video_id}'
                )
            ),
            types.Part(
                text='''విశ్లేషించి తెలుగులో 5-8 ముఖ్య వార్తా శీర్షికలు సంక్షిప్త వివరణతో తయారు చేయండి.
                
Format as JSON array:
[
  "వార్త శీర్షిక 1 - సంక్షిప్త వివరణ",
  "వార్త శీర్షిక 2 - సంక్షిప్త వివరణ"
]'''
            )
        ]
    )
)

# Parse response
summary = json.loads(response.text)
```

**Error Handling**: 3 retries with exponential backoff (1s, 2s, 4s)
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=4))
def process_with_gemini(video_id):
    # API call here
    pass
```

### 4. Data File Structure

**Decision**: Hybrid approach - Latest news + 30-day archive

**Directory Structure**:
```
data/
├── latest.json              # Current day (fast access)
├── index.json               # List of all available dates
└── archive/
    ├── 2025-12/
    │   ├── 2025-12-08.json
    │   ├── 2025-12-07.json
    │   └── ...
    └── 2025-11/
        └── ...
```

**Rotation Policy**:
- Keep 30 days of historical data
- Auto-delete files older than 30 days (weekly cleanup workflow)
- `latest.json` always points to most recent processed day

**`index.json` Schema**:
```json
{
  "last_updated": "2025-12-08T17:35:00Z",
  "available_dates": [
    {
      "date": "2025-12-08",
      "slots": ["9pm", "7am"],
      "file": "archive/2025-12/2025-12-08.json"
    },
    {
      "date": "2025-12-07",
      "slots": ["9pm"],
      "file": "archive/2025-12/2025-12-07.json"
    }
  ]
}
```

### 5. Frontend Data Loading Strategy

**Decision**: Fetch `index.json` first, then load date-specific files on demand

**Loading Sequence**:
```javascript
// On page load
1. Fetch data/index.json (get available dates list)
2. Render sidebar with available dates
3. Load data/latest.json (show today's news by default)
4. On date click → fetch data/archive/YYYY-MM/YYYY-MM-DD.json

// Cache busting
- Append ?t={timestamp} to JSON URLs for new data
- Use localStorage with version key to track updates
```

**Fallback Strategy**:
```javascript
// If index.json fails, generate last 30 days as fallback
const fallbackDates = generateLast30Days(); // Calculate dates in JS
// Try fetching each date's JSON file
```

**Cache Busting**:
```javascript
const timestamp = Date.now();
fetch(`data/index.json?t=${timestamp}`); // Force fresh fetch
```

### 6. Sidebar Date Rendering

**Decision**: Scrollable sidebar with both time slot indicators

**Sidebar Design**:
```
┌─────────────────────────┐
│  వార్తల చరిత్ర          │
├─────────────────────────┤
│ ● 8 Dec 2025            │ ← Today (highlighted)
│   ✓ 9 PM  ✓ 7 AM        │
├─────────────────────────┤
│   7 Dec 2025            │
│   ✓ 9 PM  ✗ 7 AM        │ ← Missing 7 AM
├─────────────────────────┤
│   6 Dec 2025            │
│   ✓ 9 PM  ✓ 7 AM        │
├─────────────────────────┤
│   ... (scrollable)       │
└─────────────────────────┘
```

**Mobile View** (< 768px):
- Sidebar collapses to hamburger menu (top-left)
- Opens as full-screen overlay on click
- Swipe left to close
- Bottom navigation shows current date

### 7. News Summary Display Behavior

**Decisions**:

1. **First Visit**: Load current day automatically
   ```javascript
   window.addEventListener('DOMContentLoaded', () => {
     loadNewsForDate(getCurrentDateIST());
   });
   ```

2. **Preserve Selection**: Use localStorage
   ```javascript
   localStorage.setItem('selectedDate', '2025-12-08');
   // On refresh, restore last selected date
   ```

3. **Date Switch Animation**: CSS fade transition (300ms)
   ```css
   .news-content {
     transition: opacity 0.3s ease-in-out;
   }
   ```

4. **Processing Indicator**: Show when data not available
   ```html
   <div class="processing-indicator">
     <span class="spinner"></span>
     <p>వార్తలు ప్రాసెస్ అవుతున్నాయి... (News processing...)</p>
     <small>దయచేసి కొన్ని నిమిషాల తర్వాత తనిఖీ చేయండి</small>
   </div>
   ```

### 8. Error Scenario Handling

**1. Video Not Found for Time Slot**:
```json
{
  "9pm": {
    "status": "not_found",
    "error_message": "Video not published yet",
    "checked_at": "2025-12-08T17:30:00Z"
  }
}
```
- UI shows: "9 PM వార్తలు ఇంకా అందుబాటులో లేవు" (9 PM news not yet available)

**2. Gemini API Failure**:
```json
{
  "9pm": {
    "status": "error",
    "error_message": "Gemini API rate limit exceeded",
    "video_id": "dQw4w9WgXcQ",
    "video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ"
  }
}
```
- UI shows: "వార్తలు ప్రాసెస్ చేయలేకపోయాం. YouTube వీడియో చూడండి" (Couldn't process. Watch YouTube video)
- Display video link as fallback

**3. Network Error Loading JSON**:
```javascript
try {
  const data = await fetch('data/archive/2025-12-08.json');
} catch (error) {
  // Show cached version from localStorage
  const cached = localStorage.getItem('news-2025-12-08');
  if (cached) {
    renderNews(JSON.parse(cached));
    showWarning('ఆఫ్‌లైన్ డేటా చూపిస్తున్నాం'); // Showing offline data
  }
}
```

**4. Corrupted JSON File**:
```javascript
try {
  const data = await response.json();
} catch (parseError) {
  console.error('JSON parse error:', parseError);
  showError('డేటా చదవలేకపోయాం. దయచేసి రిఫ్రెష్ చేయండి');
  // Notify admin via GitHub issue (optional)
}
```

### 9. GitHub Pages Deployment

**Decision**: Commit to `dev` branch, GitHub Pages serves `dev`

**Workflow**:
```
GitHub Actions (process-news.yml)
  ↓
Generate JSON files
  ↓
git add data/
git commit -m "chore: update news for 2025-12-08"
git push origin dev
  ↓
GitHub Pages auto-detects push
  ↓
Rebuilds site (1-2 minutes)
  ↓
Site live with fresh data
```

**Pages Configuration**:
- Source: `dev` branch
- Path: `/` (root directory)
- Custom domain: Optional (can add later)

**Auto-Rebuild**: GitHub Pages automatically rebuilds on any push to `dev` branch

### 10. Historical Data Management

**Decision**: Rotate data after 30 days, keep user-visible history at 30 days

**Storage Strategy**:
- Repository storage: 30 days rolling window
- User-visible history: 30 days (matches storage)
- Cleanup: Weekly GitHub Actions workflow

**Weekly Cleanup Workflow**:
```yaml
# .github/workflows/cleanup-old-data.yml
name: Cleanup Old Data
on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight UTC
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Delete files older than 30 days
        run: |
          find data/archive -name '*.json' -type f -mtime +30 -delete
      - name: Update index.json
        run: python scripts/rebuild_index.py
      - name: Commit changes
        run: |
          git add data/
          git commit -m "chore: cleanup data older than 30 days" || echo "Nothing to cleanup"
          git push
```

**Archival Strategy** (Future Enhancement):
- After 30 days, archive to GitHub Release assets (free unlimited storage)
- Keep compressed archive: `news-2025-11.tar.gz`
- User can download historical archives if needed

## Resolved Technical Questions

### API Quotas Summary
| Service | Daily Quota | Daily Usage | Utilization |
|---------|-------------|-------------|-------------|
| YouTube Data API | 10,000 units | ~202 units | 2% ✅ |
| Gemini API | Varies by tier | 2 video requests | Low ✅ |
| GitHub Actions | 2000 minutes/month | ~30 minutes/month | 1.5% ✅ |

### Font Loading Strategy
**Decision**: Google Fonts CDN with preconnect
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap" rel="stylesheet">
```
- Rationale: Smaller bundle, reliable CDN, good caching
- Fallback: System Telugu fonts in CSS

### Service Worker for Offline
**Decision**: Phase 2 enhancement (not MVP)
- MVP: Basic localStorage caching
- Future: Full service worker with offline-first strategy

### Time Zone Display
**Decision**: All timestamps in IST (Indian Standard Time)
```javascript
const formatTimeIST = (isoString) => {
  return new Date(isoString).toLocaleString('te-IN', {
    timeZone: 'Asia/Kolkata',
    dateStyle: 'long',
    timeStyle: 'short'
  });
};
```

### Video Thumbnails
**Decision**: Yes, show thumbnails in UI
```json
{
  "9pm": {
    "thumbnail_url": "https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
  }
}
```
- Improves visual appeal
- Lazy load images for performance

### Notification Recipients
**Decision**: Configure `NOTIFICATION_EMAIL` GitHub Secret
- Default: Repository owner's email
- Configurable per deployment

### Holiday/Missing Videos
**Decision**: Graceful handling with user-friendly message
- Backend: Mark as `"status": "not_found"`
- Frontend: Show "ఆ రోజు వార్తలు లేవు" (No news that day)

### Future Channel Support
**Decision**: Design for single channel, keep extensible
- Current: Hardcoded ETV channel ID
- Future: Config file for multiple channels
- Architecture allows easy extension

## Success Metrics

### Technical Metrics
- **Automation Success Rate**: > 95% of scheduled runs succeed
- **Page Load Time**: < 1.5s (P95) on 3G
- **Date Click Latency**: < 100ms (P95)
- **Total Page Weight**: < 150 KB
- **Backend Processing Time**: < 5 minutes per video
- **Test Coverage**: > 80% for backend, > 70% for frontend

### Business Metrics
- **System Uptime**: > 99.5% (accounting for scheduled maintenance)
- **Data Freshness**: News available within 1 hour of YouTube publication
- **Cost**: $0/month (GitHub free tier only)
- **Manual Intervention**: < 1 hour/month for monitoring

### User Experience Metrics
- **Time to View News**: < 3 seconds from page load to viewing summaries
- **Mobile Usability**: Fully functional on 360px viewport
- **Accessibility**: WCAG AA compliant
- **Historical Access**: 30 days of news available 100% of time

## Implementation Phases

### Phase 1: Backend Automation (Weeks 1-2)
1. Setup GitHub Actions workflow skeleton
2. Implement YouTube video discovery script
3. Implement Gemini video processing script
4. Implement JSON generation script
5. Add error handling and retry logic
6. Configure API keys as GitHub Secrets
7. Test end-to-end workflow
8. Add notification on failure

### Phase 2: Frontend UI (Weeks 3-4)
1. Create HTML structure with semantic elements
2. Implement CSS styling (mobile-first)
3. Implement sidebar date navigation
4. Implement news display components
5. Implement data loading from JSON files
6. Add Telugu language support and fonts
7. Test responsive design on multiple devices
8. Add accessibility features (ARIA labels, keyboard nav)

### Phase 3: Integration & Testing (Week 5)
1. End-to-end testing (workflow → UI)
2. Performance optimization
3. Visual regression testing
4. Manual testing on real devices
5. Fix bugs and polish UI
6. Documentation (README, deployment guide)

### Phase 4: Deployment & Monitoring (Week 6)
1. Deploy to GitHub Pages
2. Configure custom domain (optional)
3. Set up monitoring and alerts
4. Test with real ETV videos for 7 days
5. Gather feedback and iterate
6. Final handoff and documentation

## Implementation Reference

### Key Configuration Values

| Configuration | Value | Notes |
|---------------|-------|-------|
| **ETV Channel ID** | `UCJi8M0hRKjz8SLPvJKEVTOg` | Verified as of 2025-12-08 |
| **9 PM Video Pattern** | `9 PM \| ETV Telugu News \| {Date}` | Regex: `^9 PM \| ETV Telugu News \|` |
| **7 AM Video Pattern** | `7 AM \| ETV Telugu News \| {Date}` | Regex: `^7 AM \| ETV Telugu News \|` |
| **Workflow Cron (9 AM IST)** | `'30 3 * * *'` | UTC: 3:30 AM |
| **Workflow Cron (11 PM IST)** | `'30 17 * * *'` | UTC: 5:30 PM |
| **Data Retention** | 30 days | Weekly cleanup on Sundays |
| **Target Branch** | `dev` | Direct commits from Actions |
| **Telugu Font** | Noto Sans Telugu | Google Fonts CDN |
| **Mobile Breakpoint** | 768px | Sidebar collapse point |
| **Performance Budget** | 150 KB | Total page weight |
| **FCP Target** | < 1.5s | On 3G network |

### GitHub Secrets Configuration

```bash
# Required secrets (configure in repository settings)
YOUTUBE_API_KEY=AIza...        # YouTube Data API v3 key
GEMINI_API_KEY=AIza...         # Google Gemini API key
NOTIFICATION_EMAIL=user@email  # Optional: failure alerts
```

### Python Dependencies

```python
# scripts/requirements.txt
google-api-python-client==2.100.0
google-generativeai==0.3.0
requests==2.31.0
tenacity==8.2.3  # For retry logic
pytest==7.4.0
```

### Gemini API Reference

**Documentation**: https://ai.google.dev/gemini-api/docs/video-understanding#python_2

**Model**: `gemini-2.5-flash` (supports YouTube URLs in `file_data`)

**Prompt Template**:
```
విశ్లేషించి తెలుగులో 5-8 ముఖ్య వార్తా శీర్షికలు సంక్షిప్త వివరణతో తయారు చేయండి.

Format as JSON array:
[
  "వార్త శీర్షిక 1 - సంక్షిప్త వివరణ",
  "వార్త శీర్షిక 2 - సంక్షిప్త వివరణ"
]
```

### UI Text (Telugu Translations)

| English | Telugu | Context |
|---------|--------|---------|
| ETV Telugu News Summary | ETV తెలుగు న్యూస్ సారాంశం | Header |
| News History | వార్తల చరిత్ర | Sidebar title |
| 9 PM News | రాత్రి 9 గంటల వార్తలు | Section header |
| 7 AM News | ఉదయం 7 గంటల వార్తలు | Section header |
| Watch on YouTube | YouTube లో చూడండి | Video link |
| No news available | సమాచారం లేదు | Missing data |
| News processing... | వార్తలు ప్రాసెస్ అవుతున్నాయి... | Loading state |
| Showing offline data | ఆఫ్‌లైన్ డేటా చూపిస్తున్నాం | Cache fallback |
| No news that day | ఆ రోజు వార్తలు లేవు | Holiday/missing |
| Couldn't process | వార్తలు ప్రాసెస్ చేయలేకపోయాం | API error |

### File Naming Conventions

```
# Backend scripts
scripts/
├── process_daily_news.py       # Main orchestrator
├── youtube_fetcher.py          # YouTube API wrapper
├── gemini_processor.py         # Gemini API wrapper
├── json_generator.py           # Data file creation
├── rebuild_index.py            # Index regeneration
└── utils/
    ├── validators.py           # Input validation
    ├── error_handler.py        # Retry logic
    └── config.py               # Constants

# Data files
data/
├── latest.json                 # Symlink or copy of today
├── index.json                  # Master index
├── cache/
│   └── video-ids.json          # Processed video cache
└── archive/
    └── YYYY-MM/
        └── YYYY-MM-DD.json     # Daily news files

# Frontend files
index.html
css/
├── main.css                    # Global styles
├── sidebar.css                 # Sidebar component
├── news-display.css            # News content
└── telugu-fonts.css            # Typography
js/
├── app.js                      # Entry point
├── components/
│   ├── sidebar.js              # Date navigation
│   └── news-display.js         # Content renderer
└── utils/
    ├── data-loader.js          # Fetch JSON
    └── date-formatter.js       # IST formatting
```

### Testing Commands

```bash
# Backend tests
cd scripts/
python -m pytest tests/backend/ -v

# Frontend tests
npx playwright test tests/frontend/

# Manual workflow trigger
gh workflow run process-news.yml --ref dev -f date=2025-12-08 -f slot=both
```

### Deployment Checklist

- [ ] Configure GitHub Secrets (YOUTUBE_API_KEY, GEMINI_API_KEY)
- [ ] Enable GitHub Actions in repository settings
- [ ] Configure GitHub Pages source (dev branch, root directory)
- [ ] Verify cron schedule converts IST → UTC correctly
- [ ] Test manual workflow dispatch
- [ ] Add repository collaborators (if team project)
- [ ] Set up notification email (optional)
- [ ] Document API key rotation process
- [ ] Monitor first week of automated runs

### Performance Optimization Checklist

**Backend**:
- [ ] Cache video IDs to prevent duplicate API calls
- [ ] Use exponential backoff for API retries
- [ ] Generate index.json only when archive changes
- [ ] Implement rate limiting for API calls

**Frontend**:
- [ ] Lazy load images (thumbnails)
- [ ] Minify CSS/JS for production
- [ ] Use font-display: swap for Telugu fonts
- [ ] Implement browser cache with versioning
- [ ] Preconnect to fonts.googleapis.com
- [ ] Use IntersectionObserver for sidebar scrolling

### Monitoring & Alerts

**What to Monitor**:
1. GitHub Actions workflow success rate (target: > 95%)
2. API quota usage (YouTube, Gemini)
3. Page load performance (Lighthouse CI)
4. JSON file size growth (prevent bloat)
5. User-visible errors (404s, parse errors)

**Alert Conditions**:
- Workflow fails 2 consecutive times → Email alert
- YouTube API quota > 80% → Warning notification
- GitHub Actions minutes > 80% → Reduce frequency
- JSON files not updating > 24 hours → Critical alert

### Maintenance Tasks

**Daily** (automated):
- Process 9 PM news video
- Process 7 AM news video
- Update index.json

**Weekly** (automated):
- Cleanup data older than 30 days
- Rebuild index.json from scratch

**Monthly** (manual):
- Review API quota usage
- Check GitHub Actions usage
- Review error logs
- Update dependencies (if security patches)

**Quarterly** (manual):
- Verify ETV channel ID still valid
- Test video title pattern still matches
- Performance audit (Lighthouse)
- Accessibility audit (WAVE tool)

## Notes

- **Commit Strategy**: Commit only if file content changed (avoid empty commits)
- **Mobile-First**: Start with 360px viewport, progressively enhance for larger screens
- **IST Display**: All user-facing timestamps in Indian Standard Time
- **Error Philosophy**: Fail gracefully, never show stack traces to users
- **Accessibility**: WCAG AA compliant, keyboard navigable
- **Offline Support**: Phase 2 enhancement with service worker

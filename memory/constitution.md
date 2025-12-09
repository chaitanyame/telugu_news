# ETV Telugu News Aggregator - Constitution

## Vision

Build a **fully automated, zero-latency** ETV Telugu News aggregation website where GitHub Actions serves as the backend processing engine. The system automatically discovers, processes, and publishes daily 9 PM and 7 AM news videos from ETV Telugu News YouTube channel using Google Gemini API, storing results as static JSON files. The frontend is a **passive viewer** - a fast, accessible, mobile-first interface that reads pre-processed data with instant page transitions and zero API calls during user interaction. The entire system runs on GitHub's free infrastructure (Actions + Pages) with no servers, databases, or manual intervention required.

## Architectural Philosophy: Automation-First

### The Core Separation

```
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (GitHub Actions - Python)                          │
│  • Runs automatically on schedule (daily at 10 PM, 8 AM IST)│
│  • Fetches videos from YouTube                              │
│  • Processes videos with Gemini API                         │
│  • Generates static JSON files                              │
│  • Commits results to repository                            │
│  • Triggers GitHub Pages deployment                         │
│  • Zero human interaction required                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
                  (JSON files committed)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (GitHub Pages - Vanilla JS)                       │
│  • Reads static JSON files only                             │
│  • No API calls during user interaction                     │
│  • Instant page transitions                                 │
│  • Works offline after first load                           │
│  • Zero latency for all operations                          │
└─────────────────────────────────────────────────────────────┘
```

**Key Principle**: The UI never waits for processing. All heavy lifting happens in background automation before the user visits.

## Core Principles

### 1. Simplicity First (with Strategic Separation)

**Frontend (Vanilla JS)**:
- **Zero frameworks**: Pure HTML, CSS, JavaScript - no React, Vue, or Angular
- **Zero build process**: Deploy directly to GitHub Pages without bundlers
- **Zero API calls**: All data pre-processed and served as static JSON
- **Progressive enhancement**: Core functionality works without JavaScript, enhanced experience with it

**Backend (Python Automation)**:
- **Purpose-built scripts**: Python for YouTube/Gemini API orchestration
- **Minimal dependencies**: Only essential libraries (requests, google-api-python-client, google-generativeai)
- **GitHub Actions native**: Use GitHub's workflow syntax, no custom CI/CD
- **Idempotent operations**: Same input always produces same output, safe to re-run

### 2. Test-Driven Development (TDD) - MANDATORY

> ⚠️ **NON-NEGOTIABLE**: Implementation code MUST NOT be written before a failing test exists.

```
┌─────────────────────────────────────────────────────────────────┐
│  🛑 TDD IS A HARD GATE - NOT A SUGGESTION                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BEFORE writing ANY implementation code:                        │
│                                                                 │
│  1. Create test file: tests/{feature}.spec.ts                  │
│  2. Run test: npx playwright test tests/{feature}.spec.ts      │
│  3. VERIFY test FAILS                                          │
│  4. Update feature_list.json:                                  │
│     - test_file: "tests/{feature}.spec.ts"                     │
│     - test_fails_before: true                                  │
│                                                                 │
│  ONLY THEN may you write implementation code.                  │
│                                                                 │
│  AFTER implementation passes:                                   │
│  5. Run test: verify it PASSES                                  │
│  6. Update feature_list.json:                                  │
│     - test_passes_after: true                                  │
│     - passes: true                                             │
│                                                                 │
│  ⛔ Setting passes:true without test_passes_after:true          │
│     is a TDD VIOLATION                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

- **RED**: Write the test FIRST - verify it FAILS
- **GREEN**: Implement ONLY enough code to pass the test
- **REFACTOR**: Clean up while keeping tests green
- **ENFORCEMENT**: If test passes before implementation, the test is wrong
- **VIOLATION**: Writing implementation before test is a framework violation

### 3. Mobile-First User Experience

- **Performance budget**: First contentful paint < 1.5s on 3G
- **Responsive by default**: Design for 360px mobile screens first, then scale up
- **Touch-friendly**: Minimum 44px touch targets for all interactive elements
- **Offline-aware**: Graceful degradation when network is unavailable

### 4. Telugu Language Excellence

- **Unicode UTF-8**: All files must use UTF-8 encoding
- **Font rendering**: Test across Chrome, Firefox, Safari for Telugu script consistency
- **Readability**: Proper line-height (1.6-1.8) and letter-spacing for Telugu text
- **Cultural sensitivity**: News presentation aligned with Telugu-speaking audience expectations

### 5. Automation-First API Integration

**Critical Principle**: APIs are ONLY called by GitHub Actions backend, NEVER by frontend.

- **Security**: API keys stored as GitHub Secrets, never in code
- **Automation boundary**: YouTube API + Gemini API = backend only
- **Channel validation**: Automated script validates ETV Telugu News channel ID
- **Video filtering**: Regex patterns in Python script match exact titles
- **Video processing**: Gemini API's video intelligence extracts news summaries
- **Error handling**: Automated retries with exponential backoff in GitHub Actions
- **Notifications**: Email/Slack alerts on workflow failure
- **Rate limiting**: Batch processing respects API quotas (YouTube: 10,000/day, Gemini: varies by tier)
- **Resilience**: Failed runs auto-retry 3 times before alerting
- **Zero user impact**: Processing failures never affect frontend (serves last good data)

### 6. Zero-Latency Frontend Principle

**The UI is a Viewer, Not a Processor**

```
Frontend responsibilities:
✅ Read static JSON files
✅ Render Telugu text beautifully
✅ Provide instant date/time navigation
✅ Cache data in browser (optional enhancement)

Frontend NEVER does:
❌ Call YouTube API
❌ Call Gemini API
❌ Process videos
❌ Wait for any external service
❌ Show loading spinners (data is already there)
```

**Performance Contract**:
- Page load → First paint: < 1 second
- Click date → News display: < 50ms (read from JSON)
- All interactions: Instant (no network calls)
- Offline capable: Works after first load

### 7. Incremental Progress
- One feature at a time
- Complete before moving on
- Commit after each success
- Don't try to do too much

### 7. File-Based Memory
- All state lives in files
- `feature_list.json` is the source of truth
- Progress notes bridge sessions
- Git history enables rollback

### 8. Verify Before Claiming
- Test features before marking complete
- Check existing features still work
- Quality over speed

### 9. Document for Amnesia
- Next agent has zero memory
- Write clear progress notes
- Explain decisions
- Leave clean state

### 10. Update Progress Immediately
- Update progress notes after each feature completion
- Document bugs/issues as soon as discovered
- Write before ending session (mandatory)
- Rule: "If you wouldn't remember it tomorrow, write it down now."

### 11. Feature List is Sacred
- Only change `passes` field
- Never remove features
- Never edit descriptions
- Never modify steps

## Technical Standards

### Language & Runtime (Dual-Stack Architecture)

#### Frontend Stack (User-Facing)
- **Language**: Vanilla JavaScript (ES6+) - zero frameworks
- **Markup**: HTML5 with semantic elements
- **Styling**: CSS3 with custom properties (CSS variables)
- **Deployment**: GitHub Pages (static hosting)
- **Browser Support**: Modern evergreen browsers (Chrome 90+, Firefox 88+, Safari 14+)
- **Data Source**: Static JSON files (`data/processed/*.json`)
- **No Runtime**: No Node.js, no server, no API calls

#### Backend Stack (Automation)
- **Language**: Python 3.11+ (GitHub Actions runner)
- **Runtime**: GitHub Actions Ubuntu runners
- **Execution**: Scheduled cron (daily at 22:00 IST, 08:00 IST)
- **APIs Used**:
  - YouTube Data API v3 (video discovery)
  - Google Gemini API (video content analysis)
- **Output**: Static JSON files committed to repository
- **Triggers**: 
  - Scheduled: `cron: '30 16 * * *'` (10 PM IST)
  - Scheduled: `cron: '30 2 * * *'` (8 AM IST)
  - Manual: `workflow_dispatch` (for testing)

### Code Quality Standards

#### JavaScript
- Use `const` and `let`, never `var`
- Meaningful variable names: `newsArticles` not `arr`
- Pure functions where possible
- Avoid global scope pollution
- Use template literals for string concatenation
- Modular components in separate files

```javascript
// Good
const parseYouTubeResponse = (responseData) => {
  const articles = responseData.items.map(item => ({
    title: item.snippet.title,
    publishedAt: new Date(item.snippet.publishedAt)
  }));
  return articles;
};

// Bad
function f(d) {
  var a = [];
  for (var i = 0; i < d.items.length; i++) {
    a.push(d.items[i].snippet.title);
  }
  return a;
}
```

#### CSS
- Mobile-first media queries
- CSS custom properties for theming
- BEM or utility-first naming conventions
- No inline styles in HTML
- Optimize for Telugu text rendering

```css
/* Good */
:root {
  --color-primary: #1e40af;
  --font-telugu: 'Noto Sans Telugu', sans-serif;
  --line-height-telugu: 1.7;
}

.news-card__title {
  font-family: var(--font-telugu);
  line-height: var(--line-height-telugu);
}

/* Mobile-first */
@media (min-width: 768px) {
  .news-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

#### HTML
- Semantic HTML5 elements
- Proper heading hierarchy (h1 → h2 → h3)
- ARIA labels for accessibility
- lang attribute with Telugu support

```html
<!-- Good -->
<article class="news-card" lang="te">
  <h2 class="news-card__title">వార్త శీర్షిక</h2>
  <p class="news-card__summary">వార్త సారాంశం...</p>
</article>

<!-- Bad -->
<div>
  <div class="title">వార్త శీర్షిక</div>
  <div>వార్త సారాంశం...</div>
</div>
```

## Libraries

### Frontend Libraries (None Required)

| Category | Library | Reason |
|----------|---------|--------|
| **UI Testing** | Playwright | Test pre-generated JSON rendering |
| **HTTP Client** | `fetch` (native) | Only for reading static JSON files |
| **Framework** | None (Vanilla JS) | Zero dependencies, zero build step |
| **State Management** | None | Read-only data from JSON files |

### Backend Libraries (Python)

```python
# scripts/requirements.txt
google-api-python-client==2.100.0  # YouTube Data API
google-generativeai==0.3.0         # Gemini API
requests==2.31.0                   # HTTP client
python-dotenv==1.0.0               # Environment variables (local dev)
pytest==7.4.0                      # Testing framework
```

| Category | Library | Reason |
|----------|---------|--------|
| **YouTube API** | google-api-python-client | Official Google SDK for video discovery |
| **Gemini API** | google-generativeai | Official SDK for video content analysis |
| **HTTP Client** | requests | Simple, reliable HTTP library |
| **Testing** | pytest | Industry standard Python testing |

### Explicitly Avoided (Frontend)
- ❌ React, Vue, Angular - Unnecessary for reading static JSON
- ❌ Webpack, Vite, Parcel - No build process needed
- ❌ TypeScript - Adds compilation step, vanilla JS reads JSON fine
- ❌ jQuery - Modern `fetch()` API is native
- ❌ Bootstrap, Tailwind - Custom CSS keeps bundle minimal
- ❌ Axios, Ky - Native `fetch()` sufficient for JSON files

### Explicitly Avoided (Backend)
- ❌ Node.js for backend - Python better for API orchestration
- ❌ Database (MySQL, PostgreSQL) - Static JSON files sufficient
- ❌ Redis, Memcached - No caching layer needed
- ❌ Docker - GitHub Actions provides runtime

## Quality Gates

### Frontend Quality Gates
Before marking any frontend feature as complete (`passes: true`):

- [ ] **Tests pass**: `npx playwright test tests/frontend/{feature}.spec.ts` succeeds
- [ ] **TDD cycle complete**: test_fails_before=true AND test_passes_after=true
- [ ] **Manual browser verification**: Feature works in live browser
- [ ] **Static JSON loading**: Only reads from `data/processed/*.json`, no API calls
- [ ] **Zero latency**: Date click → news display < 100ms
- [ ] **Mobile responsive**: Works on 360px mobile viewport
- [ ] **Telugu text renders correctly**: No garbled Unicode characters
- [ ] **Performance check**: First paint < 1s on throttled 3G
- [ ] **Error handling**: Graceful fallback if JSON missing
- [ ] **No console errors**: Clean browser console
- [ ] **Offline capable**: Works after first load (optional enhancement)
- [ ] **Accessibility**: Keyboard navigation and screen reader friendly

### Backend Quality Gates
Before marking any backend feature as complete (`passes: true`):

- [ ] **Tests pass**: `pytest tests/backend/test_{feature}.py` succeeds
- [ ] **TDD cycle complete**: test_fails_before=true AND test_passes_after=true
- [ ] **GitHub Actions workflow runs**: Workflow completes without errors
- [ ] **ETV channel validation**: Only fetches from official ETV channel
- [ ] **Title pattern matching**: Regex correctly filters 9 PM and 7 AM videos
- [ ] **Video processing**: Gemini API successfully extracts Telugu news summaries
- [ ] **JSON generation**: Valid JSON files created in `data/processed/`
- [ ] **API key security**: Secrets used, no hardcoded keys
- [ ] **Error handling**: Retries with exponential backoff
- [ ] **Notification on failure**: Email/alert sent on workflow failure
- [ ] **Idempotent**: Re-running same date produces same output
- [ ] **30-day cleanup**: Old data automatically removed

### Integration Quality Gates
Before creating PR:

- [ ] **End-to-end test**: Full workflow run + frontend displays new data
- [ ] **Historical data intact**: Previous 30 days still accessible
- [ ] **Index updated**: `index.json` reflects all available dates
- [ ] **GitHub Pages deploys**: Site auto-deploys with new data
- [ ] **No manual steps**: Entire pipeline automated

## File Conventions

### Project Structure (Automation-First)

```
/
├───────────────────────────────────────────────────
│ FRONTEND (GitHub Pages - Static Site)          │
├───────────────────────────────────────────────────
├── index.html                      # Main entry point (date/time sidebar)
├── css/
│   ├── main.css                # Global styles
│   ├── components/             # Component-specific styles
│   │   ├── sidebar.css         # Date/time navigation sidebar
│   │   ├── news-card.css       # News summary cards
│   │   └── video-embed.css     # Video player styles
│   └── telugu-fonts.css        # Telugu typography
├── js/
│   ├── app.js                  # Main app (loads JSON, renders UI)
│   ├── components/
│   │   ├── sidebar.js          # Interactive date/time sidebar
│   │   ├── news-list.js        # News summary renderer
│   │   └── video-player.js     # Embedded YouTube player
│   └── utils/
│       ├── data-loader.js      # Fetch static JSON files
│       └── date-formatter.js   # Telugu date/time formatting
├── assets/
│   ├── images/                 # Logos, icons
│   └── fonts/                  # Telugu fonts (if self-hosted)
├───────────────────────────────────────────────────
│ DATA (Generated by Backend Automation)        │
├───────────────────────────────────────────────────
├── data/
│   ├── processed/              # Generated JSON files
│   │   ├── index.json          # Master index (last 30 days)
│   │   ├── 2025-12-08.json     # Single day's news
│   │   ├── 2025-12-07.json
│   │   └── ... (30 days history)
│   └── config/
│       └── etv-channel.json    # ETV channel config (static)
├───────────────────────────────────────────────────
│ BACKEND (GitHub Actions - Python Scripts)     │
├───────────────────────────────────────────────────
├── .github/
│   └── workflows/
│       ├── process-news.yml    # Main automation workflow
│       └── cleanup-old-data.yml # Weekly cleanup (keep 30 days)
├── scripts/
│   ├── process_daily_news.py   # Main orchestrator
│   ├── youtube_fetcher.py      # Fetch ETV videos
│   ├── gemini_processor.py     # Process videos with Gemini
│   ├── json_generator.py       # Generate static JSON
│   ├── utils/
│   │   ├── validators.py       # Channel/title validation
│   │   ├── error_handler.py    # Retry logic, notifications
│   │   └── config.py           # API keys, constants
│   └── requirements.txt        # Python dependencies
├───────────────────────────────────────────────────
│ TESTING & FRAMEWORK                            │
├───────────────────────────────────────────────────
├── tests/
│   ├── frontend/               # Playwright UI tests
│   │   ├── date-navigation.spec.ts
│   │   └── news-display.spec.ts
│   ├── backend/                # Python unit tests
│   │   ├── test_youtube_fetcher.py
│   │   ├── test_gemini_processor.py
│   │   └── test_json_generator.py
│   └── issues/                 # Bug regression tests
└── memory/                     # Agent framework files
```

**Key Principle**: Frontend reads `data/processed/*.json` only. Backend generates these files via GitHub Actions.

### Naming Conventions
- **Files**: kebab-case (`news-card.js`, `main.css`)
- **CSS classes**: BEM or kebab-case (`.news-card__title`, `.btn-primary`)
- **JavaScript**: camelCase for variables/functions, PascalCase for classes
- **Constants**: UPPER_SNAKE_CASE (`API_ENDPOINT`, `MAX_ARTICLES`)

### File Sizes
- HTML files: < 50 KB
- CSS files: < 30 KB per file
- JavaScript modules: < 15 KB per file (keep modular)
- Total bundle (all files): < 150 KB uncompressed

## Testing Strategy

### Test Types

#### 1. Frontend Tests (Playwright)
- **Location**: `tests/frontend/{feature}.spec.ts`
- **Scope**: UI interactions with static JSON data
- **Run**: `npx playwright test tests/frontend/`

```typescript
// Example: tests/frontend/date-navigation.spec.ts
test('should load and display news for selected date', async ({ page }) => {
  await page.goto('http://localhost:8000');
  
  // Wait for sidebar to load
  await expect(page.locator('.date-sidebar')).toBeVisible();
  
  // Click on a date
  await page.click('[data-date="2025-12-08"]');
  
  // Verify news loads instantly (< 100ms)
  const startTime = Date.now();
  await expect(page.locator('.news-card').first()).toBeVisible();
  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(100);
  
  // Verify Telugu content rendered
  await expect(page.locator('.news-card__headline')).toContainText(/[\u0C00-\u0C7F]+/);
});

test('should navigate between 9 PM and 7 AM slots', async ({ page }) => {
  await page.goto('http://localhost:8000');
  await page.click('[data-date="2025-12-08"]');
  
  // Click 9 PM slot
  await page.click('[data-slot="9PM"]');
  await expect(page.locator('.broadcast-title')).toContainText('9 PM');
  
  // Click 7 AM slot
  await page.click('[data-slot="7AM"]');
  await expect(page.locator('.broadcast-title')).toContainText('7 AM');
});

test('should work offline after first load', async ({ page, context }) => {
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');
  
  // Go offline
  await context.setOffline(true);
  
  // Should still navigate (if service worker implemented)
  await page.click('[data-date="2025-12-08"]');
  await expect(page.locator('.news-card')).toBeVisible();
});
```

#### 2. Backend Tests (pytest)
- **Location**: `tests/backend/test_{module}.py`
- **Scope**: Python script unit tests
- **Run**: `pytest tests/backend/ -v`

```python
# Example: tests/backend/test_youtube_fetcher.py
import pytest
from scripts.youtube_fetcher import fetch_etv_videos, is_valid_title
from datetime import date

def test_fetch_etv_videos_returns_list():
    """Test that YouTube fetcher returns list of videos."""
    videos = fetch_etv_videos(date(2025, 12, 8))
    assert isinstance(videos, list)

def test_is_valid_title_accepts_9pm_format():
    """Test title validation for 9 PM news."""
    valid_title = "9 PM | ETV Telugu News | 8th December 2024"
    assert is_valid_title(valid_title) == True

def test_is_valid_title_rejects_wrong_format():
    """Test title validation rejects invalid format."""
    invalid_title = "Some Random Video Title"
    assert is_valid_title(invalid_title) == False

def test_is_valid_title_accepts_7am_format():
    """Test title validation for 7 AM news."""
    valid_title = "7 AM | ETV Telugu News | 8th December 2024"
    assert is_valid_title(valid_title) == True

# Example: tests/backend/test_gemini_processor.py
from scripts.gemini_processor import process_video_content

def test_process_video_returns_json_structure():
    """Test that Gemini processor returns expected JSON structure."""
    mock_video = {
        'id': 'test123',
        'title': '9 PM | ETV Telugu News | 8th December 2024'
    }
    result = process_video_content(mock_video)
    
    assert 'news_items' in result
    assert isinstance(result['news_items'], list)
    assert all('headline' in item for item in result['news_items'])
    assert all('summary' in item for item in result['news_items'])
```

#### 2. Regression Tests (Bug Fixes)
- **Location**: `tests/issues/I{id}-{description}.spec.ts`
- **Scope**: Verify bugs stay fixed
- **Run**: `npx playwright test tests/issues/`

#### 3. Manual Testing Checklist
Before deploying to production:
- [ ] Test on actual mobile device (Android/iOS)
- [ ] Test with slow 3G throttling
- [ ] Verify Telugu text in Chrome, Firefox, Safari
- [ ] Test with API rate limit exceeded
- [ ] Test with invalid YouTube URL
- [ ] Test offline behavior

### Testing Principles
- Write tests in Telugu where appropriate for error messages
- Test edge cases: empty input, malformed URLs, API failures
- Use Playwright's built-in assertions (`.toBeVisible()`, `.toHaveText()`)
- Keep tests isolated - no dependencies between tests
- Run tests before committing

## Performance Requirements

### Load Time Budget (3G Connection)
- **Time to First Byte (TTFB)**: < 600ms
- **First Contentful Paint (FCP)**: < 1.5s
- **Time to Interactive (TTI)**: < 3.0s
- **Total Page Weight**: < 150 KB (uncompressed)

### Optimization Techniques
1. **Critical CSS inline**: Above-the-fold styles in `<head>`
2. **Defer non-critical JS**: Use `defer` attribute
3. **Lazy load images**: Use `loading="lazy"`
4. **Minimize API calls**: Batch requests when possible
5. **Cache API responses**: Store in sessionStorage (expires on tab close)
6. **Font optimization**: Use `font-display: swap` for Telugu fonts

### API Performance
- **Gemini API timeout**: 30 seconds for video processing (longer than text)
- **YouTube API timeout**: 10 seconds for video search
- **Client-side debouncing**: 500ms for manual trigger button
- **Rate limit handling**: Exponential backoff (1s, 2s, 4s...)

## Fully Automated Backend Processing

### GitHub Actions Workflow (The Engine)

**Critical Principle**: Zero manual intervention. The system runs itself.

```yaml
# .github/workflows/process-news.yml
name: Process ETV Telugu News

on:
  # Scheduled runs (automatic)
  schedule:
    - cron: '30 16 * * *'  # 10:00 PM IST (after 9 PM news published)
    - cron: '30 2 * * *'   # 8:00 AM IST (after 7 AM news published)
  
  # Manual trigger (for testing/debugging only)
  workflow_dispatch:
    inputs:
      date:
        description: 'Process specific date (YYYY-MM-DD)'
        required: false
        default: 'today'

jobs:
  process-news:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Required to commit processed data
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r scripts/requirements.txt
      
      - name: Process daily news
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          NOTIFICATION_EMAIL: ${{ secrets.NOTIFICATION_EMAIL }}
        run: |
          python scripts/process_daily_news.py \
            --date "${{ github.event.inputs.date || 'today' }}"
      
      - name: Commit processed data
        run: |
          git config user.name "ETV News Bot"
          git config user.email "actions@github.com"
          git add data/processed/
          
          if git diff --staged --quiet; then
            echo "No changes to commit"
          else
            git commit -m "chore: process ETV news for $(date +%Y-%m-%d)"
            git push
          fi
      
      - name: Notify on failure
        if: failure()
        uses: dawidd6/action-send-mail@v3
        with:
          server_address: smtp.gmail.com
          server_port: 587
          username: ${{ secrets.SMTP_USERNAME }}
          password: ${{ secrets.SMTP_PASSWORD }}
          subject: '⚠️ ETV News Processing Failed'
          body: |
            Workflow run failed: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
            Date: $(date)
          to: ${{ secrets.NOTIFICATION_EMAIL }}
```

### Python Processing Script (Orchestrator)

```python
# scripts/process_daily_news.py
import argparse
from datetime import datetime, timedelta
from youtube_fetcher import fetch_etv_videos
from gemini_processor import process_video_content
from json_generator import generate_daily_json, update_index
from utils.error_handler import retry_with_backoff, notify_error

def main(target_date: str):
    """Main orchestrator for daily news processing."""
    
    # Parse date
    if target_date == 'today':
        date = datetime.now().date()
    else:
        date = datetime.strptime(target_date, '%Y-%m-%d').date()
    
    print(f"Processing ETV Telugu News for {date}")
    
    try:
        # Step 1: Fetch videos from YouTube
        videos = retry_with_backoff(
            fetch_etv_videos,
            date=date,
            max_retries=3
        )
        print(f"Found {len(videos)} ETV news videos")
        
        if not videos:
            print("No videos found for this date")
            return
        
        # Step 2: Process each video with Gemini API
        processed_news = []
        for video in videos:
            news_data = retry_with_backoff(
                process_video_content,
                video=video,
                max_retries=3
            )
            processed_news.append(news_data)
        
        # Step 3: Generate static JSON files
        generate_daily_json(date, processed_news)
        update_index(date, processed_news)
        
        print(f"Successfully processed {len(processed_news)} news broadcasts")
    
    except Exception as e:
        notify_error(f"Processing failed: {str(e)}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default='today')
    args = parser.parse_args()
    main(args.date)
```

### Static JSON Data Structure

**Critical Principle**: Frontend ONLY reads pre-generated JSON files. No API calls.

#### Master Index File
```json
// data/processed/index.json
{
  "generated_at": "2025-12-08T16:05:00Z",
  "days_available": 30,
  "dates": [
    {
      "date": "2025-12-08",
      "broadcasts": [
        {
          "slot": "9PM",
          "published_at": "2025-12-08T15:30:00Z",
          "processed_at": "2025-12-08T16:00:00Z",
          "video_id": "dQw4w9WgXcQ",
          "news_count": 12,
          "data_file": "2025-12-08.json"
        },
        {
          "slot": "7AM",
          "published_at": "2025-12-08T01:30:00Z",
          "processed_at": "2025-12-08T02:00:00Z",
          "video_id": "abc123xyz",
          "news_count": 8,
          "data_file": "2025-12-08.json"
        }
      ]
    },
    // ... previous 29 days
  ]
}
```

#### Daily News File
```json
// data/processed/2025-12-08.json
{
  "date": "2025-12-08",
  "broadcasts": [
    {
      "slot": "9PM",
      "video_id": "dQw4w9WgXcQ",
      "title": "9 PM | ETV Telugu News | 8th December 2024",
      "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
      "published_at": "2025-12-08T15:30:00Z",
      "processed_at": "2025-12-08T16:00:00Z",
      "duration_seconds": 3600,
      "news_items": [
        {
          "id": 1,
          "headline": "తెలంగాణలో నూతన విధానం ఆమోదం",
          "summary": "ముఖ్యమంత్రి రేవంత్ రెడ్డి నూతన విధానము ప్రవేశపెట్టారు...",
          "category": "రాజకీయం",
          "timestamp_start": "00:02:15",
          "timestamp_end": "00:05:30"
        },
        {
          "id": 2,
          "headline": "హైదరాబాద్‌లో భారీ వర్షాలు",
          "summary": "హైదరాబాద్ మరియు ప్రాంతాలలో భారీ వర్షాలు...",
          "category": "వాతావరణం",
          "timestamp_start": "00:05:35",
          "timestamp_end": "00:08:20"
        }
        // ... 10 more news items
      ]
    },
    {
      "slot": "7AM",
      "video_id": "abc123xyz",
      // ... similar structure
    }
  ]
}
```

#### Frontend Data Loading (Zero Latency)
```javascript
// js/utils/data-loader.js

/**
 * Load master index (sidebar population)
 */
export async function loadIndex() {
  const response = await fetch('data/processed/index.json');
  return response.json(); // < 50ms typically
}

/**
 * Load specific day's news (instant click response)
 */
export async function loadDayNews(date) {
  const response = await fetch(`data/processed/${date}.json`);
  return response.json(); // < 50ms typically
}

/**
 * No API calls. No waiting. Just read files.
 */
```

#### Weekly Cleanup Automation
```yaml
# .github/workflows/cleanup-old-data.yml
name: Cleanup Old News Data

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday midnight
  workflow_dispatch:

jobs:
  cleanup:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Remove data older than 30 days
        run: |
          cd data/processed
          find . -name '*.json' -type f -mtime +30 -delete
          python ../../scripts/update_index.py  # Rebuild index
      - name: Commit changes
        run: |
          git config user.name "ETV News Bot"
          git config user.email "actions@github.com"
          git add data/processed/
          git commit -m "chore: cleanup data older than 30 days"
          git push
```

## API Integration Standards

### API Integration Architecture

#### 1. YouTube Data API (Video Discovery)

**Purpose**: Fetch daily 9 PM and 7 AM news videos from ETV Telugu News channel

```javascript
// YouTube Data API v3 - Search for videos
const YOUTUBE_API_ENDPOINT = 'https://www.googleapis.com/youtube/v3/search';
const ETV_CHANNEL_ID = 'UC_RIp9SfWPoellpXGBvd4jg'; // ETV Telugu News official

const searchParams = {
  part: 'snippet',
  channelId: ETV_CHANNEL_ID,
  type: 'video',
  order: 'date',
  maxResults: 10,
  publishedAfter: new Date().toISOString().split('T')[0] + 'T00:00:00Z', // Today
  q: '9 PM | ETV Telugu News OR 7 AM | ETV Telugu News',
  key: YOUTUBE_API_KEY
};

// Filter exact title matches
const validTitlePatterns = [
  /^9 PM \| ETV Telugu News \| \d{1,2}(st|nd|rd|th) [A-Za-z]+ \d{4}$/i,
  /^7 AM \| ETV Telugu News \| \d{1,2}(st|nd|rd|th) [A-Za-z]+ \d{4}$/i
];

const isValidETVNewsVideo = (video) => {
  const title = video.snippet.title;
  return validTitlePatterns.some(pattern => pattern.test(title));
};
```

#### 2. Gemini API (Video Processing)

**Purpose**: Process video content and extract Telugu news summaries

```javascript
// Gemini API - Video file upload and analysis
const GEMINI_API_ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta';
const MODEL = 'gemini-1.5-pro'; // Supports video processing

// Step 1: Upload video file to Gemini
const uploadVideoFile = async (videoUrl) => {
  const response = await fetch(`${GEMINI_API_ENDPOINT}/files`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GEMINI_API_KEY}`
    },
    body: JSON.stringify({
      file: {
        uri: videoUrl // YouTube video URL or downloaded file
      }
    })
  });
  return response.json(); // Returns { name: 'files/abc123', uri: '...' }
};

// Step 2: Process video with prompt
const processVideoWithGemini = async (fileData) => {
  const prompt = `
Analyze this ETV Telugu News broadcast and extract all news items.

For each news story, provide:
1. Headline in Telugu
2. Brief summary in Telugu (2-3 sentences)
3. Category (e.g., రాజకీయం, అంతర్జాతీయం, క్రీడలు, సినిమా)
4. Approximate timestamp in video (MM:SS)

Format response as JSON array:
[
  {
    "headline": "తెలుగు వార్త శీర్షిక",
    "summary": "విస్తృత సారాంశం...",
    "category": "రాజకీయం",
    "timestamp": "02:15"
  }
]
`;

  const response = await fetch(`${GEMINI_API_ENDPOINT}/models/${MODEL}:generateContent`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${GEMINI_API_KEY}`
    },
    body: JSON.stringify({
      contents: [
        {
          parts: [
            { text: prompt },
            { file_data: { file_uri: fileData.uri, mime_type: 'video/*' } }
          ]
        }
      ]
    })
  });
  
  return response.json();
};
```

#### 3. Response Structure

```javascript
// Success: Processed news data
{
  videoId: 'dQw4w9WgXcQ',
  title: '9 PM | ETV Telugu News | 8th December 2024',
  publishedAt: '2024-12-08T15:30:00Z',
  channelTitle: 'ETV Telugu News',
  processedAt: '2024-12-08T16:00:00Z',
  newsItems: [
    {
      headline: 'తెలంగాణలో నూతన విధానం ఆమోదం',
      summary: 'ముఖ్యమంత్రి రేవంత్ రెడ్డి నూతన విధానము ప్రవేశపెట్టారు...',
      category: 'రాజకీయం',
      timestamp: '02:15'
    },
    // ... more news items
  ]
}

// Error response structure
{
  error: {
    code: 'RATE_LIMIT_EXCEEDED',
    message: 'API rate limit reached',
    retryAfter: 3600 // seconds
  }
}
```

### Error Categories & Telugu Messages

| Error Code | English Meaning | Telugu Message |
|------------|-----------------|----------------|
| `INVALID_CHANNEL` | Not ETV Telugu News channel | ఇది ETV తెలుగు వార్తల చ్యానల్ కాదు |
| `INVALID_VIDEO_TITLE` | Title doesn't match 9 PM or 7 AM pattern | వీడియో శీర్షిక 9 PM లేదా 7 AM వార్తల ఫార్మాట్‌లో లేదు |
| `NO_VIDEOS_FOUND` | No videos found for today | ఈ రోజు వీడియోలు కనపడలేదు |
| `VIDEO_PROCESSING_FAILED` | Gemini video processing failed | వీడియో ప్రాసెసింగ్ విఫలమయ్యింది |
| `RATE_LIMIT_EXCEEDED` | Too many requests | చాలా అభ్యర్థనలు. కొంత సమయం తర్వాత ప్రయత్నించండి |
| `API_ERROR` | Gemini API failure | సర్వర్ సమస్య. కొన్ని నిమిషాల తర్వాత ప్రయత్నించండి |
| `NETWORK_ERROR` | No internet connection | ఇంటర్నెట్ కనెక్షన్ లేదు. దయచేసి తనిఖీ చేయండి |
| `PARSE_ERROR` | Cannot parse video content | వీడియో నుండి వార్తలను విశ్లేషించలేకపోయాము |

### Security Best Practices
1. **Never commit API keys**: Use `.env` files (gitignored) for both Gemini and YouTube API keys
2. **Environment variable access**:
   ```javascript
   const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';
   const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || '';
   
   if (!GEMINI_API_KEY || !YOUTUBE_API_KEY) {
     throw new Error('API keys not configured');
   }
   ```
3. **Client-side key handling**: For GitHub Pages, use GitHub Secrets + Actions for daily automation
4. **Channel validation**: Whitelist only ETV Telugu News channel ID
5. **Title validation**: Strict regex patterns for 9 PM and 7 AM news
6. **Rate limiting**: Implement exponential backoff for both YouTube and Gemini APIs
7. **Video source verification**: Only process videos from verified ETV Telugu News channel

## Telugu Language Considerations

### Typography Standards
- **Primary font**: 'Noto Sans Telugu' (Google Fonts)
- **Fallback**: 'Pothana2000', 'Vemana2000', sans-serif
- **Line height**: 1.7 (Telugu needs more vertical space)
- **Font size**: Minimum 16px (mobile), 18px (desktop)
- **Letter spacing**: 0.02em for better readability

### CSS Configuration
```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap');

:root {
  --font-telugu: 'Noto Sans Telugu', 'Pothana2000', sans-serif;
  --font-size-base: 16px;
  --line-height-telugu: 1.7;
  --letter-spacing-telugu: 0.02em;
}

body {
  font-family: var(--font-telugu);
  font-size: var(--font-size-base);
  line-height: var(--line-height-telugu);
  letter-spacing: var(--letter-spacing-telugu);
}
```

### HTML Configuration
```html
<!DOCTYPE html>
<html lang="te">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>తెలుగు వార్తలు - Telugu News</title>
</head>
```

### Text Rendering Tests
Before deployment, verify Telugu text renders correctly:
- [ ] Chrome (Windows, Mac, Android)
- [ ] Firefox (Windows, Mac)
- [ ] Safari (Mac, iOS)
- [ ] Edge (Windows)

### Content Guidelines
- **Respectful language**: Avoid controversial or inflammatory Telugu translations
- **Formal vs. informal**: Use formal Telugu for news content
- **Diacritics**: Ensure proper rendering of vowel marks (మాత్రలు)

## GitHub Pages Deployment

### Deployment Process
1. **Branch**: Deploy from `main` branch
2. **Source directory**: `/` (root) or `/docs` if specified
3. **Custom domain**: Configure in repository settings (optional)
4. **HTTPS**: Enforce HTTPS (GitHub provides free SSL)

### Pre-Deployment Checklist
- [ ] All tests pass locally
- [ ] Manual testing complete
- [ ] No API keys in committed code
- [ ] `index.html` at repository root
- [ ] Relative paths for all assets (no absolute URLs)
- [ ] Meta tags configured (title, description, og:image)

### Deployment Workflow
```bash
# 1. Verify tests pass
npx playwright test

# 2. Commit changes
git add .
git commit -m "feat: add Telugu news parsing"

# 3. Push to GitHub
git push origin main

# 4. GitHub Pages auto-deploys (2-5 minutes)
# 5. Verify at: https://{username}.github.io/{repo-name}
```

### GitHub Actions (Optional Enhancement)
For automated testing on push:
```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm install
      - run: npx playwright install
      - run: npx playwright test
```

## Development Practices

### Branching Strategy (Spec Kit + Harness)
- **Main branch**: `main` (production, deployed to GitHub Pages)
- **Development branch**: `dev` (integration branch)
- **Feature branches**: Created by `/speckit.specify` (e.g., `001-youtube-parsing`)
- **Hotfix branches**: `hotfix/I{id}-{description}` (for urgent bugs)

### Commit Message Format
```
<type>: <short description>

<optional body>

<optional footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, CSS changes
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Build tasks, dependencies

**Examples**:
```
feat: add YouTube URL validation
fix: correct Telugu font rendering in Safari
docs: update API integration guide
test: add Playwright test for error modal
```

### Code Review Guidelines
- **Atomic commits**: One logical change per commit
- **Descriptive messages**: Explain "why" not just "what"
- **Self-review**: Re-read your changes before committing
- **Test coverage**: Every commit should pass existing tests

### Local Development
```bash
# Start local server
python -m http.server 8000
# or
npx serve .

# Run tests
npx playwright test

# Run specific test
npx playwright test tests/features/youtube-input.spec.ts

# Run in UI mode (debugging)
npx playwright test --ui
```

## Documentation Requirements

### Code Comments
- **When to comment**:
  - Complex algorithms or business logic
  - API integration points
  - Workarounds for browser bugs
  - Telugu-specific rendering hacks
- **When NOT to comment**:
  - Self-explanatory code
  - Obvious variable names

```javascript
// Good: Explains Telugu-specific logic
// Telugu text requires extra line-height for proper vowel mark rendering
const teluguLineHeight = 1.7;

// Bad: Redundant comment
// Set the title
const title = 'వార్త శీర్షిక';
```

### README Documentation
Required sections in `README.md`:
1. **Project overview** (English + Telugu)
2. **Setup instructions** (how to run locally)
3. **API configuration** (environment variables)
4. **Testing guide** (how to run tests)
5. **Deployment instructions** (GitHub Pages setup)
6. **Contributing guidelines**

### API Documentation
Maintain `docs/api-contract.md`:
- Gemini API endpoint
- Request/response formats
- Error codes and handling
- Rate limiting details

### Progress Documentation
Update `memory/claude-progress.md` after:
- Feature completion
- Bug discovery
- Session end (mandatory)

## How These Principles Drive Technical Decisions

This section explains how to apply the constitution during planning and implementation.

### Decision Framework

When evaluating any technical decision, ask these questions in order:

1. **Does it violate TDD?**
   - ❌ STOP: Writing implementation before tests fails → Rewrite approach
   - ✅ PROCEED: Test exists and fails → Continue

2. **Does it add dependencies?**
   - ❌ REJECT: New npm package without strong justification
   - ✅ ACCEPT: Vanilla JS/CSS solution or proven necessary library

3. **Does it require a build step?**
   - ❌ REJECT: Webpack, TypeScript, JSX require compilation
   - ✅ ACCEPT: Static HTML/CSS/JS deploy directly to GitHub Pages

4. **Is it mobile-first?**
   - ❌ REJECT: Desktop-only designs or 1200px base layouts
   - ✅ ACCEPT: 360px mobile design that scales up

5. **Does it handle Telugu correctly?**
   - ❌ REJECT: Generic fonts, improper line-height, hardcoded English errors
   - ✅ ACCEPT: Telugu fonts, proper rendering, localized messages

6. **Is it performant for 3G?**
   - ❌ REJECT: 500KB bundle, synchronous API calls, no caching
   - ✅ ACCEPT: < 150KB total, async operations, sessionStorage cache

7. **Is API key secure?**
   - ❌ REJECT: Hardcoded keys, committed `.env` files
   - ✅ ACCEPT: Environment variables, GitHub Secrets for deployment

### Example Decision Trees

#### Scenario 1: "Should we use React for this project?"

```
Question: Does it add dependencies?
→ YES: React adds react, react-dom (150KB+ gzipped)

Question: Does it require a build step?
→ YES: JSX requires Babel/Webpack compilation

Question: Is it necessary for core functionality?
→ NO: Vanilla JS can handle video fetching, API calls, DOM updates

Decision: ❌ REJECT React
Rationale: Violates "Simplicity First" and "Zero build process" principles
Alternative: Use vanilla JS with modular components
```

#### Scenario 1b: "Should we allow users to manually trigger video processing from the UI?"

```
Question: Does it violate automation-first principle?
→ YES: Constitution states "Zero API calls from browser during operation"

Question: Does it require API keys in frontend?
→ YES: Would need to expose YouTube + Gemini keys (SECURITY VIOLATION)

Question: What is the user waiting for?
→ Processing takes 2-5 minutes per video (BAD UX)

Question: What does constitution say?
→ "The UI never waits for processing. All heavy lifting happens in background automation."

Decision: ❌ REJECT manual trigger UI button
Rationale: Violates "Zero-Latency Frontend Principle" and security best practices
Implementation: 
  - GitHub Actions runs automatically on schedule
  - Users see pre-processed data instantly
  - Manual trigger via GitHub Actions UI only (for admins/testing)
Alternative: Show "Last updated: 10:05 PM IST" timestamp, no manual button
```

#### Scenario 1c: "Should we use Node.js for the backend processing?"

```
Question: Does Python have better API support?
→ YES: google-api-python-client and google-generativeai are official SDKs

Question: Does it require additional setup?
→ Node.js would work, but Python is GitHub Actions' default language

Question: What does the team know?
→ Python more common for data processing/ML workflows

Question: Is there a strong reason to use Node.js?
→ NO: Frontend already vanilla JS, no code sharing benefit

Decision: ✅ USE Python for backend
Rationale: 
  - Official Google API SDKs
  - Better for video/ML processing
  - GitHub Actions native support
  - Clear separation: JS=frontend, Python=backend
Implementation: scripts/*.py with requirements.txt
```

#### Scenario 2: "Should we use Playwright or Cypress for testing?"

```
Question: Does it violate TDD?
→ NO: Both support TDD workflows

Question: Which is the framework default?
→ Playwright (per libraries.instructions.md)

Question: Is there a compelling reason to override?
→ NO: Playwright meets all requirements

Decision: ✅ ACCEPT Playwright
Rationale: Framework default, excellent browser support, project standard
```

#### Scenario 3: "How should we handle API rate limiting?"

```
Question: Is it performant for 3G?
→ Exponential backoff reduces wasted requests on slow networks

Question: Does it handle errors gracefully?
→ YES: Telugu error message + retry logic

Question: Does it improve UX?
→ YES: User sees "కొంత సమయం తర్వాత ప్రయత్నించండి" instead of hard failure

Decision: ✅ IMPLEMENT exponential backoff with Telugu error messages
Implementation:
- Client-side retry: 1s, 2s, 4s, 8s delays
- Store retry count in sessionStorage
- Display Telugu message: "చాలా అభ్యర్థనలు. 4 సెకన్లలో మళ్ళీ ప్రయత్నిస్తాం"
```

#### Scenario 4: "Should we store parsed news in localStorage or sessionStorage?"

```
Question: What are the security implications?
→ localStorage persists across sessions (privacy concern for news reading history)
→ sessionStorage clears on tab close (better for privacy)

Question: What are the UX implications?
→ News should be fresh on each visit, not cached indefinitely

Question: What does the constitution say about data handling?
→ "Parsed news data stored in browser session only"

Decision: ✅ USE sessionStorage
Rationale: Aligns with "No external database required for MVP" and privacy-first approach
```

### Planning Phase Guidelines

When creating specifications (`/speckit.specify`):

1. **Start with the constitution**
   - Read `memory/constitution.md` before writing spec
   - Ensure spec aligns with core principles
   - Reference specific principles in spec rationale

2. **Identify potential violations early**
   - Flag any dependencies that need justification
   - Note performance concerns upfront
   - Plan for Telugu language requirements

3. **Design for TDD**
   - Write testable acceptance criteria
   - Define test scenarios before implementation plan
   - Ensure each feature has measurable pass/fail

### Implementation Phase Guidelines

When implementing features (`@Coder`):

1. **TDD Gate Enforcement**
   ```
   BEFORE touching implementation files:
   □ Read feature description
   □ Write test in tests/features/{feature}.spec.ts
   □ Run test → verify FAILS
   □ Update feature_list.json: test_fails_before = true
   
   ONLY AFTER test fails:
   □ Write minimal implementation
   □ Run test → verify PASSES
   □ Update feature_list.json: test_passes_after = true, passes = true
   ```

2. **Simplicity Checkpoint**
   - Can this be done with vanilla JS? → Do that first
   - Is this CSS custom property reusable? → Add to `:root`
   - Can this component be < 50 lines? → Refactor if needed

3. **Telugu Verification**
   - Does this display text? → Use Telugu error messages
   - Does this render Telugu? → Test in 3 browsers
   - Does this measure text? → Account for Telugu line-height

4. **Performance Monitoring**
   - Add console timing: `console.time('API Call')` / `console.timeEnd('API Call')`
   - Check Network tab: Total payload < 150KB?
   - Test on throttled 3G: First paint < 1.5s?

### Code Review Self-Checklist

Before committing any code:

- [ ] **TDD**: Test written first, failed before implementation, passes after
- [ ] **No dependencies**: Added zero npm packages (or justified if necessary)
- [ ] **No build step**: Code runs directly in browser without compilation
- [ ] **Mobile-first**: Tested at 360px viewport
- [ ] **Telugu rendering**: Verified font, line-height, error messages
- [ ] **Performance**: Checked bundle size, API response times
- [ ] **Security**: No API keys in code, environment variables used
- [ ] **Accessibility**: Keyboard nav works, ARIA labels present
- [ ] **Documentation**: README updated if API changed
- [ ] **Progress notes**: `memory/claude-progress.md` updated

### Conflict Resolution

If principles conflict, prioritize in this order:

1. **TDD** - Non-negotiable, always enforced
2. **Security** - API keys, user data protection
3. **Simplicity** - Fewer dependencies over features
4. **Performance** - Load time for Indian networks
5. **Telugu UX** - Proper rendering and localization
6. **Accessibility** - Keyboard, screen reader support
7. **Nice-to-have features** - Only after core is solid

### Example: "Add animations to news cards"

```
Evaluation:
1. Does it violate TDD? → NO (can write animation test)
2. Does it impact performance? → YES (CSS animations add 2KB, delay FCP)
3. Is it mobile-friendly? → MAYBE (touch devices less reliable with hover)
4. Does it improve Telugu readability? → NO (purely decorative)

Priority Check:
- Core functionality (parsing, display) works? → If NO, defer animations
- Performance budget met? → If NO (close to 150KB), defer animations
- All critical features done? → If NO, defer animations

Decision: DEFER animations until after MVP launch
Rationale: Performance (priority 4) outweighs nice-to-have features (priority 7)
Add to backlog for post-launch enhancement
```

## Agent Behavior Guidelines

### When Starting Work
1. Read this constitution in full
2. Identify which principles apply to current task
3. Check `memory/claude-progress.md` for context
4. Review `memory/feature_list.json` for related features

### During Implementation
1. Reference constitution principles in commit messages
2. Document decision rationale in progress notes
3. Flag principle violations immediately
4. Update constitution if principles evolve

### When Uncertain
1. Ask: "Which principle does this serve?"
2. Check: "Does this align with project vision?"
3. Prefer: Simplicity over cleverness
4. Default: Follow the constitution, ask user if unclear

---

## Complete Automation Workflow

### Daily Processing Pipeline (End-to-End)

```
┌────────────────────────────────────────────────────────┐
│  10:00 PM IST (Daily) - GitHub Actions Triggered            │
└────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────┐
│  Step 1: YouTube Video Discovery                            │
│  - Call YouTube Data API v3                                 │
│  - Search ETV Telugu News channel (hardcoded ID)            │
│  - Filter by date (publishedAfter: today 00:00)             │
│  - Filter by title (regex: "9 PM | ETV Telugu News")        │
│  - Validate channel ID matches ETV official                 │
│  - Extract: video_id, title, thumbnail, published_at        │
└────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────┐
│  Step 2: Gemini Video Processing (per video)                │
│  - Upload video to Gemini API (file_data)                   │
│  - Prompt: "Extract Telugu news summaries"                  │
│  - Parse response: headlines, summaries, categories         │
│  - Extract timestamps (MM:SS format)                        │
│  - Retry 3 times with exponential backoff on failure        │
└────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────┐
│  Step 3: JSON File Generation                               │
│  - Create: data/processed/2025-12-08.json                   │
│  - Structure: { date, broadcasts: [{ 9PM, 7AM }] }          │
│  - Update: data/processed/index.json                        │
│  - Add entry to master index                                │
└────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────┐
│  Step 4: Git Commit & Push                                  │
│  - git add data/processed/                                  │
│  - git commit -m "chore: process news for 2025-12-08"       │
│  - git push origin main                                     │
└────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────┐
│  Step 5: GitHub Pages Auto-Deploy                           │
│  - GitHub detects push to main branch                       │
│  - Triggers Pages deployment (automatic)                    │
│  - Site updates within 1-2 minutes                          │
│  - Users see fresh data on next visit                       │
└────────────────────────────────────────────────────────┘

**Total Time**: ~3-5 minutes per video (2 videos/day = 6-10 minutes total)
**User Impact**: Zero - all processing happens before user visits
**Manual Steps**: Zero - fully automated
```

### Error Handling & Notifications

**Failure Scenarios**:
1. **YouTube API failure**: Retry 3 times, then email alert
2. **Gemini API failure**: Retry 3 times, then email alert
3. **No videos found**: Log warning, no alert (expected on some days)
4. **Invalid video format**: Skip video, continue processing others
5. **Git push failure**: Retry once, then email alert

**Notification Email Template**:
```
Subject: ⚠️ ETV News Processing Failed - 2025-12-08

Workflow: process-news.yml
Date: 2025-12-08
Time: 10:05 PM IST
Run ID: https://github.com/chaitanyame/telugu_news/actions/runs/123456

Error: Gemini API rate limit exceeded

Action Required:
- Check GitHub Actions logs
- Verify API quotas
- Manually trigger workflow_dispatch if needed

Last successful run: 2025-12-07 (9 PM)
```

### Monitoring & Maintenance

**Daily Checks** (automated):
- ✅ Workflow runs successfully
- ✅ JSON files generated
- ✅ Index updated
- ✅ GitHub Pages deployed

**Weekly Checks** (automated):
- ✅ Old data cleaned (> 30 days)
- ✅ Repository size under control

**Manual Checks** (monthly):
- API quota usage (YouTube, Gemini)
- Workflow performance (execution time trends)
- Error rate analysis

## Living Document

This constitution evolves with the project. When updating:

1. Use `/speckit.constitution` to regenerate
2. Document changes in git commit message
3. Update `memory/claude-progress.md` with rationale
4. Ensure all agents re-read before next session

Last updated: 2025-12-08

### Between Agents
- Provide complete handoff context
- Reference specific files and locations
- State clear success criteria
- Include rollback instructions

## Boundaries

### Agents Should
- Ask for clarification when uncertain
- Refuse clearly harmful requests
- Suggest alternatives when blocked
- Learn from feedback

### Agents Should Not
- Make assumptions about intent
- Execute without a plan
- Ignore project conventions
- Forget to checkpoint state

---

*This constitution may be amended as the project evolves. All agents must re-read this file when starting significant work.*

# Implementation Plan

**Feature Branch**: 001-etv-news-aggregator-automation  
**Specification**: [spec.md](spec.md)  
**Created**: 2025-12-08

## Specifications Covered
- [spec.md](spec.md) - ETV Telugu News Aggregation Website with Fully Automated Backend

## Implementation Philosophy

This plan follows the **Agent Harness Framework** with strict TDD enforcement:
- **One feature at a time** - No parallel implementation
- **Test-first mandatory** - Test must fail before implementation
- **Verify end-to-end** - Browser checks for UI, pytest for backend
- **Update feature_list.json** - Only change `passes` field
- **Commit frequently** - After each passing feature

## Implementation Phases

### Phase 1: Project Foundation & Data Structure
**Goal**: Establish repository structure, data models, and testing infrastructure  
**Duration**: 1-2 sessions  
**Priority**: Critical - blocks all other work

#### Tasks

1. **Create directory structure**
   - Create `data/` directory for JSON storage
   - Create `data/cache/` for video ID cache
   - Create `data/archive/YYYY-MM/` pattern for historical data
   - Create `scripts/` for Python automation
   - Create `scripts/utils/` for shared utilities
   - Create `tests/backend/` for pytest tests
   - Create `tests/frontend/` for Playwright tests
   - Create `.github/workflows/` for GitHub Actions
   - **Depends on**: None
   - **Complexity**: Low
   - **Test**: Verify directories exist with `ls -R`

2. **Setup Python environment**
   - Create `scripts/requirements.txt` with dependencies:
     - `google-api-python-client==2.100.0`
     - `google-generativeai==0.3.0`
     - `requests==2.31.0`
     - `tenacity==8.2.3`
     - `pytest==7.4.0`
   - Create `scripts/setup.py` for development setup
   - **Depends on**: Directory structure
   - **Complexity**: Low
   - **Test**: `pip install -r requirements.txt` succeeds

3. **Define JSON schema and validator**
   - Create `scripts/utils/validators.py`
   - Implement `validate_news_file(data: dict) -> bool`
   - Implement `validate_date_format(date_str: str) -> bool`
   - Implement `validate_video_id(video_id: str) -> bool`
   - Write pytest tests: `tests/backend/test_validators.py`
   - **Depends on**: Python environment
   - **Complexity**: Low
   - **TDD**: Write test first, verify failure, implement, verify pass
   - **Test file**: `tests/backend/test_validators.py`

4. **Create configuration manager**
   - Create `scripts/utils/config.py`
   - Define constants:
     - `ETV_CHANNEL_ID = "UCJi8M0hRKjz8SLPvJKEVTOg"`
     - `VIDEO_PATTERN_9PM = r"^9 PM \| ETV Telugu News \|"`
     - `VIDEO_PATTERN_7AM = r"^7 AM \| ETV Telugu News \|"`
     - `DATA_RETENTION_DAYS = 30`
   - Load secrets from environment variables
   - Write pytest tests: `tests/backend/test_config.py`
   - **Depends on**: Python environment
   - **Complexity**: Low
   - **TDD**: Write test first
   - **Test file**: `tests/backend/test_config.py`

---

### Phase 2: YouTube API Integration
**Goal**: Implement YouTube video search and metadata extraction  
**Duration**: 2-3 sessions  
**Priority**: High - required for data collection

#### Tasks

5. **Create YouTube API client wrapper**
   - Create `scripts/youtube_fetcher.py`
   - Implement `get_youtube_api_client(api_key: str) -> Resource`
   - Handle authentication errors gracefully
   - Write pytest tests with mocked API responses
   - **Depends on**: Config manager
   - **Complexity**: Medium
   - **TDD**: Write test first with mocked responses
   - **Test file**: `tests/backend/test_youtube_fetcher.py`

6. **Implement video search function**
   - In `scripts/youtube_fetcher.py`
   - Implement `search_channel_videos(client, channel_id, time_slot, date) -> dict`
   - Search by channel ID filter
   - Filter by title pattern (regex match)
   - Filter by publish date (within 24 hours of target)
   - Return: `{"video_id": str, "title": str, "published_at": str}`
   - Handle "no results found" case
   - Write pytest tests with mocked API responses
   - **Depends on**: YouTube API client wrapper
   - **Complexity**: High
   - **TDD**: Write test first with multiple scenarios
   - **Test file**: `tests/backend/test_youtube_fetcher.py`

7. **Implement video ID caching**
   - Create `scripts/utils/cache.py`
   - Implement `load_video_cache() -> dict`
   - Implement `save_video_cache(cache: dict) -> None`
   - Implement `is_video_processed(video_id: str) -> bool`
   - Implement `mark_video_processed(video_id: str, date: str) -> None`
   - Cache file: `data/cache/video-ids.json`
   - Write pytest tests for cache operations
   - **Depends on**: Directory structure
   - **Complexity**: Medium
   - **TDD**: Write test first
   - **Test file**: `tests/backend/test_cache.py`

---

### Phase 3: Gemini API Integration
**Goal**: Implement video processing and Telugu summarization  
**Duration**: 2-3 sessions  
**Priority**: High - core feature

#### Tasks

8. **Create Gemini API client wrapper**
   - Create `scripts/gemini_processor.py`
   - Implement `create_gemini_client(api_key: str) -> Client`
   - Handle authentication errors
   - Write pytest tests with mocked API
   - **Depends on**: Config manager
   - **Complexity**: Medium
   - **TDD**: Write test first
   - **Test file**: `tests/backend/test_gemini_processor.py`

9. **Implement video summarization function**
   - In `scripts/gemini_processor.py`
   - Implement `get_gemini_summary(video_url: str, api_key: str) -> list[str]`
   - Use `gemini-2.5-flash` model
   - Use `file_data` parameter with YouTube URL
   - Send Telugu prompt:
     ```
     విశ్లేషించి తెలుగులో 5-8 ముఖ్య వార్తా శీర్షికలు సంక్షిప్త వివరణతో తయారు చేయండి.
     Format as JSON array: ["వార్త 1", "వార్త 2"]
     ```
   - Parse JSON response
   - Validate response structure
   - Handle API errors (rate limit, invalid response)
   - Write pytest tests with mocked API responses
   - **Depends on**: Gemini API client wrapper
   - **Complexity**: High
   - **TDD**: Write test first with multiple scenarios
   - **Test file**: `tests/backend/test_gemini_processor.py`

10. **Implement retry logic with exponential backoff**
    - Create `scripts/utils/error_handler.py`
    - Implement `@retry_with_backoff` decorator using tenacity
    - Configuration: 3 retries, delays [1s, 2s, 4s]
    - Apply to YouTube and Gemini API calls
    - Write pytest tests for retry behavior
    - **Depends on**: YouTube and Gemini wrappers
    - **Complexity**: Medium
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_error_handler.py`

---

### Phase 4: JSON File Management
**Goal**: Implement data file creation, updates, and cleanup  
**Duration**: 2 sessions  
**Priority**: High - required for data persistence

#### Tasks

11. **Implement JSON file operations**
    - Create `scripts/json_generator.py`
    - Implement `load_or_create_news_file(date: str) -> dict`
    - Implement `save_news_file(date: str, data: dict) -> None`
    - Implement `update_news_slot(data: dict, slot: str, summary: list[str], video_data: dict) -> dict`
    - Handle file locking (prevent concurrent writes)
    - Write pytest tests for all operations
    - **Depends on**: JSON validator, directory structure
    - **Complexity**: Medium
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_json_generator.py`

12. **Implement index.json generator**
    - In `scripts/json_generator.py`
    - Implement `generate_index() -> None`
    - Scan `data/archive/` for all YYYY-MM-DD.json files
    - Build structure: `{"dates": [{"date": "2025-12-08", "slots": ["9pm", "7am"]}]}`
    - Sort by date descending (newest first)
    - Save to `data/index.json`
    - Write pytest tests
    - **Depends on**: JSON file operations
    - **Complexity**: Medium
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_json_generator.py`

13. **Implement data cleanup script**
    - Create `scripts/cleanup.py`
    - Implement `cleanup_old_files(days_to_keep: int = 30) -> None`
    - Delete files older than threshold
    - Preserve index.json and cache files
    - Log deleted files
    - Write pytest tests with temporary files
    - **Depends on**: JSON file operations
    - **Complexity**: Low
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_cleanup.py`

---

### Phase 5: Main Orchestrator Script
**Goal**: Integrate all components into main processing pipeline  
**Duration**: 2-3 sessions  
**Priority**: Critical - ties everything together

#### Tasks

14. **Create main processing script**
    - Create `scripts/process_daily_news.py`
    - Implement `main(time_slot: str, date: str) -> None`
    - Orchestration flow:
      1. Load config and secrets
      2. Check video ID cache
      3. Search YouTube for video
      4. Get Gemini summary
      5. Load/create news file
      6. Update news slot
      7. Save news file
      8. Update index.json
      9. Mark video as processed
    - Handle all error cases with graceful degradation
    - Write pytest tests with end-to-end mocking
    - **Depends on**: All Phase 2-4 components
    - **Complexity**: High
    - **TDD**: Write test first with full integration
    - **Test file**: `tests/backend/test_process_daily_news.py`

15. **Add command-line interface**
    - In `scripts/process_daily_news.py`
    - Use `argparse` for CLI arguments:
      - `--slot` (required): "9pm" or "7am"
      - `--date` (optional): YYYY-MM-DD (defaults to today)
      - `--force`: Bypass cache, reprocess video
    - Add `--dry-run` flag for testing
    - Write pytest tests for CLI parsing
    - **Depends on**: Main processing script
    - **Complexity**: Low
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_process_daily_news.py`

16. **Add logging and error reporting**
    - In `scripts/process_daily_news.py`
    - Configure Python logging module
    - Log levels: INFO for success, WARNING for retries, ERROR for failures
    - Output format: JSON for GitHub Actions parsing
    - Write logs to stdout (GitHub Actions captures)
    - Write pytest tests for log output
    - **Depends on**: Main processing script
    - **Complexity**: Low
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_process_daily_news.py`

---

### Phase 6: GitHub Actions Workflows
**Goal**: Automate daily processing with scheduled workflows  
**Duration**: 2 sessions  
**Priority**: Critical - enables automation

#### Tasks

17. **Create 9 PM news workflow**
    - Create `.github/workflows/process-9pm-news.yml`
    - Trigger: `cron: '30 3 * * *'` (9:00 AM IST)
    - Steps:
      1. Checkout repository
      2. Setup Python 3.11
      3. Install dependencies
      4. Run `python scripts/process_daily_news.py --slot 9pm`
      5. Commit changes if files modified
      6. Push to dev branch
    - Secrets: `YOUTUBE_API_KEY`, `GEMINI_API_KEY`
    - **Depends on**: Main processing script
    - **Complexity**: Medium
    - **TDD**: Manual workflow trigger test
    - **Test file**: Manual verification via GitHub UI

18. **Create 7 AM news workflow**
    - Create `.github/workflows/process-7am-news.yml`
    - Trigger: `cron: '30 17 * * *'` (11:00 PM IST)
    - Steps: Same as 9 PM workflow with `--slot 7am`
    - **Depends on**: Main processing script
    - **Complexity**: Medium
    - **TDD**: Manual workflow trigger test
    - **Test file**: Manual verification via GitHub UI

19. **Create weekly cleanup workflow**
    - Create `.github/workflows/cleanup-old-data.yml`
    - Trigger: `cron: '0 0 * * 0'` (Sunday midnight UTC)
    - Steps:
      1. Checkout repository
      2. Setup Python
      3. Run `python scripts/cleanup.py`
      4. Regenerate index.json
      5. Commit changes
      6. Push to dev branch
    - **Depends on**: Cleanup script
    - **Complexity**: Low
    - **TDD**: Manual workflow trigger test
    - **Test file**: Manual verification via GitHub UI

20. **Add manual workflow dispatch**
    - Update all workflows with `workflow_dispatch` trigger
    - Add inputs:
      - `date` (optional): Process specific date
      - `force` (boolean): Force reprocessing
    - Enable manual reruns from GitHub UI
    - **Depends on**: All workflows
    - **Complexity**: Low
    - **Test**: Trigger manual run via GitHub UI

---

### Phase 7: Frontend - HTML Structure
**Goal**: Build semantic HTML foundation  
**Duration**: 1 session  
**Priority**: High - required for all UI work

#### Tasks

21. **Create index.html with semantic structure**
    - Create `index.html`
    - Structure:
      - `<header>` with site title
      - `<main>` with `<aside>` (sidebar) and `<article>` (content)
      - `<footer>` with last updated timestamp
    - All text in Telugu
    - Meta tags: UTF-8, viewport, description
    - Link to Google Fonts (Noto Sans Telugu)
    - Write Playwright test: `tests/frontend/test_html_structure.spec.ts`
    - **Depends on**: None
    - **Complexity**: Low
    - **TDD**: Write test first (check elements exist)
    - **Test file**: `tests/frontend/test_html_structure.spec.ts`

22. **Add accessibility attributes**
    - Add ARIA labels in Telugu
    - Add `lang="te"` to HTML tag
    - Add skip-to-content link
    - Ensure keyboard navigation works
    - Write Playwright test for accessibility
    - **Depends on**: HTML structure
    - **Complexity**: Low
    - **TDD**: Write test first (check ARIA attributes)
    - **Test file**: `tests/frontend/test_accessibility.spec.ts`

---

### Phase 8: Frontend - CSS Styling
**Goal**: Implement responsive, mobile-first styles  
**Duration**: 2 sessions  
**Priority**: Medium - enhances UX

#### Tasks

23. **Create base CSS styles**
    - Create `css/main.css`
    - CSS custom properties for colors, spacing, typography
    - Reset default styles
    - Base typography with Noto Sans Telugu
    - Font sizes, line heights, letter spacing
    - Write Playwright test: verify styles apply
    - **Depends on**: HTML structure
    - **Complexity**: Low
    - **TDD**: Write test first (check computed styles)
    - **Test file**: `tests/frontend/test_styles.spec.ts`

24. **Implement mobile-first layout**
    - Create `css/layout.css`
    - Mobile (360px): Single column, sidebar at bottom
    - Tablet (768px): Sidebar slides in from left
    - Desktop (1024px): Sidebar fixed left (25% width)
    - Use CSS Grid or Flexbox
    - Write Playwright test with viewport changes
    - **Depends on**: Base CSS
    - **Complexity**: Medium
    - **TDD**: Write test first (check layout at breakpoints)
    - **Test file**: `tests/frontend/test_responsive_layout.spec.ts`

25. **Style sidebar component**
    - Create `css/sidebar.css`
    - Date list item styles
    - Hover effects, selected state
    - Checkmark icons for available slots
    - Scrollable list with fixed header
    - Write Playwright test for interactions
    - **Depends on**: Layout CSS
    - **Complexity**: Medium
    - **TDD**: Write test first (check hover, selection)
    - **Test file**: `tests/frontend/test_sidebar.spec.ts`

26. **Style news content area**
    - Create `css/news-display.css`
    - News card styling (shadow, border, padding)
    - Summary bullet points
    - YouTube button styling
    - Video thumbnail (if used)
    - Write Playwright test
    - **Depends on**: Layout CSS
    - **Complexity**: Medium
    - **TDD**: Write test first (check element styles)
    - **Test file**: `tests/frontend/test_news_display.spec.ts`

27. **Add dark mode support**
    - Update `css/main.css` with dark mode variables
    - Use `prefers-color-scheme` media query
    - Invert colors for dark mode
    - Test both modes in Playwright
    - **Depends on**: All CSS files
    - **Complexity**: Low
    - **TDD**: Write test first (check dark mode styles)
    - **Test file**: `tests/frontend/test_dark_mode.spec.ts`

---

### Phase 9: Frontend - JavaScript Data Loading
**Goal**: Implement data fetching and caching  
**Duration**: 2 sessions  
**Priority**: Critical - core frontend functionality

#### Tasks

28. **Create data loader utility**
    - Create `js/utils/data-loader.js`
    - Implement `async fetchIndex() -> object`
    - Implement `async fetchNewsForDate(date) -> object`
    - Add cache busting with timestamp query param
    - Handle fetch errors gracefully
    - Return fallback data on error
    - Write Playwright test with mocked fetch
    - **Depends on**: HTML structure
    - **Complexity**: Medium
    - **TDD**: Write test first (check fetch calls)
    - **Test file**: `tests/frontend/test_data_loader.spec.ts`

29. **Implement localStorage caching**
    - In `js/utils/data-loader.js`
    - Cache index.json in localStorage
    - Cache recent news files (last 7 days)
    - Implement cache invalidation (24 hour TTL)
    - Prefer cache over network for performance
    - Write Playwright test for cache behavior
    - **Depends on**: Data loader utility
    - **Complexity**: Medium
    - **TDD**: Write test first (check localStorage)
    - **Test file**: `tests/frontend/test_caching.spec.ts`

---

### Phase 10: Frontend - UI Components
**Goal**: Implement interactive UI components  
**Duration**: 3-4 sessions  
**Priority**: Critical - user-facing features

#### Tasks

30. **Create sidebar date list component**
    - Create `js/components/sidebar.js`
    - Implement `generateDateList(dates) -> HTMLElement`
    - Render list items with date, available slots
    - Add click handlers
    - Highlight today's date
    - Show checkmarks for available slots (9pm/7am)
    - Write Playwright test for rendering and interaction
    - **Depends on**: Data loader, HTML structure
    - **Complexity**: High
    - **TDD**: Write test first (check DOM generation)
    - **Test file**: `tests/frontend/test_sidebar_component.spec.ts`

31. **Create news display component**
    - Create `js/components/news-display.js`
    - Implement `renderNewsSection(sectionId, newsData, timeSlot) -> void`
    - Display video title
    - Render 5-8 bullet points
    - Add YouTube link button
    - Show timestamp
    - Handle missing data (show Telugu message)
    - Write Playwright test
    - **Depends on**: HTML structure
    - **Complexity**: High
    - **TDD**: Write test first (check rendering)
    - **Test file**: `tests/frontend/test_news_display_component.spec.ts`

32. **Create date formatter utility**
    - Create `js/utils/date-formatter.js`
    - Implement `formatDateDisplay(date) -> string`
    - Convert "2025-12-08" to "8 డిసెంబర్ 2025"
    - Support Telugu month names
    - Write Playwright test
    - **Depends on**: None
    - **Complexity**: Low
    - **TDD**: Write test first (check formatting)
    - **Test file**: `tests/frontend/test_date_formatter.spec.ts`

33. **Implement page initialization**
    - Create `js/app.js`
    - Implement `initializePage() -> void`
    - Load index.json
    - Generate sidebar date list
    - Load today's news by default
    - Set up event listeners
    - Handle URL parameters (optional date)
    - Write Playwright test for full page load
    - **Depends on**: All components, data loader
    - **Complexity**: High
    - **TDD**: Write test first (check initialization flow)
    - **Test file**: `tests/frontend/test_app_initialization.spec.ts`

34. **Implement date navigation**
    - In `js/app.js`
    - Implement `handleDateClick(date) -> void`
    - Clear previous content
    - Show loading indicator
    - Fetch news for selected date
    - Render news sections
    - Update URL (pushState)
    - Update "last updated" footer
    - Write Playwright test for navigation flow
    - **Depends on**: Page initialization, components
    - **Complexity**: Medium
    - **TDD**: Write test first (check navigation)
    - **Test file**: `tests/frontend/test_date_navigation.spec.ts`

35. **Add loading and error states**
    - In `js/app.js` and `js/components/news-display.js`
    - Show spinner during data fetch
    - Show Telugu error messages on failure:
      - "సమాచారం లేదు" (No data available)
      - "వార్తలు ప్రాసెస్ అవుతున్నాయి..." (Processing news)
      - "ఆ రోజు వార్తలు లేవు" (No news that day)
      - "వార్తలు ప్రాసెస్ చేయలేకపోయాం" (Processing failed)
    - Write Playwright test for all states
    - **Depends on**: News display component
    - **Complexity**: Medium
    - **TDD**: Write test first (check error messages)
    - **Test file**: `tests/frontend/test_loading_states.spec.ts`

---

### Phase 11: Integration & End-to-End Testing
**Goal**: Verify entire system works together  
**Duration**: 2-3 sessions  
**Priority**: Critical - ensures production readiness

#### Tasks

36. **Create end-to-end backend test**
    - Create `tests/backend/test_e2e_backend.py`
    - Mock YouTube and Gemini APIs
    - Run full processing pipeline
    - Verify JSON files created
    - Verify index.json updated
    - Verify cache updated
    - **Depends on**: All backend components
    - **Complexity**: High
    - **TDD**: Write test first
    - **Test file**: `tests/backend/test_e2e_backend.py`

37. **Create end-to-end frontend test**
    - Create `tests/frontend/test_e2e_frontend.spec.ts`
    - Test complete user journey:
      1. Load page
      2. Verify today's news displays
      3. Click different date in sidebar
      4. Verify news updates
      5. Test responsive breakpoints
      6. Test dark mode toggle
    - **Depends on**: All frontend components
    - **Complexity**: High
    - **TDD**: Write test first
    - **Test file**: `tests/frontend/test_e2e_frontend.spec.ts`

38. **Test GitHub Actions workflows locally**
    - Install `act` (GitHub Actions local runner)
    - Test each workflow with sample data
    - Verify commits work correctly
    - Check error handling
    - **Depends on**: All workflows
    - **Complexity**: Medium
    - **Test**: Manual verification with `act`

---

### Phase 12: Documentation & Deployment
**Goal**: Document system and deploy to production  
**Duration**: 1-2 sessions  
**Priority**: Medium - required for launch

#### Tasks

39. **Write README.md**
    - Create comprehensive README with:
      - Project overview
      - Architecture diagram
      - Setup instructions
      - API key configuration
      - Deployment guide
      - Contributing guidelines
    - **Depends on**: None
    - **Complexity**: Low
    - **Test**: Manual review

40. **Configure GitHub Secrets**
    - Add `YOUTUBE_API_KEY` to repository secrets
    - Add `GEMINI_API_KEY` to repository secrets
    - Document secret rotation process
    - **Depends on**: None
    - **Complexity**: Low
    - **Test**: Verify workflow can access secrets

41. **Configure GitHub Pages**
    - Enable GitHub Pages on dev branch
    - Set source to root directory
    - Add custom domain (if applicable)
    - Test deployment
    - **Depends on**: Frontend complete
    - **Complexity**: Low
    - **Test**: Visit GitHub Pages URL

42. **Create monitoring dashboard**
    - Document how to monitor:
      - Workflow success rate
      - API quota usage
      - Page performance (Lighthouse)
    - Set up email alerts for workflow failures
    - **Depends on**: Deployment
    - **Complexity**: Low
    - **Test**: Manual setup verification

---

### Phase 13: Performance Optimization (Optional Enhancement)
**Goal**: Optimize for best user experience  
**Duration**: 1-2 sessions  
**Priority**: Low - nice-to-have improvements

#### Tasks

43. **Optimize frontend performance**
    - Minify CSS and JavaScript
    - Add preconnect to Google Fonts
    - Use font-display: swap
    - Implement image lazy loading (if thumbnails added)
    - Run Lighthouse audit, fix issues
    - **Depends on**: Frontend complete
    - **Complexity**: Low
    - **Test**: Lighthouse score > 90

44. **Add service worker for offline support**
    - Create `sw.js` service worker
    - Cache static assets (HTML, CSS, JS)
    - Cache recent JSON files
    - Show offline indicator when network unavailable
    - **Depends on**: Frontend complete
    - **Complexity**: Medium
    - **TDD**: Write test first (check caching)
    - **Test file**: `tests/frontend/test_service_worker.spec.ts`

45. **Add analytics (privacy-respecting)**
    - Implement simple analytics:
      - Page views per date
      - Most viewed news days
      - User timezone distribution
    - Use privacy-respecting solution (no cookies)
    - **Depends on**: Deployment
    - **Complexity**: Low
    - **Test**: Manual verification

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **YouTube API quota exceeded** | Medium | High | Implement aggressive caching, monitor usage, use exponential backoff |
| **Gemini API fails to process video** | Low | High | Retry logic with backoff, graceful degradation, show "processing" message |
| **ETV changes video title pattern** | Low | High | Implement fuzzy title matching, alert on multiple failures, manual fallback |
| **GitHub Actions minutes exceeded** | Low | Medium | Workflows are minimal (~5 min/day), monitor usage, reduce frequency if needed |
| **JSON file corruption** | Low | Medium | Validate before saving, keep backups in git history, auto-recovery script |
| **GitHub Pages deployment fails** | Low | High | Auto-retry on failure, manual deployment fallback, monitoring alerts |
| **Frontend breaks on old browsers** | Medium | Low | Use progressive enhancement, test on target browsers (last 2 versions) |
| **Telugu font not loading** | Low | Medium | Use font-display: swap, include fallback fonts, test on slow networks |
| **Data retention cleanup deletes wrong files** | Low | High | Dry-run mode, date validation before delete, test thoroughly |
| **Concurrent workflow runs conflict** | Low | Medium | Use GitHub Actions concurrency groups, file locking in scripts |

## Success Criteria

### Backend Automation
- [ ] Workflows run successfully on schedule (9 AM IST, 11 PM IST)
- [ ] Videos found and processed within 5 minutes of workflow start
- [ ] JSON files generated with correct structure and Telugu content
- [ ] Index.json updated automatically after each processing
- [ ] Old data cleaned up weekly (retain 30 days)
- [ ] Errors logged with actionable information
- [ ] API quotas stay under 80% usage

### Frontend Display
- [ ] Page loads in < 1.5s on 3G network (Lighthouse)
- [ ] All text displays correctly in Telugu (UTF-8)
- [ ] Sidebar shows last 30 days of available news
- [ ] Clicking date loads news instantly (< 200ms)
- [ ] Responsive design works on mobile (360px) to desktop (1920px)
- [ ] Dark mode works correctly with prefers-color-scheme
- [ ] Keyboard navigation works for all interactive elements
- [ ] WCAG AA accessibility compliance

### Testing & Quality
- [ ] All backend tests pass (pytest)
- [ ] All frontend tests pass (Playwright)
- [ ] Code coverage > 80% for backend
- [ ] No console errors in browser
- [ ] No broken links or 404s
- [ ] Manual workflow triggers work correctly

### Documentation
- [ ] README.md complete with setup instructions
- [ ] API key configuration documented
- [ ] Architecture diagram explains system flow
- [ ] Troubleshooting guide for common issues
- [ ] Contributing guidelines for future developers

## Open Decisions

### Resolved
- **IST to UTC conversion**: 9 AM IST = 3:30 UTC, 11 PM IST = 17:30 UTC ✅
- **Data structure**: Hybrid latest.json + archive/YYYY-MM/ with 30-day rotation ✅
- **Gemini API integration**: Use file_data with YouTube URL ✅
- **Frontend loading strategy**: index.json → on-demand date files ✅
- **Error handling**: 3 retries with exponential backoff, graceful degradation ✅

### Pending Phase 2 Enhancements (Not Blocking Launch)
- **Video thumbnails**: Should we display thumbnails? (adds complexity, YouTube API calls)
- **Share buttons**: Add social media sharing? (Telugu audience preference?)
- **Search functionality**: Search within news summaries? (adds complexity)
- **PWA features**: Full Progressive Web App with install prompt?
- **Multi-language support**: Add English translations?

## Estimated Timeline

**Total Duration**: 15-20 sessions (assuming 2-3 hours per session)

- **Phase 1-4 (Backend Foundation)**: 6-8 sessions
- **Phase 5-6 (Integration & Automation)**: 4-5 sessions
- **Phase 7-10 (Frontend)**: 6-8 sessions
- **Phase 11-12 (Testing & Deployment)**: 3-4 sessions
- **Phase 13 (Optional Enhancements)**: 2-3 sessions

**Critical Path**:
1. Backend infrastructure (Python scripts, API integration) - Phases 1-5
2. GitHub Actions automation - Phase 6
3. Frontend UI - Phases 7-10
4. Integration testing - Phase 11
5. Deployment - Phase 12

## Next Steps

1. **Run `/speckit.tasks`** to convert this plan into actionable tasks
2. **Run `/harness.generate`** to create feature_list.json
3. **Use `@Coder`** to implement features one at a time with TDD
4. **Update memory/claude-progress.md** after each session

## Notes

- **TDD is non-negotiable** - Every feature must have a failing test before implementation
- **One feature at a time** - Complete each task fully before moving to next
- **Commit frequently** - After each passing feature, commit to git
- **Verify end-to-end** - Browser checks for frontend, API mocks for backend
- **Document blockers** - Update claude-progress.md if stuck
- **Leave clean state** - No half-finished work at session end

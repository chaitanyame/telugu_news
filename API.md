# API Documentation - ETV Telugu News Aggregator

## Overview

The Telugu News Aggregator provides a simple JSON-based API for accessing aggregated news data from ETV Telugu channel.

## Data Structure

### Index File

**Location**: `/data/index.json`

```json
{
  "dates": ["2025-12-09", "2025-12-08", "2025-12-07"],
  "last_updated": "2025-12-09T17:15:00Z"
}
```

**Fields**:
- `dates` (array): List of dates with available news, sorted newest first (YYYY-MM-DD format)
- `last_updated` (string): ISO 8601 timestamp of last update

### News File

**Location**: `/data/{date}.json` (e.g., `/data/2025-12-09.json`)

```json
{
  "date": "2025-12-09",
  "news": [
    {
      "slot": "9pm",
      "video_id": "dQw4w9WgXcQ",
      "title": "ETV తెలుగు వార్తలు - 9 PM - డిసెంబర్ 9, 2025",
      "published_at": "2025-12-09T15:30:00Z",
      "summary": [
        "రాష్ట్ర ప్రభుత్వం కొత్త పథకాలను ప్రకటించింది",
        "వ్యవసాయ రంగంలో ముఖ్యమైన మార్పులు చేపట్టనున్నారు"
      ]
    }
  ]
}
```

**Fields**:
- `date` (string): Date of news in YYYY-MM-DD format
- `news` (array): Array of news items

**News Item Fields**:
- `slot` (string): Time slot - either "9pm" or "7am"
- `video_id` (string): YouTube video ID
- `title` (string): News bulletin title in Telugu
- `published_at` (string): ISO 8601 timestamp when video was published
- `summary` (array): Array of Telugu strings, each a news point from the bulletin

## JavaScript API

### DataLoader Module

Global module available as `window.DataLoader`.

#### `fetchIndex()`

Fetches the index file containing all available dates.

```javascript
const index = await DataLoader.fetchIndex();
// Returns: { dates: [], last_updated: '', error?: '' }
```

**Returns**:
- On success: `{ dates: string[], last_updated: string }`
- On error: `{ dates: [], last_updated: '', error: string }`

#### `fetchNewsForDate(date)`

Fetches news for a specific date.

```javascript
const news = await DataLoader.fetchNewsForDate('2025-12-09');
// Returns: { date: '', news: [], error?: '' }
```

**Parameters**:
- `date` (string): Date in YYYY-MM-DD format

**Returns**:
- On success: `{ date: string, news: NewsItem[] }`
- On error/404: `{ date: string, news: [], error: string }`

#### `fetchNewsForDates(dates)`

Batch fetch news for multiple dates.

```javascript
const allNews = await DataLoader.fetchNewsForDates(['2025-12-09', '2025-12-08']);
// Returns: Array of news objects
```

**Parameters**:
- `dates` (string[]): Array of dates in YYYY-MM-DD format

**Returns**:
- Array of news objects (same structure as `fetchNewsForDate`)

#### `fetchLatestNews()`

Fetches news for the most recent available date.

```javascript
const latest = await DataLoader.fetchLatestNews();
// Returns: { date: '', news: [], error?: '' }
```

**Returns**:
- Same structure as `fetchNewsForDate`

## App Module

Global module available as `window.App`.

#### `init()`

Initializes the application. Called automatically on page load.

```javascript
App.init();
```

#### `applyFilters()`

Applies current filter settings and re-renders news list.

```javascript
App.applyFilters();
```

#### `changePage(direction)`

Changes pagination page.

```javascript
App.changePage(1);  // Next page
App.changePage(-1); // Previous page
```

**Parameters**:
- `direction` (number): 1 for next page, -1 for previous page

## Cache Busting

All API requests include a cache-busting timestamp parameter:
```
/data/index.json?t=1702148700000
```

This ensures fresh data is always fetched, avoiding stale cached responses.

## Error Handling

The API uses graceful error handling:
- Network errors return fallback data with an `error` field
- 404 errors return empty arrays
- Malformed JSON returns empty arrays
- All errors are logged to console

Example error response:
```json
{
  "date": "2025-12-09",
  "news": [],
  "error": "Failed to fetch news"
}
```

## CORS

Static JSON files are served with appropriate CORS headers allowing cross-origin requests.

## Rate Limiting

No rate limiting is implemented for static JSON files.

## Data Updates

News data is automatically updated by GitHub Actions workflows:
- **9 PM News**: Runs daily at 9:00 AM IST (3:30 AM UTC)
- **7 AM News**: Runs daily at 11:00 PM IST (5:30 PM UTC)
- **Cleanup**: Runs weekly to archive old data

## File Retention

News files are retained for 30 days by default. Older files are archived and removed from the active data directory.

## Examples

### Fetch and Display Latest News

```javascript
async function displayLatestNews() {
  const data = await DataLoader.fetchLatestNews();
  
  if (data.error) {
    console.error('Error:', data.error);
    return;
  }
  
  data.news.forEach(item => {
    console.log(`${item.slot}: ${item.title}`);
    console.log(`YouTube: https://youtube.com/watch?v=${item.video_id}`);
    item.summary.forEach(point => console.log(`- ${point}`));
  });
}
```

### Filter News by Slot

```javascript
async function get9PMNews() {
  const index = await DataLoader.fetchIndex();
  const allNews = await DataLoader.fetchNewsForDates(index.dates);
  
  const eveningNews = allNews.flatMap(day => 
    day.news.filter(item => item.slot === '9pm')
  );
  
  return eveningNews;
}
```

### Get News for Date Range

```javascript
async function getNewsInRange(startDate, endDate) {
  const index = await DataLoader.fetchIndex();
  
  const datesInRange = index.dates.filter(date => 
    date >= startDate && date <= endDate
  );
  
  const news = await DataLoader.fetchNewsForDates(datesInRange);
  return news;
}
```

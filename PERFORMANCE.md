# Performance Optimization Guide

This document describes performance optimizations for the Telugu News Aggregator.

## Lighthouse Audit Results

Target scores:
- Performance: >90
- Accessibility: 100
- Best Practices: >95
- SEO: >95

## Frontend Optimizations

### 1. Asset Optimization

**Images**:
- No images currently used
- Future: Use WebP format, lazy loading

**Fonts**:
- ✅ Using Google Fonts with `display=swap`
- ✅ Preconnect to fonts.googleapis.com
- Consider: Self-host fonts for better control

**CSS**:
- ✅ Single CSS file (main.css)
- ✅ No unused CSS
- ✅ Mobile-first approach
- Consider: Critical CSS inline for above-the-fold content

**JavaScript**:
- ✅ No large frameworks (vanilla JS)
- ✅ Modular code (IIFE pattern)
- ✅ Event delegation for efficiency
- Consider: Minification for production

### 2. Caching Strategy

**Service Worker** (✅ Implemented):
- Cache First: Static assets (HTML, CSS, JS, fonts)
- Network First: Data files (JSON)
- Stale While Revalidate: Best of both worlds

**HTTP Caching**:
```
# Static assets (1 year)
Cache-Control: public, max-age=31536000, immutable

# Data files (1 hour)
Cache-Control: public, max-age=3600, must-revalidate

# HTML (10 minutes)
Cache-Control: public, max-age=600, must-revalidate
```

**localStorage**:
- Feature #29 (not yet implemented)
- Cache news data locally
- Expire after 24 hours

### 3. Loading Performance

**Critical Rendering Path**:
```html
<!DOCTYPE html>
<html lang="te">
<head>
  <!-- Critical meta tags -->
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- Preconnect to external domains -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  
  <!-- Critical CSS inline (future optimization) -->
  <style>/* Critical above-the-fold CSS */</style>
  
  <!-- Non-critical CSS -->
  <link rel="stylesheet" href="/css/main.css">
</head>
<body>
  <!-- Content -->
  
  <!-- Scripts at end of body -->
  <script src="/js/utils/data-loader.js"></script>
  <script src="/js/main.js"></script>
  <script src="/js/app.js"></script>
  
  <!-- Service worker registration -->
  <script src="/js/sw-register.js"></script>
</body>
</html>
```

**Resource Hints**:
```html
<!-- DNS prefetch for API domain -->
<link rel="dns-prefetch" href="https://api.yourdomain.com">

<!-- Preload critical resources -->
<link rel="preload" href="/css/main.css" as="style">
<link rel="preload" href="/js/app.js" as="script">

<!-- Prefetch likely next resources -->
<link rel="prefetch" href="/data/index.json">
```

### 4. Rendering Optimizations

**Virtualization**:
- Current: Show all news with pagination
- Future: Virtual scrolling for large lists

**Debouncing**:
```javascript
// Debounce filter changes
let filterTimeout;
function debouncedFilter() {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    filterNews();
  }, 300);
}
```

**Lazy Loading**:
```javascript
// Lazy load images when added
<img 
  src="placeholder.jpg" 
  data-src="actual-image.jpg" 
  loading="lazy"
  alt="Description"
>
```

## Backend API Optimizations

### 1. Response Compression

**Gzip Compression**:
```python
# Flask app config
from flask_compress import Compress

app = Flask(__name__)
Compress(app)
```

Or in deployment:
```
# Vercel: Automatic
# Netlify: Automatic
# Nginx:
gzip on;
gzip_types application/json text/css application/javascript;
```

### 2. API Response Optimization

**Pagination**:
- ✅ Implemented with limit/offset
- Default: 100 items max per request
- Consider: Cursor-based pagination for large datasets

**Field Selection**:
```python
# Allow clients to request specific fields
@app.route('/api/news')
def get_news():
    fields = request.args.get('fields', '').split(',')
    # Return only requested fields
```

**Response Caching**:
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/news')
@cache.cached(timeout=300, query_string=True)
def get_news():
    # Cached for 5 minutes
```

### 3. Database/File Optimization

**Index File**:
- ✅ Small index file for quick date lookup
- ✅ Separate files per date to avoid loading all data

**Data Structure**:
```json
{
  "date": "2025-12-09",
  "news": [
    {
      "id": "unique-id",  // Add for better caching
      "slot": "9pm",
      "video_id": "...",
      "title": "...",
      "summary": ["..."],
      "published_at": "..."
    }
  ]
}
```

## CDN Configuration

### Cloudflare (Recommended)

**Caching Rules**:
```
# Cache everything for 1 hour
Cache Level: Standard
Browser Cache TTL: 1 hour
Edge Cache TTL: 1 hour

# Always cache static assets
Rule: *.css, *.js, *.woff2
Cache Level: Cache Everything
Edge Cache TTL: 1 month

# Cache data files briefly
Rule: /data/*.json
Cache Level: Cache Everything
Edge Cache TTL: 5 minutes
```

**Performance Features**:
- ✅ Auto Minify: CSS, JS, HTML
- ✅ Brotli compression
- ✅ HTTP/2 and HTTP/3
- ✅ Image optimization (if images added)

## Monitoring Performance

### 1. Lighthouse CI

Add to GitHub Actions:
```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://your-domain.com
          uploadArtifacts: true
```

### 2. Web Vitals

Add to frontend:
```javascript
// Track Core Web Vitals
import {getCLS, getFID, getFCP, getLCP, getTTFB} from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
  // Send to analytics service
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### 3. Performance Budget

Set budgets:
```json
{
  "budgets": [
    {
      "resourceSizes": [
        {"resourceType": "document", "budget": 30},
        {"resourceType": "script", "budget": 100},
        {"resourceType": "stylesheet", "budget": 20},
        {"resourceType": "font", "budget": 50},
        {"resourceType": "total", "budget": 200}
      ]
    }
  ]
}
```

## Optimization Checklist

### Critical (Implemented)
- [x] Mobile-first responsive design
- [x] Efficient JavaScript (no frameworks)
- [x] Event delegation
- [x] Pagination for large datasets
- [x] Service worker for offline support
- [x] Semantic HTML
- [x] Accessibility optimizations

### High Priority
- [ ] Enable HTTP/2 or HTTP/3
- [ ] Configure CDN caching
- [ ] Add resource hints (preconnect, prefetch)
- [ ] Implement response compression
- [ ] Add Lighthouse CI to GitHub Actions

### Medium Priority
- [ ] Inline critical CSS
- [ ] Minify CSS and JavaScript
- [ ] Implement localStorage caching
- [ ] Add loading skeletons
- [ ] Optimize font loading

### Low Priority
- [ ] Virtual scrolling for long lists
- [ ] Bundle JavaScript modules
- [ ] Tree shaking (if adding dependencies)
- [ ] Image optimization (when images added)
- [ ] Progressive Web App manifest

## Expected Results

After implementing all optimizations:

**Performance Metrics**:
- First Contentful Paint (FCP): <1.0s
- Largest Contentful Paint (LCP): <2.5s
- Time to Interactive (TTI): <3.0s
- Total Blocking Time (TBT): <200ms
- Cumulative Layout Shift (CLS): <0.1

**Lighthouse Scores**:
- Performance: 95+
- Accessibility: 100
- Best Practices: 100
- SEO: 100

**User Experience**:
- Instant page loads on repeat visits (service worker)
- Offline support for previously viewed news
- Fast filtering and pagination (<100ms)
- Smooth animations (60 FPS)
- No layout shifts during loading

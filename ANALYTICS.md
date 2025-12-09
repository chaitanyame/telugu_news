# Privacy-Respecting Analytics Setup

This document describes the analytics setup for the Telugu News Aggregator.

## Analytics Philosophy

We prioritize user privacy:
- ✅ No cookies or tracking scripts
- ✅ No personal data collection
- ✅ No cross-site tracking
- ✅ GDPR/CCPA compliant by default
- ✅ Simple, aggregate metrics only

## Recommended: Plausible Analytics

### Why Plausible?

- Open source and transparent
- Privacy-focused (no cookies, GDPR compliant)
- Lightweight script (<1 KB)
- Simple, beautiful dashboard
- European-hosted option available
- No impact on performance

### Setup Instructions

1. **Create Plausible Account**
   - Go to [plausible.io](https://plausible.io)
   - Sign up (€9/month for 10k pageviews)
   - Add your domain

2. **Add Tracking Script**

Add to `index.html` before closing `</head>`:

```html
<!-- Plausible Analytics - Privacy-friendly -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

Or for self-hosted:
```html
<script defer data-domain="yourdomain.com" src="https://your-plausible-instance.com/js/script.js"></script>
```

3. **Custom Events** (Optional)

Track specific interactions:

```javascript
// Track news view
function trackNewsView(date, slot) {
  if (window.plausible) {
    plausible('News View', {
      props: {
        date: date,
        slot: slot
      }
    });
  }
}

// Track filter usage
function trackFilter(filterType) {
  if (window.plausible) {
    plausible('Filter Used', {
      props: {
        type: filterType
      }
    });
  }
}

// Track YouTube click
function trackYouTubeClick(videoId) {
  if (window.plausible) {
    plausible('YouTube Click', {
      props: {
        videoId: videoId
      }
    });
  }
}
```

4. **Add to App**

Update `js/app.js`:

```javascript
// In renderNews function, add click tracking
const youtubeBtn = card.querySelector('.youtube-btn');
youtubeBtn.addEventListener('click', () => {
  if (window.plausible) {
    plausible('YouTube Click', {
      props: {
        date: item.date,
        slot: item.slot
      }
    });
  }
});

// In filterNews function, add filter tracking
function filterNews() {
  // ... existing code ...
  
  if (window.plausible) {
    plausible('Filter Applied', {
      props: {
        dateFilter: selectedDate || 'all',
        slotFilter: selectedSlot
      }
    });
  }
}
```

### Metrics Tracked

**Automatic**:
- Page views
- Unique visitors
- Bounce rate
- Visit duration
- Top pages
- Top sources/referrers
- Countries (aggregate only)
- Devices (desktop/mobile/tablet)
- Browsers
- Operating systems

**Custom Events**:
- News views (by date/slot)
- Filter usage
- YouTube clicks
- Date navigation clicks

## Alternative: Simple Analytics

Similar to Plausible, slightly different pricing.

### Setup

```html
<script async defer src="https://scripts.simpleanalyticscdn.com/latest.js"></script>
<noscript><img src="https://queue.simpleanalyticscdn.com/noscript.gif" alt="" referrerpolicy="no-referrer-when-downgrade" /></noscript>
```

Cost: €19/month for 100k pageviews

## Alternative: Umami (Self-Hosted)

Free and open source, self-hosted option.

### Setup

1. Deploy Umami to Vercel/Railway:
   ```bash
   git clone https://github.com/umami-software/umami
   cd umami
   # Follow deployment instructions
   ```

2. Add tracking script:
   ```html
   <script async src="https://your-umami-instance.com/script.js" data-website-id="your-website-id"></script>
   ```

3. Track custom events:
   ```javascript
   if (window.umami) {
     umami.track('news-view', { date: '2025-12-09', slot: '9pm' });
   }
   ```

Cost: Free (hosting costs only, ~$5-10/month)

## Server-Side Analytics (Optional)

Track API usage without frontend analytics:

```python
# In api/app.py
from collections import Counter
import json
from datetime import datetime

# Simple in-memory analytics (use Redis for production)
analytics = {
    'requests': Counter(),
    'endpoints': Counter(),
    'errors': Counter()
}

@app.before_request
def log_request():
    """Log request for analytics."""
    endpoint = request.endpoint or 'unknown'
    analytics['requests'][datetime.now().date()] += 1
    analytics['endpoints'][endpoint] += 1

@app.route('/api/analytics')
def get_analytics():
    """Internal analytics endpoint."""
    # Protect with authentication in production
    return jsonify({
        'total_requests': sum(analytics['requests'].values()),
        'requests_by_date': dict(analytics['requests']),
        'requests_by_endpoint': dict(analytics['endpoints']),
        'total_errors': sum(analytics['errors'].values())
    })
```

## Metrics Dashboard

Key metrics to monitor:

### Engagement
- **Daily Active Users**: Track trends
- **Page Views per Visit**: Measure engagement
- **Bounce Rate**: Target <40%
- **Average Session Duration**: Target >2 minutes

### Content
- **Most Viewed Dates**: Identify popular news
- **Slot Preference**: 9pm vs 7am viewership
- **Filter Usage**: Are users filtering by slot?
- **YouTube Click Rate**: % of views that click YouTube

### Technical
- **Load Time**: From Plausible performance metrics
- **Error Rate**: From Sentry
- **API Response Time**: From server logs
- **Uptime**: From UptimeRobot

### Traffic Sources
- **Direct**: Bookmarks, direct URL entry
- **Referral**: Links from other sites
- **Social**: Facebook, Twitter, etc.
- **Search**: Google, Bing, etc.

## Privacy Policy

Include analytics disclosure in privacy policy:

```markdown
## Analytics

We use [Plausible Analytics] to understand how visitors use our site. 
Plausible is privacy-friendly and:

- Does not use cookies
- Does not collect personal data
- Does not track across websites
- Is fully GDPR compliant
- Does not share data with advertisers

We only collect aggregate data such as:
- Number of page views
- Number of unique visitors
- Top pages visited
- General location (country level only)

No individual user data is ever collected or stored.

You can opt out of analytics by enabling "Do Not Track" in your browser.
```

## Compliance

### GDPR (Europe)
- ✅ No personal data collection
- ✅ No consent banner needed (with Plausible/Simple)
- ✅ No cookies used
- ✅ Data processing agreement available from provider

### CCPA (California)
- ✅ No sale of personal information
- ✅ No personal data collected
- ✅ No opt-out mechanism required

### Cookie Law
- ✅ No cookies used
- ✅ No cookie banner required

## Cost Comparison

| Solution | Cost | Hosting | Privacy | Features |
|----------|------|---------|---------|----------|
| Plausible | €9/mo | Cloud | ⭐⭐⭐⭐⭐ | Excellent |
| Simple Analytics | €19/mo | Cloud | ⭐⭐⭐⭐⭐ | Excellent |
| Umami | $5-10/mo | Self-host | ⭐⭐⭐⭐⭐ | Good |
| Google Analytics | Free | Cloud | ⭐⭐ | Excellent |
| No Analytics | $0 | N/A | ⭐⭐⭐⭐⭐ | None |

**Recommendation**: Start with Plausible for best balance of privacy, features, and ease of use.

## Implementation Checklist

- [ ] Choose analytics provider (Plausible recommended)
- [ ] Create account and add domain
- [ ] Add tracking script to index.html
- [ ] Test that analytics are recording
- [ ] Add custom event tracking (optional)
- [ ] Create analytics dashboard bookmark
- [ ] Update privacy policy with analytics disclosure
- [ ] Set up weekly analytics review
- [ ] Document key metrics to track

## Testing Analytics

```javascript
// Test that Plausible is loaded
console.log('Plausible loaded:', typeof window.plausible !== 'undefined');

// Test custom event
if (window.plausible) {
  plausible('Test Event', { props: { test: 'value' } });
  console.log('Test event sent');
}

// Check for Do Not Track
if (navigator.doNotTrack === '1') {
  console.log('Do Not Track enabled - analytics disabled');
}
```

## Resources

- [Plausible Documentation](https://plausible.io/docs)
- [Simple Analytics Documentation](https://docs.simpleanalytics.com/)
- [Umami Documentation](https://umami.is/docs)
- [GDPR Compliance Guide](https://gdpr.eu/)
- [Privacy-First Analytics Comparison](https://github.com/privacy-first/analytics)

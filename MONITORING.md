# Monitoring and Alerts Configuration

This document describes the monitoring setup for the ETV Telugu News Aggregator.

## Error Tracking - Sentry

### Setup Instructions

1. **Create Sentry Account**
   - Go to [sentry.io](https://sentry.io)
   - Sign up for free account
   - Create new project (Python/Flask)
   - Copy your DSN

2. **Configure Backend**
   ```bash
   # Install Sentry SDK
   pip install sentry-sdk[flask]
   
   # Add to api/requirements.txt
   echo "sentry-sdk[flask]==1.39.0" >> api/requirements.txt
   ```

3. **Update API Code**
   ```python
   # In api/app.py, add at the top:
   from api.sentry_config import init_sentry
   
   # After app = Flask(__name__)
   init_sentry(app)
   ```

4. **Set Environment Variable**
   ```bash
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/your-project-id
   ```

5. **Test Error Tracking**
   ```bash
   # Add test endpoint to api/app.py
   @app.route('/api/sentry-debug')
   def trigger_error():
       division_by_zero = 1 / 0
   ```

### Frontend Integration

Add to `index.html` before other scripts:

```html
<script
  src="https://js.sentry-browser.com/7.x.x/bundle.min.js"
  crossorigin="anonymous"
></script>

<script>
  Sentry.init({
    dsn: "YOUR_SENTRY_DSN_HERE",
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay(),
    ],
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    environment: "production",
  });
</script>
```

## Uptime Monitoring - UptimeRobot

### Setup Instructions

1. **Create UptimeRobot Account**
   - Go to [uptimerobot.com](https://uptimerobot.com)
   - Sign up for free account (50 monitors included)

2. **Add Monitors**
   
   **Main Site Monitor:**
   - Monitor Type: HTTP(s)
   - Friendly Name: Telugu News Aggregator - Main Site
   - URL: `https://your-domain.com/`
   - Monitoring Interval: 5 minutes
   - Monitor Timeout: 30 seconds
   - HTTP Status: 200

   **API Health Check:**
   - Monitor Type: HTTP(s)
   - Friendly Name: Telugu News API - Health
   - URL: `https://your-domain.com/api/health`
   - Monitoring Interval: 5 minutes
   - Keyword: "healthy"

   **Data Availability:**
   - Monitor Type: HTTP(s)
   - Friendly Name: Telugu News - Data Check
   - URL: `https://your-domain.com/api/news/latest`
   - Monitoring Interval: 15 minutes
   - Keyword: "news"

3. **Configure Alerts**
   - Go to My Settings > Alert Contacts
   - Add email alert
   - Add SMS (premium) or webhook for critical alerts
   - Configure alert timing:
     - Send alert when down
     - Re-alert if still down: Every 30 minutes
     - Send notification when up

4. **Add Status Badge**
   
   Add to README.md:
   ```markdown
   ![Uptime Status](https://img.shields.io/uptimerobot/status/your-monitor-id)
   ```

5. **Public Status Page** (Optional)
   - Create public status page
   - Add all monitors
   - Share URL: `https://stats.uptimerobot.com/your-page-id`

## GitHub Actions Monitoring

### Workflow Status Checks

Monitor GitHub Actions workflows:

1. **Enable Workflow Notifications**
   - Go to Settings > Notifications
   - Enable "Actions" notifications
   - Get notified on workflow failures

2. **Workflow Status Badge**
   
   Add to README.md:
   ```markdown
   ![9 PM News Workflow](https://github.com/chaitanyame/telugu_news/workflows/Process%209%20PM%20News/badge.svg)
   ![7 AM News Workflow](https://github.com/chaitanyame/telugu_news/workflows/Process%207%20AM%20News/badge.svg)
   ```

3. **Monitor Workflow Logs**
   ```bash
   # Use GitHub CLI to check workflow status
   gh run list --workflow=process-9pm-news.yml --limit 5
   gh run view --log-failed
   ```

## Alert Configuration

### Email Alerts

**UptimeRobot:**
- Site down: Immediate email
- Site up: Recovery email
- Weekly summary: Uptime report

**Sentry:**
- Error threshold: Alert when error count > 10/hour
- New issues: Alert on first occurrence
- Regression: Alert when resolved issue reoccurs

**GitHub Actions:**
- Workflow failure: Immediate email
- Weekly summary: Action usage report

### Webhook Alerts (Slack/Discord)

**Slack Integration:**

1. Create Slack webhook:
   - Go to Slack App Directory
   - Search "Incoming WebHooks"
   - Add to your workspace
   - Copy webhook URL

2. Configure in UptimeRobot:
   - Alert Contacts > Add New
   - Type: Web-Hook
   - URL: Your Slack webhook URL
   - POST value: `{"text": "*alertTypeFriendlyName* - *monitorFriendlyName*: *alertDetails*"}`

3. Configure in Sentry:
   - Settings > Integrations > Slack
   - Connect workspace
   - Configure alert rules

**Discord Integration:**

Similar to Slack, but use Discord webhook URL format:
```
https://discord.com/api/webhooks/{webhook.id}/{webhook.token}/slack
```

## Monitoring Checklist

Daily:
- [ ] Check Sentry dashboard for new errors
- [ ] Review UptimeRobot status (if issues)

Weekly:
- [ ] Review Sentry error trends
- [ ] Check UptimeRobot uptime percentage (target: >99.9%)
- [ ] Review GitHub Actions success rate
- [ ] Check API response times

Monthly:
- [ ] Review and archive old Sentry issues
- [ ] Optimize based on performance data
- [ ] Update alert thresholds if needed

## Metrics to Track

### Availability
- **Uptime**: Target >99.9% (8.76 hours downtime/year max)
- **Response Time**: Target <500ms for API, <2s for frontend

### Errors
- **Error Rate**: Target <0.1% of requests
- **Mean Time to Recovery (MTTR)**: Target <1 hour
- **Error Types**: Track most common errors

### Performance
- **API Latency**: p50, p95, p99
- **Frontend Load Time**: Lighthouse score >90
- **Data Freshness**: News updated within 30 minutes of schedule

### Usage
- **Daily Active Users**: Track via analytics
- **API Requests**: Monitor for abuse/quota issues
- **Most Viewed Dates**: Optimize caching

## Troubleshooting

### High Error Rate

1. Check Sentry for error patterns
2. Review recent deployments
3. Check API quota usage
4. Verify environment variables

### Site Down

1. Check UptimeRobot alert details
2. Verify deployment status (Vercel/Netlify dashboard)
3. Check GitHub Actions workflows
4. Test API endpoint manually: `curl https://your-domain.com/api/health`

### Slow Response

1. Check API response times in monitoring
2. Review Sentry performance data
3. Check data file sizes (large JSON files?)
4. Verify CDN caching is working

### Workflow Failures

1. Check GitHub Actions logs
2. Verify API keys are valid
3. Check YouTube API quota
4. Test script locally: `python3 -m scripts.process_daily_news --slot 9pm`

## Cost Summary

- **Sentry Free**: 5,000 errors/month, 10,000 transactions/month
- **UptimeRobot Free**: 50 monitors, 5-minute intervals
- **GitHub Actions**: 2,000 minutes/month (free for public repos)
- **Total**: $0/month for typical usage

Upgrade options:
- Sentry Team: $26/month (100,000 errors)
- UptimeRobot Pro: $7/month (1-minute intervals, SMS alerts)

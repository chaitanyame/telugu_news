# GitHub Actions Setup Guide

This document explains how to configure and use the GitHub Actions workflows for automated news processing.

## Prerequisites

Before the workflows can run successfully, you need to configure the following GitHub secrets:

### Required Secrets

1. **YOUTUBE_API_KEY**
   - YouTube Data API v3 key
   - Get from: https://console.cloud.google.com/apis/credentials
   - Permissions needed: YouTube Data API v3 enabled

2. **GEMINI_API_KEY**
   - Google Gemini API key
   - Get from: https://aistudio.google.com/app/apikey
   - Required for video summarization

### Setting Secrets in GitHub

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret:
   - Name: `YOUTUBE_API_KEY`, Value: `<your-youtube-key>`
   - Name: `GEMINI_API_KEY`, Value: `<your-gemini-key>`

## Workflows

### 1. Process 9 PM News (`process-9pm-news.yml`)

**Purpose**: Fetch and process ETV Telugu 9 PM news bulletin daily

**Schedule**: 
- Automatic: Every day at 9:00 AM IST (3:30 UTC)
- Manual: Via GitHub UI

**Manual Trigger Options**:
- `date`: Custom date in YYYY-MM-DD format (optional, defaults to today)
- `force`: Bypass cache to reprocess already-processed videos (boolean)

**Steps**:
1. Checkout dev branch
2. Setup Python 3.11
3. Install dependencies from `scripts/requirements.txt`
4. Run: `python -m scripts.process_daily_news --slot 9pm`
5. Commit and push changes if files modified

**Artifacts**:
- Workflow logs retained for 7 days

### 2. Process 7 AM News (`process-7am-news.yml`)

**Purpose**: Fetch and process ETV Telugu 7 AM news bulletin daily

**Schedule**: 
- Automatic: Every day at 11:00 PM IST (17:30 UTC)
- Manual: Via GitHub UI

**Manual Trigger Options**:
- Same as 9 PM workflow

**Steps**:
- Identical to 9 PM workflow, but processes 7 AM slot

### 3. Weekly Data Cleanup (`cleanup-old-data.yml`)

**Purpose**: Remove old archive files to keep repository size manageable

**Schedule**: 
- Automatic: Every Sunday at midnight UTC
- Manual: Via GitHub UI

**Manual Trigger Options**:
- `days_to_keep`: Number of days to retain (default: 30)
- `dry_run`: Test mode without actual deletion (boolean)

**Steps**:
1. Checkout dev branch
2. Setup Python 3.11
3. Install dependencies
4. Run: `python -m scripts.cleanup --days 30`
5. Regenerate index.json
6. Commit and push changes if files modified

**Artifacts**:
- Cleanup summary retained for 30 days

## Manual Workflow Execution

To manually trigger a workflow:

1. Go to **Actions** tab in your GitHub repository
2. Select the workflow from the left sidebar
3. Click **Run workflow** button
4. Select branch (typically `dev`)
5. Fill in optional inputs if needed
6. Click **Run workflow** to start

## Monitoring Workflows

### Viewing Workflow Runs

1. Go to **Actions** tab
2. Click on a workflow run to see details
3. Expand steps to view logs
4. Download artifacts if available

### Workflow Logs

All workflows output structured JSON logs that can be parsed for monitoring:

```json
{
  "timestamp": "2025-12-09T03:30:00Z",
  "level": "INFO",
  "message": "Processing time slot",
  "slot": "9pm",
  "date": "2025-12-09",
  "video_id": "abc123"
}
```

### Common Issues

**Issue**: Workflow fails with "API key not found"
- **Solution**: Ensure secrets are configured correctly in repository settings

**Issue**: Workflow fails with "Video not found"
- **Solution**: This is normal if no video published yet. Workflow will succeed without processing.

**Issue**: Workflow fails with "Permission denied" on push
- **Solution**: Ensure workflow has write permissions (Settings > Actions > General > Workflow permissions)

## Local Testing

Before relying on automated workflows, test locally:

### Test News Processing
```bash
# Test 9 PM processing (dry-run)
python -m scripts.process_daily_news --slot 9pm --dry-run

# Test with specific date
python -m scripts.process_daily_news --slot 9pm --date 2025-12-01

# Force reprocessing
python -m scripts.process_daily_news --slot 9pm --force
```

### Test Cleanup
```bash
# Dry run (no deletion)
python -m scripts.cleanup --dry-run

# Custom retention period
python -m scripts.cleanup --days 60

# Check what would be deleted
python -m scripts.cleanup --days 7 --dry-run
```

## Architecture

```
GitHub Actions Workflows
├── Scheduled Triggers (cron)
│   ├── 9 PM News: Daily at 9:00 AM IST
│   ├── 7 AM News: Daily at 11:00 PM IST
│   └── Cleanup: Weekly on Sunday
│
├── Manual Triggers (workflow_dispatch)
│   └── All workflows with custom inputs
│
├── Processing Pipeline
│   ├── YouTube API: Fetch video metadata
│   ├── Gemini API: Generate Telugu summaries
│   ├── JSON Storage: Save to data/archive/
│   └── Index: Update data/index.json
│
└── Git Operations
    ├── Auto-commit: github-actions[bot]
    └── Auto-push: To dev branch
```

## Data Structure

Generated files:
```
data/
├── index.json (Master index)
├── archive/
│   └── YYYY-MM/
│       └── YYYY-MM-DD.json (Daily news)
└── cache/
    └── video-ids.json (Processed videos)
```

## Maintenance

### Adjusting Schedule

Edit `.github/workflows/<workflow>.yml`:

```yaml
on:
  schedule:
    - cron: '30 3 * * *'  # Modify this line
```

Cron format: `minute hour day month weekday`

IST to UTC conversion: IST - 5:30 = UTC

### Adjusting Retention

Cleanup workflow (default 30 days):

```yaml
- name: Run cleanup script
  run: |
    python -m scripts.cleanup --days 30  # Modify this value
```

### Disabling Workflows

1. Go to **Actions** tab
2. Select workflow
3. Click **...** menu > **Disable workflow**

## Best Practices

1. **Test Locally First**: Always test changes locally before pushing
2. **Monitor Initial Runs**: Watch first few automated runs for issues
3. **Review Artifacts**: Check logs regularly for errors
4. **Keep Secrets Secure**: Never commit API keys to repository
5. **Use Dry-Run**: Test destructive operations with `--dry-run` first

## Troubleshooting

Enable debug logging in workflow:

```yaml
- name: Process news
  env:
    ACTIONS_STEP_DEBUG: true
  run: |
    python -m scripts.process_daily_news --slot 9pm
```

View detailed logs in GitHub Actions run output.

## Support

For issues or questions:
1. Check workflow logs in Actions tab
2. Review this documentation
3. Test locally to isolate the issue
4. Check API quotas and limits

# Deployment Guide - ETV Telugu News Aggregator

## Overview

This application can be deployed to various static hosting platforms. It consists of:
- Static HTML/CSS/JS frontend
- JSON data files
- GitHub Actions for automated updates

## Prerequisites

- GitHub repository with Actions enabled
- GitHub Secrets configured:
  - `YOUTUBE_API_KEY`: YouTube Data API v3 key
  - `GEMINI_API_KEY`: Google Gemini API key

## Deployment Options

### Option 1: GitHub Pages (Recommended)

**Pros**: Free, automatic deployment, good performance
**Cons**: Public repositories only for free tier

#### Steps:

1. **Enable GitHub Pages**:
   ```bash
   # Go to Settings > Pages
   # Source: Deploy from branch
   # Branch: Select 'dev' and '/ (root)'
   # Click Save
   ```

2. **Configure Base Path** (if using project site):
   ```javascript
   // Update js/utils/data-loader.js
   const BASE_PATH = '/telugu_news/data'; // Add repo name
   ```

3. **Deploy**:
   ```bash
   git push origin dev
   # Site will be available at: https://chaitanyame.github.io/telugu_news/
   ```

4. **Custom Domain** (optional):
   - Add CNAME file with your domain
   - Configure DNS CNAME record
   - Enable HTTPS in Settings

### Option 2: Netlify

**Pros**: Easy setup, preview deployments, custom domains
**Cons**: Build minutes limited on free tier

#### Steps:

1. **Connect Repository**:
   - Login to Netlify
   - Click "Add new site" > "Import existing project"
   - Connect to GitHub
   - Select repository

2. **Configure Build**:
   ```toml
   # netlify.toml
   [build]
     publish = "."
     command = ""

   [[redirects]]
     from = "/*"
     to = "/index.html"
     status = 200
   ```

3. **Deploy**:
   - Click "Deploy site"
   - Site URL: `https://your-site.netlify.app`

4. **Environment Variables**:
   - Add in Site settings > Environment variables
   - `YOUTUBE_API_KEY`
   - `GEMINI_API_KEY`

### Option 3: Vercel

**Pros**: Fast CDN, serverless functions support
**Cons**: Limited to 100 deployments/day on free tier

#### Steps:

1. **Import Project**:
   - Login to Vercel
   - Click "Add New" > "Project"
   - Import from GitHub

2. **Configure**:
   ```json
   {
     "version": 2,
     "routes": [
       { "handle": "filesystem" },
       { "src": "/(.*)", "dest": "/index.html" }
     ]
   }
   ```

3. **Deploy**:
   - Click "Deploy"
   - Site URL: `https://your-project.vercel.app`

### Option 4: Cloudflare Pages

**Pros**: Fast global CDN, unlimited bandwidth
**Cons**: Requires Cloudflare account

#### Steps:

1. **Create Project**:
   - Login to Cloudflare Dashboard
   - Pages > Create a project
   - Connect to GitHub

2. **Configure**:
   - Build command: (leave empty)
   - Build output directory: `/`
   - Branch: `dev`

3. **Deploy**:
   - Click "Save and Deploy"
   - Site URL: `https://your-project.pages.dev`

## Post-Deployment Configuration

### GitHub Actions

Ensure workflows have write permissions:
```yaml
# .github/workflows/*.yml
permissions:
  contents: write
```

### Data Directory

Ensure `data/` directory is tracked in git:
```bash
git add data/*.json
git commit -m "Add data files"
git push
```

### CORS Configuration

For GitHub Pages, no configuration needed.
For custom servers, add CORS headers:
```nginx
# Nginx
add_header Access-Control-Allow-Origin *;
add_header Access-Control-Allow-Methods "GET, OPTIONS";
```

## Monitoring

### Check Workflow Status

```bash
# View workflow runs
https://github.com/chaitanyame/telugu_news/actions

# Check specific workflow
gh run list --workflow=process-9pm-news.yml
```

### Check Site Status

```bash
# Test data endpoint
curl https://your-site.com/data/index.json

# Check specific date
curl https://your-site.com/data/2025-12-09.json
```

## Troubleshooting

### Workflows Not Running

1. **Check Secrets**:
   ```bash
   # Go to Settings > Secrets > Actions
   # Verify YOUTUBE_API_KEY and GEMINI_API_KEY exist
   ```

2. **Check Permissions**:
   ```bash
   # Settings > Actions > General
   # Workflow permissions: Read and write permissions
   ```

3. **Manual Trigger**:
   ```bash
   # Actions > Select workflow > Run workflow
   ```

### Data Not Updating

1. **Check Workflow Logs**:
   ```bash
   # Actions > Latest run > View logs
   ```

2. **Verify Data Files**:
   ```bash
   ls -la data/
   cat data/index.json
   ```

3. **Test Locally**:
   ```bash
   python -m scripts.process_daily_news --slot 9pm --date 2025-12-09
   ```

### Site Not Loading

1. **Check Console Errors**:
   - Open Browser DevTools > Console
   - Look for 404 or CORS errors

2. **Verify File Paths**:
   ```javascript
   // Check BASE_PATH in data-loader.js
   const BASE_PATH = '/data'; // Should match your deployment
   ```

3. **Test Locally**:
   ```bash
   python -m http.server 8000
   # Visit http://localhost:8000
   ```

## Performance Optimization

### Enable Caching

Add cache headers for static assets:
```yaml
# Netlify: netlify.toml
[[headers]]
  for = "/data/*.json"
  [headers.values]
    Cache-Control = "public, max-age=3600"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000"
```

### Enable Compression

Most platforms enable gzip/brotli automatically. Verify:
```bash
curl -H "Accept-Encoding: gzip" -I https://your-site.com
# Should see: Content-Encoding: gzip
```

### CDN Configuration

Use CDN for faster global access:
- Cloudflare (free tier available)
- CloudFront (AWS)
- Fastly (paid)

## Backup and Recovery

### Backup Data Files

```bash
# Create backup
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Restore from backup
tar -xzf backup-20251209.tar.gz
git add data/
git commit -m "Restore data from backup"
git push
```

### Disaster Recovery

1. **Clone Repository**:
   ```bash
   git clone https://github.com/chaitanyame/telugu_news.git
   ```

2. **Restore Secrets**:
   - Add YOUTUBE_API_KEY
   - Add GEMINI_API_KEY

3. **Redeploy**:
   - Push to GitHub
   - Workflows will auto-run
   - Site will redeploy automatically

## Scaling

For high traffic:

1. **Use CDN**: Cloudflare, CloudFront
2. **Enable Caching**: Browser cache + CDN cache
3. **Optimize Assets**: Minify CSS/JS
4. **Lazy Loading**: Load data on-demand
5. **Service Worker**: Cache static assets

## Cost Estimates

- **GitHub Pages**: Free
- **Netlify Free**: 100 GB bandwidth, 300 build minutes/month
- **Vercel Free**: 100 GB bandwidth, 100 deployments/day
- **Cloudflare Pages**: Unlimited bandwidth, 500 builds/month

All options are free for typical usage (< 10k visitors/month).

## Security

### API Keys

- Never commit API keys to git
- Use GitHub Secrets
- Rotate keys periodically

### HTTPS

- Always use HTTPS
- Most platforms enable automatically
- For custom domains, use Let's Encrypt

### Content Security

- Escape user content (already implemented)
- No inline scripts (CSP-compliant)
- CORS properly configured

## Maintenance

### Weekly Tasks

- Check workflow status
- Review error logs
- Monitor disk usage

### Monthly Tasks

- Update dependencies
- Review analytics
- Optimize performance

### As Needed

- Rotate API keys
- Update content
- Fix bugs

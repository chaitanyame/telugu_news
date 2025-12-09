"""
ETV Telugu News Aggregator API

Simple Flask API for serving aggregated Telugu news data.
Reads from JSON files in the data/ directory.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
DATA_DIR = Path(__file__).parent.parent / "data"
MAX_NEWS_ITEMS = 100  # Limit response size


def read_json_file(filepath):
    """Read and parse a JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        app.logger.error(f"Invalid JSON in file: {filepath}")
        return None


def get_available_dates():
    """Get list of available news dates from index.json."""
    index_file = DATA_DIR / "index.json"
    data = read_json_file(index_file)
    
    if data and 'dates' in data:
        return data['dates']
    
    # Fallback: scan directory for date files
    dates = []
    for file in DATA_DIR.glob("*.json"):
        if file.name != "index.json":
            # Extract date from filename (YYYY-MM-DD.json)
            date_str = file.stem
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date_str)
            except ValueError:
                continue
    
    return sorted(dates, reverse=True)


def get_news_for_date(date_str):
    """Get news data for a specific date."""
    news_file = DATA_DIR / f"{date_str}.json"
    return read_json_file(news_file)


@app.route('/')
def index():
    """API root endpoint with documentation."""
    return jsonify({
        "name": "ETV Telugu News Aggregator API",
        "version": "1.0.0",
        "endpoints": {
            "/api/dates": "Get list of available news dates",
            "/api/news": "Get all news or filter by date/slot",
            "/api/news/latest": "Get latest news",
            "/api/news/<date>": "Get news for specific date",
            "/health": "Health check endpoint"
        },
        "documentation": "https://github.com/chaitanyame/telugu_news/blob/dev/API.md"
    })


@app.route('/health')
def health():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


@app.route('/api/dates')
def get_dates():
    """
    Get list of available news dates.
    
    Returns:
        {
            "dates": ["2025-12-09", "2025-12-08", ...],
            "count": 3,
            "last_updated": "2025-12-09T17:15:00Z"
        }
    """
    dates = get_available_dates()
    
    # Try to get last_updated from index.json
    index_file = DATA_DIR / "index.json"
    index_data = read_json_file(index_file)
    last_updated = index_data.get('last_updated') if index_data else None
    
    return jsonify({
        "dates": dates,
        "count": len(dates),
        "last_updated": last_updated or datetime.utcnow().isoformat() + "Z"
    })


@app.route('/api/news')
def get_news():
    """
    Get news data with optional filtering.
    
    Query Parameters:
        - date: Filter by specific date (YYYY-MM-DD)
        - slot: Filter by time slot (9pm or 7am)
        - limit: Maximum number of news items (default: 100)
        - offset: Offset for pagination (default: 0)
    
    Returns:
        {
            "news": [...],
            "count": 10,
            "total": 20,
            "filters": {...}
        }
    """
    # Get query parameters
    date_filter = request.args.get('date')
    slot_filter = request.args.get('slot')
    limit = min(int(request.args.get('limit', MAX_NEWS_ITEMS)), MAX_NEWS_ITEMS)
    offset = int(request.args.get('offset', 0))
    
    all_news = []
    
    if date_filter:
        # Get news for specific date
        news_data = get_news_for_date(date_filter)
        if news_data and 'news' in news_data:
            all_news.extend(news_data['news'])
    else:
        # Get news for all available dates
        dates = get_available_dates()
        for date in dates[:30]:  # Limit to 30 most recent dates
            news_data = get_news_for_date(date)
            if news_data and 'news' in news_data:
                # Add date field to each news item
                for item in news_data['news']:
                    item['date'] = date
                all_news.extend(news_data['news'])
    
    # Apply slot filter
    if slot_filter:
        all_news = [item for item in all_news if item.get('slot') == slot_filter]
    
    # Apply pagination
    total = len(all_news)
    paginated_news = all_news[offset:offset + limit]
    
    return jsonify({
        "news": paginated_news,
        "count": len(paginated_news),
        "total": total,
        "filters": {
            "date": date_filter,
            "slot": slot_filter,
            "limit": limit,
            "offset": offset
        }
    })


@app.route('/api/news/latest')
def get_latest_news():
    """
    Get news from the most recent available date.
    
    Returns:
        {
            "date": "2025-12-09",
            "news": [...],
            "count": 2
        }
    """
    dates = get_available_dates()
    
    if not dates:
        return jsonify({
            "error": "No news data available",
            "date": None,
            "news": [],
            "count": 0
        }), 404
    
    latest_date = dates[0]
    news_data = get_news_for_date(latest_date)
    
    if not news_data or 'news' not in news_data:
        return jsonify({
            "error": "No news found for latest date",
            "date": latest_date,
            "news": [],
            "count": 0
        }), 404
    
    return jsonify({
        "date": latest_date,
        "news": news_data['news'],
        "count": len(news_data['news'])
    })


@app.route('/api/news/<date>')
def get_news_by_date(date):
    """
    Get news for a specific date.
    
    Args:
        date: Date string in YYYY-MM-DD format
    
    Returns:
        {
            "date": "2025-12-09",
            "news": [...],
            "count": 2
        }
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return jsonify({
            "error": "Invalid date format. Use YYYY-MM-DD",
            "date": date
        }), 400
    
    news_data = get_news_for_date(date)
    
    if not news_data or 'news' not in news_data:
        return jsonify({
            "error": "No news found for this date",
            "date": date,
            "news": [],
            "count": 0
        }), 404
    
    return jsonify({
        "date": date,
        "news": news_data['news'],
        "count": len(news_data['news'])
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": str(error)
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    app.logger.error(f"Internal error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)

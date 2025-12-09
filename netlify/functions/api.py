"""Netlify Functions wrapper for Flask API"""

from api.app import app


def handler(event, context):
    """AWS Lambda handler for Netlify Functions."""
    # For Netlify Functions, we use serverless-wsgi
    from serverless_wsgi import handle_request
    return handle_request(app, event, context)

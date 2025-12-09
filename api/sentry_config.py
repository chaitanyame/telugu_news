"""
Sentry Integration for Error Tracking

Setup Sentry for monitoring errors in the Flask API and frontend.
"""

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import os


def init_sentry(app=None):
    """
    Initialize Sentry for error tracking.
    
    Args:
        app: Flask app instance (optional, for Flask integration)
    """
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if not sentry_dsn:
        print("Warning: SENTRY_DSN not set. Error tracking disabled.")
        return
    
    integrations = []
    if app:
        integrations.append(FlaskIntegration())
    
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=integrations,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # Adjust this value in production.
        traces_sample_rate=0.1,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # Adjust this value in production.
        profiles_sample_rate=0.1,
        environment=os.getenv('FLASK_ENV', 'development'),
    )
    
    print(f"Sentry initialized for environment: {os.getenv('FLASK_ENV', 'development')}")


# Frontend Sentry configuration (JavaScript)
SENTRY_FRONTEND_CONFIG = """
<!-- Add this to index.html before other scripts -->
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
    // Performance Monitoring
    tracesSampleRate: 0.1,
    // Session Replay
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
    environment: "production",
  });
</script>
"""

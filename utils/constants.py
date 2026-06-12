from __future__ import annotations

from datetime import timedelta


ADMIN_EMAIL = "admin@tredalq.com"
ADMIN_PASSWORD = "Admin@123"
ADMIN_NAME = "TREDALQ Admin"
ADMIN_ROLE = "admin"
ADMIN_MOBILE = "9999999999"
ADMIN_COUNTRY = "India"
ADMIN_EXPERIENCE = "Expert"

JWT_EXPIRY = timedelta(hours=24)
AUTH_COOKIE_NAME = "tredalq_auth"
LOGIN_RATE_LIMIT_ATTEMPTS = 5
LOGIN_RATE_LIMIT_WINDOW_MINUTES = 10

DEFAULT_SYMBOL = "AAPL"
DEFAULT_MARKET_SYMBOL = "RELIANCE.NS"

USER_MENU = [
    "Dashboard",
    "Market",
    "Prediction",
    "Analytics",
    "Portfolio",
    "Watchlist",
    "Alerts",
    "Settings",
]

ADMIN_MENU = [
    "Dashboard",
    "Users",
    "AI Models",
    "Analytics",
    "API Monitor",
    "System Health",
    "Settings",
]

MENU_ICONS = {
    "Dashboard": "house",
    "Market": "graph-up",
    "Prediction": "cpu",
    "Analytics": "bar-chart",
    "Portfolio": "briefcase",
    "Watchlist": "star",
    "Alerts": "bell",
    "Settings": "gear",
    "Users": "people",
    "AI Models": "robot",
    "API Monitor": "plug",
    "System Health": "pc-display",
}

COUNTRIES = [
    "India",
    "United States",
    "United Kingdom",
    "Canada",
    "Australia",
    "Singapore",
    "Germany",
    "Japan",
    "United Arab Emirates",
]

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Expert"]

PREDICTION_PERIODS = {
    "1 day": 1,
    "1 week": 5,
    "1 month": 22,
}

MODEL_OPTIONS = ["Best Accuracy", "Random Forest", "XGBoost", "LinReg", "Prophet", "LSTM"]
BEST_ACCURACY_MODEL = "Best Accuracy"

PAGE_DESCRIPTIONS = {
    "Dashboard": "Live portfolio intelligence, price action, and the latest model-driven signals.",
    "Market": "Real-time symbol lookup with candlesticks, volume, and technical context.",
    "Prediction": "Train and compare live forecasts using real market data and time-series models.",
    "Analytics": "Technical indicators, model accuracy metrics, and sector-level market snapshots.",
    "Portfolio": "Track holdings, exposure, transaction history, and unrealized performance.",
    "Watchlist": "Monitor priority tickers with live prices, changes, and alert thresholds.",
    "Alerts": "Manage threshold alerts and review which symbols are close to trigger levels.",
    "Settings": "Maintain your profile, experience level, and password securely.",
    "Users": "Admin access to registration trends, role assignments, and user directory views.",
    "AI Models": "Monitor model availability, evaluation metrics, and recent prediction quality.",
    "API Monitor": "Track market-data usage volume, fetch health, and high-traffic symbols.",
    "System Health": "Inspect app runtime status, storage health, and environment dependencies.",
}

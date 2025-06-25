"""Configuration module for flight tracker."""

import os
from typing import List, Optional

# Try to load dotenv for development environments
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env file if it exists
except ImportError:
    # dotenv not installed, skip loading (production environment)
    pass


class Config:
    """Configuration class for flight tracker."""

    # File paths
    TRACKED_COUNTRIES_FILE = "tracked_countries.txt"
    AIRPORTS_CSV = os.path.join("data", "airports.csv")
    COUNTRIES_CSV = os.path.join("data", "countries.csv")
    EMAIL_CSS = os.path.join("styles", "email.css")

    # Default countries to track if file not found
    DEFAULT_COUNTRIES = ["IQ", "IR", "IL", "SY", "JO", "LB"]

    # Email configuration
    GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
    GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    @classmethod
    def has_email_config(cls) -> bool:
        """Check if all required email configuration is present."""
        return all([cls.GMAIL_EMAIL, cls.GMAIL_APP_PASSWORD, cls.RECIPIENT_EMAIL])

    @classmethod
    def get_missing_email_vars(cls) -> List[str]:
        """Get list of missing email environment variables."""
        missing = []
        if not cls.GMAIL_EMAIL:
            missing.append("GMAIL_EMAIL")
        if not cls.GMAIL_APP_PASSWORD:
            missing.append("GMAIL_APP_PASSWORD")
        if not cls.RECIPIENT_EMAIL:
            missing.append("RECIPIENT_EMAIL")
        return missing

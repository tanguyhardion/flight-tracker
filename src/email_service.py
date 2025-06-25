"""Email service for sending flight notifications."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from .config import Config
from .html_generator import HTMLGenerator


class EmailService:
    """Handles email notifications for flight alerts."""

    def __init__(self):
        self.html_generator = HTMLGenerator()

    def _validate_email_config(self) -> bool:
        """Validate email configuration and print helpful messages."""
        if not Config.has_email_config():
            missing_vars = Config.get_missing_email_vars()
            print("Gmail credentials missing - skipping email notification")
            print(f"Required environment variables: {', '.join(missing_vars)}")
            return False
        return True

    def _create_email_message(
        self, total_flights: int, flight_details: List[Dict[str, Any]]
    ) -> MIMEMultipart:
        """Create the email message with HTML content."""
        message = MIMEMultipart("alternative")
        message["Subject"] = f"Flight Alert: {total_flights} flights detected"
        message["From"] = Config.GMAIL_EMAIL
        message["To"] = Config.RECIPIENT_EMAIL

        # Generate HTML content
        html_body = self.html_generator.generate_email_html(
            total_flights, flight_details
        )
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        return message

    def _send_via_smtp(self, message: MIMEMultipart) -> None:
        """Send email via Gmail SMTP."""
        with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.starttls()  # Enable encryption
            server.login(Config.GMAIL_EMAIL, Config.GMAIL_APP_PASSWORD)
            server.send_message(message)

    def send_notification(
        self, total_flights: int, flight_details: List[Dict[str, Any]]
    ) -> bool:
        """
        Send email notification for detected flights.

        Args:
            total_flights: Total number of flights detected
            flight_details: List of flight detail dictionaries

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not self._validate_email_config():
            return False

        if total_flights == 0:
            print("No flights to notify about")
            return False

        try:
            message = self._create_email_message(total_flights, flight_details)
            self._send_via_smtp(message)
            print(f"✅ Email notification sent to {Config.RECIPIENT_EMAIL}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

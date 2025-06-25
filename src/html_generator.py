"""HTML generation utilities for email notifications."""

import os
from datetime import datetime
from typing import List, Dict, Any
from .config import Config


class HTMLGenerator:
    """Generates HTML content for email notifications."""

    def __init__(self):
        self._css_cache = None

    def _load_css(self) -> str:
        """Load CSS content from file with caching."""
        if self._css_cache is None:
            try:
                with open(Config.EMAIL_CSS, "r", encoding="utf-8") as file:
                    self._css_cache = file.read()
            except Exception as e:
                print(f"Error loading CSS file: {e}")
                self._css_cache = ""
        return self._css_cache

    def _create_flight_html(self, flight_detail: Dict[str, Any]) -> str:
        """Create HTML for a single flight."""
        flight_url = f"https://www.flightradar24.com/{flight_detail['call_sign']}/{flight_detail['flight_id']}"

        return f"""
                <div class="flight-item">
                    Flight <a href='{flight_url}' target='_blank' class='flight-link'>{flight_detail['call_sign']} (ID: {flight_detail['flight_id']})</a>:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{flight_detail['origin_airport_name']} ({flight_detail['origin_country_name']})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{flight_detail['destination_airport_name']} ({flight_detail['destination_country_name']})
                </div>"""

    def _create_country_container(
        self, country_name: str, flight_count: int, flights_html: List[str]
    ) -> str:
        """Create HTML container for a country's flights."""
        flight_word = "flight" if flight_count == 1 else "flights"

        return f"""
                        <div class="country-container">
                            <div class="country-header">{country_name}: {flight_count} {flight_word}</div>
                            <div class="country-flights">
                                {''.join(flights_html)}
                            </div>
                        </div>"""

    def _group_flights_by_country(
        self, flight_details: List[Dict[str, Any]]
    ) -> List[str]:
        """Group flights by country and create HTML containers."""
        containers = []
        current_country = None
        country_flights = []

        for detail in flight_details:
            # Check if we've moved to a new country
            if current_country != detail["country"]:
                # Process previous country if we have flights
                if current_country is not None and country_flights:
                    country_name = detail.get("country_name", "Unknown")
                    # Get the country name from the previous detail
                    prev_detail = next(
                        (d for d in flight_details if d["country"] == current_country),
                        None,
                    )
                    if prev_detail:
                        country_name = prev_detail["country_name"]

                    container = self._create_country_container(
                        country_name, len(country_flights), country_flights
                    )
                    containers.append(container)

                # Start new country
                current_country = detail["country"]
                country_flights = []

            # Add flight to current country
            flight_html = self._create_flight_html(detail)
            country_flights.append(flight_html)

        # Handle the last country
        if current_country is not None and country_flights:
            # Find the country name from the last detail
            last_detail = next(
                (
                    d
                    for d in reversed(flight_details)
                    if d["country"] == current_country
                ),
                None,
            )
            country_name = last_detail["country_name"] if last_detail else "Unknown"

            container = self._create_country_container(
                country_name, len(country_flights), country_flights
            )
            containers.append(container)

        return containers

    def generate_email_html(
        self, total_flights: int, flight_details: List[Dict[str, Any]]
    ) -> str:
        """Generate complete HTML email body."""
        css_content = self._load_css()
        flight_containers = self._group_flights_by_country(flight_details)
        timestamp = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")

        return f"""
            <html>
            <head>
                <style>
                    {css_content}
                </style>
            </head>
            <body>
                <h2>🛫 Flight Tracking Alert</h2>
                
                <div class="flight-list">
                {''.join(flight_containers)}
                </div>
                
                <div class="timestamp">
                    <strong>Timestamp:</strong> {timestamp}
                </div>
                
                <div class="footer">
                    <p><em>This is an automated notification from your flight tracking system.</em></p>
                    <p><small>Click on any flight link to view it on FlightRadar24</small></p>
                </div>
            </body>
            </html>
            """

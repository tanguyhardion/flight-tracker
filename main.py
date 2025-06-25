from FlightRadar24 import FlightRadar24API
import smtplib
import os
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to load dotenv for development environments
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file if it exists
except ImportError:
    # dotenv not installed, skip loading (production environment)
    pass


class FlightTracker:
    def __init__(self, countries_to_track=None):
        self.fr_api = FlightRadar24API()
        self.airport_countries = self._load_airport_countries()
        self.country_airports = self._load_country_airports()
        self.country_codes_to_names = self._load_country_names()
        self.country_names_to_codes = {v: k for k, v in self.country_codes_to_names.items()}
        self.airport_names = self._load_airport_names()
        
        # Set default countries to track if none provided
        if countries_to_track is None:
            self.countries_to_track = self._load_countries_from_file()
        else:
            self.countries_to_track = countries_to_track

    def _load_countries_from_file(self, filename="tracked_countries.txt"):
        """Load country names from a text file and convert to country codes."""
        countries = []
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    country_name = line.strip()  # Remove whitespace
                    if country_name:  # Skip empty lines
                        # Convert country name to country code
                        country_code = self.country_names_to_codes.get(country_name)
                        if country_code:
                            countries.append(country_code)
                        else:
                            print(f"Warning: Country '{country_name}' not found in countries.csv")
            
            if not countries:
                print(f"No valid countries found in {filename}, using default countries")
                return ["IQ", "IR", "IL", "SY", "JO", "LB"]  # Fallback to default
            
            print(f"Loaded {len(countries)} countries from {filename}: {[self.country_codes_to_names.get(code, code) for code in countries]}")
            return countries
            
        except FileNotFoundError:
            print(f"File {filename} not found, using default countries")
            return ["IQ", "IR", "IL", "SY", "JO", "LB"]  # Default countries
        except Exception as e:
            print(f"Error loading countries from {filename}: {e}")
            return ["IQ", "IR", "IL", "SY", "JO", "LB"]  # Default countries

    def _load_airport_countries(self):
        """Load airport to country mapping from a CSV file."""
        airport_countries = {}
        try:
            csv_path = os.path.join("data", "airports.csv")
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    airport_code = row.get("code")  # IATA code column
                    country_code = row.get("country")  # Country code column
                    if airport_code and country_code:
                        airport_countries[airport_code] = country_code
        except Exception as e:
            print(f"Error loading airport countries: {e}")
        return airport_countries

    def _load_country_airports(self):
        """Load airports grouped by country code from the CSV file."""
        country_airports = {}
        try:
            csv_path = os.path.join("data", "airports.csv")
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    airport_code = row.get("code")
                    country_code = row.get("country")
                    
                    if airport_code and country_code:
                        if country_code not in country_airports:
                            country_airports[country_code] = []
                        country_airports[country_code].append(airport_code)
        except Exception as e:
            print(f"Error loading country airports: {e}")
        return country_airports

    def _load_country_names(self):
        """Load country code to name mapping from countries.csv."""
        country_names = {}
        try:
            csv_path = os.path.join("data", "countries.csv")
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    country_code = row.get("alpha-2")  # ISO 2-letter code
                    country_name = row.get("name")
                    if country_code and country_name:
                        country_names[country_code] = country_name
        except Exception as e:
            print(f"Error loading country names: {e}")
        return country_names

    def _load_airport_names(self):
        """Load airport code to name mapping from airports.csv."""
        airport_names = {}
        try:
            csv_path = os.path.join("data", "airports.csv")
            with open(csv_path, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    airport_code = row.get("code")  # IATA code
                    airport_name = row.get("name")
                    if airport_code and airport_name:
                        airport_names[airport_code] = airport_name
        except Exception as e:
            print(f"Error loading airport names: {e}")
        return airport_names

    def _get_country_name(self, country_code):
        """Get country name for a country code."""
        return self.country_codes_to_names.get(country_code, country_code)

    def _get_airport_name(self, airport_code):
        """Get airport name for an airport code."""
        return self.airport_names.get(airport_code, airport_code)

    def _get_country_code(self, airport_code):
        """Get country code for an airport code from the CSV data."""
        return self.airport_countries.get(airport_code, "Unknown")

    def _load_css(self, css_filename):
        """Load CSS content from a file in the styles folder."""
        try:
            css_path = os.path.join("styles", css_filename)
            with open(css_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"Error loading CSS file {css_filename}: {e}")
            return ""

    def get_flights_to_country(self, country_code):
        """Get flights to a specific country using airports from CSV."""
        flights = self.fr_api.get_flights()
        country_flights = []

        # Get airports for this country from CSV data
        country_airports = self.country_airports.get(country_code, [])
        
        if not country_airports:
            country_name = self._get_country_name(country_code)
            print(f"No airports found for {country_name} ({country_code}) in CSV data")
            return []

        country_name = self._get_country_name(country_code)
        print(f"Tracking {len(country_airports)} airports for {country_name} ({country_code}): {country_airports[:5]}{'...' if len(country_airports) > 5 else ''}")

        for flight in flights:
            destination = getattr(flight, "destination_airport_iata", None)
            if destination and destination in country_airports:
                country_flights.append(flight)

        return country_flights

    def track_all_flights(self):
        """Track flights to all specified countries."""
        print("Flight Tracking Report")
        print("-" * 30)
        tracked_country_names = [self._get_country_name(code) for code in self.countries_to_track]
        print(f"Tracking countries: {', '.join(tracked_country_names)}")
        print("-" * 30)

        flight_report = []
        flight_details = []  # Store detailed flight info for email hyperlinks
        total_flights = 0

        for country_code in self.countries_to_track:
            flights = self.get_flights_to_country(country_code)
            flight_count = len(flights)
            total_flights += flight_count
            country_name = self._get_country_name(country_code)
            print(f"→  {country_name}: {flight_count} flights")

            if flight_count > 0:
                flight_report.append(f"{country_name}: {flight_count} flights")
                # Add some flight details
                for i, flight in enumerate(flights):
                    call_sign = getattr(flight, "callsign", "Unknown")
                    flight_id = getattr(flight, "id", "Unknown")
                    origin = getattr(flight, "origin_airport_iata", "Unknown")
                    destination = getattr(flight, "destination_airport_iata", "Unknown")

                    # Store detailed info for email
                    origin_country = self._get_country_code(origin)
                    destination_country = self._get_country_code(destination)
                    origin_country_name = self._get_country_name(origin_country)
                    destination_country_name = self._get_country_name(destination_country)
                    origin_airport_name = self._get_airport_name(origin)
                    destination_airport_name = self._get_airport_name(destination)

                    flight_details.append(
                        {
                            "call_sign": call_sign,
                            "flight_id": flight_id,
                            "origin": origin,
                            "destination": destination,
                            "origin_country": origin_country,
                            "destination_country": destination_country,
                            "origin_country_name": origin_country_name,
                            "destination_country_name": destination_country_name,
                            "origin_airport_name": origin_airport_name,
                            "destination_airport_name": destination_airport_name,
                            "country": country_code,
                            "country_name": country_name,
                        }
                    )

                    flight_report.append(
                        f"  - Flight {call_sign} (ID: {flight_id}): {origin_airport_name} → {destination_airport_name}"
                    )

        if total_flights > 0:
            self.send_email_notification(flight_report, total_flights, flight_details)
        else:
            print("No flights detected - no email sent")

    def send_email_notification(self, flight_report, total_flights, flight_details):
        """Send email notification when flights are detected using Gmail SMTP"""
        try:  # Get email settings from environment variables
            sender_email = os.getenv("GMAIL_EMAIL")
            sender_password = os.getenv("GMAIL_APP_PASSWORD")
            recipient_email = os.getenv("RECIPIENT_EMAIL")

            if not sender_email or not sender_password or not recipient_email:
                print("Gmail credentials missing - skipping email notification")
                print(
                    "Required environment variables: GMAIL_EMAIL, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL"
                )
                return

            # Gmail SMTP configuration
            smtp_server = "smtp.gmail.com"
            smtp_port = 587

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Flight Alert: {total_flights} flights detected"
            message["From"] = sender_email
            message["To"] = recipient_email

            # Build flight list with country containers
            flight_html_containers = []
            current_country = None
            country_flights = []

            for detail in flight_details:
                if current_country != detail["country"]:
                    # If we have accumulated flights for the previous country, create container
                    if current_country is not None and country_flights:
                        country_count = len(country_flights)
                        flight_word = "flight" if country_count == 1 else "flights"
                        previous_country_name = self._get_country_name(current_country)

                        container_html = f"""
                        <div class="country-container">
                            <div class="country-header">{previous_country_name}: {country_count} {flight_word}</div>
                            <div class="country-flights">
                                {''.join(country_flights)}
                            </div>
                        </div>"""
                        flight_html_containers.append(container_html)

                    # Start new country
                    current_country = detail["country"]
                    country_flights = []

                # Create hyperlink to FlightRadar24
                flight_url = f"https://www.flightradar24.com/{detail['call_sign']}/{detail['flight_id']}"
                flight_html = f"""
                <div class="flight-item">
                    Flight <a href='{flight_url}' target='_blank' class='flight-link'>{detail['call_sign']} (ID: {detail['flight_id']})</a>:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{detail['origin_airport_name']} ({detail['origin_country_name']})<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;↓<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;{detail['destination_airport_name']} ({detail['destination_country_name']})
                </div>"""
                country_flights.append(flight_html)

            # Add the last country container
            if current_country is not None and country_flights:
                country_count = len(country_flights)
                flight_word = "flight" if country_count == 1 else "flights"
                last_country_name = self._get_country_name(current_country)

                container_html = f"""
                <div class="country-container">
                    <div class="country-header">{last_country_name}: {country_count} {flight_word}</div>
                    <div class="country-flights">
                        {''.join(country_flights)}
                    </div>
                </div>"""
                flight_html_containers.append(container_html)

            # Load CSS from external file
            email_css = self._load_css("email.css")

            html_body = f"""
            <html>
            <head>
                <style>
                    {email_css}
                </style>
            </head>
            <body>
                <h2>🛫 Flight Tracking Alert</h2>
                
                <div class="flight-list">
                {''.join(flight_html_containers)}
                </div>
                
                <div class="timestamp">
                    <strong>Timestamp:</strong> {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
                </div>
                
                <div class="footer">
                    <p><em>This is an automated notification from your flight tracking system.</em></p>
                    <p><small>Click on any flight link to view it on FlightRadar24</small></p>
                </div>
            </body>
            </html>
            """

            # Create HTML part
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)  # Send email using Gmail SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Enable encryption (required for Gmail)
                server.login(sender_email, sender_password)
                server.send_message(message)

            print(f"✅ Email notification sent to {recipient_email}")

        except Exception:
            print(f"❌ Failed to send email.")
            raise


def main():
    # Now the countries will be loaded from tracked_countries.txt automatically
    # You can still override by passing a list if needed:
    # tracker = FlightTracker(["US", "CA", "GB"])  # Custom override
    
    tracker = FlightTracker()  # Will load from tracked_countries.txt
    tracker.track_all_flights()


if __name__ == "__main__":
    main()
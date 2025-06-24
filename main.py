from FlightRadar24 import FlightRadar24API
import smtplib
import os
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class FlightTracker:
    def __init__(self):
        self.fr_api = FlightRadar24API()
        self.airport_countries = self._load_airport_countries()
        self.airports = {
            "Iraq": [
                "BGW",  # Baghdad International
                "BSR",  # Basra International
                "EBL",  # Erbil International
                "ISU",  # Sulaymaniyah International
                "NJF",  # Najaf International
                "OSM",  # Mosul International
                "KIK",  # Kirkuk International
                "TQD",  # Al Taqaddum Air Base
            ],
            "Iran": [
                "IKA",  # Tehran Imam Khomeini International
                "THR",  # Tehran Mehrabad International
                "MHD",  # Mashhad International
                "SYZ",  # Shiraz International
                "IFN",  # Isfahan International
                "TBZ",  # Tabriz International
                "AWZ",  # Ahvaz International
                "BND",  # Bandar Abbas International
                "ABD",  # Abadan Airport
                "KER",  # Kerman Airport
                "GSM",  # Qasem Soleimani International (Qeshm)
                "RAS",  # Rasht Airport
                "SRY",  # Sari Airport
                "ZBR",  # Chabahar Airport
                "ZAH",  # Zahedan International
                "BUZ",  # Bushehr Airport
                "KSH",  # Kermanshah Airport
                "HDM",  # Hamadan Airport
                "SXI",  # Sirri Island Airport
            ],
            "Israel": [
                "TLV",  # Ben Gurion International (Tel Aviv)
                "HFA",  # Haifa Airport
                "ETH",  # Eilat Airport
                "ETM",  # Ramon Airport (Eilat)
                "RPN",  # Rosh Pina Airport
                "VDA",  # Ovda Airport (Eilat)
            ],
            "Syria": [
                "DAM",  # Damascus International
                "ALP",  # Aleppo International
                "LTK",  # Latakia International
                "DEZ",  # Deir ez-Zor Airport
                "KAC",  # Qamishli Airport
            ],
            "Jordan": [
                "AMM",  # Queen Alia International (Amman)
                "ADJ",  # Amman Civil Airport (Marka)
                "AQJ",  # King Hussein International (Aqaba)
                "OMF",  # Mafraq Airport
            ],
            "Lebanon": [
                "BEY",  # Beirut Rafic Hariri International
                "KYE",  # Rene Mouawad Air Base (Kleiat)
            ],
        }

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

    def _get_country_code(self, airport_code):
        """Get country code for an airport code from the CSV data."""
        return self.airport_countries.get(airport_code, "Unknown")

    def _get_country_name(self, country_code):
        """Convert country code to full country name."""
        country_mapping = {
            "US": "USA",
            "IL": "Israel",
            "IQ": "Iraq",
            "IR": "Iran",
            "SY": "Syria",
            "JO": "Jordan",
            "LB": "Lebanon",
            "GB": "United Kingdom",
            "DE": "Germany",
            "FR": "France",
            "ES": "Spain",
            "IT": "Italy",
            "NL": "Netherlands",
            "BE": "Belgium",
            "CH": "Switzerland",
            "AT": "Austria",
            "SE": "Sweden",
            "NO": "Norway",
            "DK": "Denmark",
            "FI": "Finland",
            "RU": "Russia",
            "CN": "China",
            "JP": "Japan",
            "KR": "South Korea",
            "IN": "India",
            "AU": "Australia",
            "CA": "Canada",
            "BR": "Brazil",
            "MX": "Mexico",
            "AR": "Argentina",
            "TR": "Turkey",
            "EG": "Egypt",
            "SA": "Saudi Arabia",
            "AE": "UAE",
            "QA": "Qatar",
            "KW": "Kuwait",
            "BH": "Bahrain",
            "OM": "Oman",
            # Add more as needed
        }
        return country_mapping.get(country_code, country_code)

    def _load_css(self, css_filename):
        """Load CSS content from a file in the styles folder."""
        try:
            css_path = os.path.join("styles", css_filename)
            with open(css_path, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            print(f"Error loading CSS file {css_filename}: {e}")
            return ""

    def get_flights_to_country(self, country):
        flights = self.fr_api.get_flights()
        country_flights = []

        if country not in self.airports:
            print(f"Country '{country}' not found")
            return []

        for flight in flights:
            destination = getattr(flight, "destination_airport_iata", None)
            if destination and destination in self.airports[country]:
                country_flights.append(flight)

        return country_flights

    def track_all_flights(self):
        print("Flight Tracking Report")
        print("-" * 30)

        flight_report = []
        flight_details = []  # Store detailed flight info for email hyperlinks
        total_flights = 0

        for country in self.airports:
            flights = self.get_flights_to_country(country)
            flight_count = len(flights)
            total_flights += flight_count
            print(f"→  {country}: {flight_count} flights")

            if flight_count > 0:
                flight_report.append(f"{country}: {flight_count} flights")
                # Add some flight details
                for i, flight in enumerate(flights):
                    call_sign = getattr(flight, "callsign", "Unknown")
                    flight_id = getattr(flight, "id", "Unknown")
                    origin = getattr(flight, "origin_airport_iata", "Unknown")
                    destination = getattr(flight, "destination_airport_iata", "Unknown")

                    # Store detailed info for email
                    origin_country = self._get_country_code(origin)
                    destination_country = self._get_country_code(destination)

                    flight_details.append(
                        {
                            "call_sign": call_sign,
                            "flight_id": flight_id,
                            "origin": origin,
                            "destination": destination,
                            "origin_country": origin_country,
                            "destination_country": destination_country,
                            "country": country,
                        }
                    )

                    flight_report.append(
                        f"  - Flight {call_sign} (ID: {flight_id}): {origin} → {destination}"
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

                        container_html = f"""
                        <div class="country-container">
                            <div class="country-header">{current_country}: {country_count} {flight_word}</div>
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
                    &nbsp;&nbsp;&nbsp;&nbsp;{detail['origin']} ({detail['origin_country']}) → {detail['destination']} ({detail['destination_country']})
                </div>"""
                country_flights.append(flight_html)

            # Add the last country container
            if current_country is not None and country_flights:
                country_count = len(country_flights)
                flight_word = "flight" if country_count == 1 else "flights"

                container_html = f"""
                <div class="country-container">
                    <div class="country-header">{current_country}: {country_count} {flight_word}</div>
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
    tracker = FlightTracker()
    tracker.track_all_flights()


if __name__ == "__main__":
    main()

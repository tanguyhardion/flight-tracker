from FlightRadar24 import FlightRadar24API
import smtplib
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class FlightTracker:
    def __init__(self):
        self.fr_api = FlightRadar24API()
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
                    flight_details.append(
                        {
                            "call_sign": call_sign,
                            "flight_id": flight_id,
                            "origin": origin,
                            "destination": destination,
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

            # Build flight list with hyperlinks
            flight_html_list = []
            current_country = None

            for detail in flight_details:
                if current_country != detail["country"]:
                    current_country = detail["country"]
                    country_count = sum(
                        1 for d in flight_details if d["country"] == current_country
                    )
                    flight_word = "flight" if country_count == 1 else "flights"
                    flight_html_list.append(
                        f"<li class='country-header'>{current_country}: {country_count} {flight_word}</li>"
                    )

                # Create hyperlink to FlightRadar24
                flight_url = f"https://www.flightradar24.com/{detail['call_sign']}/{detail['flight_id']}"
                flight_html_list.append(
                    f"<li class='flight-item'>Flight <a href='{flight_url}' target='_blank' class='flight-link'>{detail['call_sign']} (ID: {detail['flight_id']})</a>: {detail['origin']} → {detail['destination']}</li>"
                )

            html_body = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    h2 {{
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                    }}
                    h3 {{
                        color: #34495e;
                        margin-top: 30px;
                        margin-bottom: 15px;
                    }}
                    .flight-list {{
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        list-style: none;
                        padding-left: 20px;
                    }}
                    .flight-list li {{
                        margin-bottom: 8px;
                        line-height: 1.4;
                    }}
                    .country-header {{
                        color: #495057;
                        font-size: 16px;
                        font-weight: bold;
                        margin-bottom: 10px;
                        margin-top: 20px;
                        border-bottom: 2px solid #dee2e6;
                        padding-bottom: 5px;
                    }}
                    .flight-item {{
                        margin-left: 20px;
                        margin-bottom: 5px;
                        padding: 8px;
                        background-color: #ffffff;
                        border-radius: 4px;
                        border-left: 3px solid #3498db;
                    }}
                    .flight-link {{
                        color: #007bff;
                        text-decoration: none;
                        font-weight: bold;
                    }}
                    .flight-link:hover {{
                        text-decoration: underline;
                    }}
                    .summary-card {{
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
                    }}
                    .summary-card-title {{
                        color: #495057;
                        font-size: 20px;
                        margin-bottom: 10px;
                        font-weight: bold;
                    }}
                    .timestamp {{
                        color: #6c757d;
                        font-style: italic;
                        margin-top: 30px;
                        text-align: center;
                    }}
                    .footer {{
                        border-top: 2px solid #dee2e6;
                        margin-top: 30px;
                        padding-top: 20px;
                        text-align: center;
                        color: #6c757d;
                    }}
                    a {{
                        color: #007bff;
                        text-decoration: none;
                    }}
                    a:hover {{
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h2>🛫 Flight Tracking Alert</h2>
                
                <ul class="flight-list">
                {''.join(flight_html_list)}
                </ul>
                
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

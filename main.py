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
                "ESB",  # Erbil International
                "ISU",  # Sulaymaniyah International
                "NJF",  # Najaf International
                "OSM",  # Mosul International
                "KIK",  # Kirkuk Air Base
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
                "GSM",  # Qasem Soleimani International (Gheshm)
                "RAS",  # Rasht Airport
                "SRY",  # Sari Airport
                "ZBR",  # Chabahar Airport
                "ZAH",  # Zahedan International
            ],
            "Israel": [
                "TLV",  # Ben Gurion International (Tel Aviv)
                "HFA",  # Haifa Airport
                "ETH",  # Eilat Airport
                "ETM",  # Ramon Airport (Eilat)
                "RPN",  # Rosh Pina Airport
                "MSR",  # Tel Nov Air Base (if tracking military)
            ],
            "Qatar": [
                "DOH",  # Hamad International Airport (Doha)
                "XJD",  # Al Udeid Air Base (if tracking military)
            ],
            "Kuwait": [
                "KWI",  # Kuwait International Airport
                "KAC",  # Kuwait Air Base (Ali Al Salem)
            ],
            "Bahrain": [
                "BAH",  # Bahrain International Airport
                "NAS",  # Naval Air Station Bahrain (if tracking military)
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
        """Send email notification when flights are detected using Outlook SMTP"""
        try:
            # Get email settings from environment variables
            sender_email = os.getenv("OUTLOOK_EMAIL")
            sender_password = os.getenv("OUTLOOK_PASSWORD")
            recipient_email = os.getenv("RECIPIENT_EMAIL")

            if not sender_email or not sender_password or not recipient_email:
                print("Email credentials missing - skipping email notification")
                print(
                    "Required: OUTLOOK_EMAIL, OUTLOOK_PASSWORD and RECIPIENT_EMAIL environment variables"
                )
                return

            # Outlook SMTP configuration
            smtp_server = "smtp-mail.outlook.com"
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
                    flight_html_list.append(
                        f"<li><strong>{current_country}: {country_count} flights</strong></li>"
                    )

                # Create hyperlink to FlightRadar24
                flight_url = f"https://www.flightradar24.com/{detail['call_sign']}/{detail['flight_id']}"
                flight_html_list.append(
                    f"<li style='margin-left: 20px;'>Flight <a href='{flight_url}' target='_blank'>{detail['call_sign']} (ID: {detail['flight_id']})</a>: {detail['origin']} → {detail['destination']}</li>"
                )

            html_body = f"""
            <html>
            <body>
                <h2>🛫 Flight Tracking Alert</h2>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>{total_flights} flights detected</strong> to your tracked destinations:</p>
                
                <ul>
                {''.join(flight_html_list)}
                </ul>
                
                <p><em>This is an automated notification from your flight tracking system.</em></p>
                <p><small>Click on any flight link to view it on FlightRadar24</small></p>
            </body>
            </html>
            """

            # Create HTML part
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

            # Send email using Outlook SMTP
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Enable encryption
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

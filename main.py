from FlightRadar24 import FlightRadar24API
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime


class FlightTracker:
    def __init__(self):
        self.fr_api = FlightRadar24API()
        self.airports = {
            "Israel": ["TLV", "SDV", "HFA"],
            "Iran": ["IKA", "MHD", "SYZ"],
            "Iceland": ["KEF", "RKV"],
            "France": ["CDG", "ORY", "LYS"],
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
        total_flights = 0

        for country in self.airports:
            flights = self.get_flights_to_country(country)
            flight_count = len(flights)
            total_flights += flight_count
            print(f"→  {country}: {flight_count} flights")
            
            if flight_count > 0:
                flight_report.append(f"{country}: {flight_count} flights")
                # Add some flight details
                for i, flight in enumerate(flights[:3]):  # Show first 3 flights
                    flight_id = getattr(flight, "id", "Unknown")
                    origin = getattr(flight, "origin_airport_iata", "Unknown")
                    destination = getattr(flight, "destination_airport_iata", "Unknown")
                    flight_report.append(f"  - Flight {flight_id}: {origin} → {destination}")
                if flight_count > 3:
                    flight_report.append(f"  ... and {flight_count - 3} more flights")
          # Send email if there are flights
        if total_flights > 0:
            self.send_email_notification(flight_report, total_flights)
        else:
            print("No flights detected - no email sent")
    
    def send_email_notification(self, flight_report, total_flights):
        """Send email notification when flights are detected"""
        try:
            # Email configuration from environment variables
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            recipient_email = os.getenv('RECIPIENT_EMAIL')
            
            if not all([sender_email, sender_password, recipient_email]):
                print("Email configuration missing - skipping email notification")
                return
            
            # Type assertions for email variables
            assert sender_email is not None
            assert sender_password is not None
            assert recipient_email is not None
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Flight Alert: {total_flights} flights detected"
            
            # Email body
            body = f"""
Flight Tracking Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{total_flights} flights detected to your tracked destinations:

{chr(10).join(flight_report)}

This is an automated notification from your flight tracking system.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
            
            print(f"✅ Email notification sent to {recipient_email}")
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")


def main():
    tracker = FlightTracker()
    tracker.track_all_flights()


if __name__ == "__main__":
    main()

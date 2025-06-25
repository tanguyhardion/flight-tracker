"""Core flight tracking functionality."""

from typing import List, Dict, Any, Optional
from FlightRadar24 import FlightRadar24API
from .data_loader import DataLoader, CountryLoader
from .email_service import EmailService


class FlightDetail:
    """Data class for flight details."""

    def __init__(self, flight, data_loader: DataLoader):
        self.call_sign = getattr(flight, "callsign", "Unknown")
        self.flight_id = getattr(flight, "id", "Unknown")
        self.origin = getattr(flight, "origin_airport_iata", "Unknown")
        self.destination = getattr(flight, "destination_airport_iata", "Unknown")

        # Resolve airport and country information
        self.origin_country = data_loader.get_airport_country(self.origin)
        self.destination_country = data_loader.get_airport_country(self.destination)
        self.origin_country_name = data_loader.get_country_name(self.origin_country)
        self.destination_country_name = data_loader.get_country_name(
            self.destination_country
        )
        self.origin_airport_name = data_loader.get_airport_name(self.origin)
        self.destination_airport_name = data_loader.get_airport_name(self.destination)

    def to_dict(self, country_code: str, country_name: str) -> Dict[str, Any]:
        """Convert to dictionary for email generation."""
        return {
            "call_sign": self.call_sign,
            "flight_id": self.flight_id,
            "origin": self.origin,
            "destination": self.destination,
            "origin_country": self.origin_country,
            "destination_country": self.destination_country,
            "origin_country_name": self.origin_country_name,
            "destination_country_name": self.destination_country_name,
            "origin_airport_name": self.origin_airport_name,
            "destination_airport_name": self.destination_airport_name,
            "country": country_code,
            "country_name": country_name,
        }


class FlightTracker:
    """Main flight tracking class."""

    def __init__(self, countries_to_track: Optional[List[str]] = None):
        self.fr_api = FlightRadar24API()
        self.data_loader = DataLoader()
        self.country_loader = CountryLoader(self.data_loader)
        self.email_service = EmailService()

        # Load countries to track
        if countries_to_track is None:
            self.countries_to_track = self.country_loader.load_countries_from_file()
        else:
            self.countries_to_track = countries_to_track

    def _get_flights_to_country(self, country_code: str) -> List[Any]:
        """Get flights to a specific country."""
        flights = self.fr_api.get_flights()
        country_flights = []

        # Get airports for this country
        country_airports = self.data_loader.get_country_airports(country_code)

        if not country_airports:
            country_name = self.data_loader.get_country_name(country_code)
            print(f"No airports found for {country_name} ({country_code}) in CSV data")
            return []

        country_name = self.data_loader.get_country_name(country_code)
        airport_display = country_airports[:5]
        if len(country_airports) > 5:
            airport_display.append("...")
        print(
            f"Tracking {len(country_airports)} airports for {country_name} ({country_code}): {airport_display}"
        )

        # Filter flights to this country
        for flight in flights:
            destination = getattr(flight, "destination_airport_iata", None)
            if destination and destination in country_airports:
                country_flights.append(flight)

        return country_flights

    def _create_flight_details(
        self, flights: List[Any], country_code: str
    ) -> List[Dict[str, Any]]:
        """Create detailed flight information for email."""
        flight_details = []
        country_name = self.data_loader.get_country_name(country_code)

        for flight in flights:
            detail = FlightDetail(flight, self.data_loader)
            flight_details.append(detail.to_dict(country_code, country_name))

        return flight_details

    def _print_flight_summary(self, country_code: str, flight_count: int) -> None:
        """Print flight summary for a country."""
        country_name = self.data_loader.get_country_name(country_code)
        print(f"→  {country_name}: {flight_count} flights")

    def _print_flight_details(self, flight_details: List[Dict[str, Any]]) -> List[str]:
        """Print and return flight details for console output."""
        flight_report = []

        for detail in flight_details:
            flight_info = (
                f"  - Flight {detail['call_sign']} (ID: {detail['flight_id']}): "
                f"{detail['origin_airport_name']} → {detail['destination_airport_name']}"
            )
            flight_report.append(flight_info)

        return flight_report

    def track_all_flights(self) -> None:
        """Track flights to all specified countries and send notifications."""
        print("Flight Tracking Report")
        print("-" * 30)

        # Display tracked countries
        tracked_country_names = [
            self.data_loader.get_country_name(code) for code in self.countries_to_track
        ]
        print(f"Tracking countries: {', '.join(tracked_country_names)}")
        print("-" * 30)

        flight_report = []
        all_flight_details = []
        total_flights = 0

        # Process each country
        for country_code in self.countries_to_track:
            flights = self._get_flights_to_country(country_code)
            flight_count = len(flights)
            total_flights += flight_count

            self._print_flight_summary(country_code, flight_count)

            if flight_count > 0:
                country_name = self.data_loader.get_country_name(country_code)
                flight_report.append(f"{country_name}: {flight_count} flights")

                # Create detailed flight information
                flight_details = self._create_flight_details(flights, country_code)
                all_flight_details.extend(flight_details)

                # Print flight details to console
                detailed_reports = self._print_flight_details(flight_details)
                flight_report.extend(detailed_reports)

        # Send email notification if flights were found
        if total_flights > 0:
            self.email_service.send_notification(total_flights, all_flight_details)
        else:
            print("No flights detected - no email sent")

    def get_tracked_countries(self) -> List[str]:
        """Get list of currently tracked country codes."""
        return self.countries_to_track.copy()

    def get_tracked_country_names(self) -> List[str]:
        """Get list of currently tracked country names."""
        return [
            self.data_loader.get_country_name(code) for code in self.countries_to_track
        ]

    def add_country(self, country_code: str) -> bool:
        """Add a country to track."""
        if country_code not in self.countries_to_track:
            # Validate country exists
            if country_code in self.data_loader.get_all_country_codes():
                self.countries_to_track.append(country_code)
                return True
            else:
                print(f"Country code '{country_code}' not found in available countries")
                return False
        return False

    def remove_country(self, country_code: str) -> bool:
        """Remove a country from tracking."""
        if country_code in self.countries_to_track:
            self.countries_to_track.remove(country_code)
            return True
        return False

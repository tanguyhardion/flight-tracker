"""Command-line interface for the flight tracker."""

import argparse
import sys
from typing import List, Optional
from .flight_tracker import FlightTracker
from .data_loader import DataLoader


class FlightTrackerCLI:
    """Command-line interface for flight tracker operations."""

    def __init__(self):
        self.data_loader = DataLoader()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description="Flight Tracker - Monitor flights to specific countries",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                          # Run with countries from tracked_countries.txt
  %(prog)s --countries US CA GB     # Track specific countries by code
  %(prog)s --list-countries         # List all available countries
  %(prog)s --show-config            # Show current configuration
            """,
        )

        parser.add_argument(
            "--countries", nargs="+", help="Country codes to track (e.g., US CA GB)"
        )

        parser.add_argument(
            "--list-countries",
            action="store_true",
            help="List all available countries and their codes",
        )

        parser.add_argument(
            "--show-config", action="store_true", help="Show current configuration"
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without sending email notifications",
        )

        return parser

    def _list_countries(self) -> None:
        """List all available countries."""
        print("Available Countries:")
        print("-" * 50)

        # Get all country codes and names
        all_codes = sorted(self.data_loader.get_all_country_codes())

        for code in all_codes:
            name = self.data_loader.get_country_name(code)
            airports = self.data_loader.get_country_airports(code)
            airport_count = len(airports)
            print(f"{code:3} - {name:30} ({airport_count} airports)")

    def _show_config(self) -> None:
        """Show current configuration."""
        from .config import Config

        print("Flight Tracker Configuration:")
        print("-" * 50)
        print(f"Tracked Countries File: {Config.TRACKED_COUNTRIES_FILE}")
        print(f"Airports CSV: {Config.AIRPORTS_CSV}")
        print(f"Countries CSV: {Config.COUNTRIES_CSV}")
        print(f"Email CSS: {Config.EMAIL_CSS}")
        print()
        print("Email Configuration:")
        print(
            f"Gmail Email: {'✓' if Config.GMAIL_EMAIL else '✗'} {Config.GMAIL_EMAIL or 'Not set'}"
        )
        print(
            f"Gmail Password: {'✓' if Config.GMAIL_APP_PASSWORD else '✗'} {'Set' if Config.GMAIL_APP_PASSWORD else 'Not set'}"
        )
        print(
            f"Recipient Email: {'✓' if Config.RECIPIENT_EMAIL else '✗'} {Config.RECIPIENT_EMAIL or 'Not set'}"
        )
        print(f"SMTP Server: {Config.SMTP_SERVER}:{Config.SMTP_PORT}")

    def _validate_countries(self, country_codes: List[str]) -> List[str]:
        """Validate and filter country codes."""
        valid_codes = []
        available_codes = self.data_loader.get_all_country_codes()

        for code in country_codes:
            code = code.upper()
            if code in available_codes:
                valid_codes.append(code)
            else:
                print(f"Warning: Country code '{code}' not found")

        return valid_codes

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI with the given arguments."""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        try:
            if parsed_args.list_countries:
                self._list_countries()
                return 0

            if parsed_args.show_config:
                self._show_config()
                return 0

            # Determine countries to track
            countries_to_track = None
            if parsed_args.countries:
                countries_to_track = self._validate_countries(parsed_args.countries)
                if not countries_to_track:
                    print("No valid countries specified")
                    return 1

            # Create and run flight tracker
            tracker = FlightTracker(countries_to_track)

            if parsed_args.dry_run:
                print("DRY RUN MODE - No emails will be sent")
                # Temporarily disable email service
                tracker.email_service = None

            tracker.track_all_flights()
            return 0

        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 1
        except Exception as e:
            print(f"Error: {e}")
            return 1


def main():
    """Main CLI entry point."""
    cli = FlightTrackerCLI()
    sys.exit(cli.run())

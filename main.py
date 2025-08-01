"""Main entry point for the flight tracker application."""
import sys
import os

# Add the project root to the Python path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.flight_tracker import FlightTracker


def main():
    """Main function to run the flight tracker."""
    # Create flight tracker instance
    # Countries will be loaded from tracked_countries.txt automatically
    # You can also override by passing a list if needed:
    # tracker = FlightTracker(["US", "CA", "GB"])  # Custom override
    
    tracker = FlightTracker()  # Will load from tracked_countries.txt
    tracker.track_all_flights()


if __name__ == "__main__":
    main()

# Flight Tracker

A Python application that monitors flights to specific countries and sends email notifications when flights are detected.

## Project Structure

```
flight-tracker/
├── src/                          # Main source code
│   ├── __init__.py
│   ├── config.py                 # Configuration and environment settings
│   ├── data_loader.py           # Data loading utilities
│   ├── flight_tracker.py       # Core flight tracking logic
│   ├── email_service.py         # Email notification service
│   ├── html_generator.py        # HTML email generation
│   ├── utils.py                 # Utility functions
│   └── main.py                  # Entry point (when running as module)
├── data/                        # Data files
│   ├── airports.csv            # Airport data
│   └── countries.csv           # Country data
├── styles/                      # CSS styles
│   └── email.css               # Email styling
├── tracked_countries.txt       # Countries to track
├── requirements.txt            # Python dependencies
├── main.py                     # Original main file (deprecated)
├── main_new.py                 # New main entry point
└── README_NEW.md              # This file
```

## Features

- **Modular Design**: Separated into logical modules for better maintainability
- **Configuration Management**: Centralized configuration with environment variable support
- **Data Loading**: Efficient loading and caching of airport and country data
- **Email Notifications**: HTML email notifications with flight details and links
- **Error Handling**: Comprehensive error handling and logging
- **Extensible**: Easy to add new features and modify existing ones

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in a `.env` file:
```
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
```

## Usage

### Basic Usage

Run with countries from `tracked_countries.txt`:
```bash
python main_new.py
```

### As a Module

```python
from src.flight_tracker import FlightTracker

# Use default countries from file
tracker = FlightTracker()
tracker.track_all_flights()

# Use specific countries
tracker = FlightTracker(["US", "CA", "GB"])
tracker.track_all_flights()

# Add/remove countries dynamically
tracker.add_country("FR")
tracker.remove_country("GB")
```

## Module Descriptions

### `config.py`
Centralized configuration management with environment variable support and validation.

### `data_loader.py`
Handles loading and caching of CSV data files. Includes:
- `DataLoader`: Main data loading class with lazy loading
- `CountryLoader`: Loads tracked countries from file

### `flight_tracker.py`
Core flight tracking functionality:
- `FlightDetail`: Data class for flight information
- `FlightTracker`: Main tracking class with country management

### `email_service.py`
Email notification service with HTML email generation and SMTP handling.

### `html_generator.py`
Generates HTML content for email notifications with proper styling and flight grouping.

### `cli.py`
Command-line interface with comprehensive options and help text.

### `utils.py`
Common utility functions used across modules.

## Configuration

### Environment Variables
- `GMAIL_EMAIL`: Your Gmail address
- `GMAIL_APP_PASSWORD`: Gmail app password (not regular password)
- `RECIPIENT_EMAIL`: Email address to receive notifications

### Files
- `tracked_countries.txt`: List of country names to track (one per line)
- `data/airports.csv`: Airport information with IATA codes
- `data/countries.csv`: Country information with ISO codes
- `styles/email.css`: CSS styling for email notifications

## Error Handling

The application includes comprehensive error handling:
- Missing configuration files use sensible defaults
- Invalid country codes are warned about and skipped
- Email failures are logged but don't crash the application
- CSV loading errors are handled gracefully

## Extending the Application

### Adding New Data Sources
1. Create a new loader class in `data_loader.py`
2. Add configuration options in `config.py`
3. Update the main `FlightTracker` class to use the new data

### Adding New Notification Methods
1. Create a new service class similar to `EmailService`
2. Add configuration options in `config.py`
3. Update the `FlightTracker` to use multiple notification services

### Adding New CLI Commands
1. Add new arguments to the parser in `cli.py`
2. Implement the corresponding functionality
3. Update the help text and examples

## Migration from Old Code

The old `main.py` has been refactored into multiple modules:

- Configuration → `config.py`
- Data loading → `data_loader.py`
- Flight tracking → `flight_tracker.py`
- Email → `email_service.py`
- HTML generation → `html_generator.py`
- CLI → `cli.py`

All functionality is preserved, but now organized in a more maintainable structure.

## Dependencies

- `FlightRadarAPI`: For accessing flight data
- `python-dotenv`: For environment variable management
- Standard library modules: `smtplib`, `csv`, `os`, `datetime`, `email`

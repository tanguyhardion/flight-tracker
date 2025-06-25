"""Data loading utilities for flight tracker."""
import csv
import os
from typing import Dict, List, Set
from .config import Config


class DataLoader:
    """Handles loading and caching of CSV data and country information."""
    
    def __init__(self):
        self._airport_countries: Dict[str, str] = {}
        self._country_airports: Dict[str, List[str]] = {}
        self._country_codes_to_names: Dict[str, str] = {}
        self._country_names_to_codes: Dict[str, str] = {}
        self._airport_names: Dict[str, str] = {}
        self._loaded = False
    
    def _ensure_loaded(self) -> None:
        """Ensure all data is loaded. Lazy loading pattern."""
        if not self._loaded:
            self._load_all_data()
            self._loaded = True
    
    def _load_all_data(self) -> None:
        """Load all CSV data files."""
        self._load_airports_data()
        self._load_countries_data()
        self._build_reverse_mappings()
    
    def _load_airports_data(self) -> None:
        """Load airport data from CSV file."""
        try:
            with open(Config.AIRPORTS_CSV, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    airport_code = row.get("code")
                    airport_name = row.get("name")
                    country_code = row.get("country")
                    
                    if airport_code and country_code:
                        # Map airport to country
                        self._airport_countries[airport_code] = country_code
                        
                        # Group airports by country
                        if country_code not in self._country_airports:
                            self._country_airports[country_code] = []
                        self._country_airports[country_code].append(airport_code)
                        
                        # Map airport code to name
                        if airport_name:
                            self._airport_names[airport_code] = airport_name
                            
        except Exception as e:
            print(f"Error loading airports data: {e}")
    
    def _load_countries_data(self) -> None:
        """Load country data from CSV file."""
        try:
            with open(Config.COUNTRIES_CSV, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    country_code = row.get("alpha-2")
                    country_name = row.get("name")
                    
                    if country_code and country_name:
                        self._country_codes_to_names[country_code] = country_name
                        
        except Exception as e:
            print(f"Error loading countries data: {e}")
    
    def _build_reverse_mappings(self) -> None:
        """Build reverse mappings for efficient lookups."""
        self._country_names_to_codes = {
            name: code for code, name in self._country_codes_to_names.items()
        }
    
    def get_airport_country(self, airport_code: str) -> str:
        """Get country code for an airport."""
        self._ensure_loaded()
        return self._airport_countries.get(airport_code, "Unknown")
    
    def get_country_airports(self, country_code: str) -> List[str]:
        """Get list of airports for a country."""
        self._ensure_loaded()
        return self._country_airports.get(country_code, [])
    
    def get_country_name(self, country_code: str) -> str:
        """Get country name for a country code."""
        self._ensure_loaded()
        return self._country_codes_to_names.get(country_code, country_code)
    
    def get_country_code(self, country_name: str) -> str:
        """Get country code for a country name."""
        self._ensure_loaded()
        return self._country_names_to_codes.get(country_name, "")
    
    def get_airport_name(self, airport_code: str) -> str:
        """Get airport name for an airport code."""
        self._ensure_loaded()
        return self._airport_names.get(airport_code, airport_code)
    
    def get_all_country_codes(self) -> Set[str]:
        """Get all available country codes."""
        self._ensure_loaded()
        return set(self._country_codes_to_names.keys())
    
    def get_all_country_names(self) -> Set[str]:
        """Get all available country names."""
        self._ensure_loaded()
        return set(self._country_names_to_codes.keys())
    

class CountryLoader:
    """Handles loading of tracked countries from file."""
    
    def __init__(self, data_loader: DataLoader):
        self.data_loader = data_loader
    
    def load_countries_from_file(self, filename: str = None) -> List[str]:
        """Load country names from a text file and convert to country codes."""
        if filename is None:
            filename = Config.TRACKED_COUNTRIES_FILE
            
        countries = []
        
        try:
            with open(filename, "r", encoding="utf-8") as file:
                for line in file:
                    country_name = line.strip()
                    if country_name:  # Skip empty lines
                        country_code = self.data_loader.get_country_code(country_name)
                        if country_code:
                            countries.append(country_code)
                        else:
                            print(f"Warning: Country '{country_name}' not found in countries.csv")
            
            if not countries:
                print(f"No valid countries found in {filename}, using default countries")
                return Config.DEFAULT_COUNTRIES
            
            # Convert codes to names for logging
            country_names = [self.data_loader.get_country_name(code) for code in countries]
            print(f"Loaded {len(countries)} countries from {filename}: {country_names}")
            return countries
            
        except FileNotFoundError:
            print(f"File {filename} not found, using default countries")
            return Config.DEFAULT_COUNTRIES
        except Exception as e:
            print(f"Error loading countries from {filename}: {e}")
            return Config.DEFAULT_COUNTRIES

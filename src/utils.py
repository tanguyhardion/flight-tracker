"""Utility functions for the flight tracker."""

from typing import List, Dict, Any
import os


def validate_file_exists(filepath: str, description: str = "File") -> bool:
    """Validate that a file exists and print a helpful message if not."""
    if os.path.exists(filepath):
        return True
    else:
        print(f"{description} not found: {filepath}")
        return False


def format_flight_count(count: int) -> str:
    """Format flight count with proper singular/plural."""
    return "flight" if count == 1 else "flights"


def print_separator(char: str = "-", length: int = 50) -> None:
    """Print a separator line."""
    print(char * length)


def group_by_key(
    items: List[Dict[str, Any]], key: str
) -> Dict[str, List[Dict[str, Any]]]:
    """Group a list of dictionaries by a specific key."""
    grouped = {}
    for item in items:
        group_key = item.get(key, "Unknown")
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped


def safe_get_attr(obj: Any, attr: str, default: Any = "Unknown") -> Any:
    """Safely get an attribute from an object with a default value."""
    return getattr(obj, attr, default)

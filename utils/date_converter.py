"""
Date conversion utilities used by FastAPI endpoints.
"""

from datetime import datetime


class DateConverter:
    def convert_date_to_time(self, givenDate: str) -> str:
        """
        Convert a given date-time to milliseconds since the Unix epoch (January 1, 1970).

        Supports multiple formats:
        - DD-MM-YYYY HH:MMAM/PM (e.g., "01-12-2025 02:30PM")
        - ISO 8601 (e.g., "2025-12-01T14:30:00")
        - ISO date only (e.g., "2025-12-01")

        Args:
            givenDate (str): The date-time string in one of the supported formats.

        Returns:
            str: The equivalent time in milliseconds since Unix epoch.
        """
        # Try ISO format first (YYYY-MM-DDTHH:MM:SS)
        if "T" in givenDate:
            try:
                dt = datetime.fromisoformat(givenDate.replace("Z", "+00:00"))
                milliseconds = int(dt.timestamp() * 1000)
                return str(milliseconds)
            except ValueError:
                pass

        # Try ISO date only (YYYY-MM-DD)
        if givenDate.count("-") == 2 and " " not in givenDate and "T" not in givenDate:
            try:
                dt = datetime.fromisoformat(givenDate)
                milliseconds = int(dt.timestamp() * 1000)
                return str(milliseconds)
            except ValueError:
                pass

        # Fall back to DD-MM-YYYY HH:MMAM/PM format
        if " " not in givenDate:
            raise ValueError(f"Invalid date format: {givenDate}. Expected one of: 'DD-MM-YYYY HH:MMAM/PM', 'YYYY-MM-DDTHH:MM:SS', or 'YYYY-MM-DD'")

        try:
            date_str, time_str = givenDate.split()
            day, month, year = map(int, date_str.split('-'))
            time_obj = datetime.strptime(time_str, "%I:%M%p")
            target_date = datetime(year, month, day, time_obj.hour, time_obj.minute)
            milliseconds = int(target_date.timestamp() * 1000)
            return str(milliseconds)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid DD-MM-YYYY HH:MMAM/PM format: {givenDate}. Error: {e}")


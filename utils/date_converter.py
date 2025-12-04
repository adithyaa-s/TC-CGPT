"""
Date conversion utilities used by FastAPI endpoints.
"""

from datetime import datetime


class DateConverter:
    def convert_date_to_time(self, givenDate: str) -> str:
        """
        Convert a given date-time in the format DD-MM-YYYY HH:MMAM/PM to milliseconds
        since the Unix epoch (January 1, 1970).

        Args:
            givenDate (str): The date-time string in DD-MM-YYYY HH:MMAM/PM format.

        Returns:
            str: The equivalent time in milliseconds since Unix epoch.
        """

        date_str, time_str = givenDate.split()
        day, month, year = map(int, date_str.split('-'))
        time_obj = datetime.strptime(time_str, "%I:%M%p")
        target_date = datetime(year, month, day, time_obj.hour, time_obj.minute)
        milliseconds = int(target_date.timestamp() * 1000)
        return str(milliseconds)


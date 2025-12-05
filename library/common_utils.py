# library/common_utils.py

import os
import requests
from utils.oauth import ZohoOAuth
from utils.user_oauth import get_user_org_info
from datetime import datetime

class TrainerCentralCommon:
    """
    Shared helper for common TrainerCentral API operations.
    Provides base URL, OAuth token, and generic delete functionality.
    
    NOTE: This class now uses per-user org info fetched from portals API.
    The ORG_ID and DOMAIN are retrieved dynamically from the user session
    instead of being hardcoded environment variables.
    """
    def __init__(self):
        # Get org info from user session (stored during OAuth flow)
        org_info = get_user_org_info()
        self.ORG_ID = org_info.get("org_id") or os.getenv("ORG_ID")
        self.DOMAIN = org_info.get("domain") or os.getenv("DOMAIN")
        
        if not self.ORG_ID or not self.DOMAIN:
            raise ValueError("ORG_ID and DOMAIN must be configured via user OAuth flow or environment variables")
        
        self.base_url = f"{self.DOMAIN}/api/v4/{self.ORG_ID}"
        self.oauth = ZohoOAuth()

    def delete_resource(self, resource: str, resource_id: str) -> dict:
        """
        Delete a generic resource.

        Args:
            resource (str): the resource path (e.g. "sessions", "courses", "course/<courseId>/sections")
            resource_id (str): the ID of the resource to delete.

        Returns:
            dict: API response JSON.
        """
        request_url = f"{self.base_url}/{resource}/{resource_id}.json"
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        response = requests.delete(request_url, headers=headers)
        return response.json()




class DateConverter:
    def convert_date_to_time(self, givenDate: str) -> str:
        """ 
        Convert a given date-time in the format DD-MM-YYYY HH:MMAM/PM to milliseconds 
        since the Unix epoch (January 1, 1970).
        
        Args:
            givenDate (str): The date-time string in DD-MM-YYYY HH:MMAM/PM format.
        
        Returns:
            str: The equivalent time in milliseconds since Unix epoch.
        
        Example:
            convert_date_to_time("29-11-2025 4:30PM") -> "1732882800000"
        """

        date_str, time_str = givenDate.split() 
        day, month, year = map(int, date_str.split('-'))
        time_obj = datetime.strptime(time_str, "%I:%M%p")  
        target_date = datetime(year, month, day, time_obj.hour, time_obj.minute)
        milliseconds = int(target_date.timestamp() * 1000)
        return str(milliseconds)

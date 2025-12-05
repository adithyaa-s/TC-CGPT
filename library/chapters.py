"""
TrainerCentral Chapters (Sections) API Wrapper.
"""

import os
import requests
from utils.user_oauth import get_user_org_info
from .oauth import ZohoOAuth


class TrainerCentralChapters:
    """
    Provides helper functions to interact with TrainerCentral's
    chapter (section) APIs.
    
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

    def create_chapter(self, section_data: dict):
        """
        Create a chapter under a course.

        API (Create chapter) details:
        - Method: POST
        - Endpoint: /api/v4/<orgId>/sections.json
        - OAuth Scope: TrainerCentral.sectionapi.CREATE

        Body:
        {
            "section": {
                "courseId": "<courseId>",
                "name": "<chapter name>"
            }
        }

        Args:
            section_data (dict): e.g.
                {
                    "courseId": "3000094000002000004",
                    "name": "Introduction"
                }

        Returns:
            dict: API response containing the created section.
        """
        request_url = f"{self.base_url}/sections.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }
        data = {"section": section_data}

        return requests.post(request_url, json=data, headers=headers).json()

    def update_chapter(self, course_id: str, section_id: str, updates: dict):
        """
        Edit a chapter name or reorder a chapter inside a course.

        API (Edit chapter) details:
        - Method: PUT
        - Endpoint:
          /api/v4/<orgId>/course/<courseId>/sections/<sectionId>.json
        - OAuth Scope: TrainerCentral.sectionapi.UPDATE

        Body:
        {
            "section": {
                "name": "<chapter name>",
                "sectionIndex": 0        # only when reordering
            }
        }

        Args:
            course_id (str): ID of the course that owns the chapter.
            section_id (str): ID of the chapter (section).
            updates (dict): fields to update.

        Returns:
            dict: API response containing the updated section.
        """
        request_url = (
            f"{self.base_url}/course/{course_id}/sections/{section_id}.json"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }
        data = {"section": updates}

        return requests.put(request_url, json=data, headers=headers).json()

    def delete_chapter(self, course_id: str, section_id: str):
        """
        Delete a chapter from a course.

        API (Delete chapter) details:
        - Method: DELETE
        - Endpoint:
          /api/v4/<orgId>/course/<courseId>/sections/<sectionId>.json
        - OAuth Scope: TrainerCentral.sectionapi.DELETE

        Args:
            course_id (str): ID of the course.
            section_id (str): ID of the chapter (section).

        Returns:
            dict: Response JSON from the delete call.
        """
        request_url = (
            f"{self.base_url}/course/{course_id}/sections/{section_id}.json"
        )
        headers = {
            "Authorization": f"Bearer {self.oauth.get_access_token()}",
        }

        return requests.delete(request_url, headers=headers).json()

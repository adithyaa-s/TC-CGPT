"""
TrainerCentral Course Management API Wrapper.
"""

import os
import requests
from utils.oauth import ZohoOAuth
from utils.user_oauth import get_user_org_info


class TrainerCentralCourses:
    """
    Provides helper functions to interact with TrainerCentral's course APIs.
    
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

    def post_course(self, course_data: dict):
        """
        Create a new course in TrainerCentral.

        API (Create Course) details:
        - Method: POST  
        - Endpoint: /api/v4/{orgId}/courses.json  
        - OAuth Scope: TrainerCentral.courseapi.CREATE  

        Body format:
        {
            "course": {
                "courseName": "<Course Title>",
                "subTitle": "<Subtitle>",
                "description": "<Description>",
                "courseCategories": [
                    {"categoryName": "Category1"},
                    {"categoryName": "Category2"}
                ]
            }
        }

        Returns:
            dict: API response containing created course, ticket, category mapping, etc.
        """
        request_url = f"{self.base_url}/courses.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        data = {"course": course_data}

        return requests.post(request_url, json=data, headers=headers).json()

    def get_course(self, course_id: str):
        """
        Fetch the details of a single course.

        API (View Course) details:
        - Method: GET  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  

        Returns:
            dict: Contains course details such as:
                - id / courseId  
                - courseName  
                - subTitle  
                - description  
                - links to sessions, tickets, etc.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.get(request_url, headers=headers).json()

    def list_courses(self):
        """
        List all courses (or paginated subset) from TrainerCentral.

        API (List Courses) details:
        - Method: GET  
        - Endpoint: /api/v4/{orgId}/courses.json  
        - Query Params:
            * limit  
            * si (start index)

        Returns:
            dict with:
            - "courses": list of courses  
            - "courseCategories": mapping data  
            - "meta": includes totalCourseCount
        """
        request_url = f"{self.base_url}/courses.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.get(request_url, headers=headers).json()

    def update_course(self, course_id: str, updates: dict):
        """
        Edit/update an existing TrainerCentral course.

        API (Edit Course) details:
        - Method: PUT  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  
        - OAuth Scope: TrainerCentral.courseapi.UPDATE  

        Body:
        {
            "course": {
                "courseName": "<New Title>",
                "subTitle": "<New Subtitle>",
                "description": "<Updated Description>",
                "courseCategories": [
                    {"categoryName": "Category1"},
                    {"categoryName": "Category2"}
                ]
            }
        }

        Returns:
            dict: Response containing the updated course object.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.oauth.get_access_token()}"
        }
        data = {"course": updates}

        return requests.put(request_url, json=data, headers=headers).json()

    def delete_course(self, course_id: str):
        """
        Permanently delete a TrainerCentral course.

        API (Delete Course) details:
        - Method: DELETE  
        - Endpoint: /api/v4/{orgId}/courses/{courseId}.json  
        - OAuth Scope: TrainerCentral.courseapi.DELETE  

        Returns:
            dict: Response JSON from the delete call.
        """
        request_url = f"{self.base_url}/courses/{course_id}.json"
        headers = {"Authorization": f"Bearer {self.oauth.get_access_token()}"}

        return requests.delete(request_url, headers=headers).json()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

from library.courses import TrainerCentralCourses

router = APIRouter(prefix="/courses", tags=["courses"])


class CourseCreateRequest(BaseModel):
    courseName: str
    subTitle: Optional[str] = None
    description: Optional[str] = None
    courseCategories: Optional[list[Any]] = None


class CourseUpdateRequest(BaseModel):
    courseName: Optional[str] = None
    subTitle: Optional[str] = None
    description: Optional[str] = None
    courseCategories: Optional[list[Any]] = None


@router.post("/", summary="Create a new course")
async def create_course(body: CourseCreateRequest, orgId: str, access_token: str):
    """Create a new course in TrainerCentral.
    
    This endpoint creates a new course with metadata such as name, subtitle,
    description, and category mappings.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        body (CourseCreateRequest): Course metadata
            - courseName (str, required): The title of the course
            - subTitle (str, optional): Subtitle or tagline
            - description (str, optional): Long-form description
            - courseCategories (list, optional): List of category objects, e.g. [{ "categoryName": "Category1" }]

        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: API response containing created course details, including:
            - course ID
            - course name and metadata
            - ticket mappings (if applicable)
            - category mappings
    
    Raises:
        HTTPException: 400/500 if course creation fails
    
    Example:
        POST /courses/
        {
            "courseName": "Python Basics",
            "subTitle": "An introduction to Python programming",
            "description": "Learn the fundamentals of Python...",
            "courseCategories": [{"categoryName": "Programming"}]
        }
    """
    tc = TrainerCentralCourses()
    return tc.post_course(body.dict(), orgId, access_token)


@router.get("/{course_id}", summary="Get course by ID")
async def get_course(course_id: str, orgId: str, access_token: str):
    """Retrieve detailed information about a specific course.
    
    Note: Provide orgId and access token of the user, after OAuth, as parameters.  

    Args:
        course_id (str): The unique identifier of the course
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Complete course object with:
            - id / courseId
            - courseName, subTitle, description
            - deliveryMode
            - links to sessions, chapters, materials
            - enrollment and completion statistics
            
    
    Raises:
        HTTPException: 404 if course not found, 500 if API call fails
    
    Example:
        GET /courses/19208000000035003
    """
    tc = TrainerCentralCourses()
    return tc.get_course(course_id, orgId, access_token)


@router.get("/", summary="List all courses")
async def list_courses(orgId: str, access_token: str):
    """List all available courses in the organization.

    Args:
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Array of course objects with metadata. Each course includes:
            - courseId, courseName, subTitle
            - description, deliveryMode
            - enrollment count, completion status
            - timestamps (created, updated)
    
    Raises:
        HTTPException: 500 if list request fails
    
    Note:
        Provide orgId and access token of the user, after OAuth, as parameters.  
        Pagination is not currently implemented. For large course libraries,
        consider filtering by status or date range in a future update.
    
    Example:
        GET /courses/
    """
    tc = TrainerCentralCourses()
    return tc.list_courses(orgId, access_token)


@router.put("/{course_id}", summary="Update a course")
async def update_course(course_id: str, body: CourseUpdateRequest, orgId: str, access_token: str):
    """Update an existing course's metadata.
    
    Allows modification of course name, subtitle, description, and categories.
    Only provided fields are updated; omitted fields remain unchanged.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        course_id (str): The ID of the course to update
        body (CourseUpdateRequest): Fields to update (all optional)
            - courseName: New course title
            - subTitle: New subtitle
            - description: New description
            - courseCategories: Updated category mappings
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Updated course object with all metadata
    
    Raises:
        HTTPException: 404 if course not found, 500 if update fails
    
    Example:
        PUT /courses/19208000000035003
        {
            "courseName": "Advanced Python Programming",
            "description": "Deep dive into Python...."
        }
    """
    tc = TrainerCentralCourses()
    return tc.update_course(course_id, body.dict(exclude_unset=True), orgId, access_token)


@router.delete("/{course_id}", summary="Delete a course")
async def delete_course(course_id: str, orgId: str, access_token: str):
    """Permanently delete a course from the organization.
    
    WARNING: This action cannot be undone. All associated sessions, chapters,
    materials, and enrollment records will be deleted.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        course_id (str): The ID of the course to delete
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user

    
    Returns:
        dict: Confirmation response with deletion status
    
    Raises:
        HTTPException: 404 if course not found, 500 if deletion fails
    
    Example:
        DELETE /courses/19208000000035003
    """
    tc = TrainerCentralCourses()
    return tc.delete_course(course_id, orgId, access_token)

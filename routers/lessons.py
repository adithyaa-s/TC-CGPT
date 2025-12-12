from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional

from library.lessons import TrainerCentralLessons

router = APIRouter(prefix="/lessons", tags=["lessons"])


class LessonCreateRequest(BaseModel):
    """Request body for creating a lesson with content.
    
    Attributes:
        session_data (dict): Lesson metadata such as:
            - name: Lesson title (required)
            - courseId: Parent course ID (required)
            - sectionId: Parent section/chapter ID (optional)
            - deliveryMode: Delivery mode (4 = content-based lesson)
            - description: Short blurb (optional)
        content_html (str): Full lesson body in HTML format
        content_filename (str): Display name for the content file (default: "Content")
    """
    session_data: dict
    content_html: str
    content_filename: Optional[str] = "Content"


class LessonUpdateRequest(BaseModel):
    updates: dict


@router.post("/create", summary="Create a lesson under a course")
async def create_lesson(body: LessonCreateRequest, orgId: str, access_token: str):
    """Create a lesson (session) with rich-text content under a course.
    
    This endpoint creates a new lesson/session with full HTML content and associates
    it with a course and optionally a section/chapter. The content is uploaded separately
    after the session is created.
    
    Args:
        body (LessonCreateRequest): Lesson creation payload
            - session_data (dict): Lesson metadata including:
                - name: Lesson title (required)
                - courseId: Parent course ID (required)
                - sectionId: Parent section/chapter ID (optional)
                - deliveryMode: Delivery mode (4 for content-based lesson)
                - description: Short blurb (optional)
            - content_html (str): Full lesson body in HTML format
            - content_filename (str): Display name for content file
        
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Response object containing:
            - lesson: Session creation response (includes sessionId)
            - content: Content upload response
    
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    
    Example:
        POST /lessons/create
        {
            "session_data": {
                "name": "Introduction to Web Development",
                "courseId": "19208000000035003",
                "sectionId": "19208000000042002",
                "deliveryMode": 4,
                "description": "Learn the basics of HTML, CSS, and JavaScript"
            },
            "content_html": "<h2>Getting Started</h2><p>HTML is the foundation...</p>",
            "content_filename": "Intro to Web Dev"
        }
    """
    tc = TrainerCentralLessons()
    return tc.create_lesson_with_content(body.session_data, body.content_html, body.content_filename, orgId, access_token)


@router.put("/{session_id}", summary="Update a lesson/session")
async def update_lesson(session_id: str, body: LessonUpdateRequest, orgId: str, access_token: str):
    """Update an existing lesson/session metadata.
    
    Allows modification of lesson properties such as name, description, and schedule.
    Only provided fields are updated; omitted fields remain unchanged.
    
    Args:
        session_id (str): The ID of the lesson/session to update
        body (LessonUpdateRequest): Fields to update
            - updates (dict): Dictionary of session properties to modify, e.g.
                {
                    "name": "Updated Lesson Title",
                    "description": "New description",
                    "isActive": true
                }
        
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Updated session object with all metadata
    
    Raises:
        HTTPException: 404 if session not found, 500 if update fails
    
    Example:
        PUT /lessons/19208000000050001
        {
            "updates": {
                "name": "Advanced Web Development",
                "description": "Covering frameworks and best practices"
            }
        }
    """
    tc = TrainerCentralLessons()
    return tc.update_lesson(session_id, body.updates, orgId, access_token)


@router.delete("/{session_id}", summary="Delete a lesson/session")
async def delete_lesson(session_id: str, orgId: str, access_token: str):
    """Permanently delete a lesson/session from the course.
    
    WARNING: This action cannot be undone. All associated content, materials,
    and learner interactions will be deleted.
    
    Args:
        session_id (str): The ID of the lesson/session to delete
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Confirmation response with deletion status
    
    Raises:
        HTTPException: 404 if session not found, 500 if deletion fails
    
    Example:
        DELETE /lessons/19208000000050001
    """
    tc = TrainerCentralLessons()
    return tc.delete_lesson(session_id, orgId, access_token)

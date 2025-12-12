from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from utils.date_converter import DateConverter
from library.course_live_workshops import TrainerCentralLiveWorkshops

router = APIRouter(prefix="/course", tags=["course_live_workshops"])


class CreateCourseLiveRequest(BaseModel):
    """Request body for creating a live workshop session inside a course.
    
    Attributes:
        name (str): Title of the live workshop session.
        description_html (str): HTML description of the workshop content.
        start_time (str): Session start time in format DD-MM-YYYY HH:MMAM/PM (e.g., "05-12-2025 3:00PM").
        end_time (str): Session end time in format DD-MM-YYYY HH:MMAM/PM (e.g., "05-12-2025 5:00PM").
    """
    name: str
    description_html: str
    start_time: str  # DD-MM-YYYY HH:MMPM
    end_time: str


class InviteLearnerRequest(BaseModel):
    """Request body for inviting a learner to a course or course live session.
    
    Attributes:
        email (str): Email address of the learner to invite.
        first_name (str): First name of the learner.
        last_name (str): Last name of the learner.
        course_id (str, optional): Course ID to invite the learner to. Either course_id or session_id must be provided.
        session_id (str, optional): Course live session ID to invite the learner to. Either course_id or session_id must be provided.
        is_access_granted (bool, optional): Whether to grant access to the learner. Defaults to True.
        expiry_time (int, optional): Unix timestamp for when the access expires (in milliseconds).
        expiry_duration (str, optional): Duration for which the learner has access (e.g., "30d" for 30 days).
    """
    email: str
    first_name: str
    last_name: str
    course_id: Optional[str] = None
    session_id: Optional[str] = None
    is_access_granted: Optional[bool] = True
    expiry_time: Optional[int] = None
    expiry_duration: Optional[str] = None


@router.post("/{course_id}/live_sessions", summary="Create a live session inside a course")
async def create_course_live_session(course_id: str, body: CreateCourseLiveRequest, orgId: str, access_token: str):
    """Create a live workshop session inside a course.
    
    Creates a new live workshop (synchronous session) within a course. This endpoint
    allows trainers to schedule live training sessions with learners, including setting
    the session title, description, time, and capacity.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        course_id (str, path parameter): The unique identifier of the course.
        body (CreateCourseLiveRequest): Request body containing:
            - name: Title of the live session
            - description_html: HTML content describing the workshop
            - start_time: Session start time (format: DD-MM-YYYY HH:MMAM/PM, e.g., "05-12-2025 3:00PM")
            - end_time: Session end time (format: DD-MM-YYYY HH:MMAM/PM, e.g., "05-12-2025 5:00PM")
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
        
    
    Returns:
        dict: API response containing the newly created live session with details:
            - sessionId: Unique identifier for the session
            - name: Session title
            - startTime: Start time in Unix milliseconds
            - endTime: End time in Unix milliseconds
            - Other session metadata
    
    Raises:
        HTTPException 400: Invalid course_id, invalid date format, or missing required fields
        HTTPException 401: Unauthorized (invalid OAuth token)
        HTTPException 404: Course not found
        HTTPException 500: Server error from Trainer Central API
    
    Example:
        Request:
            POST /course/19208000000035003/live_sessions
            Content-Type: application/json
            
            {
              "name": "Advanced Web Development Workshop",
              "description_html": "<h2>Learn Advanced Web Dev</h2><p>Covering React, Node.js, and deployment strategies</p>",
              "start_time": "05-12-2025 3:00PM",
              "end_time": "05-12-2025 5:00PM",
            }
        
        Response (200 OK):
            {
              "sessionId": "19208000000067890",
              "name": "Advanced Web Development Workshop",
              "courseId": "19208000000035003",
              "startTime": 1733425800000,
              "endTime": 1733432900000,
              "status": "active"
            }
    """
    # library currently accepts date strings and converts internally,
    # but we accept the LLM-friendly format and pass it through.
    tc = TrainerCentralLiveWorkshops()
    print("IN ROUTER - CREATE WORKSHOP")
    print(course_id, body)
    return tc.create_course_live_workshop(
        orgId, 
        access_token,
        course_id=course_id,
        name=body.name,
        description_html=body.description_html,
        start_time_str=body.start_time,
        end_time_str=body.end_time
    )


@router.get("/{course_id}/live_sessions", summary="List live sessions in a course")
async def list_course_live_sessions(course_id: str, orgId: str, access_token: str, filter_type: int = 5, limit: int = 50, si: int = 0):
    """Retrieve a list of upcoming live sessions within a course.
    
    Fetches all upcoming live workshop sessions scheduled for a specific course.
    Returns sessions in chronological order with optional pagination and filtering.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        course_id (str, path parameter): The unique identifier of the course.
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
        filter_type (int, query parameter): Filter type for sessions (default: 5).
            - 5: Upcoming sessions
            - Other values may represent different session states
        limit (int, query parameter): Maximum number of sessions to return (default: 50, max: typically 200).
        si (int, query parameter): Start index for pagination (default: 0). Use with limit for page-based pagination.
    
    Returns:
        dict: API response containing list of live sessions with structure:
            {
              "sessions": [
                {
                  "sessionId": "...",
                  "name": "...",
                  "startTime": ...,
                  "endTime": ...,
                  "status": "..."
                },
                ...
              ],
              "totalCount": number,
              "count": number,
              "pageIndex": number
            }
    
    Raises:
        HTTPException 400: Invalid course_id or invalid query parameters
        HTTPException 401: Unauthorized (invalid OAuth token)
        HTTPException 404: Course not found
        HTTPException 500: Server error from Trainer Central API
    
    Example:
        Request:
            GET /course/19208000000035003/live_sessions?filter_type=5&limit=10&si=0
        
        Response (200 OK):
            {
              "sessions": [
                {
                  "sessionId": "19208000000067890",
                  "name": "Advanced Web Development Workshop",
                  "startTime": 1733425800000,
                  "endTime": 1733432900000,
                  "status": "active"
                },
                {
                  "sessionId": "19208000000067891",
                  "name": "JavaScript Fundamentals",
                  "startTime": 1733512200000,
                  "endTime": 1733519400000,
                  "status": "active"
                }
              ],
              "totalCount": 2,
              "count": 2,
              "pageIndex": 0
            }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.list_upcoming_live_sessions(course_id, orgId, access_token, filter_type, limit, si)


@router.delete("/live_sessions/{session_id}", summary="Delete a course live session")
async def delete_course_live_session(session_id: str, orgId: str, access_token: str):
    """Delete a live workshop session from a course.
    
    Permanently removes a scheduled live workshop session from a course. This action
    cannot be undone and will notify enrolled learners of the cancellation.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        session_id (str, path parameter): The unique identifier of the live session to delete.
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: API response confirming deletion with structure:
            {
              "success": true,
              "message": "Session deleted successfully",
              "sessionId": "..."
            }
    
    Raises:
        HTTPException 400: Invalid session_id format
        HTTPException 401: Unauthorized (invalid OAuth token)
        HTTPException 404: Session not found or already deleted
        HTTPException 409: Cannot delete session (e.g., session already started or completed)
        HTTPException 500: Server error from Trainer Central API
    
    Example:
        Request:
            DELETE /course/live_sessions/19208000000067890
        
        Response (200 OK):
            {
              "success": true,
              "message": "Session deleted successfully",
              "sessionId": "19208000000067890"
            }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.delete_live_session(session_id, orgId, access_token)


@router.post("/invite_learner", summary="Invite learner to course or course live session")
async def invite_learner(body: InviteLearnerRequest, orgId: str, access_token: str):
    """Send an invitation to a learner to enroll in a course or attend a live session.
    
    Creates a learner account or sends an invitation to an existing learner to join a course
    or attend a specific live workshop session. Supports optional access expiry configuration
    and grant/revoke control.

    Note: Provide orgId and access token of the user, after OAuth, as parameters.  
    
    Args:
        body (InviteLearnerRequest): Request body containing:
            - email: Learner's email address (required)
            - first_name: Learner's first name (required)
            - last_name: Learner's last name (required)
            - course_id: Course to invite learner to (optional, either course_id or session_id required)
            - session_id: Course live session to invite learner to (optional, either course_id or session_id required)
            - is_access_granted: Grant/revoke access (default: true)
            - expiry_time: Unix timestamp in milliseconds when access expires (optional)
            - expiry_duration: Duration string like "30d", "1m", "1y" (optional)
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: API response containing learner invitation status with structure:
            {
              "success": true,
              "message": "Invitation sent successfully",
              "learnerId": "...",
              "email": "...",
              "accessStatus": "granted" or "revoked",
              "expiryTime": ... (milliseconds)
            }
    
    Raises:
        HTTPException 400: Invalid email, missing required fields (both course_id and session_id missing), or invalid expiry format
        HTTPException 401: Unauthorized (invalid OAuth token)
        HTTPException 404: Course or session not found
        HTTPException 409: Learner already invited or access already granted
        HTTPException 500: Server error from Trainer Central API
    
    Example:
        Request (Invite to Course):
            POST /course/invite_learner
            Content-Type: application/json
            
            {
              "email": "john.doe@example.com",
              "first_name": "John",
              "last_name": "Doe",
              "course_id": "19208000000035003",
              "is_access_granted": true,
              "expiry_duration": "30d"
            }
        
        Response (200 OK):
            {
              "success": true,
              "message": "Invitation sent successfully",
              "learnerId": "19208000000089456",
              "email": "john.doe@example.com",
              "accessStatus": "granted",
              "expiryTime": 1736017800000
            }
        
        Request (Invite to Live Session):
            POST /course/invite_learner
            Content-Type: application/json
            
            {
              "email": "jane.smith@example.com",
              "first_name": "Jane",
              "last_name": "Smith",
              "session_id": "19208000000067890"
            }
        
        Response (200 OK):
            {
              "success": true,
              "message": "Invitation sent successfully",
              "learnerId": "19208000000089457",
              "email": "jane.smith@example.com",
              "accessStatus": "granted"
            }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.invite_learner_to_course_or_course_live_session(
        orgId, 
        access_token,
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        course_id=body.course_id,
        session_id=body.session_id,
        is_access_granted=body.is_access_granted,
        expiry_time=body.expiry_time,
        expiry_duration=body.expiry_duration,
    )

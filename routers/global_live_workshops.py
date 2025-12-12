from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from utils.date_converter import DateConverter
from library.live_workshops import TrainerCentralLiveWorkshops

router = APIRouter(prefix="/global_workshops", tags=["global_live_workshops"])


class CreateGlobalWorkshopRequest(BaseModel):
    name: str
    description_html: str
    start_time: str
    end_time: str


class CreateOccurrenceRequest(BaseModel):
    sessionId: str
    scheduledTime: str  # DD-MM-YYYY HH:MMPM
    scheduledEndTime: str
    durationTime: Optional[int] = None
    recurrence: Optional[Dict[str, Any]] = None


@router.post("/create", summary="Create a global live workshop")
async def create_global_workshop(body: CreateGlobalWorkshopRequest, orgId: str, access_token: str):
    """Create a global live workshop (not associated with a course).
    
    This endpoint creates a standalone live workshop that learners can register
    for directly without needing course enrollment. Workshop date/time are converted
    from human-readable format to Unix milliseconds.
    
    Args:
        body (CreateGlobalWorkshopRequest): Workshop creation payload
            - name (str): Workshop title
            - description_html (str): Workshop description in HTML format
            - start_time (str): Start time in ISO format (e.g., "2025-01-15T10:00:00") or "DD-MM-YYYY HH:MMAM/PM"
            - end_time (str): End time in same format as start_time
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Created workshop session with:
            - sessionId: Workshop ID for reference
            - name, description, schedule details
            - registration link and access info
    
    Raises:
        HTTPException: 400 if date format invalid or validation fails, 500 if creation fails
    
    Example:
        POST /global_workshops/create
        {
            "name": "Advanced Python Workshop",
            "description_html": "<p>Learn advanced Python patterns...</p>",
            "start_time": "2025-01-20T14:00:00",
            "end_time": "2025-01-20T16:00:00",
        }
    """
    dc = DateConverter()
    start_ms = int(dc.convert_date_to_time(body.start_time))
    end_ms = int(dc.convert_date_to_time(body.end_time))

    session_data = {
        "name": body.name,
        "description": body.description_html,
        "deliveryMode": 3,
        "scheduledTime": start_ms,
        "scheduledEndTime": end_ms
    }

    tc = TrainerCentralLiveWorkshops()
    return tc.create_global_workshop(session_data, orgId, access_token)


@router.put("/{session_id}", summary="Update a global workshop")
async def update_workshop(session_id: str, updates: Dict[str, Any], orgId: str, access_token: str):
    """Update a global workshop's metadata or schedule.
    
    Args:
        session_id (str): The ID of the workshop to update
        updates (dict): Fields to update, e.g.:
            {
                "name": "Updated Workshop Title",
                "description": "New description",
                "schedule": {"startTime": ..., "endTime": ...}
            }
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Updated workshop object
    
    Raises:
        HTTPException: 404 if workshop not found, 500 if update fails
    
    Example:
        PUT /global_workshops/19208000000050001
        {
            "name": "Advanced Python - Rescheduled"
        }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.update_workshop(session_id, updates, orgId, access_token)


@router.post("/occurrence", summary="Create a workshop occurrence")
async def create_occurrence(body: CreateOccurrenceRequest, orgId: str, access_token: str):
    """Create an occurrence (session instance) for a global workshop.
    
    Workshops can have multiple occurrences (repeating sessions or alternative dates).
    This endpoint creates a new scheduled occurrence tied to an existing workshop.
    
    Args:
        body (CreateOccurrenceRequest): Occurrence creation payload
            - sessionId (str): Parent workshop/session ID
            - scheduledTime (str): Occurrence start time in ISO format or "DD-MM-YYYY HH:MMAM/PM"
            - scheduledEndTime (str): Occurrence end time in same format
            - durationTime (int, optional): Duration in minutes (if different from workshop)
            - recurrence (dict, optional): Recurrence rules for repeating occurrences
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Created occurrence (talk) with:
            - talkId: Occurrence ID
            - sessionId, scheduledTime, scheduledEndTime
            - registration info and join link
    
    Raises:
        HTTPException: 400 if format invalid or validation fails, 500 if creation fails
    
    Example:
        POST /global_workshops/occurrence
        {
            "sessionId": "19208000000050001",
            "scheduledTime": "2025-01-20T14:00:00",
            "scheduledEndTime": "2025-01-20T16:00:00"
        }
    """
    dc = DateConverter()
    scheduled_ms = int(dc.convert_date_to_time(body.scheduledTime))
    scheduled_end_ms = int(dc.convert_date_to_time(body.scheduledEndTime))

    talk_data = {
        "sessionId": body.sessionId,
        "scheduledTime": scheduled_ms,
        "scheduledEndTime": scheduled_end_ms,
    }
    if body.durationTime is not None:
        talk_data["durationTime"] = body.durationTime
    if body.recurrence is not None:
        talk_data["recurrence"] = body.recurrence

    tc = TrainerCentralLiveWorkshops()
    return tc.create_occurrence(talk_data, orgId, access_token)


@router.put("/occurrence/{talk_id}", summary="Update a workshop occurrence")
async def update_occurrence(talk_id: str, updates: Dict[str, Any], orgId: str, access_token: str):
    """Update a workshop occurrence (session instance).
    
    Args:
        talk_id (str): The ID of the occurrence to update
        updates (dict): Fields to update (e.g., time, duration, cancellation status)
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user

    Returns:
        dict: Updated occurrence object
    
    Raises:
        HTTPException: 404 if occurrence not found, 500 if update fails
    
    Example:
        PUT /global_workshops/occurrence/19208000000051001
        {
            "scheduledTime": 1705766400000
        }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.update_occurrence(talk_id, updates, orgId, access_token)


@router.get("/", summary="List global workshops")
async def list_global_workshops(orgId: str, access_token: str, filter_type: int = 5, limit: int = 50, si: int = 0):
    """List all upcoming global live workshops in the organization.
    
    Args:
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
        filter_type (int): Filter by workshop status (default: 5 = upcoming)
        limit (int): Max number of workshops to return (default: 50)
        si (int): Start index for pagination (default: 0)
    
    Returns:
        dict: Array of workshop objects with:
            - sessionId, name, description
            - schedule (start time, end time, timezone)
            - registration count, status
            - occurrence details
    
    Raises:
        HTTPException: 500 if list request fails
    
    Example:
        GET /global_workshops/?filter_type=5&limit=25
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.list_all_upcoming_workshops(orgId, access_token, filter_type, limit, si)


@router.post("/{session_id}/invite", summary="Invite a user to a global workshop session")
async def invite_user(session_id: str, email: str, orgId: str, access_token: str, role: int = 3, source: int = 1):
    """Invite an existing user to register for a global workshop.
    
    Args:
        session_id (str): The ID of the workshop to invite the user to
        email (str): Email address of the user to invite
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
        role (int): User role in workshop (3 = learner, higher = instructor; default: 3)
        source (int): Invitation source (1 = internal; default: 1)
    
    Returns:
        dict: Invitation confirmation with:
            - invitationId
            - userEmail, workshop details
            - registration link
    
    Raises:
        HTTPException: 404 if workshop/user not found, 500 if invitation fails
    
    Example:
        POST /global_workshops/19208000000050001/invite
        {
            "email": "user@example.com",
            "role": 3
        }
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.invite_user_to_workshop(session_id, email, orgId, access_token, role, source)

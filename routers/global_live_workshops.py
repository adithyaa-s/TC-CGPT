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
    timezone: str
    max_attendees: Optional[int] = 0


class CreateOccurrenceRequest(BaseModel):
    sessionId: str
    scheduledTime: str  # DD-MM-YYYY HH:MMPM
    scheduledEndTime: str
    durationTime: Optional[int] = None
    recurrence: Optional[Dict[str, Any]] = None


@router.post("/create", summary="Create a global live workshop")
async def create_global_workshop(body: CreateGlobalWorkshopRequest):
    """Create a global live workshop (not tied to a course).

    POST /global_workshops/create
    """
    # convert dates to ms and pass into library method that expects ms
    dc = DateConverter()
    start_ms = int(dc.convert_date_to_time(body.start_time))
    end_ms = int(dc.convert_date_to_time(body.end_time))

    # Build a session payload similar to library expectations
    session_data = {
        "name": body.name,
        "description": body.description_html,
        "deliveryMode": 6,
        "maxParticipants": body.max_attendees,
        "schedule": {
            "startTime": start_ms,
            "endTime": end_ms,
            "timeZone": body.timezone,
        },
    }

    tc = TrainerCentralLiveWorkshops()
    return tc.create_global_workshop(
        name=body.name,
        description_html=body.description_html,
        start_time_str=body.start_time,
        end_time_str=body.end_time,
        timezone=body.timezone,
        max_attendees=body.max_attendees,
    )


@router.put("/{session_id}", summary="Update a global workshop")
async def update_workshop(session_id: str, updates: Dict[str, Any]):
    """Update a global live workshop by session ID.

    PUT /global_workshops/{session_id}
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.update_workshop(session_id, updates)


@router.post("/occurrence", summary="Create a workshop occurrence")
async def create_occurrence(body: CreateOccurrenceRequest):
    """Create an occurrence (talk) for a global workshop.

    POST /global_workshops/occurrence
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
    return tc.create_occurrence(talk_data)


@router.put("/occurrence/{talk_id}", summary="Update an occurrence")
async def update_occurrence(talk_id: str, updates: Dict[str, Any]):
    """Update a workshop occurrence by talk ID.

    PUT /global_workshops/occurrence/{talk_id}
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.update_occurrence(talk_id, updates)


@router.get("/", summary="List global workshops")
async def list_global_workshops(filter_type: int = 5, limit: int = 50, si: int = 0):
    """List upcoming global live workshops.

    GET /global_workshops?filter_type=&limit=&si=
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.list_all_upcoming_workshops(filter_type, limit, si)


@router.post("/{session_id}/invite", summary="Invite a user to a global workshop session")
async def invite_user(session_id: str, email: str, role: int = 3, source: int = 1):
    """Invite an existing user (by email) to a global workshop session.

    POST /global_workshops/{session_id}/invite
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.invite_user_to_workshop(session_id, email, role, source)

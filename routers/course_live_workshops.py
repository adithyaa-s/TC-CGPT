from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from utils.date_converter import DateConverter
from library.course_live_workshops import TrainerCentralLiveWorkshops

router = APIRouter(prefix="/course", tags=["course_live_workshops"])


class CreateCourseLiveRequest(BaseModel):
    name: str
    description_html: str
    start_time: str  # DD-MM-YYYY HH:MMPM
    end_time: str
    timezone: str
    max_attendees: Optional[int] = 0


class InviteLearnerRequest(BaseModel):
    email: str
    first_name: str
    last_name: str
    course_id: Optional[str] = None
    session_id: Optional[str] = None
    is_access_granted: Optional[bool] = True
    expiry_time: Optional[int] = None
    expiry_duration: Optional[str] = None


@router.post("/{course_id}/live_sessions", summary="Create a live session inside a course")
async def create_course_live_session(course_id: str, body: CreateCourseLiveRequest):
    """Create a live workshop session inside a course.

    POST /course/{course_id}/live_sessions
    Body: { name, description_html, start_time, end_time, timezone, max_attendees }
    """
    # library currently accepts date strings and converts internally,
    # but we accept the LLM-friendly format and pass it through.
    tc = TrainerCentralLiveWorkshops()
    return tc.create_course_live_workshop(
        course_id=course_id,
        name=body.name,
        description_html=body.description_html,
        start_time_str=body.start_time,
        end_time_str=body.end_time,
        timezone=body.timezone,
        max_attendees=body.max_attendees,
    )


@router.get("/{course_id}/live_sessions", summary="List live sessions in a course")
async def list_course_live_sessions(course_id: str, filter_type: int = 5, limit: int = 50, si: int = 0):
    """List upcoming live sessions inside a course.

    GET /course/{course_id}/live_sessions
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.list_upcoming_live_sessions(filter_type, limit, si)


@router.delete("/live_sessions/{session_id}", summary="Delete a course live session")
async def delete_course_live_session(session_id: str):
    """Delete a live session by session_id.

    DELETE /course/live_sessions/{session_id}
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.delete_live_session(session_id)


@router.post("/invite_learner", summary="Invite learner to course or course live session")
async def invite_learner(body: InviteLearnerRequest):
    """Invite a learner to a course or a course live session.

    POST /course/invite_learner
    """
    tc = TrainerCentralLiveWorkshops()
    return tc.invite_learner_to_course_or_course_live_session(
        email=body.email,
        first_name=body.first_name,
        last_name=body.last_name,
        course_id=body.course_id,
        session_id=body.session_id,
        is_access_granted=body.is_access_granted,
        expiry_time=body.expiry_time,
        expiry_duration=body.expiry_duration,
    )

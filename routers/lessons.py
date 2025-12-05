from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Optional

from library.lessons import TrainerCentralLessons

router = APIRouter(prefix="/lessons", tags=["lessons"])


class LessonCreateRequest(BaseModel):
    session_data: dict
    content_html: str
    content_filename: Optional[str] = "Content"


class LessonUpdateRequest(BaseModel):
    updates: dict


@router.post("/create", summary="Create a lesson under a course")
async def create_lesson(body: LessonCreateRequest):
    """Create a lesson under a course.

    POST /lessons/create
    Body: { session_data, content_html, content_filename }
    Returns: { "lesson": {...}, "content": {...} }
    """
    tc = TrainerCentralLessons()
    return tc.create_lesson_with_content(body.session_data, body.content_html, body.content_filename)


@router.put("/{session_id}", summary="Update a lesson/session")
async def update_lesson(session_id: str, body: LessonUpdateRequest):
    """Update an existing lesson/session.

    PUT /lessons/{session_id}
    Body: { updates }
    """
    tc = TrainerCentralLessons()
    return tc.update_lesson(session_id, body.updates)


@router.delete("/{session_id}", summary="Delete a lesson/session")
async def delete_lesson(session_id: str):
    """Delete a lesson/session by session ID.

    DELETE /lessons/{session_id}
    """
    tc = TrainerCentralLessons()
    return tc.delete_lesson(session_id)

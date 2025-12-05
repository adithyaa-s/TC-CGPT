from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from library.assignments import TrainerCentralAssignments

router = APIRouter(prefix="/assignments", tags=["assignments"])


class AssignmentCreateRequest(BaseModel):
    assignment_data: dict
    instruction_html: str
    instruction_filename: Optional[str] = "Instructions"
    view_type: Optional[int] = 4


@router.post("/create", summary="Create an assignment with instructions")
async def create_assignment(body: AssignmentCreateRequest):
    """Create an assignment under a course/chapter and attach instructions.

    POST /assignments/create
    Body: { assignment_data, instruction_html, instruction_filename, view_type }
    Returns: { assignment, instructions }
    """
    tc = TrainerCentralAssignments()
    return tc.create_assignment_with_instructions(
        body.assignment_data,
        body.instruction_html,
        body.instruction_filename,
        body.view_type,
    )


@router.delete("/{session_id}", summary="Delete an assignment/session")
async def delete_assignment(session_id: str):
    """Delete an assignment (session) by session ID.

    DELETE /assignments/{session_id}
    """
    tc = TrainerCentralAssignments()
    return tc.delete_assignment(session_id)

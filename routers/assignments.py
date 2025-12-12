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
    """Create an assignment under a course/chapter with instruction content.
    
    This endpoint creates a new assignment (deliveryMode=7) with attached instruction
    materials. The instructions are uploaded as a separate text file after the session
    is created.
    
    Args:
        body (AssignmentCreateRequest): Assignment creation payload
            - assignment_data (dict): Assignment metadata, e.g.:
                {
                    "name": "Assignment Title",
                    "courseId": "...",
                    "sectionId": "...",
                    "deliveryMode": 7,
                    "description": "..."
                }
            - instruction_html (str): Instruction content in HTML format
            - instruction_filename (str): Display name for instruction file (default: "Instructions")
            - view_type (int): Content viewer type (default: 4)
    
    Returns:
        dict: Response containing:
            - assignment: Session creation response with assignmentId
            - instructions: Instruction upload response
    
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    
    Example:
        POST /assignments/create
        {
            "assignment_data": {
                "name": "Database Design Project",
                "courseId": "19208000000035003",
                "sectionId": "19208000000042002",
                "deliveryMode": 7
            },
            "instruction_html": "<h3>Task</h3><p>Design a relational database...</p>",
            "instruction_filename": "Project Instructions"
        }
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
    """Permanently delete an assignment (session) from the course.
    
    WARNING: This action cannot be undone. All instruction materials, learner
    submissions, and grading records will be deleted.
    
    Args:
        session_id (str): The ID of the assignment/session to delete
    
    Returns:
        dict: Confirmation response with deletion status
    
    Raises:
        HTTPException: 404 if session not found, 500 if deletion fails
    
    Example:
        DELETE /assignments/19208000000050002
    """
    tc = TrainerCentralAssignments()
    return tc.delete_assignment(session_id)

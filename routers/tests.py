from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

from library.tests import TrainerCentralTests

router = APIRouter(prefix="/tests", tags=["tests"])


class FullTestCreateRequest(BaseModel):
    session_id: str
    name: str
    description_html: str
    questions: Dict[str, Any]


class TestFormCreateRequest(BaseModel):
    session_id: str
    name: str
    description_html: str


class AddQuestionsRequest(BaseModel):
    session_id: str
    form_id_value: str
    questions: Dict[str, Any]


@router.post("/create_full", summary="Create a complete test under a lesson")
async def create_full_test(body: FullTestCreateRequest):
    """Create a complete test with form and questions in one request.
    
    This endpoint creates a test form under a lesson (session) and immediately
    adds all questions. It's a convenience method that combines two API calls.
    
    Args:
        body (FullTestCreateRequest): Test creation payload
            - session_id (str): Parent lesson/session ID
            - name (str): Test title
            - description_html (str): Test description in HTML format
            - questions (dict): Question definitions keyed by question ID, e.g.:
                {
                    "q1": {"type": "mcq", "text": "What is...", "options": [...], "correctOption": 0},
                    "q2": {"type": "essay", "text": "Explain..."}
                }
    
    Returns:
        dict: Response containing form and questions creation results
    
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    
    Example:
        POST /tests/create_full
        {
            "session_id": "19208000000050001",
            "name": "Chapter 1 Quiz",
            "description_html": "<p>Test your knowledge of Chapter 1</p>",
            "questions": {
                "q1": {"type": "mcq", "text": "Which is correct?", "options": ["A", "B", "C"], "correctOption": 1}
            }
        }
    """
    tc = TrainerCentralTests()
    return tc.create_full_test(body.session_id, body.name, body.description_html, body.questions)


@router.post("/create_form", summary="Create a test form")
async def create_test_form(body: TestFormCreateRequest):
    """Create a test form under a lesson without questions.
    
    This endpoint creates an empty test form that can be populated with questions
    separately using /tests/add_questions. Returns the formIdValue needed for
    subsequent question additions.
    
    Args:
        body (TestFormCreateRequest): Form creation payload
            - session_id (str): Parent lesson/session ID
            - name (str): Test/form title
            - description_html (str): Form description in HTML format
    
    Returns:
        dict: API response containing:
            - formIdValue: ID needed to add questions to this form
            - form metadata (name, description, etc.)
    
    Raises:
        HTTPException: 400 if validation fails, 500 if creation fails
    
    Example:
        POST /tests/create_form
        {
            "session_id": "19208000000050001",
            "name": "Mid-Term Exam",
            "description_html": "<p>Mid-term assessment for the course</p>"
        }
    """
    tc = TrainerCentralTests()
    return tc.create_test_form(body.session_id, body.name, body.description_html)


@router.post("/add_questions", summary="Add questions to an existing form")
async def add_test_questions(body: AddQuestionsRequest):
    """Add questions to an existing test form.
    
    This endpoint populates a previously created form with one or more questions
    (MCQ, essay, true/false, fill-in-the-blanks, etc.).
    
    Args:
        body (AddQuestionsRequest): Question addition payload
            - session_id (str): Parent lesson/session ID
            - form_id_value (str): Form ID returned from /tests/create_form
            - questions (dict): Question definitions keyed by question ID, e.g.:
                {
                    "q1": {"type": "mcq", "text": "...", "options": [...], "correctOption": 0},
                    "q2": {"type": "essay", "text": "..."}
                }
    
    Returns:
        dict: Response confirming all questions were added
    
    Raises:
        HTTPException: 400 if validation fails, 404 if form not found, 500 if addition fails
    
    Example:
        POST /tests/add_questions
        {
            "session_id": "19208000000050001",
            "form_id_value": "19208000000060001",
            "questions": {
                "q1": {"type": "mcq", "text": "Select the correct answer", "options": ["A", "B"], "correctOption": 0}
            }
        }
    """
    tc = TrainerCentralTests()
    return tc.add_questions(body.session_id, body.form_id_value, body.questions)


@router.get("/course/{course_id}/sessions", summary="Get course sessions")
async def get_course_sessions(course_id: str):
    """Fetch all lessons/sessions (including tests) under a course.
    
    This endpoint retrieves all session types (lessons, tests, assignments) that
    belong to a specified course.
    
    Args:
        course_id (str): The ID of the course
    
    Returns:
        dict: Array of session objects with metadata:
            - sessionId, name, description
            - deliveryMode, createdTime, updatedTime
            - enrollment counts, completion status
    
    Raises:
        HTTPException: 404 if course not found, 500 if retrieval fails
    
    Example:
        GET /tests/course/19208000000035003/sessions
    """
    tc = TrainerCentralTests()
    return tc.get_course_sessions(course_id)

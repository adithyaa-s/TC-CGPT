from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

from library.tests import TrainerCentralTests

router = APIRouter(prefix="/tests", tags=["tests"])
tc = TrainerCentralTests()


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
    """Create a complete test: create form and upload questions.

    POST /tests/create_full
    """
    return tc.create_full_test(body.session_id, body.name, body.description_html, body.questions)


@router.post("/create_form", summary="Create a test form")
async def create_test_form(body: TestFormCreateRequest):
    """Create only the test form (returns form.formIdValue).

    POST /tests/create_form
    """
    return tc.create_test_form(body.session_id, body.name, body.description_html)


@router.post("/add_questions", summary="Add questions to an existing form")
async def add_test_questions(body: AddQuestionsRequest):
    """Add questions to an existing test form.

    POST /tests/add_questions
    Body: { session_id, form_id_value, questions }
    """
    return tc.add_questions(body.session_id, body.form_id_value, body.questions)


@router.get("/course/{course_id}/sessions", summary="Get course sessions")
async def get_course_sessions(course_id: str):
    """Fetch all sessions (lessons) under a course.

    GET /tests/course/{course_id}/sessions
    """
    return tc.get_course_sessions(course_id)

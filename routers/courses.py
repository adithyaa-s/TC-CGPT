from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Any

from library.courses import TrainerCentralCourses

router = APIRouter(prefix="/courses", tags=["courses"])


class CourseCreateRequest(BaseModel):
    courseName: str
    subTitle: Optional[str] = None
    description: Optional[str] = None
    courseCategories: Optional[list[Any]] = None


class CourseUpdateRequest(BaseModel):
    courseName: Optional[str] = None
    subTitle: Optional[str] = None
    description: Optional[str] = None
    courseCategories: Optional[list[Any]] = None


@router.post("/", summary="Create a new course")
async def create_course(body: CourseCreateRequest):
    """Create a new course.

    POST /courses/

    Body: CourseCreateRequest

    Returns the TrainerCentral create course response.
    """
    tc = TrainerCentralCourses()
    return tc.post_course(body.dict())


@router.get("/{course_id}", summary="Get course by ID")
async def get_course(course_id: str):
    """Retrieve a course by its ID.

    GET /courses/{course_id}
    """
    tc = TrainerCentralCourses()
    return tc.get_course(course_id)


@router.get("/", summary="List courses")
async def list_courses():
    """List courses (no pagination currently).

    GET /courses/
    """
    tc = TrainerCentralCourses()
    return tc.list_courses()


@router.put("/{course_id}", summary="Update a course")
async def update_course(course_id: str, body: CourseUpdateRequest):
    """Update an existing course.

    PUT /courses/{course_id}
    """
    tc = TrainerCentralCourses()
    return tc.update_course(course_id, body.dict(exclude_unset=True))


@router.delete("/{course_id}", summary="Delete a course")
async def delete_course(course_id: str):
    """Delete a course by ID.

    DELETE /courses/{course_id}
    """
    tc = TrainerCentralCourses()
    return tc.delete_course(course_id)

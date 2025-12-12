from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from library.chapters import TrainerCentralChapters

router = APIRouter(prefix="/chapters", tags=["chapters"])


class ChapterCreateRequest(BaseModel):
    """Request body for creating a chapter/section under a course.
    
    Attributes:
        courseId (str): ID of the parent course (required)
        name (str): Name/title of the chapter (required)
    """
    courseId: str
    name: str


class ChapterUpdateRequest(BaseModel):
    """Request body for updating a chapter/section.
    
    Attributes:
        name (str, optional): New chapter name
        sectionIndex (int, optional): New position (0-based) of the chapter in the course
    """
    name: Optional[str] = None
    sectionIndex: Optional[int] = None


@router.post("/", summary="Create a new chapter")
async def create_chapter(body: ChapterCreateRequest, orgId: str, access_token: str):
    """Create a new chapter (section) under a course in TrainerCentral.
    
    Chapters are organizational units within a course that group related lessons/sessions.
    They help structure course content into logical modules or units.
    
    Args:
        body (ChapterCreateRequest): Chapter metadata
            - courseId (str, required): ID of the course under which to create the chapter
            - name (str, required): Name/title of the chapter

        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: API response containing created chapter details, including:
            - id / sectionId
            - name / sectionName
            - courseId
            - sectionIndex (position in course)
            - createdTime
            - lastUpdatedTime
            - status
    
    Raises:
        HTTPException: 400 if validation fails, 404 if course not found, 500 if creation fails
    
    Example:
        POST /chapters/
        {
            "courseId": "19208000000035003",
            "name": "Introduction to Python"
        }
    """
    tc = TrainerCentralChapters()
    return tc.create_chapter(body.dict(), orgId, access_token)


@router.put("/{course_id}/sections/{section_id}", summary="Update a chapter")
async def update_chapter(course_id: str, section_id: str, body: ChapterUpdateRequest, orgId: str, access_token: str):
    """Update an existing chapter's name and/or position in a course.
    
    Allows modification of chapter metadata such as name and ordering within the course.
    Only provided fields are updated; omitted fields remain unchanged.
    
    Args:
        course_id (str): The ID of the course that owns the chapter
        section_id (str): The ID of the chapter (section) to update
        body (ChapterUpdateRequest): Fields to update (all optional)
            - name (str): New chapter name
            - sectionIndex (int): New 0-based position of the chapter in the course

        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Updated chapter object with all metadata
    
    Raises:
        HTTPException: 404 if course or chapter not found, 500 if update fails
    
    Note:
        Use sectionIndex to reorder chapters within a course. Index is 0-based,
        so the first chapter has sectionIndex = 0.
    
    Example:
        PUT /chapters/19208000000035003/sections/19208000000042002
        {
            "name": "Advanced Python Concepts",
            "sectionIndex": 2
        }
    """
    tc = TrainerCentralChapters()
    return tc.update_chapter(course_id, section_id, body.dict(exclude_unset=True), orgId, access_token)


@router.delete("/{course_id}/sections/{section_id}", summary="Delete a chapter")
async def delete_chapter(course_id: str, section_id: str, orgId: str, access_token: str):
    """Permanently delete a chapter from a course in TrainerCentral.
    
    WARNING: This action cannot be undone. All lessons/sessions within this chapter
    may be affected (depending on TrainerCentral's cascading delete behavior).
    
    Args:
        course_id (str): The ID of the course that owns the chapter
        section_id (str): The ID of the chapter (section) to delete
        orgId (str): Organization ID of the user
        access_token (str): Access Token of the user
    
    Returns:
        dict: Confirmation response with deletion status
    
    Raises:
        HTTPException: 404 if course or chapter not found, 500 if deletion fails
    
    Example:
        DELETE /chapters/19208000000035003/sections/19208000000042002
    """
    tc = TrainerCentralChapters()
    return tc.delete_chapter(course_id, section_id, orgId, access_token)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import courses, lessons, tests, assignments, course_live_workshops, global_live_workshops, oauth

app = FastAPI(title="TrainerCentral API Wrapper")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(courses.router)
app.include_router(lessons.router)
app.include_router(tests.router)
app.include_router(assignments.router)
app.include_router(course_live_workshops.router)
app.include_router(global_live_workshops.router)
app.include_router(oauth.router)

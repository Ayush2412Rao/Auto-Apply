import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.config import settings
from backend.app.api.routes import health, profile, preferences, jobs, resumes, applications, agent
from backend.app.scheduler.runner import start_scheduler, stop_scheduler
from backend.app.db.init_db import initialize_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB is ready & start scheduler
    print("Application starting up...")
    try:
        initialize_database()
    except Exception as e:
        print(f"Startup DB init notice: {e}")
    start_scheduler()
    yield
    # Shutdown
    print("Application shutting down...")
    stop_scheduler()

app = FastAPI(
    title=settings.APP_NAME,
    description="Production-Ready Agentic AI Auto-Apply Platform powered by LangGraph, ChromaDB, Gemini, Scrapy, and FastAPI.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware (Enable seamless access from Next.js dashboard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for direct document viewing
app.mount("/static/resumes", StaticFiles(directory=settings.TAILORED_RESUME_DIR), name="tailored_resumes")

# Include Routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(profile.router, prefix=settings.API_V1_STR)
app.include_router(preferences.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(resumes.router, prefix=settings.API_V1_STR)
app.include_router(applications.router, prefix=settings.API_V1_STR)
app.include_router(agent.router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

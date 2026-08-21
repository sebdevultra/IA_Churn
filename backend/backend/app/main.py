import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, logger
from backend.app.core.errors import AppBaseException, app_exception_handler, generic_exception_handler
from backend.app.db.init_db import init_db
from backend.app.workers.scheduler import start_scheduler, shutdown_scheduler
from backend.app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Initializing {settings.PROJECT_NAME} ({settings.ENVIRONMENT})...")
    init_db()
    start_scheduler()
    yield
    # Shutdown
    logger.info("Application shutting down...")
    shutdown_scheduler()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Academic and Production-grade Customer Sentiment & Churn Risk Monitoring API with AI and Deterministic Risk Engine.",
    version="1.0.0",
    lifespan=lifespan
)

# Exception Handlers
app.add_exception_handler(AppBaseException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Router (mounted at /api/v1 and /api for seamless frontend integration)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/api")

# Frontend Static Assets Serving
candidate_front_dirs = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend")),
    os.path.abspath(os.path.join(os.getcwd(), "frontend")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "frontend")),
]

front_dir = None
for cand in candidate_front_dirs:
    if os.path.exists(cand) and os.path.isdir(cand):
        front_dir = cand
        break

if front_dir:
    css_dir = os.path.join(front_dir, "css")
    js_dir = os.path.join(front_dir, "js")
    assets_dir = os.path.join(front_dir, "assets")

    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")

    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    app.mount("/static", StaticFiles(directory=front_dir), name="static")

# Mount /data directory for CSV datasets
project_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
if not os.path.exists(project_data_dir):
    project_data_dir = os.path.abspath(os.path.join(os.getcwd(), "data"))

if os.path.exists(project_data_dir):
    app.mount("/data", StaticFiles(directory=project_data_dir), name="data")

    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        index_file = os.path.join(front_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": f"{settings.PROJECT_NAME} API running. Access /docs for Swagger UI."}
else:
    @app.get("/", include_in_schema=False)
    async def serve_dashboard():
        return {"message": f"{settings.PROJECT_NAME} API running. Access /docs for Swagger UI."}

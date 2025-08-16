import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.auth.routes.auth_local import router as auth_local
from src.auth.routes.auth_oauth import router as auth_oauth
from src.auth.routes.auth_recovery import router as auth_recovery
from src.auth.routes.auth_tokens import router as auth_tokens
from src.care.router import router as care_router
from src.chat.routes import chat_router  # New LangGraph-powered chat
from src.core.config import settings
from src.core.logging import get_logger, setup_logging
from src.core.routes.health import router as health_router
from src.core.startup import run_startup_checks
from src.diagnosis.router import router as diagnosis_router
from src.identification.router import router as identification_router
from src.plants.router import router as plants_router
from src.podcast.router import router as podcast_router
from src.reminders.router import router as reminders_router
from src.shared.utils import simple_generate_unique_route_id
from src.tracking.router import router as tracking_router

# Configure logging
setup_logging(level="INFO", log_file="logs/app.log")
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    generate_unique_id_function=simple_generate_unique_route_id,
    openapi_url=settings.OPENAPI_URL,
)

# Run startup checks and log application status
run_startup_checks()


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

    return response


# Add Session Middleware (required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.ACCESS_SECRET_KEY,
    max_age=3600,  # 1 hour session
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health
app.include_router(health_router)

app.include_router(podcast_router, prefix="/podcast", tags=["podcast"])

# Auth
app.include_router(auth_local)
app.include_router(auth_oauth)
app.include_router(auth_tokens)
app.include_router(auth_recovery)

# Plants - Include all sub-routers directly
app.include_router(plants_router, prefix="/api")  # /api/plants/*
app.include_router(identification_router, prefix="/api")  # /api/plants/identify/*
app.include_router(reminders_router, prefix="/api")  # /api/plants/reminders/*
app.include_router(care_router, prefix="/api")  # /api/plants/care/*
app.include_router(diagnosis_router, prefix="/api")  # /api/plants/diagnose/*
app.include_router(tracking_router, prefix="/api")  # /api/plants/track/*
app.include_router(chat_router, prefix="/api")  # /api/plants/chat/*

# Plant Diagnosis
app.include_router(diagnosis_router)

# Others


# OK baby
logger.info(f"{settings.APP_NAME} ready to rock!")

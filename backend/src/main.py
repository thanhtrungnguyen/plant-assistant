import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.auth.routes.auth_local import router as auth_local
from src.auth.routes.auth_oauth import router as auth_oauth
from src.auth.routes.auth_recovery import router as auth_recovery
from src.auth.routes.auth_tokens import router as auth_tokens
from src.core.config import settings
from src.core.routes.health import router as health_router
from src.core.logging import setup_logging, get_logger
from src.shared.utils import simple_generate_unique_route_id

# Configure logging
setup_logging(level="INFO", log_file="logs/app.log")
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    generate_unique_id_function=simple_generate_unique_route_id,
    openapi_url=settings.OPENAPI_URL,
)

logger.info(f"Starting {settings.APP_NAME} application")
logger.info(f"CORS origins: {settings.CORS_ORIGINS}")


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s")

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Health
app.include_router(health_router)
logger.info("Health router included")

# Auth
app.include_router(auth_local)
logger.info("Auth local router included")
app.include_router(auth_oauth)
logger.info("Auth OAuth router included")
app.include_router(auth_tokens)
logger.info("Auth tokens router included")
app.include_router(auth_recovery)
logger.info("Auth recovery router included")

# Others

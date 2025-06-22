from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.src.texts.routes import router as texts_router

# Set up logging configuration
setup_logging()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include routers with API prefix
app.include_router(texts_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Ballad AI Backend is running"}

@app.get("/")
async def root():
    return {"message": "Welcome to Ballad AI Backend", "docs": "/docs"}

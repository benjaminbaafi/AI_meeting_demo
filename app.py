"""
Main FastAPI application.
Handles routing, middleware, and application lifecycle.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys

from config import settings


# Configure standard logging
LOG_LEVEL = getattr(logging, settings.log_level.upper(), logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_file),
    ],
)

logger = logging.getLogger(settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AI Meeting Participant application...")
    
    # Initialize Redis connection
    try:
        from utils.redis_service import get_redis_service
        redis_service = await get_redis_service()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Failed to connect to Redis: %s", str(e))
        logger.warning("Application will continue but job persistence may not work")
    
    yield
    
    # Close Redis connection
    try:
        from utils.redis_service import close_redis_service
        await close_redis_service()
        logger.info("Redis connection closed")
    except Exception as e:
        logger.error("Error closing Redis connection: %s", str(e))
    
    logger.info("Shutting down AI Meeting Participant application...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered meeting transcription, summarization, and action item extraction",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.debug else "Please contact support",
        },
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Meeting Participant API",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }


# Import and include routers
from api.v1 import upload, transcription, summary, admin

app.include_router(upload.router, prefix="/api/v1", tags=["Upload"])
app.include_router(transcription.router, prefix="/api/v1", tags=["Transcription"])
app.include_router(summary.router, prefix="/api/v1", tags=["Summary"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

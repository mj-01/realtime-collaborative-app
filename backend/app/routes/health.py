"""
Health check and system status routes.
"""
from fastapi import APIRouter
from app.utils.logging import get_logger

logger = get_logger("health_routes")
router = APIRouter(tags=["health"])

@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Welcome to the Backend API"}

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    logger.debug("Health check requested")
    return {"status": "healthy"}

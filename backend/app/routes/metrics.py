"""
Metrics and health monitoring routes.
"""

import time
from fastapi import APIRouter, Depends
from app.middleware.metrics import MetricsMiddleware
from app.utils.logging import get_logger

logger = get_logger("metrics_routes")
router = APIRouter(prefix="/metrics", tags=["metrics"])

# Global metrics instance (will be set by main.py)
metrics_middleware: MetricsMiddleware = None

def get_metrics_middleware() -> MetricsMiddleware:
    """Get metrics middleware instance."""
    return metrics_middleware

@router.get("/")
async def get_metrics(metrics: MetricsMiddleware = Depends(get_metrics_middleware)):
    """Get application metrics."""
    if not metrics:
        return {"error": "Metrics not available"}
    
    metrics_data = metrics.get_metrics()
    logger.info(f"Metrics requested: {metrics_data}")
    
    return {
        "status": "healthy",
        "metrics": metrics_data,
        "timestamp": time.time()
    }

@router.get("/health")
async def detailed_health_check():
    """Detailed health check with system information."""
    import psutil
    import time
    
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                }
            }
        }
        
        logger.info(f"Health check: CPU {cpu_percent}%, Memory {memory.percent}%")
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }

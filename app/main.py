"""
FastAPI Application - BISINDO CSLR Demo
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
from pathlib import Path

from app.config import settings
from app.api.routes import router as api_router
from app.utils import setup_logger

# Setup logging
logger = setup_logger(
    __name__,
    log_file=settings.log_file,
    log_level=settings.log_level
)

# Create FastAPI app
app = FastAPI(
    title="BISINDO CSLR Demo",
    description="Continuous Sign Language Recognition for BISINDO",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Middleware
# ==========

# CORS - Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)


# Include API routes
# ==================
app.include_router(api_router)


# Event handlers
# ==============

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    import torch
    
    # Get device info
    device = settings.get_device()
    device_info = settings.get_device_info()
    
    logger.info("=" * 60)
    logger.info("🤟 BISINDO CSLR Demo - Starting")
    logger.info("=" * 60)
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Device: {device.upper()}")
    logger.info(f"CUDA Available: {torch.cuda.is_available()}")
    
    if device == "cuda":
        logger.info(f"GPU: {device_info.get('gpu_name', 'Unknown')}")
        logger.info(f"GPU Memory: {device_info.get('gpu_memory_gb', 'Unknown'):.2f} GB")
    else:
        logger.info("ℹ️  Running on CPU - inference will be slower")
        logger.info("💡 For faster processing, install GPU support (CUDA 11.8+)")
    
    logger.info(f"API Workers: {device_info['api_workers']}")
    logger.info(f"Batch Size: {device_info['batch_size']}")
    logger.info(f"Inference Timeout: {device_info['inference_timeout']}s")
    logger.info(f"Debug: {settings.debug}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("BISINDO CSLR Demo - Shutting down")
    
    # Clear GPU cache if needed
    try:
        from app.utils.device import clear_gpu_cache
        clear_gpu_cache()
    except:
        pass


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - redirects to API docs or frontend"""
    return {
        "status": "ok",
        "message": "BISINDO CSLR Demo API",
        "docs": "/docs",
        "version": "1.0.0"
    }


# Health check
@app.get("/health")
async def health():
    """Simple health check"""
    import torch
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available()
    }


# Error handlers
# ==============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return {
        "status": "error",
        "code": "INTERNAL_ERROR",
        "message": str(exc)
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers if settings.environment == "production" else 1,
        log_level=settings.log_level.lower()
    )

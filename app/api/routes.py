"""
API Routes
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional
from datetime import datetime
import logging

from app.api.schemas import (
    UploadResponse,
    PredictResponse,
    StatusResponse,
    ResultsResponse,
    HealthResponse,
    ErrorResponse
)

router = APIRouter(prefix="/api", tags=["inference"])
logger = logging.getLogger(__name__)


# Temporary storage for demo
_uploads = {}  # video_id -> file info
_jobs = {}     # job_id -> job info
_results = {}  # video_id -> results


@router.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Upload RGB video file.
    
    Returns:
        video_id: Unique identifier for this video
        next_step: URL of next endpoint to call
    """
    try:
        import uuid
        from app.config import settings
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        file_extension = f".{file.filename.split('.')[-1].lower()}"
        from app.utils.constants import SUPPORTED_VIDEO_EXTENSIONS
        
        if file_extension not in SUPPORTED_VIDEO_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported format. Use: {', '.join(SUPPORTED_VIDEO_EXTENSIONS)}"
            )
        
        # Generate video ID
        video_id = str(uuid.uuid4())
        
        # Read file content
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        from app.utils.constants import MAX_UPLOAD_SIZE_BYTES
        if len(content) > MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large (max {MAX_UPLOAD_SIZE_BYTES / (1024*1024)}MB)"
            )
        
        # Save file
        file_path = settings.uploads_dir / f"{video_id}{file_extension}"
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Store metadata
        _uploads[video_id] = {
            'path': str(file_path),
            'filename': file.filename,
            'size_bytes': len(content),
            'timestamp': datetime.now()
        }
        
        logger.info(f"Video uploaded: {video_id} ({file_size_mb:.2f} MB)")
        
        return UploadResponse(
            status="success",
            video_id=video_id,
            message="Video uploaded successfully",
            file_size_mb=file_size_mb,
            next_step="/api/predict"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict", response_model=dict)
async def predict(video_id: str = Query(..., description="Video ID from upload")):
    """
    Run inference on uploaded video.
    
    Returns:
        Predicted glosses and metadata
    """
    try:
        if video_id not in _uploads:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # For now, return mock response (actual inference in Phase 2)
        return {
            "status": "accepted",
            "job_id": f"job_{video_id}",
            "message": "Inference job queued",
            "check_status_url": f"/api/status/job_{video_id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=StatusResponse)
async def check_status(job_id: str):
    """Check job status"""
    try:
        # For now, return mock status (actual implementation in Phase 2)
        return StatusResponse(
            job_id=job_id,
            status="in_progress",
            progress=None
        )
    
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{video_id}", response_model=dict)
async def get_results(video_id: str):
    """Get inference results"""
    try:
        if video_id not in _results:
            return {
                "status": "not_found",
                "message": "Results not yet available"
            }
        
        return {
            "status": "success",
            "results": _results[video_id]
        }
    
    except Exception as e:
        logger.error(f"Results retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import torch
    
    return HealthResponse(
        status="ok",
        version="1.0.0",
        model_loaded=False,  # TODO: check if model is loaded
        gpu_available=torch.cuda.is_available(),
        timestamp=datetime.now()
    )

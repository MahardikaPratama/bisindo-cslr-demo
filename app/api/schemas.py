"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


# Request Schemas
# ===============

class UploadRequest(BaseModel):
    """File upload metadata (implicit - handled by FastAPI)"""
    pass


class PredictRequest(BaseModel):
    """Inference request"""
    video_id: str = Field(..., description="Video ID from upload")
    extract_skeleton: bool = Field(True, description="Extract skeleton visualization")
    return_visualizations: bool = Field(True, description="Return skeleton images")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)


# Response Schemas
# ================

class UploadResponse(BaseModel):
    """File upload response"""
    status: str
    video_id: str
    message: str
    file_size_mb: float
    duration_seconds: Optional[float] = None
    fps: Optional[float] = None
    resolution: Optional[str] = None
    next_step: str = "/predict"


class GlossResult(BaseModel):
    """Single gloss prediction"""
    id: int
    word: str
    confidence: float
    start_frame: int
    end_frame: int
    start_time: str
    end_time: str


class PredictResponse(BaseModel):
    """Inference response"""
    status: str
    video_id: str
    glosses: List[GlossResult]
    full_sentence: str
    sentence_confidence: float
    total_frames: int
    fps: float
    duration_seconds: float
    processing_time: float


class ProgressStage(BaseModel):
    """Single processing stage"""
    percent: int = Field(..., ge=0, le=100)
    status: str  # 'pending', 'in_progress', 'completed'


class JobProgress(BaseModel):
    """Job progress details"""
    stage: str
    percent: int = Field(..., ge=0, le=100)
    stages: Dict[str, ProgressStage]
    elapsed: float
    estimate_remaining: Optional[float] = None


class StatusResponse(BaseModel):
    """Status check response"""
    job_id: str
    status: str  # 'queued', 'in_progress', 'completed', 'failed'
    progress: Optional[JobProgress] = None
    error: Optional[str] = None


class ResultsResponse(BaseModel):
    """Full results response"""
    status: str
    video_id: str
    results: PredictResponse
    metadata: Dict[str, Any]
    timestamp: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    model_loaded: bool
    gpu_available: bool
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    status: str = "error"
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

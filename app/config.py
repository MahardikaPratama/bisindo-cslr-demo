"""
Application Configuration

Supports both GPU (CUDA) and CPU-only modes.
Environment configurations:
- .env.gpu — NVIDIA GPU optimized (4 workers, cuda)
- .env.cpu — CPU-only optimized (1 worker, cpu)
- .env.example — Auto-detect (default)
"""

import os
import torch
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file"""
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # Server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    models_dir: Path = Path(__file__).parent.parent / "models"
    configs_dir: Path = Path(__file__).parent.parent / "configs"
    uploads_dir: Path = Path(__file__).parent.parent / "uploads"
    outputs_dir: Path = Path(__file__).parent.parent / "outputs"
    
    # Model Configuration
    model_path: str = "baseline_model_bisindo.pt"
    gloss_dict_path: str = "bisindo_gloss_dict.json"
    
    # Inference
    device: str = "cuda"  # 'cuda', 'cpu', or 'auto'
    batch_size: int = 1
    inference_timeout: int = 60
    max_video_size_mb: int = 500
    
    # Upload
    upload_dir: Path = uploads_dir
    cleanup_ttl_hours: int = 1
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_device(self) -> str:
        """
        Get the device to use for inference.
        
        Returns:
            str: 'cuda' or 'cpu'
        """
        if self.device.lower() == "auto":
            # Auto-detect: use CUDA if available, else CPU
            if torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        elif self.device.lower() in ["cuda", "gpu"]:
            if torch.cuda.is_available():
                return "cuda"
            else:
                print("⚠️  WARNING: CUDA requested but not available. Falling back to CPU.")
                return "cpu"
        elif self.device.lower() == "cpu":
            return "cpu"
        else:
            # Invalid device, use CPU
            print(f"⚠️  WARNING: Unknown device '{self.device}'. Using CPU.")
            return "cpu"
    
    def get_device_info(self) -> dict:
        """Get information about the configured device."""
        device = self.get_device()
        info = {
            "device": device,
            "cuda_available": torch.cuda.is_available(),
            "api_workers": self.api_workers,
            "batch_size": self.batch_size,
            "inference_timeout": self.inference_timeout,
        }
        
        if device == "cuda":
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1e9
        
        return info


# Load settings
settings = Settings()

# Create necessary directories
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
settings.outputs_dir.mkdir(parents=True, exist_ok=True)
logs_dir = settings.base_dir / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)

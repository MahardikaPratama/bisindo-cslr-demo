"""
Device Management (GPU/CPU)

Supports both NVIDIA GPU (CUDA) and CPU-only modes.
"""

import torch
import logging

logger = logging.getLogger(__name__)


def get_device(device_preference: str = 'cuda') -> torch.device:
    """
    Get PyTorch device (GPU or CPU).
    
    Args:
        device_preference: Preferred device ('cuda', 'cpu', or 'auto')
    
    Returns:
        torch.device object
    
    Examples:
        >>> device = get_device('cuda')  # Use GPU if available
        >>> device = get_device('cpu')   # Force CPU
        >>> device = get_device('auto')  # Auto-detect
    """
    pref = device_preference.lower()
    
    if pref == 'auto':
        # Auto-detect: use CUDA if available, else CPU
        if torch.cuda.is_available():
            device = torch.device('cuda:0')
            logger.info(f"✅ Auto-detected GPU: {torch.cuda.get_device_name(0)}")
            return device
        else:
            device = torch.device('cpu')
            logger.info("ℹ️  GPU not available, using CPU")
            return device
    elif pref in ['cuda', 'gpu']:
        if torch.cuda.is_available():
            device = torch.device('cuda:0')
            logger.info(f"✅ Using GPU: {torch.cuda.get_device_name(0)}")
            return device
        else:
            logger.warning("⚠️  CUDA requested but not available, falling back to CPU")
            device = torch.device('cpu')
            logger.info("Using CPU")
            return device
    elif pref == 'cpu':
        device = torch.device('cpu')
        logger.info("💻 Using CPU for inference")
        return device
    else:
        logger.warning(f"Unknown device '{device_preference}', defaulting to CPU")
        return torch.device('cpu')


def get_device_info() -> dict:
    """
    Get detailed information about available devices.
    
    Returns:
        dict with device information
    """
    info = {
        'cuda_available': torch.cuda.is_available(),
        'pytorch_version': torch.__version__,
    }
    
    if torch.cuda.is_available():
        info['cuda_version'] = torch.version.cuda
        info['cudnn_version'] = torch.backends.cudnn.version()
        info['current_gpu'] = torch.cuda.get_device_name(0)
        info['gpu_count'] = torch.cuda.device_count()
        
        # Get device properties
        props = torch.cuda.get_device_properties(0)
        info['gpu_memory_total_gb'] = props.total_memory / 1e9
        
        # Get allocated memory
        info['gpu_memory_allocated_mb'] = torch.cuda.memory_allocated(0) / 1e6
        info['gpu_memory_cached_mb'] = torch.cuda.memory_reserved(0) / 1e6
        
        # Check CUDA capabilities
        info['max_threads_per_block'] = props.max_threads_per_block
        info['compute_capability'] = f"{props.major}.{props.minor}"
    else:
        info['device'] = 'CPU'
        info['cuda_version'] = None
        info['cudnn_version'] = None
    
    return info


def clear_gpu_cache():
    """Clear GPU cache to free memory after inference"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        logger.info("🧹 GPU cache cleared")
    else:
        logger.debug("GPU not available, cache clearing skipped")

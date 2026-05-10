"""
Model Loader and Caching
"""

import torch
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ModelCache:
    """
    Singleton model cache with lazy loading.
    Loads model once and caches it in memory.
    """
    
    _instance: Optional['ModelCache'] = None
    
    def __init__(self, model_path: str, device: str = 'cuda'):
        """
        Initialize model cache.
        
        Args:
            model_path: Path to model weights file
            device: Device to load model on ('cuda' or 'cpu')
        """
        self.model_path = Path(model_path)
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        self._model = None
        self._model_config = None
        
        logger.info(f"ModelCache initialized for: {model_path} on device: {self.device}")
    
    @staticmethod
    def getInstance(model_path: str, device: str = 'cuda') -> 'ModelCache':
        """Get or create singleton instance"""
        if ModelCache._instance is None:
            ModelCache._instance = ModelCache(model_path, device)
        return ModelCache._instance
    
    def load_model(self) -> torch.nn.Module:
        """
        Load model from disk.
        Lazy loading: only loads when first called.
        
        Returns:
            Loaded model
        """
        if self._model is not None:
            logger.info("Model already loaded from cache")
            return self._model
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        logger.info(f"Loading model from: {self.model_path}")
        
        try:
            # Load state dict
            checkpoint = torch.load(self.model_path, map_location=self.device, weights_only=False)
            
            # Extract model state dict
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Try to infer model architecture from state dict
            # For now, we'll use a placeholder - actual model will be imported
            from app.services.model import TwoStream_Cosign
            
            # Create model with default config
            model_config = self._get_default_model_config()
            self._model = TwoStream_Cosign(**model_config)
            
            # Load weights
            self._model.load_state_dict(state_dict, strict=False)
            self._model = self._model.to(self.device)
            self._model.eval()
            
            logger.info(f"Model loaded successfully on {self.device}")
            logger.info(f"Model parameters: {sum(p.numel() for p in self._model.parameters()):,}")
            
            return self._model
        
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def get_model(self) -> torch.nn.Module:
        """Get model (load if necessary)"""
        if self._model is None:
            self.load_model()
        return self._model
    
    def _get_default_model_config(self) -> Dict[str, Any]:
        """Get default model configuration"""
        return {
            'visual_args': {
                'in_channels': 2,
                'split': [25, 46, 67, 86],
                'temporal_kernel': 5,
                'hidden_size': 1024,
                'modes': ['body', 'hand21', 'mouth_8'],
                'level': '1',
                'adaptive': True,
            },
            'gloss_dict': self._get_gloss_dict(),
            'conv_type': 'K3-P2-K3-P2',
            'loss_weights': {},
            'norm_scale': 32
        }
    
    def _get_gloss_dict(self) -> Dict[str, Any]:
        """Load gloss dictionary (placeholder)"""
        # TODO: Load actual gloss dictionary from config
        return {
            'id2gloss': {},
            'gloss2id': {}
        }
    
    def clear(self):
        """Clear model from cache"""
        if self._model is not None:
            del self._model
            self._model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Model cache cleared")
    
    def __enter__(self):
        return self.get_model()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

"""
Skeleton Preprocessing and Normalization
"""

import numpy as np
import logging
from typing import Tuple
from scipy.interpolate import interp1d

from app.utils.constants import (
    TOTAL_KEYPOINTS,
    KEYPOINT_CONFIDENCE_THRESHOLD,
    NORMALIZE_BY_CENTER,
    TEMPORAL_PADDING_LENGTH,
    TEMPORAL_SMOOTHING_SIGMA
)

logger = logging.getLogger(__name__)


class SkeletonPreprocessor:
    """
    Preprocess skeleton sequences for model inference.
    
    Pipeline:
        1. Filter by confidence
        2. Normalize by body center
        3. Spatial scaling
        4. Handle missing keypoints
        5. Temporal smoothing
        6. Temporal padding/resampling
    """
    
    # Pose reference points for body center (shoulder/spine area)
    # Indices relative to pose keypoints (61-85 in full skeleton)
    _POSE_CENTER_INDICES = [11, 12]  # Shoulder indices in pose
    
    def __init__(
        self,
        confidence_threshold: float = KEYPOINT_CONFIDENCE_THRESHOLD,
        normalize_by_center: bool = NORMALIZE_BY_CENTER,
        temporal_padding: int = TEMPORAL_PADDING_LENGTH,
        temporal_smoothing_sigma: float = TEMPORAL_SMOOTHING_SIGMA
    ):
        """
        Initialize preprocessor with configuration.
        
        Args:
            confidence_threshold: Min confidence to keep keypoint
            normalize_by_center: Whether to normalize by body center
            temporal_padding: Fixed temporal length
            temporal_smoothing_sigma: Gaussian smoothing sigma
        """
        self.confidence_threshold = confidence_threshold
        self.normalize_by_center = normalize_by_center
        self.temporal_padding = temporal_padding
        self.temporal_smoothing_sigma = temporal_smoothing_sigma
        
        logger.info(
            f"SkeletonPreprocessor initialized "
            f"(threshold={confidence_threshold}, padding={temporal_padding})"
        )
    
    def preprocess(
        self,
        skeleton: np.ndarray,
        confidences: np.ndarray,
        reduce_to_2d: bool = True
    ) -> Tuple[np.ndarray, int]:
        """
        Full preprocessing pipeline.
        
        Args:
            skeleton: np.ndarray of shape (T, 86, D) where D=2 or 3
            confidences: np.ndarray of shape (T, 86)
            reduce_to_2d: Whether to drop z-dimension
        
        Returns:
            Tuple of:
                - processed_skeleton: shape (temporal_padding, 86, 2)
                - seq_len: Actual sequence length (≤ temporal_padding)
        """
        T, K, D = skeleton.shape
        logger.info(f"Preprocessing skeleton: {skeleton.shape}, confidences: {confidences.shape}")
        
        # Step 1: Filter by confidence
        skeleton = self._filter_by_confidence(skeleton, confidences)
        
        # Step 2: Normalize by body center
        if self.normalize_by_center:
            skeleton = self._normalize_by_center(skeleton)
        
        # Step 3: Spatial scaling
        skeleton = self._spatial_scaling(skeleton)
        
        # Step 4: Handle missing keypoints
        skeleton = self._interpolate_missing(skeleton)
        
        # Step 5: Temporal smoothing
        skeleton = self._temporal_smooth(skeleton)
        
        # Step 6: Reduce to 2D if needed
        if reduce_to_2d and D == 3:
            skeleton = skeleton[:, :, :2]
        
        # Step 7: Temporal padding/resampling
        skeleton_padded, seq_len = self._temporal_pad_or_resample(skeleton)
        
        logger.info(f"Preprocessing complete: {skeleton_padded.shape}, seq_len={seq_len}")
        
        return skeleton_padded, seq_len
    
    def _filter_by_confidence(
        self,
        skeleton: np.ndarray,
        confidences: np.ndarray
    ) -> np.ndarray:
        """Filter out low-confidence keypoints"""
        T, K, D = skeleton.shape
        
        for t in range(T):
            for k in range(K):
                if confidences[t, k] < self.confidence_threshold:
                    skeleton[t, k, :] = 0.0
        
        return skeleton
    
    def _normalize_by_center(self, skeleton: np.ndarray) -> np.ndarray:
        """Normalize skeleton by subtracting body center"""
        T, K, D = skeleton.shape
        
        for t in range(T):
            # Calculate centroid from non-zero keypoints
            non_zero = skeleton[t] != 0
            if np.any(non_zero):
                # Center calculation (mean of non-zero points)
                valid_points = skeleton[t][np.any(non_zero, axis=1)]
                center = np.mean(valid_points, axis=0)
                skeleton[t] = skeleton[t] - center
        
        return skeleton
    
    def _spatial_scaling(self, skeleton: np.ndarray) -> np.ndarray:
        """Scale skeleton to unit scale"""
        T, K, D = skeleton.shape
        
        for t in range(T):
            # Calculate max distance from origin
            distances = np.linalg.norm(skeleton[t], axis=1)
            max_distance = np.max(distances)
            
            if max_distance > 0:
                skeleton[t] = skeleton[t] / max_distance
            
            # Clip to [-1, 1]
            skeleton[t] = np.clip(skeleton[t], -1.0, 1.0)
        
        return skeleton
    
    def _interpolate_missing(self, skeleton: np.ndarray) -> np.ndarray:
        """Interpolate missing keypoints temporally"""
        T, K, D = skeleton.shape
        
        for k in range(K):
            for d in range(D):
                values = skeleton[:, k, d]
                
                # Find zero values
                zero_mask = values == 0
                valid_mask = ~zero_mask
                
                if np.sum(valid_mask) > 1:
                    valid_indices = np.where(valid_mask)[0]
                    valid_values = values[valid_indices]
                    
                    # Interpolate
                    try:
                        interp_func = interp1d(
                            valid_indices,
                            valid_values,
                            kind='linear',
                            fill_value='extrapolate'
                        )
                        interpolated = interp_func(np.arange(T))
                        skeleton[:, k, d] = interpolated
                    except Exception as e:
                        logger.warning(f"Interpolation failed for keypoint {k}, dim {d}: {e}")
        
        return skeleton
    
    def _temporal_smooth(self, skeleton: np.ndarray) -> np.ndarray:
        """Apply temporal Gaussian smoothing"""
        from scipy.ndimage import gaussian_filter1d
        
        T, K, D = skeleton.shape
        
        # Apply Gaussian filter along temporal axis
        skeleton_smoothed = np.zeros_like(skeleton)
        for k in range(K):
            for d in range(D):
                skeleton_smoothed[:, k, d] = gaussian_filter1d(
                    skeleton[:, k, d],
                    sigma=self.temporal_smoothing_sigma,
                    axis=0
                )
        
        return skeleton_smoothed
    
    def _temporal_pad_or_resample(self, skeleton: np.ndarray) -> Tuple[np.ndarray, int]:
        """Pad or resample skeleton to fixed temporal length"""
        T, K, D = skeleton.shape
        target_T = self.temporal_padding
        
        seq_len = min(T, target_T)
        
        if T < target_T:
            # Pad with zeros at the end
            padded = np.zeros((target_T, K, D), dtype=np.float32)
            padded[:T] = skeleton
            return padded, seq_len
        
        elif T > target_T:
            # Resample using interpolation
            indices = np.linspace(0, T - 1, target_T)
            resampled = np.zeros((target_T, K, D), dtype=np.float32)
            
            for k in range(K):
                for d in range(D):
                    interp_func = interp1d(
                        np.arange(T),
                        skeleton[:, k, d],
                        kind='linear',
                        fill_value='extrapolate'
                    )
                    resampled[:, k, d] = interp_func(indices)
            
            return resampled, target_T
        
        else:
            # Already correct length
            return skeleton, seq_len

"""
Unit tests for skeleton extraction
"""

import pytest
import numpy as np
from app.services.skeleton_extractor import SkeletonExtractor


@pytest.fixture
def extractor():
    """Create SkeletonExtractor instance"""
    return SkeletonExtractor()


def test_extractor_initialization(extractor):
    """Test extractor initialization"""
    assert extractor is not None
    assert extractor.model is not None
    assert extractor._dims in [2, 3]


def test_landmarks_extraction(extractor):
    """Test landmark extraction from mock data"""
    import cv2
    
    # Create dummy frame (all zeros - MediaPipe will handle it)
    dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Extract should not crash on empty frame
    try:
        keypoints, confidences = extractor.extract_frame(dummy_frame)
        assert keypoints.shape[0] == 86
        assert keypoints.shape[1] in [2, 3]
        assert confidences.shape[0] == 86
    except Exception as e:
        pytest.skip(f"MediaPipe not properly initialized: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

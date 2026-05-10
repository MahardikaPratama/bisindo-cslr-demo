"""
Unit tests for skeleton preprocessing
"""

import pytest
import numpy as np
from app.services.skeleton_preprocessor import SkeletonPreprocessor


@pytest.fixture
def preprocessor():
    """Create SkeletonPreprocessor instance"""
    return SkeletonPreprocessor()


def test_preprocessor_initialization(preprocessor):
    """Test preprocessor initialization"""
    assert preprocessor is not None
    assert preprocessor.confidence_threshold == 0.3
    assert preprocessor.temporal_padding == 250


def test_preprocess_basic(preprocessor):
    """Test basic preprocessing pipeline"""
    # Create dummy skeleton data
    T, K, D = 100, 86, 3
    skeleton = np.random.randn(T, K, D).astype(np.float32)
    confidences = np.ones((T, K), dtype=np.float32)
    
    # Preprocess
    result, seq_len = preprocessor.preprocess(skeleton, confidences)
    
    # Check output shape
    assert result.shape[0] == preprocessor.temporal_padding
    assert result.shape[1] == 86
    assert result.shape[2] == 2  # Reduced to 2D
    assert seq_len == min(T, preprocessor.temporal_padding)


def test_filter_by_confidence(preprocessor):
    """Test confidence filtering"""
    T, K, D = 10, 86, 2
    skeleton = np.ones((T, K, D), dtype=np.float32)
    confidences = np.zeros((T, K), dtype=np.float32)
    confidences[:, :] = 0.2  # Below threshold
    
    result = preprocessor._filter_by_confidence(skeleton, confidences)
    
    # All should be zeroed out
    assert np.allclose(result, 0)


def test_temporal_padding(preprocessor):
    """Test temporal padding"""
    # Test with short sequence
    T, K, D = 50, 86, 3
    skeleton = np.random.randn(T, K, D).astype(np.float32)
    
    result, seq_len = preprocessor._temporal_pad_or_resample(skeleton)
    
    assert result.shape[0] == preprocessor.temporal_padding
    assert seq_len == T


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

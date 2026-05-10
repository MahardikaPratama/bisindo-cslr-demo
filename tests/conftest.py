"""
Conftest for pytest
"""

import pytest


@pytest.fixture
def sample_video_path():
    """Path to sample video for testing"""
    from pathlib import Path
    return Path(__file__).parent / "fixtures" / "sample_video.mp4"

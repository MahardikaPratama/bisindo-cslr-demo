"""
Constants for BISINDO CSLR Demo
"""

# Keypoint Layout (Isharah 86-Point Format)
# ============================================

# Left Hand: 21 keypoints (indices 0-20)
LEFT_HAND_RANGE = (0, 21)

# Right Hand: 21 keypoints (indices 21-41)
RIGHT_HAND_RANGE = (21, 42)

# Mouth: 19 keypoints (indices 42-60)
MOUTH_RANGE = (42, 61)

# Pose: 25 keypoints (indices 61-85)
POSE_RANGE = (61, 86)

# Total keypoints
TOTAL_KEYPOINTS = 86

# Keypoint dimensions
USE_3D_COORDINATES = False  # Use 2D only (x, y)
KEYPOINT_DIMS = 2 if not USE_3D_COORDINATES else 3

# MediaPipe Configuration
# =======================
MEDIAPIPE_CONFIG = {
    'static_image_mode': False,
    'model_complexity': 1,  # 0=light, 1=full, 2=heavy
    'smooth_landmarks': True,
    'enable_segmentation': False,
    'smooth_segmentation': False,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5
}

# Confidence Threshold
KEYPOINT_CONFIDENCE_THRESHOLD = 0.3

# Skeleton Normalization
# ======================
NORMALIZE_BY_CENTER = True
TEMPORAL_PADDING_LENGTH = 250  # Fixed temporal length for model
TEMPORAL_SMOOTHING_SIGMA = 1.0

# CTC Decoding
# ============
CTC_BEAM_WIDTH = 10
CTC_BLANK_ID = 0

# Video Processing
# ================
VIDEO_FPS = 25
MAX_VIDEO_DURATION_SECONDS = 600  # 10 minutes
SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}

# API
# ===
MAX_UPLOAD_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB
REQUEST_TIMEOUT_SECONDS = 60

# Error Messages
# ==============
ERROR_MESSAGES = {
    'INVALID_FILE': 'File format not supported. Use: mp4, avi, mov, webm, mkv',
    'FILE_TOO_LARGE': f'File size exceeds {500}MB limit',
    'EXTRACTION_FAILED': 'Failed to extract skeleton from video',
    'MODEL_ERROR': 'Model inference failed',
    'TIMEOUT': 'Processing took too long (>60 seconds)',
    'GPU_OOM': 'GPU out of memory',
    'NOT_FOUND': 'Resource not found',
    'INVALID_REQUEST': 'Invalid request parameters'
}

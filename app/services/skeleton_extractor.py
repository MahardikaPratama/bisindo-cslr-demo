"""
MediaPipe Skeleton Extractor - 86 Keypoint Extraction
Based on Isharah format for BISINDO
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
from typing import Tuple, Optional

from app.utils.constants import (
    MEDIAPIPE_CONFIG,
    TOTAL_KEYPOINTS,
    USE_3D_COORDINATES,
    LEFT_HAND_RANGE,
    RIGHT_HAND_RANGE,
    MOUTH_RANGE,
    POSE_RANGE,
    KEYPOINT_CONFIDENCE_THRESHOLD
)

logger = logging.getLogger(__name__)


class SkeletonExtractor:
    """
    Extract 86-keypoint skeleton from video frames using MediaPipe Holistic.
    
    Keypoint Layout (Isharah Format):
        Indices  0-20:  Left Hand  (21 points)
        Indices 21-40:  Right Hand (21 points)
        Indices 42-60:  Mouth      (19 points)
        Indices 61-85:  Pose       (25 points)
    """
    
    # Mouth landmark indices (lip contour from 468-point face mesh)
    _MOUTH_INDICES = [
        # Outer lip (10 points, clockwise)
        61, 185, 40, 39, 37, 0, 267, 269, 270, 409,
        # Inner lip (9 points)
        78, 191, 80, 81, 82, 13, 312, 311, 308,
    ]  # Total: 19
    
    def __init__(self):
        """Initialize MediaPipe Holistic"""
        self.mp_holistic = mp.solutions.holistic
        self.model = self.mp_holistic.Holistic(**MEDIAPIPE_CONFIG)
        self._dims = 3 if USE_3D_COORDINATES else 2
        logger.info(f"SkeletonExtractor initialized (dims={self._dims}D)")
    
    def extract_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract 86 keypoints from a single BGR frame.
        
        Args:
            frame: BGR video frame from OpenCV
        
        Returns:
            keypoints: np.ndarray of shape (86, dims) where dims=2 or 3
            confidences: np.ndarray of shape (86,) with confidence scores
        """
        # Convert BGR to RGB for MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model.process(rgb)
        
        keypoints = []
        confidences = []
        
        # Extract left hand (21 points, indices 0-20)
        left_hand_kpts, left_hand_conf = self._extract_landmarks(
            results.left_hand_landmarks,
            range(LEFT_HAND_RANGE[1] - LEFT_HAND_RANGE[0])
        )
        keypoints.extend(left_hand_kpts)
        confidences.extend(left_hand_conf)
        
        # Extract right hand (21 points, indices 21-40)
        right_hand_kpts, right_hand_conf = self._extract_landmarks(
            results.right_hand_landmarks,
            range(RIGHT_HAND_RANGE[1] - RIGHT_HAND_RANGE[0])
        )
        keypoints.extend(right_hand_kpts)
        confidences.extend(right_hand_conf)
        
        # Extract mouth (19 points, indices 42-60)
        mouth_kpts, mouth_conf = self._extract_landmarks(
            results.face_landmarks,
            self._MOUTH_INDICES
        )
        keypoints.extend(mouth_kpts)
        confidences.extend(mouth_conf)
        
        # Extract pose (25 points, indices 61-85)
        pose_kpts, pose_conf = self._extract_landmarks(
            results.pose_landmarks,
            range(POSE_RANGE[1] - POSE_RANGE[0])
        )
        keypoints.extend(pose_kpts)
        confidences.extend(pose_conf)
        
        return np.array(keypoints, dtype=np.float32), np.array(confidences, dtype=np.float32)
    
    def _extract_landmarks(
        self,
        landmarks_obj,
        indices
    ) -> Tuple[list, list]:
        """
        Extract landmarks from MediaPipe object.
        
        Args:
            landmarks_obj: MediaPipe landmarks object or None
            indices: Landmark indices to extract
        
        Returns:
            Tuple of (landmarks_list, confidences_list)
        """
        empty_point = [0.0] * self._dims
        empty_confidence = 0.0
        
        if landmarks_obj is None:
            return (
                [list(empty_point) for _ in indices],
                [empty_confidence for _ in indices]
            )
        
        landmarks = []
        confidences = []
        
        for idx in indices:
            if idx < len(landmarks_obj.landmark):
                lm = landmarks_obj.landmark[idx]
                
                if self._dims == 3:
                    landmarks.append([lm.x, lm.y, lm.z])
                else:
                    landmarks.append([lm.x, lm.y])
                
                # Confidence (presence) - default to 1.0 if not available
                confidence = getattr(lm, 'presence', 1.0)
                confidences.append(confidence)
            else:
                landmarks.append(list(empty_point))
                confidences.append(empty_confidence)
        
        return landmarks, confidences
    
    def extract_video(
        self,
        video_path: str,
        fps: int = 25,
        max_frames: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, dict]:
        """
        Extract skeleton from entire video.
        
        Args:
            video_path: Path to video file
            fps: Target frames per second
            max_frames: Maximum frames to process (None = all)
        
        Returns:
            Tuple of:
                - skeleton: np.ndarray of shape (T, 86, dims)
                - confidences: np.ndarray of shape (T, 86)
                - metadata: dict with video info
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise RuntimeError(f"Failed to open video: {video_path}")
        
        # Get video metadata
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate frame interval for target fps
        frame_interval = int(video_fps / fps) if fps < video_fps else 1
        
        skeletons = []
        confidences_list = []
        frame_count = 0
        
        logger.info(f"Extracting skeleton from video: {video_path}")
        logger.info(f"Video info: {width}x{height}, {video_fps} fps, {total_frames} frames")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            # Sample frames at target fps
            if frame_count % frame_interval == 0:
                try:
                    keypoints, frame_confidences = self.extract_frame(frame)
                    skeletons.append(keypoints)
                    confidences_list.append(frame_confidences)
                except Exception as e:
                    logger.warning(f"Error extracting frame {frame_count}: {e}")
                    # Fill with zeros
                    skeletons.append(np.zeros((TOTAL_KEYPOINTS, self._dims), dtype=np.float32))
                    confidences_list.append(np.zeros(TOTAL_KEYPOINTS, dtype=np.float32))
                
                if max_frames and len(skeletons) >= max_frames:
                    break
            
            frame_count += 1
        
        cap.release()
        
        skeleton_array = np.array(skeletons, dtype=np.float32)
        confidences_array = np.array(confidences_list, dtype=np.float32)
        
        metadata = {
            'video_path': video_path,
            'original_fps': video_fps,
            'target_fps': fps,
            'frame_interval': frame_interval,
            'total_frames': total_frames,
            'extracted_frames': len(skeletons),
            'width': width,
            'height': height,
            'duration_seconds': total_frames / video_fps
        }
        
        logger.info(f"Extracted {len(skeletons)} frames from video")
        
        return skeleton_array, confidences_array, metadata
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'model'):
            self.model.close()

# BISINDO CSLR Demo System — Comprehensive Implementation Plan

**Version:** 1.0  
**Date:** May 2026  
**Target:** Production-grade inference and demonstration system  
**Scope:** End-to-end web demo for BISINDO Continuous Sign Language Recognition (CSLR)

---

## 1. Project Overview

### Purpose
Build a **polished, user-friendly web demonstration system** for BISINDO Continuous Sign Language Recognition. The system enables end users to upload Indonesian Sign Language (BISINDO) videos and receive real-time gloss predictions using a deep learning model trained on skeleton keypoints.

### Scope
- **In-Scope:**
  - RGB video upload & preprocessing
  - Automatic skeleton extraction via MediaPipe
  - Skeleton formatting & normalization
  - Inference using trained BISINDO model
  - Gloss sequence prediction with confidence scores
  - Modern, responsive UI with real-time visualization
  - Full end-to-end pipeline

- **Out-of-Scope:**
  - Training logic (removed entirely)
  - Distributed training infrastructure
  - Experiment tracking & hyperparameter tuning
  - Complex data augmentation (inference-only)
  - Multi-model ensembling

### Demo Objectives
1. **User Adoption:** Provide intuitive interface for non-technical users to test BISINDO CSLR
2. **Reproducibility:** Demonstrate model performance on custom videos
3. **Research Validation:** Enable researchers to verify predictions visually
4. **Deployment Ready:** Serve as foundation for production deployment (Heroku, AWS, Google Cloud)

### Expected User Flow
```
User opens webpage
    ↓
Selects/uploads RGB video
    ↓
System shows upload progress
    ↓
Backend extracts frames and runs MediaPipe skeleton extraction
    ↓
System shows skeleton visualization & extraction progress
    ↓
Model runs inference with normalization & preprocessing
    ↓
CTC decoder outputs gloss sequence
    ↓
Results displayed: predicted glosses, confidence, timeline, skeleton preview
    ↓
User can download results or test another video
```

---

## 2. Repository Analysis

### 2.1 RGB-to-Skeleton-MediaPipe Repository

#### Purpose
Standardized preprocessing pipeline for converting BISINDO RGB videos into 86-keypoint skeleton sequences using MediaPipe Holistic API.

#### Important Modules

| Module | Purpose | Reusable? | Notes |
|--------|---------|-----------|-------|
| `src/extractor/holistic_86.py` | MediaPipe extraction → 86 keypoints | ✅ **YES** | Core extractor; minimal dependencies |
| `src/core/pipeline.py` | Orchestration & file I/O | ⚠️ **PARTIAL** | Designed for batch processing; need inference-only wrapper |
| `src/converter/` | Pickle/Excel export | ❌ **NO** | Unnecessary for web demo |
| `src/config/` | Configuration constants | ✅ **YES** | Keypoint ranges, MediaPipe settings |
| `src/processor/` | Video frame processing | ✅ **YES** | Frame extraction, rotation handling |
| `src/utils/` | General utilities | ⚠️ **PARTIAL** | Some usable; others are dataset-specific |

#### Key Technical Details
- **Keypoint Count:** 86 total keypoints per frame
  - Left Hand (GL): 21 points (indices 0–20)
  - Right Hand (GR): 21 points (indices 21–41)
  - Mouth (GM): 19 points (indices 42–60)
  - Pose (GP): 25 points (indices 61–85)

- **Output Format:** NumPy array with shape `(T, 86, 2)` or `(T, 86, 3)`
  - T = number of frames
  - 2D: [x, y] normalized coordinates (0.0–1.0)
  - 3D: [x, y, z] with depth information

- **MediaPipe Version Constraint:** Must use `mediapipe==0.10.14`
  - Versions ≥ 0.10.18 removed `mp.solutions.holistic` (legacy API)
  - This is critical for compatibility

#### Unnecessary Files
- `notebooks/` — visualization/analysis notebooks
- `splitting_data/` — dataset splitting (not needed for inference)
- `data/` — raw training/test data folders

#### Adaptation Strategy
1. **Extract `holistic_86.py`** as-is (minimal changes)
2. **Simplify `pipeline.py`** → create inference-focused wrapper `SkeletonExtractor`
3. **Remove file I/O logic** → handle video frames in memory (streaming)
4. **Wrap config constants** in a dedicated module
5. **Handle video upload** via FastAPI file endpoints

#### Dependency Concerns
- **MediaPipe 0.10.14** → strictly required; conflicts with newer versions
- **OpenCV** → required for frame extraction
- **NumPy** → required for keypoint arrays
- **Pandas/Openpyxl** → can be removed (used only for Excel export)
- **Streamlit** → can be removed (we use FastAPI + React)

#### Expected Refactoring
- Remove all training/data split logic
- Simplify frame handling (memory-based instead of file-based)
- Add batch processing support for streaming inference
- Handle variable video lengths gracefully
- Add error handling for missing keypoints/low confidence

---

### 2.2 MSLR_ICCV2025 Repository

#### Purpose
Skeleton-based CSLR model architecture and full training/evaluation pipeline. Contains the trained BISINDO model (`models/baseline_model_bisindo.pt`).

#### Important Modules

| Module | Purpose | Reusable? | Notes |
|--------|---------|-----------|-------|
| `slr_network.py` | Model definition (TwoStream_Cosign) | ✅ **YES** | Core architecture; inference-only |
| `modules/visual_extractor.py` | Feature extraction (ST-GCN) | ✅ **YES** | Spatial-temporal graph convolution |
| `modules/temporal_layers/` | BiLSTM, temporal convolution | ✅ **YES** | Sequence modeling |
| `utils/decode.py` | CTC beam search decoder | ✅ **YES** | Gloss prediction from logits |
| `utils/skeleton_augmentation.py` | Data transforms | ⚠️ **PARTIAL** | Some augmentations useful; training-only ones removed |
| `datasets/skeleton_feeder.py` | Data loader | ⚠️ **PARTIAL** | Need lightweight version for single-video inference |
| `evaluation/slr_eval/` | WER calculation, evaluation | ❌ **NO** | Only needed for batch evaluation |
| `configs/Double_Cosign_sd.yaml` | Model hyperparameters | ✅ **YES** | Contains model architecture details |
| `preprocess/` | Data preprocessing scripts | ❌ **NO** | Training-only preprocessing |
| `ctcdecode/` | CTC decoding library | ✅ **YES** | Required dependency; included in repo |

#### Key Technical Details

**Model Architecture (TwoStream_Cosign):**
- Dual-stream: Static (pose) and Motion (temporal delta) streams
- Fusion: Combined features from both streams
- Each stream: ST-GCN feature extraction → Temporal Conv → BiLSTM → CTC classifier
- CTC Loss with optional class weighting
- Output: Logits per frame → CTC beam decoder → gloss sequence

**Input Shape Requirements:**
- **Input:** `(B, T, 86, 2)` or `(B, T, 86, 3)` where:
  - B = batch size (1 for inference)
  - T = temporal frames (variable, typically 100–200)
  - 86 = keypoints
  - 2 or 3 = coordinates (x, y) or (x, y, z)

**Preprocessing Pipeline (For Inference):**
1. **Skeleton Normalization:** 
   - Normalize keypoints by body center (reference point)
   - Optional Z-score normalization per joint
   - Handling missing keypoints (confidence < threshold)

2. **Spatial Standardization:**
   - Split skeleton into body parts: [body, hand21, mouth_8]
   - Each part normalized independently
   - Output shape: `(T, 86, 2)` → `(T, C)` after flattening

3. **Temporal Padding:**
   - Pad or resample to fixed length (~250 frames typical)
   - Store actual sequence length for CTC loss

4. **Tensor Conversion:**
   - Convert NumPy → PyTorch tensor
   - Move to GPU if available

**Decoding Process:**
- Model outputs logits: `(T, B, num_classes)` where num_classes ≈ 200–300
- CTC beam search (beam width = 10) decodes logits → gloss indices
- Gloss dictionary maps indices → actual words
- Remove consecutive duplicates (CTC merging)

#### Unnecessary Files
- `main.py` — training script
- `seq_scripts.py` — training loop
- `configs/` (except architecture details) — hyperparameters tuned for training
- `work_dir/` — training outputs
- Training-specific augmentations (jitter, dropout, etc.)
- Class weighting logic (optional for inference)

#### Adaptation Strategy
1. **Extract model & decoding logic** → `InferenceModel` class
2. **Simplify `skeleton_feeder.py`** → create `SkeletonPreprocessor` for single-video
3. **Create minimal config** → only inference-critical parameters
4. **Wrap `Decode` class** → integrate with model for end-to-end inference
5. **Handle GPU/CPU dynamically** → device auto-detection

#### Dependency Concerns
- **PyTorch** → required (model inference)
- **ctcdecode** → included in repo; beam search decoding
- **NumPy/SciPy** → required for preprocessing
- **YAML** → minimal; used for config parsing
- **Distribute training dependencies** → completely removed (torch.distributed, etc.)
- **LightningPL, Wandb, etc.** → removed

#### Expected Refactoring
- Remove all training-related code (optimizer, loss computation, checkpointing)
- Simplify model loading (only `state_dict` required)
- Create lightweight data processor (no augmentation, no batching complexity)
- Make tensor shapes explicit & document clearly
- Add confidence/uncertainty estimation if possible

---

## 3. System Architecture

### High-Level Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React/Jinja2)                  │
│                                                               │
│  [Upload Widget] → [Progress Bar] → [Results Dashboard]     │
│   (video select)     (extraction)    (glosses + skeleton)    │
└────────────────┬────────────────────────────────────────────┘
                 │ (HTTP/WebSocket)
                 ↓
┌─────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Async)                        │
│                                                               │
│  [API Endpoints] → [Job Queue] → [Inference Worker]         │
│  /upload /predict                 (async processing)         │
│  /visualize /status                                          │
│  /health                                                     │
└────────┬──────────────┬──────────────┬──────────────────────┘
         │              │              │
         ↓              ↓              ↓
    ┌────────────────────────────────────────┐
    │   INFERENCE PIPELINE (Sequential)      │
    │                                        │
    │  1. Video Frame Extraction             │
    │     └→ VideoProcessor.extract_frames() │
    │                                        │
    │  2. MediaPipe Extraction               │
    │     └→ SkeletonExtractor.extract()     │
    │     └→ shape: (T, 86, 2)               │
    │                                        │
    │  3. Skeleton Preprocessing             │
    │     └→ SkeletonPreprocessor.process()  │
    │     └→ Normalization, padding, etc.    │
    │                                        │
    │  4. Model Inference                    │
    │     └→ Model.forward()                 │
    │     └→ Output logits: (T, B, C)        │
    │                                        │
    │  5. CTC Decoding                       │
    │     └→ CTCDecoder.decode()             │
    │     └→ Output: gloss sequence          │
    │                                        │
    └────────────────────────────────────────┘
                 │
         ┌───────┴────────┐
         ↓                ↓
    ┌────────────┐   ┌────────────────┐
    │  Results   │   │  Visualization │
    │ (glosses)  │   │  (skeletons)   │
    └────────────┘   └────────────────┘
         │                │
         └────────┬───────┘
                  ↓
         ┌──────────────────┐
         │ JSON Response    │
         │ (via WebSocket)  │
         └──────────────────┘
```

### Component Breakdown

**1. Frontend Layer**
- User interface for video upload
- Progress visualization (extraction, inference)
- Results display (glosses, skeleton preview, timeline)
- Real-time updates via WebSocket/Server-Sent Events (SSE)

**2. FastAPI Backend**
- REST/WebSocket API endpoints
- Async request handling (multiple uploads)
- Job queue for sequential inference
- File upload handling with size limits

**3. Skeleton Extraction Service**
- MediaPipe-based frame-by-frame extraction
- Handles variable-length videos
- Stores extracted skeletons in memory (for single demo)
- Returns: numpy array (T, 86, 2)

**4. Preprocessing Service**
- Normalizes skeleton coordinates
- Handles missing/low-confidence keypoints
- Pads/resamples to fixed temporal length
- Applies inference-only transforms
- Returns: torch tensor (1, T, C) ready for model

**5. Inference Engine**
- Loads trained BISINDO model
- Runs forward pass on preprocessed skeleton
- Returns raw logits: (1, T, num_classes)
- Handles GPU/CPU device management

**6. Decoding Service**
- CTC beam search decoding
- Maps indices → gloss words
- Filters consecutive duplicates
- Returns: list of (gloss, confidence) tuples

**7. Visualization Service**
- Renders skeleton coordinates as 2D visualization
- Frame-by-frame skeleton preview
- Optional timeline with predicted glosses
- Outputs JSON for frontend rendering

### Storage Strategy
- **Temporary Files:** Uploaded videos stored temporarily in `/uploads/` (TTL-based cleanup)
- **Model Weights:** `models/baseline_model_bisindo.pt` (read-only, cached in memory)
- **Gloss Dictionary:** JSON file loaded at startup
- **In-Memory Processing:** Skeletons processed in-memory (avoid disk bottleneck)

---

## 4. End-to-End Inference Pipeline

### Detailed Processing Steps

```
STEP 1: VIDEO UPLOAD & INGESTION
  Input: User uploads .mp4, .avi, or .mov file
  Process:
    - File validation (format, size ≤ 500MB)
    - Store temp file with UUID name: /uploads/{uuid}.mp4
    - Extract video metadata (duration, fps, resolution)
  Output: video_id, metadata dict

STEP 2: FRAME EXTRACTION
  Input: video_path, fps (default: 25 fps)
  Process:
    - Use OpenCV VideoCapture to read frames
    - Extract frames at specified fps (resample if needed)
    - Convert BGR → RGB for MediaPipe
    - Skip corrupted frames with fallback to nearest valid frame
  Output: frames list, shape (T, H, W, 3), actual_fps

STEP 3: SKELETON EXTRACTION (MEDIAPIPE)
  Input: frames (T, H, W, 3)
  Process:
    FOR EACH frame:
      - Run MediaPipe Holistic detection
      - Extract 86 keypoints [x, y, z] (world coordinates)
      - Normalize to [x, y, z] ∈ [0, 1] (relative to frame)
      - Handle missing keypoints:
        * If confidence < 0.5: fill with [0, 0, 0]
        * Store per-keypoint confidence separately
      - Arrange in 86-keypoint order:
        * Indices  0–20:  Left Hand (21 points)
        * Indices 21–41:  Right Hand (21 points)
        * Indices 42–60:  Mouth (19 points)
        * Indices 61–85:  Pose (25 points)
  Output: skeleton array, shape (T, 86, 3), confidence array (T, 86)

STEP 4: SKELETON NORMALIZATION & PREPROCESSING
  Input: skeleton (T, 86, 3), confidence (T, 86)
  Process:
    4.1 Keypoint Confidence Filtering:
        - If confidence < threshold (0.3): zero out keypoint
    
    4.2 Body-Center Normalization (critical!):
        - Identify reference point: center of shoulder/spine (index ~62-63)
        - Compute centroid: mean of all non-zero keypoints
        - Subtract centroid from all keypoints
        - Result: skeleton relative to body center
    
    4.3 Spatial Scaling:
        - Compute max distance from center to any keypoint
        - Scale all keypoints by 1/max_distance (normalize to unit scale)
        - Clip to [-1, 1] range
    
    4.4 Missing Keypoint Handling:
        - For each frame, if > 50% keypoints missing:
          * Interpolate from adjacent frames (temporal smoothing)
        - For isolated missing keypoints:
          * Use spatial interpolation from neighbors
    
    4.5 Temporal Smoothing (optional):
        - Apply light Gaussian smoothing over temporal window (±3 frames)
        - Reduce jitter from MediaPipe
    
    4.6 Reduce to 2D (if needed):
        - Use only [x, y], drop z-coordinate
        - Model trained on 2D; z-info not critical
  Output: normalized_skeleton (T, 86, 2)

STEP 5: TEMPORAL PADDING/RESAMPLING
  Input: normalized_skeleton (T, 86, 2)
  Process:
    - Determine target length: T_max = 250 (typical)
    - If T < T_max:
        * Pad with zeros at end: (T_max, 86, 2)
    - If T > T_max:
        * Resample using linear interpolation to T_max
        * Or: keep original T (variable length okay for model)
    - Store sequence length: seq_len = min(T, T_max)
  Output: padded_skeleton (T_max, 86, 2), seq_len

STEP 6: TENSOR CONVERSION & RESHAPING
  Input: padded_skeleton (T_max, 86, 2), seq_len
  Process:
    - Convert NumPy → PyTorch tensor
    - Reshape for model input:
      * Model expects: (B, T, C) where B=1, T=T_max, C=feature_dim
      * Feature dim depends on model architecture:
        - If skeleton is split into parts: C = sum of part features
        - Typical: C = 86 × 2 = 172 (flattened)
      * Final shape: (1, T_max, 172)
    - Move to device (GPU if available, else CPU)
  Output: input_tensor (1, T_max, 172), device

STEP 7: MODEL INFERENCE
  Input: input_tensor (1, T_max, 172), seq_len
  Process:
    - Load model (lazy-load on first request, cache thereafter)
    - Set model to eval mode: model.eval()
    - Forward pass (no_grad):
      * inputs_dict = {'x': input_tensor, 'len_x': torch.tensor([seq_len])}
      * output_dict = model(inputs_dict)
      * Output contains logits from multiple streams:
        - 'conv1d_logits_fusion': (T_max, 1, num_classes)
        - 'seq_logits_fusion': (T_max, 1, num_classes)
    - Select primary output: seq_logits (contextual, better quality)
    - Reshape: (T_max, 1, num_classes) → (T_max, num_classes)
  Output: logits (T_max, num_classes), seq_len

STEP 8: CTC BEAM SEARCH DECODING
  Input: logits (T_max, num_classes), seq_len
  Process:
    - Prepare logits for CTC decoder:
      * Apply log_softmax: log_probs = F.log_softmax(logits, dim=-1)
      * Normalize by model scale factor: log_probs * norm_scale
    - CTC Beam Decoder parameters:
      * Beam width: 10
      * Blank ID: 0 (reserved for CTC blank)
      * Vocab: generated from gloss dictionary
    - Decode:
      * ctc_decoder.decode(log_probs, [seq_len])
      * Returns: beam_results (B, beam_width, T), out_lens, scores
    - Extract best path:
      * result = beam_results[0, 0, :out_lens[0, 0]]  # First batch, first beam
      * Maps indices → gloss IDs via gloss dictionary
    - Post-processing:
      * Remove consecutive duplicates (CTC merging)
      * Filter blank tokens (index 0)
      * Convert indices → gloss words
  Output: predicted_glosses (list of strings), confidence_scores (list of floats)

STEP 9: VISUALIZATION PREPARATION
  Input: skeleton (T, 86, 2), predicted_glosses, seq_len
  Process:
    - Select key frames for visualization:
      * Start frame, middle frame, end frame (or every N frames)
    - For each frame:
      * Render skeleton as 2D plot (keypoints + connections)
      * Overlay predicted gloss (if available)
      * Convert to base64 image for frontend
    - Prepare timeline data:
      * Map each gloss to frame range
      * Create timeline JSON: [{'gloss': word, 'start': t1, 'end': t2}, ...]
  Output: visualization_json, skeleton_images (base64)

STEP 10: RESULT COMPILATION & RESPONSE
  Input: predicted_glosses, confidence_scores, visualizations, metadata
  Process:
    - Compile JSON response:
      {
        'status': 'success',
        'video_id': uuid,
        'glosses': ['এক', 'দুই', 'তিন', ...],
        'confidences': [0.95, 0.87, 0.92, ...],
        'full_sentence': 'এক দুই তিন ...',
        'processing_time': 3.2,
        'skeleton_frames': [base64_img1, ...],
        'timeline': [{'gloss': ..., 'start': ...}, ...],
        'metadata': {'duration': 5.2, 'fps': 25, ...}
      }
    - Cleanup:
      * Delete temp video file
      * Release GPU memory if batch size=1
  Output: JSON response to frontend

STEP 11: ERROR HANDLING & FALLBACK
  Failure Points & Mitigations:
    - Video format unsupported: return 400 Bad Request
    - Video corrupted: skip frames, proceed with valid ones
    - MediaPipe extraction fails: log warning, use zero skeleton
    - Model inference OOM: fall back to CPU
    - CTC decoding produces empty result: return empty glosses + log
    - Timeout (>30sec): cancel and return 504 timeout error
```

---

## 5. Folder Structure

### Complete Directory Layout for `bisindo-cslr-demo/`

```
bisindo-cslr-demo/
│
├── README.md                          # Project documentation & quick start
├── .gitignore                         # Standard Python .gitignore
├── plan.md                            # THIS FILE: implementation plan
│
├── models/                            # Trained model weights
│   └── baseline_model_bisindo.pt     # Pre-trained BISINDO CSLR model (CRITICAL)
│
├── configs/                           # Inference-only configuration files
│   ├── inference.yaml                 # Model & inference hyperparameters
│   ├── dataset_info/                  # Gloss dictionary & metadata
│   │   ├── bisindo_gloss_dict.json   # Mapping: gloss ↔ index
│   │   └── bisindo_metadata.json     # Dataset info (vocab size, etc.)
│   └── mediapipe_config.yaml         # MediaPipe extraction settings
│
├── app/                               # FastAPI application
│   ├── __init__.py
│   ├── main.py                        # FastAPI app initialization & endpoints
│   ├── config.py                      # App configuration (paths, settings)
│   ├── server.py                      # Development/production server runner
│   │
│   ├── api/                           # API endpoint handlers
│   │   ├── __init__.py
│   │   ├── routes.py                  # /upload, /predict, /health, etc.
│   │   ├── schemas.py                 # Pydantic models for requests/responses
│   │   └── middleware.py              # CORS, auth, logging middleware
│   │
│   ├── services/                      # Core inference services
│   │   ├── __init__.py
│   │   ├── video_processor.py         # Frame extraction from uploaded videos
│   │   ├── skeleton_extractor.py      # MediaPipe → 86 keypoints
│   │   ├── skeleton_preprocessor.py   # Normalization & preprocessing
│   │   ├── model_loader.py            # Load & cache trained model
│   │   ├── inference_engine.py        # Model forward pass
│   │   ├── ctc_decoder.py             # CTC beam search decoding
│   │   └── visualization.py           # Skeleton rendering & timeline
│   │
│   ├── workers/                       # Background job processing
│   │   ├── __init__.py
│   │   ├── task_queue.py              # Job queue (asyncio or RQ)
│   │   └── inference_worker.py        # Async inference executor
│   │
│   ├── utils/                         # Utility functions
│   │   ├── __init__.py
│   │   ├── logger.py                  # Logging setup
│   │   ├── constants.py               # Magic numbers, keypoint ranges, etc.
│   │   ├── validators.py              # Input validation
│   │   ├── converters.py              # NumPy ↔ Torch, etc.
│   │   └── device.py                  # GPU/CPU device management
│   │
│   └── cache/                         # Model caching & memory management
│       ├── __init__.py
│       └── model_cache.py             # Singleton model loader with LRU cache
│
├── frontend/                          # Frontend application (React or Jinja2)
│   │
│   ├── [IF REACT]
│   ├── package.json
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── index.js
│   │   ├── App.jsx                    # Main app component
│   │   ├── components/
│   │   │   ├── Upload.jsx             # Video upload widget
│   │   │   ├── ProgressBar.jsx        # Real-time progress indicator
│   │   │   ├── Results.jsx            # Prediction results display
│   │   │   ├── SkeletonViewer.jsx     # Skeleton visualization
│   │   │   └── Timeline.jsx           # Timeline with gloss sequence
│   │   ├── services/
│   │   │   └── api.js                 # API client (fetch/axios)
│   │   ├── styles/
│   │   │   └── App.css
│   │   └── utils/
│   │       └── helpers.js
│   │
│   ├── [IF JINJA2 + HTMX]
│   ├── templates/
│   │   ├── base.html                  # Base template layout
│   │   ├── index.html                 # Home page
│   │   ├── upload.html                # Upload form
│   │   ├── results.html               # Results display
│   │   └── components/
│   │       ├── progress_bar.html
│   │       ├── skeleton_viewer.html
│   │       └── gloss_timeline.html
│   └── static/
│       ├── css/
│       │   ├── tailwind.css           # Tailwind CSS
│       │   └── custom.css
│       ├── js/
│       │   ├── main.js                # Frontend logic
│       │   ├── api.js                 # API communication
│       │   └── visualization.js       # Skeleton rendering (Canvas/SVG)
│       └── images/
│           └── logo.png
│
├── tests/                             # Unit & integration tests
│   ├── __init__.py
│   ├── conftest.py                    # Pytest fixtures
│   ├── test_skeleton_extractor.py     # Test MediaPipe extraction
│   ├── test_preprocessor.py           # Test normalization pipeline
│   ├── test_inference.py              # Test model inference
│   ├── test_decoder.py                # Test CTC decoding
│   ├── test_api.py                    # Test API endpoints
│   └── fixtures/
│       ├── sample_video.mp4           # Test video
│       └── expected_output.json       # Expected inference result
│
├── scripts/                           # Utility scripts
│   ├── download_model.py              # Script to download baseline_model_bisindo.pt
│   ├── generate_gloss_dict.py         # Generate gloss dictionary (if needed)
│   ├── test_skeleton_extraction.py    # Standalone skeleton extraction test
│   └── benchmark.py                   # Performance benchmarking
│
├── uploads/                           # Temporary uploaded video storage (gitignore)
│   └── .gitkeep
│
├── outputs/                           # Inference outputs (logs, visualizations)
│   ├── .gitkeep
│   ├── logs/
│   │   └── app.log                    # Application logs
│   └── visualizations/
│       └── (frame images, skeletons)
│
├── checkpoints/                       # Optional: model checkpoints for debugging
│   └── .gitkeep
│
├── docs/                              # Documentation
│   ├── API.md                         # API reference
│   ├── INSTALLATION.md                # Setup instructions
│   ├── ARCHITECTURE.md                # Technical architecture overview
│   ├── INFERENCE_PIPELINE.md          # Detailed pipeline documentation
│   └── TROUBLESHOOTING.md             # Common issues & fixes
│
├── requirements.txt                   # Python dependencies (pinned versions)
├── requirements-dev.txt               # Development dependencies
├── Dockerfile                         # Docker image for deployment
├── docker-compose.yml                 # Docker Compose for local dev
│
├── .env.example                       # Environment variables template
├── .github/                           # GitHub workflows (optional CI/CD)
│   └── workflows/
│       ├── tests.yml
│       └── deploy.yml
│
└── LICENSE                            # MIT or appropriate license
```

### Key Directory Purposes

| Directory | Purpose | Storage | Notes |
|-----------|---------|---------|-------|
| `models/` | Model weights | Persistent (git-lfs or download) | Critical; do NOT delete |
| `configs/` | Inference config + gloss dict | Persistent (git) | Load at startup |
| `app/` | FastAPI backend code | Persistent (git) | Core inference logic |
| `frontend/` | UI code | Persistent (git) | React or Jinja2 |
| `uploads/` | Temp video files | Volatile (cleanup after inference) | Gitignored; TTL-based removal |
| `outputs/` | Logs & visualizations | Volatile (optional retention) | Gitignored; cleanup weekly |
| `tests/` | Unit & integration tests | Persistent (git) | Pytest framework |
| `scripts/` | Utility scripts | Persistent (git) | For development/deployment |

---

## 6. Code Migration Plan

### 6.1 Files to Copy (With Minimal Modification)

| Source Repo | Source File | Target Location | Action | Notes |
|-------------|-------------|-----------------|--------|-------|
| `rgb-to-skeleton-mediapipe` | `src/extractor/holistic_86.py` | `app/services/skeleton_extractor.py` | **EXTRACT AS-IS** | Remove file I/O; keep extraction logic |
| `rgb-to-skeleton-mediapipe` | `src/config/` | `app/utils/constants.py` | **MIGRATE** | Copy keypoint ranges, MediaPipe settings |
| `rgb-to-skeleton-mediapipe` | `src/processor/video.py` | `app/services/video_processor.py` | **EXTRACT** | Frame extraction & rotation handling |
| `MSLR_ICCV2025` | `slr_network.py` | `app/services/model.py` | **COPY** | Model definition; remove training logic |
| `MSLR_ICCV2025` | `modules/visual_extractor.py` | `app/services/visual_extractor.py` | **COPY** | Feature extraction; inference-only |
| `MSLR_ICCV2025` | `modules/temporal_layers/` | `app/services/temporal_layers/` | **COPY** | BiLSTM, temporal conv layers |
| `MSLR_ICCV2025` | `modules/stgcn_layers/` | `app/services/stgcn_layers/` | **COPY** | Graph convolution layers |
| `MSLR_ICCV2025` | `utils/decode.py` | `app/services/ctc_decoder.py` | **WRAP** | CTC decoding; adapt for single-video |
| `MSLR_ICCV2025` | `configs/Double_Cosign_sd.yaml` | `configs/inference.yaml` | **EXTRACT** | Model architecture hyperparameters |

### 6.2 Files to Rewrite (Simplified Versions)

| Source Repo | Source File | Target Location | Reason | Details |
|-------------|-------------|-----------------|--------|---------|
| `MSLR_ICCV2025` | `datasets/skeleton_feeder.py` | `app/services/skeleton_preprocessor.py` | **Simplify for inference** | Remove augmentation, batching, LMDB; keep only normalization |
| `MSLR_ICCV2025` | `main.py` | N/A | **Complete rewrite** | Replace with FastAPI app; no training logic |
| `rgb-to-skeleton-mediapipe` | `src/core/pipeline.py` | `app/services/inference_engine.py` | **Inference-only wrapper** | Remove file I/O, split mapping; keep orchestration |

### 6.3 Files to Remove Entirely

| Source Repo | Files | Reason |
|-------------|-------|--------|
| `MSLR_ICCV2025` | `seq_scripts.py` | Training-only |
| `MSLR_ICCV2025` | `main.py` | Training harness |
| `MSLR_ICCV2025` | `evaluation/` | Batch evaluation (not needed for single inference) |
| `MSLR_ICCV2025` | `preprocess/` | Training data preprocessing (not needed) |
| `MSLR_ICCV2025` | `configs/` (except architecture) | Hyperparameters tuned for training |
| `rgb-to-skeleton-mediapipe` | `notebooks/` | Exploratory analysis (not needed) |
| `rgb-to-skeleton-mediapipe` | `splitting_data/` | Dataset splitting (training-only) |
| `rgb-to-skeleton-mediapipe` | `data/` | Raw training data |
| Both | All distributed training code | Not needed for single-inference demo |

### 6.4 Dependency Consolidation

**Critical Dependencies (Must Keep):**
```
mediapipe==0.10.14      # Skeleton extraction (strictly pinned)
opencv-python>=4.8.0    # Video frame reading
numpy>=1.24.0,<2.0.0    # Numerical computing
torch>=2.0.0            # Model inference
fastapi>=0.95.0         # Web framework
uvicorn>=0.22.0         # ASGI server
ctcdecode               # CTC beam decoder (from repo)
Pillow>=9.5.0           # Image manipulation
```

**Optional Dependencies:**
```
python-multipart        # File upload handling
aiofiles                # Async file I/O
pydantic>=2.0           # Request/response validation
pydantic-settings       # Config management
python-dotenv           # Environment variables
```

**Remove Entirely:**
```
pandas                  # Excel export (not needed)
openpyxl                # Excel export (not needed)
torch.distributed       # Distributed training
wandb                   # Experiment tracking
torchvision             # Auxiliary vision tasks
scipy (optional)        # Some preprocessing uses scipy
```

### 6.5 Module Integration Map

```
┌──────────────────────────────────────────────────┐
│  rgb-to-skeleton-mediapipe IMPORTS               │
│  ↓                                               │
│  app/services/skeleton_extractor.py              │
│    ├── holistic_86.py (extracted)                │
│    ├── constants.py (keypoint ranges, etc.)      │
│    └── video_processor.py (frame extraction)     │
│                                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  MSLR_ICCV2025 IMPORTS                           │
│  ↓                                               │
│  app/services/                                   │
│    ├── model.py (slr_network.py)                │
│    ├── visual_extractor.py                      │
│    ├── stgcn_layers/                            │
│    ├── temporal_layers/                         │
│    └── ctc_decoder.py (utils/decode.py)         │
│                                                  │
│  app/services/                                   │
│    └── skeleton_preprocessor.py (skeleton_feeder) │
│                                                  │
└──────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  NEW MODULES (FastAPI Wrapper)                   │
│  ↓                                               │
│  app/                                            │
│    ├── main.py (FastAPI app)                    │
│    ├── api/routes.py (endpoints)                │
│    ├── services/inference_engine.py (orchestrator) │
│    └── cache/model_cache.py (singleton loader)  │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 7. Model Integration Plan

### 7.1 Model File Details

**Trained Model:**
- **Path:** `models/baseline_model_bisindo.pt`
- **Type:** PyTorch state_dict
- **Size:** ~100–300 MB (typical for ST-GCN + BiLSTM)
- **Architecture:** `TwoStream_Cosign` (Dual-stream: static + motion)
- **Input:** Normalized skeleton sequences
- **Output:** Logits for CTC decoding

### 7.2 Model Loading Strategy

**Lazy Loading with Caching:**
```python
class ModelCache:
    def __init__(self, model_path, config_path, device='cuda'):
        self.model_path = model_path
        self.config = load_yaml(config_path)
        self.device = device
        self._model = None
    
    def get_model(self):
        if self._model is None:
            # Load only on first call
            self._model = load_model(self.model_path, self.config, self.device)
        return self._model
    
    # Singleton instance
    _instance = None
    
    @staticmethod
    def instance():
        if ModelCache._instance is None:
            ModelCache._instance = ModelCache(...)
        return ModelCache._instance
```

**Rationale:**
- Model loaded once at startup or first inference request
- Cached in GPU memory (if available)
- Reduces latency on subsequent requests
- Graceful fallback to CPU if GPU OOM

### 7.3 Expected Input Tensor Format

**For Single Video Inference:**

```python
inputs_dict = {
    'x': torch.tensor(
        skeleton_array,  # shape: (1, T, C)
        dtype=torch.float32,
        device=device
    ),
    'len_x': torch.tensor([seq_len], dtype=torch.long, device=device)
}
```

**Detailed Shape Breakdown:**

| Parameter | Shape | Description |
|-----------|-------|-------------|
| `x` | (1, T, 172) | Batch size 1; T temporal frames; 172 = 86 keypoints × 2 coords |
| `len_x` | (1,) | Actual sequence length (≤ T) |
| T | ~250 | Padded temporal length (fixed) |
| 86 | keypoints | Left(21) + Right(21) + Mouth(19) + Pose(25) |
| 2 | coords | [x, y] normalized coordinates |

**Variable Length Handling:**
- Input can be variable T, but typically padded to fixed length
- `len_x` tells model true sequence length (for CTC loss masking)
- Model handles padding; don't include padding in CTC loss

### 7.4 Model Inference Mode

**Critical: Inference-Only Configuration**
```python
model.eval()  # Disable dropout, batch norm training

with torch.no_grad():  # Disable gradient computation
    output_dict = model(inputs_dict)
```

**Output Structure:**
```python
output_dict = {
    'recognized_sents_fusion': [  # Best predictions (contextual BiLSTM)
        [('এক', 0), ('দুই', 1), ...],  # (gloss, position) tuples
    ],
    'conv_sents_fusion': [...],  # Conv-only predictions (fallback)
}
```

**Interpreting Outputs:**
- Model returns **gloss predictions, NOT raw logits**
- Decoding happens inside model.forward()
- Can also extract intermediate logits for confidence scores

### 7.5 Device Handling (GPU/CPU)

**Automatic Device Selection:**
```python
def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda:0')
    else:
        return torch.device('cpu')

# Load model to device
model = model.to(device)

# Ensure inputs on same device
inputs_dict['x'] = inputs_dict['x'].to(device)
inputs_dict['len_x'] = inputs_dict['len_x'].to(device)
```

**Memory Management:**
- For CPU: ~2–4 GB RAM required
- For GPU: ~4–8 GB VRAM required (RTX 3090 easily handles)
- Clear GPU cache after inference if needed

### 7.6 Decoding Strategy

**CTC Beam Search Configuration:**
```python
decoder = Decode(
    gloss_dict=load_gloss_dict(),
    num_classes=len(gloss_dict) + 1,  # +1 for blank
    search_mode='beam',  # 'beam' or 'max'
    blank_id=0
)

# Model outputs logits → decoder produces glosses
logits = model_output  # (T, B, num_classes)
predicted_glosses = decoder.decode(
    logits,
    vid_lgt=seq_len,
    batch_first=False,  # T×B×C format
    probs=False  # Raw logits, not probabilities
)
```

**Output:**
- **Format:** List of (gloss_string, frame_index) tuples
- **Confidence:** Beam score (log probability of path)
- **Post-processing:**
  - Remove consecutive duplicates (CTC merging)
  - Filter blank tokens automatically
  - Join glosses → final sentence

---

## 8. Skeleton Extraction Plan

### 8.1 MediaPipe Holistic Components

**What is MediaPipe Holistic?**
- Single unified API for pose, hand, and face detection
- Efficient lightweight model suitable for real-time inference
- Outputs **landmarks** (normalized 2D or 3D coordinates)

**Selected Components:**
```
┌─ Left Hand  (21 points) ─────────────┐
│  0: wrist, 1: thumb_cmc, 2: ..., 20: pinky_tip
│  Range: [0, 21)
│
├─ Right Hand (21 points) ────────────┤
│  0: wrist, 1: thumb_cmc, 2: ..., 20: pinky_tip
│  Range: [0, 21)
│
├─ Mouth (19 points) ─────────────────┤
│  Custom selection from 468-point face mesh:
│  Outer lip (10) + Inner lip (9)
│  Range: specific indices (non-contiguous)
│
└─ Pose (25 points) ──────────────────┘
   0: nose, 1-4: eyes/ears, 5-22: body/limbs
   Range: [0, 25)
```

### 8.2 Keypoint Selection & Indexing

**Critical: Isharah 86-Keypoint Format**

```
BISINDO 86-Keypoint Layout:

Index Range | Component | Count | Source | Details
────────────┼───────────┼───────┼────────┼─────────────────
0–20        | Left Hand | 21    | MP     | Sequential indices
21–41       | Right Hand| 21    | MP     | Sequential indices
42–60       | Mouth     | 19    | MP     | Selected lip indices
61–85       | Pose      | 25    | MP     | Sequential indices
────────────┼───────────┴───────┴────────┴─────────────────
Total       | Skeleton  | 86    |        | Fixed layout
```

**Implementation:**
```python
# From src/extractor/holistic_86.py
keypoints = []

# Left hand: sequential 0–20
keypoints.extend(extract_landmarks(hand_landmarks_left, range(21)))

# Right hand: sequential 0–20
keypoints.extend(extract_landmarks(hand_landmarks_right, range(21)))

# Mouth: custom lip indices
keypoints.extend(extract_landmarks(face_landmarks, MOUTH_INDICES))

# Pose: sequential 0–24
keypoints.extend(extract_landmarks(pose_landmarks, range(25)))

# Result: (86, 3) array [x, y, z] or (86, 2) array [x, y]
```

### 8.3 Frame Processing Strategy

**Per-Frame Extraction:**

```
FOR EACH video frame (BGR):
  1. Convert BGR → RGB
  2. Run MediaPipe Holistic inference
  3. Extract hand + face + pose landmarks
  4. Arrange in 86-point order
  5. Normalize [pixel_coords] → [0, 1] range
  6. Handle missing landmarks (confidence < threshold)
  7. Return (86, 3) array

Aggregate across T frames → (T, 86, 3) array
```

**Coordinate Normalization:**
- MediaPipe outputs normalized [0, 1] coordinates by default
- x, y ∈ [0, 1] (relative to frame width/height)
- z ∈ [0, 1] (depth; can be unreliable; optional to drop)

### 8.4 Handling Missing Keypoints

**Detection Confidence:**
- Each MediaPipe landmark includes **confidence score** [0, 1]
- Typical threshold: > 0.5

**Missing Keypoint Handling Strategy:**
```python
if confidence < CONFIDENCE_THRESHOLD:
    # Option 1: Zero out
    keypoint = [0.0, 0.0, 0.0]
    
    # Option 2: Interpolate from neighbors
    keypoint = interpolate_from_neighbors(T, frame_idx, keypoint_idx)
```

**Frame-Level Robustness:**
- If > 50% keypoints missing in a frame:
  - Use temporal interpolation from adjacent frames
  - Or: mark frame as unreliable and pad later

### 8.5 Temporal Normalization

**What is Temporal Normalization?**
- Smoothing jitter across frames
- Filtering high-frequency noise
- Preserving intentional motion

**Implementation:**
```python
# Light Gaussian smoothing (±3 frame window)
skeleton_smoothed = gaussian_filter1d(skeleton, sigma=1.0, axis=0)

# Or: Kalman filter for motion tracking
# Or: Skip if not needed (model may handle jitter)
```

**When to Apply:**
- Optional; depends on video quality
- MediaPipe already provides some smoothing
- Full pipeline may be: extract → smooth → normalize → preprocess

### 8.6 Output Skeleton Format

**Final Output from Extraction Stage:**

```python
skeleton = np.ndarray(
    shape=(T, 86, D),  # T frames, 86 keypoints, D dims
    dtype=np.float32
)

# Where:
# T = variable (1–600 frames typical; ~25 fps × 5–25 sec video)
# 86 = fixed keypoint count (isharah format)
# D = 2 (x, y normalized) or 3 (x, y, z with depth)

# All values: normalized [0, 1] or centered around origin after preprocessing
```

**Example Shape:**
- 5-second video @ 25 fps = 125 frames
- Output: (125, 86, 2) — ready for preprocessing

---

## 9. Frontend/UI Plan

### 9.1 Page Layouts & User Flow

**Page 1: Home / Upload Page**
```
┌────────────────────────────────────┐
│   BISINDO CSLR Demo                │
│   Continuous Sign Language         │
│   Recognition System               │
│                                    │
│  [Upload Video] [Drag & Drop Box]  │
│                                    │
│  Supported: MP4, AVI, MOV (≤500MB) │
│                                    │
│  [Start Demo] [View Samples]       │
└────────────────────────────────────┘
```

**Key Elements:**
- Logo + branding
- Clear upload interface
- File type & size restrictions
- Help text with examples
- Link to documentation

**Page 2: Processing / Progress Page**
```
┌────────────────────────────────────┐
│   Processing Your Video...         │
│                                    │
│  ⏳ Frame Extraction: ████░░░░░░   │
│  ⏳ Skeleton Detection: ░░░░░░░░░░  │
│  ⏳ Preprocessing: ░░░░░░░░░░░░░░░░ │
│  ⏳ Model Inference: ░░░░░░░░░░░░░░ │
│  ⏳ Decoding: ░░░░░░░░░░░░░░░░░░░░  │
│                                    │
│  Elapsed: 3.2 / ~10 seconds        │
│                                    │
│  [Cancel]                          │
└────────────────────────────────────┘
```

**Key Elements:**
- Multi-stage progress bars
- Real-time status updates (WebSocket/SSE)
- Estimated time remaining
- Cancel button
- Video preview (optional)

**Page 3: Results / Dashboard Page**
```
┌────────────────────────────────────┐
│   Recognition Results              │
│                                    │
│  Predicted Sentence (আরবি):        │
│  ╔════════════════════════════════╗│
│  ║ এক দুই তিন চার পাঁচ             ║│
│  ╚════════════════════════════════╝│
│                                    │
│  ┌─ Gloss Timeline ────────────────┐
│  │ এক      [0:00 – 0:30]  [95%]  │
│  │ দুই     [0:30 – 1:00]  [87%]  │
│  │ তিন     [1:00 – 1:35]  [92%]  │
│  └─────────────────────────────────┘
│                                    │
│  [Video Frame at Best Match]       │
│  ┌──────────────┐                  │
│  │ Skeleton viz │                  │
│  │ (plot)       │                  │
│  └──────────────┘                  │
│                                    │
│  [Download Results] [Test Another] │
└────────────────────────────────────┘
```

**Key Elements:**
- Predicted glosses (sentence view)
- Per-gloss timeline with confidence
- Frame-by-frame skeleton visualization
- Download option (JSON, CSV)
- Navigation to upload another video

### 9.2 UI Component Design

**1. Upload Widget**
- Drag-and-drop box
- File selector button
- Progress bar during upload
- File name & size display
- Validation error messages

**2. Progress Bar**
- Multi-stage indicators:
  - Frame extraction (10%)
  - Skeleton detection (30%)
  - Preprocessing (20%)
  - Model inference (30%)
  - Decoding (10%)
- Real-time updates via WebSocket
- Estimated time (exponential moving average)

**3. Skeleton Viewer**
- 2D skeleton rendering (Canvas or SVG)
- Keypoint connections (pose graph)
- Color coding by body part
- Frame slider (timeline)
- Play/pause animation

**4. Gloss Timeline**
- Horizontal timeline
- Gloss boxes positioned by frame range
- Confidence color gradient (red=low, green=high)
- Hover shows frame number & exact timing

**5. Results Panel**
- Predicted sentence (large, clear typography)
- Per-gloss breakdown:
  - Gloss word
  - Frame range
  - Confidence score (%)
  - Recheck / flag option (optional)

### 9.3 Responsive Design

**Mobile (≤768px):**
- Stack layouts vertically
- Touch-friendly buttons (min 44px)
- Simplified skeleton viewer (small canvas)
- Collapsible sections for timeline
- Full-width input fields

**Tablet (769–1024px):**
- Two-column layout (upload left, results right)
- Medium skeleton viewer
- Readable gloss timeline

**Desktop (>1024px):**
- Three-column layout optional
- Large skeleton visualization
- Detailed timeline with tooltip
- Side-by-side comparison (before/after)

### 9.4 Design System (Tailwind CSS)

**Color Palette:**
```
Primary:    #2563EB (Blue)      — buttons, links
Success:    #10B981 (Green)     — confident predictions
Warning:    #F59E0B (Orange)    — medium confidence
Error:      #EF4444 (Red)       — low confidence, errors
Background: #F9FAFB (Light Gray) — page background
Text:       #111827 (Dark Gray) — main text
```

**Typography:**
- Headings: Inter Bold, 28–48px
- Body: Inter Regular, 14–16px
- Monospace: Fira Code, 12px (for gloss code/debug)

**Spacing:**
- Base unit: 8px
- Padding: 8, 16, 24, 32px
- Margin: 16, 24, 32px
- Gap: 8, 12, 16px

**Component Examples:**
```html
<!-- Button -->
<button class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
  Upload Video
</button>

<!-- Progress -->
<div class="w-full bg-gray-200 rounded-full h-2">
  <div class="bg-blue-600 h-2 rounded-full" style="width: 65%"></div>
</div>

<!-- Card -->
<div class="bg-white rounded-lg shadow-md p-6">
  <h3 class="text-lg font-semibold mb-4">Results</h3>
  <!-- Content -->
</div>
```

---

## 10. FastAPI API Design

### 10.1 API Endpoints Overview

| Method | Endpoint | Purpose | Request | Response |
|--------|----------|---------|---------|----------|
| POST | `/upload` | Upload RGB video | multipart/form-data | {video_id, status} |
| POST | `/predict` | Run inference | {video_id} | {glosses, confidence, ...} |
| GET | `/status/{video_id}` | Check job status | URL param | {status, progress} |
| GET | `/results/{video_id}` | Retrieve results | URL param | {glosses, timeline, skeleton_frames} |
| GET | `/visualize/{video_id}` | Get skeleton frames | URL param | {frames_base64} |
| GET | `/health` | Health check | — | {status: 'ok'} |
| DELETE | `/cleanup/{video_id}` | Delete uploaded file | URL param | {status} |

### 10.2 Detailed Endpoint Specifications

#### 10.2.1 POST `/upload`

**Purpose:** Upload video file and create inference job

**Request:**
```http
POST /upload HTTP/1.1
Content-Type: multipart/form-data

[Binary video file in 'file' field]
```

**Request Schema:**
```python
from fastapi import UploadFile, File

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """
    Args:
        file: Video file (MP4, AVI, MOV, WebM)
        
    Validation:
        - Max size: 500 MB
        - Allowed extensions: {.mp4, .avi, .mov, .webm}
    """
    pass
```

**Response (200 OK):**
```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Video uploaded successfully",
  "file_size": 15728640,
  "duration": 5.5,
  "next_step": "/predict"
}
```

**Response (400 Bad Request):**
```json
{
  "status": "error",
  "code": "INVALID_FILE",
  "message": "File size exceeds 500MB limit",
  "allowed_formats": [".mp4", ".avi", ".mov", ".webm"],
  "max_size_mb": 500
}
```

#### 10.2.2 POST `/predict`

**Purpose:** Run inference on uploaded video

**Request:**
```http
POST /predict HTTP/1.1
Content-Type: application/json

{
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "extract_skeleton": true,
  "return_visualizations": true,
  "confidence_threshold": 0.5
}
```

**Request Schema:**
```python
from pydantic import BaseModel

class PredictRequest(BaseModel):
    video_id: str
    extract_skeleton: bool = True
    return_visualizations: bool = True
    confidence_threshold: float = 0.5
    return_intermediate: bool = False  # Return logits, etc.
```

**Response (202 Accepted - Async Job):**
```json
{
  "status": "accepted",
  "job_id": "job_550e8400-e29b-41d4-a716-446655440001",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Inference job queued",
  "check_status_url": "/status/job_550e8400-e29b-41d4-a716-446655440001",
  "estimate_seconds": 15
}
```

**Response (200 OK - Synchronous, Fast):**
```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "glosses": [
    {"word": "এক", "confidence": 0.95, "start_frame": 0, "end_frame": 25},
    {"word": "দুই", "confidence": 0.87, "start_frame": 25, "end_frame": 50}
  ],
  "full_sentence": "এক দুই তিন চার পাঁচ",
  "sentence_confidence": 0.89,
  "processing_time": 3.2,
  "frame_count": 125,
  "fps": 25
}
```

#### 10.2.3 GET `/status/{job_id}`

**Purpose:** Check inference job progress

**Response:**
```json
{
  "job_id": "job_550e8400-e29b-41d4-a716-446655440001",
  "status": "in_progress",
  "progress": {
    "stage": "model_inference",
    "percent": 65,
    "stages": {
      "frame_extraction": {"percent": 100, "status": "completed"},
      "skeleton_extraction": {"percent": 100, "status": "completed"},
      "preprocessing": {"percent": 100, "status": "completed"},
      "model_inference": {"percent": 65, "status": "in_progress"},
      "decoding": {"percent": 0, "status": "pending"}
    }
  },
  "elapsed": 5.3,
  "estimate_remaining": 3.2
}
```

#### 10.2.4 GET `/results/{video_id}`

**Purpose:** Retrieve inference results

**Response:**
```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": {
    "glosses": [
      {
        "id": 0,
        "word": "এক",
        "confidence": 0.95,
        "start_frame": 0,
        "end_frame": 25,
        "start_time": "0:00.000",
        "end_time": "0:01.000"
      }
    ],
    "full_sentence": "এক দুই তিন চার পাঁচ",
    "sentence_confidence": 0.89,
    "total_frames": 125,
    "fps": 25,
    "duration": 5.0
  },
  "visualizations": {
    "skeleton_frames": [
      {
        "frame_idx": 0,
        "timestamp": 0.0,
        "image_base64": "data:image/png;base64,...",
        "predicted_gloss": "এক"
      }
    ]
  },
  "metadata": {
    "model_version": "baseline_bisindo_v1",
    "inference_device": "cuda:0",
    "processing_time_seconds": 3.2,
    "timestamp": "2026-05-10T12:34:56Z"
  }
}
```

#### 10.2.5 GET `/health`

**Purpose:** Liveness check

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "model_loaded": true,
  "gpu_available": true,
  "timestamp": "2026-05-10T12:34:56Z"
}
```

### 10.3 Async Considerations

**Sync vs. Async Execution:**

```python
# Sync: < 3 sec (simple case)
@app.post("/predict")
async def predict(req: PredictRequest):
    result = run_inference_synchronously(req.video_id)
    return result  # 200 OK immediate

# Async: > 3 sec (background job)
@app.post("/predict")
async def predict(req: PredictRequest):
    job_id = queue_inference_job(req.video_id)
    return {
        "status": "accepted",
        "job_id": job_id,
        "check_status_url": f"/status/{job_id}"
    }  # 202 Accepted

# Check status periodically
@app.get("/status/{job_id}")
async def check_status(job_id: str):
    job = get_job(job_id)
    if job.done():
        return {"status": "completed", "result": job.result}
    else:
        return {"status": "in_progress", "progress": job.progress()}
```

**WebSocket for Real-time Updates (Optional):**
```python
@app.websocket("/ws/progress/{video_id}")
async def websocket_progress(websocket: WebSocket, video_id: str):
    await websocket.accept()
    
    while not inference_complete(video_id):
        progress = get_progress(video_id)
        await websocket.send_json(progress)
        await asyncio.sleep(1)  # Update every 1 sec
    
    result = get_results(video_id)
    await websocket.send_json({"status": "completed", "result": result})
    await websocket.close()
```

### 10.4 Error Handling

**Standard Error Response:**
```json
{
  "status": "error",
  "code": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {
    "step": "skeleton_extraction",
    "reason": "MediaPipe detected < 50% keypoints in frame 42"
  }
}
```

**Common Error Codes:**
| Code | HTTP | Description | Action |
|------|------|-------------|--------|
| `INVALID_FILE` | 400 | Bad format/size | Re-upload |
| `VIDEO_NOT_FOUND` | 404 | Video ID invalid | Check ID |
| `EXTRACTION_FAILED` | 422 | Skeleton extraction error | Re-upload |
| `MODEL_ERROR` | 500 | Model inference error | Retry |
| `TIMEOUT` | 504 | Processing took > 60sec | Retry / use smaller video |
| `GPU_OOM` | 503 | GPU out of memory | Retry / use CPU |

### 10.5 Request/Response Examples

**Example: Full Workflow**

```bash
# 1. Upload
curl -X POST \
  -F "file=@video.mp4" \
  http://localhost:8000/upload

# Response
{
  "video_id": "abc123",
  "status": "success"
}

# 2. Predict (async)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"video_id": "abc123"}' \
  http://localhost:8000/predict

# Response (202 Accepted)
{
  "job_id": "job_xyz789",
  "status": "accepted"
}

# 3. Check Status (polling)
curl http://localhost:8000/status/job_xyz789

# 4. Get Results
curl http://localhost:8000/results/abc123

# 5. Cleanup
curl -X DELETE http://localhost:8000/cleanup/abc123
```

---

## 11. Dependency Plan

### 11.1 Core Dependencies (Required)

```
# Critical — Must have exact versions or close to it
mediapipe==0.10.14        # MediaPipe Holistic (legacy API)
torch>=2.0.0              # PyTorch model inference
fastapi>=0.95.0           # Web framework
uvicorn[standard]>=0.22.0 # ASGI server

# Essential numeric/data handling
numpy>=1.24.0,<2.0.0      # NumPy (NOT 2.0+; breaks PyTorch)
opencv-python>=4.8.0      # OpenCV for video I/O

# CTC decoding (included in repo)
ctcdecode                  # From MSLR_ICCV2025/ctcdecode

# File upload
python-multipart>=0.0.5    # FastAPI multipart form parsing
```

### 11.2 Optional Dependencies

```
# Frontend & async improvements
aiofiles>=23.0.0          # Async file I/O (optional)
pydantic>=2.0             # Request/response validation (built into FastAPI)
pydantic-settings>=2.0    # Config management

# Utilities
python-dotenv>=0.21.0     # Environment variables
Pillow>=9.5.0             # Image manipulation (skeleton rendering)
tqdm>=4.65.0              # Progress bars (CLI utilities)

# Development/testing
pytest>=7.0               # Testing framework
pytest-asyncio>=0.21.0    # Async test support
httpx>=0.23.0             # HTTP client for tests
black>=23.0               # Code formatter
flake8>=6.0               # Linter
mypy>=1.0                 # Type checker
```

### 11.3 Removed Dependencies (Training-Only)

| Dependency | Reason | Alternative |
|------------|--------|-------------|
| `torch.distributed` | Distributed training | N/A (single inference) |
| `wandb` | Experiment tracking | Logging via Python logging |
| `tensorboard` | Visualization | Inference only; no training |
| `pytorch-lightning` | Training framework | FastAPI replaces it |
| `pandas` | Excel export | JSON output instead |
| `openpyxl` | Excel creation | JSON output instead |
| `scipy` | Scientific computing | NumPy/PyTorch (optional) |
| `torchvision` | Vision models | Not needed for inference |
| `albumentations` | Data augmentation | Inference only; no augmentation |

### 11.4 Version Pinning Strategy

**Strict Pinning (No flexibility):**
```
mediapipe==0.10.14  # ONLY this version; 0.10.18+ breaks
numpy>=1.24.0,<2.0.0  # Must NOT upgrade to 2.0+
```

**Reasonable Range (May update):**
```
torch>=2.0.0        # 2.0+, 2.1, 2.2 all okay
fastapi>=0.95.0     # Any recent version
```

**Optional (Flexible):**
```
Pillow>=9.5.0       # Any recent version; not critical
tqdm>=4.65.0        # Non-critical utility
```

### 11.5 Environment Setup

**Python Version:**
- Minimum: Python 3.8
- Recommended: Python 3.10+
- Tested: Python 3.10, 3.11

**Installation:**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

**requirements.txt:**
```
# Core (Inference)
mediapipe==0.10.14
torch>=2.0.0
fastapi>=0.95.0
uvicorn[standard]>=0.22.0
numpy>=1.24.0,<2.0.0
opencv-python>=4.8.0
python-multipart>=0.0.5

# Optional (Recommended)
aiofiles>=23.0.0
Pillow>=9.5.0
python-dotenv>=0.21.0
```

**requirements-dev.txt:**
```
-r requirements.txt

# Testing
pytest>=7.0
pytest-asyncio>=0.21.0
httpx>=0.23.0

# Code quality
black>=23.0
flake8>=6.0
mypy>=1.0
```

---

## 12. Deployment Plan

### 12.1 Local Development Deployment

**Setup Steps:**

```bash
# 1. Clone repository
git clone https://github.com/user/bisindo-cslr-demo.git
cd bisindo-cslr-demo

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download model weights
python scripts/download_model.py

# 5. Start development server
python app/server.py --dev
```

**Development Server:**
```python
# app/server.py
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Auto-reload on code change
        log_level="info"
    )
```

**Access UI:**
- Frontend: http://localhost:3000 (React dev server)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs (Swagger UI)

### 12.2 Production Deployment

#### 12.2.1 Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libopencv-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app/
COPY models/ ./models/
COPY configs/ ./configs/

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  backend:
    build: .
    container_name: bisindo-cslr-backend
    ports:
      - "8000:8000"
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
    environment:
      - DEVICE=cuda  # or 'cpu'
      - MAX_VIDEO_SIZE=500
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: bisindo-cslr-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped
```

**Build & Run:**
```bash
docker-compose up -d
```

#### 12.2.2 Cloud Deployment (Heroku)

**Procfile:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Deploy:**
```bash
heroku login
heroku create bisindo-cslr-demo
git push heroku main
heroku logs --tail
```

#### 12.2.3 AWS/Google Cloud Deployment

**AWS:**
- **Compute:** EC2 (GPU instance: g4dn.xlarge)
- **Storage:** S3 for uploaded videos + results
- **Serving:** ALB + Auto-scaling group
- **Model:** Store in S3, load at startup

**Google Cloud:**
- **Compute:** Cloud Run (serverless; limited GPU support)
- **Alternative:** Compute Engine (managed VMs)
- **Storage:** Cloud Storage

### 12.3 CPU-Only Support

**Rationale:** Not all users have GPU; fallback to CPU with acceptable latency

**Strategy:**
```python
# Automatic device selection
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# CPU inference typically:
# - Model load: ~5 sec
# - Single inference: ~15–30 sec
# - Total: ~20–40 sec (acceptable for web demo)
```

**Optimization for CPU:**
- Reduce batch size to 1 (already done)
- Use lighter model version (optional; may reduce accuracy)
- Increase timeout to 60 sec
- Queue jobs if CPU-only to avoid blocking

### 12.4 GPU Support

**Supported GPU:**
- NVIDIA GPUs (CUDA 11.8+)
- RTX 3090, RTX 4090, A100, V100, etc.

**GPU Memory:**
- Model + inference: ~4–8 GB VRAM
- Batch size 1: minimal overhead
- Multiple concurrent requests: queue them

**GPU Setup:**
```bash
# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA toolkit
# (Usually pre-installed in Docker/cloud environments)
```

**Performance (Rough Benchmarks):**
| Device | Model Load | Single Inference | Total |
|--------|-----------|-----------------|-------|
| CPU (Intel i7) | 5 sec | 20 sec | ~25 sec |
| CPU (AMD Ryzen) | 5 sec | 15 sec | ~20 sec |
| GPU (RTX 3090) | 2 sec | 2 sec | ~4 sec |
| GPU (RTX 4090) | 1 sec | 1 sec | ~2 sec |

### 12.5 Configuration for Production

**Environment Variables (.env):**
```
# Server
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Model & Inference
DEVICE=cuda  # or 'cpu'
BATCH_SIZE=1
INFERENCE_TIMEOUT=60
MAX_VIDEO_SIZE_MB=500

# Upload storage
UPLOAD_DIR=./uploads
CLEANUP_TTL_HOURS=1  # Delete temp files after 1 hour

# API
API_WORKERS=4
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Monitoring (optional)
ENABLE_METRICS=true
LOG_FILE=./logs/app.log
```

**Load production config:**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = False
    device: str = "cuda"
    max_video_size_mb: int = 500
    inference_timeout: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 13. Performance & Risk Analysis

### 13.1 Performance Bottlenecks

**1. MediaPipe Skeleton Extraction**
- **Bottleneck:** Real-time per-frame processing
- **Typical Latency:** ~30 ms/frame @ 25 fps
  - For 125 frames (5 sec video) ≈ 4 seconds total
- **Optimization:**
  - Batch processing (extract every N frames, interpolate)
  - GPU acceleration (MediaPipe v0.9+ supports GPU)
  - Parallel frame processing (multiple threads)

**2. Model Inference**
- **Bottleneck:** Forward pass through ST-GCN + BiLSTM
- **Typical Latency:**
  - GPU (RTX 3090): ~2 seconds
  - CPU: ~15–20 seconds
- **Optimization:**
  - Quantization (INT8) — reduces accuracy slightly
  - Model distillation (smaller model) — if needed
  - Batch inference (queue multiple requests)

**3. CTC Decoding**
- **Bottleneck:** Beam search (beam width=10)
- **Typical Latency:** ~100–500 ms
- **Optimization:**
  - Reduce beam width to 5 (slightly less accurate)
  - Implement local pruning
  - Cache decoder state if streaming

**4. Video I/O**
- **Bottleneck:** Reading & decoding video frames
- **Typical Latency:** ~1–2 seconds (depends on codec)
- **Optimization:**
  - Use hardware-accelerated codecs (H.264, H.265)
  - Stream frames from upload directly (no disk write)

### 13.2 Memory Usage

| Component | Typical Usage | Notes |
|-----------|---------------|-------|
| Model weights | 200–400 MB | Loaded once; cached in VRAM/RAM |
| Skeleton frames (T=250) | 500 KB | Small; keep in memory |
| Intermediate tensors | 100–200 MB | Temporary; released after inference |
| WebSocket connections | 1 MB/connection | Scale with concurrent users |
| **Total (single request)** | **~500 MB** | Peak during inference |

**Memory Scaling:**
- **Single user:** 500 MB
- **10 concurrent users:** 5 GB (assuming queue)
- **100 concurrent users:** Can queue; serve ~10 simultaneously

### 13.3 Network Bandwidth

**Typical Request:**
- Video upload: 10–100 MB (depends on duration/codec)
- API response: 1–10 MB (JSON + skeleton images in base64)
- **Total:** 11–110 MB per request

**Optimization:**
- Compress video before upload (client-side)
- Stream response (Server-Sent Events for progress)
- Compress JSON (gzip middleware)

### 13.4 Risk Analysis

#### Risk 1: MediaPipe Detection Failures
**Scenario:** Video has poor lighting, signer partially outside frame, fast motion
- **Impact:** Skeleton extracted with missing/unreliable keypoints
- **Mitigation:**
  - Implement confidence thresholding
  - Temporal interpolation for missing frames
  - User warning: "Poor skeleton detection quality; prediction may be inaccurate"
- **Fallback:** Return partial result with low confidence

#### Risk 2: Model Inference Out-of-Memory (OOM)
**Scenario:** Long video (>5 min) or GPU memory exhausted
- **Impact:** Inference crashes; 500 error
- **Mitigation:**
  - Implement video segmentation (split into 5-sec chunks, infer separately)
  - Graceful fallback to CPU
  - Clear error: "Video too long; please upload ≤5 minute clip"
- **Timeout:** 60 seconds max; return partial results

#### Risk 3: CTC Decoder Produces Empty Output
**Scenario:** Model predicts only blanks (no valid glosses)
- **Impact:** Empty result; confusing to user
- **Mitigation:**
  - Return model confidence scores (check if all < threshold)
  - Suggest: "No clear glosses detected; try better lighting/angle"
  - Fallback: Return top-K candidates even if low confidence

#### Risk 4: Model Accuracy Degradation on Out-of-Distribution Videos
**Scenario:** Video style different from training data (e.g., different signer, background, lighting)
- **Impact:** Poor predictions; user dissatisfaction
- **Mitigation:**
  - **Disclaimer:** "Model trained on BISINDO; may not work well on other sign languages"
  - Confidence scores indicate reliability
  - Option to report bad predictions (feedback loop for retraining)
- **Note:** No real-time mitigation; requires retraining

#### Risk 5: High Latency on CPU-Only Machines
**Scenario:** User runs locally on laptop without GPU
- **Impact:** Wait time 20–40 seconds; poor UX
- **Mitigation:**
  - Show progress indicators
  - Provide GPU recommendations (setup guide)
  - Option to use cloud API (if available)
  - Cache results (for same video)

#### Risk 6: Security: Malicious File Upload
**Scenario:** User uploads malware-like or extremely large file
- **Impact:** Denial-of-service (disk space, CPU exhaustion)
- **Mitigation:**
  - Strict file validation:
    - Max size: 500 MB
    - Magic byte check (confirm actual video format)
    - Scan with VirusTotal API (optional)
  - Sandbox inference (containerization)
  - Rate limiting: 10 requests/hour per IP
  - Cleanup: Delete temp files after 1 hour

#### Risk 7: API Rate Limiting & Abuse
**Scenario:** Malicious actor spams API with requests
- **Impact:** Service degradation
- **Mitigation:**
  - Rate limiting: 10 requests/minute per IP
  - Require API key for production (optional)
  - Queue management (reject if queue > 50 jobs)
  - Log & alert on abuse

#### Risk 8: Model Version Mismatch
**Scenario:** Code expects `TwoStream_Cosign` but old model loaded
- **Impact:** Inference error; confusing error message
- **Mitigation:**
  - Store model metadata (version, architecture name)
  - Verify at load time
  - Clear error: "Model version mismatch; please re-download baseline_model_bisindo.pt"

### 13.5 Testing Strategy

**Unit Tests:**
- Skeleton extraction (mock MediaPipe, test keypoint arrangement)
- Preprocessing (test normalization, padding)
- Decoder (test CTC beam search output)

**Integration Tests:**
- End-to-end: video → skeleton → inference → glosses
- API endpoints: upload, predict, status, results
- Error handling: invalid file, timeout, OOM

**Load Tests:**
- Single user: 5 concurrent requests
- Stress: 50 concurrent requests (should queue gracefully)
- Spike: Sudden 100 requests (monitor resource usage)

**Benchmark:**
- Latency: Single request end-to-end (target: < 30 sec CPU, < 5 sec GPU)
- Throughput: Requests/minute (target: ~5 requests/min on CPU)
- Memory: Peak usage (target: < 2 GB on CPU, < 8 GB on GPU)

---

## 14. Implementation Phases

### Phase 1: Foundation & Core Pipeline (Weeks 1–2)

**Goals:**
- Set up FastAPI backend structure
- Integrate MediaPipe skeleton extraction
- Implement basic preprocessing
- Load and test trained model

**Deliverables:**
- `app/main.py` — FastAPI app skeleton
- `app/services/skeleton_extractor.py` — MediaPipe wrapper
- `app/services/skeleton_preprocessor.py` — Normalization
- `app/services/model_loader.py` — Model loading & caching
- `requirements.txt` — Pinned dependencies
- Unit tests for skeleton extraction

**Files Created:**
```
app/
├── __init__.py
├── main.py
├── config.py
├── api/
│   ├── __init__.py
│   ├── routes.py (stub)
│   ├── schemas.py (stub)
│   └── middleware.py
├── services/
│   ├── __init__.py
│   ├── skeleton_extractor.py (from holistic_86.py)
│   ├── skeleton_preprocessor.py (rewritten)
│   ├── model_loader.py (new)
│   ├── video_processor.py (new)
│   └── inference_engine.py (stub)
├── utils/
│   ├── __init__.py
│   ├── constants.py
│   ├── device.py
│   └── logger.py
└── cache/
    ├── __init__.py
    └── model_cache.py

tests/
├── test_skeleton_extractor.py
└── test_preprocessor.py
```

**Success Criteria:**
- MediaPipe extracts 86 keypoints from sample video
- Preprocessing normalizes skeleton without errors
- Model loads successfully; forward pass completes
- Unit tests pass (80%+ coverage)

---

### Phase 2: API Implementation (Weeks 2–3)

**Goals:**
- Implement REST API endpoints
- Handle file uploads
- Implement async job queue
- Add progress tracking

**Deliverables:**
- `/upload` endpoint
- `/predict` endpoint (async)
- `/status/{job_id}` endpoint
- `/results/{video_id}` endpoint
- Job queue implementation
- API documentation (Swagger)

**Files Created/Modified:**
```
app/
├── api/
│   ├── routes.py (full implementation)
│   ├── schemas.py (full implementation)
│   └── middleware.py (CORS, logging)
├── workers/
│   ├── __init__.py
│   ├── task_queue.py
│   └── inference_worker.py
├── cache/
│   └── model_cache.py
└── services/
    ├── inference_engine.py (full orchestration)
    ├── visualization.py (skeleton rendering)
    └── ctc_decoder.py (decoding wrapper)

requirements.txt (add async dependencies)
.env.example
```

**Success Criteria:**
- Upload endpoint accepts video files
- Predict endpoint queues jobs and returns job_id
- Status endpoint shows progress (% complete)
- API docs accessible at /docs
- Integration tests pass (upload → predict → results)

---

### Phase 3: Frontend Development (Weeks 3–4)

**Goals:**
- Build responsive upload interface
- Implement progress visualization
- Display results (glosses, skeleton, timeline)
- Add error handling

**Deliverables:**
- React/Jinja2 UI with Tailwind CSS
- Upload widget with drag-and-drop
- Progress bars for each stage
- Results dashboard
- Skeleton viewer component

**Files Created:**
```
frontend/
├── [React OR Jinja2]
├── components/
│   ├── Upload.jsx
│   ├── ProgressBar.jsx
│   ├── Results.jsx
│   ├── SkeletonViewer.jsx
│   └── Timeline.jsx
├── static/
│   ├── css/tailwind.css
│   ├── js/api.js
│   └── js/visualization.js
└── public/index.html

OR (Jinja2):
templates/
├── base.html
├── index.html
├── upload.html
├── results.html
└── components/

static/
├── css/
├── js/
└── images/
```

**Success Criteria:**
- Upload works on desktop & mobile
- Progress bars update in real-time (WebSocket/SSE)
- Results display correctly
- Skeleton viewer renders keypoints
- UI responsive (mobile, tablet, desktop)

---

### Phase 4: Integration & Optimization (Weeks 4–5)

**Goals:**
- End-to-end testing (video → glosses)
- Performance optimization
- Error handling & logging
- Documentation

**Deliverables:**
- Full integration tests
- Benchmark results (latency, memory)
- Error handling for edge cases
- README, API docs, deployment guide
- Docker setup

**Files Created/Modified:**
```
tests/
├── test_api.py (integration tests)
├── test_inference.py (end-to-end)
└── fixtures/sample_video.mp4

docs/
├── API.md
├── INSTALLATION.md
├── ARCHITECTURE.md
└── TROUBLESHOOTING.md

Dockerfile
docker-compose.yml
README.md
DEPLOYMENT.md
.github/workflows/tests.yml
```

**Success Criteria:**
- E2E test: Upload → inference → results (< 30 sec CPU)
- Memory: < 2 GB peak on CPU
- Latency: < 5 sec on GPU (RTX 3090)
- All tests pass
- Documentation complete
- Docker build succeeds

---

### Phase 5: Production Hardening (Week 5–6)

**Goals:**
- Security & rate limiting
- Monitoring & logging
- Deployment & scaling
- User feedback mechanism

**Deliverables:**
- Rate limiting middleware
- Advanced logging & monitoring
- Deployment scripts (Heroku, AWS)
- User feedback endpoint
- Performance monitoring dashboard

**Files Created/Modified:**
```
app/
├── api/middleware.py (rate limiting, CORS, auth)
├── utils/logger.py (structured logging)
└── monitoring/metrics.py (Prometheus metrics)

scripts/
├── deploy.sh
└── health_check.py

.github/workflows/
├── tests.yml
├── deploy.yml
└── security-scan.yml

monitoring/
└── prometheus.yml (optional)
```

**Success Criteria:**
- Rate limiting enforced (10 req/min per IP)
- Structured logs (JSON format, searchable)
- Deployment scripts tested
- Monitoring dashboard set up
- Security checklist passed
- Ready for public release

---

## 15. Final Deliverables

### 15.1 Code & Artifacts

- ✅ **Backend:**
  - FastAPI application with inference pipeline
  - MediaPipe skeleton extraction
  - Model loading & caching
  - CTC decoding integration
  - Async job queue
  - Comprehensive error handling

- ✅ **Frontend:**
  - Modern, responsive UI (React or Jinja2)
  - Video upload widget
  - Real-time progress tracking
  - Results visualization (glosses, skeleton, timeline)
  - Mobile-friendly design

- ✅ **Model Integration:**
  - `baseline_model_bisindo.pt` loaded & tested
  - Inference pipeline optimized for speed
  - GPU/CPU device handling
  - Confidence scoring

### 15.2 Documentation

- ✅ **README.md** — Quick start, overview
- ✅ **INSTALLATION.md** — Setup instructions
- ✅ **API.md** — Endpoint reference & examples
- ✅ **ARCHITECTURE.md** — System design, module breakdown
- ✅ **INFERENCE_PIPELINE.md** — Detailed workflow
- ✅ **DEPLOYMENT.md** — Local, Docker, cloud deployment
- ✅ **TROUBLESHOOTING.md** — Common issues & solutions

### 15.3 Configuration Files

- ✅ **requirements.txt** — Python dependencies (pinned)
- ✅ **configs/inference.yaml** — Model hyperparameters
- ✅ **configs/bisindo_gloss_dict.json** — Gloss vocabulary
- ✅ **configs/mediapipe_config.yaml** — Extraction settings
- ✅ **.env.example** — Environment template

### 15.4 Testing & Benchmarks

- ✅ **Unit tests** — Skeleton extraction, preprocessing, decoding
- ✅ **Integration tests** — Full pipeline (video → glosses)
- ✅ **API tests** — Endpoint validation
- ✅ **Load tests** — Concurrent request handling
- ✅ **Benchmark report** — Latency, memory, throughput

### 15.5 Deployment & DevOps

- ✅ **Dockerfile** — Production-ready image
- ✅ **docker-compose.yml** — Local multi-container setup
- ✅ **Deployment scripts** — Heroku, AWS, Google Cloud
- ✅ **Health checks** — Liveness & readiness probes
- ✅ **CI/CD workflows** — GitHub Actions (test, lint, deploy)

### 15.6 Assets & Visualizations

- ✅ **Sample videos** — Test data for demo
- ✅ **Logo & branding** — UI assets
- ✅ **Architecture diagram** — System overview
- ✅ **Data flow diagrams** — Inference pipeline visualization
- ✅ **Performance graphs** — Latency benchmarks

### 15.7 Metadata

- ✅ **LICENSE** — MIT or appropriate
- ✅ **.gitignore** — Standard Python ignores
- ✅ **CHANGELOG.md** — Version history
- ✅ **CODE_OF_CONDUCT.md** — Community guidelines

---

## 16. Success Metrics & Acceptance Criteria

### System Metrics

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Inference Latency (GPU)** | < 5 sec | ≤ 10 sec acceptable |
| **Inference Latency (CPU)** | < 30 sec | ≤ 45 sec acceptable |
| **Memory (Peak)** | < 2 GB CPU | ≤ 4 GB acceptable |
| **Uptime** | 99.5% | ≥ 99% acceptable |
| **API Availability** | 99.9% | ≥ 99.5% acceptable |
| **Test Coverage** | ≥ 80% | ≥ 70% acceptable |

### Model Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| **WER (Word Error Rate)** | ≤ 20% | Measured on validation set |
| **Confidence Calibration** | ≥ 0.9 | High confidence = high accuracy |
| **Inference Speed** | ≥ 50 FPS (GPU) | Real-time capable |

### User Experience

| Metric | Target | Notes |
|--------|--------|-------|
| **UI Load Time** | < 2 sec | First Contentful Paint |
| **Upload Acceptance** | ≥ 95% | Valid video formats |
| **Error Recovery** | 100% | Graceful error messages |
| **Mobile Compatibility** | 100% | Responsive design |

---

## 17. Known Limitations & Future Work

### Current Limitations

1. **Single Language:** Only BISINDO supported (transfer learning needed for other sign languages)
2. **Model Accuracy:** WER ~20% on validation set (room for improvement)
3. **Video Constraints:** ≤ 5 minutes, standard codecs only
4. **MediaPipe Version:** Locked to 0.10.14 (no newer features)
5. **No Streaming:** Inference requires full video upload (not real-time streaming)
6. **No Speaker Adaptation:** Single model for all signers (not signer-specific)

### Future Enhancements

1. **Real-Time Streaming:** Inference on live webcam input
2. **Multi-Language Support:** Train on additional sign languages
3. **Signer Adaptation:** Fine-tune model per user (few-shot learning)
4. **Confidence Explanations:** Highlight which keypoints influenced prediction
5. **Video Preprocessing:** Auto-crop, lighting correction
6. **Mobile App:** Native iOS/Android application
7. **Offline Mode:** Run inference locally in browser (TensorFlow.js)
8. **Community Feedback:** Crowd-source corrections for model improvement
9. **Advanced Visualization:** 3D skeleton animation, motion arrows
10. **API Rate Tiers:** Free tier, Pro tier, Enterprise tier

---

## 18. References & Resources

### Papers
- **ST-GCN:** Spatial Temporal Graph Convolutional Networks for Skeleton-Based Action Recognition
- **CoSign:** Contrastive Learning for Sign Language Recognition
- **CTC Loss:** Connectionist Temporal Classification (Graves et al., 2006)

### Libraries & Frameworks
- [MediaPipe](https://mediapipe.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyTorch](https://pytorch.org/)
- [ctcdecode](https://github.com/parlance/ctcdecode)

### Repositories
- Source: `rgb-to-skeleton-mediapipe/`
- Source: `MSLR_ICCV2025/`

### Community
- BISINDO Sign Language Dataset
- Sign Language Recognition Research Community

---

## Appendix A: Configuration YAML Structure

### inference.yaml (Simplified)

```yaml
# Model configuration
model:
  name: TwoStream_Cosign
  path: models/baseline_model_bisindo.pt
  device: cuda  # or 'cpu'
  
# Visual extractor args
visual_args:
  in_channels: 2  # x, y only
  split: [25, 46, 67, 86]
  temporal_kernel: 5
  hidden_size: 1024
  modes: ['body', 'hand21', 'mouth_8']
  level: '1'
  adaptive: true

# Preprocessing
preprocessing:
  skeleton_format: isharah  # 86-keypoint format
  normalization: true
  normalize_by_center: true
  temporal_padding: 250  # Fixed sequence length
  confidence_threshold: 0.3
  interpolate_missing: true

# Inference
inference:
  batch_size: 1
  num_workers: 0
  device: cuda
  dtype: float32
  
# CTC Decoding
decoding:
  beam_width: 10
  blank_id: 0
  search_mode: beam  # 'beam' or 'max'

# Gloss dictionary
gloss_dict_path: configs/bisindo_gloss_dict.json
```

---

## Appendix B: API Request/Response Boilerplate

### Upload Request Example

```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@example_video.mp4" \
  -H "X-Client-ID: unique-user-id"
```

### Upload Response Example

```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Video uploaded successfully",
  "file_size_mb": 15.7,
  "duration_seconds": 5.5,
  "fps": 25,
  "resolution": "1920x1080",
  "next_step": "/predict"
}
```

---

## Appendix C: Error Handling Reference

| Status Code | Scenario | Example Response |
|-------------|----------|------------------|
| 200 OK | Successful prediction | `{"status": "success", "glosses": [...]}` |
| 202 Accepted | Job queued | `{"status": "accepted", "job_id": "..."}` |
| 400 Bad Request | Invalid file | `{"status": "error", "code": "INVALID_FILE", ...}` |
| 404 Not Found | Video not found | `{"status": "error", "code": "NOT_FOUND", ...}` |
| 413 Payload Too Large | File > 500MB | `{"status": "error", "code": "FILE_TOO_LARGE", ...}` |
| 422 Unprocessable | Extraction failed | `{"status": "error", "code": "EXTRACTION_FAILED", ...}` |
| 500 Server Error | Model crash | `{"status": "error", "code": "MODEL_ERROR", ...}` |
| 503 Service Unavailable | GPU OOM | `{"status": "error", "code": "GPU_OOM", ...}` |
| 504 Gateway Timeout | > 60 sec | `{"status": "error", "code": "TIMEOUT", ...}` |

---

**END OF PLAN**

---

## Summary

This comprehensive plan provides:

✅ **1. Project Overview** — Clear purpose, scope, and user flow  
✅ **2. Repository Analysis** — Detailed breakdown of reusable components from both repos  
✅ **3. System Architecture** — High-level data flow and component design  
✅ **4. End-to-End Pipeline** — Step-by-step inference process (11 detailed stages)  
✅ **5. Folder Structure** — Complete directory layout with annotations  
✅ **6. Code Migration Plan** — Exactly which files to copy, rewrite, or remove  
✅ **7. Model Integration** — How to load, run, and manage the BISINDO model  
✅ **8. Skeleton Extraction** — MediaPipe integration and 86-keypoint format details  
✅ **9. Frontend/UI Plan** — Page layouts, components, responsive design, Tailwind CSS  
✅ **10. FastAPI API Design** — Detailed endpoint specs with request/response formats  
✅ **11. Dependency Plan** — Critical, optional, and removed dependencies  
✅ **12. Deployment Plan** — Local, Docker, cloud (Heroku, AWS, Google Cloud)  
✅ **13. Performance & Risk Analysis** — Bottlenecks, memory, security, mitigation strategies  
✅ **14. Implementation Phases** — 5-phase plan over 5–6 weeks with deliverables  
✅ **15. Final Deliverables** — Code, docs, configs, tests, DevOps, assets  

The plan is **production-oriented**, **technically detailed**, and **immediately actionable** for implementation.

---

**Ready for Phase 1 implementation to begin!**

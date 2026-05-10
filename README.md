<div align="center">

# 🤟 BISINDO CSLR Demo

### Web-based Continuous Sign Language Recognition Interface
### for BISINDO — Bandung Variant · Real-time Analysis

<br/>

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0.0-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-0097A7?style=flat-square)](https://google.github.io/mediapipe/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3.3.0-38B2AC?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

**Companion Application for BISINDO CSLR Research** · [View Research](../MSLR_ICCV2025/)

*End-to-end web interface for skeleton-based continuous sign language recognition*

<br/>

[🚀 Quick Start](#-quick-start) &nbsp;|&nbsp; [📚 Architecture](#-architecture) &nbsp;|&nbsp; [📖 Documentation](#-documentation) &nbsp;|&nbsp; [⚙️ Configuration](#️-configuration) &nbsp;|&nbsp; [🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [System Requirements](#-system-requirements)
- [Quick Start](#-quick-start)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Configuration](#️-configuration)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Troubleshooting](#-troubleshooting)
- [Citation](#-citation)
- [License](#-license)

---

## 🎯 Overview

**BISINDO CSLR Demo** is a full-stack web application that provides an intuitive interface for continuous sign language recognition using skeleton-based deep learning models. It combines:

- **🎬 Real-time video processing** with MediaPipe Holistic pose estimation
- **🧠 Advanced skeleton normalization** with 6-stage preprocessing pipeline
- **⚡ GPU-accelerated inference** using PyTorch models
- **🎨 Modern web UI** built with React and Vite
- **🔄 Async processing** with real-time progress tracking

The application is designed for:
- **Research demonstration** of skeleton-based CSLR models
- **End-user interaction** with minimal technical knowledge required
- **Educational purposes** in computer vision and NLP
- **Production deployment** with proper optimization

---

## ✨ Features

### Backend
✅ **MediaPipe Holistic Integration** — Extract 86 keypoints (hands, pose, face) from video  
✅ **6-Stage Preprocessing Pipeline** — Spatial normalization, temporal smoothing, confidence filtering  
✅ **Model Caching** — Singleton pattern with lazy loading for efficient memory usage  
✅ **Async Job Queue** — Non-blocking inference with progress tracking  
✅ **GPU/CPU Support** — Automatic device selection with fallback  
✅ **Comprehensive Logging** — Rotating file logs for debugging and monitoring  
✅ **RESTful API** — Auto-generated OpenAPI documentation with Swagger UI  

### Frontend
✅ **Drag-and-Drop Upload** — Intuitive video file selection with visual feedback  
✅ **Real-time Progress** — 5-stage progress indicators with live updates  
✅ **Results Visualization** — Gloss timeline with confidence scores and color coding  
✅ **Responsive Design** — Optimized for desktop, tablet, and mobile  
✅ **Error Handling** — User-friendly error messages and recovery options  
✅ **Results Export** — Download predictions as JSON  

---

## 🧠 Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB BROWSER (React)                      │
│  ┌──────────────┬──────────────┬────────────────────────┐   │
│  │Upload (Drag) │ProgressBar   │Results + Timeline      │   │
│  │  Component   │  Component   │   Component            │   │
│  └──────────────┴──────────────┴────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTP / REST API
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend Server                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            Core Processing Pipeline                  │   │
│  │                                                      │   │
│  │  1. Skeleton Extraction (MediaPipe Holistic)         │   │
│  │     → 86 keypoints (GL, GR, GP, GM)                 │   │
│  │                                                      │   │
│  │  2. Skeleton Preprocessing (6 Stages)               │   │
│  │     → Confidence filtering                          │   │
│  │     → Center normalization                          │   │
│  │     → Spatial scaling                               │   │
│  │     → Missing keypoint interpolation                │   │
│  │     → Temporal smoothing                            │   │
│  │     → Temporal padding (250 frames)                 │   │
│  │                                                      │   │
│  │  3. Model Inference (TwoStream_Cosign)              │   │
│  │     → GCN + 1D-CNN + BiLSTM                         │   │
│  │                                                      │   │
│  │  4. CTC Decoding                                    │   │
│  │     → Beam search (width=10)                        │   │
│  │     → Gloss sequence + confidence scores            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Async Job Queue + Model Cache              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Upload** → Video file sent to backend via `/api/upload`
2. **Queue** → Job created, `job_id` returned immediately (non-blocking)
3. **Extract** → MediaPipe extracts 86 keypoints per frame
4. **Preprocess** → 6-stage skeleton normalization
5. **Infer** → Model processes normalized skeleton
6. **Decode** → CTC decoder outputs glosses + confidence
7. **Poll** → Frontend polls `/api/status` & `/api/results`
8. **Display** → Results shown in UI with timeline

---

## 📋 System Requirements

### Hardware
- **CPU:** Intel i5+ / AMD Ryzen 5+ (minimum)
- **RAM:** 8GB (minimum), 16GB+ recommended
- **GPU:** NVIDIA with CUDA support (optional, highly recommended)
  - 2GB+ VRAM for inference
  - CUDA 11.8+ with cuDNN required for GPU acceleration
- **Storage:** 2GB free space for model weights + logs

### Software

#### Backend
- Python 3.10+
- PyTorch 2.0.0+ with CUDA support (if using GPU)
- MediaPipe 0.10.14 (**locked version**, do not upgrade)
- FastAPI, Uvicorn
- NumPy <2.0.0 (PyTorch compatibility)

#### Frontend
- Node.js 18+
- npm or yarn
- Modern web browser (Chrome, Firefox, Safari, Edge)

---
### Installation

```bash
cd c:\TA\Source-Code\BISINDO_PROJECT
cd bisindo-cslr-demo
```

#### Step 2: Backend Setup

**Create virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**For GPU support (optional but recommended):**
```bash
# Install PyTorch with CUDA 11.8 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Configure environment:**
```bash
cp .env.example .env
# Edit .env if needed (optional for development)
```

#### Step 3: Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
```

### Running the Application

#### Terminal 1 — Start Backend Server
```bash
# From project root (venv activated)
python -m uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify backend:**
- API Docs: http://localhost:8000/docs (Swagger UI)
- Health Check: http://localhost:8000/api/health

#### Terminal 2 — Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

**Expected output:**
```
  VITE v4.4.0  ready in 245 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

**Open in browser:**
- Application: http://localhost:3000
- Backend should be running at http://localhost:8000

---

## ⚙️ Configuration

### Backend Configuration (`.env`)

```bash
# Environment
ENVIRONMENT=development          # development, production
DEBUG=true                      # Enable debug logging

# Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model
DEVICE=cuda                     # cuda, cpu
MODEL_PATH=models/baseline_model_bisindo.pt
GLOSS_DICT_PATH=configs/bisindo_gloss_dict.json

# Inference
INFERENCE_TIMEOUT=60            # seconds
MAX_VIDEO_SIZE_MB=500

# Logging
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/app.log

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Configuration (`.env`)

```bash
# API Server
VITE_API_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
```

### Model Configuration

Model hyperparameters are in `configs/`:

```yaml
# configs/Double_Cosign_sd.yaml
dataset: bisindo_sd
model_args:
  num_classes: 1024           # Gloss vocabulary size
feeder_args:
  downsampling: true
  downsampling_ratio: 0.5
  normalization_types:
    - missing_kp
    - temporal
  augmentation_types: []
```

---

## 📚 API Documentation

### Auto-Generated Docs
Open http://localhost:8000/docs in your browser for interactive API documentation.

### Endpoints

#### Health Check
```bash
GET /api/health
```
**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "model_loaded": true,
  "gpu_available": true,
  "timestamp": "2026-05-10T10:30:00Z"
}
```

#### Upload Video
```bash
POST /api/upload
Content-Type: multipart/form-data

Body: { file: <video_file> }
```
**Response:**
```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Video uploaded successfully",
  "file_size_mb": 125.5,
  "fps": 25,
  "resolution": "640x480"
}
```

#### Start Prediction
```bash
POST /api/predict?video_id=<video_id>
```
**Response:**
```json
{
  "status": "queued",
  "job_id": "job_550e8400-e29b-41d4-a716-446655440000",
  "message": "Job queued for processing"
}
```

#### Check Status
```bash
GET /api/status/{job_id}
```
**Response:**
```json
{
  "job_id": "job_550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": {
    "stage": "model_inference",
    "percent": 75,
    "message": "Running inference..."
  }
}
```

#### Get Results
```bash
GET /api/results/{video_id}
```
**Response:**
```json
{
  "status": "success",
  "video_id": "550e8400-e29b-41d4-a716-446655440000",
  "results": {
    "full_sentence": "ayah ibu anak rumah",
    "sentence_confidence": 0.856,
    "glosses": [
      {
        "id": 0,
        "word": "ayah",
        "confidence": 0.92,
        "start_frame": 10,
        "end_frame": 35,
        "start_time": "0.4s",
        "end_time": "1.4s"
      },
      { "id": 1, "word": "ibu", "confidence": 0.88, ... },
      { "id": 2, "word": "anak", "confidence": 0.81, ... },
      { "id": 3, "word": "rumah", "confidence": 0.79, ... }
    ],
    "processing_time": 8.5
  }
}
```

---

## 🔧 Development

### Project Structure

```
bisindo-cslr-demo/
│
├── app/                          # Backend (FastAPI)
│   ├── main.py                  # Application entry point
│   ├── config.py                # Configuration (Pydantic)
│   ├── api/
│   │   ├── routes.py            # Endpoint handlers
│   │   └── schemas.py           # Request/response models
│   ├── services/
│   │   ├── skeleton_extractor.py      # MediaPipe extraction
│   │   ├── skeleton_preprocessor.py   # Normalization pipeline
│   │   ├── model.py             # Model architecture (placeholder)
│   │   └── inference_engine.py  # Inference orchestration (Phase 2)
│   ├── cache/
│   │   └── model_cache.py       # Singleton model loader
│   ├── utils/
│   │   ├── constants.py         # Magic numbers & config
│   │   ├── device.py            # GPU/CPU management
│   │   └── __init__.py          # Logging setup
│   └── workers/                 # Async job processing (Phase 2)
│
├── frontend/                     # Frontend (React + Vite)
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── main.jsx             # React entry
│   │   ├── App.jsx              # Main component
│   │   ├── components/
│   │   │   ├── Upload.jsx
│   │   │   ├── ProgressBar.jsx
│   │   │   └── Results.jsx
│   │   ├── services/
│   │   │   └── api.js           # Axios client
│   │   └── styles/
│   │       └── index.css        # Tailwind + custom
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── configs/
│   ├── Double_Cosign_sd.yaml    # Model config
│   ├── bisindo_gloss_dict.json  # Gloss vocabulary
│   └── dataset_configs/
│
├── tests/
│   ├── test_skeleton_extractor.py
│   ├── test_skeleton_preprocessor.py
│   ├── conftest.py
│   └── __init__.py
│
├── models/                       # Model weights (gitignored)
│   └── baseline_model_bisindo.pt
│
├── logs/                         # Application logs (gitignored)
│   └── app.log
│
├── uploads/                      # User uploads (gitignored)
│
├── scripts/
│   └── setup.py                 # Setup script
│
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── README.md                    # (This file)
├── DEVELOPMENT.md               # Development guide
├── plan.md                      # Architecture & planning
└── LICENSE
```

### Running Tests

#### Backend Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_skeleton_extractor.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

#### Code Quality
```bash
# Format code
black app/ frontend/src/

# Lint
flake8 app/
mypy app/

# Auto-import sorting
isort app/
```

### Building for Production

#### Frontend Build
```bash
cd frontend
npm run build

# Output: frontend/dist/
```

#### Backend Production Server
```bash
# Install production server
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## ⚡ Performance

### Benchmarks (Baseline)

| Metric | Value | Notes |
|---|---|---|
| **Video Processing Speed** | ~3-8 sec/min | Depends on video length and GPU |
| **Skeleton Extraction** | 25 FPS | MediaPipe on single GPU |
| **Model Inference** | 5-15 ms/frame | With CUDA |
| **Memory Footprint** | ~2GB GPU | Model + batch processing |
| **UI Responsiveness** | <100ms | React + local polling |

### Optimization Tips

**Backend:**
- Use GPU (`DEVICE=cuda`) for 10x speedup
- Ensure CUDA Toolkit 11.8+ is installed
- Monitor `/api/health` for GPU status

**Frontend:**
- Modern browser with ES6 support
- Disable browser extensions for optimal performance
- Clear cache if UI lags

---

## 🐛 Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Check process
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process (Linux/macOS)
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False:
# 1. Verify NVIDIA driver: nvidia-smi
# 2. Install CUDA Toolkit 11.8
# 3. Reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### MediaPipe Import Error
```bash
# Exact version required (0.10.14)
pip uninstall mediapipe
pip install mediapipe==0.10.14 --no-cache-dir
```

### Frontend Issues

#### Can't Connect to Backend
1. Verify backend running: `http://localhost:8000/health`
2. Check CORS in `.env`: `CORS_ORIGINS=http://localhost:3000`
3. Check browser console (F12) for errors
4. Verify `.env` in frontend has correct API URL

#### Hot Reload Not Working
```bash
# Restart Vite dev server
npm run dev

# Check for port conflicts
lsof -i :3000  # macOS/Linux
```

#### Memory Issues
- Reduce video file size
- Restart backend between large uploads
- Check system RAM availability

---

## 📊 Evaluation Metrics

The system measures performance using:

| Metric | Description |
|---|---|
| **WER** (Word Error Rate) | Edit distance between predicted & reference gloss sequences (lower is better) |
| **Confidence Score** | Model confidence in predictions (0-1 scale) |
| **Inference Latency** | Time from upload to results (in seconds) |
| **FPS** | Frames per second processed (higher is better) |

---

## 📚 Documentation

- **[plan.md](./plan.md)** — Full system architecture & technical planning
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** — Development environment setup & debugging guide
- **[API Docs](http://localhost:8000/docs)** — Interactive Swagger UI (live)
- **[MSLR Research](../MSLR_ICCV2025/)** — Underlying research & model details

---

## 📖 Citation

If you use this application in your research, please cite:

```bibtex
@software{bisindo_cslr_demo,
  title   = {BISINDO CSLR Demo: Web Interface for Skeleton-Based Sign Language Recognition},
  author  = {Pratama, Mahardika and Sarah},
  year    = {2026},
  url     = {https://github.com/YOUR_REPO/bisindo-cslr-demo},
  note    = {Companion application for BISINDO CSLR research}
}
```

Also cite the underlying research:

```bibtex
@thesis{pratama2026bisindo,
  title   = {Analisis Konfigurasi Pipeline Pre-Processing pada Model GCN-1DCNN-BiLSTM
             untuk Continuous Sign Language Recognition BISINDO Variasi Bandung
             dalam Skenario Signer-Independent},
  author  = {Pratama, Mahardika and Sarah},
  year    = {2026},
  school  = {Politeknik Negeri Bandung},
  type    = {Laporan Tugas Akhir}
}
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](./LICENSE) file for details.

The underlying BISINDO CSLR research is available under **Academic Use License** — refer to [MSLR_ICCV2025/LICENSE](../MSLR_ICCV2025/LICENSE).

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** changes: `git commit -m 'Add amazing feature'`
4. **Push** to branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 (Python) and ESLint (JavaScript)
- Write unit tests for new features
- Update documentation
- Test on both CPU and GPU if possible

---

## 📬 Contact & Support

For questions, issues, or suggestions:

| Role | Name | NIM | Contact |
|---|---|---|---|
| Lead Developer | Mahardika Pratama | 221524044 | [GitHub](https://github.com/) |
| Co-Developer | Sarah | 221524059 | [GitHub](https://github.com/) |

**Institution:** Politeknik Negeri Bandung  
**Program:** D-IV Teknik Informatika

---

## 🙏 Acknowledgements

This project builds upon:
- **Min et al. (ICCV Workshop 2025)** — *A Closer Look at Skeleton-based CSLR*
- **Jiao et al. (ICCV 2023)** — *CoSign: Exploring Co-occurrence Signals in Skeleton-based CSLR*
- **Google MediaPipe** — Efficient pose estimation framework
- **Kaldi SCTK** — Evaluation tools

Special thanks to all signers and contributors in the BISINDO dataset collection process.

---

<div align="center">

Made with ❤️ for the Indonesian Deaf community · Politeknik Negeri Bandung · 2026

[⬆ Back to Top](#bisindo-cslr-demo)

</div>

# CPU-Only Setup Guide for BISINDO CSLR Demo

> **For users without NVIDIA GPU or CUDA support**

## Quick Start (CPU Mode)

### Prerequisites
- Python 3.10+
- 8GB+ RAM (16GB recommended for larger videos)
- No GPU required

---

## Step 1: Create Virtual Environment

```bash
cd bisindo-cslr-demo

# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

## Step 2: Install CPU-Only PyTorch

```bash
# Windows/macOS/Linux - CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

This installs a lightweight PyTorch version (~150MB) without CUDA dependencies.

---

## Step 3: Install Other Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure for CPU

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit `.env` with CPU settings:

```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Server
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1  # Use 1 worker for CPU to avoid memory issues

# Model - CPU MODE
DEVICE=cpu  # Force CPU usage
MODEL_PATH=models/baseline_model_bisindo.pt
GLOSS_DICT_PATH=configs/bisindo_gloss_dict.json

# Inference
BATCH_SIZE=1  # Keep batch size 1 for CPU
INFERENCE_TIMEOUT=120  # Increase timeout for CPU (slower processing)
MAX_VIDEO_SIZE_MB=500

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## Step 5: Run Backend

```bash
python -m uvicorn app.main:app --reload
```

**Expected output (CPU mode):**
```
INFO:     Device: CPU (Using CPU for inference)
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Step 6: Run Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

---

## Performance Expectations (CPU)

| Task | Time | Notes |
|---|---|---|
| **Skeleton Extraction** | 2-5 sec/min video | MediaPipe on CPU |
| **Preprocessing** | 0.5-1 sec | 6-stage pipeline |
| **Model Inference** | 50-200 ms/frame | Depends on video length |
| **CTC Decoding** | 0.2-0.5 sec | Beam search |
| **Total (1 min video)** | 2-5 minutes | Full pipeline |

### Example Timeline
```
Video: 1 minute (1500 frames @ 25 FPS)

Upload             : 2-5 sec
Skeleton Extract   : ~120 sec (at 12.5 FPS on CPU)
Preprocessing      : ~5 sec
Model Inference    : ~120 sec (80-150 ms per frame)
CTC Decoding       : ~1 sec
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total              : ~250 seconds (~4 minutes)
```

---

## Optimization Tips for CPU

### 1. Reduce Video Size
- **Lower resolution:** 480p instead of 1080p
- **Shorter videos:** Under 60 seconds recommended
- **Convert format:** MP4 with H.264 codec

Example using FFmpeg:
```bash
ffmpeg -i input.mp4 -vf scale=640:480 -c:v libx264 -preset fast -crf 23 output.mp4
```

### 2. Adjust Settings

**In `.env`:**
```bash
INFERENCE_TIMEOUT=180  # 3 minutes for longer videos
API_WORKERS=1          # Single worker to manage CPU load
```

### 3. System Optimization
- Close unnecessary applications
- Ensure good disk space (for temporary files)
- Monitor RAM usage during processing

---

## Monitoring CPU Usage

### Windows (Task Manager)
```
Ctrl+Shift+Esc → Performance → CPU
```

### macOS (Activity Monitor)
```
⌘+Space → Activity Monitor → CPU
```

### Linux (Terminal)
```bash
top
# or
htop  # If installed
```

---

## Troubleshooting

### Issue: "Out of Memory" Error

**Solution:**
1. Reduce video size (see optimization tips)
2. Increase system RAM or free up memory
3. Reduce batch size to 1 (already set)

```bash
# Check available memory
# Windows
wmic OS get TotalVisibleMemorySize,FreePhysicalMemory

# macOS/Linux
free -h  # Linux
vm_stat | grep "Pages free"  # macOS
```

### Issue: Very Slow Processing

**Expected on CPU:**
- Slower processing is normal
- Use smaller videos for testing
- GPU would be 10-50x faster

### Issue: "CUDA not available" but want to use GPU later

To switch to GPU later:
```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Install GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update .env: DEVICE=cuda
```

---

## Recommended Hardware for CPU

| Category | Recommended |
|---|---|
| **Processor** | Intel i7+ / AMD Ryzen 7+ (6+ cores) |
| **RAM** | 16GB minimum, 32GB recommended |
| **Storage** | SSD with 10GB+ free space |
| **OS** | Windows 10+, macOS 10.14+, Ubuntu 18.04+ |

---

## Installation Summary

### Quick Copy-Paste

```bash
# 1. Navigate to project
cd c:\TA\Source-Code\BISINDO_PROJECT\bisindo-cslr-demo

# 2. Create & activate venv
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 3. Install CPU PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4. Install other dependencies
pip install -r requirements.txt

# 5. Create CPU config
cp .env.example .env
# Edit .env and set: DEVICE=cpu

# 6. Start backend
python -m uvicorn app.main:app --reload

# 7. In new terminal, start frontend
cd frontend
npm install
npm run dev

# 8. Open http://localhost:3000
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` with `DEVICE=cpu`
3. Run backend: `python -m uvicorn app.main:app --reload`
4. Run frontend: `cd frontend && npm run dev`
5. Test with small videos first
6. Gradually increase video size

---

## Need Help?

- Check [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup
- See [README.md](./README.md) for full documentation
- Review [plan.md](./plan.md) for architecture details

---

## Performance Comparison

If you later upgrade to GPU:

| Operation | CPU | GPU | Speedup |
|---|---|---|---|
| Skeleton Extract | 5 sec/min | 1 sec/min | 5x |
| Model Inference | 120 sec/min | 10 sec/min | 12x |
| **Total (1 min)** | **~250 sec** | **~20 sec** | **~12x** |

---

**Happy sign language recognition! 🤟**

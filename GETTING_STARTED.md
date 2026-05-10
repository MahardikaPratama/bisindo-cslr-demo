# 🚀 Getting Started Guide

Welcome to **BISINDO CSLR Demo**! This guide will help you get started in just a few minutes.

---

## ⚡ Quick Start (2 Minutes)

### For GPU Users (Recommended)
```bash
# 1. Navigate to project
cd bisindo-cslr-demo

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install GPU PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy GPU configuration
cp .env.gpu .env

# 6. Start backend
python app/main.py

# 7. In new terminal, start frontend
cd frontend
npm install
npm run dev

# 8. Open http://localhost:3000
```

### For CPU-Only Users
```bash
# Steps 1-2: Same as above

# 3. Install CPU PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 4-8: Same as GPU users

# Note: Processing will be slower (~4-5 min per minute of video)
```

---

## 📋 Configuration Files

Choose ONE based on your hardware:

### 🖥️ CPU-Only Setup
```bash
cp .env.cpu .env
```
**Best for:** Development, testing, laptops without GPU  
**Performance:** 2-5 minutes per 1 minute of video  
**RAM needed:** 8GB minimum  

**Detailed guide:** [CPU_SETUP.md](CPU_SETUP.md)

### ⚡ GPU (NVIDIA CUDA) Setup
```bash
cp .env.gpu .env
```
**Best for:** Production, fast inference  
**Performance:** 20-60 seconds per 1 minute of video  
**VRAM needed:** 2GB minimum (4GB+ recommended)  

**Requirements:**
- NVIDIA GPU with CUDA Compute Capability 3.5+
- CUDA Toolkit 11.8+
- Latest NVIDIA driver

### 🤖 Auto-Detect Setup
```bash
cp .env.example .env
```
**Best for:** Mixed environments  
**Performance:** Auto-selects GPU if available, falls back to CPU  

---

## 📖 Documentation

| Document | Purpose | Best For |
|---|---|---|
| **[README.md](README.md)** | Full documentation & features | Overview & reference |
| **[CPU_SETUP.md](CPU_SETUP.md)** | CPU-only detailed guide | CPU users |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Side-by-side CPU vs GPU | Quick comparison |
| **[ENV_CONFIG.md](ENV_CONFIG.md)** | Environment configuration | Configuration details |
| **[DEVELOPMENT.md](DEVELOPMENT.md)** | Development setup | Developers |
| **[plan.md](plan.md)** | Architecture & design | Technical details |

---

## ✅ Verification

After starting the application, verify it's working:

### Backend
Open http://localhost:8000/docs in your browser
- Should show Swagger API documentation
- Try calling `/api/health` endpoint

### Frontend
Open http://localhost:3000 in your browser
- Should see upload interface
- Try uploading a test video

---

## 🎬 First Test

### Step 1: Prepare Video
Create a small test video (under 30 seconds):
```bash
# Using FFmpeg (optional)
ffmpeg -f lavfi -i testsrc=duration=5:size=640x480 -f lavfi -i sine=frequency=1000 test.mp4
```

Or find any short BISINDO video online.

### Step 2: Upload Video
1. Go to http://localhost:3000
2. Click on upload area or drag-drop video
3. Click "Upload & Analyze"

### Step 3: Monitor Progress
- Watch the progress bar update
- 5 stages: extraction → preprocessing → inference → decoding

### Step 4: View Results
- See predicted sentence
- Check gloss timeline with confidence scores
- Download results as JSON

---

## ⚙️ System Requirements

### Minimum (CPU)
- Python 3.10+
- 8GB RAM
- 2GB free storage
- Node.js 18+

### Recommended (GPU)
- Python 3.10+
- NVIDIA GPU (RTX 3060 or better)
- 4GB VRAM
- 16GB system RAM
- CUDA 11.8+

---

## 🐛 Common Issues

### Issue: "Port 8000 already in use"
```bash
# Use different port
uvicorn app.main:app --port 8001
# Then update frontend .env: VITE_API_URL=http://localhost:8001
```

### Issue: "ModuleNotFoundError: No module named 'mediapipe'"
```bash
# Reinstall MediaPipe (locked version)
pip install mediapipe==0.10.14 --no-cache-dir
```

### Issue: "CUDA not available"
```bash
# Check NVIDIA driver
nvidia-smi

# If error, install NVIDIA driver:
# https://www.nvidia.com/Download/driverDetails.aspx

# Then reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

See [DEVELOPMENT.md](DEVELOPMENT.md) for more troubleshooting.

---

## 📊 Performance Expectations

### CPU Mode
```
1 minute video → ~250 seconds processing (~4-5 minutes)

Skeleton Extraction: 5 seconds
Preprocessing:      1 second
Model Inference:    120 seconds
CTC Decoding:       1 second
```

### GPU Mode (RTX 3060+)
```
1 minute video → ~20 seconds processing

Skeleton Extraction: 1 second
Preprocessing:      1 second
Model Inference:    10 seconds
CTC Decoding:       0.5 second
```

---

## 🔧 Development

### Installing Dev Dependencies
```bash
pip install -r requirements-dev.txt
```

### Running Tests
```bash
pytest tests/ -v
```

### Code Quality
```bash
# Format
black app/ frontend/src/

# Lint
flake8 app/
mypy app/

# Auto-sort imports
isort app/
```

---

## 🚀 Next Steps

### After Verification
1. ✅ Verify backend running at http://localhost:8000/docs
2. ✅ Verify frontend running at http://localhost:3000
3. ✅ Test with sample video

### For Development
- Read [DEVELOPMENT.md](DEVELOPMENT.md) for debugging
- Check [plan.md](plan.md) for architecture

### For Production (Phase 5)
- Build frontend: `cd frontend && npm run build`
- Use production server: `gunicorn app.main:app --workers 4`
- Deploy to Docker/cloud

---

## 📚 Architecture Overview

```
Browser (React 18.2) ←→ HTTP ←→ FastAPI Backend (Python 3.10+)
    ↓                                    ↓
Upload Component                 MediaPipe Extraction
Progress Bar                      Skeleton Preprocessor
Results Display                   Model Inference
                                  CTC Decoding
```

---

## 🤝 Support

- **Issues:** Check [DEVELOPMENT.md](DEVELOPMENT.md) troubleshooting
- **Questions:** See [README.md](README.md) documentation
- **Configuration:** See [ENV_CONFIG.md](ENV_CONFIG.md)
- **Architecture:** See [plan.md](plan.md)

---

## 📋 Checklist

Before running:
- [ ] Python 3.10+ installed
- [ ] Node.js 18+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Model weights downloaded (if needed)

After starting:
- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] `/api/health` returns 200 status
- [ ] Upload interface displays

---

## 🎯 What's Next?

### Phase 2 (Upcoming)
- Integration of actual model inference
- CTC decoder implementation
- Async job queue

### Phase 3+
- WebSocket support
- Advanced monitoring
- Docker deployment

---

**Ready to recognize sign language? 🤟 Upload a video and get started!**

For detailed information, see [README.md](README.md)

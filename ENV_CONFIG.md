# Environment Configuration Guide

This directory contains multiple `.env` template files for different hardware setups.

## Available Configurations

### 🤖 Default (Auto-Detect)
**File:** `.env.example`
- Auto-detects CUDA availability
- Falls back to CPU if no GPU found
- Best for mixed environments

### ⚡ GPU (NVIDIA CUDA)
**File:** `.env.gpu`
- Optimized for NVIDIA GPUs
- Requires CUDA 11.8+
- Multiple API workers for parallel requests
- **Recommended for production**

### 💻 CPU Only
**File:** `.env.cpu`
- CPU-only computation
- Reduced memory footprint
- Single API worker
- **Recommended for development/testing**

---

## Quick Setup

### For GPU System
```bash
cp .env.gpu .env
# Edit .env if needed
python app/main.py
```

### For CPU System
```bash
cp .env.cpu .env
# Edit .env if needed
python app/main.py
```

### For Auto-Detect (Default)
```bash
cp .env.example .env
# Edit .env if needed
python app/main.py
```

---

## Configuration Comparison

| Setting | `.env.gpu` | `.env.cpu` | `.env.example` |
|---|---|---|---|
| **DEVICE** | cuda | cpu | cuda (falls back to cpu) |
| **API_WORKERS** | 4 | 1 | 2 |
| **BATCH_SIZE** | 1 | 1 | 1 |
| **INFERENCE_TIMEOUT** | 60s | 120s | 60s |
| **Best For** | Production | Testing | Development |

---

## Detailed Settings

### DEVICE
- `cuda` — Use NVIDIA GPU (requires CUDA 11.8+)
- `cpu` — Use CPU only
- `auto` — Auto-detect (use cuda if available, else cpu)

### API_WORKERS
- **CPU:** 1 (avoid overload)
- **GPU:** 2-4 (parallel requests)

### BATCH_SIZE
- **CPU:** 1 (memory constraint)
- **GPU:** 1-4 (depends on VRAM)

### INFERENCE_TIMEOUT
- **CPU:** 120-180 seconds (slower processing)
- **GPU:** 60 seconds (faster processing)

---

## Installation

### GPU Setup
```bash
# Install PyTorch with CUDA 11.8 support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other dependencies
pip install -r requirements.txt

# Verify GPU
python -c "import torch; print(f'GPU Available: {torch.cuda.is_available()}')"
```

### CPU Setup
```bash
# Install CPU-only PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies
pip install -r requirements.txt

# Verify CPU
python -c "import torch; print(f'CPU Available: {torch.cpu.is_available()}')"
```

---

## Performance Expectations

### GPU (NVIDIA)
- **Framework:** 20-60 seconds per minute of video
- **Total (1 min):** ~30 seconds
- **Memory:** 2-4 GB VRAM

### CPU
- **Framework:** 200-300 seconds per minute of video
- **Total (1 min):** ~4-5 minutes
- **Memory:** 4-8 GB RAM

---

## Switching Modes

### From GPU to CPU
```bash
# Uninstall CUDA version
pip uninstall torch torchvision torchaudio

# Install CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Update config
cp .env.cpu .env
python app/main.py
```

### From CPU to GPU
```bash
# Uninstall CPU version
pip uninstall torch torchvision torchaudio

# Install GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Update config
cp .env.gpu .env
python app/main.py
```

---

## Troubleshooting

### GPU Not Detected

```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If False:
# 1. Verify NVIDIA driver
nvidia-smi

# 2. Install CUDA Toolkit 11.8
# https://developer.nvidia.com/cuda-11-8-0-download-archive

# 3. Reinstall PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

### Memory Issues

**GPU:**
```bash
# Reduce batch size in .env
BATCH_SIZE=1
```

**CPU:**
```bash
# Use smaller videos
# Close unnecessary applications
# Reduce MAX_VIDEO_SIZE_MB
```

---

## Recommendations

- **Production:** Use `.env.gpu` with NVIDIA GPU
- **Development:** Use `.env.cpu` for consistency and portability
- **Testing:** Use `.env.example` with auto-detection

---

For more details, see:
- [README.md](README.md) — Full documentation
- [CPU_SETUP.md](CPU_SETUP.md) — CPU-specific guide
- [DEVELOPMENT.md](DEVELOPMENT.md) — Development setup

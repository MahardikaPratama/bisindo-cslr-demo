# Quick Reference: CPU vs GPU Setup

## Side-by-Side Comparison

### 📋 Installation

#### 🖥️ CPU-Only
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install CPU PyTorch (lightweight ~150MB)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy CPU config
cp .env.cpu .env

# 5. Run
python -m uvicorn app.main:app --reload
```

#### ⚡ GPU (NVIDIA)
```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install GPU PyTorch with CUDA 11.8 (~2.2GB)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy GPU config
cp .env.gpu .env

# 5. Run
python -m uvicorn app.main:app --reload
```

---

### ⚙️ Configuration (.env)

| Setting | CPU | GPU |
|---|---|---|
| **DEVICE** | `cpu` | `cuda` |
| **API_WORKERS** | `1` | `4` |
| **BATCH_SIZE** | `1` | `1` |
| **INFERENCE_TIMEOUT** | `120` | `60` |
| **Config File** | `.env.cpu` | `.env.gpu` |

---

### ⏱️ Performance (1-minute video)

| Operation | CPU | GPU | Speedup |
|---|---|---|---|
| **Skeleton Extract** | 5 sec | 1 sec | 5x |
| **Preprocessing** | 1 sec | 1 sec | 1x |
| **Model Inference** | 120 sec | 10 sec | 12x |
| **Decoding** | 0.5 sec | 0.5 sec | 1x |
| **TOTAL** | ~250 sec | ~20 sec | **12x** |

---

### 💾 Memory Requirements

#### CPU
- **RAM:** 8GB minimum, 16GB recommended
- **Storage:** 500MB for dependencies
- **Notes:** No special drivers needed

#### GPU
- **VRAM:** 2GB minimum, 4GB+ recommended
- **System RAM:** 8GB (for OS + supporting tasks)
- **CUDA:** Toolkit 11.8+
- **cuDNN:** 8.6+
- **Driver:** Latest NVIDIA driver

---

### 🚀 Performance Optimization

#### CPU Tips
```bash
# Use smaller videos (< 1 minute)
# Reduce resolution to 480p
# Close unnecessary apps
# Ensure 16GB+ RAM available
# Use SSD storage
```

**Settings to adjust:**
```env
# .env.cpu
MAX_VIDEO_SIZE_MB=300      # Reduce max size
INFERENCE_TIMEOUT=180      # Increase timeout
API_WORKERS=1              # Keep single worker
```

#### GPU Tips
```bash
# Install latest NVIDIA driver
# Ensure CUDA 11.8+ installed
# Use dedicated GPU (not integrated)
# Monitor VRAM with nvidia-smi
```

**Settings to adjust:**
```env
# .env.gpu
BATCH_SIZE=2               # If VRAM > 4GB
API_WORKERS=4              # Parallel processing
INFERENCE_TIMEOUT=60       # Fast processing
```

---

### 📊 Hardware Recommendations

#### For CPU-Only
```
Budget System:
- CPU: Intel i7 (6+ cores) or AMD Ryzen 7
- RAM: 16GB DDR4+
- Storage: SSD 256GB+
- OS: Windows 10+, Ubuntu 18.04+

Mid-Range System:
- CPU: Intel i9 or AMD Ryzen 9
- RAM: 32GB DDR4+
- Storage: SSD 512GB+
```

#### For GPU Acceleration
```
Budget GPU System:
- CPU: Intel i5 or AMD Ryzen 5
- GPU: RTX 3050 or GTX 1660 (2GB VRAM)
- RAM: 8GB DDR4+
- Storage: SSD 256GB+

Recommended GPU System:
- CPU: Intel i7 or AMD Ryzen 7
- GPU: RTX 3070 or RTX 4070 (8GB VRAM)
- RAM: 16GB DDR4+
- Storage: SSD 512GB+ NVMe
```

---

### 🔧 Troubleshooting

#### CPU Issues

**Problem:** Memory error
```
Solution: Use smaller videos, close apps
# Monitor RAM
free -h  # Linux
```

**Problem:** Very slow processing
```
Solution: This is normal on CPU
# Try videos < 30 seconds
# Use GPU if possible
```

#### GPU Issues

**Problem:** CUDA not detected
```bash
# Check GPU
nvidia-smi

# Check PyTorch
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 --force-reinstall
```

**Problem:** Out of VRAM
```env
# In .env.gpu, reduce:
BATCH_SIZE=1
API_WORKERS=2
```

---

### 🔄 Switching Between CPU and GPU

#### CPU → GPU
```bash
# 1. Uninstall CPU version
pip uninstall torch torchvision torchaudio

# 2. Install GPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 3. Update config
cp .env.gpu .env

# 4. Restart
python -m uvicorn app.main:app --reload
```

#### GPU → CPU
```bash
# 1. Uninstall GPU version
pip uninstall torch torchvision torchaudio

# 2. Install CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 3. Update config
cp .env.cpu .env

# 4. Restart
python -m uvicorn app.main:app --reload
```

---

### 📖 Documentation

- **CPU Setup:** See [CPU_SETUP.md](CPU_SETUP.md)
- **Full Config:** See [ENV_CONFIG.md](ENV_CONFIG.md)
- **General Setup:** See [README.md](README.md)
- **Development:** See [DEVELOPMENT.md](DEVELOPMENT.md)

---

### ✅ Verification Checklist

#### Before Running on CPU
- [ ] Python 3.10+ installed
- [ ] Virtual environment created
- [ ] CPU PyTorch installed
- [ ] `.env.cpu` copied and configured
- [ ] 16GB+ RAM available
- [ ] Storage space available

#### Before Running on GPU
- [ ] NVIDIA driver installed (latest)
- [ ] CUDA 11.8+ installed
- [ ] cuDNN 8.6+ installed
- [ ] GPU PyTorch installed
- [ ] `.env.gpu` copied and configured
- [ ] GPU memory > 2GB VRAM
- [ ] `nvidia-smi` shows GPU

---

**Choose CPU for development, GPU for production! 🚀**

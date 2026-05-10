# Development Guide

## Setting Up the Development Environment

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA GPU with CUDA support (optional but recommended)
- Git

### Backend Development Setup

#### Step 1: Create Virtual Environment
```bash
cd bisindo-cslr-demo
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 2: Install Dependencies
```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

#### Step 3: Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional for development)
# Key settings:
# - DEVICE=cuda (or cpu)
# - LOG_LEVEL=DEBUG (for debugging)
```

#### Step 4: Run Backend
```bash
# Option 1: Direct Python
python -m uvicorn app.main:app --reload

# Option 2: Uvicorn (more control)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: With debugging
uvicorn app.main:app --reload --log-level debug
```

**Backend will be available at:** http://localhost:8000  
**API Documentation:** http://localhost:8000/docs (Swagger UI)

### Frontend Development Setup

#### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

#### Step 2: Configure Environment
```bash
cp .env.example .env

# Edit .env if backend is on different address
# VITE_API_URL=http://localhost:8000
```

#### Step 3: Run Development Server
```bash
npm run dev
```

**Frontend will be available at:** http://localhost:3000

### Running Both Services

#### Terminal 1 - Backend
```bash
# From project root
source venv/bin/activate  # or venv\Scripts\activate on Windows
python -m uvicorn app.main:app --reload
```

#### Terminal 2 - Frontend
```bash
# From project root
cd frontend
npm run dev
```

Once both are running:
1. Open http://localhost:3000 in your browser
2. Upload a test video
3. Monitor backend logs for processing

## Development Workflow

### Code Organization

**Backend:**
```
app/
├── main.py                    # FastAPI app entry point
├── config.py                  # Configuration with Pydantic
├── api/
│   ├── routes.py             # Endpoint handlers
│   └── schemas.py            # Pydantic models
├── services/
│   ├── skeleton_extractor.py   # MediaPipe extraction
│   ├── skeleton_preprocessor.py # 6-stage preprocessing
│   ├── model.py              # Model architecture
│   └── inference_engine.py    # (Phase 2)
├── cache/
│   └── model_cache.py        # Singleton model loader
├── utils/
│   ├── constants.py          # Magic numbers
│   ├── device.py             # GPU/CPU management
│   └── __init__.py           # Logging setup
└── workers/                   # (Phase 2 - async jobs)
```

**Frontend:**
```
frontend/
├── public/
│   └── index.html            # HTML entry
├── src/
│   ├── main.jsx              # React entry
│   ├── App.jsx               # Main component
│   ├── styles/
│   │   └── index.css         # Tailwind + custom
│   ├── components/
│   │   ├── Upload.jsx        # Upload interface
│   │   ├── ProgressBar.jsx   # Progress display
│   │   └── Results.jsx       # Results display
│   └── services/
│       └── api.js            # Axios API client
├── vite.config.js            # Vite configuration
├── tailwind.config.js        # Tailwind configuration
└── package.json              # Dependencies
```

### Making Changes

#### Backend Changes
1. Edit files in `app/`
2. Backend auto-reloads with `--reload` flag
3. Check http://localhost:8000/docs for API updates

#### Frontend Changes
1. Edit files in `frontend/src/`
2. Vite dev server auto-reloads on save
3. Check console (F12) for errors

### Testing

#### Backend Tests
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_skeleton_extractor.py

# With coverage
pytest tests/ --cov=app

# Watch mode
pytest-watch tests/
```

#### Frontend Tests (Future)
```bash
# Setup testing library (Phase 3+)
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest

# Run tests
npm run test
```

### Code Quality

#### Formatting
```bash
# Format Python code
black app/ tests/

# Format JavaScript
npm run format  # (needs prettier setup)

# Auto-sort imports
isort app/
```

#### Linting
```bash
# Python linting
flake8 app/ tests/

# Type checking
mypy app/

# JavaScript linting (future)
npm run lint
```

## Debugging

### Backend Debugging

#### Using print() statements
```python
# In app/services/skeleton_extractor.py
print(f"DEBUG: Extracted {keypoints.shape} keypoints")
```

#### Using logging
```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

#### Accessing Logs
```bash
# Check log file
tail -f logs/app.log

# Or in Docker (Phase 5)
docker logs <container-id>
```

### Frontend Debugging

#### Browser DevTools
1. Press F12 to open Chrome DevTools
2. Check Console tab for errors/logs
3. Check Network tab for API calls
4. Use React DevTools extension

#### Logging
```javascript
// In React components
console.log("Debug:", variable)
console.error("Error:", error)
```

## Common Issues & Solutions

### Issue: Backend won't start
**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port:
uvicorn app.main:app --port 8001
```

### Issue: Frontend can't connect to backend
**Error:** `CORS error` or `Connection refused`

**Solution:**
1. Verify backend is running: http://localhost:8000/health
2. Check CORS origins in `app/main.py`:
   ```python
   allow_origins=["http://localhost:3000", "http://localhost:5173"]
   ```
3. Check `.env` in frontend:
   ```
   VITE_API_URL=http://localhost:8000
   ```

### Issue: GPU not detected
**Error:** `RuntimeError: no CUDA GPUs are available`

**Solution:**
```bash
# Check CUDA installation
python -c "import torch; print(torch.cuda.is_available())"

# If False:
# 1. Install NVIDIA drivers: https://www.nvidia.com/Download/driverDetails.aspx
# 2. Install CUDA Toolkit: https://developer.nvidia.com/cuda-toolkit
# 3. Reinstall PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue: MediaPipe import error
**Error:** `ModuleNotFoundError: No module named 'mediapipe'`

**Solution:**
```bash
# MediaPipe has platform-specific wheels
# Ensure exact version is installed:
pip install mediapipe==0.10.14

# If still issues, try:
pip uninstall mediapipe
pip install mediapipe==0.10.14 --no-cache-dir
```

## Performance Optimization

### Backend
- **GPU Acceleration:** Ensure CUDA is properly installed
- **Model Caching:** Already implemented (singleton pattern)
- **Batch Processing:** Future optimization (Phase 3)
- **Memory Management:** GPU cache cleared after inference

### Frontend
- **Code Splitting:** Use dynamic imports for large components
- **Image Optimization:** Use next-gen formats (AVIF, WebP)
- **Lazy Loading:** Videos loaded on-demand

## Deployment Preparation (Phase 5)

### Production Build

#### Frontend
```bash
cd frontend
npm run build

# Output in: frontend/dist/
```

#### Backend
```bash
# Use production ASGI server
pip install gunicorn uvicorn

# Run with gunicorn
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MediaPipe Documentation](https://mediapipe.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

---

**For architecture details, see [plan.md](./plan.md)**  
**For API documentation, see http://localhost:8000/docs**

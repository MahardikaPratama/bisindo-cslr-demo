# 📚 Documentation Index

Welcome to **BISINDO CSLR Demo**! This index helps you navigate all documentation.

---

## 🚀 Start Here

### New Users
👉 **[GETTING_STARTED.md](GETTING_STARTED.md)** — Quick start guide (2 minutes)
- CPU-only setup
- GPU setup
- First test run
- Common issues

### Existing Users
👉 **[README.md](README.md)** — Professional documentation
- Full feature list
- API endpoints
- Architecture overview
- Performance benchmarks

---

## ⚙️ Configuration & Setup

### CPU-Only Mode
📄 **[CPU_SETUP.md](CPU_SETUP.md)** — Detailed CPU configuration
- Step-by-step CPU setup
- Performance expectations (4-5 min per 1 min video)
- Optimization tips
- Troubleshooting

### GPU Mode (NVIDIA CUDA)
📄 **[.env.gpu](.env.gpu)** — GPU configuration file
- Ready-to-use GPU settings
- Copy with: `cp .env.gpu .env`

### CPU Mode
📄 **[.env.cpu](.env.cpu)** — CPU configuration file
- Ready-to-use CPU settings
- Copy with: `cp .env.cpu .env`

### All Configurations
📄 **[ENV_CONFIG.md](ENV_CONFIG.md)** — Complete configuration guide
- Side-by-side comparison
- Installation commands
- Switching between CPU/GPU
- Performance comparison

### Quick Comparison
📄 **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** — Cheat sheet
- CPU vs GPU at a glance
- Performance table
- Hardware recommendations
- Troubleshooting shortcuts

---

## 👨‍💻 Development

### Setup & Environment
📄 **[DEVELOPMENT.md](DEVELOPMENT.md)** — Development guide
- Backend setup (FastAPI)
- Frontend setup (React + Vite)
- Code organization
- Testing & debugging
- Production build

### Technical Architecture
📄 **[plan.md](plan.md)** — Complete architecture document (7000+ words)
- System design
- Data flow
- 15 sections covering all aspects
- Technical specifications

---

## 📋 File Structure

```
bisindo-cslr-demo/
├── 📘 GETTING_STARTED.md       ← Start here!
├── 📘 README.md                ← Full documentation
├── 📘 CPU_SETUP.md             ← CPU-only guide
├── 📘 QUICK_REFERENCE.md       ← CPU vs GPU cheat sheet
├── 📘 ENV_CONFIG.md            ← Configuration details
├── 📘 DEVELOPMENT.md           ← Dev setup & debugging
├── 📘 plan.md                  ← Technical architecture
├── 📘 INDEX.md                 ← This file
│
├── ⚙️ .env.example             ← Default config (auto-detect)
├── ⚙️ .env.cpu                 ← CPU-only config
├── ⚙️ .env.gpu                 ← GPU config
│
├── 🔧 app/                     ← Backend (FastAPI)
├── 🎨 frontend/                ← Frontend (React)
├── 🧪 tests/                   ← Unit tests
├── 📦 configs/                 ← Model configs
└── 📁 [other directories]
```

---

## 🎯 Quick Navigation

### By Use Case

**"I just want to run the app"**
→ [GETTING_STARTED.md](GETTING_STARTED.md)

**"I only have CPU"**
→ [CPU_SETUP.md](CPU_SETUP.md)

**"I want to compare CPU vs GPU"**
→ [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**"I want complete documentation"**
→ [README.md](README.md)

**"I want to develop/modify code"**
→ [DEVELOPMENT.md](DEVELOPMENT.md)

**"I want to understand the architecture"**
→ [plan.md](plan.md)

**"I need to configure environment"**
→ [ENV_CONFIG.md](ENV_CONFIG.md)

---

## 📊 Document Sizes & Content

| Document | Size | Best For |
|---|---|---|
| **GETTING_STARTED.md** | 5 min read | Quick start |
| **CPU_SETUP.md** | 10 min read | CPU users |
| **QUICK_REFERENCE.md** | 8 min read | Comparison |
| **README.md** | 20 min read | Overview |
| **DEVELOPMENT.md** | 15 min read | Developers |
| **ENV_CONFIG.md** | 12 min read | Configuration |
| **plan.md** | 30 min read | Deep dive |

---

## ✅ Typical User Journeys

### First-Time User (CPU)
1. Read: [GETTING_STARTED.md](GETTING_STARTED.md) (2 min)
2. Read: [CPU_SETUP.md](CPU_SETUP.md) (5 min)
3. Run: Follow setup steps
4. Test: Upload sample video

### First-Time User (GPU)
1. Read: [GETTING_STARTED.md](GETTING_STARTED.md) (2 min)
2. Read: [ENV_CONFIG.md](ENV_CONFIG.md) (5 min)
3. Run: Follow setup steps
4. Test: Upload sample video

### Returning User
1. Open: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. Copy: `cp .env.cpu .env` or `cp .env.gpu .env`
3. Run: Backend & frontend
4. Use: Web interface

### Developer
1. Read: [DEVELOPMENT.md](DEVELOPMENT.md)
2. Read: [plan.md](plan.md)
3. Clone & setup
4. Modify code

---

## 🔗 Links Between Documents

### Entry Points
- 🏠 **Home:** [GETTING_STARTED.md](GETTING_STARTED.md)
- 📚 **Main Docs:** [README.md](README.md)
- 🏗️ **Architecture:** [plan.md](plan.md)

### Configuration
- 💻 **CPU:** [CPU_SETUP.md](CPU_SETUP.md)
- ⚡ **GPU:** [ENV_CONFIG.md](ENV_CONFIG.md)
- 📋 **Compare:** [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Development
- 🔧 **Setup:** [DEVELOPMENT.md](DEVELOPMENT.md)
- 📝 **Configs:** [ENV_CONFIG.md](ENV_CONFIG.md)

---

## 🎓 Learning Path

### Beginner
```
GETTING_STARTED.md
    ↓
(Choose: CPU or GPU)
    ↓
CPU_SETUP.md OR ENV_CONFIG.md
    ↓
Run application
```

### Intermediate
```
README.md (Features & Architecture)
    ↓
Choose: CPU_SETUP.md OR ENV_CONFIG.md
    ↓
QUICK_REFERENCE.md (Performance comparison)
    ↓
Run and test
```

### Advanced
```
plan.md (Architecture deep dive)
    ↓
DEVELOPMENT.md (Code setup)
    ↓
Explore app/ and frontend/ directories
    ↓
Modify and contribute
```

---

## 🆘 Need Help?

### Setup Issues
- **"Can't decide CPU vs GPU?"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **"I only have CPU"** → [CPU_SETUP.md](CPU_SETUP.md)
- **"GPU not detected"** → [ENV_CONFIG.md](ENV_CONFIG.md) Troubleshooting section

### Running Issues
- **"Port already in use"** → [GETTING_STARTED.md](GETTING_STARTED.md#-common-issues)
- **"CUDA errors"** → [DEVELOPMENT.md](DEVELOPMENT.md#troubleshooting)
- **"Performance questions"** → [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Development Issues
- **"How to run tests?"** → [DEVELOPMENT.md](DEVELOPMENT.md#running-tests)
- **"Where is X code?"** → [plan.md](plan.md#-repository-structure)
- **"How to debug?"** → [DEVELOPMENT.md](DEVELOPMENT.md#debugging)

---

## 📱 Mobile/Quick Access

**On mobile?** Use [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

**In a hurry?** Use [GETTING_STARTED.md](GETTING_STARTED.md)

**Need specific config?** Use [ENV_CONFIG.md](ENV_CONFIG.md)

---

## 🔄 Documentation Updates

All documents are kept in sync:
- Configuration files reflect latest settings
- Examples match current implementation
- All paths are tested and verified

Last updated: **May 10, 2026**  
Version: **1.0.0**

---

## 📞 Quick Links

| What | Where |
|---|---|
| **Start Setup** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Features & API** | [README.md](README.md) |
| **CPU Setup** | [CPU_SETUP.md](CPU_SETUP.md) |
| **GPU Setup** | [ENV_CONFIG.md](ENV_CONFIG.md) |
| **Comparison** | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| **Development** | [DEVELOPMENT.md](DEVELOPMENT.md) |
| **Architecture** | [plan.md](plan.md) |

---

<div align="center">

**Choose your path:**

[🚀 GETTING STARTED](GETTING_STARTED.md) — [📚 FULL DOCS](README.md) — [🏗️ ARCHITECTURE](plan.md)

[💻 CPU SETUP](CPU_SETUP.md) — [⚡ GPU SETUP](ENV_CONFIG.md) — [📊 COMPARISON](QUICK_REFERENCE.md)

---

Happy sign language recognition! 🤟

</div>

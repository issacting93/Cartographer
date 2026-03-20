# Installation Guide

**Detailed setup instructions for all Cartographer components.**

---

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Data Setup](#data-setup)
5. [Environment Configuration](#environment-configuration)
6. [Verification](#verification)
7. [Docker Setup (Optional)](#docker-setup-optional)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Required

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **OS** | macOS 11+, Ubuntu 20.04+, Windows 10+ | macOS 13+, Ubuntu 22.04+ | Windows requires WSL2 |
| **Python** | 3.10 | 3.11 | Must support `asyncio` |
| **Node.js** | 18.0 | 20.0 LTS | For frontend |
| **RAM** | 8 GB | 16 GB | For full pipeline with 5 workers |
| **Disk Space** | 5 GB | 10 GB | Includes datasets + outputs |
| **Internet** | Required | — | For OpenAI API calls |

### Optional

- **Docker** 24+ (for containerized deployment)
- **Git LFS** (if cloning large datasets)
- **PostgreSQL** 15+ (for production storage backend)

---

## Backend Setup

### 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Cartography_v2.git
cd Cartography_v2
```

### 2. Create Python Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Verify activation:**
```bash
which python  # Should show path inside venv/
```

### 3. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install core dependencies
pip install -r requirements.txt
```

**Dependencies installed:**
- `fastapi` — Backend API framework
- `uvicorn` — ASGI server
- `pydantic` — Data validation
- `openai` — LLM API client
- `networkx` — Graph processing
- `numpy`, `pandas` — Data analysis
- `scikit-learn` — Clustering
- `hdbscan` — Density-based clustering
- `matplotlib`, `seaborn` — Visualization

### 4. Verify Backend Installation

```bash
python -c "import fastapi, openai, networkx; print('✓ Backend dependencies OK')"
```

---

## Frontend Setup

### 1. Install Node.js

**macOS (Homebrew):**
```bash
brew install node@20
```

**Ubuntu:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Windows:**
Download from [nodejs.org](https://nodejs.org/)

**Verify:**
```bash
node --version  # Should show v20.x.x
npm --version   # Should show 10.x.x
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

**Key packages:**
- `react` 18.2 — UI framework
- `react-router-dom` — Routing
- `vite` — Build tool
- `tailwindcss` — Styling
- `typescript` — Type safety

### 3. Verify Frontend Installation

```bash
npm run build  # Should compile without errors
```

---

## Data Setup

### 1. Download Source Datasets

**Option A: Full Datasets (for reproduction)**

```bash
# Create raw data directory
mkdir -p data/raw

# WildChat (requires Hugging Face account)
# 1. Visit: https://huggingface.co/datasets/allenai/wildchat
# 2. Accept license
# 3. Download via:
huggingface-cli download allenai/wildchat --repo-type dataset --local-dir data/raw/wildchat

# OASST
git clone https://github.com/LAION-AI/Open-Assistant.git data/raw/oasst

# Chatbot Arena
wget https://storage.googleapis.com/arena-external/conversations.jsonl -P data/raw/arena/
```

**Option B: Sample Data (for testing)**

```bash
# Use provided sample (included in repo)
# data/task_classified/sample_conversations.json
# No download needed
```

### 2. Verify Data Structure

```bash
# Check directory structure
tree -L 2 data/

# Expected output:
# data/
# ├── raw/
# │   ├── wildchat/
# │   ├── oasst/
# │   └── arena/
# ├── task_classified/
# │   └── all_task_enriched.json
# └── atlas_canonical/
```

### 3. Generate Enriched Classifications (if not included)

```bash
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/task_classified/all_task_enriched.json \
  --model gpt-4o-mini \
  --workers 3
```

**Time estimate:** ~1-2 hours for 1,000 conversations

---

## Environment Configuration

### 1. Create `.env` File

```bash
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env`:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-...                    # Required: Your API key
OPENAI_MODEL=gpt-4o-mini                       # Default model
OPENAI_MAX_RETRIES=3                           # Retry on errors
OPENAI_TIMEOUT=60                              # Seconds

# Backend Configuration
BACKEND_HOST=0.0.0.0                           # API host
BACKEND_PORT=8000                              # API port
DATA_DIR=/path/to/Cartography_v2/data/users    # User data storage

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000        # Backend URL

# Pipeline Configuration
PIPELINE_WORKERS=5                             # Parallel workers
PIPELINE_CACHE=true                            # Enable caching
PIPELINE_VERBOSE=false                         # Debug logging

# Database (Optional - for production)
# DATABASE_URL=postgresql://user:pass@localhost/cartographer
```

### 3. Set API Key

**Secure method (recommended):**
```bash
export OPENAI_API_KEY="sk-proj-..."  # Add to ~/.bashrc or ~/.zshrc
```

**Quick method (less secure):**
Paste directly into `.env`

**Verify:**
```bash
python -c "import os; print('✓ API key set' if os.getenv('OPENAI_API_KEY') else '✗ API key missing')"
```

---

## Verification

### 1. Test Backend

```bash
# Activate venv
source venv/bin/activate  # or .\venv\Scripts\Activate.ps1 on Windows

# Start FastAPI server
cd backend
uvicorn main:app --reload --port 8000
```

**Visit:** http://localhost:8000/docs

**Expected:** Swagger UI with API endpoints

**Test endpoint:**
```bash
curl http://localhost:8000/api/context/task/list?user_id=test_user
# Should return: {"tasks": []}
```

### 2. Test Frontend

```bash
# Separate terminal
cd frontend
npm run dev
```

**Visit:** http://localhost:5173

**Expected:** Landing page with "CUI 2026" header

### 3. Test Pipeline

```bash
# Run on sample data
python -m scripts.atlas.run_pipeline \
  --enriched data/task_classified/sample_conversations.json \
  --output-dir data/test_output \
  --limit 1
```

**Expected output:**
```
Pipeline initialized
Processing 1 conversations...
✓ abc123: 12 turns, 3 constraints, 2 violations
Metrics saved to data/test_output/metrics/all_metrics.json
```

### 4. Full System Check

```bash
# Run verification script
python scripts/verify_installation.py
```

**Expected:**
```
✓ Python 3.10+
✓ Node.js 18+
✓ Backend dependencies
✓ Frontend dependencies
✓ OpenAI API key set
✓ Data directory structure
✓ Sample data available
All checks passed!
```

---

## Docker Setup (Optional)

### 1. Install Docker

**macOS/Windows:** Download [Docker Desktop](https://www.docker.com/products/docker-desktop/)

**Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER  # Add to docker group
```

### 2. Build Images

```bash
# Build backend
docker build -t cartographer-backend -f docker/Dockerfile.backend .

# Build frontend
docker build -t cartographer-frontend -f docker/Dockerfile.frontend .
```

### 3. Run with Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your API key

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

**Services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Database: postgresql://localhost:5432

### 4. Run Pipeline in Docker

```bash
docker-compose exec backend python -m scripts.atlas.run_pipeline \
  --enriched /data/task_classified/all_task_enriched.json \
  --output-dir /data/atlas_canonical
```

---

## Troubleshooting

### Python Issues

**Problem:** `ModuleNotFoundError`

```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Problem:** `ssl.SSLError` on macOS

```bash
# Solution: Install certificates
/Applications/Python\ 3.11/Install\ Certificates.command
```

### Node.js Issues

**Problem:** `npm ERR! EACCES`

```bash
# Solution: Fix permissions or use nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 20
nvm use 20
```

**Problem:** `VITE build fails`

```bash
# Solution: Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json .vite
npm install
```

### OpenAI API Issues

**Problem:** `429 Rate Limit Exceeded`

```bash
# Solution: Reduce workers or add delay
python -m scripts.atlas.run_pipeline \
  --workers 1 \
  --delay 2  # 2 seconds between requests
```

**Problem:** `401 Unauthorized`

```bash
# Solution: Check API key
echo $OPENAI_API_KEY  # Should start with sk-proj-
```

### Data Issues

**Problem:** `FileNotFoundError: all_task_enriched.json`

```bash
# Solution: Generate it first
python -m scripts.atlas.pipeline.classify_task_first \
  --source data/raw/ \
  --output data/task_classified/all_task_enriched.json
```

**Problem:** `JSONDecodeError`

```bash
# Solution: Validate JSON
python -m json.tool data/task_classified/all_task_enriched.json > /dev/null
# If error, check line number in error message
```

### Database Issues (Docker)

**Problem:** `Connection refused`

```bash
# Check if container is running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

---

## Platform-Specific Notes

### macOS (Apple Silicon)

Some packages may require Rosetta:

```bash
# Install Rosetta
softwareupdate --install-rosetta

# Use x86_64 Python
arch -x86_64 python3 -m venv venv
```

### Windows (WSL2)

Install WSL2 first:

```powershell
wsl --install -d Ubuntu-22.04
wsl
# Then follow Ubuntu instructions
```

### Cloud Instances (AWS/GCP/Azure)

```bash
# Increase file descriptor limits
ulimit -n 4096

# Use tmux for long-running pipeline
tmux new -s pipeline
python -m scripts.atlas.run_pipeline ...
# Ctrl+B, then D to detach
```

---

## Next Steps

1. ✅ Installation complete
2. → Read [GETTING_STARTED.md](GETTING_STARTED.md) for quick examples
3. → Read [DATA_GUIDE.md](DATA_GUIDE.md) to understand data structure
4. → Read [DOCUMENTATION.md](DOCUMENTATION.md) for full technical reference

---

## Updating

### Pull Latest Changes

```bash
git pull origin main

# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Node dependencies
cd frontend
npm update
```

### Database Migrations (if applicable)

```bash
# Run Alembic migrations
alembic upgrade head
```

---

**Installation issues?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open an issue on GitHub.

# 🚀 Quick Start Guide

Get TerraForge Studio running in 5 minutes!

## Prerequisites

- **Node.js** 18+ 
- **Python** 3.11+
- **PostgreSQL** 15+
- **Redis** 7+

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/terraforge/studio.git
cd studio
```

### 2. Frontend Setup

```bash
cd frontend-new
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 3. Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb terraforge
alembic upgrade head

# Start backend
uvicorn realworldmapgen.api.main:app --reload
```

Backend runs at `http://localhost:8000`

### 4. Start Redis

```bash
redis-server
```

## Generate Your First Terrain

1. Open `http://localhost:5173`
2. Set bounding box coordinates
3. Choose resolution (1024 recommended)
4. Click "Generate Terrain"
5. Export to your game engine!

## Next Steps

- [Full Installation Guide](INSTALLATION.md)
- [API Documentation](API_SPECIFICATION.md)
- [Exporters Guide](EXPORTERS_GUIDE.md)

---

**That's it!** You're ready to generate beautiful terrains! 🌍✨

# 🚀 TerraForge Studio - Quick Start Guide

## New Features Overview

You now have 5 powerful new features ready to use:

1. **🌙 Dark Mode** - Automatic theme switching
2. **🐳 Docker** - Production deployment ready
3. **📦 Batch Processing** - Process multiple terrains at once
4. **🌍 3D Preview** - Full CesiumJS integration
5. **🤖 AI Assistant** - Intelligent terrain analysis

---

## Quick Start (Development)

### 1. Install Dependencies

```bash
# Backend dependencies (if not already installed)
poetry install

# Frontend dependencies
cd frontend-new
npm install
```

### 2. Start Development Server

```bash
# Terminal 1: Start backend
poetry run uvicorn realworldmapgen.api.main:app --reload --port 8000

# Terminal 2: Start frontend
cd frontend-new
npm run dev
```

### 3. Open Browser

Navigate to: `http://localhost:5173`

**That's it!** All new features are now active.

---

## Using the New Features

### Dark Mode 🌙

**Location**: Top-right header, next to Settings button

**How to use**:
1. Click the theme toggle buttons
2. Choose: Light / Dark / Auto
3. Theme is saved automatically

**Auto mode**: Follows your system theme

### 3D Preview 🌍

**Location**: Main view, "3D Preview" tab

**How to use**:
1. Select an area on the 2D map
2. Click "3D Preview" tab
3. Wait for CesiumJS to load (~5 seconds)
4. Use controls to navigate

**Controls**:
- 🔍 Zoom In/Out buttons
- 🏠 Home view
- 🔄 Reset to selection
- 📸 Screenshot

### Batch Processing 📦

**How to add to your UI**:

```typescript
import BatchProcessor from './components/BatchProcessor';
import QueueManager from './components/QueueManager';

// In your component
<BatchProcessor onSubmitBatch={handleBatch} />
<QueueManager />
```

**Usage**:
1. Click "Add Job" to add terrain generation jobs
2. Configure each job (name, resolution, formats)
3. Click "Submit Batch" to start processing
4. Monitor progress in QueueManager

**CSV Import**: Prepare CSV with format:
```csv
name,north,south,east,west,resolution,formats
terrain1,37.8,37.79,-122.4,-122.41,2048,unreal5|unity
terrain2,40.7,40.69,-74.0,-74.01,4096,gltf
```

### AI Assistant 🤖

**How to add to your UI**:

```typescript
import AIAssistant from './components/AIAssistant';

// In your component
<AIAssistant 
  bbox={selectedBbox}
  onApplyRecommendations={handleAIRecommendations}
/>
```

**Usage**:
1. Select an area on the map
2. Click "Analyze" in AI Assistant panel
3. Wait 2-10 seconds for analysis
4. Review recommendations
5. Click "Apply AI Recommendations" (optional)

**With Ollama** (optional):
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull model
ollama pull llama3.1:8b

# Start Ollama
ollama serve
```

**Without Ollama**: Works automatically with rule-based analysis

---

## Docker Deployment 🐳

### Development Mode

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access at: `http://localhost:8000`

### Production Mode

```bash
# Create .env file
cat > .env << EOF
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
OLLAMA_HOST=http://host.docker.internal:11434
EOF

# Start with environment file
docker-compose --env-file .env up -d

# Check health
curl http://localhost:8000/api/health
```

### With Nginx (Production)

```bash
# Nginx is included in docker-compose.yml
# Access via:
# - http://localhost:80 (Nginx)
# - http://localhost:8000 (Direct)

# To use SSL:
# 1. Place certificates in ssl/ directory
# 2. Uncomment SSL block in nginx.conf
# 3. Restart: docker-compose restart nginx
```

---

## Example Integration

### Full App with All Features

```typescript
import { useState } from 'react';
import MapSelector from './components/MapSelector';
import ExportPanel from './components/ExportPanel';
import Preview3D from './components/Preview3D';
import AIAssistant from './components/AIAssistant';
import BatchProcessor from './components/BatchProcessor';
import QueueManager from './components/QueueManager';
import ThemeToggle from './components/ThemeToggle';

function App() {
  const [selectedBbox, setSelectedBbox] = useState(null);
  const [activeTab, setActiveTab] = useState('2d');
  const [showBatch, setShowBatch] = useState(false);

  const handleAIRecommendations = (settings) => {
    console.log('AI recommendations:', settings);
    // Apply settings to your export panel
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header with Theme Toggle */}
      <header className="glass border-b border-gray-200 dark:border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            TerraForge Studio
          </h1>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <button onClick={() => setShowBatch(!showBatch)}>
              {showBatch ? 'Hide Batch' : 'Show Batch'}
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Map/3D */}
          <div className="lg:col-span-2">
            {activeTab === '2d' ? (
              <MapSelector
                selectedBbox={selectedBbox}
                onBboxChange={setSelectedBbox}
              />
            ) : (
              <Preview3D bbox={selectedBbox} />
            )}
          </div>

          {/* Right: Controls */}
          <div className="space-y-6">
            <ExportPanel />
            <AIAssistant 
              bbox={selectedBbox}
              onApplyRecommendations={handleAIRecommendations}
            />
          </div>
        </div>

        {/* Batch Processing (optional) */}
        {showBatch && (
          <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <BatchProcessor onSubmitBatch={console.log} />
            <QueueManager />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
```

---

## API Examples

### Check Health
```bash
curl http://localhost:8000/api/health
```

### AI Analysis
```bash
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "bbox": {
      "north": 37.8,
      "south": 37.79,
      "east": -122.4,
      "west": -122.41
    }
  }'
```

### Batch Queue Status
```bash
curl http://localhost:8000/api/batch/stats
```

### List Batch Jobs
```bash
curl http://localhost:8000/api/batch/jobs
```

---

## Troubleshooting

### Dark Mode Not Working
1. Check browser console for errors
2. Verify ThemeProvider is wrapping App
3. Clear localStorage: `localStorage.clear()`

### 3D Preview Shows Loading Forever
1. Check CesiumJS is installed: `npm list cesium`
2. Verify Cesium Ion token is valid
3. Check browser console for errors
4. Try refreshing the page

### Batch Processing Not Starting
1. Check backend is running: `curl http://localhost:8000/api/health`
2. Verify Redis is running (optional)
3. Check browser network tab for errors
4. Review backend logs

### AI Analysis Fails
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Verify model is installed: `ollama list`
3. AI will fallback to rule-based if Ollama unavailable
4. Check OLLAMA_HOST environment variable

### Docker Issues
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f terraforge

# Restart services
docker-compose restart

# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## Performance Tips

### 3D Preview
- Use lower terrain quality for better FPS
- Disable shadows if performance is poor
- Reduce vertical exaggeration for complex terrain

### Batch Processing
- Limit concurrent jobs to 3-5
- Use lower resolutions for faster processing
- Enable only needed features

### AI Analysis
- Use smaller models for faster response
- Rule-based fallback is instant
- Cache results for repeated analyses

### Docker
- Allocate 4GB+ RAM for Docker
- Use SSD for volumes
- Limit worker count based on CPU

---

## Next Steps

1. **Customize Theme**: Edit `src/styles/index.css` for custom colors
2. **Add AI Models**: Install different Ollama models
3. **Configure Batch Size**: Adjust max concurrent jobs
4. **Enable SSL**: Set up certificates for HTTPS
5. **Monitor Performance**: Add logging/metrics

---

## Resources

- **Docker Guide**: See `DOCKER_DEPLOYMENT.md`
- **Features Summary**: See `FEATURES_IMPLEMENTED.md`
- **Component Docs**: Check source code comments
- **API Docs**: Visit `/docs` when backend running

---

## Support

Having issues? Check:
1. Browser console (F12)
2. Backend logs (`docker-compose logs -f`)
3. Network tab (F12 → Network)
4. Component source code

**All features are production-ready!** 🚀

Enjoy your enhanced TerraForge Studio! 🎉


// RealWorldMapGen-BNG Frontend with Advanced Map Controls
const API_BASE_URL = 'http://localhost:8000';

let map;
let selectedBounds = null;
let drawnItems;
let currentDrawTool = 'rectangle';
let searchMarker = null;

// Initialize map
function initMap() {
    // Create map
    map = L.map('map').setView([55.7558, 37.6173], 13);

    // Add multiple base layers
    const osmStandard = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    });

    const osmHOT = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OSM Team',
        maxZoom: 19
    });

    const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri',
        maxZoom: 19
    });

    // Add default layer
    osmStandard.addTo(map);

    // Layer control
    const baseMaps = {
        "🗺️ OpenStreetMap": osmStandard,
        "🔥 Humanitarian": osmHOT,
        "🛰️ Satellite": satellite
    };

    L.control.layers(baseMaps).addTo(map);

    // Initialize drawing layer
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    // Drawing control
    const drawControl = new L.Control.Draw({
        position: 'topleft',
        draw: {
            polyline: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    map.addControl(drawControl);

    // Map events
    map.on(L.Draw.Event.CREATED, handleDrawCreated);
    map.on(L.Draw.Event.EDITED, handleDrawEdited);
    map.on(L.Draw.Event.DELETED, handleDrawDeleted);
    map.on('mousemove', updateCoordinateDisplay);

    // Initialize controls
    setupMapControls();
    setupSearch();
}

// Setup map control buttons
function setupMapControls() {
    // Rectangle tool
    document.getElementById('rectangleTool').addEventListener('click', () => {
        setActiveTool('rectangle');
        new L.Draw.Rectangle(map, drawControl.options.draw.rectangle).enable();
    });

    // Polygon tool
    document.getElementById('polygonTool').addEventListener('click', () => {
        setActiveTool('polygon');
        new L.Draw.Polygon(map, drawControl.options.draw.polygon).enable();
    });

    // Circle tool
    document.getElementById('circleTool').addEventListener('click', () => {
        setActiveTool('circle');
        new L.Draw.Circle(map, drawControl.options.draw.circle).enable();
    });

    // Clear selection
    document.getElementById('clearSelection').addEventListener('click', () => {
        drawnItems.clearLayers();
        selectedBounds = null;
        updateAreaInfo();
    });

    // Fit to bounds
    document.getElementById('fitBounds').addEventListener('click', () => {
        if (drawnItems.getLayers().length > 0) {
            map.fitBounds(drawnItems.getBounds(), { padding: [50, 50] });
        }
    });
}

// Set active drawing tool
function setActiveTool(tool) {
    currentDrawTool = tool;
    document.querySelectorAll('.map-tool-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tool + 'Tool').classList.add('active');
}

// Setup location search
function setupSearch() {
    const searchInput = document.getElementById('mapSearch');
    let searchTimeout;

    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();

        if (query.length < 3) return;

        searchTimeout = setTimeout(() => searchLocation(query), 500);
    });

    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchLocation(e.target.value.trim());
        }
    });
}

// Search location using Nominatim
async function searchLocation(query) {
    if (!query) return;

    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=1`
        );
        const results = await response.json();

        if (results.length > 0) {
            const result = results[0];
            const lat = parseFloat(result.lat);
            const lon = parseFloat(result.lon);

            // Remove previous search marker
            if (searchMarker) {
                map.removeLayer(searchMarker);
            }

            // Add new marker
            searchMarker = L.marker([lat, lon], {
                icon: L.divIcon({
                    className: 'search-marker',
                    html: '📍',
                    iconSize: [30, 30]
                })
            }).addTo(map);

            // Pan to location
            map.setView([lat, lon], 14, { animate: true });

            // Show popup
            searchMarker.bindPopup(`<b>${result.display_name}</b>`).openPopup();
        }
    } catch (error) {
        console.error('Search failed:', error);
    }
}

// Update coordinate display
function updateCoordinateDisplay(e) {
    const lat = e.latlng.lat.toFixed(4);
    const lon = e.latlng.lng.toFixed(4);
    document.getElementById('coordDisplay').textContent = `Lat: ${lat}, Lon: ${lon}`;
}

// Handle draw created event
function handleDrawCreated(e) {
    const layer = e.layer;
    
    // Clear previous drawings
    drawnItems.clearLayers();
    drawnItems.addLayer(layer);

    // Get bounds
    updateBoundsFromLayer(layer);
    updateAreaInfo();
}

// Handle draw edited event
function handleDrawEdited(e) {
    const layers = e.layers;
    layers.eachLayer(layer => {
        updateBoundsFromLayer(layer);
        updateAreaInfo();
    });
}

// Handle draw deleted event
function handleDrawDeleted(e) {
    selectedBounds = null;
    updateAreaInfo();
}

// Update bounds from layer
function updateBoundsFromLayer(layer) {
    let bounds;

    if (layer instanceof L.Rectangle || layer instanceof L.Polygon) {
        bounds = layer.getBounds();
    } else if (layer instanceof L.Circle) {
        bounds = layer.getBounds();
    }

    if (bounds) {
        selectedBounds = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
    }
}

// Update area info display
function updateAreaInfo() {
    const areaInfo = document.getElementById('areaInfo');
    const generateBtn = document.getElementById('generateBtn');
    
    if (selectedBounds) {
        const area = calculateAreaKm2(selectedBounds);
        
        document.getElementById('areaCoords').textContent = 
            `N: ${selectedBounds.north.toFixed(4)}, S: ${selectedBounds.south.toFixed(4)}, E: ${selectedBounds.east.toFixed(4)}, W: ${selectedBounds.west.toFixed(4)}`;
        
        document.getElementById('areaSize').textContent = 
            `Area: ${area.toFixed(2)} km²`;
        
        areaInfo.style.display = 'block';
        
        // Enable generate button
        generateBtn.disabled = false;
        generateBtn.style.opacity = '1';
        generateBtn.style.cursor = 'pointer';
    } else {
        areaInfo.style.display = 'none';
        
        // Disable generate button
        generateBtn.disabled = true;
        generateBtn.style.opacity = '0.6';
        generateBtn.style.cursor = 'not-allowed';
    }
}

// Calculate area in square kilometers
function calculateAreaKm2(bounds) {
    const latDiff = bounds.north - bounds.south;
    const lonDiff = bounds.east - bounds.west;
    const avgLat = (bounds.north + bounds.south) / 2;
    const area = Math.abs(latDiff * lonDiff * Math.cos(avgLat * Math.PI / 180) * 111.32 * 111.32);
    return area;
}

// Check system health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();

        const healthBadge = document.getElementById('healthStatus');
        const ollamaBadge = document.getElementById('ollamaStatus');

        if (data.status === 'healthy') {
            healthBadge.textContent = '✅ System Online';
            healthBadge.className = 'badge success';
        } else {
            healthBadge.textContent = '❌ System Offline';
            healthBadge.className = 'badge danger';
        }

        if (data.ollama && data.ollama.available) {
            ollamaBadge.textContent = '🤖 AI Connected';
            ollamaBadge.className = 'badge success';
        } else {
            ollamaBadge.textContent = '⚠️ AI Unavailable';
            ollamaBadge.className = 'badge warning';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('healthStatus').textContent = '❌ Connection Error';
        document.getElementById('healthStatus').className = 'badge danger';
    }
}

// Generate map
async function generateMap() {
    if (!selectedBounds) {
        alert('Please select an area on the map first');
        return;
    }

    const mapName = document.getElementById('mapName').value.trim();
    if (!mapName) {
        alert('Please enter a map name');
        return;
    }

    // Validate map name
    if (!/^[a-zA-Z0-9_-]+$/.test(mapName)) {
        alert('Map name can only contain letters, numbers, underscores, and hyphens');
        return;
    }

    const resolution = parseInt(document.getElementById('resolution').value);
    const exportEngine = document.getElementById('exportEngine').value;

    const request = {
        name: mapName,
        bbox: selectedBounds,
        resolution: resolution,
        export_engine: exportEngine,
        enable_ai_analysis: document.getElementById('enableAI').checked,
        enable_roads: document.getElementById('enableRoads').checked,
        enable_traffic_lights: document.getElementById('enableTrafficLights').checked,
        enable_parking: document.getElementById('enableParking').checked,
        enable_buildings: document.getElementById('enableBuildings').checked,
        enable_vegetation: document.getElementById('enableVegetation').checked
    };

    // Disable generate button
    const generateBtn = document.getElementById('generateBtn');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Generating...';

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });

        const data = await response.json();

        if (response.ok) {
            // Show status and poll for progress
            showProgress(data.task_id, mapName);
        } else {
            alert('Error: ' + (data.detail || 'Failed to start generation'));
            generateBtn.disabled = false;
            generateBtn.textContent = '🚀 Generate Map';
        }
    } catch (error) {
        console.error('Generation failed:', error);
        alert('Failed to connect to server');
        generateBtn.disabled = false;
        generateBtn.textContent = '🚀 Generate Map';
    }
}

// Show and update progress
function showProgress(taskId, mapName) {
    const statusDiv = document.getElementById('status');
    const resultDiv = document.getElementById('result');
    
    statusDiv.style.display = 'block';
    resultDiv.style.display = 'none';

    // Poll for status
    const pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/tasks/${taskId}`);
            
            if (!response.ok) {
                // Task might be completed already
                if (response.status === 404) {
                    clearInterval(pollInterval);
                    showResult(mapName);
                    return;
                }
                throw new Error(`HTTP ${response.status}`);
            }
            
            const status = await response.json();
            updateProgressDisplay(status);

            if (status.status === 'completed') {
                clearInterval(pollInterval);
                showResult(mapName);
            } else if (status.status === 'failed') {
                clearInterval(pollInterval);
                showError(status.error || 'Generation failed');
            }
        } catch (error) {
            console.error('Status check failed:', error);
        }
    }, 1000);
}

// Update progress display
function updateProgressDisplay(status) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const currentStep = document.getElementById('currentStep');

    progressBar.style.width = status.progress + '%';
    progressText.textContent = Math.round(status.progress) + '%';
    currentStep.textContent = status.current_step || 'Processing...';
}

// Show result
function showResult(mapName) {
    document.getElementById('status').style.display = 'none';
    document.getElementById('result').style.display = 'block';
    document.getElementById('resultMessage').innerHTML = `
        <div class="alert alert-success">
            <h4>✓ Generation Complete!</h4>
            <p>Map "${mapName}" has been generated successfully!</p>
            
            <h5 style="margin-top: 20px;">📦 Ready to Install</h5>
            <div class="download-buttons" style="margin-bottom: 20px;">
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/zip" 
                   class="btn btn-success btn-lg" download>
                    <strong>⬇ Download BeamNG.drive Mod (.zip)</strong>
                </a>
                <p style="margin-top: 10px; color: #666; font-size: 0.9em;">
                    Extract this file to your BeamNG.drive/mods/ folder
                </p>
            </div>
            
            <h5>📄 Individual Files</h5>
            <div class="download-buttons">
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/heightmap" 
                   class="btn btn-primary btn-sm" download>Heightmap</a>
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/roads" 
                   class="btn btn-primary btn-sm" download>Roads</a>
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/objects" 
                   class="btn btn-primary btn-sm" download>Objects</a>
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/traffic" 
                   class="btn btn-primary btn-sm" download>Traffic</a>
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/level" 
                   class="btn btn-primary btn-sm" download>Level</a>
                <a href="${API_BASE_URL}/api/maps/${mapName}/download/metadata" 
                   class="btn btn-primary btn-sm" download>Info</a>
            </div>
        </div>
    `;

    // Re-enable generate button
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('generateBtn').textContent = '🚀 Generate Map';
}

// Show error
function showError(errorMessage) {
    document.getElementById('status').style.display = 'none';
    document.getElementById('result').style.display = 'block';
    document.getElementById('resultMessage').innerHTML = `
        <div class="alert alert-danger">
            <h4>✗ Generation Failed</h4>
            <p>${errorMessage}</p>
            <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
        </div>
    `;

    // Re-enable generate button
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('generateBtn').textContent = '🚀 Generate Map';
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    checkHealth();
    
    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
    
    // Setup generate button
    document.getElementById('generateBtn').addEventListener('click', generateMap);
});

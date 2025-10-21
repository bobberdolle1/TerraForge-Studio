// RealWorldMapGen-BNG Frontend Application

const API_BASE_URL = 'http://localhost:8000';

let map;
let drawnItems;
let selectedBounds = null;

// Initialize map
function initMap() {
    map = L.map('map').setView([37.7749, -122.4194], 12); // San Francisco default

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Initialize draw controls
    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);

    const drawControl = new L.Control.Draw({
        draw: {
            rectangle: {
                shapeOptions: {
                    color: '#667eea',
                    weight: 3,
                    fillOpacity: 0.2
                }
            },
            polygon: false,
            polyline: false,
            circle: false,
            marker: false,
            circlemarker: false
        },
        edit: {
            featureGroup: drawnItems,
            remove: true
        }
    });
    map.addControl(drawControl);

    // Handle rectangle drawn
    map.on(L.Draw.Event.CREATED, function (event) {
        const layer = event.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        
        const bounds = layer.getBounds();
        selectedBounds = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        };
        
        updateBboxInfo();
        document.getElementById('generateBtn').disabled = false;
    });

    // Handle rectangle edited/deleted
    map.on(L.Draw.Event.EDITED, function (event) {
        const layers = event.layers;
        layers.eachLayer(function (layer) {
            const bounds = layer.getBounds();
            selectedBounds = {
                north: bounds.getNorth(),
                south: bounds.getSouth(),
                east: bounds.getEast(),
                west: bounds.getWest()
            };
            updateBboxInfo();
        });
    });

    map.on(L.Draw.Event.DELETED, function () {
        selectedBounds = null;
        updateBboxInfo();
        document.getElementById('generateBtn').disabled = true;
    });
}

// Update bounding box information display
function updateBboxInfo() {
    const bboxCoords = document.getElementById('bboxCoords');
    const bboxArea = document.getElementById('bboxArea');

    if (selectedBounds) {
        bboxCoords.innerHTML = `
            North: ${selectedBounds.north.toFixed(5)}<br>
            South: ${selectedBounds.south.toFixed(5)}<br>
            East: ${selectedBounds.east.toFixed(5)}<br>
            West: ${selectedBounds.west.toFixed(5)}
        `;

        const area = calculateAreaKm2(selectedBounds);
        bboxArea.textContent = `Area: ${area.toFixed(2)} km²`;
    } else {
        bboxCoords.textContent = 'No area selected';
        bboxArea.textContent = '';
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

        document.getElementById('healthStatus').textContent = 
            data.status === 'healthy' ? '✓ Online' : '✗ Offline';
        document.getElementById('healthStatus').style.background = 
            data.status === 'healthy' ? '#28a745' : '#dc3545';

        document.getElementById('ollamaStatus').textContent = 
            data.ollama.available ? '✓ Connected' : '✗ Not Available';
        document.getElementById('ollamaStatus').style.background = 
            data.ollama.available ? '#28a745' : '#ffc107';
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('healthStatus').textContent = '✗ Error';
        document.getElementById('healthStatus').style.background = '#dc3545';
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

    // Validate map name (alphanumeric, underscores, hyphens only)
    if (!/^[a-zA-Z0-9_-]+$/.test(mapName)) {
        alert('Map name can only contain letters, numbers, underscores, and hyphens');
        return;
    }

    const request = {
        name: mapName,
        bbox: selectedBounds,
        resolution: parseInt(document.getElementById('resolution').value),
        enable_ai_analysis: document.getElementById('enableAI').checked,
        enable_roads: document.getElementById('enableRoads').checked,
        enable_traffic_lights: document.getElementById('enableTrafficLights').checked,
        enable_parking: document.getElementById('enableParking').checked,
        enable_buildings: document.getElementById('enableBuildings').checked,
        enable_vegetation: document.getElementById('enableVegetation').checked
    };

    // Disable generate button
    document.getElementById('generateBtn').disabled = true;
    document.getElementById('generateBtn').textContent = 'Generating...';

    // Show status panel
    document.getElementById('status').style.display = 'block';
    document.getElementById('result').style.display = 'none';

    try {
        const response = await fetch(`${API_BASE_URL}/api/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const status = await response.json();
        
        // For demo purposes, simulate progress
        // In production, you would poll the status endpoint
        simulateProgress(mapName);

    } catch (error) {
        console.error('Generation error:', error);
        alert(`Error: ${error.message}`);
        document.getElementById('generateBtn').disabled = false;
        document.getElementById('generateBtn').textContent = 'Generate Map';
        document.getElementById('status').style.display = 'none';
    }
}

// Simulate generation progress (in production, poll the status endpoint)
function simulateProgress(mapName) {
    let progress = 0;
    const steps = [
        'Extracting OpenStreetMap data',
        'Analyzing terrain with AI',
        'Generating heightmap',
        'Optimizing infrastructure placement',
        'Exporting to BeamNG.drive format'
    ];
    let currentStep = 0;

    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 100) progress = 100;

        document.getElementById('progressFill').style.width = progress + '%';
        document.getElementById('statusText').textContent = `Progress: ${progress.toFixed(0)}%`;

        if (progress >= 20 * (currentStep + 1) && currentStep < steps.length) {
            document.getElementById('statusStep').textContent = steps[currentStep];
            currentStep++;
        }

        if (progress >= 100) {
            clearInterval(interval);
            showResult(mapName);
        }
    }, 500);
}

// Show generation result
function showResult(mapName) {
    document.getElementById('status').style.display = 'none';
    document.getElementById('result').style.display = 'block';
    document.getElementById('resultMessage').textContent = 
        `Map "${mapName}" has been generated successfully!`;

    // Create download links
    const downloadLinks = document.getElementById('downloadLinks');
    downloadLinks.innerHTML = `
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/heightmap" download>
            📊 Download Heightmap
        </a>
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/roads" download>
            🛣️ Download Roads Data
        </a>
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/objects" download>
            🏢 Download Objects Data
        </a>
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/traffic" download>
            🚦 Download Traffic Data
        </a>
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/metadata" download>
            📋 Download Metadata
        </a>
        <a href="${API_BASE_URL}/api/maps/${mapName}/download/level" download>
            🎮 Download Level JSON
        </a>
    `;

    // Re-enable generate button
    document.getElementById('generateBtn').disabled = false;
    document.getElementById('generateBtn').textContent = 'Generate Map';
}

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    checkHealth();

    // Set up generate button
    document.getElementById('generateBtn').addEventListener('click', generateMap);

    // Check health every 30 seconds
    setInterval(checkHealth, 30000);
});

/**
 * TerraForge Studio - Main Application
 */

import { useState, useEffect } from 'react';
import { Globe, Settings, Download, Map, Box } from 'lucide-react';
import MapSelector from './components/MapSelector';
import ExportPanel from './components/ExportPanel';
import StatusMonitor from './components/StatusMonitor';
import Preview3D from './components/Preview3D';
import { terraforgeApi } from './services/api';
import type { BoundingBox, ExportFormat, ElevationSource, GenerationStatus } from './types';

function App() {
  const [selectedBbox, setSelectedBbox] = useState<BoundingBox | null>(null);
  const [activeTab, setActiveTab] = useState<'2d' | '3d'>('2d');
  const [currentTask, setCurrentTask] = useState<GenerationStatus | null>(null);
  const [appHealth, setAppHealth] = useState<any>(null);

  // Check API health on startup
  useEffect(() => {
    terraforgeApi.getHealth()
      .then(health => setAppHealth(health))
      .catch(console.error);
  }, []);

  const handleGenerateTerrain = async (config: {
    name: string;
    resolution: number;
    exportFormats: ExportFormat[];
    elevationSource: ElevationSource;
    enableRoads: boolean;
    enableBuildings: boolean;
    enableWeightmaps: boolean;
  }) => {
    if (!selectedBbox) {
      alert('Please select an area on the map first');
      return;
    }

    try {
      const status = await terraforgeApi.generateTerrain({
        bbox: selectedBbox,
        name: config.name,
        resolution: config.resolution,
        export_formats: config.exportFormats,
        elevation_source: config.elevationSource,
        enable_roads: config.enableRoads,
        enable_buildings: config.enableBuildings,
        enable_weightmaps: config.enableWeightmaps,
        enable_vegetation: true,
        enable_water_bodies: true,
      });

      setCurrentTask(status);

      // Poll for status updates
      const pollInterval = setInterval(async () => {
        const updated = await terraforgeApi.getStatus(status.task_id);
        setCurrentTask(updated);

        if (updated.status === 'completed' || updated.status === 'failed') {
          clearInterval(pollInterval);
        }
      }, 2000);

    } catch (error) {
      console.error('Generation failed:', error);
      alert('Failed to start terrain generation');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="glass border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Globe className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">TerraForge Studio</h1>
                <p className="text-sm text-gray-600">
                  Professional 3D Terrain Generator {appHealth?.version && `v${appHealth.version}`}
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                {appHealth?.data_sources && (
                  <span>
                    {appHealth.data_sources.available.length} / {appHealth.data_sources.total} sources available
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Map & 3D Preview */}
          <div className="lg:col-span-2 space-y-6">
            {/* Tab Switcher */}
            <div className="glass rounded-lg p-2 flex space-x-2">
              <button
                onClick={() => setActiveTab('2d')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md transition ${
                  activeTab === '2d'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Map className="w-5 h-5" />
                <span>2D Map Selector</span>
              </button>
              <button
                onClick={() => setActiveTab('3d')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md transition ${
                  activeTab === '3d'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Box className="w-5 h-5" />
                <span>3D Preview</span>
              </button>
            </div>

            {/* Map or 3D View */}
            <div className="glass rounded-lg overflow-hidden shadow-lg" style={{ height: '600px' }}>
              {activeTab === '2d' ? (
                <MapSelector
                  selectedBbox={selectedBbox}
                  onBboxChange={setSelectedBbox}
                />
              ) : (
                <Preview3D bbox={selectedBbox} />
              )}
            </div>
          </div>

          {/* Right Panel - Controls & Status */}
          <div className="space-y-6">
            {/* Export Configuration */}
            <div className="glass rounded-lg p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Export Configuration
              </h2>
              <ExportPanel
                onGenerate={handleGenerateTerrain}
                disabled={!selectedBbox}
              />
            </div>

            {/* Generation Status */}
            {currentTask && (
              <div className="glass rounded-lg p-6 shadow-lg">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <Download className="w-5 h-5 mr-2" />
                  Generation Status
                </h2>
                <StatusMonitor status={currentTask} />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-sm text-gray-600">
        <p>
          TerraForge Studio - Professional Cross-Platform 3D Terrain Generator
        </p>
        <p className="mt-1">
          Supports Unreal Engine 5, Unity, GLTF, and GeoTIFF
        </p>
      </footer>
    </div>
  );
}

export default App;


/**
 * TerraForge Studio - Main Application
 */

import { useState, useEffect, useRef } from 'react';
import { Globe, Settings as SettingsIcon, Download, Map, Box, History, Database, Share2 } from 'lucide-react';
import MapSelector from './components/MapSelector';
import ExportPanel from './components/ExportPanel';
import StatusMonitor from './components/StatusMonitor';
import Preview3D from './components/Preview3D';
import SettingsPage from './components/Settings/SettingsPage';
import SetupWizard from './components/SetupWizard';
import ThemeToggle from './components/ThemeToggle';
import GenerationHistory from './components/GenerationHistory';
import CacheManager from './components/CacheManager';
import ShareDialog from './components/ShareDialog';
import ShareManager from './components/ShareManager';
import MobileNav from './components/MobileNav';
import { terraforgeApi } from './services/api';
import { settingsApi } from './services/settings-api';
import { notify } from './utils/toast';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useWebSocket } from './hooks/useWebSocket';
import { useIsMobile } from './hooks/useMediaQuery';
import { historyStorage } from './utils/history-storage';
import type { BoundingBox, ExportFormat, ElevationSource, GenerationStatus } from './types';
import type { GenerationHistoryItem } from './types/history';

function App() {
  const [selectedBbox, setSelectedBbox] = useState<BoundingBox | null>(null);
  const [activeTab, setActiveTab] = useState<'2d' | '3d'>('2d');
  const [currentTask, setCurrentTask] = useState<GenerationStatus | null>(null);
  const [appHealth, setAppHealth] = useState<any>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [showWizard, setShowWizard] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showCache, setShowCache] = useState(false);
  const [showShare, setShowShare] = useState(false);
  const [showShareManager, setShowShareManager] = useState(false);
  const [wsUrl, setWsUrl] = useState<string | null>(null);
  const generationStartTime = useRef<number>(0);
  
  // Mobile detection
  const isMobile = useIsMobile();

  // WebSocket connection for live updates
  useWebSocket(wsUrl, {
    onMessage: (data) => {
      if (data.type === 'status_update') {
        setCurrentTask({
          task_id: data.task_id,
          status: data.status,
          progress: data.progress,
          current_step: data.current_step,
          message: data.message,
          error: data.error,
          download_url: data.download_url,
        });

        // Handle completion/failure
        if (data.status === 'completed') {
          notify.success('Terrain generation completed!');
          saveToHistory(data, 'completed', data.thumbnail_base64);
        } else if (data.status === 'failed') {
          notify.error('Terrain generation failed');
          saveToHistory(data, 'failed');
        }
      }
    },
    onOpen: () => {
      notify.info('Connected to live updates');
    },
    onClose: () => {
      console.log('WebSocket connection closed');
    },
    reconnect: true,
  });

  // Check API health and first run on startup
  useEffect(() => {
    Promise.all([
      terraforgeApi.getHealth(),
      settingsApi.checkFirstRun()
    ]).then(([health, firstRun]) => {
      setAppHealth(health);
      setShowWizard(firstRun.show_wizard);
    }).catch(console.error);
  }, []);

  // Helper function to save generation to history
  const saveToHistory = (data: any, status: 'completed' | 'failed', thumbnail?: string) => {
    if (!selectedBbox || !currentTask) return;

    const duration = Date.now() - generationStartTime.current;
    const historyItem: GenerationHistoryItem = {
      id: data.task_id,
      timestamp: Date.now(),
      name: currentTask.current_step || 'terrain',
      bbox: selectedBbox,
      config: {
        resolution: 2048, // These should come from the actual config
        exportFormats: [],
        elevationSource: 'auto',
        enableRoads: true,
        enableBuildings: true,
        enableWeightmaps: true,
      },
      status,
      downloadUrl: data.download_url,
      thumbnail: thumbnail,
      stats: {
        duration,
      },
    };
    historyStorage.add(historyItem);
  };

  // Keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+g': () => {
      // Trigger generation if export panel is visible
      if (selectedBbox) {
        notify.info('Press Generate button to start (Ctrl+G shortcut active)');
      } else {
        notify.error('Please select an area on the map first');
      }
    },
    'ctrl+d': () => {
      // Toggle theme (will be implemented when we import useTheme)
      const event = new CustomEvent('toggle-theme');
      window.dispatchEvent(event);
      notify.info('Theme toggled');
    },
    'ctrl+3': () => {
      // Toggle to 3D view
      setActiveTab('3d');
      notify.info('Switched to 3D Preview');
    },
    'ctrl+2': () => {
      // Toggle to 2D view
      setActiveTab('2d');
      notify.info('Switched to 2D Map');
    },
    'ctrl+s': () => {
      // Open settings
      setShowSettings(true);
    },
    'ctrl+h': () => {
      // Open history
      setShowHistory(true);
    },
    'ctrl+shift+c': () => {
      // Open cache manager
      setShowCache(true);
    },
    'ctrl+shift+s': () => {
      // Open share manager
      setShowShareManager(true);
    },
    'escape': () => {
      // Close modals
      if (showSettings) setShowSettings(false);
      if (showWizard) setShowWizard(false);
      if (showHistory) setShowHistory(false);
      if (showCache) setShowCache(false);
      if (showShare) setShowShare(false);
      if (showShareManager) setShowShareManager(false);
    },
  });

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
      notify.error('Please select an area on the map first');
      return;
    }

    const loadingToast = notify.loading('Starting terrain generation...');
    generationStartTime.current = Date.now();

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
      notify.dismiss(loadingToast);
      notify.success(`Generation started: ${config.name}`);

      // Connect to WebSocket for real-time updates
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsBaseUrl = `${protocol}//${window.location.hostname}:8000`;
      setWsUrl(`${wsBaseUrl}/ws/generation/${status.task_id}`);

    } catch (error) {
      console.error('Generation failed:', error);
      notify.dismiss(loadingToast);
      notify.error('Failed to start terrain generation');
    }
  };

  const handleRepeatGeneration = (item: GenerationHistoryItem) => {
    setSelectedBbox(item.bbox);
    handleGenerateTerrain({
      name: item.name + '_repeat',
      resolution: item.config.resolution,
      exportFormats: item.config.exportFormats,
      elevationSource: item.config.elevationSource,
      enableRoads: item.config.enableRoads,
      enableBuildings: item.config.enableBuildings,
      enableWeightmaps: item.config.enableWeightmaps,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 transition-colors duration-200">
      {/* Setup Wizard */}
      {showWizard && (
        <SetupWizard onComplete={() => setShowWizard(false)} />
      )}

      {/* Settings Modal */}
      {showSettings && (
        <SettingsPage onClose={() => setShowSettings(false)} />
      )}

      {/* History Modal */}
      {showHistory && (
        <GenerationHistory
          onClose={() => setShowHistory(false)}
          onRepeat={handleRepeatGeneration}
        />
      )}

      {/* Cache Manager Modal */}
      {showCache && (
        <CacheManager
          onClose={() => setShowCache(false)}
        />
      )}

      {/* Share Dialog */}
      {showShare && selectedBbox && (
        <ShareDialog
          config={{
            bbox: selectedBbox,
            name: 'Shared Terrain',
            resolution: 2048,
            exportFormats: ['gltf'],
            elevationSource: 'auto',
            enableRoads: true,
            enableBuildings: true,
            enableWeightmaps: true,
          }}
          onClose={() => setShowShare(false)}
        />
      )}

      {/* Share Manager */}
      {showShareManager && (
        <ShareManager
          onClose={() => setShowShareManager(false)}
        />
      )}

      {/* Header */}
      <header className="glass border-b border-gray-200 dark:border-gray-700">
        <div className={`container mx-auto px-4 ${isMobile ? 'py-2' : 'py-4'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Globe className={`${isMobile ? 'w-6 h-6' : 'w-8 h-8'} text-blue-600 dark:text-blue-400`} />
              <div>
                <h1 className={`${isMobile ? 'text-lg' : 'text-2xl'} font-bold text-gray-900 dark:text-white`}>
                  TerraForge{!isMobile && ' Studio'}
                </h1>
                {!isMobile && (
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Professional 3D Terrain Generator {appHealth?.version && `v${appHealth.version}`}
                  </p>
                )}
              </div>
            </div>

            <div className={`flex items-center ${isMobile ? 'space-x-2' : 'space-x-4'}`}>
              {!isMobile && (
                <>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {appHealth?.data_sources && (
                      <span>
                        {appHealth.data_sources.available.length} / {appHealth.data_sources.total} sources
                      </span>
                    )}
                  </div>
                  
                  <ThemeToggle />
                  
                  <button
                    onClick={() => setShowShareManager(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-md border border-gray-300 dark:border-gray-600 transition"
                    title="Share Manager (Ctrl+Shift+S)"
                  >
                    <Share2 className="w-5 h-5" />
                    <span className="hidden xl:inline">Share</span>
                  </button>

                  <button
                    onClick={() => setShowCache(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-md border border-gray-300 dark:border-gray-600 transition"
                    title="Cache Manager (Ctrl+Shift+C)"
                  >
                    <Database className="w-5 h-5" />
                    <span className="hidden xl:inline">Cache</span>
                  </button>

                  <button
                    onClick={() => setShowHistory(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-md border border-gray-300 dark:border-gray-600 transition"
                    title="Generation History (Ctrl+H)"
                  >
                    <History className="w-5 h-5" />
                    <span className="hidden lg:inline">History</span>
                  </button>
                  
                  <button
                    onClick={() => setShowSettings(true)}
                    className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-900 dark:text-white rounded-md border border-gray-300 dark:border-gray-600 transition"
                    title="Settings (Ctrl+S)"
                  >
                    <SettingsIcon className="w-5 h-5" />
                    <span className="hidden lg:inline">Settings</span>
                  </button>
                </>
              )}
              
              {isMobile && (
                <ThemeToggle />
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className={`container mx-auto px-4 ${isMobile ? 'py-3 pb-20' : 'py-6'}`}>
        <div className={`grid grid-cols-1 ${isMobile ? 'gap-3' : 'lg:grid-cols-3 gap-6'}`}>
          {/* Left Panel - Map & 3D Preview */}
          <div className={`${isMobile ? '' : 'lg:col-span-2'} space-y-${isMobile ? '3' : '6'}`}>
            {/* Tab Switcher - Hide on mobile (use bottom nav instead) */}
            {!isMobile && (
              <div className="glass rounded-lg p-2 flex space-x-2">
              <button
                onClick={() => setActiveTab('2d')}
                className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md transition ${
                  activeTab === '2d'
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
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
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
              >
                <Box className="w-5 h-5" />
                <span>3D Preview</span>
              </button>
            </div>
            )}

            {/* Map or 3D View */}
            <div className="glass rounded-lg overflow-hidden shadow-lg" style={{ height: isMobile ? '400px' : '600px' }}>
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
          <div className={`space-y-${isMobile ? '3' : '6'}`}>
            {/* Export Configuration */}
            <div className="glass rounded-lg p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <Download className="w-5 h-5 mr-2" />
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
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Download className="w-5 h-5 mr-2" />
                  Generation Status
                </h2>
                <StatusMonitor status={currentTask} />
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Mobile Bottom Navigation */}
      {isMobile && (
        <MobileNav
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onHistoryOpen={() => setShowHistory(true)}
          onShareOpen={() => setShowShareManager(true)}
          onSettingsOpen={() => setShowSettings(true)}
        />
      )}

      {/* Footer - Hide on mobile */}
      {!isMobile && (
        <footer className="mt-12 py-6 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>
            TerraForge Studio - Professional Cross-Platform 3D Terrain Generator
          </p>
          <p className="mt-1">
            Supports Unreal Engine 5, Unity, GLTF, and GeoTIFF
          </p>
        </footer>
      )}
    </div>
  );
}

export default App;


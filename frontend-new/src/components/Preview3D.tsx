/**
 * 3D Preview Component with CesiumJS
 * Full terrain visualization with satellite imagery
 */

import { useEffect, useRef, useState } from 'react';
import { Camera, Home, ZoomIn, ZoomOut, RotateCcw, Download } from 'lucide-react';
import type { BoundingBox } from '@/types';

interface Preview3DProps {
  bbox: BoundingBox | null;
  terrainData?: {
    elevationUrl?: string;
    imageryUrl?: string;
  };
}

const Preview3D: React.FC<Preview3DProps> = ({ bbox, terrainData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<any>(null);
  const [isInitialized, setIsInitialized] = useState(false);
  const [cameraMode, setCameraMode] = useState<'free' | 'orbit'>('free');

  useEffect(() => {
    // Initialize CesiumJS viewer
    const initializeCesium = async () => {
      if (!containerRef.current || isInitialized) return;

      try {
        // Dynamically import Cesium to avoid SSR issues
        const Cesium = await import('cesium');
        
        // Set Cesium ion access token (use your own token)
        Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5N2UyMjcwOS00MDY1LTQxYjEtYjZjMy00YTU0ZTg1YmUwYmUiLCJpZCI6MTQyODk1LCJpYXQiOjE2ODY1NjE2Njl9.example';

        // Create viewer
        const viewer = new Cesium.Viewer(containerRef.current, {
          terrainProvider: await Cesium.createWorldTerrainAsync(),
          imageryProvider: new Cesium.IonImageryProvider({ assetId: 2 }),
          baseLayerPicker: false,
          geocoder: false,
          homeButton: false,
          sceneModePicker: false,
          navigationHelpButton: false,
          animation: false,
          timeline: false,
          fullscreenButton: false,
          vrButton: false,
          shadows: true,
          shouldAnimate: false,
        });

        // Enable lighting
        viewer.scene.globe.enableLighting = true;
        
        // Set terrain exaggeration for better visibility
        viewer.scene.verticalExaggeration = 1.5;

        viewerRef.current = viewer;
        setIsInitialized(true);

        // Fly to bbox if provided
        if (bbox) {
          flyToBoundingBox(viewer, bbox, Cesium);
        }

      } catch (error) {
        console.error('Failed to initialize Cesium:', error);
      }
    };

    initializeCesium();

    // Cleanup
    return () => {
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
      }
    };
  }, []);

  useEffect(() => {
    // Update view when bbox changes
    if (viewerRef.current && bbox && isInitialized) {
      import('cesium').then(Cesium => {
        flyToBoundingBox(viewerRef.current, bbox, Cesium);
      });
    }
  }, [bbox, isInitialized]);

  const flyToBoundingBox = (viewer: any, box: BoundingBox, Cesium: any) => {
    const center = {
      longitude: (box.east + box.west) / 2,
      latitude: (box.north + box.south) / 2,
    };

    const latDiff = box.north - box.south;
    const lonDiff = box.east - box.west;
    const range = Math.max(latDiff, lonDiff) * 111320; // Approx meters per degree

    viewer.camera.flyTo({
      destination: Cesium.Cartesian3.fromDegrees(
        center.longitude,
        center.latitude,
        range * 2
      ),
      orientation: {
        heading: Cesium.Math.toRadians(0),
        pitch: Cesium.Math.toRadians(-45),
        roll: 0,
      },
      duration: 2,
    });
  };

  const handleZoomIn = () => {
    if (!viewerRef.current) return;
    import('cesium').then(Cesium => {
      const camera = viewerRef.current.camera;
      const moveRate = camera.positionCartographic.height / 10;
      camera.moveForward(moveRate);
    });
  };

  const handleZoomOut = () => {
    if (!viewerRef.current) return;
    import('cesium').then(Cesium => {
      const camera = viewerRef.current.camera;
      const moveRate = camera.positionCartographic.height / 10;
      camera.moveBackward(moveRate);
    });
  };

  const handleResetView = () => {
    if (!viewerRef.current || !bbox) return;
    import('cesium').then(Cesium => {
      flyToBoundingBox(viewerRef.current, bbox, Cesium);
    });
  };

  const handleHomeView = () => {
    if (!viewerRef.current) return;
    import('cesium').then(Cesium => {
      viewerRef.current.camera.flyHome(1.5);
    });
  };

  const handleScreenshot = () => {
    if (!viewerRef.current) return;
    
    viewerRef.current.render();
    const canvas = viewerRef.current.scene.canvas;
    
    canvas.toBlob((blob: Blob | null) => {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.download = `terrain-preview-${Date.now()}.png`;
      link.href = url;
      link.click();
      URL.revokeObjectURL(url);
    });
  };

  const toggleCameraMode = () => {
    setCameraMode(mode => mode === 'free' ? 'orbit' : 'free');
  };

  return (
    <div className="relative w-full h-full bg-gray-900">
      {/* Cesium Container */}
      <div ref={containerRef} className="w-full h-full" />

      {/* Loading State */}
      {!isInitialized && (
        <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-blue-900 to-indigo-900">
          <div className="text-center text-white p-8">
            <div className="animate-spin w-12 h-12 border-4 border-white border-t-transparent rounded-full mx-auto mb-4" />
            <h3 className="text-xl font-bold">Initializing 3D View...</h3>
            <p className="text-sm mt-2 opacity-75">Loading CesiumJS terrain engine</p>
          </div>
        </div>
      )}

      {/* No Selection State */}
      {isInitialized && !bbox && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-white p-8 bg-black/50 backdrop-blur-sm rounded-lg">
            <div className="text-6xl mb-4">🌍</div>
            <h3 className="text-xl font-bold mb-2">3D Terrain Preview</h3>
            <p className="text-sm opacity-75">Select an area on the 2D map to preview in 3D</p>
          </div>
        </div>
      )}

      {/* 3D Controls */}
      {isInitialized && (
        <div className="absolute top-4 right-4 flex flex-col space-y-2">
          <button
            onClick={handleScreenshot}
            className="p-3 bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 rounded-lg shadow-lg transition"
            title="Take Screenshot"
          >
            <Download className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={handleZoomIn}
            className="p-3 bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 rounded-lg shadow-lg transition"
            title="Zoom In"
          >
            <ZoomIn className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={handleZoomOut}
            className="p-3 bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 rounded-lg shadow-lg transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={handleResetView}
            disabled={!bbox}
            className="p-3 bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 rounded-lg shadow-lg transition disabled:opacity-50"
            title="Reset View to Selection"
          >
            <RotateCcw className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={handleHomeView}
            className="p-3 bg-white/90 dark:bg-gray-800/90 hover:bg-white dark:hover:bg-gray-700 rounded-lg shadow-lg transition"
            title="Home View"
          >
            <Home className="w-5 h-5 text-gray-700 dark:text-gray-300" />
          </button>
          
          <button
            onClick={toggleCameraMode}
            className={`p-3 rounded-lg shadow-lg transition ${
              cameraMode === 'orbit' 
                ? 'bg-blue-600 text-white' 
                : 'bg-white/90 dark:bg-gray-800/90 text-gray-700 dark:text-gray-300'
            }`}
            title={`Camera Mode: ${cameraMode}`}
          >
            <Camera className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Info Panel */}
      {isInitialized && bbox && (
        <div className="absolute bottom-4 left-4 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm rounded-lg p-4 shadow-lg max-w-xs">
          <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Selected Area</h4>
          <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
            <p>North: {bbox.north.toFixed(4)}°</p>
            <p>South: {bbox.south.toFixed(4)}°</p>
            <p>East: {bbox.east.toFixed(4)}°</p>
            <p>West: {bbox.west.toFixed(4)}°</p>
            <p className="pt-1 border-t border-gray-300 dark:border-gray-600">
              Area: {bbox.area_km2?.toFixed(2) || 'N/A'} km²
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Preview3D;

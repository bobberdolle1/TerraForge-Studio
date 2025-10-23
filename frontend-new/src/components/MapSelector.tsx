/**
 * Map Selector Component - Leaflet-based area selection
 */

import { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet-draw';
import type { BoundingBox } from '@/types';
import { Layers } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface MapSelectorProps {
  selectedBbox: BoundingBox | null;
  onBboxChange: (bbox: BoundingBox | null) => void;
}

const MapSelector: React.FC<MapSelectorProps> = ({ selectedBbox, onBboxChange }) => {
  const { t } = useTranslation();
  const mapRef = useRef<L.Map | null>(null);
  const drawnItemsRef = useRef<L.FeatureGroup | null>(null);
  const currentLayerRef = useRef<L.TileLayer | null>(null);
  const labelLayerRef = useRef<L.TileLayer | null>(null);
  const [mapType, setMapType] = useState<'osm' | 'satellite' | 'hybrid' | 'topo'>('osm');

  useEffect(() => {
    // Initialize map
    if (!mapRef.current) {
      const map = L.map('map').setView([40.7128, -74.0060], 4);

      // Create layer based on map type
      const getLayer = (type: 'osm' | 'satellite' | 'hybrid' | 'topo') => {
        switch (type) {
          case 'satellite':
            return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
              attribution: '© Esri, Maxar, Earthstar Geographics',
              maxZoom: 19,
            });
          case 'hybrid':
            return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
              attribution: '© Esri, Maxar, Earthstar Geographics',
              maxZoom: 19,
            });
          case 'topo':
            return L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
              attribution: '© OpenTopoMap contributors',
              maxZoom: 17,
            });
          case 'osm':
          default:
            return L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
              attribution: '© OpenStreetMap contributors',
              maxZoom: 19,
            });
        }
      };
      
      // Labels overlay for hybrid mode
      const getLabelsLayer = () => {
        return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {
          attribution: '© Esri',
          maxZoom: 19,
        });
      };

      const layer = getLayer(mapType);
      layer.addTo(map);
      currentLayerRef.current = layer;
      
      // Add labels for hybrid mode
      if (mapType === 'hybrid') {
        const labelsLayer = getLabelsLayer();
        labelsLayer.addTo(map);
        labelLayerRef.current = labelsLayer;
      }

      // Store functions on map for later use
      (map as any)._getLayer = getLayer;
      (map as any)._getLabelsLayer = getLabelsLayer;

      const drawnItems = new L.FeatureGroup();
      map.addLayer(drawnItems);

      // Add drawing controls with improved UX
      const drawControl = new L.Control.Draw({
        position: 'topleft',
        edit: {
          featureGroup: drawnItems,
          remove: true, // Enable deletion
        },
        draw: {
          polygon: {
            allowIntersection: false,
            drawError: {
              color: '#e74c3c',
              message: '<strong>Error:</strong> Shape edges cannot cross!',
            },
            shapeOptions: {
              color: '#10b981',
              weight: 5,
              opacity: 0.9,
              fillColor: '#10b981',
              fillOpacity: 0.3,
            },
            showArea: true,
            metric: true,
            repeatMode: false,
            // maxPoints не указан = неограниченное количество точек
            icon: new L.DivIcon({
              iconSize: new L.Point(10, 10),
              className: 'leaflet-div-icon leaflet-editing-icon'
            }),
          },
          polyline: false,
          rectangle: {
            shapeOptions: {
              color: '#3b82f6',
              weight: 5,
              opacity: 0.9,
              fillColor: '#3b82f6',
              fillOpacity: 0.3,
            },
            showArea: true,
            metric: true,
            repeatMode: false,
          },
          circle: false,
          marker: false,
          circlemarker: false,
        },
      });
      map.addControl(drawControl);

      // Handle drawing created
      map.on(L.Draw.Event.CREATED, (event: any) => {
        const layer = event.layer;
        drawnItems.clearLayers();
        drawnItems.addLayer(layer);
        
        // ПРИНУДИТЕЛЬНО УСТАНОВИТЬ СТИЛИ!
        if (layer instanceof L.Rectangle) {
          layer.setStyle({
            color: '#3b82f6',
            weight: 5,
            opacity: 0.9,
            fillColor: '#3b82f6',
            fillOpacity: 0.3,
          });
        } else if (layer instanceof L.Polygon) {
          layer.setStyle({
            color: '#10b981',
            weight: 5,
            opacity: 0.9,
            fillColor: '#10b981',
            fillOpacity: 0.3,
          });
        }

        const bounds = layer.getBounds();
        const bbox: BoundingBox = {
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest(),
        };

        onBboxChange(bbox);
        if ((mapRef.current as any)?._updateInfo) {
          (mapRef.current as any)._updateInfo(bbox);
        }
      });

      // Handle drawing edited
      map.on(L.Draw.Event.EDITED, (event: any) => {
        const layers = event.layers;
        layers.eachLayer((layer: any) => {
          const bounds = layer.getBounds();
          const bbox: BoundingBox = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest(),
          };
          onBboxChange(bbox);
        });
      });

      // Handle drawing deleted
      map.on(L.Draw.Event.DELETED, () => {
        onBboxChange(null);
      });

      // Add info control for selected area
      const InfoControl = L.Control.extend({
        options: { position: 'bottomleft' },
        onAdd: function () {
          const div = L.DomUtil.create('div', 'leaflet-control-info');
          div.style.background = 'white';
          div.style.padding = '10px';
          div.style.borderRadius = '8px';
          div.style.boxShadow = '0 2px 4px rgba(0,0,0,0.2)';
          div.style.fontSize = '12px';
          div.innerHTML = '<div id="map-info"><b>Draw a rectangle or polygon to select area</b></div>';
          return div;
        }
      });
      new InfoControl().addTo(map);

      // Update info on bbox change
      const updateInfo = (bbox: BoundingBox | null) => {
        const infoDiv = document.getElementById('map-info');
        if (!infoDiv) return;

        if (bbox) {
          const width = Math.abs(bbox.east - bbox.west) * 111; // rough km
          const height = Math.abs(bbox.north - bbox.south) * 111; // rough km
          const area = width * height;
          infoDiv.innerHTML = `
            <b>Selected Area:</b><br/>
            <span style="font-size: 11px;">
            N: ${bbox.north.toFixed(4)}°<br/>
            S: ${bbox.south.toFixed(4)}°<br/>
            E: ${bbox.east.toFixed(4)}°<br/>
            W: ${bbox.west.toFixed(4)}°<br/>
            Area: ~${area.toFixed(1)} km²
            </span>
          `;
        } else {
          infoDiv.innerHTML = '<b>Draw a rectangle or polygon to select area</b>';
        }
      };

      // Store update function for later use
      (map as any)._updateInfo = updateInfo;

      mapRef.current = map;
      drawnItemsRef.current = drawnItems;
    }

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, [onBboxChange]);

  // Change map layer when mapType changes
  useEffect(() => {
    if (mapRef.current && currentLayerRef.current) {
      const getLayer = (mapRef.current as any)._getLayer;
      const getLabelsLayer = (mapRef.current as any)._getLabelsLayer;
      if (getLayer) {
        // Remove old layer
        mapRef.current.removeLayer(currentLayerRef.current);
        // Remove old labels if any
        if (labelLayerRef.current) {
          mapRef.current.removeLayer(labelLayerRef.current);
          labelLayerRef.current = null;
        }
        // Add new layer
        const newLayer = getLayer(mapType);
        newLayer.addTo(mapRef.current);
        currentLayerRef.current = newLayer;
        // Add labels for hybrid mode
        if (mapType === 'hybrid' && getLabelsLayer) {
          const labelsLayer = getLabelsLayer();
          labelsLayer.addTo(mapRef.current);
          labelLayerRef.current = labelsLayer;
        }
      }
    }
  }, [mapType]);

  return (
    <div className="relative w-full h-full">
      <div id="map" className="w-full h-full" />
      
      {/* Map Type Selector */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-2">
        <button
          onClick={() => setMapType('osm')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${
            mapType === 'osm'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
          title="OpenStreetMap"
        >
          <Layers className="w-4 h-4" />
          <span>{t('map.mapType.osm')}</span>
        </button>
        <button
          onClick={() => setMapType('satellite')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${
            mapType === 'satellite'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
          title="Satellite"
        >
          <Layers className="w-4 h-4" />
          <span>{t('map.mapType.satellite')}</span>
        </button>
        <button
          onClick={() => setMapType('hybrid')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${
            mapType === 'hybrid'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
          title="Hybrid (Satellite + Labels)"
        >
          <Layers className="w-4 h-4" />
          <span>{t('map.mapType.hybrid')}</span>
        </button>
        <button
          onClick={() => setMapType('topo')}
          className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition ${
            mapType === 'topo'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
          title="Topographic"
        >
          <Layers className="w-4 h-4" />
          <span>{t('map.mapType.topo')}</span>
        </button>
      </div>
      
      {selectedBbox && (
        <div className="absolute top-4 right-4 glass rounded-lg p-4 shadow-lg max-w-xs">
          <h3 className="font-semibold text-sm text-gray-900 mb-2">Selected Area</h3>
          <div className="text-xs text-gray-600 space-y-1">
            <p>North: {selectedBbox.north.toFixed(4)}°</p>
            <p>South: {selectedBbox.south.toFixed(4)}°</p>
            <p>East: {selectedBbox.east.toFixed(4)}°</p>
            <p>West: {selectedBbox.west.toFixed(4)}°</p>
            <p className="pt-2 border-t border-gray-200">
              Area: ~{calculateArea(selectedBbox).toFixed(2)} km²
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

function calculateArea(bbox: BoundingBox): number {
  const latDiff = bbox.north - bbox.south;
  const lonDiff = bbox.east - bbox.west;
  const avgLat = (bbox.north + bbox.south) / 2;
  return Math.abs(latDiff * lonDiff * Math.cos((avgLat * Math.PI) / 180) * 111.32 * 111.32);
}

export default MapSelector;


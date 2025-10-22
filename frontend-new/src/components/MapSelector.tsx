/**
 * Map Selector Component - Leaflet-based area selection
 */

import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet-draw';
import type { BoundingBox } from '@/types';

interface MapSelectorProps {
  selectedBbox: BoundingBox | null;
  onBboxChange: (bbox: BoundingBox | null) => void;
}

const MapSelector: React.FC<MapSelectorProps> = ({ selectedBbox, onBboxChange }) => {
  const mapRef = useRef<L.Map | null>(null);
  const drawnItemsRef = useRef<L.FeatureGroup | null>(null);

  useEffect(() => {
    // Initialize map
    if (!mapRef.current) {
      const map = L.map('map').setView([40.7128, -74.0060], 4);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map);

      const drawnItems = new L.FeatureGroup();
      map.addLayer(drawnItems);

      // Add drawing controls
      const drawControl = new L.Control.Draw({
        edit: {
          featureGroup: drawnItems,
          edit: false,
        },
        draw: {
          polygon: {},
          polyline: false,
          rectangle: {},
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

        const bounds = layer.getBounds();
        const bbox: BoundingBox = {
          north: bounds.getNorth(),
          south: bounds.getSouth(),
          east: bounds.getEast(),
          west: bounds.getWest(),
        };

        onBboxChange(bbox);
      });

      // Handle drawing deleted
      map.on(L.Draw.Event.DELETED, () => {
        onBboxChange(null);
      });

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

  return (
    <div className="relative w-full h-full">
      <div id="map" className="w-full h-full" />
      
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


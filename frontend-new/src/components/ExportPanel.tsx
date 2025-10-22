/**
 * Export Configuration Panel
 */

import { useState } from 'react';
import { Rocket } from 'lucide-react';
import type { ExportFormat, ElevationSource } from '@/types';

interface ExportPanelProps {
  onGenerate: (config: {
    name: string;
    resolution: number;
    exportFormats: ExportFormat[];
    elevationSource: ElevationSource;
    enableRoads: boolean;
    enableBuildings: boolean;
    enableWeightmaps: boolean;
  }) => void;
  disabled: boolean;
}

const ExportPanel: React.FC<ExportPanelProps> = ({ onGenerate, disabled }) => {
  const [name, setName] = useState('my_terrain');
  const [resolution, setResolution] = useState(2048);
  const [exportFormats, setExportFormats] = useState<ExportFormat[]>(['unreal5']);
  const [elevationSource, setElevationSource] = useState<ElevationSource>('auto');
  const [enableRoads, setEnableRoads] = useState(true);
  const [enableBuildings, setEnableBuildings] = useState(true);
  const [enableWeightmaps, setEnableWeightmaps] = useState(true);

  const handleGenerate = () => {
    if (!name.trim()) {
      alert('Please enter a terrain name');
      return;
    }

    onGenerate({
      name,
      resolution,
      exportFormats,
      elevationSource,
      enableRoads,
      enableBuildings,
      enableWeightmaps,
    });
  };

  const toggleFormat = (format: ExportFormat) => {
    setExportFormats(prev =>
      prev.includes(format)
        ? prev.filter(f => f !== format)
        : [...prev, format]
    );
  };

  return (
    <div className="space-y-4">
      {/* Terrain Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Terrain Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="my_terrain"
        />
      </div>

      {/* Resolution */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Heightmap Resolution
        </label>
        <select
          value={resolution}
          onChange={(e) => setResolution(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value={1009}>1009 (UE5 Small)</option>
          <option value={2017}>2017 (UE5 Medium)</option>
          <option value={2048}>2048 (Standard)</option>
          <option value={2049}>2049 (Unity)</option>
          <option value={4033}>4033 (UE5 Large)</option>
          <option value={4096}>4096 (High Detail)</option>
        </select>
      </div>

      {/* Export Formats */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Export Formats
        </label>
        <div className="space-y-2">
          {(['unreal5', 'unity', 'gltf', 'geotiff'] as ExportFormat[]).map(format => (
            <label key={format} className="flex items-center">
              <input
                type="checkbox"
                checked={exportFormats.includes(format)}
                onChange={() => toggleFormat(format)}
                className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700 capitalize">{format}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Elevation Source */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Elevation Source
        </label>
        <select
          value={elevationSource}
          onChange={(e) => setElevationSource(e.target.value as ElevationSource)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
        >
          <option value="auto">Auto (Best Available)</option>
          <option value="srtm">SRTM (Free, 30-90m)</option>
          <option value="opentopography">OpenTopography (High-res)</option>
        </select>
      </div>

      {/* Features */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Features
        </label>
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={enableRoads}
              onChange={(e) => setEnableRoads(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">Roads</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={enableBuildings}
              onChange={(e) => setEnableBuildings(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">Buildings</span>
          </label>
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={enableWeightmaps}
              onChange={(e) => setEnableWeightmaps(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700">Material Weightmaps</span>
          </label>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={disabled || exportFormats.length === 0}
        className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
      >
        <Rocket className="w-5 h-5" />
        <span>Generate Terrain</span>
      </button>
    </div>
  );
};

export default ExportPanel;


/**
 * Export Configuration Panel
 */

import { useState } from 'react';
import { Rocket, Sparkles } from 'lucide-react';
import PresetSelector from './PresetSelector';
import type { ExportFormat, ElevationSource } from '@/types';
import type { TerrainPreset } from '../types/presets';
import { notify } from '../utils/toast';

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
  const [showPresets, setShowPresets] = useState(false);

  const handleGenerate = () => {
    if (!name.trim()) {
      notify.error('Please enter a terrain name');
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

  const handleApplyPreset = (preset: TerrainPreset) => {
    setName(preset.name.toLowerCase().replace(/\s+/g, '_'));
    setResolution(preset.config.resolution);
    setExportFormats(preset.config.exportFormats);
    setElevationSource(preset.config.elevationSource);
    setEnableRoads(preset.config.enableRoads);
    setEnableBuildings(preset.config.enableBuildings);
    setEnableWeightmaps(preset.config.enableWeightmaps);
    setShowPresets(false);
    notify.success(`Applied preset: ${preset.name}`);
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
      {/* Preset Selector Modal */}
      {showPresets && (
        <PresetSelector
          onSelectPreset={handleApplyPreset}
          onClose={() => setShowPresets(false)}
        />
      )}

      {/* Load Preset Button */}
      <button
        onClick={() => setShowPresets(true)}
        className="w-full flex items-center justify-center space-x-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-3 rounded-md hover:from-purple-700 hover:to-indigo-700 transition"
      >
        <Sparkles className="w-5 h-5" />
        <span>Load Preset Template</span>
      </button>

      {/* Terrain Name */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Terrain Name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
          placeholder="my_terrain"
        />
      </div>

      {/* Resolution */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Heightmap Resolution
        </label>
        <select
          value={resolution}
          onChange={(e) => setResolution(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
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
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Export Formats
        </label>
        <div className="space-y-2">
          {(['unreal5', 'unity', 'gltf', 'geotiff'] as ExportFormat[]).map(format => (
            <label key={format} className="flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={exportFormats.includes(format)}
                onChange={() => toggleFormat(format)}
                className="rounded text-blue-600 focus:ring-2 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300 capitalize">{format}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Elevation Source */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Elevation Source
        </label>
        <select
          value={elevationSource}
          onChange={(e) => setElevationSource(e.target.value as ElevationSource)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
        >
          <option value="auto">Auto (Best Available)</option>
          <option value="srtm">SRTM (Free, 30-90m)</option>
          <option value="opentopography">OpenTopography (High-res)</option>
        </select>
      </div>

      {/* Features */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Features
        </label>
        <div className="space-y-2">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={enableRoads}
              onChange={(e) => setEnableRoads(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Roads</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={enableBuildings}
              onChange={(e) => setEnableBuildings(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Buildings</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={enableWeightmaps}
              onChange={(e) => setEnableWeightmaps(e.target.checked)}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Material Weightmaps</span>
          </label>
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerate}
        disabled={disabled || exportFormats.length === 0}
        className="w-full flex items-center justify-center space-x-2 bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed transition"
      >
        <Rocket className="w-5 h-5" />
        <span>Generate Terrain</span>
      </button>
    </div>
  );
};

export default ExportPanel;

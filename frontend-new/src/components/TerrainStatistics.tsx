import React from 'react';
import { BarChart3, TrendingUp, Mountain, Waves } from 'lucide-react';

interface TerrainStats {
  minElevation: number;
  maxElevation: number;
  avgElevation: number;
  area: number;
  slopeAnalysis: {
    flat: number; // 0-5%
    gentle: number; // 5-15%
    moderate: number; // 15-30%
    steep: number; // >30%
  };
  aspectAnalysis: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
}

export const TerrainStatistics: React.FC<{ stats: TerrainStats }> = ({ stats }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
        <BarChart3 className="w-6 h-6 text-blue-600" />
        Terrain Statistics
      </h2>

      {/* Elevation Stats */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Elevation Profile
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <StatCard
            label="Minimum"
            value={`${stats.minElevation.toFixed(1)}m`}
            icon={<Waves className="w-5 h-5 text-blue-500" />}
          />
          <StatCard
            label="Average"
            value={`${stats.avgElevation.toFixed(1)}m`}
            icon={<Mountain className="w-5 h-5 text-green-500" />}
          />
          <StatCard
            label="Maximum"
            value={`${stats.maxElevation.toFixed(1)}m`}
            icon={<Mountain className="w-5 h-5 text-red-500" />}
          />
        </div>
        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
          Elevation range: {(stats.maxElevation - stats.minElevation).toFixed(1)}m
        </div>
      </div>

      {/* Slope Analysis */}
      <div className="mb-6">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Slope Distribution
        </h3>
        <div className="space-y-3">
          <SlopeBar label="Flat (0-5°)" percentage={stats.slopeAnalysis.flat} color="bg-green-500" />
          <SlopeBar label="Gentle (5-15°)" percentage={stats.slopeAnalysis.gentle} color="bg-yellow-500" />
          <SlopeBar label="Moderate (15-30°)" percentage={stats.slopeAnalysis.moderate} color="bg-orange-500" />
          <SlopeBar label="Steep (>30°)" percentage={stats.slopeAnalysis.steep} color="bg-red-500" />
        </div>
      </div>

      {/* Aspect Analysis */}
      <div>
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
          Aspect Distribution
        </h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">North</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {stats.aspectAnalysis.north}%
            </div>
          </div>
          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">South</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {stats.aspectAnalysis.south}%
            </div>
          </div>
          <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">East</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {stats.aspectAnalysis.east}%
            </div>
          </div>
          <div className="p-3 bg-pink-50 dark:bg-pink-900/20 rounded-lg">
            <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">West</div>
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {stats.aspectAnalysis.west}%
            </div>
          </div>
        </div>
      </div>

      {/* Area */}
      <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div className="text-sm text-gray-600 dark:text-gray-400">Total Area</div>
        <div className="text-2xl font-bold text-gray-900 dark:text-white">
          {stats.area.toFixed(2)} km²
        </div>
      </div>
    </div>
  );
};

const StatCard: React.FC<{ label: string; value: string; icon: React.ReactNode }> = ({
  label,
  value,
  icon,
}) => (
  <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
    <div className="flex items-center gap-2 mb-2">{icon}</div>
    <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">{label}</div>
    <div className="text-lg font-bold text-gray-900 dark:text-white">{value}</div>
  </div>
);

const SlopeBar: React.FC<{ label: string; percentage: number; color: string }> = ({
  label,
  percentage,
  color,
}) => (
  <div>
    <div className="flex items-center justify-between mb-1">
      <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
      <span className="text-sm font-medium text-gray-900 dark:text-white">{percentage}%</span>
    </div>
    <div className="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
      <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${percentage}%` }} />
    </div>
  </div>
);

export default TerrainStatistics;

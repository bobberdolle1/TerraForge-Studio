/**
 * Generation Status Monitor
 */

import { CheckCircle, XCircle, Loader, Download } from 'lucide-react';
import type { GenerationStatus } from '@/types';

interface StatusMonitorProps {
  status: GenerationStatus;
}

const StatusMonitor: React.FC<StatusMonitorProps> = ({ status }) => {
  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Loader className="w-6 h-6 text-blue-500 animate-spin" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'processing':
        return 'bg-blue-500';
      default:
        return 'bg-gray-300';
    }
  };

  return (
    <div className="space-y-4">
      {/* Status Header */}
      <div className="flex items-center space-x-3">
        {getStatusIcon()}
        <div className="flex-1">
          <p className="font-semibold text-gray-900 capitalize">{status.status}</p>
          <p className="text-sm text-gray-600">{status.current_step}</p>
        </div>
      </div>

      {/* Progress Bar */}
      {status.status === 'processing' && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progress</span>
            <span>{status.progress.toFixed(0)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`${getStatusColor()} h-2 rounded-full transition-all duration-300`}
              style={{ width: `${status.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Message */}
      {status.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-800">{status.error}</p>
        </div>
      )}

      {/* Success Result */}
      {status.result && (
        <div className="bg-green-50 border border-green-200 rounded-md p-4 space-y-3">
          <h4 className="font-semibold text-green-900">Generation Complete!</h4>
          
          <div className="text-sm text-green-800 space-y-1">
            <p><strong>Terrain:</strong> {status.result.terrain_name}</p>
            <p><strong>Resolution:</strong> {status.result.resolution}x{status.result.resolution}</p>
            <p><strong>Area:</strong> {status.result.area_km2.toFixed(2)} km²</p>
            <p>
              <strong>Elevation:</strong> {status.result.elevation_range.min.toFixed(1)}m 
              - {status.result.elevation_range.max.toFixed(1)}m
            </p>
          </div>

          {/* Export Downloads */}
          <div className="pt-3 border-t border-green-300">
            <p className="text-sm font-semibold text-green-900 mb-2">Exports:</p>
            <div className="space-y-2">
              {Object.keys(status.result.exports).map(format => (
                <a
                  key={format}
                  href={`/api/download/${status.task_id}/${format}`}
                  className="flex items-center justify-between px-3 py-2 bg-white rounded-md hover:bg-green-100 transition"
                >
                  <span className="text-sm text-gray-700 capitalize">{format}</span>
                  <Download className="w-4 h-4 text-green-600" />
                </a>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StatusMonitor;


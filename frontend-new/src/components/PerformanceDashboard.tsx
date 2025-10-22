import React, { useState, useEffect } from 'react';
import { Activity, Zap, HardDrive, Cpu, Clock, TrendingUp } from 'lucide-react';

interface PerformanceMetrics {
  fps: number;
  memory: {
    used: number;
    total: number;
  };
  cpu: number;
  loadTime: number;
  apiLatency: number;
  cacheHitRate: number;
}

export const PerformanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    memory: { used: 45, total: 100 },
    cpu: 23,
    loadTime: 2.3,
    apiLatency: 120,
    cacheHitRate: 87,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate real-time metrics
      setMetrics({
        fps: 55 + Math.random() * 10,
        memory: {
          used: 40 + Math.random() * 20,
          total: 100,
        },
        cpu: 20 + Math.random() * 30,
        loadTime: 2 + Math.random() * 1,
        apiLatency: 100 + Math.random() * 50,
        cacheHitRate: 80 + Math.random() * 15,
      });
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (value: number, good: number, warning: number) => {
    if (value >= good) return 'text-green-600';
    if (value >= warning) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
          <Activity className="w-8 h-8 text-blue-600" />
          Performance Monitor
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Real-time system performance metrics
        </p>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* FPS */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-blue-100 dark:bg-blue-900/20 rounded-lg">
              <Zap className="w-6 h-6 text-blue-600" />
            </div>
            <span className={`text-3xl font-bold ${getStatusColor(metrics.fps, 55, 45)}`}>
              {metrics.fps.toFixed(0)}
            </span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">FPS</div>
          <div className="mt-2 text-xs text-gray-500">Target: 60 FPS</div>
        </div>

        {/* Memory */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 dark:bg-purple-900/20 rounded-lg">
              <HardDrive className="w-6 h-6 text-purple-600" />
            </div>
            <span className={`text-3xl font-bold ${getStatusColor(100 - metrics.memory.used, 60, 30)}`}>
              {metrics.memory.used.toFixed(0)}%
            </span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">Memory Usage</div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all"
              style={{ width: `${metrics.memory.used}%` }}
            />
          </div>
        </div>

        {/* CPU */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
              <Cpu className="w-6 h-6 text-orange-600" />
            </div>
            <span className={`text-3xl font-bold ${getStatusColor(100 - metrics.cpu, 60, 30)}`}>
              {metrics.cpu.toFixed(0)}%
            </span>
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">CPU Usage</div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-2">
            <div
              className="bg-orange-600 h-2 rounded-full transition-all"
              style={{ width: `${metrics.cpu}%` }}
            />
          </div>
        </div>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Load Time */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="w-5 h-5 text-green-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Page Load Time
            </span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {metrics.loadTime.toFixed(2)}s
          </div>
          <div className="text-xs text-gray-500 mt-1">Target: &lt;3s</div>
        </div>

        {/* API Latency */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              API Latency
            </span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {metrics.apiLatency.toFixed(0)}ms
          </div>
          <div className="text-xs text-gray-500 mt-1">Target: &lt;200ms</div>
        </div>

        {/* Cache Hit Rate */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="w-5 h-5 text-purple-600" />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Cache Hit Rate
            </span>
          </div>
          <div className="text-2xl font-bold text-gray-900 dark:text-white">
            {metrics.cacheHitRate.toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">Target: &gt;80%</div>
        </div>
      </div>

      {/* Performance Tips */}
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg p-6">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
          Performance Tips
        </h3>
        <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
          {metrics.memory.used > 70 && (
            <li className="flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              High memory usage detected. Consider clearing cache.
            </li>
          )}
          {metrics.fps < 50 && (
            <li className="flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              Low FPS detected. Try disabling animations or closing other tabs.
            </li>
          )}
          {metrics.cacheHitRate < 80 && (
            <li className="flex items-center gap-2">
              <span className="text-yellow-600">⚠️</span>
              Cache efficiency is low. Warm up cache by browsing common features.
            </li>
          )}
          {metrics.memory.used < 70 && metrics.fps > 55 && metrics.cacheHitRate > 80 && (
            <li className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              All systems running optimally!
            </li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default PerformanceDashboard;

import React, { useState, useEffect } from 'react';
import { BarChart, TrendingUp, Users, Clock, Download, Map } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface AnalyticsData {
  totalGenerations: number;
  totalExports: number;
  activeUsers: number;
  avgGenerationTime: number;
  popularFormats: Array<{ format: string; count: number }>;
  recentActivity: Array<{ date: string; count: number }>;
}

export const AnalyticsDashboard: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d'>('7d');

  useEffect(() => {
    fetchAnalytics(timeRange);
  }, [timeRange]);

  const fetchAnalytics = async (range: string) => {
    // Mock data - replace with actual API call
    setData({
      totalGenerations: 1247,
      totalExports: 893,
      activeUsers: 156,
      avgGenerationTime: 2.3,
      popularFormats: [
        { format: 'Godot', count: 345 },
        { format: 'Unity', count: 298 },
        { format: 'Unreal', count: 250 },
      ],
      recentActivity: [
        { date: '2025-10-16', count: 45 },
        { date: '2025-10-17', count: 52 },
        { date: '2025-10-18', count: 48 },
        { date: '2025-10-19', count: 61 },
        { date: '2025-10-20', count: 55 },
        { date: '2025-10-21', count: 58 },
        { date: '2025-10-22', count: 67 },
      ],
    });
  };

  if (!data) {
    return <div className="p-6">Loading analytics...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Monitor your terrain generation activity
          </p>
        </div>
        <div className="flex gap-2">
          {(['7d', '30d', '90d'] as const).map((range) => (
            <AccessibleButton
              key={range}
              variant={timeRange === range ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setTimeRange(range)}
            >
              {range}
            </AccessibleButton>
          ))}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={<Map className="w-6 h-6" />}
          title="Total Generations"
          value={data.totalGenerations.toLocaleString()}
          trend="+12%"
          color="blue"
        />
        <StatCard
          icon={<Download className="w-6 h-6" />}
          title="Total Exports"
          value={data.totalExports.toLocaleString()}
          trend="+8%"
          color="green"
        />
        <StatCard
          icon={<Users className="w-6 h-6" />}
          title="Active Users"
          value={data.activeUsers.toLocaleString()}
          trend="+15%"
          color="purple"
        />
        <StatCard
          icon={<Clock className="w-6 h-6" />}
          title="Avg. Gen Time"
          value={`${data.avgGenerationTime}s`}
          trend="-5%"
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Activity Over Time
          </h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {data.recentActivity.map((item, i) => {
              const maxCount = Math.max(...data.recentActivity.map(d => d.count));
              const height = (item.count / maxCount) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <div
                    className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                    style={{ height: `${height}%` }}
                    title={`${item.date}: ${item.count} generations`}
                  />
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(item.date).getDate()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Popular Formats */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Popular Export Formats
          </h2>
          <div className="space-y-4">
            {data.popularFormats.map((format, i) => {
              const maxCount = Math.max(...data.popularFormats.map(f => f.count));
              const percentage = (format.count / maxCount) * 100;
              return (
                <div key={i}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                      {format.format}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {format.count}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  icon: React.ReactNode;
  title: string;
  value: string;
  trend: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

const StatCard: React.FC<StatCardProps> = ({ icon, title, value, trend, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  const trendColor = trend.startsWith('+') ? 'text-green-600' : 'text-red-600';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        <div className={`flex items-center gap-1 text-sm font-medium ${trendColor}`}>
          <TrendingUp className="w-4 h-4" />
          {trend}
        </div>
      </div>
      <div>
        <p className="text-sm text-gray-600 dark:text-gray-400">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
          {value}
        </p>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

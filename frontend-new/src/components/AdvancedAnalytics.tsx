import React, { useState } from 'react';
import { BarChart3, Download, Calendar, TrendingUp, PieChart } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface AnalyticsData {
  period: string;
  generations: number;
  exports: number;
  users: number;
  avgTime: number;
}

export const AdvancedAnalytics: React.FC = () => {
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');
  
  const data: AnalyticsData[] = [
    { period: 'Week 1', generations: 245, exports: 189, users: 45, avgTime: 2.3 },
    { period: 'Week 2', generations: 312, exports: 234, users: 52, avgTime: 2.1 },
    { period: 'Week 3', generations: 289, exports: 198, users: 48, avgTime: 2.4 },
    { period: 'Week 4', generations: 401, exports: 301, users: 61, avgTime: 2.0 },
  ];

  const exportFormats = [
    { name: 'Godot', count: 345, percentage: 38 },
    { name: 'Unity', count: 298, percentage: 33 },
    { name: 'Unreal', count: 189, percentage: 21 },
    { name: 'glTF', count: 90, percentage: 10 },
  ];

  const handleExportReport = () => {
    // Export analytics to CSV/PDF
    console.log('Exporting report...');
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Advanced Analytics
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Detailed insights and performance metrics
          </p>
        </div>
        <div className="flex gap-2">
          <AccessibleButton
            variant="outline"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleExportReport}
          >
            Export Report
          </AccessibleButton>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex gap-2 mb-6">
        {(['7d', '30d', '90d', '1y'] as const).map((range) => (
          <button
            key={range}
            onClick={() => setTimeRange(range)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              timeRange === range
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {range === '1y' ? '1 Year' : range}
          </button>
        ))}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <SummaryCard
          title="Total Generations"
          value="1,247"
          change="+12%"
          trend="up"
          icon={<BarChart3 className="w-6 h-6" />}
          color="blue"
        />
        <SummaryCard
          title="Total Exports"
          value="922"
          change="+8%"
          trend="up"
          icon={<Download className="w-6 h-6" />}
          color="green"
        />
        <SummaryCard
          title="Active Users"
          value="156"
          change="+15%"
          trend="up"
          icon={<TrendingUp className="w-6 h-6" />}
          color="purple"
        />
        <SummaryCard
          title="Avg. Time"
          value="2.2s"
          change="-5%"
          trend="down"
          icon={<Calendar className="w-6 h-6" />}
          color="orange"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Activity Chart */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Activity Trend
          </h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {data.map((item, i) => {
              const maxValue = Math.max(...data.map(d => d.generations));
              const height = (item.generations / maxValue) * 100;
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-2">
                  <div className="relative w-full">
                    <div
                      className="w-full bg-blue-500 rounded-t transition-all hover:bg-blue-600"
                      style={{ height: `${height * 2}px` }}
                      title={`${item.period}: ${item.generations} generations`}
                    />
                  </div>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    {item.period}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Format Distribution */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <PieChart className="w-5 h-5" />
            Export Format Distribution
          </h2>
          <div className="space-y-4">
            {exportFormats.map((format, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {format.name}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {format.count}
                    </span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      {format.percentage}%
                    </span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all"
                    style={{ width: `${format.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Detailed Metrics
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Period
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Generations
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Exports
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Active Users
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Avg Time
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {data.map((row, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    {row.period}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {row.generations}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {row.exports}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {row.users}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                    {row.avgTime}s
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const SummaryCard: React.FC<{
  title: string;
  value: string;
  change: string;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: string;
}> = ({ title, value, change, trend, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-3">
        <div className={`p-2 rounded-lg ${colorClasses[color as keyof typeof colorClasses]}`}>
          {icon}
        </div>
        <span className={`text-sm font-medium ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </span>
      </div>
      <div>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{title}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
      </div>
    </div>
  );
};

export default AdvancedAnalytics;

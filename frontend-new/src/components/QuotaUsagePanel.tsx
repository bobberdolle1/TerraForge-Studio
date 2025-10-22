import React from 'react';
import { Zap, HardDrive, Download, Globe, TrendingUp } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface QuotaUsage {
  type: string;
  used: number;
  limit: number;
  unit: string;
  icon: React.ReactNode;
  color: string;
}

export const QuotaUsagePanel: React.FC = () => {
  const quotas: QuotaUsage[] = [
    {
      type: 'Terrain Generation',
      used: 45,
      limit: 50,
      unit: 'generations',
      icon: <Zap className="w-5 h-5" />,
      color: 'blue',
    },
    {
      type: 'Exports',
      used: 18,
      limit: 20,
      unit: 'exports',
      icon: <Download className="w-5 h-5" />,
      color: 'green',
    },
    {
      type: 'Storage',
      used: 0.8,
      limit: 1,
      unit: 'GB',
      icon: <HardDrive className="w-5 h-5" />,
      color: 'purple',
    },
    {
      type: 'API Calls',
      used: 856,
      limit: 1000,
      unit: 'calls',
      icon: <Globe className="w-5 h-5" />,
      color: 'orange',
    },
  ];

  const getPercentage = (used: number, limit: number) => (used / limit) * 100;

  const getColorClasses = (color: string, percentage: number) => {
    const isWarning = percentage > 80;
    const isDanger = percentage > 95;

    if (isDanger) return 'bg-red-500';
    if (isWarning) return 'bg-yellow-500';

    const colors = {
      blue: 'bg-blue-500',
      green: 'bg-green-500',
      purple: 'bg-purple-500',
      orange: 'bg-orange-500',
    };
    return colors[color as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Resource Usage
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Current plan: <span className="font-semibold text-blue-600">Free</span>
            </p>
          </div>
          <AccessibleButton variant="primary" leftIcon={<TrendingUp className="w-4 h-4" />}>
            Upgrade Plan
          </AccessibleButton>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {quotas.map((quota) => {
          const percentage = getPercentage(quota.used, quota.limit);
          const barColor = getColorClasses(quota.color, percentage);

          return (
            <div
              key={quota.type}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg bg-${quota.color}-100 dark:bg-${quota.color}-900/20 text-${quota.color}-600`}>
                    {quota.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {quota.type}
                    </h3>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      This month
                    </p>
                  </div>
                </div>
              </div>

              <div className="mb-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-2xl font-bold text-gray-900 dark:text-white">
                    {quota.used}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    of {quota.limit} {quota.unit}
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className={`${barColor} h-3 rounded-full transition-all duration-300`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>

              <div className="text-sm text-gray-600 dark:text-gray-400">
                {percentage > 80 ? (
                  <span className="text-yellow-600 dark:text-yellow-400 font-medium">
                    ⚠️ {Math.round(100 - percentage)}% remaining
                  </span>
                ) : (
                  <span>{Math.round(percentage)}% used</span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Plan Comparison */}
      <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          Upgrade for More Resources
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Starter</h3>
            <div className="text-3xl font-bold text-blue-600 mb-4">$9/mo</div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>✓ 500 generations/month</li>
              <li>✓ 200 exports/month</li>
              <li>✓ 10 GB storage</li>
              <li>✓ 10K API calls/day</li>
            </ul>
          </div>
          <div className="border-2 border-blue-500 rounded-lg p-4 relative">
            <div className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-bold">
              POPULAR
            </div>
            <h3 className="font-semibold text-lg mb-2">Pro</h3>
            <div className="text-3xl font-bold text-blue-600 mb-4">$29/mo</div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>✓ 5,000 generations/month</li>
              <li>✓ 2,000 exports/month</li>
              <li>✓ 100 GB storage</li>
              <li>✓ 100K API calls/day</li>
            </ul>
          </div>
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Enterprise</h3>
            <div className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Custom</div>
            <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
              <li>✓ Unlimited generations</li>
              <li>✓ Unlimited exports</li>
              <li>✓ Unlimited storage</li>
              <li>✓ Unlimited API calls</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuotaUsagePanel;

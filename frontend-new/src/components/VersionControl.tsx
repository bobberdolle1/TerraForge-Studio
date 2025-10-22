import React, { useState } from 'react';
import { GitBranch, GitCommit, Clock, RotateCcw, Download } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface Version {
  id: string;
  message: string;
  author: string;
  timestamp: number;
  changes: number;
}

export const VersionControl: React.FC = () => {
  const [versions, setVersions] = useState<Version[]>([
    {
      id: 'v1.0.3',
      message: 'Updated terrain parameters',
      author: 'Current User',
      timestamp: Date.now() - 3600000,
      changes: 5,
    },
    {
      id: 'v1.0.2',
      message: 'Added new export format',
      author: 'Current User',
      timestamp: Date.now() - 7200000,
      changes: 3,
    },
    {
      id: 'v1.0.1',
      message: 'Initial configuration',
      author: 'Current User',
      timestamp: Date.now() - 86400000,
      changes: 12,
    },
  ]);

  const [currentVersion, setCurrentVersion] = useState('v1.0.3');

  const handleRestore = (versionId: string) => {
    if (window.confirm(`Restore to version ${versionId}?`)) {
      setCurrentVersion(versionId);
      // Trigger restore logic
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <GitBranch className="w-6 h-6 text-blue-600" />
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Version Control
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Current: {currentVersion}
            </p>
          </div>
        </div>
        <AccessibleButton variant="primary" size="sm">
          Save New Version
        </AccessibleButton>
      </div>

      <div className="space-y-4">
        {versions.map((version) => (
          <div
            key={version.id}
            className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
          >
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded">
              <GitCommit className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="font-semibold text-gray-900 dark:text-white">
                  {version.id}
                </span>
                {version.id === currentVersion && (
                  <span className="px-2 py-0.5 bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 text-xs rounded-full">
                    Current
                  </span>
                )}
              </div>
              <p className="text-gray-700 dark:text-gray-300 mb-2">
                {version.message}
              </p>
              <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {new Date(version.timestamp).toLocaleString()}
                </span>
                <span>{version.changes} changes</span>
                <span>by {version.author}</span>
              </div>
            </div>

            <div className="flex gap-2">
              {version.id !== currentVersion && (
                <AccessibleButton
                  variant="outline"
                  size="sm"
                  onClick={() => handleRestore(version.id)}
                  leftIcon={<RotateCcw className="w-4 h-4" />}
                >
                  Restore
                </AccessibleButton>
              )}
              <AccessibleButton
                variant="ghost"
                size="sm"
                leftIcon={<Download className="w-4 h-4" />}
              >
                Export
              </AccessibleButton>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VersionControl;

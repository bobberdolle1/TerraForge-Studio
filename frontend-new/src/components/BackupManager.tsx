import React, { useState } from 'react';
import { Download, Upload, Archive, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface Backup {
  id: string;
  name: string;
  size: number;
  created: number;
  type: 'auto' | 'manual';
  status: 'success' | 'failed';
  includes: string[];
}

export const BackupManager: React.FC = () => {
  const [backups] = useState<Backup[]>([
    {
      id: '1',
      name: 'Auto Backup - Oct 22',
      size: 45_000_000,
      created: Date.now() - 3600000,
      type: 'auto',
      status: 'success',
      includes: ['Projects', 'Settings', 'Exports'],
    },
    {
      id: '2',
      name: 'Manual Backup - Oct 20',
      size: 38_000_000,
      created: Date.now() - 86400000 * 2,
      type: 'manual',
      status: 'success',
      includes: ['Projects', 'Settings'],
    },
  ]);

  const [autoBackup, setAutoBackup] = useState(true);
  const [backupFrequency, setBackupFrequency] = useState<'daily' | 'weekly'>('daily');

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleCreateBackup = () => {
    console.log('Creating manual backup...');
  };

  const handleRestoreBackup = (backupId: string) => {
    console.log('Restoring backup:', backupId);
  };

  const handleExportSettings = () => {
    const settings = {
      preferences: {},
      projects: [],
      exports: [],
    };
    const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'terraforge-settings.json';
    a.click();
  };

  const handleImportSettings = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = (e: any) => {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const settings = JSON.parse(event.target?.result as string);
          console.log('Importing settings:', settings);
        } catch (err) {
          console.error('Failed to import settings:', err);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Backup & Restore
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Manage your data backups and settings
        </p>
      </div>

      {/* Settings Export/Import */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Settings Management
        </h2>
        <div className="flex gap-4">
          <AccessibleButton
            variant="outline"
            leftIcon={<Download className="w-4 h-4" />}
            onClick={handleExportSettings}
          >
            Export Settings
          </AccessibleButton>
          <AccessibleButton
            variant="outline"
            leftIcon={<Upload className="w-4 h-4" />}
            onClick={handleImportSettings}
          >
            Import Settings
          </AccessibleButton>
        </div>
      </div>

      {/* Auto Backup Configuration */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Automatic Backup
        </h2>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Enable Auto Backup</span>
            <button
              onClick={() => setAutoBackup(!autoBackup)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                autoBackup ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  autoBackup ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div>
            <label className="block text-sm text-gray-700 dark:text-gray-300 mb-2">
              Backup Frequency
            </label>
            <select
              value={backupFrequency}
              onChange={(e) => setBackupFrequency(e.target.value as any)}
              disabled={!autoBackup}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>
      </div>

      {/* Create Manual Backup */}
      <div className="mb-6">
        <AccessibleButton
          variant="primary"
          leftIcon={<Archive className="w-4 h-4" />}
          onClick={handleCreateBackup}
        >
          Create Manual Backup
        </AccessibleButton>
      </div>

      {/* Backup List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Available Backups
          </h2>
        </div>

        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {backups.map((backup) => (
            <div key={backup.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white">
                      {backup.name}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        backup.type === 'auto'
                          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300'
                          : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
                      }`}
                    >
                      {backup.type}
                    </span>
                    {backup.status === 'success' ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-red-600" />
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-2">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {new Date(backup.created).toLocaleString()}
                    </span>
                    <span>{formatSize(backup.size)}</span>
                  </div>

                  <div className="flex gap-2">
                    {backup.includes.map((item) => (
                      <span
                        key={item}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                      >
                        {item}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2">
                  <AccessibleButton
                    variant="outline"
                    size="sm"
                    onClick={() => handleRestoreBackup(backup.id)}
                  >
                    Restore
                  </AccessibleButton>
                  <AccessibleButton
                    variant="outline"
                    size="sm"
                    leftIcon={<Download className="w-4 h-4" />}
                  >
                    Download
                  </AccessibleButton>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BackupManager;

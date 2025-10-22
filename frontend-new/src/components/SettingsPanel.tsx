import React from 'react';
import { Settings, Bell, Palette, Zap, Shield, Globe } from 'lucide-react';
import { userPreferences } from '../services/user-preferences';

export const SettingsPanel: React.FC = () => {
  const prefs = userPreferences.get();

  const updatePref = (key: string, value: any) => {
    userPreferences.set({ [key]: value } as any);
  };

  return (
    <div className="p-6 max-w-4xl">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
          <Settings className="w-8 h-8 text-blue-600" />
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Customize your TerraForge experience
        </p>
      </div>

      {/* Appearance */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5" />
          Appearance
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Theme
            </label>
            <select
              value={prefs.theme}
              onChange={(e) => updatePref('theme', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Font Size
            </label>
            <select
              value={prefs.fontSize}
              onChange={(e) => updatePref('fontSize', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>
        </div>
      </section>

      {/* Behavior */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Behavior
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Auto-save</span>
            <input
              type="checkbox"
              checked={prefs.autoSave}
              onChange={(e) => updatePref('autoSave', e.target.checked)}
              className="w-4 h-4"
            />
          </label>

          {prefs.autoSave && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Auto-save Interval (seconds)
              </label>
              <input
                type="number"
                value={prefs.autoSaveInterval}
                onChange={(e) => updatePref('autoSaveInterval', parseInt(e.target.value))}
                min={10}
                max={300}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          )}

          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Confirm before delete</span>
            <input
              type="checkbox"
              checked={prefs.confirmBeforeDelete}
              onChange={(e) => updatePref('confirmBeforeDelete', e.target.checked)}
              className="w-4 h-4"
            />
          </label>
        </div>
      </section>

      {/* Notifications */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notifications
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Enable notifications</span>
            <input
              type="checkbox"
              checked={prefs.enableNotifications}
              onChange={(e) => updatePref('enableNotifications', e.target.checked)}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Enable sounds</span>
            <input
              type="checkbox"
              checked={prefs.enableSounds}
              onChange={(e) => updatePref('enableSounds', e.target.checked)}
              className="w-4 h-4"
            />
          </label>
        </div>
      </section>

      {/* Collaboration */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Globe className="w-5 h-5" />
          Collaboration
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Show live cursors</span>
            <input
              type="checkbox"
              checked={prefs.showLiveCursors}
              onChange={(e) => updatePref('showLiveCursors', e.target.checked)}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Enable real-time sync</span>
            <input
              type="checkbox"
              checked={prefs.enableRealTimeSync}
              onChange={(e) => updatePref('enableRealTimeSync', e.target.checked)}
              className="w-4 h-4"
            />
          </label>
        </div>
      </section>

      {/* Privacy */}
      <section className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5" />
          Privacy
        </h2>
        
        <div className="space-y-4">
          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Analytics enabled</span>
            <input
              type="checkbox"
              checked={prefs.analyticsEnabled}
              onChange={(e) => updatePref('analyticsEnabled', e.target.checked)}
              className="w-4 h-4"
            />
          </label>

          <label className="flex items-center justify-between">
            <span className="text-gray-700 dark:text-gray-300">Crash reports</span>
            <input
              type="checkbox"
              checked={prefs.crashReportsEnabled}
              onChange={(e) => updatePref('crashReportsEnabled', e.target.checked)}
              className="w-4 h-4"
            />
          </label>
        </div>
      </section>
    </div>
  );
};

export default SettingsPanel;

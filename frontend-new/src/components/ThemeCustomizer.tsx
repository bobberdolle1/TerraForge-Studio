import React, { useState } from 'react';
import { Palette, Sun, Moon, Monitor } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';
import { useTheme } from '../hooks/useTheme';
import useLocalStorage from '../hooks/useLocalStorage';

interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
}

export const ThemeCustomizer: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [colors, setColors] = useLocalStorage<ThemeColors>('theme-colors', {
    primary: '#2563eb',
    secondary: '#64748b',
    accent: '#8b5cf6',
  });
  const [isOpen, setIsOpen] = useState(false);

  const presetThemes = [
    { name: 'Ocean', primary: '#0ea5e9', secondary: '#06b6d4', accent: '#3b82f6' },
    { name: 'Forest', primary: '#10b981', secondary: '#059669', accent: '#22c55e' },
    { name: 'Sunset', primary: '#f59e0b', secondary: '#ef4444', accent: '#f97316' },
    { name: 'Purple', primary: '#8b5cf6', secondary: '#a855f7', accent: '#c084fc' },
    { name: 'Default', primary: '#2563eb', secondary: '#64748b', accent: '#8b5cf6' },
  ];

  const applyTheme = (newColors: ThemeColors) => {
    setColors(newColors);
    const root = document.documentElement;
    root.style.setProperty('--color-primary', newColors.primary);
    root.style.setProperty('--color-secondary', newColors.secondary);
    root.style.setProperty('--color-accent', newColors.accent);
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-20 right-4 p-3 bg-purple-600 text-white rounded-full shadow-lg hover:bg-purple-700 transition-all z-40"
        aria-label="Customize theme"
      >
        <Palette className="w-5 h-5" />
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Theme Customization
            </h2>

            {/* Mode Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Color Mode
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  onClick={() => setTheme('light')}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    theme === 'light'
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <Sun className="w-5 h-5 mx-auto mb-1" />
                  <span className="text-xs">Light</span>
                </button>
                <button
                  onClick={() => setTheme('dark')}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    theme === 'dark'
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <Moon className="w-5 h-5 mx-auto mb-1" />
                  <span className="text-xs">Dark</span>
                </button>
                <button
                  onClick={() => setTheme('system')}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    theme === 'system'
                      ? 'border-blue-600 bg-blue-50 dark:bg-blue-900'
                      : 'border-gray-300 dark:border-gray-600'
                  }`}
                >
                  <Monitor className="w-5 h-5 mx-auto mb-1" />
                  <span className="text-xs">System</span>
                </button>
              </div>
            </div>

            {/* Preset Themes */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Color Presets
              </label>
              <div className="grid grid-cols-5 gap-2">
                {presetThemes.map((preset) => (
                  <button
                    key={preset.name}
                    onClick={() => applyTheme(preset)}
                    className="aspect-square rounded-lg border-2 border-gray-300 dark:border-gray-600 hover:scale-110 transition-transform"
                    style={{ background: preset.primary }}
                    title={preset.name}
                  />
                ))}
              </div>
            </div>

            {/* Custom Colors */}
            <div className="space-y-3 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Primary Color
                </label>
                <input
                  type="color"
                  value={colors.primary}
                  onChange={(e) => applyTheme({ ...colors, primary: e.target.value })}
                  className="w-full h-10 rounded cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Secondary Color
                </label>
                <input
                  type="color"
                  value={colors.secondary}
                  onChange={(e) => applyTheme({ ...colors, secondary: e.target.value })}
                  className="w-full h-10 rounded cursor-pointer"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Accent Color
                </label>
                <input
                  type="color"
                  value={colors.accent}
                  onChange={(e) => applyTheme({ ...colors, accent: e.target.value })}
                  className="w-full h-10 rounded cursor-pointer"
                />
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2">
              <AccessibleButton
                variant="primary"
                className="flex-1"
                onClick={() => setIsOpen(false)}
              >
                Done
              </AccessibleButton>
              <AccessibleButton
                variant="outline"
                onClick={() => applyTheme(presetThemes[4])}
              >
                Reset
              </AccessibleButton>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ThemeCustomizer;

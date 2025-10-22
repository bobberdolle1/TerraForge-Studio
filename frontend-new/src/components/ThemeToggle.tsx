/**
 * Theme Toggle Component
 * Provides a UI to switch between Light, Dark, and Auto themes
 */

import { Sun, Moon, Monitor } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { theme, setTheme, resolvedTheme } = useTheme();

  const themes = [
    { value: 'light' as const, icon: Sun, label: 'Light' },
    { value: 'dark' as const, icon: Moon, label: 'Dark' },
    { value: 'auto' as const, icon: Monitor, label: 'Auto' },
  ];

  return (
    <div className="flex items-center bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-600 p-1">
      {themes.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => setTheme(value)}
          className={`
            flex items-center space-x-2 px-3 py-1.5 rounded-md transition-all
            ${theme === value 
              ? 'bg-blue-600 text-white shadow-sm' 
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
            }
          `}
          title={`${label} theme${value === 'auto' ? ` (currently ${resolvedTheme})` : ''}`}
        >
          <Icon className="w-4 h-4" />
          <span className="text-sm font-medium hidden sm:inline">{label}</span>
        </button>
      ))}
    </div>
  );
};

export default ThemeToggle;


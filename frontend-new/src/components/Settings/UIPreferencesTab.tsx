import { useState } from 'react';
import { Loader } from 'lucide-react';
import type { UIPreferences } from '@/types/settings';

interface UIPreferencesTabProps {
  ui: UIPreferences;
  onSave: (ui: UIPreferences) => void;
  saving: boolean;
}

const UIPreferencesTab: React.FC<UIPreferencesTabProps> = ({ ui, onSave, saving }) => {
  const [formData, setFormData] = useState(ui);

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold">UI & Language Preferences</h3>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Language</label>
          <select
            value={formData.language}
            onChange={(e) => setFormData({ ...formData, language: e.target.value as 'en' | 'ru' })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="en">English</option>
            <option value="ru">Русский</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Theme</label>
          <select
            value={formData.theme}
            onChange={(e) => setFormData({ ...formData, theme: e.target.value as any })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end pt-6 border-t">
        <button onClick={() => onSave(formData)} disabled={saving} className="px-6 py-3 bg-blue-600 text-white rounded-md">
          {saving && <Loader className="w-4 h-4 animate-spin mr-2" />}
          Save Preferences
        </button>
      </div>
    </div>
  );
};

export default UIPreferencesTab;


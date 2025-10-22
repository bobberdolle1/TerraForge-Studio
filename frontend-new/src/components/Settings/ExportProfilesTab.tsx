import { useState } from 'react';
import { Loader } from 'lucide-react';
import type { ExportProfiles } from '@/types/settings';

interface ExportProfilesTabProps {
  profiles: ExportProfiles;
  onSave: (profiles: ExportProfiles) => void;
  saving: boolean;
}

const ExportProfilesTab: React.FC<ExportProfilesTabProps> = ({ profiles, onSave, saving }) => {
  const [formData, setFormData] = useState(profiles);

  return (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold">Export Profiles</h3>

      <div className="bg-white rounded-lg p-6 border">
        <h4 className="font-semibold mb-4">Unreal Engine 5</h4>
        <div className="space-y-3">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.unreal5.export_weightmaps}
              onChange={(e) => setFormData({
                ...formData,
                unreal5: { ...formData.unreal5, export_weightmaps: e.target.checked }
              })}
              className="rounded text-blue-600"
            />
            <span className="ml-2 text-sm">Export Weightmaps</span>
          </label>
        </div>
      </div>

      <div className="flex justify-end pt-6 border-t">
        <button
          onClick={() => onSave(formData)}
          disabled={saving}
          className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {saving && <Loader className="w-4 h-4 animate-spin mr-2" />}
          Save Profiles
        </button>
      </div>
    </div>
  );
};

export default ExportProfilesTab;


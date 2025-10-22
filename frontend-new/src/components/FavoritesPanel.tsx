import React, { useState } from 'react';
import { Star, Trash2, MapPin, Plus } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';
import { Tooltip } from './Tooltip';
import useLocalStorage from '../hooks/useLocalStorage';
import { notify } from '../utils/toast';

interface FavoriteLocation {
  id: string;
  name: string;
  bbox: {
    north: number;
    south: number;
    east: number;
    west: number;
  };
  createdAt: number;
  tags?: string[];
}

interface FavoritesPanelProps {
  onLocationSelect?: (bbox: FavoriteLocation['bbox']) => void;
  currentBbox?: FavoriteLocation['bbox'] | null;
  className?: string;
}

/**
 * Favorites Panel Component
 * Manages favorite locations and quick access
 */
export const FavoritesPanel: React.FC<FavoritesPanelProps> = ({
  onLocationSelect,
  currentBbox,
  className = '',
}) => {
  const [favorites, setFavorites] = useLocalStorage<FavoriteLocation[]>('terraforge-favorites', []);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [newFavoriteName, setNewFavoriteName] = useState('');

  const addFavorite = () => {
    if (!currentBbox) {
      notify.error('Please select an area first');
      return;
    }

    if (!newFavoriteName.trim()) {
      notify.error('Please enter a name');
      return;
    }

    const newFavorite: FavoriteLocation = {
      id: Date.now().toString(),
      name: newFavoriteName.trim(),
      bbox: currentBbox,
      createdAt: Date.now(),
    };

    setFavorites([...favorites, newFavorite]);
    setNewFavoriteName('');
    setShowAddDialog(false);
    notify.success(`Added "${newFavorite.name}" to favorites`);
  };

  const removeFavorite = (id: string) => {
    const favorite = favorites.find(f => f.id === id);
    setFavorites(favorites.filter(f => f.id !== id));
    notify.success(`Removed "${favorite?.name}" from favorites`);
  };

  const selectFavorite = (favorite: FavoriteLocation) => {
    if (onLocationSelect) {
      onLocationSelect(favorite.bbox);
      notify.info(`Loaded "${favorite.name}"`);
    }
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Star className="w-5 h-5 text-yellow-500" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">
            Favorite Locations
          </h2>
        </div>
        <Tooltip content="Add current area to favorites">
          <AccessibleButton
            variant="primary"
            size="sm"
            onClick={() => setShowAddDialog(true)}
            disabled={!currentBbox}
          >
            <Plus className="w-4 h-4" />
            Add
          </AccessibleButton>
        </Tooltip>
      </div>

      {/* Add Dialog */}
      {showAddDialog && (
        <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <input
            type="text"
            value={newFavoriteName}
            onChange={(e) => setNewFavoriteName(e.target.value)}
            placeholder="Enter location name..."
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg mb-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            onKeyDown={(e) => e.key === 'Enter' && addFavorite()}
            autoFocus
          />
          <div className="flex gap-2">
            <AccessibleButton variant="primary" size="sm" onClick={addFavorite}>
              Save
            </AccessibleButton>
            <AccessibleButton variant="ghost" size="sm" onClick={() => setShowAddDialog(false)}>
              Cancel
            </AccessibleButton>
          </div>
        </div>
      )}

      {/* Favorites List */}
      <div className="space-y-2">
        {favorites.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <Star className="w-12 h-12 mx-auto mb-2 opacity-50" />
            <p>No favorite locations yet</p>
            <p className="text-sm mt-1">Select an area and click "Add" to save it</p>
          </div>
        ) : (
          favorites.map((favorite) => (
            <div
              key={favorite.id}
              className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors group"
            >
              <button
                onClick={() => selectFavorite(favorite)}
                className="flex-1 flex items-center gap-3 text-left"
              >
                <MapPin className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <div className="flex-1">
                  <div className="font-medium text-gray-900 dark:text-white">
                    {favorite.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(favorite.createdAt).toLocaleDateString()}
                  </div>
                </div>
              </button>
              <Tooltip content="Remove from favorites">
                <button
                  onClick={() => removeFavorite(favorite.id)}
                  className="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                  aria-label="Remove favorite"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </Tooltip>
            </div>
          ))
        )}
      </div>

      {favorites.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
          {favorites.length} favorite location{favorites.length !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  );
};

export default FavoritesPanel;

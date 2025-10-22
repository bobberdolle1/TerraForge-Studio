import React, { useState } from 'react';
import { Package, Download, Star, Search } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface Plugin {
  id: string;
  name: string;
  description: string;
  author: string;
  version: string;
  rating: number;
  downloads: number;
  category: string;
  price: number;
}

export const PluginMarketplace: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [category, setCategory] = useState('all');
  
  const plugins: Plugin[] = [
    {
      id: '1',
      name: 'Advanced Erosion',
      description: 'Realistic erosion simulation',
      author: 'TerrainLab',
      version: '2.1.0',
      rating: 4.8,
      downloads: 15420,
      category: 'generation',
      price: 0,
    },
  ];

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Plugin Marketplace</h1>
      
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search plugins..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-2 border rounded-lg"
        />
      </div>

      <div className="grid gap-4">
        {plugins.map((plugin) => (
          <div key={plugin.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
            <h3 className="font-semibold text-lg">{plugin.name}</h3>
            <p className="text-sm text-gray-600">{plugin.description}</p>
            <div className="flex items-center gap-3 mt-2 text-sm">
              <span className="flex items-center gap-1">
                <Star className="w-4 h-4 fill-yellow-500 text-yellow-500" />
                {plugin.rating}
              </span>
              <span>{plugin.downloads} downloads</span>
              <span>v{plugin.version}</span>
            </div>
            <AccessibleButton variant="primary" size="sm" className="mt-3">
              Install
            </AccessibleButton>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PluginMarketplace;

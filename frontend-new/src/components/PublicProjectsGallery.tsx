import React, { useState } from 'react';
import { Globe, Heart, Eye, Download, Share2, Lock, Unlock } from 'lucide-react';
import { AccessibleButton } from './AccessibleButton';

interface Project {
  id: string;
  title: string;
  description: string;
  author: string;
  thumbnail: string;
  isPublic: boolean;
  likes: number;
  views: number;
  downloads: number;
  tags: string[];
  createdAt: number;
}

export const PublicProjectsGallery: React.FC = () => {
  const [projects] = useState<Project[]>([
    {
      id: '1',
      title: 'Alpine Mountains',
      description: 'Realistic mountain range with snow peaks',
      author: 'TerrainMaster',
      thumbnail: '🏔️',
      isPublic: true,
      likes: 234,
      views: 1520,
      downloads: 89,
      tags: ['mountains', 'realistic', 'snow'],
      createdAt: Date.now() - 86400000,
    },
    {
      id: '2',
      title: 'Tropical Paradise',
      description: 'Island with beaches and palm trees',
      author: 'IslandCreator',
      thumbnail: '🏝️',
      isPublic: true,
      likes: 567,
      views: 3240,
      downloads: 145,
      tags: ['island', 'tropical', 'beach'],
      createdAt: Date.now() - 172800000,
    },
    {
      id: '3',
      title: 'Desert Dunes',
      description: 'Vast desert with realistic sand dunes',
      author: 'DesertWizard',
      thumbnail: '🏜️',
      isPublic: true,
      likes: 123,
      views: 890,
      downloads: 45,
      tags: ['desert', 'dunes', 'arid'],
      createdAt: Date.now() - 259200000,
    },
  ]);

  const [filter, setFilter] = useState<'trending' | 'recent' | 'popular'>('trending');

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Community Projects
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Explore and share terrain creations with the community
        </p>
      </div>

      {/* Filter Tabs */}
      <div className="flex gap-2 mb-6">
        {(['trending', 'recent', 'popular'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg capitalize transition-colors ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* Projects Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <div
            key={project.id}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-all"
          >
            {/* Thumbnail */}
            <div className="h-48 bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-8xl">
              {project.thumbnail}
            </div>

            {/* Content */}
            <div className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-bold text-lg text-gray-900 dark:text-white">
                  {project.title}
                </h3>
                <div className="flex items-center gap-1">
                  {project.isPublic ? (
                    <Globe className="w-4 h-4 text-green-500" title="Public" />
                  ) : (
                    <Lock className="w-4 h-4 text-gray-400" title="Private" />
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                {project.description}
              </p>

              <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
                by {project.author}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1 mb-3">
                {project.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                <span className="flex items-center gap-1">
                  <Heart className="w-4 h-4" />
                  {project.likes}
                </span>
                <span className="flex items-center gap-1">
                  <Eye className="w-4 h-4" />
                  {project.views}
                </span>
                <span className="flex items-center gap-1">
                  <Download className="w-4 h-4" />
                  {project.downloads}
                </span>
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                <AccessibleButton variant="primary" size="sm" className="flex-1">
                  View
                </AccessibleButton>
                <AccessibleButton
                  variant="outline"
                  size="sm"
                  leftIcon={<Heart className="w-4 h-4" />}
                >
                  Like
                </AccessibleButton>
                <AccessibleButton
                  variant="ghost"
                  size="sm"
                  leftIcon={<Share2 className="w-4 h-4" />}
                >
                  Share
                </AccessibleButton>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PublicProjectsGallery;
